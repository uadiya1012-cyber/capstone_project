"""
`protected_media` — production-д media файлд хандах эрхийн тестүүд.

Яагаад тест өөрийн urlconf-той вэ: `config/urls.py` нь маршрутаа
`settings.DEBUG`-ийн дагуу сонгодог бөгөөд тэр шийдвэр модулийг import
хийх үед НЭГ л удаа гардаг. Локал `.env`-д `DEBUG=True` байвал тест
production-ын маршрутыг шалгалгүй өнгөрөх байсан. Тиймээс энд тухайн
маршрутыг ил тодорхойлж `ROOT_URLCONF`-ийг түр солино — тест нь орчны
тохиргооноос хамаарахаа болино.
"""

import shutil
import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.urls import path

from config.views import may_view, protected_media
from expenses.models import Expense

# Тест хугацаанд ашиглах MEDIA_ROOT. Бодит media/ хавтсанд хүрэхгүй.
_MEDIA = tempfile.mkdtemp(prefix='test-media-')

urlpatterns = [
    path('media/<path:path>', protected_media, name='protected_media'),
    # `settings.LOGIN_URL` нь зам биш URL-ийн НЭР ('login') тул `login_required`-ийн
    # redirect шийдэгдэхийн тулд энэ urlconf-д ижил нэртэй зам байх шаардлагатай.
    path('accounts/', lambda r: HttpResponse('login form'), name='login'),
]

RECEIPT = 'receipts/2026/09/22/bill.jpg'
AVATAR = 'avatars/owner.png'
UNKNOWN = 'exports/tailan.pdf'


@override_settings(ROOT_URLCONF=__name__, MEDIA_ROOT=_MEDIA, SECURE_SSL_REDIRECT=False)
class ProtectedMediaTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Бодитоор үйлчлэх файлууд. Агуулга нь хамаагүй — 200 үед биетээр
        # уншигдаж байгааг батлахад хүрэлцэнэ.
        for rel in (RECEIPT, AVATAR, UNKNOWN):
            f = Path(_MEDIA) / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(b'file-content')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(_MEDIA, ignore_errors=True)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user('owner', password='Test1234!')
        cls.other = User.objects.create_user('other', password='Test1234!')
        cls.staff = User.objects.create_user('staff_u', password='Test1234!', is_staff=True)
        Expense.objects.create(
            user=cls.owner, amount='12500.00', date='2026-09-22',
            description='Тестийн зардал', receipt=RECEIPT,
        )

    # --- нэвтрэлт ---

    def test_zochin_login_ruu_shiljine(self):
        """Нэвтрээгүй зочин файл рүү хүрэх ч үгүй — login руу шилжинэ."""
        r = self.client.get(f'/media/{RECEIPT}')
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/', r.headers['Location'])

    # --- баримт: эзэмшил ---

    def test_ezen_oor_barimtaa_kharna(self):
        self.client.force_login(self.owner)
        r = self.client.get(f'/media/{RECEIPT}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(b''.join(r.streaming_content), b'file-content')

    def test_busad_kheregleegch_barimt_kharakhgui(self):
        """Хамгийн чухал тест: URL мэдсэн ч бусдын баримт харагдахгүй.

        403 биш 404 — файл байгаа гэдгийг ч мэдэгдэхгүй.
        """
        self.client.force_login(self.other)
        r = self.client.get(f'/media/{RECEIPT}')
        self.assertEqual(r.status_code, 404)

    def test_staff_bugdiig_kharna(self):
        self.client.force_login(self.staff)
        r = self.client.get(f'/media/{RECEIPT}')
        self.assertEqual(r.status_code, 200)

    # --- аватар ---

    def test_avatar_nevtersen_bukhend_kharagdana(self):
        self.client.force_login(self.other)
        r = self.client.get(f'/media/{AVATAR}')
        self.assertEqual(r.status_code, 200)

    # --- хориотой замууд ---

    def test_tanikhgui_zam_khoriotoi(self):
        """`receipts/`, `avatars/`-т хамаарахгүй зам — файл БАЙГАА ч хориотой."""
        self.client.force_login(self.staff)
        r = self.client.get(f'/media/{UNKNOWN}')
        self.assertEqual(r.status_code, 404)

    def test_path_traversal_khoriotoi(self):
        """`receipts/` -ээр эхэлсэн ч гараад явах оролдлого эзэмшилд таарахгүй."""
        self.assertFalse(may_view(self.other, 'receipts/../../config/settings.py'))
        self.assertFalse(may_view(self.other, '../config/settings.py'))


@override_settings(SECURE_SSL_REDIRECT=False)
class LoginRedirectTests(TestCase):
    """
    Нэвтрээгүй хэрэглэгчийг хамгаалалттай хуудаснаас нэвтрэх формд хүргэх.

    Энд ЗОРИУД өөрийн urlconf хэрэглэхгүй — бодит `config.urls`-аар бүх гинжийг
    (login_required → settings.LOGIN_URL → accounts/urls.py) шалгах нь чухал.
    LOGIN_URL заагаагүй бол Django `/accounts/login/` руу шиднэ, тэр зам нь энэ
    аппад байхгүй тул хэрэглэгч 404 хардаг.
    """

    def test_zochin_nevtrekh_formd_khurne(self):
        from django.urls import reverse

        r = self.client.get('/accounts/dashboard/', follow=True)
        self.assertEqual(r.status_code, 200, 'нэвтрэх хуудас нээгдэх ёстой (404 биш)')
        final_url = r.redirect_chain[-1][0]
        self.assertIn(reverse('login'), final_url)

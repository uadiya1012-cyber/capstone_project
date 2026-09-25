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
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage, InMemoryStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import path

from config.db_url import parse_database_url
from config.media_check import describe, round_trip
from config.storage import ProtectedS3Storage
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


class ProtectedS3StorageTests(SimpleTestCase):
    """
    config/storage.py — файл bucket-д байсан ч URL нь `/media/...` хэвээр байх
    ёстой. Энэ нь эрхийн хаалга (`protected_media`)-ыг тойрохгүй байх цорын
    ганц баталгаа: S3Storage-ийн анхдагч `url()` нь bucket-ийн гарын үсэгтэй
    шууд хаяг буцаадаг бөгөөд түүнийг template-д хэвлэвэл `may_view` ажиллахгүй.
    Сүлжээнд хандахгүй — S3Storage холболтоо зөвхөн уншиж/бичихэд үүсгэдэг.
    """

    def _storage(self):
        return ProtectedS3Storage(
            bucket_name='test-bucket', access_key='k', secret_key='s',
            endpoint_url='https://example.invalid',
        )

    def test_url_media_zam_butsaana(self):
        self.assertEqual(self._storage().url(RECEIPT), f'/media/{RECEIPT}')

    def test_url_kirill_temdegt_kodlono(self):
        """Монгол нэртэй файл: хөтөч уншихуйц percent-кодлолт (FileSystemStorage-тэй ижил)."""
        self.assertEqual(
            self._storage().url('avatars/зураг 1.png'),
            '/media/avatars/%D0%B7%D1%83%D1%80%D0%B0%D0%B3%201.png',
        )

    @override_settings(MEDIA_URL='/files')
    def test_media_url_tegsh_zuraasgui_bol_nemne(self):
        self.assertEqual(self._storage().url(AVATAR), f'/files/{AVATAR}')


_BUCKET_STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}


@override_settings(ROOT_URLCONF=__name__, STORAGES=_BUCKET_STORAGES, SECURE_SSL_REDIRECT=False)
class ProtectedMediaBucketTests(TestCase):
    """
    Media локал диск дээр БИШ үед (production-ы bucket) `protected_media` файлыг
    storage-оос өөрөө уншиж дамжуулна. Жинхэнэ bucket-ийн оронд Django-ийн
    InMemoryStorage: тэр ч FileSystemStorage биш тул view-ийн яг тэр салбар
    ажиллана, сүлжээ/нууц түлхүүр хэрэггүй.
    """

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user('b_owner', password='Test1234!')
        cls.other = User.objects.create_user('b_other', password='Test1234!')
        cls.staff = User.objects.create_user('b_staff', password='Test1234!', is_staff=True)

    def setUp(self):
        # Файлыг тест бүрд шинээр бичнэ — InMemoryStorage-ийн агуулга тестүүдийн
        # хооронд хадгалагддаг тул нэр давхцахаас дагавар нэмэгдэнэ (file_overwrite=False).
        self.expense = Expense.objects.create(
            user=self.owner, amount='9900.00', date='2026-09-25', description='Bucket тест',
            receipt=SimpleUploadedFile('bill.jpg', b'jpeg-bytes', content_type='image/jpeg'),
        )
        self.path = self.expense.receipt.name

    def test_url_media_zam(self):
        self.assertTrue(self.path.startswith('receipts/'), self.path)
        self.assertEqual(self.expense.receipt.url, f'/media/{self.path}')

    def test_ezen_barimtaa_storage_oos_unshina(self):
        self.client.force_login(self.owner)
        r = self.client.get(f'/media/{self.path}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(b''.join(r.streaming_content), b'jpeg-bytes')
        self.assertEqual(r['Content-Type'], 'image/jpeg')

    def test_busad_kheregleegch_404(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(f'/media/{self.path}').status_code, 404)

    def test_staff_bugdiig_kharna(self):
        self.client.force_login(self.staff)
        r = self.client.get(f'/media/{self.path}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(b''.join(r.streaming_content), b'jpeg-bytes')

    def test_baikhgui_file_404(self):
        """Эрх байгаа ч файл storage-д алга (жишээ: диск цэвэрлэгдсэн үеийн хуучин DB мөр)."""
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get('/media/avatars/alga.png').status_code, 404)


class MediaCheckTests(SimpleTestCase):
    """config/media_check.py — scripts/check_media_bucket.py-ийн цөм. Сүлжээгүй."""

    def test_lokal_storage_shalgakh_zuilgui(self):
        steps = round_trip(FileSystemStorage(location=_MEDIA))
        self.assertEqual(len(steps), 1)
        self.assertFalse(steps[0].ok)
        self.assertIn('MEDIA_S3_BUCKET', steps[0].detail)

    def test_bucket_buten_ergelt(self):
        """Bucket-ийн оронд InMemoryStorage: бичих → унших → /media/ URL → устгах бүгд ✓, файл үлдэхгүй."""
        storage = InMemoryStorage(base_url='/media/')
        steps = round_trip(storage)
        self.assertEqual([s.name for s in steps], ['storage', 'бичих', 'унших', 'url', 'устгах'])
        self.assertTrue(all(s.ok for s in steps), [(s.name, s.detail) for s in steps if not s.ok])
        self.assertTrue(steps[1].detail.startswith('healthcheck/'))
        self.assertFalse(storage.exists(steps[1].detail))

    def test_aldaag_tokhirgoond_chigluulj_tailbarlana(self):
        from botocore.exceptions import ClientError, EndpointConnectionError

        def client_error(code):
            return ClientError({'Error': {'Code': code, 'Message': 'x'}}, 'PutObject')

        self.assertIn('MEDIA_S3_SECRET_KEY', describe(client_error('SignatureDoesNotMatch')))
        self.assertIn('MEDIA_S3_BUCKET', describe(client_error('NoSuchBucket')))
        self.assertIn('MEDIA_S3_ACCESS_KEY', describe(client_error('InvalidAccessKeyId')))
        self.assertIn('эрхгүй', describe(client_error('AccessDenied')))
        self.assertIn('MEDIA_S3_ENDPOINT_URL', describe(EndpointConnectionError(endpoint_url='https://x.invalid')))
        self.assertIn('ValueError', describe(ValueError('юу ч биш')))


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


class DatabaseUrlTests(SimpleTestCase):
    """
    config/db_url.py — DATABASE_URL задлагч. Өгөгдлийн сан хэрэггүй (SimpleTestCase).

    Эдгээр тохиолдлын хоёр нь production дээр бодитоор тохиолдсон: тасарсан URL
    (Render-ийн эхний deploy унасан) ба Neon-ийн channel_binding-ийг хаяж байсан.
    """

    NEON = ('postgresql://neondb_owner:npg_s3cret@ep-brook-123-pooler.c-3.ap-southeast-1'
            '.aws.neon.tech/neondb?sslmode=require&channel_binding=require')

    def test_neon_url_buren_zadarna(self):
        d = parse_database_url(self.NEON)
        self.assertEqual(d['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(d['NAME'], 'neondb')
        self.assertEqual(d['USER'], 'neondb_owner')
        self.assertEqual(d['PASSWORD'], 'npg_s3cret')
        self.assertEqual(d['HOST'], 'ep-brook-123-pooler.c-3.ap-southeast-1.aws.neon.tech')
        self.assertEqual(d['PORT'], '5432')
        self.assertEqual(d['CONN_MAX_AGE'], 60)

    def test_channel_binding_damjuulna(self):
        """Neon-ийн MITM хамгаалалт хаягдахгүй, libpq руу хүрнэ."""
        d = parse_database_url(self.NEON)
        self.assertEqual(d['OPTIONS'], {'sslmode': 'require', 'channel_binding': 'require'})

    def test_tanikhgui_query_damjuulakhgui(self):
        """Allowlist-д байхгүй параметр libpq руу очвол холболт унана — шүүнэ."""
        d = parse_database_url(self.NEON + '&foo=bar&application_name=x')
        self.assertNotIn('foo', d['OPTIONS'])
        self.assertNotIn('application_name', d['OPTIONS'])

    def test_query_gui_bol_default_sslmode(self):
        d = parse_database_url('postgresql://u:p@h/db', default_sslmode='prefer')
        self.assertEqual(d['OPTIONS'], {'sslmode': 'prefer'})

    def test_port_bolon_kodlogdson_nuuts_ug(self):
        d = parse_database_url('postgresql://u:p%40ss%2Fw@h:6543/db')
        self.assertEqual(d['PORT'], '6543')
        self.assertEqual(d['PASSWORD'], 'p@ss/w')

    def test_tasarsan_url_changa_unana(self):
        """Production дээр бодитоор тохиолдсон: /neondb?... сүүл хуулагдаагүй."""
        with self.assertRaises(ImproperlyConfigured) as cm:
            parse_database_url('postgresql://neondb_owner:npg_s3cret@ep-x-pooler.neon.tech')
        msg = str(cm.exception)
        self.assertIn('NAME', msg)
        self.assertIn('/neondb', msg)
        self.assertNotIn('npg_s3cret', msg, 'нууц үг алдааны мессежид гарч болохгүй')

    def test_url_bish_text_changa_unana(self):
        with self.assertRaises(ImproperlyConfigured) as cm:
            parse_database_url('1234')
        self.assertIn('HOST', str(cm.exception))
        self.assertIn('USER', str(cm.exception))

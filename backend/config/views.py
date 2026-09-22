"""
Төслийн түвшний view-ууд: health check ба хамгаалалттай media.

Апп тус бүрийн (accounts, expenses, ...) логикт хамаарахгүй, харин
байршуулалтын (deployment) шаардлагаас үүдсэн хоёр зүйл энд байна.
"""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.views.static import serve

from expenses.models import Expense


def healthz(request):
    """
    Платформын health check (Render → `healthCheckPath`).

    Зориуд өгөгдлийн санд ХАНДАХГҮЙ. Шалтгаан: Neon-ийн үнэгүй compute нь
    5 минут ажилгүй бол унтдаг бөгөөд сэрэхэд ~1 секунд шаардана. Health
    check DB-гээс хамаарвал тэр сэрэх хугацаанд "unhealthy" гэж тооцогдож,
    Render deploy-г буруугаар унагаах эрсдэлтэй. Энэ endpoint нь зөвхөн
    "процесс амьд, хүсэлт хүлээж авч байна" гэдгийг хэлнэ.

    `settings.SECURE_REDIRECT_EXEMPT` нь энэ замыг http → https redirect-ээс
    чөлөөлдөг — платформын дотоод prober http-ээр ирдэг тул 301 биш 200 авна.
    """
    return HttpResponse('ok', content_type='text/plain')


def may_view(user, path):
    """
    `user` нь `/media/<path>` файлыг харах эрхтэй эсэхийг шийднэ.

    Энэ функц бол хамгаалалтын цорын нэг хаалга — `protected_media` доор
    үүнээс `False` буцвал 404 болно.

    `path` нь MEDIA_ROOT-оос хойших харьцангуй зам (урд `/media/` байхгүй),
    жишээ: `receipts/2026/09/22/bill.jpg`, `avatars/profile.png`.

    Бодлого:
      • `avatars/...`  — нэвтэрсэн хэрэглэгч бүр
      • `receipts/...` — зөвхөн зардлын эзэн, эсвэл `is_staff` админ
      • бусад бүх зам — хориотой

    `user` нь ЗААВАЛ нэвтэрсэн байна — `protected_media` дээрх
    `@login_required` зочныг аль хэдийн шүүсэн байдаг.

    Буцаах: True = үйлчил, False = 404. Энэ функцийн тестүүд `config/tests.py`.
    """
    # Профайлын зураг — нэвтэрсэн хэрэглэгч бүрд харагдана. Баримт шиг нууц
    # биш бөгөөд хожим хэрэглэгчдийн жагсаалт, админ самбар нэмэхэд зураг
    # эвдэрч харагдахгүй байхын тулд.
    if path.startswith('avatars/'):
        return True

    # Баримтын зураг — хувийн санхүүгийн бичиг баримт.
    if path.startswith('receipts/'):
        # `is_staff` нь Django-ийн admin панелийн эрхтэй тулгуурладаг тул
        # `createsuperuser`-ээр үүсгэсэн админ нэмэлт тохиргоогүйгээр ажиллана
        # (`role` нь анхдагчаар 'USER' болдог тул тэрийг шалгавал хоцордог).
        if user.is_staff:
            return True
        # `Expense.receipt` нь `receipts/...` замыг ЯГ ижил хэлбэрээр хадгалдаг
        # тул шууд харьцуулж эзэмшлийг тогтооно. Өөр хэрэглэгчийн баримт бол
        # хоосон буцаж, дуудсан view нь 404 өгнө.
        return Expense.objects.filter(receipt=path, user=user).exists()

    # Танихгүй зам. Зориуд хаана: хожим шинэ `upload_to` (жишээ: тайлангийн
    # PDF) нэмэхэд энэ функцийг засах хүртэл автоматаар нээгдэхгүй байг.
    return False


@login_required
def protected_media(request, path):
    """
    Production-д `/media/<path>`-г эрхийн шалгалттайгаар үйлчилнэ.

    DEBUG=True үед config/urls.py нь Django-ийн `static()` helper-ээр
    шалгалтгүй үйлчилдэг — локал хөгжүүлэлтэд хангалттай. Production-д тэр
    маршрут байхгүй болдог (WhiteNoise нь зөвхөн STATIC_ROOT-д үйлчилдэг),
    тиймээс энэ view орж ирнэ.

    Эрхгүй үед 403 биш 404 буцаана: "энэ файл байгаа, гэхдээ чи харж
    болохгүй" гэж хэлэх нь өөрөө мэдээлэл тараах (баримт хэзээ үүссэн,
    хэн үүсгэсэн г.м. таамаглах боломж) тул байхгүй гэж хариулна.

    `serve()` нь `safe_join` ашигладаг тул `../` -аар MEDIA_ROOT-оос гарах
    оролдлого (path traversal) өөрөө хаагддаг.
    """
    if not may_view(request.user, path):
        raise Http404
    return serve(request, path, document_root=settings.MEDIA_ROOT)

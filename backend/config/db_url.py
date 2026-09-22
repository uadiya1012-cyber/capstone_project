"""
DATABASE_URL-ийг Django-ийн DATABASES['default'] хэлбэрт хөрвүүлнэ.

settings.py-ээс тусад нь салгасан шалтгаан: settings нь модуль ачаалагдах үед нэг л
удаа ажилладаг тул доторх логикийг unit test-ээр шалгах аргагүй байсан. Цэвэр функц
болгосноор янз бүрийн URL-ийг (тасарсан, %-кодлогдсон, query-тэй/-гүй) тестлэж,
production дээр л илэрдэг байсан алдааг локалд барина.
"""

from urllib.parse import parse_qs, unquote, urlparse

from django.core.exceptions import ImproperlyConfigured

# Query-оос libpq руу дамжуулах холболтын параметрүүд. Neon зэрэг үүлэн Postgres нь
# `?sslmode=require&channel_binding=require` гэж өгдөг:
#   sslmode         — шифрлэлт. `require` нь шифрлэдэг ч серверийн сертификатыг
#                     ШАЛГАДАГГҮЙ (MITM-д эмзэг).
#   channel_binding — SCRAM нэвтрэлтийг TLS сувагтай холбож, дээрх цоорхойг хаана.
#                     Neon үүнийг санамсаргүй биш, яг энэ шалтгаанаар нэмдэг.
#   sslrootcert     — `sslmode=verify-full` хэрэглэх үед CA файлын зам.
#   connect_timeout — унтсан compute (Neon scale-to-zero) сэрэхийг хэр удаан хүлээх.
# Allowlist-ээр хязгаарласан: query-г бүхэлд нь дамжуулбал танихгүй нэг параметр
# холболтыг бүхэлд нь унагаана ("invalid connection option").
LIBPQ_QUERY_PARAMS = ('sslmode', 'channel_binding', 'sslrootcert', 'connect_timeout')


def parse_database_url(url, default_sslmode='require'):
    """
    `postgresql://USER:PASSWORD@HOST[:PORT]/DBNAME?sslmode=...` → DATABASES dict.

    NAME, HOST, USER-ийн аль нэг нь хоосон бол ImproperlyConfigured — юу дутууг
    нэрлэж, хүлээж байгаа хэлбэрийг харуулна. Нууц үгийг хэзээ ч мессежид оруулахгүй.
    """
    u = urlparse(url)
    query = {k: v[0] for k, v in parse_qs(u.query).items()}

    options = {k: query[k] for k in LIBPQ_QUERY_PARAMS if k in query}
    options.setdefault('sslmode', default_sslmode)

    config = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': u.path.lstrip('/'),
        'USER': unquote(u.username or ''),
        'PASSWORD': unquote(u.password or ''),
        'HOST': u.hostname or '',
        'PORT': str(u.port or 5432),
        # Хүсэлт бүрд шинээр холбогдохгүй, 60 секунд дахин ашиглана (үүлэн DB-д чухал)
        'CONN_MAX_AGE': 60,
        'OPTIONS': options,
    }

    # Бүтэн бус URL-ийг дуугүй хүлээж авбал Django хожим "Please supply the NAME
    # value" гэсэн 40 мөр traceback өгдөг бөгөөд тэр нь холболтын мөрийг хуулахдаа
    # сүүлийг тасалсан гэдгийг хэлж чадахгүй. Тиймээс энд чанга унана.
    missing = [k for k in ('NAME', 'HOST', 'USER') if not config[k]]
    if missing:
        raise ImproperlyConfigured(
            'DATABASE_URL-ийг задлахад {} дутуу гарлаа. Хүлээж байгаа хэлбэр:\n'
            '  postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require\n'
            'Холболтын мөрийг бүтнээр хуулсан эсэхээ шалгана уу — өгөгдлийн сангийн '
            'нэр (жишээ: /neondb) болон ?sslmode=require сүүл байх ёстой.\n'
            'Одоогийн задлалт: USER={!r}, HOST={!r}, NAME={!r} (нууц үг хэвлэгдэхгүй).'
            .format(', '.join(missing), config['USER'], config['HOST'], config['NAME'])
        )
    return config

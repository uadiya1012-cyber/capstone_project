import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# SECURITY WARNING: keep the secret key used in production secret!
#
# SECRET_KEY нь session cookie болон CSRF token-д гарын үсэг зурдаг.
# Түлхүүрийг мэддэг хүн дурын хэрэглэгчийн session хуурамчаар үүсгэж
# чадна — өөрөөр хэлбэл нэвтрэлтийг бүхэлд нь тойрч гарна.
#
# Өмнө нь энд hardcode хийсэн түлхүүр fallback болж байсан бөгөөд тэр
# түлхүүр хоёр public repo-гийн git түүхэнд ил гарсан. Тиймээс дахин
# ашиглаж болохгүй.
#
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if not DEBUG:
        # Production-д чимээгүй ажиллахаас чанга унасан нь дээр.
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(
            'SECRET_KEY тохируулаагүй байна. .env файлд SECRET_KEY-г зааж өгнө үү. '
            'Шинэ түлхүүр үүсгэх: python -c "from django.core.management.utils '
            'import get_random_secret_key; print(get_random_secret_key())"'
        )
    # Зөвхөн DEBUG=True үеийн нөөц. Санамсаргүй түлхүүр биш тогтмолыг сонгосон
    # шалтгаан: runserver нь файл засах бүрд дахин ачаалдаг тул санамсаргүй
    # түлхүүр бол хадгалах болгонд session тасарч, байнга дахин нэвтрэх болно.
    # Энэ утга production-д хэзээ ч хүрэхгүй — дээрх raise саатуулна.
    SECRET_KEY = 'django-insecure-dev-only-never-used-when-debug-is-false'

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]

# Render нь үйлчилгээний бодит домэйныг RENDER_EXTERNAL_HOSTNAME хувьсагчаар
# өөрөө өгдөг. render.yaml-д бичсэн нэр аль хэдийн эзэлэгдсэн байвал Render
# өөр домэйн (жишээ: capstone-expense-tracker-a1b2.onrender.com) оноодог —
# тэр үед ALLOWED_HOSTS/CSRF/CORS-ыг гараар засахгүйгээр өөрөө таарна.
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # local apps
    'static_app',
    'accounts',
    'category',
    'expenses',
    'budget',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # CORS middleware should be at the top
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For serving static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


import sys
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

# PaaS (Render, Railway, Koyeb) болон Neon зэрэг үүлэн Postgres нь холболтоо нэг
# DATABASE_URL мөрөөр өгдөг. Байвал дээрх DB_* хувьсагчдыг дарж бичнэ; байхгүй бол
# (локал, docker-compose) салангид хувьсагчид хэвээр ажиллана.
_database_url = os.environ.get('DATABASE_URL')
if _database_url:
    from urllib.parse import parse_qs, unquote, urlparse

    _u = urlparse(_database_url)
    _sslmode = (
        parse_qs(_u.query).get('sslmode', [None])[0]
        or os.environ.get('DB_SSLMODE', 'require')
    )
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': _u.path.lstrip('/'),
        'USER': unquote(_u.username or ''),
        'PASSWORD': unquote(_u.password or ''),
        'HOST': _u.hostname or '',
        'PORT': str(_u.port or 5432),
        # Хүсэлт бүрд шинээр холбогдохгүй, 60 секунд дахин ашиглана (үүлэн DB-д чухал)
        'CONN_MAX_AGE': 60,
        'OPTIONS': {'sslmode': _sslmode},
    }

    # Бүтэн бус URL-ийг ДУУГҮЙ хүлээж авбал алдаа хожим, танихад бэрх хэлбэрээр
    # гардаг: Django "settings.DATABASES is improperly configured. Please supply
    # the NAME value" гэсэн 40 мөр traceback өгөх бөгөөд тэр нь `DATABASE_URL`-ийг
    # хуулахдаа сүүлийг тасалсан гэдгийг хэлж чадахгүй. Тиймээс энд шалгаж,
    # яг юу дутууг нэрлэнэ. Нууц үгийг хэвлэхгүй.
    _missing = [k for k in ('NAME', 'HOST', 'USER') if not DATABASES['default'][k]]
    if _missing:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(
            'DATABASE_URL-ийг задлахад {} дутуу гарлаа. Хүлээж байгаа хэлбэр:\n'
            '  postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require\n'
            'Холболтын мөрийг бүтнээр хуулсан эсэхээ шалгана уу — өгөгдлийн сангийн '
            'нэр (жишээ: /neondb) болон ?sslmode=require сүүл байх ёстой.\n'
            'Одоогийн задлалт: USER={!r}, HOST={!r}, NAME={!r} (нууц үг хэвлэгдэхгүй).'
            .format(
                ', '.join(_missing),
                DATABASES['default']['USER'],
                DATABASES['default']['HOST'],
                DATABASES['default']['NAME'],
            )
        )

if os.environ.get('USE_SQLITE') == 'True' or 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'mn'

TIME_ZONE = 'Asia/Ulaanbaatar'

USE_I18N = True

USE_TZ = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise: статик файлуудыг gzip/brotli шахаж кэштэй үйлчилнэ. Manifest-гүй хувилбар —
# template-д дурдсан файл олдохгүй байсан ч collectstatic унахгүй (deploy аюулгүй).
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (user-uploaded content)
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = Path(os.getenv('MEDIA_ROOT', BASE_DIR / 'media'))

AUTH_USER_MODEL = 'accounts.CustomUser'

# Нэвтрэх хуудас нь accounts/urls.py-д `path('', ...)` дээр байдаг тул бодит зам нь
# `/accounts/`. Django-ийн анхдагч LOGIN_URL нь `/accounts/login/` — тэр зам энэ аппад
# БАЙХГҮЙ. Заагаагүй бол `@login_required` бүх view (26 байршил) нэвтрээгүй
# хэрэглэгчийг 404 руу шиддэг: session 30 минутын дараа дуусахад хэрэглэгч нэвтрэх
# формын оронд "Not Found" хардаг. Замын оронд URL-ийн НЭРийг өгсөн нь зам хожим
# өөрчлөгдвөл өөрөө дагаж зөв хэвээр байхын тулд.
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'user_dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#1 хөтөч хаагдах үед шууд logout хийх
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 1800 #30 минут болоод автоматаар logout хийнэ
SESSION_SAVE_EVERY_REQUEST = True #хэрэглэгч ямар нэгэн үйлдэл хийх бүрт сешн хугацааг сунгана

# Email Configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CORS: production-д зөвхөн CORS_ALLOWED_ORIGINS-д таслалаар жагсаасан origin-ууд
# (жишээ: https://app.example.com,https://example.com). DEBUG үед, жагсаалт өгөөгүй бол
# бүгдийг нээнэ — локал Flutter/вэб хөгжүүлэлтэд.
CORS_ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()
]
CORS_ALLOW_ALL_ORIGINS = DEBUG and not CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = True

# Admin болон формуудын CSRF нь https origin-ийг ил зөвшөөрөхийг шаарддаг
# (жишээ: https://capstone-expense-tracker.onrender.com).
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()
]

# Дээрх ALLOWED_HOSTS-тэй ижил шалтгаанаар Render-ийн домэйныг origin болгож нэмнэ.
if RENDER_EXTERNAL_HOSTNAME:
    _render_origin = f'https://{RENDER_EXTERNAL_HOSTNAME}'
    if _render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_render_origin)
    if _render_origin not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(_render_origin)

# Production (DEBUG=False): PaaS нь HTTPS-ийг өөрийн proxy дээр тайлж, Django руу
# http-ээр дамжуулдаг тул X-Forwarded-Proto толгойд итгэнэ; cookie-г зөвхөн https-ээр.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True') == 'True'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '3600'))
    # Health check нь платформын дотоод prober-оос http-ээр, X-Forwarded-Proto
    # толгойгүй ирж болдог. Redirect-ээс чөлөөлөөгүй бол 301 хариу авч,
    # Render үйлчилгээг "unhealthy" гэж тооцох эрсдэлтэй. Зам нь урд налуугүй.
    SECURE_REDIRECT_EXEMPT = [r'^healthz/$']
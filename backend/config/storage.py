"""
Media (аватар, баримтын зураг)-г S3-төст bucket-д хадгалах storage.

Render-ийн үнэгүй instance-ийн диск deploy, restart болон 15 минут идэвхгүй
болж унтах бүрд цэвэрлэгддэг тул production-д зураг хадгалах газар тусдаа
байх ёстой. S3 протоколоор ажилладаг ямар ч үйлчилгээ тохирно (Backblaze B2,
Cloudflare R2, AWS S3) — суурь нь django-storages-ийн `S3Storage`.

Ганц ялгаа: `url()` нь bucket-ийн (гарын үсэгтэй) шууд хаяг БИШ, `/media/<нэр>`
буцаана. Ингэснээр:
  • bucket бүрэн хаалттай үлдэнэ (нийтэд нээх шаардлагагүй, CORS хэрэггүй);
  • хүсэлт бүр `config.views.protected_media`-гийн `may_view()` шалгалтаар
    дамжина — "баримтыг зөвхөн эзэн + админ харна" дүрэм хэвээр;
  • template-д `.url` ашигладаг газрууд өөрчлөгдөхгүй.
Файлыг Django өөрөө bucket-оос уншиж дамжуулна (`protected_media`-г үз).
Асаах тохиргоо: settings.py дахь `MEDIA_S3_*` орчны хувьсагчид.
"""

from django.conf import settings
from django.utils.encoding import filepath_to_uri
from storages.backends.s3 import S3Storage


class ProtectedS3Storage(S3Storage):
    def url(self, name, parameters=None, expire=None, http_method=None):
        base = settings.MEDIA_URL
        if not base.endswith('/'):
            base += '/'
        return base + filepath_to_uri(name)

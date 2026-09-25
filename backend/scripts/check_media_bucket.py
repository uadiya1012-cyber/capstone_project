#!/usr/bin/env python
"""
Media bucket-ийн түлхүүрийг Render-д оруулахаас ӨМНӨ локалаас шалгана.

Хэрэглээ (backend/ дотроос):
    .venv/bin/python scripts/check_media_bucket.py

Утгуудыг асууж авна (manage_prod.sh-тэй ижил шалтгаанаар: командын мөрөнд
бичвэл shell-ийн түүхэнд үлдэнэ, .env-д хийвэл локал runserver ч bucket
руу бичиж эхэлнэ). Зөвхөн энэ процессийн орчинд амьдарна.

Юу хийдэг вэ: bucket-д `healthcheck/<цаг>.txt` гэсэн жижиг файл бичиж,
буцааж уншиж, URL нь /media/... эсэхийг, дараа нь устгагдсаныг шалгана.
Бүгд ✓ бол Render → Environment-д оруулах нэр/утгын жагсаалтыг хэвлэнэ
(нууц түлхүүр далдлагдсан).
"""

import getpass
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def ask(label: str, secret: bool = False) -> str:
    prompt = f'{label}: '
    value = getpass.getpass(prompt) if secret else input(prompt)
    return value.strip()


def main() -> int:
    if not os.getenv('MEDIA_S3_BUCKET'):
        print(
            '┌──────────────────────────────────────────────────────────────────┐\n'
            '│ Bucket-ийн тохиргоог асууна. Нууц түлхүүр буулгахад харагдахгүй. │\n'
            '│ R2: endpoint https://<account_id>.r2.cloudflarestorage.com, бүс auto │\n'
            '│ B2: endpoint https://s3.<бүс>.backblazeb2.com, бүс = тэр <бүс>       │\n'
            '└──────────────────────────────────────────────────────────────────┘'
        )
        os.environ['MEDIA_S3_BUCKET'] = ask('Bucket-ийн нэр')
        # Dashboard-оос хуулахад төгсгөлд нь '/' эсвэл '/bucket-нэр' дагалдаж ирдэг —
        # хоёулаа гарын үсгийн алдаа (SignatureDoesNotMatch) үүсгэдэг тул цэвэрлэнэ.
        endpoint = ask('Endpoint URL (https://...)').rstrip('/')
        bucket = os.environ['MEDIA_S3_BUCKET']
        if endpoint.endswith('/' + bucket):
            endpoint = endpoint[: -len(bucket) - 1]
            print(f'  (endpoint-ийн төгсгөлөөс /{bucket}-г хасав)')
        os.environ['MEDIA_S3_ENDPOINT_URL'] = endpoint
        region = ask('Бүс (R2 → auto; B2 → us-west-004 г.м.; хоосон = алгасах)')
        if region:
            os.environ['MEDIA_S3_REGION'] = region
        os.environ['MEDIA_S3_ACCESS_KEY'] = ask('Access key ID')
        os.environ['MEDIA_S3_SECRET_KEY'] = ask('Secret access key', secret=True)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django

    django.setup()
    from django.core.files.storage import storages

    from config.media_check import round_trip

    steps = round_trip(storages['default'])
    print()
    for step in steps:
        mark = '✓' if step.ok else '✗'
        print(f'  {mark} {step.name:<8} {step.detail}')
    print()

    if not all(step.ok for step in steps):
        print('Тохиргоо бүрэн зөв биш — дээрх тайлбарын дагуу засаад дахин ажиллуул.')
        return 1

    secret = os.environ['MEDIA_S3_SECRET_KEY']
    print('Бүгд зөв. Render → Environment-д ЯГ эдгээр нэрээр оруулна:')
    print(f'  MEDIA_S3_BUCKET        = {os.environ["MEDIA_S3_BUCKET"]}')
    print(f'  MEDIA_S3_ENDPOINT_URL  = {os.environ["MEDIA_S3_ENDPOINT_URL"]}')
    if os.getenv('MEDIA_S3_REGION'):
        print(f'  MEDIA_S3_REGION        = {os.environ["MEDIA_S3_REGION"]}')
    print(f'  MEDIA_S3_ACCESS_KEY    = {os.environ["MEDIA_S3_ACCESS_KEY"]}')
    print(f'  MEDIA_S3_SECRET_KEY    = ****{secret[-4:]}  (бүтнээр нь өөрөө буулгана)')
    print('Хадгалахад Render автоматаар дахин deploy хийнэ; дараа нь аватар солиод шалга.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

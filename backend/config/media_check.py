"""
Media bucket-ийн холболтыг БОДИТ объектоор шалгах.

`scripts/check_media_bucket.py` энэ модулийг ашиглана: Render-д түлхүүр
оруулахаас өмнө локалаас нэг жижиг файл бичиж, уншиж, устгаж үзнэ. Ингэснээр
"deploy хийсэн, зураг оруулахад 500" гэсэн хамгийн муу мөчид биш, өмнө нь
алдаагаа олно. Алдааны кодыг хүний хэлээр тайлбарлана (`describe`).
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage


@dataclass
class Step:
    name: str
    ok: bool
    detail: str = ''


def describe(error: Exception) -> str:
    """boto3/botocore-ийн алдааг тохиргооны аль утга буруу байгаад чиглүүлж тайлбарлана."""
    code = ''
    response = getattr(error, 'response', None)
    if isinstance(response, dict):
        code = str(response.get('Error', {}).get('Code', ''))
    hints = {
        'InvalidAccessKeyId': 'Access key ID буруу (MEDIA_S3_ACCESS_KEY)',
        'SignatureDoesNotMatch': 'Нууц түлхүүр (MEDIA_S3_SECRET_KEY) эсвэл бүс (MEDIA_S3_REGION) буруу',
        'AccessDenied': 'Түлхүүр энэ bucket-д унших/бичих эрхгүй — bucket-д зориулсан Read & Write түлхүүр үүсгэ',
        'NoSuchBucket': 'Ийм нэртэй bucket алга (MEDIA_S3_BUCKET) — нэрийг яг хуул',
        'InvalidBucketName': 'Bucket-ийн нэр буруу хэлбэртэй (MEDIA_S3_BUCKET)',
        # HEAD хүсэлт (exists) хариугаа тайлбаргүй буцаадаг тул код нь зөвхөн HTTP статус болдог.
        '403': 'Хандалт татгалзагдав (403). Элбэг шалтгаан: нууц түлхүүр харагдахгүй горимд дутуу/буруу буулгагдсан; '
               'бусад: token энэ bucket-д эрхгүй, endpoint буруу',
        '401': 'Нэвтрэлт татгалзагдав (401): access key эсвэл нууц түлхүүр буруу',
    }
    if code in hints:
        return f'{hints[code]} [{code}]'
    name = type(error).__name__
    if name in ('EndpointConnectionError', 'ConnectionError', 'gaierror'):
        return f'Endpoint URL-д холбогдож чадсангүй (MEDIA_S3_ENDPOINT_URL) эсвэл интернет алга [{name}]'
    if code:
        return f'{code}: {error}'
    return f'{name}: {error}'


def round_trip(storage) -> list[Step]:
    """
    bucket ↔ Django хоёрын хооронд нэг файлын бүтэн эргэлт: бичих → унших → URL → устгах.

    FileSystemStorage бол шалгах зүйл байхгүй — MEDIA_S3_BUCKET өгөгдөөгүй гэсэн үг.
    """
    if isinstance(storage, FileSystemStorage):
        return [Step('storage', False, 'MEDIA_S3_BUCKET өгөгдөөгүй — локал диск ашиглаж байна, bucket шалгах зүйл алга')]

    steps = [Step('storage', True, type(storage).__name__)]

    # Бичихээс өмнө bucket-ийн жагсаалтыг нэг удаа асууна: энэ хүсэлт хариугаа
    # тайлбартай буцаадаг тул түлхүүр буруу, гарын үсэг зөрсөн, эрхгүй гэдгийг
    # ялгаж хэлнэ (HEAD бол зөвхөн 403 гэж хэлээд дуугүй байдаг).
    bucket = getattr(storage, 'bucket_name', None)
    connection = getattr(storage, 'connection', None) if bucket else None
    if connection is not None:
        try:
            connection.meta.client.list_objects_v2(Bucket=bucket, MaxKeys=1)
            steps.append(Step('холболт', True, f'bucket «{bucket}» руу нэвтэрлээ'))
        except Exception as error:  # noqa: BLE001
            steps.append(Step('холболт', False, describe(error)))
            return steps

    name = f'healthcheck/{datetime.now(timezone.utc):%Y%m%dT%H%M%S}.txt'
    payload = b'capstone media bucket check'

    try:
        saved = storage.save(name, ContentFile(payload))
        steps.append(Step('бичих', True, saved))
    except Exception as error:  # noqa: BLE001 — ямар ч алдааг тайлбарлаж харуулна
        steps.append(Step('бичих', False, describe(error)))
        return steps

    try:
        with storage.open(saved, 'rb') as handle:
            data = handle.read()
        steps.append(Step('унших', data == payload, '' if data == payload else 'уншсан агуулга бичсэнээс зөрөв'))
    except Exception as error:  # noqa: BLE001
        steps.append(Step('унших', False, describe(error)))

    url = storage.url(saved)
    steps.append(Step('url', url.startswith('/media/'), url))

    try:
        storage.delete(saved)
        gone = not storage.exists(saved)
        steps.append(Step('устгах', gone, '' if gone else 'устгасны дараа ч байсаар байна'))
    except Exception as error:  # noqa: BLE001
        steps.append(Step('устгах', False, describe(error)))

    return steps

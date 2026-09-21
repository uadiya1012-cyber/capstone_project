# Backend image — локал (docker-compose runserver-ээр дарж ажиллуулна) ба production
# (Render г.м. PaaS: CMD нь start.sh → migrate, collectstatic, gunicorn).
# Python-ы хувилбарыг .venv-тэй ижил байлгав (3.14) — ингэснээр container
# дотор ажиллах болон host дээр шууд ажиллуулах хоёр ижил зан төлөвтэй болно.
FROM python:3.14-slim

# PYTHONDONTWRITEBYTECODE: .pyc файл үүсгэхгүй (bind mount дээр хог үлдээхгүй)
# PYTHONUNBUFFERED: log-ийг шууд гаргана, буферт саатуулахгүй
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# requirements-ийг кодоос ТУСДАА эхэлж хуулав. Ингэснээр код засах бүрд
# Docker layer cache эвдрэхгүй — зөвхөн requirements.txt өөрчлөгдсөн үед
# л pip install дахин ажиллана.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Container ДОТОР стандарт 8000. Host руу зарлах дугаарыг
# docker-compose.yml шийднэ.
EXPOSE 8000

CMD ["sh", "start.sh"]

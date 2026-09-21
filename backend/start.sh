#!/bin/sh
# Production эхлүүлэгч (PaaS / Docker). Локал хөгжүүлэлтэд docker-compose.yml
# энэ файлыг ашиглахгүй, runserver-ээ өөрөө ажиллуулдаг.
#
#   1. migrate      — өгөгдлийн сангийн бүтцийг шинэчилнэ
#   2. collectstatic — статик файлуудыг STATIC_ROOT руу цуглуулна (WhiteNoise үйлчилнэ)
#   3. gunicorn     — PaaS-ийн өгсөн $PORT дээр (байхгүй бол 8000)
#
# exec ашигласнаар gunicorn нь PID 1 болж, платформын SIGTERM-ийг шууд хүлээн авна.
set -e
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -

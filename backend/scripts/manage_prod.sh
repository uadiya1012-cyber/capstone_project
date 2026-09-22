#!/bin/bash
# Production-ын өгөгдлийн сан (Neon) дээр manage.py тушаал ажиллуулна.
#
# Хэрэгцээ: Render-ийн үнэгүй багцад Shell байхгүй. Харин Neon нь интернетэд
# нээлттэй тул локал машинаас шууд холбогдож болно — админ үүсгэх, өгөгдөл
# шалгах зэрэг нэг удаагийн ажилд хангалттай.
#
# Хэрэглээ:
#   ./scripts/manage_prod.sh createsuperuser
#   ./scripts/manage_prod.sh showmigrations
#   ./scripts/manage_prod.sh shell
#
# ЯАГААД DATABASE_URL-ийг АСУУДАГ ВЭ:
#   1. Командын мөрөнд бичвэл shell-ийн түүхэнд (~/.zsh_history) нууц үг тэй
#      хамт бүртгэгдэж, тэндээ үлддэг.
#   2. `.env` файлд хийвэл settings.py-ийн load_dotenv() түүнийг локал
#      хөгжүүлэлтэд ч ачаална — `runserver` санамсаргүйгээр PRODUCTION санг
#      ашиглаж эхэлнэ. Энэ бол хамгийн хорт төрлийн алдаа.
#   Тиймээс зөвхөн энэ процессийн орчинд, асууж авна.

set -e
cd "$(dirname "$0")/.."

PY=.venv/bin/python
[ -x "$PY" ] || PY=python3

printf 'Neon-ийн DATABASE_URL (харагдахгүй): '
read -rs DATABASE_URL
echo
export DATABASE_URL

if [ -z "$DATABASE_URL" ]; then
  echo "❌ Хоосон байна. Neon → Connect → Pooled connection-ээс хуулна." >&2
  exit 1
fi

# DEBUG=False үед settings.py нь SECRET_KEY-г шаарддаг. Энэ тушаалын хүрээнд
# SECRET_KEY нь ямар ч хадгалагдах өгөгдөлд нөлөөлөхгүй — тэр нь session болон
# CSRF token-д гарын үсэг зурахад хэрэглэгддэг бөгөөд CLI тушаал тэднийг
# үүсгэдэггүй. Нууц үг нь PBKDF2 + хэрэглэгч тус бүрийн salt-аар хэшлэгддэг,
# SECRET_KEY-гээс хамаардаггүй. Тиймээс түр санамсаргүй утга аюулгүй.
export DEBUG=False
export SECRET_KEY="$("$PY" -c 'from django.core.management.utils import get_random_secret_key as g; print(g())')"

echo "→ $* (production DB дээр)"
exec "$PY" manage.py "$@"

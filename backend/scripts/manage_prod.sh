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
#   ./scripts/manage_prod.sh shell -c "..."
#
# ЯАГААД DATABASE_URL-ийг АСУУДАГ ВЭ:
#   1. Командын мөрөнд бичвэл shell-ийн түүхэнд (~/.zsh_history) нууц үгтэй
#      хамт бүртгэгдэж, тэндээ үлддэг.
#   2. `.env` файлд хийвэл settings.py-ийн load_dotenv() түүнийг локал
#      хөгжүүлэлтэд ч ачаална — `runserver` санамсаргүйгээр PRODUCTION санг
#      ашиглаж эхэлнэ. Энэ бол хамгийн хорт төрлийн алдаа.
#   Тиймээс зөвхөн энэ процессийн орчинд, асууж авна.

set -e
cd "$(dirname "$0")/.."

PY=.venv/bin/python
[ -x "$PY" ] || PY=python3

cat <<'HINT'
┌─────────────────────────────────────────────────────────────────────┐
│ Доор асуух зүйл нь ТАНЫ нууц үг БИШ.                                │
│ Өгөгдлийн сангийн холболтын мөр — postgresql:// гэж эхлэх урт мөр.  │
│                                                                     │
│ Хаанаас авах:                                                       │
│   Render → үйлчилгээ → Environment → DATABASE_URL → copy            │
│   (эсвэл Neon → Connect → Pooled connection)                        │
│                                                                     │
│ Буулгахад дэлгэц дээр ЮУ Ч ХАРАГДАХГҮЙ (⌘V, дараа нь Enter).        │
│ Дараа нь зөв орсон эсэхийг нууц үггүйгээр доор харуулна.            │
└─────────────────────────────────────────────────────────────────────┘
HINT
printf 'Холболтын мөр (postgresql://...): '
read -rs DATABASE_URL
echo

# Урд/хойно санамсаргүй орсон хоосон зай, хашилтыг цэвэрлэнэ. Copy/paste-ээр
# мөрийн төгсгөлийн зай, хааяа хашилт хамт ирдэг.
DATABASE_URL="$(printf '%s' "$DATABASE_URL" | tr -d '[:space:]' | sed "s/^['\"]//;s/['\"]$//")"
export DATABASE_URL

# Django-г ачаалахаас ӨМНӨ хэлбэрийг шалгаж, юу хүлээн авсныг нууц үггүйгээр
# харуулна. Оролт нуугдмал байх нь "paste хийгдсэн үү?" гэсэн тодорхойгүй
# байдал үүсгэдэг тул баталгаажуулах цонх нээлттэй байх нь чухал.
"$PY" - <<'PYEOF' || exit 1
import os, sys
from urllib.parse import urlparse

raw = os.environ.get('DATABASE_URL', '')
if not raw:
    sys.exit('❌ Хоосон байна. Neon → Connect → Pooled connection-ээс хуулна.')

u = urlparse(raw)
missing = [n for n, v in (('scheme', u.scheme), ('USER', u.username),
                          ('HOST', u.hostname), ('DBNAME', u.path.lstrip('/')))
           if not v]
print('Хүлээн авсан (нууц үг нуусан):')
print(f"  {u.scheme or '???'}://{u.username or '???'}:***@"
      f"{u.hostname or '???'}/{u.path.lstrip('/') or '???'}"
      f"{'?' + u.query if u.query else ''}")
if missing:
    sys.exit(f"\n❌ {', '.join(missing)} дутуу — URL бүтэн буулгагдаагүй байна.\n"
             "   Хүлээж байгаа хэлбэр:\n"
             "   postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require")
if '-pooler' not in (u.hostname or ''):
    print('  ⚠️  hostname-д "-pooler" байхгүй — direct холболт байж магадгүй '
          '(ажиллана, гэхдээ Neon pooled-ийг зөвлөдөг).')
print('  ✅ Хэлбэр зөв.')
PYEOF

# DEBUG=False үед settings.py нь SECRET_KEY-г шаарддаг. Энэ тушаалын хүрээнд
# SECRET_KEY нь ямар ч хадгалагдах өгөгдөлд нөлөөлөхгүй — тэр нь session болон
# CSRF token-д гарын үсэг зурахад хэрэглэгддэг бөгөөд CLI тушаал тэднийг
# үүсгэдэггүй. Нууц үг нь PBKDF2 + хэрэглэгч тус бүрийн salt-аар хэшлэгддэг,
# SECRET_KEY-гээс хамаардаггүй. Тиймээс түр санамсаргүй утга аюулгүй.
export DEBUG=False
export SECRET_KEY="$("$PY" -c 'from django.core.management.utils import get_random_secret_key as g; print(g())')"

echo
echo "→ manage.py $* (production DB дээр)"
exec "$PY" manage.py "$@"

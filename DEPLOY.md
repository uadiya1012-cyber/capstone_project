# Production-д байрлуулах — Render + Neon (үнэгүй)

Backend (Django) нь **Render**-ийн үнэгүй web service дээр Docker-оор, өгөгдлийн сан нь
**Neon**-ийн үнэгүй Postgres дээр ажиллана. Хоёулаа карт шаардахгүй. Кодын бэлтгэл
(`render.yaml`, `backend/start.sh`, `DATABASE_URL`, CORS/HTTPS тохиргоо) бэлэн — доорх
алхмуудыг дарааллаар нь хийхэд л болно.

## 1. Neon — үнэгүй Postgres

1. https://neon.tech → GitHub-аар бүртгүүл → **New project** (нэр: `capstone`, бүс: Frankfurt эсвэл Singapore).
2. Dashboard → **Connect** → *Pooled connection*-г сонгоод холболтын мөрийг хуул:
   `postgresql://<user>:<password>@<ep-xxx>.neon.tech/neondb?sslmode=require`
   Энэ мөр бол `DATABASE_URL`. Хэнд ч бүү харуул, git-д бүү оруул.

## 2. Render — web service (Blueprint)

1. https://render.com → GitHub-аар бүртгүүл → **New → Blueprint** → `capstone_project` репог сонго.
2. Render `render.yaml`-ийг уншиж **capstone-expense-tracker** үйлчилгээг санал болгоно.
   `DATABASE_URL` асуухад Neon-ийн мөрийг оруул. `SECRET_KEY`-г Render өөрөө санамсаргүй үүсгэнэ.
3. **Apply** → Docker build 3–5 мин → `backend/start.sh` ажиллана: `migrate` → `collectstatic` → `gunicorn`.
4. https://capstone-expense-tracker.onrender.com/admin/login/ нээгдэж байвал амжилттай.
   Үйлчилгээний нэр өөр байвал (`xxx.onrender.com`) **Environment** хэсэгт `ALLOWED_HOSTS`,
   `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS` гурвыг шинэ домэйнд тааруул.
5. Админ хэрэглэгч: Render → **Shell** → `python manage.py createsuperuser`
   (эсвэл `python setup_and_init.py` — жишээ хэрэглэгч, өгөгдөлтэй).

## 3. Flutter клиент

Backend-ийн хаягийг build үед өгнө (`lib/services/api_service.dart` → `String.fromEnvironment`):

```bash
# Production
flutter build apk --dart-define=API_BASE_URL=https://capstone-expense-tracker.onrender.com/api/v1

# Android emulator дээр локал backend (docker compose → host 8020)
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8020/api/v1
```

Өгөөгүй бол `http://127.0.0.1:8000/api/v1` (iOS simulator, desktop).

## 4. Орчны хувьсагчид

| Нэр | Утга | Тайлбар |
|---|---|---|
| `DEBUG` | `False` | Production-д заавал |
| `SECRET_KEY` | Render үүсгэнэ | 50+ тэмдэгт; хуучин ил гарсан түлхүүрийг хэзээ ч бүү ашигла |
| `ALLOWED_HOSTS` | `capstone-expense-tracker.onrender.com` | Таслалаар олон домэйн |
| `CSRF_TRUSTED_ORIGINS` | `https://capstone-expense-tracker.onrender.com` | Admin, формуудад |
| `CORS_ALLOWED_ORIGINS` | `https://...` | Вэб клиент байвал; Flutter native апп CORS шаарддаггүй |
| `DATABASE_URL` | Neon-ийн мөр | `?sslmode=require` байвал хэрэглэнэ, үгүй бол `DB_SSLMODE` (анхдагч `require`) |
| `WEB_CONCURRENCY` | `2` | gunicorn worker (үнэгүй 512 MB-д 2 хангалттай) |
| `SECURE_SSL_REDIRECT` | `True` (анхдагч) | http → https |

## 5. Анхаарах зүйлс

- **Унтах:** үнэгүй Render 15 минут хүсэлтгүй бол унтдаг, эхний хүсэлт 30–50 секунд. Neon-ийн
  compute ч 5 минутын дараа унтдаг (сэрэхэд ~1 сек).
- **Media (баримтын зураг):** Render-ийн үнэгүй дискэнд түр хадгалагдаж, deploy бүрд устна.
  Хэрэгтэй бол Cloudinary/S3 руу шилжүүлнэ (ирээдүйн ажил).
- **Локал production симуляци** (бодит нууц үггүй):
  `DEBUG=False SECRET_KEY=<түр> DATABASE_URL=<Neon> python manage.py check --deploy`
- Локал хөгжүүлэлт өөрчлөгдөөгүй: `docker compose up` (runserver, DEBUG=True, порт 8020).

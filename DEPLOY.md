# Production-д байрлуулах — Render + Neon (үнэгүй)

Backend (Django) нь **Render**-ийн үнэгүй web service дээр Docker-оор, өгөгдлийн сан нь
**Neon**-ийн үнэгүй Postgres дээр ажиллана. Хоёулаа карт шаардахгүй. Кодын бэлтгэл
(`render.yaml`, `backend/start.sh`, `DATABASE_URL`, CORS/HTTPS тохиргоо) бэлэн — доорх
алхмуудыг дарааллаар нь хийхэд л болно.

## 1. Neon — үнэгүй Postgres

1. https://neon.tech → GitHub-аар бүртгүүл → **New project** (нэр: `capstone`,
   бүс: **AWS Asia Pacific 1 (Singapore)**). Бүс нь `render.yaml`-ийн `region: singapore`-тэй
   ижил байх ЗААВАЛ шаардлагатай — өөр тив дээр байвал query бүр далай гаталж хоцрогдоно.
   Postgres хувилбар 18, database нэр `neondb` (анхдагч) хэвээр. Бусад үйлчилгээ (Object
   storage, Functions, AI gateway, Neon Auth) хэрэггүй — унтраасан хэвээр үлдээ.
2. Dashboard → **Connect** → *Pooled connection*-г сонгоод холболтын мөрийг хуул:
   `postgresql://<user>:<password>@<ep-xxx>.neon.tech/neondb?sslmode=require`
   Энэ мөр бол `DATABASE_URL`. Хэнд ч бүү харуул, git-д бүү оруул.

## 2. Render — web service (Blueprint)

1. https://render.com → GitHub-аар бүртгүүл → **New → Blueprint** → `capstone_project` репог сонго.
2. Render `render.yaml`-ийг уншиж **capstone-expense-tracker** үйлчилгээг санал болгоно.
   `DATABASE_URL` асуухад Neon-ийн мөрийг оруул. `SECRET_KEY`-г Render өөрөө санамсаргүй үүсгэнэ.
3. **Apply** → Docker build 3–5 мин → `backend/start.sh` ажиллана: `migrate` → `collectstatic` → `gunicorn`.
   Render `/healthz/` замаар эрүүл мэндийг шалгана (өгөгдлийн санд хандахгүй хөнгөн endpoint —
   Neon унтсан байсан ч deploy унахгүй).
4. https://capstone-expense-tracker.onrender.com/admin/login/ нээгдэж байвал амжилттай.
   Үйлчилгээний нэр эзэлэгдсэн байж Render өөр домэйн оноовол (`xxx.onrender.com`) **гараар засах
   шаардлагагүй** — Django нь Render-ийн `RENDER_EXTERNAL_HOSTNAME` хувьсагчийг уншиж
   `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS` гуравт өөрөө нэмнэ.
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
| `ALLOWED_HOSTS` | `capstone-expense-tracker.onrender.com` | Таслалаар олон домэйн. Render-ийн `RENDER_EXTERNAL_HOSTNAME` автоматаар нэмэгдэнэ |
| `CSRF_TRUSTED_ORIGINS` | `https://capstone-expense-tracker.onrender.com` | Admin, формуудад |
| `CORS_ALLOWED_ORIGINS` | `https://...` | Вэб клиент байвал; Flutter native апп CORS шаарддаггүй |
| `DATABASE_URL` | Neon-ийн мөр | `?sslmode=require` байвал хэрэглэнэ, үгүй бол `DB_SSLMODE` (анхдагч `require`) |
| `WEB_CONCURRENCY` | `2` | gunicorn worker (үнэгүй 512 MB-д 2 хангалттай) |
| `SECURE_SSL_REDIRECT` | `True` (анхдагч) | http → https |

## 5. Анхаарах зүйлс

- **Унтах:** үнэгүй Render 15 минут хүсэлтгүй бол унтдаг, эхний хүсэлт 30–50 секунд. Neon-ийн
  compute ч 5 минутын дараа унтдаг (сэрэхэд ~1 сек).
- **Media (аватар, баримтын зураг):** `/media/...` замыг production-д `config/views.py`-ийн
  `protected_media` view үйлчилнэ — нэвтрэлт шаардаж, `may_view()` дотор эзэмшлийг шалгана
  (баримт бол хувийн санхүүгийн бичиг баримт тул зөвхөн эзэн + админ харна). Гэхдээ **файлууд
  Render-ийн үнэгүй дискэнд түр хадгалагдаж, deploy бүрд устдаг** — тогтвортой хадгалалт
  хэрэгтэй бол Cloudinary/S3 руу шилжүүлнэ (ирээдүйн ажил).
- **Локал production симуляци** (бодит нууц үггүй):
  `DEBUG=False SECRET_KEY=<түр> DATABASE_URL=<Neon> python manage.py check --deploy`
- Локал хөгжүүлэлт өөрчлөгдөөгүй: `docker compose up` (runserver, DEBUG=True, порт 8020).

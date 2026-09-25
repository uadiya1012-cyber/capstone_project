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
4. `https://<үйлчилгээний нэр>.onrender.com/healthz/` нь `ok` буцааж байвал амжилттай.
   Одоогийн live: **https://capstone-expense-tracker-c9g1.onrender.com** (нэр эзэлэгдсэн тул
   Render `-c9g1` дагавар нэмсэн).
   Үйлчилгээний нэр эзэлэгдсэн байж Render өөр домэйн оноовол (`xxx.onrender.com`) **гараар засах
   шаардлагагүй** — Django нь Render-ийн `RENDER_EXTERNAL_HOSTNAME` хувьсагчийг уншиж
   `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS` гуравт өөрөө нэмнэ.
5. Админ хэрэглэгч — **үнэгүй багцад Render Shell байхгүй** (Starter-ээс дээш), харин Neon
   интернетэд нээлттэй тул локал машинаас production DB дээр шууд ажиллуулна:
   ```bash
   cd backend
   ./scripts/manage_prod.sh createsuperuser
   ```
   Скрипт `DATABASE_URL`-ийг асууна (Render → Environment → `DATABASE_URL`-ээс хуулна; таны
   нууц үг биш). Оролт нуугдмал, харин буулгасны дараа нууц үгийг далдалж юу орсныг харуулна.
   Дараа нь аппын өөрийн эрхийн системд админ болгоно — `createsuperuser` нь `is_staff`-ийг
   тавьдаг ч `CustomUser.role`-ийг `USER` үлдээдэг, аппын `role_required` decorator
   зөвхөн `role`-ийг шалгадаг:
   ```bash
   ./scripts/manage_prod.sh shell -c "
   from accounts.models import CustomUser
   u = CustomUser.objects.get(username='НЭР'); u.role = 'ADMIN'; u.save()"
   ```
   ⚠️ `setup_and_init.py`-г **live дээр бүү ажиллуул**: `bob_admin` / `Test1234!` (ADMIN) зэрэг
   нууц үг нь public репод ил бичигдсэн хэрэглэгчдийг үүсгэдэг. Зөвхөн локал/demo-д.

## 3. Flutter клиент

Backend-ийн хаягийг build үед өгнө (`lib/services/api_service.dart` → `String.fromEnvironment`):

```bash
# Production
flutter build apk --dart-define=API_BASE_URL=https://capstone-expense-tracker-c9g1.onrender.com/api/v1

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
| `MEDIA_S3_BUCKET` | bucket-ийн нэр | Өгвөл media bucket-д хадгалагдана (§6); өгөхгүй бол Render-ийн түр диск |
| `MEDIA_S3_ENDPOINT_URL` | `https://<account_id>.r2.cloudflarestorage.com` | R2, B2 зэрэг AWS биш үйлчилгээнд заавал |
| `MEDIA_S3_ACCESS_KEY` / `MEDIA_S3_SECRET_KEY` | bucket-ийн API түлхүүр | Зөвхөн энэ bucket-д эрхтэй түлхүүр үүсгэ |
| `MEDIA_S3_REGION` | `auto` (R2) / bucket-ийн бүс (B2) | Үйлчилгээний зааснаар; AWS-д бүсийн нэр |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | Gmail хаяг / app password | Бүртгүүлэх урсгалын баталгаажуулах захиа. Өгөхгүй бол зочин бүртгүүлж чадахгүй (нэвтрэх л ажиллана) |

## 5. Анхаарах зүйлс

- **Унтах:** үнэгүй Render 15 минут хүсэлтгүй бол унтдаг, эхний хүсэлт 30–50 секунд. Neon-ийн
  compute ч 5 минутын дараа унтдаг (сэрэхэд ~1 сек).
- **Media (аватар, баримтын зураг):** `/media/...` замыг production-д `config/views.py`-ийн
  `protected_media` view үйлчилнэ — нэвтрэлт шаардаж, `may_view()` дотор эзэмшлийг шалгана
  (баримт бол хувийн санхүүгийн бичиг баримт тул зөвхөн эзэн + админ харна). Өгөгдмөлөөр
  файлууд Render-ийн үнэгүй дискэнд түр хадгалагдана — **deploy, restart болон 15 минут
  идэвхгүй болж унтах бүрд устна** (Render-ийн баримт: үнэгүй instance-д persistent disk
  холбох боломжгүй). Тогтвортой хадгалалт: §6 — S3-төст bucket, код бэлэн.
- **Локал production симуляци** (бодит нууц үггүй):
  `DEBUG=False SECRET_KEY=<түр> DATABASE_URL=<Neon> python manage.py check --deploy`
- Локал хөгжүүлэлт өөрчлөгдөөгүй: `docker compose up` (runserver, DEBUG=True, порт 8020).

## 6. Media-г bucket-д — тогтвортой хадгалалт

Render-ийн үнэгүй instance persistent disk холбож чадахгүй тул аватар, баримтын зургийг
S3 протоколтой bucket-д хадгална (`config/storage.py`, `django-storages`). Код бэлэн:
bucket үүсгээд орчны хувьсагч өгөхөд л асна, өгөхгүй бол өмнөх шигээ түр дискэнд.

**Ямар үйлчилгээ:** үнэгүй багцтай хоёр сонголт, хоёулаа S3 API-тай:
- **Cloudflare R2** — 10 GB, гаралтын урсгал үнэгүй, bucket-ийг Азийн ойролцоо (APAC) байрлуулж
  болно (Render Singapore-той ойр). Асаахад Cloudflare төлбөрийн хэрэгсэл нэмэхийг шаардаж магадгүй
  (үнэгүй хязгаар дотор төлбөр гарахгүй). Endpoint `https://<account_id>.r2.cloudflarestorage.com`,
  бүс `auto`. ACL дэмждэггүй — энэ кодын тохиргоо ACL илгээдэггүй тул таарна.
- **Backblaze B2** — 10 GB, API дуудлага үнэгүй, карт шаардахгүй; харин дата төв нь АНУ/Европт тул
  зураг бүр далай гаталж ирнэ (Django дамжуулдаг учир ~0.3 с нэмэгдэнэ). Endpoint
  `https://s3.<бүс>.backblazeb2.com` (bucket-ийн хуудсанд бичээстэй), бүс = тэр `<бүс>`.

Bucket-ийг **private** үүсгэ. Нийтэд нээх, CORS тохируулах шаардлагагүй: Django файлыг өөрөө
уншиж `/media/...`-аар дамжуулдаг тул эрхийн шалгалт (`may_view`) хэвээр ажиллана, bucket-ийн
шууд хаяг хаана ч харагдахгүй.

1. Bucket үүсгэ (жишээ нь `capstone-media`), private.
2. Зөвхөн энэ bucket-д унших/бичих эрхтэй API түлхүүр (access key ID + secret) үүсгэ. Secret
   зөвхөн үүсгэх мөчид нэг удаа харагддаг — хуулж аваад аюулгүй газар түр хадгал.
3. **Түлхүүрээ локалаас шалга** (Render-д оруулахаас өмнө):
   ```bash
   cd backend && .venv/bin/python scripts/check_media_bucket.py
   ```
   Утгуудыг асууж аваад bucket-д жижиг файл бичиж, уншиж, устгана; алдаа гарвал аль утга
   буруу байгааг хэлнэ. Бүгд ✓ бол Render-д оруулах нэр/утгын жагсаалтыг хэвлэнэ.
4. Render → үйлчилгээ → Environment: `MEDIA_S3_BUCKET`, `MEDIA_S3_ENDPOINT_URL`,
   `MEDIA_S3_ACCESS_KEY`, `MEDIA_S3_SECRET_KEY`, шаардлагатай бол `MEDIA_S3_REGION`.
   Хадгалахад Render автоматаар дахин deploy хийнэ (2–4 мин).
5. Шалгах: нэвтэрч аватар солих → зураг харагдана; 15 минутаас удаан хүлээгээд (сервер унтаад
   сэрсний дараа) дахин нээхэд зураг хэвээр; bucket дотор `avatars/...` объект гарч ирнэ;
   `/media/avatars/...` хаягийг зочноор нээхэд нэвтрэх хуудас руу шилжүүлнэ.

Анхаар: bucket холбохоос өмнө оруулсан зургийн DB бичлэгүүд файлгүй үлдсэн (диск
цэвэрлэгдсэн) тул тэдгээр нь эвдэрсэн хэвээр харагдана — дахин оруулна. Түлхүүрийг
`.env`, git-д хэзээ ч бүү хий.


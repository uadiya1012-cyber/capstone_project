# [Expense Tracker (Зардлын Бүртгэл)] — Requirements

## 1. Төслийн Тойм

[Төслийн богино тайлбар]

- Expense Tracker нь хэрэглэгч өөрийн өдөр тутмын зардлыг бүртгэж, ангилж, сарын тайлан харах боломжтой web application юм.
- Хэрэглэгч зардлаа category-аар хувааж, нийт зарцуулалтаа хянах бөгөөд budget тогтоож, зардлаа удирдах боломжтой байна.

## 2. Хэрэглэгчид

- Хэн ашиглах вэ?
- Бүртгэлтэй хэрэглэгч
  - Бүртгүүлэх
  - Нэвтрэх
  - Зардал нэмэх, засах, устгах
  - Ангилал үүсгэх
  - Сарын тайлан харах
  - Budget тохируулах
  - бүртгэлтэй хэрэглэгч нь зардал хянах өөрийн зардал зэргээ тохируулах боломжтой

- Зочин хэрэглэгч
  - Зөвхөн register/login

## 3. Core Features (MVP)

- Feature 1: Authentication
  - register
  - login
  - logout
  - Хэрэглэгч бүр өөрийн зардлыг л харах (User-based data isolation)

- Feature 2: EXPENSE CRUD #1
  - Model: Expense
    - Created expense (amount, category, date, description)
    - Read expense list
    - Update expense list
    - Delete expense list
  - HTMX:
    - inline expense нэмэх
    - expense устгах
    - expense update хийх үед page reload хийгдэхгүй
- Feature 3: CATEGORY CRUD
  - Model: Category
    - Category үүсгэх
    - Category засах
    - Category устгах
    - Expense-г category-р шүүх
  - HTMX:
    - Category нэмэх үед page refresh хийхгүй
    - Category filter хийх
- Feature 4: Monthly Summary and Budget
  - Model: Budget(сарын төсөв)
    - Сарын нийт зардал харуулах
    - Category тус бүрийн нийлбэр
    - Butget тогтоох
    - Butget давсан эсэх харуулах
  - HTMX:
    - Month filter хийх
    - Budget update хийх

## 4. Tech Stack

- Backend: Django 5, Django Templates
- Interactivity: HTMX
- Styling: Pico CSS
- Database: PostgreSQL (Docker)
- Auth: Django built-in authentication

## 5. Хязгаарлалт

- Хугацаа: 4 долоо хоног
- Баг: Ганцаарчилсан

## 6. Амжилтын Шалгуур

- [ ] Auth ажиллаж байгаа
- [ ] CRUD #1 бүрэн
- [ ] CRUD #2 бүрэн
- [ ] Supporting feature бүрэн
- [ ] 3+ HTMX interaction
- [ ] Tests бичсэн
- [ ] Deploy хийсэн

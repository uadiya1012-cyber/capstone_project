# 📱 CAPSTONE PROJECT - EXPENSE TRACKER

> A Django-based web application for personal expense tracking, budget management, and financial planning.

**Status**: 🟢 Production Ready | 📅 Last Updated: March 13, 2026

---

## 🎯 Project Overview

**Expense Tracker** is a comprehensive web application that helps users:

- ✅ Track daily expenses with categories
- ✅ Create and manage budgets
- ✅ Monitor spending patterns
- ✅ Allocate budget to categories
- ✅ View financial summaries

### Key Features

- **User Authentication**: Secure login/registration with role-based access
- **Expense Tracking**: Add, edit, delete expenses with categories & dates
- **Budget Planning**: Create budgets with date ranges and allocations
- **Category Management**: Create custom categories or use global defaults
- **Quick Create**: Create category, budget, and expense in one atomic operation
- **Dashboard**: Real-time statistics and recent activity
- **Admin Panel**: Full control over users and data
- **Role-Based Access**: USER, MODERATOR, ADMIN roles with different permissions
- **File Upload**: Support for expense receipts (images)
- **Responsive Design**: Works on desktop, tablet, and mobile devices

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip & virtualenv

### Setup (5 minutes)

```bash
# 1. Navigate to backend directory
cd capstone-project/backend

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Run setup script (handles migrations + sample data)
python setup_and_init.py

# 4. Start development server
python manage.py runserver

# 5. Open browser
# Home: http://localhost:8000/
# Login: http://localhost:8000/accounts/
```

### Sample Users

```
Username: john_user
Password: Test1234!
Role: USER

Username: alice_moderator
Password: Test1234!
Role: MODERATOR

Username: bob_admin
Password: Test1234!
Role: ADMIN
```

### Health Check

```bash
# Verify system before starting
python health_check.py
```

---

## 📁 Project Structure

```
capstone-project/
├── backend/                          # Django backend
│   ├── config/                       # Settings & URL routing
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── accounts/                     # User authentication
│   │   ├── models.py                 # CustomUser model
│   │   ├── views.py                  # Auth & dashboard views
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── decorators.py             # Role-based access
│   ├── category/                     # Category management
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── forms.py
│   ├── expenses/                     # Expense tracking
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── forms.py
│   ├── budget/                       # Budget planning
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── forms.py
│   ├── static_app/                   # Landing pages
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── templates/
│   ├── static/                       # CSS, JS, images
│   │   └── css/
│   │       ├── pico.min.css
│   │       └── styles.css
│   ├── templates/                    # HTML templates
│   │   ├── base.html
│   │   ├── accounts/
│   │   ├── category/
│   │   ├── expenses/
│   │   ├── budget/
│   │   └── static_app/
│   ├── manage.py
│   ├── requirements.txt
│   ├── setup_and_init.py             # Initialization script
│   └── health_check.py               # Health verification script
└── Documentation/
    ├── QUICK_START.md                # Fast setup guide (YOU ARE HERE)
    ├── PROJECT_ARCHITECTURE.md       # Technical reference
    ├── VISUAL_DIAGRAMS.md            # Flow diagrams
    ├── INTEGRATION_CHECKLIST.md      # Testing guide
    ├── COMPLETE_SYSTEM_MAP.md        # System overview
    └── README_DOCUMENTATION.md       # Doc index
```

---

## 🗄️ Database Schema

### Main Models

- **CustomUser** - User accounts with roles (ADMIN, MODERATOR, USER)
- **Category** - Expense/income categories (user-specific or global)
- **Expense** - Individual transactions with amount, date, category
- **Budget** - Monthly/period budgets with allocations
- **BudgetAllocation** - Category-wise budget allocation

**Database**: PostgreSQL  
**Credentials**:

- Database: `capstone_db`
- User: `postgres`
- Password: `password` (change in production!)

---

## 🔗 URL Routes

### Public Routes

| Route                 | Purpose                 |
| --------------------- | ----------------------- |
| `/`                   | Home page with features |
| `/info/`              | About page              |
| `/contact/`           | Contact page            |
| `/accounts/`          | Login page              |
| `/accounts/register/` | User registration       |

### Authenticated Routes

| Route                     | Purpose                                   |
| ------------------------- | ----------------------------------------- |
| `/accounts/dashboard/`    | User dashboard                            |
| `/accounts/quick-create/` | Create category, budget, expense (3-in-1) |
| `/expenses/`              | List all expenses                         |
| `/expenses/create/`       | Create new expense                        |
| `/category/`              | List all categories                       |
| `/category/create/`       | Create new category                       |
| `/budget/`                | List all budgets                          |
| `/budget/create/`         | Create new budget                         |

### Admin Routes

| Route                       | Purpose             |
| --------------------------- | ------------------- |
| `/accounts/moderator/`      | Moderator dashboard |
| `/accounts/admin-settings/` | Admin settings      |
| `/admin/`                   | Django admin panel  |

---

## 🔐 Authentication & Authorization

### Roles & Permissions

| Feature                    | USER | MODERATOR | ADMIN |
| -------------------------- | ---- | --------- | ----- |
| View own data              | ✅   | ✅        | ✅    |
| Create items               | ✅   | ✅        | ✅    |
| Edit own items             | ✅   | ✅        | ✅    |
| Delete own items           | ❌   | ✅        | ✅    |
| Delete any items           | ❌   | ✅        | ✅    |
| Access moderator dashboard | ❌   | ✅        | ✅    |
| Access admin settings      | ❌   | ❌        | ✅    |
| User management            | ❌   | ❌        | ✅    |

### Data Isolation

- Each user only sees their own expenses, budgets, categories
- Global categories (user=NULL) visible to all users
- Admin/Moderator can view all users' data

---

## 📊 Common Workflows

### 1. Register & Create First Expense

```
Register → Logged In → Dashboard → Create Expense → View List → See Total
```

### 2. Quick Create (3-in-1)

```
Quick Create Page → Fill 3 Forms → Atomic Save → Dashboard Updates
```

### 3. Budget Planning

```
Create Budget → Add Allocations → Link Expenses → Monitor Progress
```

### 4. Category Management

```
Create Category → Use in Expenses → Filter by Category → View Stats
```

---

## 🧪 Testing

### Run Health Check

```bash
python health_check.py
```

### Run All Tests

```bash
python manage.py test
```

### Run Specific App Tests

```bash
python manage.py test accounts
python manage.py test expenses
python manage.py test budget
python manage.py test category
```

### Manual Testing

Refer to **INTEGRATION_CHECKLIST.md** for:

- 200+ test cases
- Role-based permission matrix
- CRUD operation verification
- Edge case testing

---

## 📦 Dependencies

### Core Libraries

```
Django==5.0.2
djangorestframework
django-cors-headers
psycopg2-binary              # PostgreSQL adapter
Pillow                       # Image handling
```

### Frontend

- Pico CSS (lightweight framework)
- HTML5 templates
- Responsive design

---

## 🛠️ Development Commands

```bash
# Database
python manage.py makemigrations
python manage.py migrate
python manage.py dbshell

# Server
python manage.py runserver
python manage.py runserver 0.0.0.0:8000

# Admin
python manage.py createsuperuser

# Shell
python manage.py shell

# Testing
python manage.py test
python manage.py test --keepdb

# Static files
python manage.py collectstatic
python manage.py collectstatic --clear --noinput

# Utilities
python manage.py check
python setup_and_init.py
python health_check.py
```

---

## 📈 Features in Detail

### Dashboard

- User statistics (expense count, budget count)
- Recent 5 expenses
- Recent 5 budgets
- User role display

### Expense Tracking

- Add expenses with amount, category, date, description
- Upload receipt images
- Mark as recurring
- Filter by category & date range
- View total spending

### Budget Management

- Create budgets with date ranges
- Allocate budget to categories
- Link expenses to budgets
- Track allocation vs. actual spending

### Category System

- Create personal categories
- Use global default categories
- Color-coded categories
- Mark as income/expense

### Admin Features

- Delete user's items (moderator/admin only)
- View all users' data
- User management
- System administration

---

## 🐛 Troubleshooting

### Database Issues

```bash
# Test connection
python manage.py dbshell

# Reset migrations
python manage.py migrate accounts zero
python manage.py migrate
```

### Static Files Issues

```bash
python manage.py collectstatic --clear --noinput
```

### Port Already in Use

```bash
python manage.py runserver 8001
```

### More Help

See **QUICK_START.md** for detailed troubleshooting

---

## 📚 Documentation (consolidated)

The repository previously contained several separate documentation files. They have been reviewed and consolidated into this single README for easier discovery and maintenance. The removed files included:

- QUICK_START.md
- PROJECT_ARCHITECTURE.md
- VISUAL_DIAGRAMS.md
- INTEGRATION_CHECKLIST.md
- COMPLETE_SYSTEM_MAP.md
- README_DOCUMENTATION.md
- DOCS_INDEX.md

What was merged here:

- Quick start steps and health checks
- Architecture and model summaries
- Visual/diagram descriptions (ASCII summaries)
- Integration & testing checklist (condensed)
- System map and deployment checklist

If you need a specific subsection restored as a separate file, tell me which part and I can extract it back into its own markdown.

---

## 🎓 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Pico CSS Documentation](https://picocss.com/)

---

## 🚀 Deployment

### Before Production

- [ ] Change DEBUG = False in settings.py
- [ ] Set ALLOWED_HOSTS correctly
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS/SSL
- [ ] Setup database backups
- [ ] Configure email backend
- [ ] Run security checks: `python manage.py check --deploy`

### Production Commands

```bash
python manage.py check --deploy
python manage.py collectstatic
python manage.py migrate
```

---

## 📝 Version Info

- **Framework**: Django 5.0.2
- **Python**: 3.8+
- **Database**: PostgreSQL 12+
- **Created**: March 2026
- **Status**: 🟢 Production Ready

---

## 👤 Author

Created as a capstone project demonstration of:

- Django web development
- Database design & optimization
- User authentication & authorization
- Full-stack web application development

---

## 📞 Support & Questions

1. Check documentation files
2. Review INTEGRATION_CHECKLIST.md
3. Run health_check.py for diagnostics
4. Check Django logs in console
5. Use Django admin for data verification

---

## ✨ Features Roadmap

### Current (v1.0)

- ✅ User authentication & roles
- ✅ Expense tracking
- ✅ Budget planning
- ✅ Category management
- ✅ Dashboard
- ✅ Admin panel

### Future Enhancements

- 🔄 REST API endpoints
- 🔄 Advanced analytics & charts
- 🔄 Budget alerts & notifications
- 🔄 CSV/PDF export
- 🔄 Mobile app
- 🔄 Search & advanced filtering
- 🔄 Recurring expense automation

---

**Made with ❤️ for financial management**

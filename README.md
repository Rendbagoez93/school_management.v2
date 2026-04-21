# School Management System

> **Single-instance packaged application for educational institutions**
> 
> One installation per school | Django 6.0 Backend | RESTful API | Modern Python Architecture

[![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0+-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15+-red.svg)](https://www.django-rest-framework.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.11+-purple.svg)](https://docs.pydantic.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-blue.svg)](https://www.postgresql.org/)
[![pytest](https://img.shields.io/badge/pytest-8.4+-yellow.svg)](https://pytest.org/)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Development](#-development)
- [Contributing](#-contributing)
- [Documentation](#-documentation)

---

## 🎯 Overview

### What is School Management System?

School Management System is a **single-instance packaged application** designed for educational institutions to manage their complete academic operations. Each school runs its own dedicated installation - this is **not a SaaS platform**.

### Core Purpose

Provide educational institutions with a comprehensive, easy-to-deploy system for:

- **Academic Management**: Academic years, grades/classes, subjects, enrollments
- **User Management**: Students, teachers, staff, parents with role-based access
- **Attendance Tracking**: Daily attendance for students, teachers, and staff
- **Report Cards**: Term-based academic performance reports with grades
- **Staff Operations**: Teacher assignments, staff management, scheduling
- **Parent Portal**: Mobile/web access for parents to monitor their children's progress

### Key Characteristics

✅ **Single-Instance** — One installation per school (not multi-tenant SaaS)  
✅ **Modern Python** — Python 3.14+ with latest type hints (PEP 695)  
✅ **Django 6.0** — ASGI support for async views and better performance  
✅ **Type-Safe** — Full type hints with Pydantic validation  
✅ **RESTful API** — Standardized JSON API for mobile/web clients  
✅ **Role-Based Access** — Granular permissions via Django Groups + role field  
✅ **Testing First** — pytest + factory_boy + 80%+ coverage target  

---

## ✨ Features

### For School Administrators

- **Academic Year Setup**: Guided workflow to configure academic year, import students/staff, create grades
- **User Management**: Create and manage users (teachers, staff, students, parents) with role-based permissions
- **School Configuration**: Customize school name, logo, contact information, and branding
- **Staff Management**: Assign roles, departments, and permissions to staff members
- **Grade Management**: Create and organize classes/grades with assigned teachers

### For Teachers

- **Attendance Marking**: Record daily student attendance (present, absent, late, excused)
- **Grade Entry**: Enter and update student grades for subjects
- **Class Management**: View assigned classes and students
- **Schedule Viewing**: Access class timetables and schedules

### For Parents (via Mobile/Web Portal)

- **Student Monitoring**: View attendance, grades, and progress for multiple children
- **Report Cards**: Download term/semester report cards (PDF)
- **Announcements**: Receive school-wide and class-specific announcements
- **Schedule Access**: View class timetables and school calendar

### For Students

- **Personal Dashboard**: View own attendance, grades, and schedules
- **Report Cards**: Access academic performance reports
- **Announcements**: Stay updated with school news and events

---

## 🛠 Tech Stack

### Backend (Python/Django)

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.14+ | Modern async support, PEP 695 type params |
| **Framework** | Django | 6.0+ | ASGI, async views, ORM |
| **API Framework** | Django REST Framework | 3.15+ | RESTful API endpoints |
| **Validation** | Pydantic | 2.11+ | Request/response validation |
| **Database** | PostgreSQL | Latest | Primary data store |
| **DB Driver** | psycopg3 | 3.2+ | PostgreSQL adapter with async support |
| **Settings** | pydantic-settings | 2.9+ | Environment-based configuration |
| **Logging** | structlog | 25.0+ | Structured JSON logging |
| **Testing** | pytest + pytest-django | 8.4+ | Unit and integration testing |
| **Fixtures** | factory_boy | 3.3+ | Test data generation |
| **Code Quality** | ruff | Latest | Linting and formatting |

### Optional Dependencies

- **API Extras**: JWT auth, API documentation (drf-spectacular), CORS, filters
- **Content**: Rich text editor (CKEditor), image handling (Pillow)
- **Documents**: PDF generation (ReportLab, xhtml2pdf)
- **Data**: Excel import/export (pandas, openpyxl)
- **Realtime**: WebSocket support (Daphne)

---

## 📁 Project Structure

```
school_management.v2/
├── config/                      # Django settings and configuration
│   ├── settings/
│   │   ├── base.py             # Base settings (apps, middleware, DRF config)
│   │   ├── envcommon.py        # Environment variables via Pydantic
│   │   ├── databases.py        # Database configuration
│   │   ├── local.py            # Development settings
│   │   └── schoolconf.py       # School-specific configuration
│   ├── urls.py                 # Main URL routing
│   ├── api_urls.py             # API endpoint aggregator
│   ├── roles.py                # RoleEnum definitions
│   ├── asgi.py                 # ASGI application
│   └── wsgi.py                 # WSGI application
│
├── modules/                     # Reusable infrastructure modules
│   ├── user/                   # Core user model and authentication
│   │   ├── models.py           # AbstractUser, User model
│   │   ├── managers.py         # Custom user managers
│   │   ├── mixins.py           # Timestamp, Security, Preferences mixins
│   │   ├── forms/              # Authentication forms
│   │   └── tests/              # User module tests
│   └── auth/                   # Authentication rules and settings
│       └── auth_rules.py       # Permission rules
│
├── applications/                # Business domain applications
│   ├── academic_setup/         # Academic year setup workflow
│   │   ├── models.py           # AcademicYearSetup, ImportTask
│   │   ├── orchestrator.py     # Setup workflow orchestrator
│   │   └── tests/              # Setup workflow tests
│   ├── user_management/        # User profiles and management
│   │   ├── models.py           # SchoolUser, Parent, Student, SchoolStaff
│   │   ├── services.py         # User business logic
│   │   ├── validators.py       # Pydantic validation schemas
│   │   └── tests/              # User management tests
│   └── school_management/      # School operations
│       ├── academic_management/    # Academic years and enrollment
│       │   ├── models.py           # AcademicYear, StudentEnrollment
│       │   └── tests/              # Academic management tests
│       ├── grade_management/       # Grades/classes management
│       │   ├── models.py           # Grade model
│       │   ├── factories.py        # Test data factories
│       │   └── tests/              # Grade management tests
│       └── staff_management/       # Staff operations (in progress)
│
├── shared/                      # Shared utilities and helpers
│   ├── base_models.py          # TimeStampedModel, SoftDeletableModel
│   ├── monad.py                # Functional programming utilities
│   └── api/                    # API infrastructure
│       ├── exceptions.py       # ApiError exception
│       ├── response.py         # Standardized response wrappers
│       ├── parsers.py          # Pydantic request parsing
│       └── middleware.py       # ApiErrorMiddleware
│
├── templates/                   # Django templates (web interface)
├── assets/                     # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── img/
├── tests/                      # Project-level tests
├── scripts/                    # Utility scripts
│
├── manage.py                   # Django management script
├── pyproject.toml             # Python dependencies (uv/pip)
├── school_config.yaml         # School configuration file
└── README.md                  # This file
```

### Application Architecture

The project follows a **modular monolith** pattern:

- **`modules/`** — Infrastructure-level, reusable across projects (user auth, core models)
- **`applications/`** — Business logic specific to school management domain
- **`shared/`** — Common utilities and base classes
- **`config/`** — Django configuration with environment-based settings

---

## 🚀 Installation

### Prerequisites

- **Python 3.14+** (required for modern type hints and async features)
- **PostgreSQL** (recommended for production)
- **uv** (recommended) or **pip** for dependency management

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/school_management.v2.git
cd school_management.v2
```

### Step 2: Create Virtual Environment

Using `uv` (recommended):

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Or using standard Python:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies

Using `uv`:

```bash
uv pip install -e .
```

Or using pip:

```bash
pip install -e .
```

For development (includes testing and linting tools):

```bash
uv pip install -e ".[dev,test]"
```

### Step 4: Database Setup

Create PostgreSQL database:

```bash
createdb school_management
```

Or use SQLite for development (default).

### Step 5: Run Migrations

```bash
python manage.py migrate
```

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 7: Load Initial Data (Optional)

```bash
python manage.py loaddata fixtures/initial_data.json
```

### Step 8: Run Development Server

```bash
python manage.py runserver
```

Access at: `http://127.0.0.1:8000/`

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root (copy from `.env.example` if provided):

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=school_management
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Internationalization
LANGUAGE_CODE=en-us
TIME_ZONE=UTC

# CORS (for mobile apps)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### School Configuration

Edit `school_config.yaml` to customize your school:

```yaml
name: "Your School Name"
address: "123 School Street, City, Country"
phone: "+1234567890"
email: "info@yourschool.com"
description: "Excellence in Education"
attributes:
  established: 2024
  motto: "Learn, Grow, Succeed"
  colors:
    primary: "#1976D2"
    secondary: "#FFC107"
```

---

## 📖 Usage

### Running the Application

```bash
# Development server
python manage.py runserver

# Production (with Gunicorn)
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# ASGI server (Daphne for async/WebSocket)
daphne config.asgi:application
```

### Admin Interface

Access Django admin at: `http://127.0.0.1:8000/admin/`

Log in with superuser credentials created during setup.

### Management Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Create Django groups for roles
python manage.py create_groups

# Shell
python manage.py shell
```

---

## 🔌 API Documentation

### API Response Format

All API responses follow a standardized format:

#### Success Response

```json
{
  "code": "ok",
  "msg": "success",
  "data": {
    "id": 1,
    "name": "John Doe",
    ...
  }
}
```

#### List Response

```json
{
  "code": "ok",
  "msg": "success",
  "data": {
    "results": [
      {...},
      {...}
    ]
  }
}
```

#### Paginated Response

```json
{
  "code": "ok",
  "msg": "success",
  "data": {
    "results": [...],
    "pagination": {
      "totalItems": 100,
      "totalPages": 5,
      "currentPage": 1,
      "perPage": 20
    }
  }
}
```

#### Error Response

```json
{
  "code": "error_code",
  "msg": "Human-readable error message",
  "data": null
}
```

### Authentication

The API uses JWT (JSON Web Token) authentication:

```bash
# Login (get tokens)
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "password123"
}

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Use access token in requests
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### API Utilities

The project provides utilities in `shared/api/` for consistent API development:

- **`ApiError`** — Raise HTTP errors that are automatically converted to JSON
- **`parse_query(request, Schema)`** — Parse and validate query parameters
- **`parse_body(request, Schema)`** — Parse and validate JSON request body
- **`api_response(data)`** — Return standardized single object response
- **`api_list_response(results)`** — Return list response
- **`api_paginated_response(...)`** — Return paginated response

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=applications --cov=modules --cov=shared

# Run specific test file
pytest applications/user_management/tests/test_models.py

# Run with verbose output
pytest -v

# Run in parallel (faster)
pytest -n auto
```

### Test Structure

- Use `pytest` with `@pytest.mark.django_db` for database tests
- Use `factory_boy` for test data generation (no manual fixtures)
- Test files: `test_models.py`, `test_services.py`, `test_views.py`, `test_api.py`
- Factories in: `tests/factories.py` or `factories.py` per app

### Example Test

```python
import pytest
from applications.user_management.models import SchoolUser
from config.roles import RoleEnum

@pytest.mark.django_db
def test_create_teacher():
    teacher = SchoolUser.objects.create_teacher(
        email="teacher@school.com",
        password="securepass",
        first_name="John",
        last_name="Doe"
    )
    assert teacher.role == RoleEnum.TEACHER.value
    assert teacher.groups.filter(name=RoleEnum.TEACHER.value).exists()
```

---

## 💻 Development

### Code Style

- **Formatting**: Ruff (line length: 120)
- **Type Hints**: Required on all functions and class attributes
- **Imports**: Sorted, grouped (stdlib, third-party, local)
- **Comments**: Only when necessary (code should be self-documenting)

### Running Code Quality Tools

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### Best Practices

1. **Type Everything** — Use type hints everywhere (Python 3.14+ syntax)
2. **Validate with Pydantic** — Use Pydantic models for request/response validation
3. **Avoid N+1 Queries** — Always use `select_related()` and `prefetch_related()`
4. **Test First** — Write tests before or alongside implementation
5. **Use Services** — Keep business logic in `services.py`, not views or models
6. **Structured Logging** — Use `structlog` with key-value pairs
7. **Raise, Don't Return Errors** — Use `ApiError` for API errors

### Django Patterns

```python
# ✅ Good: Service layer pattern
# services.py
async def create_student(data: StudentCreateSchema) -> Student:
    student = await Student.objects.acreate(**data.model_dump())
    logger.info("student_created", student_id=student.id)
    return student

# views.py
async def create_student_view(request):
    data = parse_body(request, StudentCreateSchema)
    student = await create_student(data)
    return api_response(student, code="created", status=201)

# ❌ Bad: Business logic in views
async def create_student_view(request):
    data = json.loads(request.body)
    student = await Student.objects.acreate(**data)
    return JsonResponse({"student": student})
```

---

## 🤝 Contributing

### Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && ruff check .`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Commit Messages

Use conventional commits format:

```
feat: add student enrollment API endpoint
fix: resolve N+1 query in grade list view
docs: update API documentation
test: add tests for parent model
refactor: extract service layer from views
```

---

## 📚 Documentation

### Additional Documentation

| Document | Purpose | Location |
|----------|---------|----------|
| **Copilot Instructions** | Backend development guidelines | [.github/copilot-instructions.md](.github/copilot-instructions.md) |
| **Implementation Guide** | Implementation roadmap and status | [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) |
| **Changes Summary** | Recent changes and updates | [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md) |
| **Analysis** | Architecture analysis and decisions | [ANALYSIS.md](ANALYSIS.md) |

### API Documentation (Interactive)

When `drf-spectacular` is installed:

- **Swagger UI**: `http://127.0.0.1:8000/api/docs/`
- **ReDoc**: `http://127.0.0.1:8000/api/redoc/`
- **OpenAPI Schema**: `http://127.0.0.1:8000/api/schema/`

---

## 🏫 User Roles

The system supports the following user roles (defined in `config/roles.py`):

| Role | Description | Access Level |
|------|-------------|--------------|
| **Admin** | System administrator | Full access to all features |
| **Principal** | School principal | Administrative access |
| **Vice Principal** | Assistant principal | Administrative access (limited) |
| **Teacher** | Teaching staff | Class management, grading, attendance |
| **Staff** | Non-teaching staff | Limited administrative access |
| **Librarian** | Library management | Library module access |
| **Accountant** | Financial management | Finance module access |
| **Counselor** | Student counseling | Student records (read-only) |
| **Nurse** | Health management | Health records access |
| **Receptionist** | Front desk | Visitor management, basic access |
| **Student** | Enrolled student | Personal dashboard, view own data |
| **Parent** | Guardian | View children's data via portal |

Roles are implemented using both:
- **`role` field** — For API filtering and display
- **Django Groups** — For granular permissions

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Authors

- **Your Name** - Initial work

---

## 🙏 Acknowledgments

- Django community for the amazing framework
- Pydantic for type-safe validation
- All contributors and supporters

---

**Made with ❤️ for educational institutions**

### Backend (Web Admin)

**Color Palette** (Professional Education Theme):
- **Primary**: `#1976D2` (Professional Blue)
- **Accent**: `#FFA726` (Academic Orange/Gold)
- **Success**: `#43A047` (Green — attendance present)
- **Error**: `#DC3545` (Red — attendance absent)
- **Warning**: `#FBC02D` (Yellow — attendance late)

**UI Framework**: Bootstrap 5 + Custom CSS  
**JavaScript**: HTMX + Alpine.js + Vanilla JS (no bundlers)  
**Templates**: Django Templates with partials  

### Mobile (Parent Portal)

**Component Prefix**: `Sms*` (School Management System)
- `SmsButton`, `SmsCard`, `SmsBadge`, `SmsTextField`
- `SmsStudentCard`, `SmsAttendanceCalendar`, `SmsReportCardItem`

**Color Palette**: Same as web (Professional Blue + Academic Orange)

---

## 🔐 Authentication & Roles

### User Roles

| Role | Login Method | Access |
|------|-------------|--------|
| **Admin** | Email + Password (or Google OAuth) | Full system access (web dashboard) |
| **Teacher** | Google OAuth or Email + Password | Mark attendance, enter grades, view assigned classes |
| **Staff** | Email + Password | Mark own attendance, limited dashboard access |
| **Parent** | Email + Password | Mobile app only: view children's data |

### API Authentication

- **Backend**: JWT tokens (Bearer authentication)
- **Mobile**: Email + Password → JWT token → stored securely (EncryptedSharedPreferences)

---

## 📡 API Overview

### Base URL
```
http://<school-server>/api/
```

### Key Endpoints

**Authentication:**
- `POST /api/auth/parent-login/` — Parent login
- `GET /api/auth/me/` — Get current user
- `POST /api/auth/change-password/` — Change password

**Parent & Students:**
- `GET /api/parent/children/` — Get parent's children list
- `GET /api/students/{student_id}/` — Get student details

**Attendance:**
- `GET /api/attendance/student/{student_id}/?month=YYYY-MM` — Monthly attendance

**Reports:**
- `GET /api/reports/student/{student_id}/` — Report cards list
- `GET /api/reports/{report_id}/` — Report card detail
- `GET /api/reports/{report_id}/download/` — Download PDF

**Schedule:**
- `GET /api/schedule/student/{student_id}/` — Weekly timetable

**Announcements:**
- `GET /api/announcements/` — School announcements (paginated)
- `GET /api/announcements/{announcement_id}/` — Announcement detail

**School Config:**
- `GET /api/school/info/` — School branding and info

### Response Format

All API responses follow a standard wrapper:

```json
{
  "code": "ok",
  "msg": "success",
  "data": { ... }
}
```

**Error responses:**
```json
{
  "code": "error_code",
  "msg": "Human-readable error message",
  "data": null
}
```

---

## 🚀 Development Roadmap

### Backend

- [x] Phase 0: Project setup & architecture
- [ ] Phase 1: Core models (School, AcademicYear, Grade, Subject, Student, Teacher, Staff, Parent)
- [ ] Phase 2: Attendance module
- [ ] Phase 3: Report card & grading system
- [ ] Phase 4: Schedule/timetable management
- [ ] Phase 5: Announcements & notifications
- [ ] Phase 6: Web admin dashboard

### Mobile (Parent Portal)

- [ ] Phase 0: Project setup & design system
- [ ] Phase 1: Authentication (email + password)
- [ ] Phase 2: Dashboard & children list
- [ ] Phase 3: Core features (attendance, reports, schedule, announcements)
- [ ] Phase 4: Advanced features (offline caching, PDF download, push notifications)

---

## 🧪 Testing Strategy

### Backend
- **Framework**: pytest + pytest-django
- **Factories**: factory_boy for test data
- **Coverage**: Models, schemas, services, views
- **Test files**: `test_models.py`, `test_schemas.py`, `test_services.py`, `test_views.py`

### Mobile
- **Framework**: JUnit 4 + Mockito + Kotest
- **UI Testing**: Compose Testing
- **Coverage**: ViewModels, UseCases, Repositories, Composables
- **Screenshot Tests**: Visual regression testing

---

## 📦 Deployment

### Backend

**Requirements:**
- Python 3.14+
- PostgreSQL 14+
- uv (dependency manager)

**Installation:**
```bash
# Clone repository
git clone <repo-url>
cd school-management

# Install dependencies
uv sync

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Mobile

**Requirements:**
- Android Studio (Jellyfish or later)
- JDK 17
- Android SDK 24-35

**Build:**
```bash
# Clone repository
git clone <repo-url>
cd school-parent-portal

# Open in Android Studio
# Sync Gradle
# Run on emulator or device
```

---

## 🤝 Contributing

This is a private school management system. For internal development only.

### Code Style

**Backend (Python):**
- Use `ruff` for formatting and linting
- Line length: 150 characters
- Type hints required on all functions
- Use Pydantic for serialization

**Mobile (Kotlin):**
- Use `ktlint` for formatting
- Line length: 120 characters
- Clean Architecture (Data → Domain → Presentation)
- All components use `Sms` prefix

---

## 📄 License

Proprietary — All rights reserved.

---

## 📞 Support

For questions or issues, contact the development team.

---

**Last Updated**: April 21, 2026

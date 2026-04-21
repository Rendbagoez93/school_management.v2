# Copilot Instructions — School Management System

## Project Overview

- **Framework**: Django 6.0 (ASGI)
- **Python**: 3.14+
- **Config**: pydantic-settings from `.env`, structlog via YAML
- **Database**: PostgreSQL via psycopg3
- **API Framework**: Django REST Framework + Pydantic validation
- **Serialization**: DRF serializers with Pydantic for validation
- **Testing**: pytest + pytest-django + factory_boy
- **Apps location**: `applications/` directory for business logic, `modules/` for infrastructure
- **Settings**: `config/settings/` (split by environment)
- **Dependency manager**: uv + `pyproject.toml`

---

## Product Vision

### What Is School Management System?

School Management System is a **single-instance packaged application** for educational institutions. Each school runs its own dedicated installation to manage academic operations, student records, staff management, attendance tracking, grading, and parent communication. This is **not a SaaS platform** — one installation serves one school only.

### Core Domain Concepts

| Concept | Description |
|---|---|
| **School** | The institution entity. Holds school configuration (name, logo, colors, address, contact info). Single instance per installation. |
| **Academic Year** | School year with start/end dates. Multiple years stored for historical records, one marked as current. |
| **Grade/Class** | Student grouping by level (e.g., Grade 1A, Grade 2B). Each class belongs to an academic year and has an assigned class teacher. |
| **Subject** | Curriculum subjects (e.g., Mathematics, English, Science). Defined per grade level. |
| **Student** | Enrolled student with profile, enrollment date, current grade, parent links, and academic records. |
| **Teacher** | Teaching staff with assigned subjects and classes. Can mark attendance and enter grades. |
| **Staff** | Non-teaching staff (admin, janitor, security, etc.) with department and role assignments. |
| **Parent** | Guardian account linked to one or more students. Access limited to their children's data via mobile app. |
| **Schedule/Timetable** | Weekly class schedule showing subject, teacher, day, and time slots for each class. |
| **Attendance** | Daily attendance records for students, teachers, and staff with status (present, absent, late, excused). |
| **Report Card** | Academic performance reports per term/semester with subject-wise grades and remarks. |
| **Announcement** | School-wide or targeted announcements (events, holidays, notices) visible to parents via mobile app. |
| **School Branding** | Configurable colors, logo, and school name — displayed in web dashboard and mobile app. |

### Future Goals / Roadmap

- Online fee payment integration
- Library management module
- Transport/bus tracking system
- Health records management
- Exam scheduling and hall ticket generation
- SMS/Email notifications for parents
- Advanced analytics and dashboard
- Mobile app for teachers (attendance marking, grade entry)

### Language Rules

- **Web pages** (templates, landing, UI copy) — **English** (or configurable per school region)
- **API responses** (`code`, `msg`) — **English**
- **Code** (variables, comments, docstrings) — **English**
- **Template variable names** — **English**

---

## Code Style

### General

- Prefer **static typing** over dynamic. Use type hints on all function signatures, return types, and class attributes. Use `TYPE_CHECKING` imports where needed to avoid circular imports.
- Do not over-comment. Let function and class names explain intent. Add comments only when something requires special attention, is non-obvious, or is a workaround.
- Use ruff for formatting and linting. Line length is 150.

### Python / Django

- Always use `from __future__ import annotations` is not needed (Python 3.14+, PEP 649 is active).
- Use `list[str]` over `List[str]`, `str | None` over `Optional[str]`.
- **Use PEP 695 type parameter syntax** for generic functions/classes. Write `def foo[T: BaseModel](x: T) -> T` instead of using `TypeVar`. Do not import `TypeVar` — it is legacy on Python 3.14+.
- Prefer dataclasses or Pydantic models over plain dicts for structured data.
- All Django models should inherit from `shared.base_models.TimeStampedModel` or `BaseSoftDeletableModel` as appropriate.
- Custom user model is `modules.user.models.User` (`AUTH_USER_MODEL = "user.User"`).
- `User` uses `AbstractBaseUser` + `PermissionsMixin`. Identity fields: `email` (required, unique) + optional `phone_number`.
- User roles are implemented via **both** `role` field (for API filtering) **and** Django Groups (for permissions).
- Authentication is **role-based**: Teachers/Staff via Google OAuth or email+password, Parents via email+password. Superusers have passwords for Django admin.

---

## Database & QuerySet Patterns

### Avoid N+1 queries

- Always use `select_related()` for ForeignKey / OneToOne lookups and `prefetch_related()` for reverse / M2M relations.
- Select only the fields you need with `.only()` or `.values()` / `.values_list()`. Do not fetch entire rows when a subset suffices.

### Use QuerySet Managers

- If a query pattern is repeated more than once, extract it into a custom `QuerySet` method or a model `Manager`.
- Keep business logic in `services.py`, not in views or models. Models define data and managers; services orchestrate.

```python
# Preferred
class ActiveStudentManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_active=True)

class Student(TimeStampedModel):
    objects = models.Manager()
    active = ActiveStudentManager()
```

### Migrations

- One logical change per migration. Do not combine schema changes with data migrations.
- Always review auto-generated migrations before committing.

---

## User Model

`User` (modules.user.models.User) inherits from `AbstractBaseUser`, `PermissionsMixin`, `TimeStampedModel`, `SecurityMixin`, and `PreferencesMixin`.

| Field | Type | Notes |
|---|---|---|
| `id` | `UUIDField` | Primary key, auto-generated UUID |
| `email` | `EmailField` | Required, unique. Primary identifier. |
| `phone_number` | `CharField` | Optional |
| `first_name` / `last_name` | `CharField` | Optional |
| `date_of_birth` | `DateField` | Optional |
| `role` | `CharField(choices)` | ADMIN, PRINCIPAL, VP, TEACHER, STAFF, PARENT, STUDENT, etc. (indexed for API filtering) |
| `is_staff` / `is_active` | `BooleanField` | Django admin access, active status |
| `is_verified` | `BooleanField` | Email verification status |
| `date_joined` | `DateTimeField` | Account creation (indexed) |
| `date_modified` | `DateTimeField` | Last update |
| `is_deleted` / `deleted_at` | Soft delete fields | From BaseSoftDeletableModel |

**Role Choices:**
```python
# Defined in config/roles.py
from enum import StrEnum

class RoleEnum(StrEnum):
    ADMIN = "Admin"
    PRINCIPAL = "Principal"
    VP = "Vice Principal"
    TEACHER = "Teacher"
    STAFF = "Staff"
    LIBRARIAN = "Librarian"
    ACT = "Accountant"
    CSLR = "Counselor"
    NURSE = "Nurse"
    RCP = "Receptionist"
    STUDENT = "Student"
    PARENT = "Parent"
```

- `USERNAME_FIELD = "email"`
- `REQUIRED_FIELDS = []`
- Password is required for all users except those using Google OAuth.
- **Hybrid Role System:** `role` field for API filtering + Django Groups for granular permissions

```python
# Creating users with SchoolUserManager
from applications.user_management.models import SchoolUser
from config.roles import RoleEnum

teacher = SchoolUser.objects.create_teacher(
    email="teacher@school.com",
    password="securepass",
    first_name="John",
    last_name="Doe"
)
# Automatically sets role=RoleEnum.TEACHER.value and assigns to Teacher Group
```

---

## DRF + Pydantic Integration

- Use **Django REST Framework** for API endpoints (ViewSets, Routers)
- Use **Pydantic** for request/response validation within DRF
- Shared API utilities in `shared/api/`:
  - `exceptions.py` - `ApiError` exception
  - `response.py` - Response wrapper functions
  - `parsers.py` - Request parsing with Pydantic
  - `middleware.py` - API error middleware

### Request Parsing (Pydantic)

Use `shared.api.parsers` to parse and validate query parameters or JSON request bodies with Pydantic models. **Never** manually call `request.GET.get()` or `json.loads(request.body)` in views — always go through parsers.

- `parse_query(request, Schema)` — validates `request.GET` into a Pydantic model.
- `parse_body(request, Schema)` — validates JSON `request.body` into a Pydantic model.

Both **raise `ApiError`** on failure — the middleware converts it to a structured JSON response.

```python
from shared.api import parse_query, parse_body, ApiError

async def my_view(request):
    params = parse_query(request, MyQuerySchema)
    # params is a validated MyQuerySchema instance

    data = parse_body(request, MyBodySchema)
    # data is a validated MyBodySchema instance
```

### Error Handling (`ApiError`)

Use `shared.api.ApiError` to signal HTTP errors from views or services. The `ApiErrorMiddleware` catches it and returns a structured JSON response automatically.

- **Raise, don't return** — never construct `JsonResponse` error manually in view code; raise `ApiError` instead.
- The middleware is registered in `MIDDLEWARE` as `"shared.api.middleware.ApiErrorMiddleware"`.

```python
from shared.api import ApiError

# In a view or service:
raise ApiError("not_found", "Student not found.", status=404)
raise ApiError("validation_error", "Invalid input.", status=422)
```

### API Views

All API views return the standardized response wrapper using helpers from `shared.api.response`.

```python
from shared.api import api_response, api_list_response, api_paginated_response, ApiError

# Single object (DRF APIView)
class StudentDetailView(APIView):
    async def get(self, request, student_id: int):
        student = await get_student_by_id(student_id)
        if not student:
            raise ApiError("not_found", "Student not found", status=404)
        return api_response(student)

# Or with function-based view
async def student_detail(request, student_id: int):
    student = await get_student_by_id(student_id)
    if not student:
        raise ApiError("not_found", "Student not found", status=404)
    return api_response(student)
```

### Web Views (CBV or FBV, async)

```python
from django.shortcuts import render

async def student_list(request):
    students = [s async for s in Student.objects.filter(is_active=True)]
    return render(request, "students/list.html", {"students": students})
```

### URL Naming

- Use `app_name` in every `urls.py` and `api_urls.py` for namespacing.
- Web URL names: `<app>:<action>` — e.g., `students:list`, `students:detail`.
- API URL names: `<app>-api:<action>` — e.g., `students-api:detail`, `students-api:create`.

```python
# applications/school_management/student_management/urls.py
app_name = "students"
urlpatterns = [
    path("", student_list, name="list"),
]

# applications/school_management/student_management/api_urls.py
app_name = "students-api"
urlpatterns = [
    path("<int:student_id>/", student_detail, name="detail"),
]
```

---

## Project Structure Reference

```
school-management/
├── config/
│   ├── asgi.py, wsgi.py, urls.py
│   ├── api_urls.py              # Aggregates all app API routes under /api/
│   ├── roles.py                 # RoleEnum definitions
│   └── settings/
│       ├── base.py, envcommon.py, databases.py
│       ├── local.py, schoolconf.py
├── modules/                     # Reusable infrastructure
│   ├── user/                    # Core user model + managers
│   │   ├── models.py            # AbstractUser, User
│   │   ├── managers.py          # DefaultUserManager
│   │   ├── mixins.py            # TimestampMixin, SecurityMixin, PreferencesMixin
│   │   └── migrations/
│   └── auth/                    # Authentication rules
├── applications/                # Business domain apps
│   ├── academic_setup/          # Academic year setup workflow
│   │   ├── models.py            # AcademicYearSetup, ImportTask
│   │   ├── orchestrator.py      # AcademicYearOrchestrator
│   │   └── tests/
│   ├── user_management/         # User profiles and management
│   │   ├── models.py            # SchoolUser, Parent, Student, SchoolStaff
│   │   ├── services.py
│   │   └── tests/
│   └── school_management/
│       ├── academic_management/ # Academic years
│       │   ├── models.py        # AcademicYear, StudentEnrollment
│       │   └── tests/
│       ├── grade_management/    # Grades/Classes
│       │   ├── models.py        # Grade
│       │   ├── factories.py     # GradeFactory
│       │   └── tests/
│       └── staff_management/    # Staff (to be implemented)
├── shared/                      # Shared utilities
│   ├── base_models.py           # TimeStampedModel, SoftDeletableModel
│   ├── monad.py                 # Functional utilities
│   └── api/                     # API infrastructure
│       ├── exceptions.py        # ApiError
│       ├── response.py          # Response wrappers
│       ├── parsers.py           # Request parsing
│       └── middleware.py        # ApiErrorMiddleware
├── templates/                   # Django templates for web interface
├── assets/                      # Static files (css, js, img)
├── tests/                       # Project-level tests
└── pyproject.toml               # Dependencies via uv
```

**Note:** Future apps to be added under `applications/school_management/`:
- `student_management/` - Student profiles and operations
- `parent_management/` - Parent profiles and student links
- `attendance/` - Attendance tracking
- `reports/` - Report cards and grades
- `schedule/` - Class timetables
- `announcements/` - School announcements

Also needed:
- `applications/school_config/` - School singleton configuration
- `applications/auth_api/` - Authentication API endpoints
│   ├── attendance/      # Attendance tracking
│   ├── reports/         # Report cards & grades
│   ├── schedule/        # Timetable management
│   └── announcements/   # School announcements
│       ├── models.py
│       ├── schemas.py
│       ├── services.py
│       ├── admin.py
│       ├── views.py     # Web views (admin/staff interface)
│       ├── api_views.py # API views (parent mobile app)
│       ├── urls.py      # Web URL routes
│       ├── api_urls.py  # API URL routes
│       ├── migrations/
│       └── tests/
│           ├── factories.py
│           ├── test_models.py
│           ├── test_schemas.py
│           ├── test_services.py
│           └── test_views.py
├── templates/
│   ├── base.html
│   └── core/<app_name>/*.html
├── static/
│   ├── css/root.css         # Design tokens (single source of truth)
│   ├── css/components/      # Component-level CSS
│   ├── css/pages/           # Page-scoped CSS
│   ├── js/                  # Global JS
│   └── js/pages/            # Page-scoped JS
├── conftest.py
├── manage.py
└── pyproject.toml
```

---

## API Response Wrapper

All API responses are wrapped in a standard format for consistency:

### Single Object Response
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

### List Response
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

### Paginated Response
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

### Error Response
```json
{
  "code": "error_code",
  "msg": "Human-readable error message",
  "data": null
}
```

---

## Testing

- Use `pytest` with `@pytest.mark.django_db` for database tests.
- Use `factory_boy` factories (in `tests/factories.py` per app) for all test data. Never use fixtures files or `setUp` with manual `create()`.
- Test file naming: `test_models.py`, `test_schemas.py`, `test_services.py`, `test_views.py`, `test_api.py`.
- Test class naming: `TestModelName` or `TestServiceFunction`.
- Each test should be independent and not rely on ordering.
- See `applications/school_management/academic_management/tests/` and `applications/school_management/grade_management/tests/` for excellent examples.

---

## Logging

- Use `structlog.get_logger(__name__)` for all logging. Do not use `logging.getLogger()`.
- Log key events in services: creation, updates, failures. Use structured key-value pairs, not f-strings.

```python
import structlog

logger = structlog.get_logger(__name__)
logger.info("student_enrolled", student_id=student.id, grade=student.grade)
logger.warning("attendance_conflict", student_id=student.id, date=date, reason=reason)
```

---

## Debugging

### Admin Login for Development

For local development and testing, you can create a superuser:

```bash
python manage.py createsuperuser
```

Then login at `http://127.0.0.1:8000/admin/`

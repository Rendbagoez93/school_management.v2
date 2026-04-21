# Implementation Guide & Next Steps

This document outlines what has been implemented and what needs to be done next.

---

## ✅ Completed (Phase 1: API Infrastructure Setup)

### 1. Dependencies Updated
- ✅ Added `psycopg[binary]>=3.2.0` for PostgreSQL
- ✅ Added `djangorestframework>=3.15.0` for API framework
- ✅ Added `structlog>=25.0.0` and `python-json-logger>=3.2.0` for structured logging
- ✅ Removed `dependency-injector` (not needed with Django's built-in DI)
- ✅ API group dependencies already present (JWT, spectacular, filters, CORS)

### 2. Shared API Infrastructure Created
Created `shared/api/` package with:
- ✅ `exceptions.py` - `ApiError` exception class
- ✅ `response.py` - Response wrapper functions:
  - `api_response()` - Single object response
  - `api_list_response()` - List response
  - `api_paginated_response()` - Paginated list response
  - `api_error()` - Error response
- ✅ `parsers.py` - Request parsing utilities:
  - `parse_query()` - Parse & validate query parameters with Pydantic
  - `parse_body()` - Parse & validate JSON body with Pydantic
- ✅ `middleware.py` - `ApiErrorMiddleware` to catch ApiError and return JSON

### 3. Settings Configuration
- ✅ Added DRF to `INSTALLED_APPS`:
  - `rest_framework`
  - `rest_framework_simplejwt`
  - `drf_spectacular`
  - `django_filters`
  - `corsheaders`
- ✅ Added middleware:
  - `corsheaders.middleware.CorsMiddleware` (before CommonMiddleware)
  - `shared.api.middleware.ApiErrorMiddleware` (at end)
- ✅ Configured `REST_FRAMEWORK` settings:
  - JWT authentication
  - JSON renderer
  - Pagination (20 items per page)
  - Filters (DjangoFilterBackend, SearchFilter, OrderingFilter)
  - DRF Spectacular schema
- ✅ Configured `SIMPLE_JWT`:
  - Access token: 24 hours
  - Refresh token: 7 days
  - Token rotation enabled
- ✅ Configured `SPECTACULAR_SETTINGS` for API docs
- ✅ Configured `CORS_ALLOWED_ORIGINS` in env settings

### 4. URL Configuration
- ✅ Created `config/api_urls.py` as API route aggregator
- ✅ Updated `config/urls.py` to include `/api/` route

### 5. User Model Enhancement
- ✅ Added `role` CharField to `AbstractUser` using existing `RoleEnum` from `config/roles.py`
- ✅ Role choices generated dynamically from RoleEnum for consistency
- ✅ Added index on `role` field for efficient API filtering
- ✅ Updated all `SchoolUserManager.create_*` methods to automatically set role field
- ✅ Role field synced with Django Groups (hybrid approach):
  - `role` field for simple API filtering
  - Django Groups for granular permissions

---

## 🔨 TODO (Phase 2: Core Missing Apps)

### 1. Create School Configuration App
```
applications/school_config/
├── __init__.py
├── apps.py
├── models.py          # School singleton model
├── admin.py           # Admin interface
└── migrations/
```

**School Model Fields:**
- name, logo, address, phone, email, website
- primary_color, accent_color (branding)
- created_at, updated_at

**Ensure only ONE record can exist** (singleton pattern)

### 2. Extract Student Management from user_management
```
applications/school_management/student_management/
├── __init__.py
├── apps.py
├── models.py          # Student profile
├── services.py        # Student operations
├── admin.py
├── migrations/
├── api/
│   ├── __init__.py
│   ├── views.py       # DRF ViewSets
│   ├── serializers.py # DRF serializers
│   └── urls.py        # API routes
└── tests/
```

**Student Model Fields:**
- user (OneToOne to User)
- roll_number (unique)
- date_of_birth, admission_date
- current_grade (FK to Grade)
- photo, blood_group, address, emergency_contact
- is_active

### 3. Extract Parent Management from user_management
```
applications/school_management/parent_management/
├── __init__.py
├── apps.py
├── models.py          # Parent profile, ParentStudent link
├── services.py
├── admin.py
├── migrations/
├── api/
│   ├── __init__.py
│   ├── views.py       # Parent authentication, children list
│   ├── serializers.py
│   └── urls.py
└── tests/
```

**ParentStudent Model Fields:**
- parent (FK to User)
- student (FK to Student)
- relationship (Father, Mother, Guardian)
- is_primary_contact

### 4. Implement Staff Management
```
applications/school_management/staff_management/
├── models.py          # SchoolStaff, Teacher models
├── services.py
├── admin.py
├── migrations/
└── api/
```

**Teacher Model Fields:**
- user (OneToOne to User)
- employee_id (unique)
- department, specialization
- date_of_joining
- is_active
- subjects (M2M through TeacherSubject)

**SchoolStaff Model Fields:**
- user (OneToOne to User)
- employee_id (unique)
- department, job_title
- date_of_joining
- is_active

---

## 🔨 TODO (Phase 3: API Endpoints for Existing Features)

### 1. Authentication API
File: `applications/auth_api/` (new app)

**Endpoints:**
- `POST /api/auth/parent-login/` - Parent login
- `GET /api/auth/me/` - Get current user
- `POST /api/auth/change-password/` - Change password
- `POST /api/auth/logout/` - Logout (optional, if using token blacklist)

### 2. Academic Year API
File: `applications/school_management/academic_management/api/`

**Endpoints:**
- `GET /api/academic/years/` - List academic years
- `GET /api/academic/years/{id}/` - Academic year detail
- `GET /api/academic/current/` - Get current academic year

### 3. Grade API
File: `applications/school_management/grade_management/api/`

**Endpoints:**
- `GET /api/grades/?academic_year={id}` - List grades for year
- `GET /api/grades/{id}/` - Grade detail

### 4. Parent & Student API
File: `applications/school_management/parent_management/api/`

**Endpoints:**
- `GET /api/parent/children/` - List parent's children
- `GET /api/students/{id}/` - Student detail (with permission check)

---

## 🔨 TODO (Phase 4: New Feature Apps)

### 1. Attendance App
```
applications/school_management/attendance/
├── models.py          # StudentAttendance, TeacherAttendance, StaffAttendance
├── services.py
├── admin.py
├── api/
└── tests/
```

**StudentAttendance Model:**
- student (FK)
- date (indexed)
- status (PRESENT, ABSENT, LATE, EXCUSED)
- marked_by (FK to User)
- remarks

**API Endpoints:**
- `GET /api/attendance/student/{student_id}/?month={YYYY-MM}` - Monthly attendance
- `GET /api/attendance/student/{student_id}/summary/` - Attendance percentage

### 2. Reports App
```
applications/school_management/reports/
├── models.py          # ReportCard, SubjectGrade
├── services.py
├── admin.py
├── api/
└── tests/
```

**ReportCard Model:**
- student (FK)
- academic_year (FK)
- term (Q1, Q2, FINAL)
- overall_grade, rank
- remarks

**SubjectGrade Model:**
- report_card (FK)
- subject (FK)
- grade, marks, max_marks
- teacher_remarks

**API Endpoints:**
- `GET /api/reports/student/{student_id}/` - List report cards
- `GET /api/reports/{id}/` - Report card detail with subject grades

### 3. Schedule App
```
applications/school_management/schedule/
├── models.py          # Schedule/Timetable
├── services.py
├── admin.py
├── api/
└── tests/
```

**Schedule Model:**
- grade (FK)
- subject (FK)
- teacher (FK)
- day_of_week (MON-FRI)
- start_time, end_time
- room_number

**API Endpoints:**
- `GET /api/schedule/grade/{grade_id}/` - Weekly timetable for grade
- `GET /api/schedule/student/{student_id}/` - Student's timetable (via current grade)

### 4. Announcements App
```
applications/school_management/announcements/
├── models.py          # Announcement
├── services.py
├── admin.py
├── api/
└── tests/
```

**Announcement Model:**
- title, content
- date_posted
- target_audience (ALL, PARENTS, STUDENTS, TEACHERS, STAFF)
- priority (NORMAL, IMPORTANT, URGENT)
- is_active

**API Endpoints:**
- `GET /api/announcements/?target=PARENTS` - List announcements for parents
- `GET /api/announcements/{id}/` - Announcement detail

---

## 🔨 TODO (Phase 5: Data Migrations & Sync)

### 1. Create Migration for User.role Field
```bash
python manage.py makemigrations user --name add_role_field
```

### 2. Data Migration to Sync Groups → role
Create a data migration to:
- Read each user's Groups
- Map Group name to Role enum value
- Update user.role field

### 3. Update SchoolUserManager
Modify `applications/user_management/models.py`:
- Add methods to sync role field when assigning Groups
- Update `create_*` methods to set role field

---

## 🔨 TODO (Phase 6: Documentation Updates)

### 1. Update `.github/copilot-instructions.md`
- Change `core/` to `applications/`
- Update project structure diagram
- Document actual user model (`user.User` with role field + Groups)
- Add API infrastructure details (DRF + Pydantic validation)

### 2. Update `.github/database-schema.md`
- Add role field to AuthUser/User table
- Add all missing app models (School, Student, Parent, ParentStudent, Teacher, etc.)

### 3. Update `.github/api-reference.md`
- Update base URL examples
- Add authentication endpoints
- Add all implemented API endpoints as they're built

---

## 📋 Testing Strategy

For each new app/feature:
1. Write factory classes (`tests/factories.py`)
2. Write model tests (`tests/test_models.py`)
3. Write service tests (`tests/test_services.py`)
4. Write API tests (`tests/test_api.py`)

Use existing test patterns from `academic_management` and `grade_management` as reference.

---

## 🚀 How to Continue

### Immediate Next Steps (Recommended Order):

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Create & run migration for role field:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create school_config app:**
   ```bash
   python manage.py startapp school_config applications/school_config
   ```

4. **Create student_management app:**
   ```bash
   python manage.py startapp student_management applications/school_management/student_management
   ```

5. **Create parent_management app:**
   ```bash
   python manage.py startapp parent_management applications/school_management/parent_management
   ```

6. **Create auth_api app for authentication endpoints:**
   ```bash
   python manage.py startapp auth_api applications/auth_api
   ```

7. **Implement models** in each new app

8. **Create API endpoints** using DRF ViewSets + shared API utilities

9. **Test everything** with pytest

10. **Update documentation** to reflect actual implementation

---

## 🎯 Priority Matrix

| Task | Priority | Effort | Impact |
|------|----------|--------|--------|
| Install dependencies | P0 | Low | High |
| Migrate role field | P0 | Low | High |
| School config app | P1 | Low | Medium |
| Student management | P0 | Medium | High |
| Parent management | P0 | Medium | High |
| Auth API endpoints | P0 | Medium | High |
| Staff management | P1 | Medium | Medium |
| Attendance app | P2 | High | High |
| Reports app | P2 | High | High |
| Schedule app | P2 | Medium | Medium |
| Announcements app | P2 | Low | Medium |

**Focus on P0 tasks first** to unlock mobile app development.

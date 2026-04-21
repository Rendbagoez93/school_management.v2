# Mobile Development Plan — School Management System (Parent Portal)

## Project Overview

**School Management System** is a single-instance packaged application for educational institutions. The backend is a Django 6.0 ASGI application providing REST APIs for school management. This document outlines the mobile app strategy for the **Parent Portal** using Android and Kotlin Compose.

### Tech Stack

- **Backend Framework**: Django 6.0 (ASGI)
- **Python**: 3.14+
- **Database**: PostgreSQL
- **API Format**: REST (JSON request/response)
- **Serialization**: Pydantic (not DRF)
- **Auth**: Email + Password for parents, Google OAuth for teachers/staff

---

## Backend Architecture

### Core Domain Model

```
School (single instance)
├── name, logo, colors, address, contact
├── AcademicYear
│   ├── name, start_date, end_date, is_current
│   └── Grade/Class
│       ├── name, level, section
│       ├── assigned_teacher (Teacher)
│       └── Student
│           ├── first_name, last_name, roll_number
│           ├── parent_links (Parent-Student relationship)
│           ├── Attendance records
│           └── Report Cards
├── Subject
│   ├── name, code, grade_level
├── Teacher
│   ├── first_name, last_name, subjects_taught
│   └── Attendance records
├── Staff
│   ├── first_name, last_name, department, role
│   └── Attendance records
├── Parent (AuthUser with role=PARENT)
│   ├── email, password, first_name, last_name
│   └── linked students (one-to-many)
├── Schedule/Timetable
│   ├── class, subject, teacher, day_of_week, start_time, end_time
├── Attendance
│   ├── student, date, status (present/absent/late/excused)
│   ├── teacher attendance
│   └── staff attendance
├── ReportCard
│   ├── student, academic_year, term, subject, grade, remarks
└── Announcement
    ├── title, content, target_audience, date_posted, is_active
```

### Key Database Rules

1. **Single school instance** — No multi-tenancy, one installation per school
2. **Roles**: ADMIN, TEACHER, STAFF, PARENT (all use AuthUser model)
3. **Parents linked to students** — One parent can have multiple children
4. **Academic years** — Historical data preserved, one marked as current
5. **Attendance is daily** — Separate tables for student/teacher/staff attendance
6. **Report cards per term** — Generated per academic year and term (e.g., Q1, Q2, Final)

### Apps Implemented

| App | Purpose | Web Routes | API Routes | Status |
|-----|---------|-----------|-----------|--------|
| `core.users` | Authentication & user management | ✅ | ✅ | Production-ready |
| `core.school` | School configuration | ✅ | ❌ | Web-only (admin) |
| `core.academic` | Academic years, grades, subjects | ✅ | ❌ | Web-only (admin) |
| `core.students` | Student management | ✅ | ✅ | Web + API |
| `core.teachers` | Teacher management | ✅ | ❌ | Web-only (admin) |
| `core.staff` | Staff management | ✅ | ❌ | Web-only (admin) |
| `core.parents` | Parent accounts & student links | ✅ | ✅ | Web + API |
| `core.attendance` | Attendance tracking | ✅ | ✅ | Web + API |
| `core.reports` | Report cards & grades | ✅ | ✅ | Web + API |
| `core.schedule` | Class timetables | ✅ | ✅ | Web + API |
| `core.announcements` | School announcements | ✅ | ✅ | Web + API |

---

## Current API Endpoints

### Base URL
```
{API_BASE}/api/
```

### Authentication Endpoints

All endpoints are `async`, `@csrf_exempt`, and return JSON in the standard response wrapper.

#### 1. Parent Login
```
POST /api/auth/parent-login/
Content-Type: application/json

{
  "email": "parent@example.com",
  "password": "securepassword"
}

Response (200 OK) — Success:
{
  "code": "ok",
  "msg": "success",
  "data": {
    "id": 1,
    "email": "parent@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "role": "PARENT",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}

Error (401):
{
  "code": "auth_failed",
  "msg": "Invalid email or password.",
  "data": null
}
```

#### 2. Get Current User
```
GET /api/auth/me/
Authorization: Bearer {token}

Response (200 OK):
{
  "code": "ok",
  "msg": "success",
  "data": {
    "id": 1,
    "email": "parent@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "role": "PARENT"
  }
}
```

#### 3. Change Password
```
POST /api/auth/change-password/
Authorization: Bearer {token}
Content-Type: application/json

{
  "oldPassword": "current123",
  "newPassword": "newsecure456"
}

Response (200 OK):
{
  "code": "ok",
  "msg": "Password changed successfully.",
  "data": null
}
```

---

### Parent & Student Endpoints

#### 1. Get My Children
```
GET /api/parent/children/
Authorization: Bearer {token}

Response (200 OK):
{
  "code": "ok",
  "msg": "success",
  "data": {
    "results": [
      {
        "id": 10,
        "firstName": "Alice",
        "lastName": "Doe",
        "rollNumber": "2025001",
        "gradeClass": "Grade 5A",
        "photo": "https://school.com/media/students/alice.jpg"
      },
      {
        "id": 11,
        "firstName": "Bob",
        "lastName": "Doe",
        "rollNumber": "2025002",
        "gradeClass": "Grade 3B",
        "photo": null
      }
    ]
  }
}
```

#### 2. Get Student Detail
```
GET /api/students/{student_id}/
Authorization: Bearer {token}

Response (200 OK):
{
  "code": "ok",
  "msg": "success",
  "data": {
    "id": 10,
    "firstName": "Alice",
    "lastName": "Doe",
    "rollNumber": "2025001",
    "gradeClass": "Grade 5A",
    "dateOfBirth": "2015-03-15",
    "admissionDate": "2020-04-01",
    "photo": "https://school.com/media/students/alice.jpg"
  }
}
```

---

### Attendance Endpoints

#### 1. Get Student Attendance (Monthly)
```
GET /api/attendance/student/{student_id}/?month=2026-04
Authorization: Bearer {token}

Response (200 OK):
{
  "code": "ok",
  "msg": "success",
  "data": {
    "studentId": 10,
    "studentName": "Alice Doe",
    "month": "2026-04",
    "summary": {
      "totalDays": 22,
      "present": 20,
      "absent": 1,
      "late": 1,
      "excused": 0,
      "attendancePercentage": 90.9
    },
    "records": [
      {
        "date": "2026-04-01",
        "status": "present",
        "remarks": null
      },
      {
        "date": "2026-04-02",
        "status": "absent",
        "remarks": "Sick leave"
      },
      {
        "date": "2026-04-03",
        "status": "late",
        "remarks": "Traffic delay"
      }
      // ... more records
    ]
  }
}
```

---

### Report Card Endpoints

#### 1. Get Student Report Cards
```
GET /api/reports/student/{student_id}/
Authorization: Bearer {token}

Response (200 OK):
{
  "code": "ok",
  "msg": "success",
  "data": {
    "results": [
      {
        "id": 100,
        "academicYear": "2025-2026",
        "term": "Q1",
        "issuedDate": "2025-11-15",
        "overallGrade": "A",
        "overallPercentage": 92.5,
        "rank": 3,
        "totalStudents": 40
      },
      {
        "id": 101,
        "academicYear": "2025-2026",
        "term": "Q2",
        "issuedDate": "2026-02-15",
        "overallGrade": "A+",
        "overallPercentage": 95.0,
        "rank": 2,
        "totalStudents": 40
      }
    ]
  }
}
```

#### 2. Get Report Card Detail
```
GET /api/reports/{report_id}/
Authorization: Bearer {token}

Response (200 OK):
{
  "code": "ok",
  "msg": "success",
  "data": {
    "id": 100,
    "student": {
      "id": 10,
      "firstName": "Alice",
      "lastName": "Doe",
      "gradeClass": "Grade 5A"
    },
    "academicYear": "2025-2026",
    "term": "Q1",
    "issuedDate": "2025-11-15",
    "subjects": [
      {
        "subjectName": "Mathematics",
        "grade": "A+",
        "score": 98,
        "maxScore": 100,
        "remarks": "Excellent performance"
      },
      {
        "subjectName": "English",
        "grade": "A",
        "score": 90,
        "maxScore": 100,
        "remarks": "Good work"
      },
      {
        "subjectName": "Science",
        "grade": "A",
        "score": 92,
        "maxScore": 100,
        "remarks": "Very good understanding"
      }
      // ... more subjects
    ],
    "overallGrade": "A",
    "overallPercentage": 92.5,
    "rank": 3,
    "totalStudents": 40,
    "classTeacherRemarks": "Alice is a bright student with excellent academic performance.",
    "principalRemarks": "Keep up the good work!"
  }
}
```

#### 3. Download Report Card PDF
```
GET /api/reports/{report_id}/download/
Authorization: Bearer {token}

Response: PDF file download (Content-Type: application/pdf)
```

---

### Schedule/Timetable Endpoints

#### 1. Get Class Schedule
```
GET /api/schedule/student/{student_id}/
Authorization: Bearer {token}

Response (200 OK):
{
  "code": "ok",
  "msg": "success",
  "data": {
    "studentId": 10,
    "gradeClass": "Grade 5A",
    "schedule": {
      "Monday": [
        {
          "period": 1,
          "startTime": "08:00",
          "endTime": "08:45",
          "subject": "Mathematics",
          "teacher": "Mr. Smith"
        },
        {
          "period": 2,
          "startTime": "08:45",
          "endTime": "09:30",
          "subject": "English",
          "teacher": "Ms. Johnson"
        }
        // ... more periods
      ],
      "Tuesday": [
        // ... Tuesday schedule
      ]
      // ... other days
    }
  }
}
```

---

### Announcement Endpoints

#### 1. Get School Announcements
```
GET /api/announcements/?page=1&per_page=10
Authorization: Bearer {token}

Response (200 OK):
{
  "code": "ok",
  "msg": "success",
  "data": {
    "results": [
      {
        "id": 50,
        "title": "Parent-Teacher Meeting on April 25",
        "content": "Dear parents, we will have a parent-teacher meeting on April 25, 2026...",
        "datePosted": "2026-04-15T10:00:00Z",
        "targetAudience": "ALL",
        "priority": "HIGH"
      },
      {
        "id": 51,
        "title": "School Holiday on April 21",
        "content": "The school will be closed on April 21 for Easter holiday.",
        "datePosted": "2026-04-10T09:00:00Z",
        "targetAudience": "ALL",
        "priority": "NORMAL"
      }
    ],
    "pagination": {
      "totalItems": 25,
      "totalPages": 3,
      "currentPage": 1,
      "perPage": 10
    }
  }
}
```

#### 2. Get Announcement Detail
```
GET /api/announcements/{announcement_id}/
Authorization: Bearer {token}

Response (200 OK):
{
  "code": "ok",
  "msg": "success",
  "data": {
    "id": 50,
    "title": "Parent-Teacher Meeting on April 25",
    "content": "Dear parents, we will have a parent-teacher meeting on April 25, 2026. Please ensure your attendance...",
    "datePosted": "2026-04-15T10:00:00Z",
    "targetAudience": "ALL",
    "priority": "HIGH",
    "attachments": [
      {
        "fileName": "meeting-schedule.pdf",
        "fileUrl": "https://school.com/media/announcements/meeting-schedule.pdf"
      }
    ]
  }
}
```

---

### School Configuration Endpoints

#### 1. Get School Info
```
GET /api/school/info/
Authorization: Bearer {token}

Response (200 OK):
{
  "code": "ok",
  "msg": "success",
  "data": {
    "name": "Green Valley High School",
    "logo": "https://school.com/media/school/logo.png",
    "address": "123 Education Street, City, Country",
    "phone": "+1234567890",
    "email": "info@greenvalley.edu",
    "website": "https://greenvalley.edu",
    "branding": {
      "primaryColor": "#1976D2",
      "accentColor": "#FFA726"
    }
  }
}
```

---

## Standard API Response Format

**Single Object:**
```json
{
  "code": "string",
  "msg": "string",
  "data": { ... object ... }
}
```

**List of Objects:**
```json
{
  "code": "ok",
  "msg": "success",
  "data": {
    "results": [ ... ]
  }
}
```

**Paginated List:**
```json
{
  "code": "ok",
  "msg": "success",
  "data": {
    "results": [ ... ],
    "pagination": {
      "totalItems": 100,
      "totalPages": 5,
      "currentPage": 1,
      "perPage": 20
    }
  }
}
```

**Error Response:**
```json
{
  "code": "error_code",
  "msg": "Human-readable error message",
  "data": null
}
```

---

## Mobile App Roadmap

### Phase 1: Authentication (MVP)
- **Goal**: Parents can login with email + password
- **Deliverables**:
  - Login screen with email/password input
  - Secure token storage (EncryptedSharedPreferences)
  - Session management (auto-logout after expiry)
  - Change password functionality

### Phase 2: Dashboard & Children List
- **Goal**: Parents see their children and basic stats
- **Deliverables**:
  - Dashboard screen with children cards
  - Child selection
  - Quick stats (attendance %, latest grade)
  - Navigation to child detail screens

### Phase 3: Core Features
- **Goal**: Parents can view attendance, reports, schedule, announcements
- **Deliverables**:
  - Attendance calendar view (monthly)
  - Report card list and detail
  - PDF download for report cards
  - Weekly schedule/timetable view
  - Announcements list with push notifications

### Phase 4: Advanced Features
- **Goal**: Offline support and additional features
- **Deliverables**:
  - Offline caching (Room database)
  - Fee payment integration (if applicable)
  - In-app messaging (parent-teacher communication)
  - Multiple language support
  - Dark mode theme

---

## Android Development Setup

### IDE & Tools
- **IDE**: Android Studio (Jellyfish or later)
- **Language**: Kotlin 2.0+
- **Build System**: Gradle (Kotlin DSL)
- **Min SDK**: 24 (Android 7.0) / **Target SDK**: 35 (Android 15)
- **Gradle Version**: 8.5+
- **AGP**: 8.2+

### Project Structure
```
school-parent-portal/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── AndroidManifest.xml
│   │   │   ├── java/com/school/parentportal/
│   │   │   │   ├── MainActivity.kt
│   │   │   │   ├── ParentPortalApp.kt
│   │   │   │   ├── di/                 # Hilt modules
│   │   │   │   ├── data/
│   │   │   │   │   ├── api/            # Retrofit interfaces
│   │   │   │   │   ├── local/          # Room database
│   │   │   │   │   ├── model/          # DTOs
│   │   │   │   │   └── repository/     # Repository implementations
│   │   │   │   ├── domain/
│   │   │   │   │   ├── model/          # Domain entities
│   │   │   │   │   ├── repository/     # Repository interfaces
│   │   │   │   │   └── usecase/        # Use cases
│   │   │   │   ├── presentation/
│   │   │   │   │   ├── screens/        # Composable screens
│   │   │   │   │   ├── components/     # Reusable components
│   │   │   │   │   ├── viewmodel/      # ViewModels
│   │   │   │   │   ├── navigation/     # Navigation
│   │   │   │   │   └── theme/          # Compose theme
│   │   │   │   └── util/
│   │   │   └── res/
│   │   ├── test/                       # Unit tests
│   │   └── androidTest/                # Instrumented tests
│   └── build.gradle.kts
└── build.gradle.kts
```

---

## Implementation Strategy: Phase 1 (Authentication)

### Step 1: Project Setup
- [ ] Create new Kotlin Compose project in Android Studio
- [ ] Configure `build.gradle.kts` with dependencies (see copilot-instructions-mobile.md)
- [ ] Set up Hilt and basic app structure
- [ ] Configure API base URL from environment

### Step 2: Data Layer
- [ ] Create Retrofit interface for `/api/auth/` endpoints
- [ ] Create Kotlin data classes for API requests/responses (use Kotlinx Serialization)
- [ ] Create `AuthRepository` interface and implementation
- [ ] Set up encrypted token storage (EncryptedSharedPreferences)
- [ ] Add OkHttp interceptor for auth headers

### Step 3: Domain Layer
- [ ] Create use cases: `LoginUseCase`, `GetCurrentUserUseCase`, `ChangePasswordUseCase`
- [ ] Map API responses to domain models

### Step 4: Presentation Layer
- [ ] Create `AuthViewModel` (Hilt-injected)
- [ ] Design Composable screens:
  - `SplashScreen` (check token, auto-navigate)
  - `LoginScreen` (email + password input)
  - `DashboardScreen` (after successful login)
- [ ] Wire up login flow
- [ ] Handle loading, error, and success states

### Step 5: Navigation
- [ ] Set up Jetpack Compose Navigation (NavHost, NavController)
- [ ] Define auth graph (splash → login → dashboard)
- [ ] Persist auth state (check token on app startup)

### Step 6: Testing
- [ ] Write unit tests for `AuthRepository` (mock Retrofit)
- [ ] Write UI tests for Compose screens

---

## Environment Configuration

### Backend Environment Variables
```bash
# Django settings
SECRET_KEY=
DEBUG=true|false
DJANGO_ENV=development|production

# Database
DATABASE__NAME=school_management
DATABASE__USER=postgres
DATABASE__PASSWORD=
DATABASE__HOST=localhost|10.0.2.2  # 10.0.2.2 for Android emulator
DATABASE__PORT=5432

# JWT Auth
JWT_SECRET_KEY=
JWT_EXPIRY_HOURS=24

# CORS (allow mobile app)
CORS_ALLOWED_ORIGINS=["http://localhost:8000", "http://10.0.2.2:8000"]
```

### Android App Configuration
```kotlin
// BuildConfig or local.properties
API_BASE_URL="http://10.0.2.2:8000/api/"  // Emulator
// or
API_BASE_URL="http://192.168.1.100:8000/api/"  // Physical device
```

---

## Next Steps

1. Review backend API endpoints (ensure all parent portal endpoints are implemented)
2. Set up Android project structure
3. Implement Phase 1 (Authentication)
4. Design and implement Phase 2 (Dashboard & Children)
5. Implement Phase 3 (Core Features: Attendance, Reports, Schedule, Announcements)
6. Add Phase 4 features (Offline, payments, etc.)

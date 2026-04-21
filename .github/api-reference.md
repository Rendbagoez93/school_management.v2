# API Reference — School Management System

## Overview

This document provides detailed API endpoint specifications for the School Management System. All endpoints return JSON responses following the standard wrapper format.

### Base URL

```
Production: https://<school-domain>/api/
Development: http://localhost:8000/api/
Android Emulator: http://10.0.2.2:8000/api/
```

### Authentication

Most endpoints require authentication via JWT token in the `Authorization` header:

```
Authorization: Bearer <jwt-token>
```

### Standard Response Format

**Success Response:**
```json
{
  "code": "ok",
  "msg": "success",
  "data": { ... }
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

**Paginated List Response:**
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

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `ok` | 200 | Request successful |
| `created` | 201 | Resource created successfully |
| `auth_failed` | 401 | Authentication failed (invalid credentials) |
| `unauthorized` | 401 | Missing or invalid authentication token |
| `forbidden` | 403 | User lacks permission to access resource |
| `not_found` | 404 | Resource not found |
| `validation_error` | 422 | Request data validation failed |
| `server_error` | 500 | Internal server error |

---

## Authentication Endpoints

### 1. Parent Login

**Endpoint:** `POST /api/auth/parent-login/`  
**Authentication:** None (public)  
**Description:** Authenticate parent user with email and password.

**Request Body:**
```json
{
  "email": "parent@example.com",
  "password": "securepassword123"
}
```

**Success Response (200 OK):**
```json
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
```

**Error Response (401 Unauthorized):**
```json
{
  "code": "auth_failed",
  "msg": "Invalid email or password.",
  "data": null
}
```

**Error Response (422 Validation Error):**
```json
{
  "code": "validation_error",
  "msg": "Email is required.",
  "data": null
}
```

---

### 2. Get Current User

**Endpoint:** `GET /api/auth/me/`  
**Authentication:** Required (Bearer token)  
**Description:** Get authenticated user's profile information.

**Request Headers:**
```
Authorization: Bearer <jwt-token>
```

**Success Response (200 OK):**
```json
{
  "code": "ok",
  "msg": "success",
  "data": {
    "id": 1,
    "email": "parent@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "phoneNumber": "+1234567890",
    "role": "PARENT"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "code": "unauthorized",
  "msg": "Invalid or expired token.",
  "data": null
}
```

---

### 3. Change Password

**Endpoint:** `POST /api/auth/change-password/`  
**Authentication:** Required (Bearer token)  
**Description:** Change the authenticated user's password.

**Request Body:**
```json
{
  "oldPassword": "currentPassword123",
  "newPassword": "newSecurePassword456"
}
```

**Success Response (200 OK):**
```json
{
  "code": "ok",
  "msg": "Password changed successfully.",
  "data": null
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid old password
- `422 Validation Error` — Password too short or weak

---

### 4. Logout (Optional)

**Endpoint:** `POST /api/auth/logout/`  
**Authentication:** Required (Bearer token)  
**Description:** Invalidate the current JWT token (if token blacklisting is implemented).

**Success Response (200 OK):**
```json
{
  "code": "ok",
  "msg": "Logged out successfully.",
  "data": null
}
```

---

## Parent & Student Endpoints

### 1. Get Parent's Children

**Endpoint:** `GET /api/parent/children/`  
**Authentication:** Required (Parent role)  
**Description:** Retrieve list of students linked to the authenticated parent.

**Success Response (200 OK):**
```json
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
        "dateOfBirth": "2015-03-15",
        "admissionDate": "2020-04-01",
        "photo": "https://school.com/media/students/alice.jpg",
        "attendancePercentage": 92.5,
        "latestGrade": "A"
      },
      {
        "id": 11,
        "firstName": "Bob",
        "lastName": "Doe",
        "rollNumber": "2025002",
        "gradeClass": "Grade 3B",
        "dateOfBirth": "2017-08-20",
        "admissionDate": "2022-04-01",
        "photo": null,
        "attendancePercentage": 88.0,
        "latestGrade": "B+"
      }
    ]
  }
}
```

**Notes:**
- `attendancePercentage` — Current academic year attendance percentage
- `latestGrade` — Most recent overall grade from latest report card
- `photo` — URL to student photo (null if not uploaded)

---

### 2. Get Student Details

**Endpoint:** `GET /api/students/{student_id}/`  
**Authentication:** Required (Parent must be linked to student)  
**Description:** Retrieve detailed information about a specific student.

**Path Parameters:**
- `student_id` (integer) — Student ID

**Success Response (200 OK):**
```json
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
    "photo": "https://school.com/media/students/alice.jpg",
    "bloodGroup": "A+",
    "address": "123 Main Street, City",
    "emergencyContact": "+1234567890",
    "classTeacher": "Ms. Emily Johnson"
  }
}
```

**Error Response (403 Forbidden):**
```json
{
  "code": "forbidden",
  "msg": "You do not have permission to view this student.",
  "data": null
}
```

**Error Response (404 Not Found):**
```json
{
  "code": "not_found",
  "msg": "Student not found.",
  "data": null
}
```

---

## Attendance Endpoints

### 1. Get Student Attendance (Monthly)

**Endpoint:** `GET /api/attendance/student/{student_id}/`  
**Authentication:** Required (Parent must be linked to student)  
**Description:** Retrieve attendance records for a student for a specific month.

**Path Parameters:**
- `student_id` (integer) — Student ID

**Query Parameters:**
- `month` (string, optional) — Month in `YYYY-MM` format. Defaults to current month.

**Example Request:**
```
GET /api/attendance/student/10/?month=2026-04
```

**Success Response (200 OK):**
```json
{
  "code": "ok",
  "msg": "success",
  "data": {
    "studentId": 10,
    "studentName": "Alice Doe",
    "gradeClass": "Grade 5A",
    "month": "2026-04",
    "summary": {
      "totalDays": 22,
      "present": 20,
      "absent": 1,
      "late": 1,
      "excused": 0,
      "attendancePercentage": 90.91
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
        "remarks": "Sick leave (medical certificate submitted)"
      },
      {
        "date": "2026-04-03",
        "status": "late",
        "remarks": "Arrived at 08:15 (school starts at 08:00)"
      },
      {
        "date": "2026-04-04",
        "status": "present",
        "remarks": null
      }
      // ... more records for the month
    ]
  }
}
```

**Attendance Status Values:**
- `present` — Student attended on time
- `absent` — Student did not attend
- `late` — Student arrived late
- `excused` — Absence was excused (e.g., medical leave, school event)

**Notes:**
- Only school days are included in `records`
- `totalDays` excludes weekends and holidays
- `attendancePercentage` = (present + late + excused) / totalDays * 100

---

## Report Card Endpoints

### 1. Get Student Report Cards

**Endpoint:** `GET /api/reports/student/{student_id}/`  
**Authentication:** Required (Parent must be linked to student)  
**Description:** Retrieve list of all report cards for a student.

**Path Parameters:**
- `student_id` (integer) — Student ID

**Query Parameters:**
- `academic_year` (string, optional) — Filter by academic year (e.g., "2025-2026")
- `term` (string, optional) — Filter by term (e.g., "Q1", "Q2", "Final")

**Success Response (200 OK):**
```json
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
      },
      {
        "id": 102,
        "academicYear": "2024-2025",
        "term": "Final",
        "issuedDate": "2025-06-30",
        "overallGrade": "A",
        "overallPercentage": 91.0,
        "rank": 5,
        "totalStudents": 38
      }
    ]
  }
}
```

---

### 2. Get Report Card Details

**Endpoint:** `GET /api/reports/{report_id}/`  
**Authentication:** Required (Parent must be linked to student)  
**Description:** Retrieve detailed report card with subject-wise grades and remarks.

**Path Parameters:**
- `report_id` (integer) — Report card ID

**Success Response (200 OK):**
```json
{
  "code": "ok",
  "msg": "success",
  "data": {
    "id": 100,
    "student": {
      "id": 10,
      "firstName": "Alice",
      "lastName": "Doe",
      "rollNumber": "2025001",
      "gradeClass": "Grade 5A",
      "photo": "https://school.com/media/students/alice.jpg"
    },
    "academicYear": "2025-2026",
    "term": "Q1",
    "issuedDate": "2025-11-15",
    "subjects": [
      {
        "subjectName": "Mathematics",
        "subjectCode": "MATH5",
        "grade": "A+",
        "score": 98,
        "maxScore": 100,
        "remarks": "Excellent performance in all topics."
      },
      {
        "subjectName": "English",
        "subjectCode": "ENG5",
        "grade": "A",
        "score": 90,
        "maxScore": 100,
        "remarks": "Good comprehension and writing skills."
      },
      {
        "subjectName": "Science",
        "subjectCode": "SCI5",
        "grade": "A",
        "score": 92,
        "maxScore": 100,
        "remarks": "Shows strong understanding of concepts."
      },
      {
        "subjectName": "Social Studies",
        "subjectCode": "SS5",
        "grade": "B+",
        "score": 88,
        "maxScore": 100,
        "remarks": "Needs to improve map reading skills."
      },
      {
        "subjectName": "Physical Education",
        "subjectCode": "PE5",
        "grade": "A",
        "score": 95,
        "maxScore": 100,
        "remarks": "Excellent participation and teamwork."
      }
    ],
    "overallGrade": "A",
    "overallPercentage": 92.5,
    "rank": 3,
    "totalStudents": 40,
    "classTeacherRemarks": "Alice is a bright and diligent student. She shows excellent academic performance and actively participates in class discussions. Keep up the good work!",
    "principalRemarks": "Well done! Continue to excel."
  }
}
```

**Grade Scale:**
- `A+` — 95-100%
- `A` — 90-94%
- `B+` — 85-89%
- `B` — 80-84%
- `C+` — 75-79%
- `C` — 70-74%
- `D` — 60-69%
- `F` — Below 60% (Fail)

---

### 3. Download Report Card PDF

**Endpoint:** `GET /api/reports/{report_id}/download/`  
**Authentication:** Required (Parent must be linked to student)  
**Description:** Download report card as PDF file.

**Path Parameters:**
- `report_id` (integer) — Report card ID

**Success Response (200 OK):**
- **Content-Type:** `application/pdf`
- **Content-Disposition:** `attachment; filename="report_card_alice_doe_2025_Q1.pdf"`
- **Response Body:** PDF binary data

**Error Responses:**
- `403 Forbidden` — Parent not authorized to view this report
- `404 Not Found` — Report card not found

---

## Schedule/Timetable Endpoints

### 1. Get Student Class Schedule

**Endpoint:** `GET /api/schedule/student/{student_id}/`  
**Authentication:** Required (Parent must be linked to student)  
**Description:** Retrieve weekly class timetable for a student.

**Path Parameters:**
- `student_id` (integer) — Student ID

**Success Response (200 OK):**
```json
{
  "code": "ok",
  "msg": "success",
  "data": {
    "studentId": 10,
    "studentName": "Alice Doe",
    "gradeClass": "Grade 5A",
    "academicYear": "2025-2026",
    "schedule": {
      "Monday": [
        {
          "period": 1,
          "startTime": "08:00",
          "endTime": "08:45",
          "subject": "Mathematics",
          "subjectCode": "MATH5",
          "teacher": "Mr. David Smith",
          "room": "Room 201"
        },
        {
          "period": 2,
          "startTime": "08:45",
          "endTime": "09:30",
          "subject": "English",
          "subjectCode": "ENG5",
          "teacher": "Ms. Emily Johnson",
          "room": "Room 202"
        },
        {
          "period": 3,
          "startTime": "09:30",
          "endTime": "10:15",
          "subject": "Science",
          "subjectCode": "SCI5",
          "teacher": "Dr. Sarah Williams",
          "room": "Lab 1"
        },
        {
          "period": 4,
          "startTime": "10:15",
          "endTime": "10:30",
          "subject": "Break",
          "subjectCode": null,
          "teacher": null,
          "room": null
        },
        {
          "period": 5,
          "startTime": "10:30",
          "endTime": "11:15",
          "subject": "Social Studies",
          "subjectCode": "SS5",
          "teacher": "Mr. Robert Brown",
          "room": "Room 203"
        },
        {
          "period": 6,
          "startTime": "11:15",
          "endTime": "12:00",
          "subject": "Art",
          "subjectCode": "ART5",
          "teacher": "Ms. Lisa Davis",
          "room": "Art Studio"
        }
      ],
      "Tuesday": [
        // ... Tuesday schedule
      ],
      "Wednesday": [
        // ... Wednesday schedule
      ],
      "Thursday": [
        // ... Thursday schedule
      ],
      "Friday": [
        // ... Friday schedule
      ]
    }
  }
}
```

**Notes:**
- Schedule is organized by day of the week
- Breaks/recess periods have `subject: "Break"` and null values for teacher/room
- Time format is 24-hour (HH:MM)

---

## Announcement Endpoints

### 1. Get School Announcements

**Endpoint:** `GET /api/announcements/`  
**Authentication:** Required  
**Description:** Retrieve paginated list of school announcements.

**Query Parameters:**
- `page` (integer, optional) — Page number (default: 1)
- `per_page` (integer, optional) — Items per page (default: 10, max: 50)
- `priority` (string, optional) — Filter by priority (`HIGH`, `NORMAL`, `LOW`)

**Success Response (200 OK):**
```json
{
  "code": "ok",
  "msg": "success",
  "data": {
    "results": [
      {
        "id": 50,
        "title": "Parent-Teacher Meeting on April 25",
        "content": "Dear parents, we will have a parent-teacher meeting...",
        "excerpt": "Dear parents, we will have a parent-teacher meeting...",
        "datePosted": "2026-04-15T10:00:00Z",
        "targetAudience": "ALL",
        "priority": "HIGH",
        "hasAttachments": true
      },
      {
        "id": 51,
        "title": "School Holiday on April 21",
        "content": "The school will be closed on April 21 for Easter holiday.",
        "excerpt": "The school will be closed on April 21 for Easter holiday.",
        "datePosted": "2026-04-10T09:00:00Z",
        "targetAudience": "ALL",
        "priority": "NORMAL",
        "hasAttachments": false
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

**Target Audience Values:**
- `ALL` — All parents
- `GRADE_5A` — Specific grade/class (e.g., Grade 5A parents only)

**Priority Values:**
- `HIGH` — Urgent/important
- `NORMAL` — Regular announcement
- `LOW` — Informational

---

### 2. Get Announcement Details

**Endpoint:** `GET /api/announcements/{announcement_id}/`  
**Authentication:** Required  
**Description:** Retrieve detailed information about a specific announcement.

**Path Parameters:**
- `announcement_id` (integer) — Announcement ID

**Success Response (200 OK):**
```json
{
  "code": "ok",
  "msg": "success",
  "data": {
    "id": 50,
    "title": "Parent-Teacher Meeting on April 25",
    "content": "Dear parents,\n\nWe will have a parent-teacher meeting on April 25, 2026...",
    "datePosted": "2026-04-15T10:00:00Z",
    "targetAudience": "ALL",
    "priority": "HIGH",
    "attachments": [
      {
        "id": 10,
        "fileName": "meeting-schedule.pdf",
        "fileSize": 245678,
        "fileUrl": "https://school.com/media/announcements/meeting-schedule.pdf"
      },
      {
        "id": 11,
        "fileName": "attendance-form.pdf",
        "fileSize": 123456,
        "fileUrl": "https://school.com/media/announcements/attendance-form.pdf"
      }
    ],
    "postedBy": {
      "name": "Principal Office",
      "role": "ADMIN"
    }
  }
}
```

---

## School Configuration Endpoints

### 1. Get School Information

**Endpoint:** `GET /api/school/info/`  
**Authentication:** Required  
**Description:** Retrieve school branding and contact information.

**Success Response (200 OK):**
```json
{
  "code": "ok",
  "msg": "success",
  "data": {
    "name": "Green Valley High School",
    "logo": "https://school.com/media/school/logo.png",
    "address": "123 Education Street, City, State, ZIP",
    "phone": "+1234567890",
    "email": "info@greenvalley.edu",
    "website": "https://greenvalley.edu",
    "branding": {
      "primaryColor": "#1976D2",
      "accentColor": "#FFA726"
    },
    "academicYear": {
      "current": "2025-2026",
      "startDate": "2025-08-01",
      "endDate": "2026-06-30"
    }
  }
}
```

**Notes:**
- `branding.primaryColor` and `branding.accentColor` should be used for theming the mobile app
- `logo` URL can be used to display school logo in app header

---

## Rate Limiting

To prevent abuse, API rate limiting is enforced:

- **Authenticated requests**: 1000 requests per hour per user
- **Unauthenticated requests**: 100 requests per hour per IP

When rate limit is exceeded, the API returns:

```json
{
  "code": "rate_limit_exceeded",
  "msg": "Too many requests. Please try again later.",
  "data": {
    "retryAfter": 3600
  }
}
```

**HTTP Status:** 429 Too Many Requests

---

## Versioning

The API currently does not use versioning (v1 is implicit). Future breaking changes will introduce versioned endpoints (e.g., `/api/v2/`).

---

## Support

For API support or to report issues, contact the development team.

---

**Last Updated**: April 21, 2026

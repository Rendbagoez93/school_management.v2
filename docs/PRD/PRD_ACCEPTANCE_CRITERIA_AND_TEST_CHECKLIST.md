# PRD Acceptance Criteria and Test Checklist

Version: 1.0  
Date: April 23, 2026

This checklist translates PRD requirements into verifiable acceptance criteria for QA and engineering.

---

## 1. Authentication and Authorization

### AC-AUTH-001 Parent Login
- Given valid parent credentials, when login is requested, then API returns 200 with token and parent profile in standard wrapper.
- Given invalid credentials, then API returns 401 with `code=auth_failed` and `data=null`.

### AC-AUTH-002 Authenticated Profile
- Given valid bearer token, `/api/auth/me/` returns user identity and role.
- Given missing or invalid token, endpoint returns `unauthorized`.

### AC-AUTH-003 Change Password
- Given correct old password and valid new password, API returns success message.
- Given incorrect old password, API returns 401.
- Given weak new password, API returns validation error.

### AC-AUTHZ-001 Parent-to-Student Access
- Parent can access only linked student IDs.
- Access to non-linked student detail, attendance, schedule, or report endpoints returns `forbidden`.

---

## 2. API Contract Consistency

### AC-API-001 Standard Wrapper
For each parent-facing endpoint:
- Success payload uses `code`, `msg`, `data` fields.
- Error payload uses `code`, `msg`, and `data=null`.
- Paginated responses include `pagination.totalItems`, `totalPages`, `currentPage`, `perPage`.

### AC-API-002 Error Code Stability
- Error codes use documented values: `auth_failed`, `unauthorized`, `forbidden`, `not_found`, `validation_error`, `server_error`, and rate limit code.

### AC-API-003 Rate Limiting
- Authenticated requests above threshold receive 429 with retry metadata.
- Unauthenticated abuse receives corresponding 429 response.

---

## 3. Student and Relationship Data

### AC-STU-001 Children List
- `/api/parent/children/` returns only linked children.
- Each child item includes key fields: id, name, roll number, grade/class, photo (nullable).

### AC-STU-002 Student Detail
- `/api/students/{id}/` returns documented student details for linked parent.
- Unknown ID returns `not_found`.

### AC-STU-003 Data Integrity
- Student roll number uniqueness enforced at persistence layer.
- Parent-student mapping uniqueness enforced for duplicate links.

---

## 4. Attendance

### AC-ATT-001 Monthly Attendance Retrieval
- `/api/attendance/student/{id}/?month=YYYY-MM` returns summary and records.
- Summary includes totalDays, present, absent, late, excused, attendancePercentage.

### AC-ATT-002 Status Vocabulary
- Status values are constrained to documented set for student attendance.

### AC-ATT-003 Uniqueness Constraint
- System rejects duplicate attendance entries for same student and date.

### AC-ATT-004 Authorization
- Parent cannot fetch attendance for non-linked student.

---

## 5. Report Cards

### AC-RPT-001 Report List
- `/api/reports/student/{id}/` returns report summaries with academic year, term, grade, percentage, rank.

### AC-RPT-002 Report Detail
- `/api/reports/{report_id}/` returns subject-level rows and overall metadata.
- Response includes teacher and principal remarks where available.

### AC-RPT-003 PDF Download
- `/api/reports/{report_id}/download/` returns PDF binary for authorized parent.
- Unauthorized access is blocked.

### AC-RPT-004 Uniqueness Constraint
- Duplicate report rows for same student, academic year, and term are prevented.

---

## 6. Schedule

### AC-SCH-001 Weekly Timetable
- `/api/schedule/student/{id}/` returns schedule grouped by weekdays.
- Entries include period, start/end times, subject, teacher, and room.

### AC-SCH-002 Conflict Prevention
- DB constraints prevent duplicate class period assignments for same grade/day/period.

---

## 7. Announcements

### AC-ANN-001 Announcement List
- `/api/announcements/` supports pagination and optional priority filter.
- Response includes priority and audience metadata.

### AC-ANN-002 Announcement Detail
- `/api/announcements/{id}/` returns full content and attachment metadata.

### AC-ANN-003 Sorting and Freshness
- Default sort is newest first.
- Newly posted announcements become visible in list within expected refresh window.

---

## 8. School Configuration and Branding

### AC-BRD-001 School Info Endpoint
- `/api/school/info/` returns school name, logo, contact info, branding colors, and current academic year context.

### AC-BRD-002 Mobile Branding Application
- Mobile app applies primary and accent color values from backend branding.
- Missing branding values fall back to safe defaults without crash.

---

## 9. Non-Functional Quality Gates

### AC-NFR-001 Query Efficiency
- Core read endpoints use relationship loading patterns to avoid N+1 behavior.

### AC-NFR-002 Availability and Resilience
- Service uptime and backup procedures follow target operational policy.

### AC-NFR-003 Logging
- Structured logs emitted for creation/update/failure in service-level operations.

### AC-NFR-004 Testing Coverage Baseline
- Model constraints, service logic, and API permission paths covered by automated tests.

---

## 10. Mobile UX Validation Checklist

- Splash routing handles valid/invalid tokens.
- Login shows loading, success, and error states.
- Dashboard shows children or empty state appropriately.
- Child detail tabs load attendance/reports/schedule independently.
- Announcement list and detail support refresh and attachment actions.
- Profile supports password change and logout.
- Accessibility checks: content descriptions, contrast, touch target sizing.

---

## 11. Regression Checklist Before Release

- Authentication endpoints pass happy path and negative tests.
- Permission tests verify parent cannot traverse to other students.
- Pagination metadata validated for list endpoints.
- Report PDF downloads validated for auth and file type headers.
- Announcement filters and detail endpoints validated.
- School branding values verified on mobile startup.
- Backup and restore smoke test performed in staging.

---

## 12. Sign-off Criteria

Release can proceed when:
- P0 acceptance criteria are fully passed.
- No unresolved high-severity authorization or data integrity defects.
- API contract tests pass for documented parent-facing endpoints.
- Mobile core flow smoke tests are green.

# PRD Epics and User Stories

Version: 1.0  
Date: April 23, 2026

This document decomposes the PRD into delivery epics and implementation-ready user stories.

---

## Epic 1: Authentication and Account Security

### Story 1.1 Parent Login
As a parent, I want to log in with email and password so I can access my children information.
- Priority: P0
- Dependencies: Auth API endpoint, JWT issuance
- Acceptance summary:
  - Valid credentials return token and parent profile.
  - Invalid credentials return `auth_failed` with no token.

### Story 1.2 Session Validation
As a parent, I want the app to validate my token on startup so I am automatically routed correctly.
- Priority: P0
- Dependencies: `GET /api/auth/me/`
- Acceptance summary:
  - Valid token routes to dashboard.
  - Invalid/expired token routes to login.

### Story 1.3 Change Password
As an authenticated user, I want to change my password so I can maintain account security.
- Priority: P1
- Dependencies: password policy, auth middleware
- Acceptance summary:
  - Old password verification required.
  - Weak passwords rejected with validation error.

---

## Epic 2: Parent-Child Relationship Access Control

### Story 2.1 List Linked Children
As a parent, I want to see only my linked children so I can select a child safely.
- Priority: P0
- Dependencies: parent-student relationship table
- Acceptance summary:
  - Endpoint returns only linked students.
  - Empty state shown when none linked.

### Story 2.2 Enforce Child Detail Authorization
As a parent, I want child details protected so no unauthorized data is exposed.
- Priority: P0
- Dependencies: relationship authorization checks
- Acceptance summary:
  - Linked parent gets student payload.
  - Unlinked parent receives `forbidden`.

---

## Epic 3: Student Profile and Academic Context

### Story 3.1 Student Detail View
As a parent, I want complete child profile details so I can review current school information.
- Priority: P1
- Dependencies: student, class, teacher data
- Acceptance summary:
  - Response includes roll number, grade, DOB, admission date, and class teacher.

### Story 3.2 Historical Academic Context
As a parent, I want data organized by academic year so I can review history accurately.
- Priority: P1
- Dependencies: academic year model and filters
- Acceptance summary:
  - Relevant endpoints support academic year filtering where documented.

---

## Epic 4: Attendance Visibility

### Story 4.1 Monthly Attendance Summary
As a parent, I want monthly attendance summaries so I can monitor attendance performance quickly.
- Priority: P0
- Dependencies: daily attendance records and monthly aggregation
- Acceptance summary:
  - Summary includes total days, present/absent/late/excused, percentage.

### Story 4.2 Daily Attendance Details
As a parent, I want per-day attendance records and remarks so I can understand absences or lateness.
- Priority: P0
- Dependencies: attendance remarks and status mapping
- Acceptance summary:
  - Day-level records include date, status, and remarks.

---

## Epic 5: Report Card Management

### Story 5.1 Report List
As a parent, I want to list report cards by child so I can see term performance snapshots.
- Priority: P0
- Dependencies: report card summaries
- Acceptance summary:
  - List includes term, academic year, grade, percentage, rank.

### Story 5.2 Report Detail
As a parent, I want subject-level report details so I can identify strengths and weaknesses.
- Priority: P0
- Dependencies: report subject details and remarks
- Acceptance summary:
  - Subject rows include grade, score/max score, remarks.
  - Includes overall grade, percentage, rank, teacher/principal remarks.

### Story 5.3 Report PDF Download
As a parent, I want to download report PDFs so I can store and share official records.
- Priority: P1
- Dependencies: PDF generation/download endpoint
- Acceptance summary:
  - Authorized user receives PDF with valid content disposition.

---

## Epic 6: Timetable and Schedule

### Story 6.1 Weekly Class Schedule
As a parent, I want to view my child timetable so I can plan daily routines.
- Priority: P1
- Dependencies: schedule mapping by weekdays
- Acceptance summary:
  - Response grouped by day and includes period/time/subject/teacher/room.

### Story 6.2 Break and Null Slot Handling
As a parent, I want non-class periods represented clearly so timetable understanding is accurate.
- Priority: P2
- Dependencies: schedule data representation rules
- Acceptance summary:
  - Break periods represented as documented (`subject=Break`, null teacher/room).

---

## Epic 7: School Announcements

### Story 7.1 Announcement Feed
As a parent, I want paginated announcements so I can stay informed about school events.
- Priority: P0
- Dependencies: announcement API and pagination
- Acceptance summary:
  - Feed returns title, date, priority, excerpt, and pagination metadata.

### Story 7.2 Announcement Detail and Attachments
As a parent, I want announcement details and attachments so I can access full information.
- Priority: P1
- Dependencies: attachment model and secure file hosting
- Acceptance summary:
  - Detail includes full content and attachment metadata.

---

## Epic 8: School Branding and Identity

### Story 8.1 Dynamic School Branding
As a parent, I want app visuals to match school branding so the app feels official and trusted.
- Priority: P1
- Dependencies: school info endpoint
- Acceptance summary:
  - App uses school name/logo/primary/accent colors from API.

### Story 8.2 Academic Year Visibility
As a parent, I want current academic year context visible so I can interpret current records correctly.
- Priority: P2
- Dependencies: school info payload with current year
- Acceptance summary:
  - Current academic year displayed in relevant views.

---

## Epic 9: Platform Quality and Reliability

### Story 9.1 Standard Response Contract Compliance
As a mobile developer, I want consistent API response structures so client parsing remains stable.
- Priority: P0
- Dependencies: shared API wrapper utilities
- Acceptance summary:
  - Endpoints conform to standard wrapper for success/error/list/pagination.

### Story 9.2 Query and Index Performance
As an operations team member, I want performant queries so parent-facing endpoints remain responsive.
- Priority: P1
- Dependencies: index strategy, ORM query optimization
- Acceptance summary:
  - Endpoints use related-loading and pagination where needed.

### Story 9.3 Backup and Recovery Readiness
As a system owner, I want backup and restore practices so data loss risk is controlled.
- Priority: P1
- Dependencies: DB operations process
- Acceptance summary:
  - Daily full backups, six-hour incrementals, regular restore drills.

---

## Epic 10: Development and Delivery Governance

### Story 10.1 Testing Strategy Enforcement
As an engineering lead, I want standardized tests so regressions are caught early.
- Priority: P0
- Dependencies: pytest and factory-based test setup
- Acceptance summary:
  - Critical modules covered by model/service/API tests.

### Story 10.2 Logging and Observability Standards
As a maintainer, I want structured logs so incidents can be diagnosed quickly.
- Priority: P1
- Dependencies: structlog configuration
- Acceptance summary:
  - Key service events and failures logged with structured fields.

### Story 10.3 Documentation Sync
As a project manager, I want docs updated with changes so teams remain aligned.
- Priority: P1
- Dependencies: documentation maintenance workflow
- Acceptance summary:
  - API/schema/feature docs updated when implementation changes.

---

## Suggested Delivery Sequence

1. Epic 1
2. Epic 2
3. Epic 4
4. Epic 5
5. Epic 7
6. Epic 6
7. Epic 8
8. Epic 9
9. Epic 10
10. Epic 3 (ongoing refinements)

---

## Release Mapping

- Phase 1 (MVP): Epic 1
- Phase 2: Epic 2 + Epic 3 (basic) + Dashboard elements
- Phase 3: Epic 4 + Epic 5 + Epic 6 + Epic 7
- Phase 4: Epic 8 + Epic 9 enhancements + advanced roadmap modules

# Product Requirements Document (PRD)

## School Management System (Web + Parent Mobile)

Version: 1.0  
Date: April 23, 2026  
Status: Draft for implementation alignment  
Source of truth: Consolidated from documentation in `.github/`

---

## 1. Executive Summary

School Management System is a single-instance packaged platform for one school per installation. It provides:
- Web administration and school operations for administrators, teachers, and staff.
- Android Parent Portal for parent-facing visibility into child performance and school communication.

This product is not multi-tenant SaaS. Every installation serves one institution with school-specific branding, data, and operational setup.

Primary value:
- Centralize academic operations.
- Improve parent-school transparency.
- Standardize school workflows and records.
- Enable role-based secure access to school data.

---

## 2. Product Vision and Problem Statement

### 2.1 Vision
Deliver an integrated, secure, and maintainable school operations platform where school staff manage academics and administration, and parents monitor their children through a dedicated mobile experience.

### 2.2 Problems Being Solved
- Fragmented student records and attendance tracking.
- Delayed parent communication for announcements and report cards.
- Lack of standardized grade/schedule/report workflows.
- Inconsistent school branding and information exposure across channels.

### 2.3 Product Principles
- Single-school deployment model.
- API-first backend with consistent response contracts.
- Role-based authorization and data segregation by relationship.
- Clean Architecture for mobile maintainability.
- Standardized error handling and observability.

---

## 3. Goals, Non-Goals, and Success Criteria

### 3.1 Business Goals
- Reduce operational overhead for school staff.
- Increase parent engagement through timely updates.
- Improve data quality via validated API contracts and schema constraints.
- Maintain extensibility for roadmap features (fees, library, transport, analytics).

### 3.2 Product Goals
- Provide core modules: users, students, attendance, reports, schedule, announcements, school config.
- Provide parent authentication and child-linked data access.
- Support dynamic school branding in web and mobile UI.
- Preserve historical records by academic year.

### 3.3 Non-Goals (Current Scope)
- Multi-school tenancy and shared cloud tenancy.
- Parent portal for iOS (Android only in current mobile plan).
- Advanced financial systems beyond future roadmap intent.
- Real-time bi-directional chat (future optional in-app messaging).

### 3.4 Success Metrics (Initial)
- Parent login success rate: >= 98% for valid credentials.
- API availability: >= 99.5% monthly uptime target.
- Attendance data accuracy: 100% unique per student/date (enforced by constraints).
- Report access latency (P95): <= 2.0s for detail endpoint under normal load.
- Announcement delivery freshness: new announcement visible in app within 60s of publication.

---

## 4. Stakeholders and Personas

### 4.1 Stakeholders
- School owner/management.
- Principal and vice principal.
- Administrative staff.
- Teachers and non-teaching staff.
- Parents/guardians.
- Engineering and QA teams.

### 4.2 Primary Personas
- Parent: views children, attendance, reports, schedules, announcements.
- Admin/Principal: configures school, manages users, oversees records, publishes announcements.
- Teacher: contributes attendance and academic records.
- Staff: operational roles with role-based access.

---

## 5. Product Scope

### 5.1 In-Scope Domains (Core)
- School configuration and branding.
- User and role management (Admin, Principal, VP, Teacher, Staff, Parent, others in role enum).
- Academic years and grades/classes.
- Student management and parent-student linking.
- Attendance (student, teacher, staff).
- Report card generation and retrieval.
- Timetable/schedule management and retrieval.
- Announcement publishing and consumption.
- Parent mobile app core flows.

### 5.2 Post-MVP / Future Scope
- Online fee payment.
- Library management.
- Transport tracking.
- Health records.
- Exam scheduling/hall tickets.
- SMS/email notifications.
- Advanced analytics dashboards.
- Teacher-focused mobile workflows.

---

## 6. Functional Requirements

### FR-1 Authentication and Session
- System shall support email/password login for parent users.
- System shall support role-based authentication model for staff/teachers (email+password and/or Google OAuth where configured).
- System shall provide authenticated profile retrieval endpoint.
- System shall support password change for authenticated users.
- System shall return standardized response wrapper with `code`, `msg`, and `data`.

### FR-2 Parent-Student Relationship Access Control
- Parent users shall access only students linked to their account.
- Student detail, attendance, reports, and schedules shall enforce relationship-based authorization.
- Unauthorized access attempts shall return `forbidden` or `unauthorized` codes as applicable.

### FR-3 Student Management
- System shall store student profile with roll number, personal details, class, and emergency data.
- System shall maintain unique roll number constraints.
- System shall expose parent-safe student detail payloads via API.

### FR-4 Attendance
- System shall store daily attendance for students, teachers, and staff as separate records.
- Student attendance shall support status values: present, absent, late, excused.
- Attendance shall enforce unique record per student/date.
- Monthly attendance API shall return summary and day-level records.

### FR-5 Academic Reports
- System shall provide report card list and detail by student.
- Report detail shall include subject-wise grade, score, max score, remarks, and overall statistics.
- System shall support report card PDF download endpoint.
- Report card uniqueness shall be enforced by student + academic year + term.

### FR-6 Schedule/Timetable
- System shall store and expose weekly timetable per class/student.
- Schedule retrieval shall group data by weekdays.
- Timetable entries shall include period, time range, subject, teacher, and room.
- Unique constraints shall prevent period conflicts per class/day/period.

### FR-7 Announcements
- System shall allow school announcements with priority and target audience.
- Parent app shall retrieve paginated announcement lists and details.
- Announcement details shall include attachments metadata when present.
- Priority and audience fields shall be filterable in list retrieval.

### FR-8 School Branding and Configuration
- System shall provide school identity and branding values (name, logo, colors, contact info).
- Mobile app shall consume branding values to theme UI dynamically.
- School entity shall behave as a singleton per installation.

### FR-9 API Consistency
- All APIs shall use standardized wrapper format for success/error responses.
- Error responses shall expose stable error codes (`validation_error`, `auth_failed`, etc.).
- Paginated endpoints shall include `pagination` object with total/page metadata.

### FR-10 Web Operational Administration
- Web interface shall support school operations management for configured modules.
- Views shall maintain English UI copy unless region-specific localization is introduced.
- App-specific URL namespacing shall be used for web and API routes.

---

## 7. Mobile Parent Portal Requirements (Android)

### 7.1 Architecture and Platform
- Android app shall use Kotlin 2.x and Jetpack Compose with Material 3.
- App shall implement Clean Architecture (Data, Domain, Presentation layers).
- Dependency injection shall use Hilt.
- API layer shall use Retrofit + OkHttp.
- Serialization shall use Kotlinx Serialization.

### 7.2 Core Screens and Flows
- Splash: token check and routing.
- Login: email/password authentication.
- Dashboard: children list and quick stats.
- Child Detail: tabs for attendance, reports, schedule.
- Reports: list + detail + PDF download.
- Announcements: list + detail + attachments.
- Profile: view profile, change password, logout.

### 7.3 UI System
- Reusable components shall use `Sms` prefix.
- No inline ad-hoc colors; use theme tokens and school branding.
- English copy required by default.
- Accessibility baseline: content descriptions, WCAG AA contrast, minimum 48dp touch targets.

---

## 8. Data and Domain Requirements

### 8.1 Core Data Entities
- Auth user, school, academic year, grade, subject, student, teacher, staff.
- Linking entities: teacher-subject, parent-student.
- Operational entities: schedule, attendance (3 types), report card, report card subject, announcement, attachments.

### 8.2 Integrity Constraints
- Single current academic year.
- Unique roll numbers and employee IDs.
- Unique attendance per actor/date.
- Unique report per student/academic-year/term.
- Parent-student and teacher-subject association uniqueness constraints.

### 8.3 Historical Record Preservation
- Academic years and report records must preserve historical data.
- Soft-deletion or active flags shall be preferred for critical records.

---

## 9. Security and Compliance Requirements

- JWT bearer authentication for protected endpoints.
- Role and relationship authorization for data access.
- Passwords stored as secure hashes.
- Admin access isolated through staff/superuser permissions.
- API shall avoid leaking internal implementation detail in error messages.
- Audit-friendly timestamps required for critical entities.

---

## 10. Non-Functional Requirements

### 10.1 Performance
- API responses should use optimized query patterns (`select_related`, `prefetch_related`, field limiting).
- Default pagination for list APIs.
- P95 target under typical load for core read endpoints <= 2s.

### 10.2 Reliability and Availability
- Target service uptime >= 99.5% monthly.
- Daily backup with incremental backups every 6 hours.
- Restore drills monthly.

### 10.3 Scalability
- System optimized for single-school scale, moderate concurrent parent and staff usage.
- Schema and API design should support future module expansion.

### 10.4 Maintainability
- Backend logic in service layer; avoid business logic in views/models where possible.
- Typed interfaces and validated request parsing required.
- Test suite with pytest + factory-based test data.

### 10.5 Observability
- Structured logging via structlog in backend services.
- Key service events and failures must be logged with contextual fields.

---

## 11. API Requirements and Contract Standards

- Endpoints must expose stable JSON schemas for mobile clients.
- Standard response contract:
  - Success: `code=ok`, `msg=success`, `data=<payload>`
  - Error: `code=<error_code>`, `msg=<message>`, `data=null`
- Rate limits:
  - Authenticated: 1000 req/hour/user.
  - Unauthenticated: 100 req/hour/IP.
- Versioning:
  - v1 implicit today.
  - Breaking changes require explicit versioned endpoints in future.

---

## 12. Release Plan and Milestones

### Phase 1: Authentication MVP
- Parent login, profile retrieval, password change.
- Token storage and auth gate in mobile.

### Phase 2: Dashboard and Child Selection
- Child list retrieval and dashboard summary cards.
- Navigation to per-child detail.

### Phase 3: Core Parent Features
- Attendance monthly view.
- Report list/detail/PDF.
- Schedule view.
- Announcements list/detail.

### Phase 4: Advanced Enhancements
- Offline caching.
- Notification improvements.
- Optional fee and communication features.

---

## 13. Dependencies and Technical Constraints

- Backend stack: Django ASGI, DRF + Pydantic validation pattern, PostgreSQL.
- Python version baseline: 3.14+.
- Mobile baseline: Android min SDK 24, target SDK 35.
- Deployment model: one installation per school.
- Language baseline: English for UI/API/code content.

---

## 14. Risks and Mitigations

- Risk: API contract drift between docs and implementation.
  - Mitigation: contract tests and synchronized API reference updates.
- Risk: Authorization gaps exposing cross-student data.
  - Mitigation: strict parent-student relationship checks on every child-scoped endpoint.
- Risk: Performance degradation on list endpoints.
  - Mitigation: pagination, indexes, query optimization patterns.
- Risk: Mobile theming inconsistency with school branding.
  - Mitigation: mandatory dynamic branding ingestion from school info endpoint.
- Risk: Notification fatigue from announcements.
  - Mitigation: priority levels and future digest strategy.

---

## 15. Acceptance Criteria (PRD-Level)

- Core parent journeys (login -> child selection -> attendance/report/schedule/announcements -> logout) are end-to-end functional.
- Data returned by parent endpoints is strictly constrained to linked students.
- API wrapper consistency is validated across all parent-facing endpoints.
- Database constraints prevent duplicate attendance/report records as specified.
- School branding endpoint successfully drives mobile identity surfaces.
- Test coverage includes model constraints, service logic, and API behavior for critical workflows.

---

## 16. Out of Scope for Current PRD Iteration

- Multi-school SaaS tenancy.
- iOS app.
- Full fee/billing implementation.
- Full messaging platform.
- Extensive regional localization and RTL support.

---

## 17. Open Questions

- What are formal SLO values per endpoint category beyond global availability targets?
- Should teacher/staff mobile features be split into separate app or role-gated modules in same app?
- Is report PDF generation synchronous or queued for larger schools?
- What is the final policy for JWT invalidation/blacklisting on logout?

---

## 18. Traceability

Detailed user stories and testable acceptance criteria are captured in:
- docs/PRD/PRD_EPICS_AND_USER_STORIES.md
- docs/PRD/PRD_ACCEPTANCE_CRITERIA_AND_TEST_CHECKLIST.md

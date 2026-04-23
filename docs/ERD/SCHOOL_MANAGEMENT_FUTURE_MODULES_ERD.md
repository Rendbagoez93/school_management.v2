# School Management System ERD (Future / Unimplemented Modules)

Date: April 23, 2026  
Scope: Target-state ERD for modules that are planned or partially unimplemented in current code.

This ERD is intended to complement the current implemented ERD (`SCHOOL_MANAGEMENT_ERD.md`) and focuses on planned entities for:
- school configuration
- student domain expansion (full student record with roll number, admission date, etc.)
- parent-student explicit linking (with relationship metadata)
- subjects and teacher-subject assignment
- schedule/timetable
- attendance (student, teacher, staff)
- report cards
- announcements

> **Note on current thin profiles**: The existing `applications.user_management` app already has thin `Student` and `Parent` profile models (a OneToOne to `User` with only `address` and `attributes` fields). The future `student_management` and `parent_management` modules described here represent the full domain expansion with dedicated records. When those modules are implemented, the thin profiles may be extended or replaced.

## References Used

- `.github/copilot-instructions.md` — authoritative backend design and architecture reference
- `.github/api-reference.md` — target API contract for mobile/parent endpoints
- `.github/mobile-dev.md` — mobile integration plan
- `docs/ERD/SCHOOL_MANAGEMENT_ERD.md` — current implemented schema (authoritative source)

> Note: `.github/database-schema.md` references an earlier design iteration. The field definitions and table names in that file do not match the current implementation. This future ERD is aligned with `copilot-instructions.md` and the current codebase as the authoritative sources.

## Target-State ERD (Mermaid)

```mermaid
erDiagram
    SCHOOL {
        bigint id PK
        string name
        string logo
        text address
        string phone
        string email
        string website
        string primary_color
        string accent_color
        datetime created_at
        datetime updated_at
    }

    USER {
        uuid id PK
        string email UK
        string role
        string first_name
        string last_name
        string phone_number
        bool is_active
        bool is_staff
        bool is_verified
        datetime date_joined
        datetime date_modified
        bool is_deleted
        datetime deleted_at
    }

    ACADEMIC_YEAR {
        bigint id PK
        string name UK
        date start_date
        date end_date
        bool is_active
        string status
        string deployment_type
        bool setup_completed
        datetime date_joined
        datetime date_modified
        bool is_deleted
        datetime deleted_at
    }

    GRADE {
        bigint id PK
        string name
        string grade
        string grade_type
        string grade_subtype
        bigint academic_year_id FK
        bool is_active
        datetime date_joined
        datetime date_modified
        bool is_deleted
        datetime deleted_at
    }

    STUDENT_RECORD {
        bigint id PK
        uuid user_id FK
        string roll_number UK
        date date_of_birth
        date admission_date
        bigint current_grade_id FK
        string photo
        string blood_group
        text address
        string emergency_contact
        bool is_active
        datetime created_at
        datetime updated_at
    }

    PARENT_RECORD {
        bigint id PK
        uuid user_id FK
        text address
        json attributes
        datetime date_joined
        datetime date_modified
    }

    PARENT_STUDENT_LINK {
        bigint id PK
        bigint parent_id FK
        bigint student_id FK
        string relationship
        bool is_primary_contact
        datetime created_at
    }

    TEACHER {
        bigint id PK
        uuid user_id FK
        string employee_id UK
        string department
        string specialization
        date date_of_joining
        bool is_active
        datetime date_joined
        datetime date_modified
        bool is_deleted
        datetime deleted_at
    }

    STAFF_MEMBER {
        bigint id PK
        uuid user_id FK
        string employee_id UK
        string department
        string job_title
        date date_of_joining
        bool is_active
        datetime date_joined
        datetime date_modified
        bool is_deleted
        datetime deleted_at
    }

    SUBJECT {
        bigint id PK
        string name
        string code UK
        int grade_level
        text description
        bool is_active
        datetime created_at
        datetime updated_at
    }

    TEACHER_SUBJECT {
        bigint id PK
        bigint teacher_id FK
        bigint subject_id FK
        bigint grade_id FK
    }

    SCHEDULE {
        bigint id PK
        bigint grade_id FK
        bigint subject_id FK
        bigint teacher_id FK
        int day_of_week
        int period
        time start_time
        time end_time
        string room
        bool is_active
        datetime created_at
        datetime updated_at
    }

    STUDENT_ATTENDANCE {
        bigint id PK
        bigint student_id FK
        date date
        string status
        text remarks
        uuid marked_by_id FK
        datetime marked_at
        datetime created_at
        datetime updated_at
    }

    TEACHER_ATTENDANCE {
        bigint id PK
        bigint teacher_id FK
        date date
        string status
        text remarks
        uuid marked_by_id FK
        datetime marked_at
        datetime created_at
        datetime updated_at
    }

    STAFF_ATTENDANCE {
        bigint id PK
        bigint staff_id FK
        date date
        string status
        text remarks
        uuid marked_by_id FK
        datetime marked_at
        datetime created_at
        datetime updated_at
    }

    REPORT_CARD {
        bigint id PK
        bigint student_id FK
        bigint academic_year_id FK
        string term
        date issued_date
        string overall_grade
        decimal overall_percentage
        int rank
        int total_students
        text class_teacher_remarks
        text principal_remarks
        datetime created_at
        datetime updated_at
    }

    REPORT_CARD_SUBJECT {
        bigint id PK
        bigint report_card_id FK
        bigint subject_id FK
        string grade
        decimal score
        decimal max_score
        text remarks
        datetime created_at
        datetime updated_at
    }

    ANNOUNCEMENT {
        bigint id PK
        string title
        text content
        string target_audience
        string priority
        datetime date_posted
        uuid posted_by_id FK
        bool is_active
        datetime created_at
        datetime updated_at
    }

    ANNOUNCEMENT_ATTACHMENT {
        bigint id PK
        bigint announcement_id FK
        string file_name
        string file
        int file_size
        datetime created_at
    }

    SCHOOL ||--o{ ACADEMIC_YEAR : configures

    ACADEMIC_YEAR ||--o{ GRADE : has
    GRADE ||--o{ STUDENT_RECORD : current_grade

    USER ||--o| STUDENT_RECORD : owns_student_account
    USER ||--o| PARENT_RECORD : owns_parent_account
    USER ||--o| TEACHER : owns_teacher_account
    USER ||--o| STAFF_MEMBER : owns_staff_account

    PARENT_RECORD ||--o{ PARENT_STUDENT_LINK : links
    STUDENT_RECORD ||--o{ PARENT_STUDENT_LINK : linked_to

    TEACHER ||--o{ TEACHER_SUBJECT : teaches
    SUBJECT ||--o{ TEACHER_SUBJECT : assigned
    GRADE ||--o{ TEACHER_SUBJECT : scoped_to

    GRADE ||--o{ SCHEDULE : has
    SUBJECT ||--o{ SCHEDULE : planned_as
    TEACHER ||--o{ SCHEDULE : delivered_by

    STUDENT_RECORD ||--o{ STUDENT_ATTENDANCE : has
    TEACHER ||--o{ TEACHER_ATTENDANCE : has
    STAFF_MEMBER ||--o{ STAFF_ATTENDANCE : has
    USER ||--o{ STUDENT_ATTENDANCE : marks
    USER ||--o{ TEACHER_ATTENDANCE : marks
    USER ||--o{ STAFF_ATTENDANCE : marks

    STUDENT_RECORD ||--o{ REPORT_CARD : receives
    ACADEMIC_YEAR ||--o{ REPORT_CARD : within
    REPORT_CARD ||--o{ REPORT_CARD_SUBJECT : contains
    SUBJECT ||--o{ REPORT_CARD_SUBJECT : evaluated_as

    USER ||--o{ ANNOUNCEMENT : posts
    ANNOUNCEMENT ||--o{ ANNOUNCEMENT_ATTACHMENT : has
```

## Module-to-Entity Mapping

- school_config (future): SCHOOL
- student_management (future): STUDENT_RECORD, PARENT_STUDENT_LINK
- parent_management (future): PARENT_RECORD, PARENT_STUDENT_LINK
- attendance (future): STUDENT_ATTENDANCE, TEACHER_ATTENDANCE, STAFF_ATTENDANCE
- reports (future): REPORT_CARD, REPORT_CARD_SUBJECT
- schedule (future): SCHEDULE, SUBJECT, TEACHER_SUBJECT
- announcements (future): ANNOUNCEMENT, ANNOUNCEMENT_ATTACHMENT

## Planned Constraints (Recommended)

- Single active school record (singleton behavior) for SCHOOL.
- Unique: SUBJECT.code.
- Unique: PARENT_STUDENT_LINK(parent_id, student_id).
- Unique: TEACHER_SUBJECT(teacher_id, subject_id, grade_id).
- Unique: SCHEDULE(grade_id, day_of_week, period).
- Unique: STUDENT_ATTENDANCE(student_id, date).
- Unique: TEACHER_ATTENDANCE(teacher_id, date).
- Unique: STAFF_ATTENDANCE(staff_id, date).
- Unique: REPORT_CARD(student_id, academic_year_id, term).
- Unique: REPORT_CARD_SUBJECT(report_card_id, subject_id).

## Gap vs Current Implemented ERD

The following entities are future/unimplemented or only partially represented today:
- SCHOOL
- SUBJECT
- TEACHER_SUBJECT
- STUDENT_RECORD (expanded student domain fields)
- PARENT_STUDENT_LINK with relationship metadata
- SCHEDULE
- STUDENT_ATTENDANCE
- TEACHER_ATTENDANCE
- STAFF_ATTENDANCE
- REPORT_CARD
- REPORT_CARD_SUBJECT
- ANNOUNCEMENT
- ANNOUNCEMENT_ATTACHMENT

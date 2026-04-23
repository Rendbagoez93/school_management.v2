# School Management System ERD

Date: April 23, 2026  
Source: Generated from implemented code models after scanning the workspace.

## Scanned Model Sources

- applications/academic_setup/models.py
- applications/user_management/models.py
- applications/school_management/academic_management/models.py
- applications/school_management/grade_management/models.py
- applications/school_management/staff_management/models.py
- modules/user/models.py
- shared/base_models.py
- modules/user/mixins.py

## Entity Relationship Diagram (Mermaid)

```mermaid
erDiagram
    USER {
        uuid id PK
        string email UK
        string first_name
        string last_name
        string phone_number
        date date_of_birth
        string role
        bool is_active
        bool is_staff
        bool is_verified
        datetime email_verified_at
        datetime password_changed_at
        int failed_login_attempts
        datetime account_locked_until
        string preferred_language
        string timezone_preference
        bool email_notifications
        bool marketing_emails
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
        date enrollment_start_date
        date enrollment_end_date
        datetime date_joined
        datetime date_modified
        bool is_deleted
        datetime deleted_at
    }

    GRADE {
        bigint id PK
        string name
        text description
        bigint academic_year_id FK
        string grade
        string grade_type
        string grade_subtype
        bool is_active
        datetime created_at
        datetime updated_at
        datetime date_joined
        datetime date_modified
        bool is_deleted
        datetime deleted_at
    }


    STUDENT_ENROLLMENT {
        bigint id PK
        uuid student_id FK
        bigint grade_id FK
        bigint academic_year_id FK
        datetime joined_at
        datetime date_joined
        datetime date_modified
        bool is_deleted
        datetime deleted_at
    }

    ACADEMIC_YEAR_SETUP {
        bigint id PK
        bigint academic_year_id FK
        string current_step
        bool basic_info_completed
        bool import_grades_completed
        bool import_students_completed
        bool assign_classrooms_completed
        bool review_completed
        string grades_import_method
        string students_import_method
        string classrooms_import_method
        datetime created_at
        datetime updated_at
        datetime date_joined
        datetime date_modified
        bool is_deleted
        datetime deleted_at
    }

    IMPORT_TASK {
        bigint id PK
        bigint academic_year_id FK
        string task_type
        string status
        string file_path
        int total_records
        int processed_records
        int success_count
        int error_count
        json error_details
        datetime completed_at
        datetime created_at
        datetime updated_at
        datetime date_joined
        datetime date_modified
        bool is_deleted
        datetime deleted_at
    }

    PARENT {
        bigint id PK
        uuid user_id FK
        text address
        json attributes
        datetime date_joined
        datetime date_modified
    }

    STUDENT_PROFILE {
        bigint id PK
        uuid user_id FK
        text address
        json attributes
        datetime date_joined
        datetime date_modified
    }

    SCHOOL_STAFF {
        bigint id PK
        uuid user_id FK
        text address
        json attributes
        datetime date_joined
        datetime date_modified
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

    PARENT_CHILDREN {
        bigint id PK
        bigint parent_id FK
        uuid schooluser_id FK
    }

    USER ||--o| PARENT : has_profile
    USER ||--o| STUDENT_PROFILE : has_profile
    USER ||--o| SCHOOL_STAFF : has_profile

    USER ||--o| TEACHER : has_teacher_profile
    USER ||--o| STAFF_MEMBER : has_staff_member_profile

    ACADEMIC_YEAR ||--o| ACADEMIC_YEAR_SETUP : setup_progress
    ACADEMIC_YEAR ||--o{ IMPORT_TASK : import_tasks
    ACADEMIC_YEAR ||--o{ GRADE : grades
    ACADEMIC_YEAR ||--o{ STUDENT_ENROLLMENT : enrollments

    GRADE ||--o{ STUDENT_ENROLLMENT : enrolls
    USER ||--o{ STUDENT_ENROLLMENT : student

    PARENT ||--o{ PARENT_CHILDREN : links
    USER ||--o{ PARENT_CHILDREN : child_user
```

## Module-to-Entity Mapping

| Entity | App Module | Model Class |
|---|---|---|
| USER | `modules.user` | `User` (abstract base: `AbstractUser`) |
| ACADEMIC_YEAR | `applications.school_management.academic_management` | `AcademicYear` |
| STUDENT_ENROLLMENT | `applications.school_management.academic_management` | `StudentEnrollment` |
| GRADE | `applications.school_management.grade_management` | `Grade` |
| ACADEMIC_YEAR_SETUP | `applications.academic_setup` | `AcademicYearSetup` |
| IMPORT_TASK | `applications.academic_setup` | `ImportTask` |
| PARENT | `applications.user_management` | `Parent` |
| STUDENT_PROFILE | `applications.user_management` | `Student` |
| SCHOOL_STAFF | `applications.user_management` | `SchoolStaff` |
| TEACHER | `applications.school_management.staff_management` | `Teacher` |
| STAFF_MEMBER | `applications.school_management.staff_management` | `StaffMember` |
| PARENT_CHILDREN | auto-generated M2M | `Parent.children` through table |

## Relationship Notes

- `SchoolUser` is a proxy model over `User`; it does not create a separate DB table.
- `BaseUserType` is abstract and contributes fields to `Parent`, `Student` (shown as `STUDENT_PROFILE`), and `SchoolStaff`. All three are in `applications.user_management`.
- **Dual-profile pattern for staff/teachers**: A teacher `User` gets a `SchoolStaff` profile (created at user creation via `SchoolUserManager.create_teacher`) and optionally a `Teacher` profile (created separately via the service layer in `staff_management`). The `Teacher` profile holds teaching-specific data (employee_id, department, specialization). Not all staff users will have a `Teacher` profile.
- **Reverse accessor names** (Django `related_name` values): `user.teacher_profile` → Teacher, `user.staff_member_profile` → StaffMember, `user.schoolstaff` → SchoolStaff, `user.student` → Student, `user.parent` → Parent.
- Parent-to-children relation is represented by an implicit Django M2M table (`PARENT_CHILDREN` above). The `children` field is defined on `Parent` and links to `SchoolUser`.
- `Grade.students` is an M2M to `User` through `StudentEnrollment`.
- Soft-delete fields (`is_deleted`, `deleted_at`) are inherited through `BaseSoftDeletableModel` on most domain entities.
- `Grade` has both inherited timestamp fields (`date_joined`, `date_modified` from `TimeStampedModel`) and explicit `created_at` / `updated_at` fields defined directly on the model. This is intentional in the current implementation.

## Important Constraints Captured from Code

- `User.email` is unique (case-insensitive: enforced via `UniqueConstraint(Lower("email"))`).
- `User.role` is indexed but nullable (blank/null allowed); roles are also enforced via Django Groups.
- `AcademicYear.name` is unique.
- `AcademicYear.status` uses a `TextChoices` enum: `SETUP`, `ENROLLMENT`, `ACTIVE`, `COMPLETED`.
- `AcademicYear.deployment_type` uses `TextChoices`: `FRESH_START`, `MID_YEAR`.
- `AcademicYearSetup.academic_year` is one-to-one.
- `Teacher.employee_id` and `StaffMember.employee_id` are unique.
- `StudentEnrollment` unique active constraint: one student per academic year where `is_deleted=False`.
- `Grade` unique tuple: (`name`, `grade`, `academic_year`, `grade_type`, `grade_subtype`).

## Schema Reference Alignment Note

> The `.github/database-schema.md` in this repository was drafted against an earlier design iteration and does not reflect the current implementation. Specifically: it uses integer PKs (actual User PK is UUID), references only 4 roles (actual system has 12 via `RoleEnum`), and models `Grade` and `Student` with different field sets. **This ERD document (generated from the actual model source files) is the authoritative schema reference.**
>
> For the planned future schema (modules not yet implemented), see `SCHOOL_MANAGEMENT_FUTURE_MODULES_ERD.md`.

## Exclusions

- Django auth internals (`auth_group`, permissions M2M) are not expanded in this ERD.
- Abstract base tables (`AbstractUser`, `BaseUserType`, `TimeStampedModel`, `BaseSoftDeletableModel`) are not shown as physical entities.

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

## Relationship Notes

- `SchoolUser` is a proxy model over `User`; it does not create a separate DB table.
- `BaseUserType` is abstract and contributes fields to `Parent`, `Student` (shown as `STUDENT_PROFILE`), and `SchoolStaff`.
- Parent-to-children relation is represented by an implicit Django M2M table (`PARENT_CHILDREN` above).
- `Grade.students` is an M2M to `User` through `StudentEnrollment`.
- Soft-delete fields (`is_deleted`, `deleted_at`) are inherited through `BaseSoftDeletableModel` on most domain entities.

## Important Constraints Captured from Code

- `AcademicYear.name` is unique.
- `AcademicYearSetup.academic_year` is one-to-one.
- `Teacher.employee_id` and `StaffMember.employee_id` are unique.
- `StudentEnrollment` unique active constraint: one student per academic year where not soft-deleted.
- `Grade` unique tuple: (`name`, `grade`, `academic_year`, `grade_type`, `grade_subtype`).

## Exclusions

- Django auth internals (`auth_group`, permissions M2M) are not expanded in this ERD.
- Abstract base tables are not shown as physical entities.

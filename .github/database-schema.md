# Database Schema Reference — School Management System

## Overview

This document outlines the database schema for the School Management System. The application uses **PostgreSQL** as the primary database.

### Schema Principles

- **Single-instance**: No multi-tenancy — one database serves one school
- **Soft deletes**: Critical records use `is_active` or `deleted_at` instead of hard deletion
- **Audit trails**: All models inherit from `TimeStampedModel` (created_at, updated_at)
- **Foreign key constraints**: Enforce referential integrity at database level
- **Indexes**: Strategic indexing on frequently queried fields

---

## Core Models

### 1. AuthUser

**Table:** `core_users_authuser`  
**Description:** Central user model for all system users (Admin, Teacher, Staff, Parent)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Unique user ID |
| `email` | String(255) | Unique, Not Null, Indexed | User email address (login identifier) |
| `password` | String(255) | Not Null | Hashed password (bcrypt/PBKDF2) |
| `phone_number` | String(20) | Nullable | Contact phone number |
| `first_name` | String(100) | Not Null | User's first name |
| `last_name` | String(100) | Not Null | User's last name |
| `role` | String(20) | Not Null, Indexed | User role: `ADMIN`, `TEACHER`, `STAFF`, `PARENT` |
| `is_active` | Boolean | Default: True, Indexed | Account active status |
| `is_staff` | Boolean | Default: False | Django admin access flag |
| `is_superuser` | Boolean | Default: False | Superuser privileges |
| `date_joined` | DateTime | Auto-now (add), Indexed | Account creation timestamp |
| `created_at` | DateTime | Auto-now (add), Indexed | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Indexes:**
- `email` (unique)
- `role`
- `is_active`
- `date_joined`
- `created_at`

**Role Choices:**
```python
class Role(models.TextChoices):
    ADMIN = "ADMIN", "Administrator"
    TEACHER = "TEACHER", "Teacher"
    STAFF = "STAFF", "Staff"
    PARENT = "PARENT", "Parent"
```

---

### 2. School

**Table:** `core_school_school`  
**Description:** School configuration (singleton — only one record per installation)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | School ID (always 1) |
| `name` | String(255) | Not Null | School name |
| `logo` | File/URL | Nullable | School logo image |
| `address` | Text | Nullable | Full address |
| `phone` | String(20) | Nullable | Contact phone |
| `email` | String(255) | Nullable | Contact email |
| `website` | String(255) | Nullable | School website URL |
| `primary_color` | String(7) | Default: `#1976D2` | Primary branding color (hex) |
| `accent_color` | String(7) | Default: `#FFA726` | Accent branding color (hex) |
| `created_at` | DateTime | Auto-now (add) | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Note:** This table should only ever have one row (enforced at application level).

---

### 3. AcademicYear

**Table:** `core_academic_academicyear`  
**Description:** School academic years (e.g., 2025-2026)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Academic year ID |
| `name` | String(100) | Not Null, Unique | Year name (e.g., "2025-2026") |
| `start_date` | Date | Not Null, Indexed | Academic year start date |
| `end_date` | Date | Not Null | Academic year end date |
| `is_current` | Boolean | Default: False, Indexed | Mark as current academic year |
| `created_at` | DateTime | Auto-now (add) | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Unique Constraint:** Only one record can have `is_current=True` at a time.

**Indexes:**
- `start_date`
- `is_current`

---

### 4. Grade (Class)

**Table:** `core_academic_grade`  
**Description:** Student grade/class levels (e.g., Grade 5A, Grade 3B)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Grade ID |
| `academic_year_id` | Integer | FK(AcademicYear), Not Null, Indexed | Associated academic year |
| `name` | String(100) | Not Null | Grade/class name (e.g., "Grade 5A") |
| `level` | Integer | Not Null, Indexed | Grade level number (1-12) |
| `section` | String(10) | Nullable | Class section (A, B, C, etc.) |
| `class_teacher_id` | Integer | FK(AuthUser), Nullable | Assigned class teacher |
| `capacity` | Integer | Default: 40 | Maximum students |
| `is_active` | Boolean | Default: True, Indexed | Active status |
| `created_at` | DateTime | Auto-now (add) | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Foreign Keys:**
- `academic_year_id` → `AcademicYear.id` (ON DELETE CASCADE)
- `class_teacher_id` → `AuthUser.id` (ON DELETE SET NULL, role must be TEACHER)

**Indexes:**
- `academic_year_id`
- `level`
- `is_active`

---

### 5. Subject

**Table:** `core_academic_subject`  
**Description:** Curriculum subjects (e.g., Mathematics, English, Science)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Subject ID |
| `name` | String(100) | Not Null | Subject name |
| `code` | String(20) | Unique, Not Null | Subject code (e.g., MATH5, ENG5) |
| `grade_level` | Integer | Nullable, Indexed | Applicable grade level (null = all levels) |
| `description` | Text | Nullable | Subject description |
| `is_active` | Boolean | Default: True, Indexed | Active status |
| `created_at` | DateTime | Auto-now (add) | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Indexes:**
- `code` (unique)
- `grade_level`
- `is_active`

---

### 6. Student

**Table:** `core_students_student`  
**Description:** Enrolled students

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Student ID |
| `roll_number` | String(50) | Unique, Not Null, Indexed | Student roll/registration number |
| `first_name` | String(100) | Not Null | First name |
| `last_name` | String(100) | Not Null | Last name |
| `date_of_birth` | Date | Not Null | Date of birth |
| `admission_date` | Date | Not Null, Indexed | Admission date |
| `current_grade_id` | Integer | FK(Grade), Not Null, Indexed | Current grade/class |
| `photo` | File/URL | Nullable | Student photo |
| `blood_group` | String(5) | Nullable | Blood group (A+, B+, etc.) |
| `address` | Text | Nullable | Residential address |
| `emergency_contact` | String(20) | Nullable | Emergency contact number |
| `is_active` | Boolean | Default: True, Indexed | Active enrollment status |
| `created_at` | DateTime | Auto-now (add), Indexed | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Foreign Keys:**
- `current_grade_id` → `Grade.id` (ON DELETE PROTECT)

**Indexes:**
- `roll_number` (unique)
- `current_grade_id`
- `admission_date`
- `is_active`
- `created_at`

---

### 7. Teacher

**Table:** `core_teachers_teacher`  
**Description:** Teaching staff (linked to AuthUser with role=TEACHER)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Teacher ID |
| `user_id` | Integer | FK(AuthUser), Unique, Not Null | Linked user account |
| `employee_id` | String(50) | Unique, Not Null | Employee/staff ID |
| `department` | String(100) | Nullable | Department (e.g., Science, Mathematics) |
| `specialization` | String(255) | Nullable | Teaching specialization |
| `date_of_joining` | Date | Not Null, Indexed | Date joined school |
| `is_active` | Boolean | Default: True, Indexed | Active employment status |
| `created_at` | DateTime | Auto-now (add) | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Foreign Keys:**
- `user_id` → `AuthUser.id` (ON DELETE CASCADE, role must be TEACHER)

**Indexes:**
- `user_id` (unique)
- `employee_id` (unique)
- `date_of_joining`
- `is_active`

---

### 8. TeacherSubject (Many-to-Many)

**Table:** `core_teachers_teachersubject`  
**Description:** Association between teachers and subjects they teach

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Record ID |
| `teacher_id` | Integer | FK(Teacher), Not Null, Indexed | Teacher |
| `subject_id` | Integer | FK(Subject), Not Null, Indexed | Subject |
| `grade_id` | Integer | FK(Grade), Nullable, Indexed | Specific grade (null = all grades) |

**Foreign Keys:**
- `teacher_id` → `Teacher.id` (ON DELETE CASCADE)
- `subject_id` → `Subject.id` (ON DELETE CASCADE)
- `grade_id` → `Grade.id` (ON DELETE CASCADE)

**Unique Constraint:** (`teacher_id`, `subject_id`, `grade_id`)

---

### 9. Staff

**Table:** `core_staff_staff`  
**Description:** Non-teaching staff (linked to AuthUser with role=STAFF)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Staff ID |
| `user_id` | Integer | FK(AuthUser), Unique, Not Null | Linked user account |
| `employee_id` | String(50) | Unique, Not Null | Employee/staff ID |
| `department` | String(100) | Nullable | Department (e.g., Admin, Security, Maintenance) |
| `job_title` | String(100) | Nullable | Job title/position |
| `date_of_joining` | Date | Not Null, Indexed | Date joined school |
| `is_active` | Boolean | Default: True, Indexed | Active employment status |
| `created_at` | DateTime | Auto-now (add) | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Foreign Keys:**
- `user_id` → `AuthUser.id` (ON DELETE CASCADE, role must be STAFF)

**Indexes:**
- `user_id` (unique)
- `employee_id` (unique)
- `date_of_joining`
- `is_active`

---

### 10. ParentStudent (Many-to-Many)

**Table:** `core_parents_parentstudent`  
**Description:** Association between parents and their children

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Record ID |
| `parent_id` | Integer | FK(AuthUser), Not Null, Indexed | Parent user |
| `student_id` | Integer | FK(Student), Not Null, Indexed | Child student |
| `relationship` | String(50) | Nullable | Relationship type (Father, Mother, Guardian) |
| `is_primary_contact` | Boolean | Default: False | Mark as primary contact |
| `created_at` | DateTime | Auto-now (add) | Record creation timestamp |

**Foreign Keys:**
- `parent_id` → `AuthUser.id` (ON DELETE CASCADE, role must be PARENT)
- `student_id` → `Student.id` (ON DELETE CASCADE)

**Unique Constraint:** (`parent_id`, `student_id`)

**Indexes:**
- `parent_id`
- `student_id`

---

### 11. Schedule (Timetable)

**Table:** `core_schedule_schedule`  
**Description:** Weekly class schedule/timetable

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Schedule ID |
| `grade_id` | Integer | FK(Grade), Not Null, Indexed | Grade/class |
| `subject_id` | Integer | FK(Subject), Not Null, Indexed | Subject |
| `teacher_id` | Integer | FK(Teacher), Not Null, Indexed | Teacher |
| `day_of_week` | Integer | Not Null, Indexed | Day (0=Monday, 6=Sunday) |
| `period` | Integer | Not Null | Period number (1-8) |
| `start_time` | Time | Not Null | Period start time |
| `end_time` | Time | Not Null | Period end time |
| `room` | String(50) | Nullable | Room/location |
| `is_active` | Boolean | Default: True | Active status |
| `created_at` | DateTime | Auto-now (add) | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Foreign Keys:**
- `grade_id` → `Grade.id` (ON DELETE CASCADE)
- `subject_id` → `Subject.id` (ON DELETE PROTECT)
- `teacher_id` → `Teacher.id` (ON DELETE PROTECT)

**Unique Constraint:** (`grade_id`, `day_of_week`, `period`)

**Indexes:**
- `grade_id`
- `subject_id`
- `teacher_id`
- `day_of_week`

**Day of Week Values:**
- 0 = Monday
- 1 = Tuesday
- 2 = Wednesday
- 3 = Thursday
- 4 = Friday
- 5 = Saturday (if applicable)
- 6 = Sunday (if applicable)

---

### 12. StudentAttendance

**Table:** `core_attendance_studentattendance`  
**Description:** Daily student attendance records

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Attendance ID |
| `student_id` | Integer | FK(Student), Not Null, Indexed | Student |
| `date` | Date | Not Null, Indexed | Attendance date |
| `status` | String(20) | Not Null, Indexed | Status: `present`, `absent`, `late`, `excused` |
| `remarks` | Text | Nullable | Additional notes (e.g., reason for absence) |
| `marked_by_id` | Integer | FK(AuthUser), Nullable | User who marked attendance |
| `marked_at` | DateTime | Auto-now (add) | Timestamp when marked |
| `created_at` | DateTime | Auto-now (add) | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Foreign Keys:**
- `student_id` → `Student.id` (ON DELETE CASCADE)
- `marked_by_id` → `AuthUser.id` (ON DELETE SET NULL)

**Unique Constraint:** (`student_id`, `date`)

**Indexes:**
- `student_id`
- `date`
- `status`
- Composite: (`student_id`, `date`)

**Status Choices:**
```python
class AttendanceStatus(models.TextChoices):
    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"
    LATE = "late", "Late"
    EXCUSED = "excused", "Excused"
```

---

### 13. TeacherAttendance

**Table:** `core_attendance_teacherattendance`  
**Description:** Daily teacher attendance records

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Attendance ID |
| `teacher_id` | Integer | FK(Teacher), Not Null, Indexed | Teacher |
| `date` | Date | Not Null, Indexed | Attendance date |
| `status` | String(20) | Not Null | Status: `present`, `absent`, `late`, `leave` |
| `remarks` | Text | Nullable | Additional notes |
| `marked_by_id` | Integer | FK(AuthUser), Nullable | User who marked attendance |
| `marked_at` | DateTime | Auto-now (add) | Timestamp when marked |
| `created_at` | DateTime | Auto-now (add) | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Foreign Keys:**
- `teacher_id` → `Teacher.id` (ON DELETE CASCADE)
- `marked_by_id` → `AuthUser.id` (ON DELETE SET NULL)

**Unique Constraint:** (`teacher_id`, `date`)

**Indexes:**
- `teacher_id`
- `date`
- Composite: (`teacher_id`, `date`)

---

### 14. StaffAttendance

**Table:** `core_attendance_staffattendance`  
**Description:** Daily staff attendance records

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Attendance ID |
| `staff_id` | Integer | FK(Staff), Not Null, Indexed | Staff member |
| `date` | Date | Not Null, Indexed | Attendance date |
| `status` | String(20) | Not Null | Status: `present`, `absent`, `late`, `leave` |
| `remarks` | Text | Nullable | Additional notes |
| `marked_by_id` | Integer | FK(AuthUser), Nullable | User who marked attendance |
| `marked_at` | DateTime | Auto-now (add) | Timestamp when marked |
| `created_at` | DateTime | Auto-now (add) | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Foreign Keys:**
- `staff_id` → `Staff.id` (ON DELETE CASCADE)
- `marked_by_id` → `AuthUser.id` (ON DELETE SET NULL)

**Unique Constraint:** (`staff_id`, `date`)

**Indexes:**
- `staff_id`
- `date`
- Composite: (`staff_id`, `date`)

---

### 15. ReportCard

**Table:** `core_reports_reportcard`  
**Description:** Student report cards (per term/semester)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Report card ID |
| `student_id` | Integer | FK(Student), Not Null, Indexed | Student |
| `academic_year_id` | Integer | FK(AcademicYear), Not Null, Indexed | Academic year |
| `term` | String(50) | Not Null | Term/semester (Q1, Q2, Final) |
| `issued_date` | Date | Not Null, Indexed | Report issuance date |
| `overall_grade` | String(5) | Nullable | Overall grade (A+, A, B+, etc.) |
| `overall_percentage` | Decimal(5,2) | Nullable | Overall percentage score |
| `rank` | Integer | Nullable | Student rank in class |
| `total_students` | Integer | Nullable | Total students in class |
| `class_teacher_remarks` | Text | Nullable | Class teacher's remarks |
| `principal_remarks` | Text | Nullable | Principal's remarks |
| `created_at` | DateTime | Auto-now (add) | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Foreign Keys:**
- `student_id` → `Student.id` (ON DELETE CASCADE)
- `academic_year_id` → `AcademicYear.id` (ON DELETE PROTECT)

**Unique Constraint:** (`student_id`, `academic_year_id`, `term`)

**Indexes:**
- `student_id`
- `academic_year_id`
- `issued_date`
- Composite: (`student_id`, `academic_year_id`, `term`)

---

### 16. ReportCardSubject

**Table:** `core_reports_reportcardsubject`  
**Description:** Subject-wise grades in a report card

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Record ID |
| `report_card_id` | Integer | FK(ReportCard), Not Null, Indexed | Report card |
| `subject_id` | Integer | FK(Subject), Not Null, Indexed | Subject |
| `grade` | String(5) | Not Null | Grade (A+, A, B+, etc.) |
| `score` | Decimal(5,2) | Not Null | Score obtained |
| `max_score` | Decimal(5,2) | Not Null | Maximum score |
| `remarks` | Text | Nullable | Teacher's remarks for this subject |
| `created_at` | DateTime | Auto-now (add) | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Foreign Keys:**
- `report_card_id` → `ReportCard.id` (ON DELETE CASCADE)
- `subject_id` → `Subject.id` (ON DELETE PROTECT)

**Unique Constraint:** (`report_card_id`, `subject_id`)

**Indexes:**
- `report_card_id`
- `subject_id`

---

### 17. Announcement

**Table:** `core_announcements_announcement`  
**Description:** School-wide or targeted announcements

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Announcement ID |
| `title` | String(255) | Not Null | Announcement title |
| `content` | Text | Not Null | Full announcement content |
| `target_audience` | String(50) | Not Null, Indexed | Target: `ALL`, `GRADE_5A`, etc. |
| `priority` | String(20) | Not Null, Indexed | Priority: `HIGH`, `NORMAL`, `LOW` |
| `date_posted` | DateTime | Auto-now (add), Indexed | Posted timestamp |
| `posted_by_id` | Integer | FK(AuthUser), Not Null | User who posted |
| `is_active` | Boolean | Default: True, Indexed | Active status |
| `created_at` | DateTime | Auto-now (add) | Record creation timestamp |
| `updated_at` | DateTime | Auto-now (update) | Last update timestamp |

**Foreign Keys:**
- `posted_by_id` → `AuthUser.id` (ON DELETE SET NULL)

**Indexes:**
- `target_audience`
- `priority`
- `date_posted`
- `is_active`

**Priority Choices:**
```python
class Priority(models.TextChoices):
    HIGH = "HIGH", "High"
    NORMAL = "NORMAL", "Normal"
    LOW = "LOW", "Low"
```

---

### 18. AnnouncementAttachment

**Table:** `core_announcements_announcementattachment`  
**Description:** File attachments for announcements

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PK, Auto-increment | Attachment ID |
| `announcement_id` | Integer | FK(Announcement), Not Null, Indexed | Announcement |
| `file_name` | String(255) | Not Null | Original file name |
| `file` | File/URL | Not Null | File path/URL |
| `file_size` | Integer | Nullable | File size in bytes |
| `created_at` | DateTime | Auto-now (add) | Upload timestamp |

**Foreign Keys:**
- `announcement_id` → `Announcement.id` (ON DELETE CASCADE)

**Indexes:**
- `announcement_id`

---

## Relationships Diagram

```
School (1:1 singleton)

AcademicYear (1) ──< (N) Grade
                         ├── (1) class_teacher → Teacher
                         └── (N) students → Student

Subject (N) ──< (N) TeacherSubject >── (N) Teacher

Student (N) ──< (N) ParentStudent >── (N) Parent (AuthUser role=PARENT)
Student (1) ──< (N) StudentAttendance
Student (1) ──< (N) ReportCard
              └── (1:N) ReportCardSubject → Subject

Teacher (linked to AuthUser role=TEACHER)
Teacher (1) ──< (N) TeacherAttendance
Teacher (N) ──< (N) Schedule

Staff (linked to AuthUser role=STAFF)
Staff (1) ──< (N) StaffAttendance

Schedule:
  - Grade (N:1)
  - Subject (N:1)
  - Teacher (N:1)

Announcement (1) ──< (N) AnnouncementAttachment
```

---

## Migrations Strategy

1. **Initial migration**: Create all tables with base schema
2. **Data migrations**: Seed initial data (School config, default academic year, subjects)
3. **Index migrations**: Add performance indexes after initial data load
4. **Constraint migrations**: Add unique constraints and foreign key constraints

---

## Performance Considerations

### Recommended Indexes

Beyond the indexes listed above, consider these composite indexes for performance:

- **StudentAttendance**: (`student_id`, `date`, `status`)
- **ReportCard**: (`student_id`, `academic_year_id`, `term`)
- **Schedule**: (`grade_id`, `day_of_week`, `period`)
- **ParentStudent**: (`parent_id`, `student_id`)

### Query Optimization

- Use `select_related()` for ForeignKey lookups
- Use `prefetch_related()` for reverse ForeignKey and ManyToMany
- Use `.only()` or `.values()` to fetch specific fields
- Implement pagination for large result sets

---

## Backup Strategy

- **Daily full backup**: Complete database dump at midnight
- **Incremental backups**: Every 6 hours
- **Retention**: Keep daily backups for 30 days, weekly for 1 year
- **Test restores**: Monthly disaster recovery drills

---

**Last Updated**: April 21, 2026

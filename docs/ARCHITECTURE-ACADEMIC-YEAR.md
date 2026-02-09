# Academic Year Management Architecture

This document describes the clean separation of concerns in the academic year management system.

## Overview

The system is built around **three core models** that each own specific responsibilities, coordinated by **one orchestrator service** that acts as the brain of the pipeline.

## The Three Core Models

### 1. AcademicYear (Owner of Lifecycle)

**Location**: `applications/school_management/academic_management/models.py`

**Responsibilities**:
- Lifecycle status (SETUP, ENROLLMENT, ACTIVE, COMPLETED)
- Deployment type (FRESH_START, MID_YEAR)
- Date boundaries (start_date, end_date, enrollment dates)
- Active/inactive flag

**What it MUST NOT do**:
- ❌ Know about setup steps
- ❌ Know how grades are imported
- ❌ Know how students are assigned
- ❌ Manage its own status transitions (removed save() logic)
- ❌ Call services or orchestrators

**Key Methods**:
- `is_in_setup` - Check if in setup phase
- `is_in_enrollment` - Check if in enrollment phase
- `is_active_year` - Check if year is active

### 2. AcademicYearSetup (Owner of Readiness)

**Location**: `applications/academic_setup/models.py`

**Responsibilities**:
- Setup progress tracking (which steps are completed)
- Import method tracking (how data was imported)
- Current step indicator

**Answers ONE question**: *"Is this academic year ready to activate?"*

**What it MUST NOT do**:
- ❌ Change AcademicYear status directly
- ❌ Create grades directly
- ❌ Enroll students directly
- ❌ Call services or orchestrators (removed all service calls)
- ❌ Calculate completion percentage (orchestrator's job)
- ❌ Know required steps based on deployment type (orchestrator's job)

**Key Fields**:
- `basic_info_completed`
- `import_grades_completed`
- `import_students_completed`
- `assign_classrooms_completed`
- `review_completed`
- `grades_import_method`, `students_import_method`, `classrooms_import_method`

### 3. Grade (Owner of Class Structure)

**Location**: `applications/school_management/grade_management/models.py`

**Responsibilities**:
- Class identity (name, grade level, type, subtype)
- Reference to academic year
- Active/inactive status

**What it MUST NOT do**:
- ❌ Care about setup steps
- ❌ Care about imports
- ❌ Care about lifecycle transitions
- ❌ Add/remove students directly (removed methods)
- ❌ Know about enrollment rules

**Key Fields**:
- `name`, `grade`, `grade_type`, `grade_subtype`
- `academic_year` (FK)
- Student relationship via `StudentEnrollment` through model

---

## The ONE Orchestrator (The Pipeline Brain)

### AcademicYearOrchestrator

**Location**: `applications/academic_setup/orchestrator.py`

This is the **ONLY** place where AcademicYear, AcademicYearSetup, and Grade are allowed to talk to each other.

### Orchestrator Sections

The orchestrator is organized into 6 logical sections:

#### **Section 1: Academic Year Lifecycle Management**
- `create_academic_year()` - Create new year + setup tracker
- `transition_to_enrollment()` - SETUP → ENROLLMENT
- `transition_to_active()` - SETUP/ENROLLMENT → ACTIVE
- `transition_to_completed()` - Any → COMPLETED

#### **Section 2: Setup Progress Management**
- `get_required_steps()` - Determine steps based on deployment type
- `get_completion_percentage()` - Calculate setup progress
- `is_setup_complete()` - Check if ready to activate
- `mark_step_complete()` - Mark a step as done

#### **Section 3: Grade Management**
- `create_grade()` - Create a single grade
- `bulk_create_grades()` - Create multiple grades from import

#### **Section 4: Student Enrollment Management**
- `enroll_student()` - Enroll one student in a grade
- `unenroll_student()` - Remove student from grade
- `transfer_student()` - Move student between grades
- `bulk_enroll_students()` - Enroll multiple students

#### **Section 5: Import Task Management**
- `create_import_task()` - Start tracking an import
- `start_import_task()` - Mark as in progress
- `update_import_progress()` - Update progress
- `complete_import_task()` - Mark as successful
- `fail_import_task()` - Mark as failed

#### **Section 6: Query Helpers**
- `get_active_academic_year()` - Get current active year
- `get_grades_for_academic_year()` - Get all grades for a year
- `get_student_enrollment()` - Get student's enrollment
- `get_students_in_grade()` - Get all students in a grade

---

## Usage Examples

### Creating a New Academic Year

```python
from applications.academic_setup.orchestrator import AcademicYearOrchestrator
from datetime import date

# Create a fresh start academic year
academic_year = AcademicYearOrchestrator.create_academic_year(
    name="2024-2025",
    start_date=date(2024, 9, 1),
    end_date=date(2025, 6, 30),
    deployment_type="FRESH_START",
    enrollment_start_date=date(2024, 7, 1),
    enrollment_end_date=date(2024, 8, 15),
)

# Automatically creates AcademicYearSetup linked to this year
```

### Progressing Through Setup

```python
# Mark basic info as complete
AcademicYearOrchestrator.mark_step_complete(
    academic_year=academic_year,
    step=AcademicYearSetup.SetupSteps.BASIC_INFO,
)

# Import grades from CSV
grades_data = [
    {'name': 'Grade 1A', 'grade': '1', 'grade_type': 'Primary'},
    {'name': 'Grade 1B', 'grade': '1', 'grade_type': 'Primary'},
    {'name': 'Grade 2A', 'grade': '2', 'grade_type': 'Primary'},
]

grades = AcademicYearOrchestrator.bulk_create_grades(
    academic_year=academic_year,
    grades_data=grades_data,
)

# Mark grades import as complete
AcademicYearOrchestrator.mark_step_complete(
    academic_year=academic_year,
    step=AcademicYearSetup.SetupSteps.IMPORT_GRADES,
    import_method=AcademicYearSetup.ImportMethod.CSV,
)
```

### Checking Setup Progress

```python
# Get completion percentage
progress = AcademicYearOrchestrator.get_completion_percentage(academic_year)
print(f"Setup is {progress}% complete")

# Check if setup is complete
if AcademicYearOrchestrator.is_setup_complete(academic_year):
    print("Ready to transition!")
```

### Transitioning Lifecycle

```python
# For fresh start: SETUP → ENROLLMENT
if academic_year.deployment_type == "FRESH_START":
    AcademicYearOrchestrator.transition_to_enrollment(academic_year)
    # Now accept enrollments...
    AcademicYearOrchestrator.transition_to_active(academic_year)

# For mid-year: SETUP → ACTIVE (skip enrollment)
else:
    AcademicYearOrchestrator.transition_to_active(academic_year)
```

### Enrolling Students

```python
from modules.user.models import User

# Get a grade
grade_1a = Grade.objects.get(name="Grade 1A", academic_year=academic_year)

# Get students
student1 = User.objects.get(email="student1@school.com")
student2 = User.objects.get(email="student2@school.com")

# Enroll one student
enrollment = AcademicYearOrchestrator.enroll_student(
    grade=grade_1a,
    student=student1,
)

# Bulk enroll
students = [student1, student2]
enrollments = AcademicYearOrchestrator.bulk_enroll_students(
    grade=grade_1a,
    students=students,
)
```

### Tracking Imports

```python
# Create import task
import_task = AcademicYearOrchestrator.create_import_task(
    academic_year=academic_year,
    task_type=ImportTask.TaskType.STUDENTS,
    total_records=500,
    file_path="/uploads/students.csv",
)

# Start the import
AcademicYearOrchestrator.start_import_task(import_task)

# Update progress as you process records
AcademicYearOrchestrator.update_import_progress(
    import_task=import_task,
    processed=250,
    success=240,
    errors=10,
    error_details={'row_15': 'Invalid email', 'row_42': 'Missing name'},
)

# Complete the import
AcademicYearOrchestrator.complete_import_task(import_task)
```

---

## Design Principles

### ✅ DO

- **Use the orchestrator** for all cross-model operations
- **Keep models simple** - just data and validation
- **Call orchestrator methods** from views/APIs
- **Add new orchestration logic** to the orchestrator, not models

### ❌ DON'T

- **Don't call model.save()** to change status - use orchestrator transitions
- **Don't add business logic** to model save() methods
- **Don't create direct relationships** between models without going through orchestrator
- **Don't scatter coordination logic** across multiple services

---

## Migration Path

If you have existing code that uses the old patterns:

### Old Pattern (❌ Don't use)
```python
# Model doing its own transitions
academic_year.setup_completed = True
academic_year.save()  # This used to auto-change status

# Model calling services
setup.mark_step_complete(step)

# Direct student enrollment
grade.add_student(student)
```

### New Pattern (✅ Use this)
```python
# Orchestrator manages transitions
AcademicYearOrchestrator.transition_to_enrollment(academic_year)

# Orchestrator marks steps
AcademicYearOrchestrator.mark_step_complete(academic_year, step)

# Orchestrator manages enrollment
AcademicYearOrchestrator.enroll_student(grade, student)
```

---

## Benefits of This Architecture

1. **Clear Ownership** - Each model has a single, clear responsibility
2. **Single Source of Truth** - All coordination logic in one place
3. **Easy to Test** - Each component can be tested independently
4. **Easy to Understand** - No hidden side effects in model.save()
5. **Easy to Extend** - Add new orchestration logic without touching models
6. **Type Safety** - Orchestrator provides clear interfaces
7. **Transaction Safety** - All orchestrator methods use @transaction.atomic

---

## Questions & Answers

**Q: Should I create more orchestrators?**
A: No. One orchestrator per domain. This is the academic year domain.

**Q: Can models talk to each other directly?**
A: Only for foreign key relationships. For operations, go through the orchestrator.

**Q: Can I add methods to models?**
A: Yes, but only for:
  - Data validation (`clean()`)
  - Simple property getters (no side effects)
  - String representation (`__str__`)

**Q: Where do I put import logic?**
A: Create separate services for import (CSV parsing, validation), but use the orchestrator for actually creating grades/enrollments.

**Q: Can the orchestrator call other services?**
A: Yes! The orchestrator can use helper services for specific tasks, but it remains the coordinator.

---

## Summary

- **AcademicYear** = Lifecycle owner (status, dates, type)
- **AcademicYearSetup** = Readiness tracker (progress, imports)
- **Grade** = Class structure (identity, students)
- **AcademicYearOrchestrator** = The brain (coordination, transitions, operations)

All working together, each doing one job well. 🎯

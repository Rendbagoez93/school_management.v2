---
name: design-patterns
description: Guide software architecture decisions by recommending appropriate design patterns for School Management System development. Use when the user mentions any of the following: design patterns, refactoring, architecture planning, selecting patterns for a project, "what pattern should I use", implementing a specific pattern (Factory, Singleton, Observer, Strategy, etc.), code structure decisions, or when designing class/object relationships. Also triggered by creational patterns, structural patterns, behavioral patterns, or GoF patterns.
---

# Design Patterns — School Management System

Help users select and implement the right design pattern for building scalable, maintainable educational software.

## Quick Decision Guide

### When User Needs to CHOOSE a Pattern

Ask these questions to narrow down:
1. **What problem are you solving?** (object creation, object composition, communication between objects, behavior variation)
2. **At what level?** (class-level or object-level)
3. **What constraints?** (flexibility, performance, simplicity)

### When User Names a Specific Pattern

Jump to implementation guidance. See references for detailed patterns:
- [Creational Patterns](references/creational.md) — Object creation mechanisms
- [Structural Patterns](references/structural.md) — Object composition and relationships
- [Structural Patterns](references/behavioral.md) — Object collaboration and communication

## Pattern Categories Overview

| Category | Purpose | Common Patterns |
|----------|---------|-----------------|
| **Creational** | Instantiate objects flexibly | Factory, Builder, Singleton, Prototype |
| **Structural** | Compose objects into structures | Adapter, Decorator, Facade, Proxy, Composite |
| **Behavioral** | Manage object communication | Observer, Strategy, Command, State, Iterator |

## Common School Management Scenarios → Pattern Mapping

| Scenario | Recommended Pattern | Why | School Example |
|----------|---------------------|-----|----------------|
| "Create different types of report cards" | Factory Method/Abstract Factory | Encapsulates report creation logic | Generate Term1Report, MidYearReport, FinalReport |
| "Ensure only one School instance exists" | Singleton | Controlled access to school config | School configuration (name, logo, branding) |
| "Build complex report cards with many fields" | Builder | Step-by-step construction | ReportCard with grades, remarks, attendance, etc. |
| "Add permissions to user roles dynamically" | Decorator | Extend AuthUser capabilities | Add grade-specific or subject-specific permissions |
| "Simplify attendance subsystem interface" | Facade | Unified API for complex operations | AttendanceService wraps StudentAttendance, TeacherAttendance, StaffAttendance |
| "Notify parents when grades are published" | Observer | Real-time notifications | ParentNotifier observes ReportCard.created event |
| "Switch between grading systems (A-F vs percentage)" | Strategy | Interchangeable grading algorithms | GradingStrategy with LetterGradeStrategy, PercentageStrategy |
| "Student status changes (enrolled→active→graduated)" | State | State-specific behavior | StudentState with EnrolledState, ActiveState, GraduatedState |
| "Handle attendance approval chain (teacher→principal)" | Chain of Responsibility | Multi-level approval workflow | AttendanceApprovalChain |
| "Undo/redo grade modifications" | Command | Encapsulate grade update operations | UpdateGradeCommand with execute() and undo() |

## Anti-Patterns to Avoid in School Management Systems

- **Singleton abuse** — Don't make every manager/service a Singleton; makes testing difficult
- **Factory overuse** — Simple Student/Teacher creation doesn't need complex factories
- **Observer spam** — Too many notifications overwhelm parents; batch updates strategically
- **Pattern obsession** — Don't force patterns where Django's built-in tools suffice
- **Premature abstraction** — Start with Django models/views, refactor to patterns when complexity grows

## Usage Patterns for School Management

**User says:** "I need different types of attendance records (student, teacher, staff)"
→ **Factory Method** — Create `AttendanceFactory` with subtypes for each role

**User says:** "Parents need real-time notifications when grades are posted"
→ **Observer pattern** — `GradePublisher` notifies `ParentObserver` via push notifications

**User says:** "I want to switch between percentage and letter grade systems"
→ **Strategy pattern** — `GradingStrategy` with `PercentageGrading` and `LetterGrading` implementations

**User says:** "How do I simplify my complex report card generation?"
→ **Facade pattern** — `ReportCardFacade` coordinates attendance, grades, remarks, etc.

**User says:** "I need to track student state transitions (enrolled→active→alumni)"
→ **State pattern** — `StudentState` with state-specific validation and transitions

**User says:** "Multiple approval levels for leave requests"
→ **Chain of Responsibility** — `LeaveApprovalChain` (ClassTeacher → Principal → Admin)

## Recommended Patterns for School Management System

### Backend (Django)

| Module | Recommended Pattern | Implementation |
|--------|---------------------|----------------|
| **School Config** | Singleton | `School` model with single instance |
| **Report Generation** | Factory + Builder | `ReportCardFactory`, `ReportCardBuilder` |
| **Attendance Services** | Facade | `AttendanceService` wraps student/teacher/staff attendance |
| **Grading System** | Strategy | Pluggable grading algorithms (percentage, letter, GPA) |
| **Notification System** | Observer | Push notifications when grades/announcements posted |
| **Permission System** | Decorator | Extend Django's permissions with role-based decorators |
| **API Response** | Template Method | Standard API wrapper (already implemented) |

### Mobile (Android/Kotlin)

| Module | Recommended Pattern | Implementation |
|--------|---------------------|----------------|
| **API Client** | Singleton + Facade | `ApiService` (Retrofit instance) |
| **Data Repository** | Repository Pattern | Clean Architecture data layer |
| **UI State Management** | State Pattern | Compose state hoisting |
| **Navigation** | Strategy | Navigation graph with deep linking |
| **Network/Cache** | Proxy Pattern | Repository decides network vs cache |
| **Notifications** | Observer | FCM integration with local observers |

## Implementation Reference

For detailed pattern information including:
- Intent and applicability
- Multi-language code examples (Python, Kotlin, TypeScript, Rust, Java)
- Common pitfalls

See:
- [Pattern Quick Reference](references/pattern-reference.md) — One-page lookup table
- [AI Pseudocode Format](references/ai-pseudocode.md) — Compact, language-agnostic syntax optimized for AI
- [Creational Patterns](references/creational.md) — Object creation patterns
- [Structural Patterns](references/structural.md) — Object composition patterns
- [Behavioral Patterns](references/behavioral.md) — Object communication patterns

## Code Examples Available In

All patterns include examples in:
- 🐍 **Python** — Django backend (primary)
- 🟣 **Kotlin** — Android mobile app (primary)
- 🟦 **TypeScript** — Modern JS with types
- 🦀 **Rust** — Systems programming
- ☕ **Java** — Enterprise reference
- 📝 **AI Pseudocode** — Language-agnostic, token-efficient

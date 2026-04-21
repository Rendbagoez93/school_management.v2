# Android UI/UX Development Plan — School Parent Portal

## Status Overview

| Layer | Status |
|-------|--------|
| Design system & theming | Planned (professional education theme) |
| Core UI components (`Sms*`) | To be implemented |
| Auth screens | To be implemented |
| Parent dashboard shell + navigation | To be implemented |
| Clean Architecture scaffolding | To be implemented |
| Real API integration | To be implemented |

---

## Design Principles (Non-Negotiable)

- **Professional, trustworthy, modern** — blue-orange education palette, clean geometry.
- **Material 3 all the way** — use `MaterialTheme.colorScheme`, `Typography`, elevation surfaces.
- **School branding is runtime** — colors and logo loaded from backend configuration.
- **`Sms` prefix mandatory** — every reusable visual pattern lives in `presentation/components/` as a `Sms*` Composable.
- **English UI copy** — all labels, hints, button text (configurable per school region if needed).
- **No inline styling** — no hardcoded hex values, no ad-hoc `Color(0xFF...)` in screens. Use design tokens from `presentation/theme/Color.kt` or `MaterialTheme.colorScheme`.
- **Stateless composables** — all composables receive state and callbacks as parameters; ViewModel drives state.

---

## Design System

### Token Map (`presentation/theme/`)

| File | Contents |
|------|----------|
| `Color.kt` | Professional education color palette (Blue, Orange, Success Green, Error Red) |
| `Type.kt` | `Typography` scale (Material 3 defaults with custom font if needed) |
| `Shapes.kt` | `Shapes` (corner radii — Material 3 defaults) |
| `Theme.kt` | `SchoolPortalTheme` — applies school branding or default theme |
| `Branding.kt` | `SchoolBranding` data class + `LocalSchoolBranding` CompositionLocal |

### Color Palette (Professional Education Theme)

```kotlin
// presentation/theme/Color.kt

// Primary (Professional Blue)
val PrimaryBlue = Color(0xFF1976D2)
val PrimaryBlueDark = Color(0xFF0D47A1)
val PrimaryBlueLight = Color(0xFFBBDEFB)
val PrimaryBlue50 = Color(0xFFE3F2FD)

// Accent (Academic Orange/Gold)
val AccentOrange = Color(0xFFFFA726)
val AccentOrangeDark = Color(0xFFF57C00)
val AccentOrangeLight = Color(0xFFFFE0B2)

// Semantic Colors
val SuccessGreen = Color(0xFF43A047)
val WarningYellow = Color(0xFFFBC02D)
val ErrorRed = Color(0xFFDC3545)
val InfoCyan = Color(0xFF0DCAF0)

// Neutrals
val NeutralDark = Color(0xFF1E2328)      // Text
val NeutralGray = Color(0xFF6B7280)       // Secondary text
val NeutralLight = Color(0xFFF9FAFB)      // Background
val NeutralBorder = Color(0xFFE5E7EB)     // Borders

// Attendance Status Colors
val AttendancePresent = SuccessGreen
val AttendanceAbsent = ErrorRed
val AttendanceLate = WarningYellow
val AttendanceExcused = InfoCyan

// Grade Colors
val GradeExcellent = Color(0xFF059669)    // A+ / A
val GradeGood = Color(0xFF10B981)         // B+ / B
val GradeAverage = Color(0xFFFBBF24)      // C
val GradePoor = ErrorRed                   // D / F
```

### Typography

```kotlin
// presentation/theme/Type.kt
val Typography = Typography(
    displayLarge = TextStyle(
        fontSize = 57.sp,
        lineHeight = 64.sp,
        fontWeight = FontWeight.Normal
    ),
    headlineLarge = TextStyle(
        fontSize = 32.sp,
        lineHeight = 40.sp,
        fontWeight = FontWeight.Bold
    ),
    headlineMedium = TextStyle(
        fontSize = 28.sp,
        lineHeight = 36.sp,
        fontWeight = FontWeight.Bold
    ),
    titleLarge = TextStyle(
        fontSize = 22.sp,
        lineHeight = 28.sp,
        fontWeight = FontWeight.SemiBold
    ),
    titleMedium = TextStyle(
        fontSize = 16.sp,
        lineHeight = 24.sp,
        fontWeight = FontWeight.Medium,
        letterSpacing = 0.15.sp
    ),
    bodyLarge = TextStyle(
        fontSize = 16.sp,
        lineHeight = 24.sp,
        fontWeight = FontWeight.Normal,
        letterSpacing = 0.5.sp
    ),
    bodyMedium = TextStyle(
        fontSize = 14.sp,
        lineHeight = 20.sp,
        fontWeight = FontWeight.Normal,
        letterSpacing = 0.25.sp
    ),
    labelLarge = TextStyle(
        fontSize = 14.sp,
        lineHeight = 20.sp,
        fontWeight = FontWeight.Medium,
        letterSpacing = 0.1.sp
    )
)
```

### Component Catalog (To Be Built)

All components use `Sms` prefix (School Management System):

| Component | Purpose | Priority |
|-----------|---------|----------|
| `SmsButton` | Primary, outline, text, icon button variants | P0 |
| `SmsCard` | Standard card with header, body, footer slots | P0 |
| `SmsBadge` | Status badges (present, absent, A+, B, etc.) | P0 |
| `SmsTextField` | Form input with label, hint, error state | P0 |
| `SmsSectionHeader` | Section divider with title | P0 |
| `SmsEmptyState` | Empty list placeholder with icon + message | P0 |
| `SmsLoadingIndicator` | Full-screen and inline loading states | P0 |
| `SmsTopBar` | App bar with school logo, title, actions | P0 |
| `SmsErrorBanner` | Inline error message banner | P0 |
| `SmsStudentCard` | Child info card (photo, name, grade, quick stats) | P1 |
| `SmsAttendanceCalendar` | Monthly calendar with attendance status | P1 |
| `SmsReportCardItem` | Report card list item (term, grade, rank) | P1 |
| `SmsScheduleItem` | Timetable period row (time, subject, teacher) | P1 |
| `SmsAnnouncementCard` | Announcement card with title, date, priority badge | P1 |
| `SmsStatCard` | Stat metric card (attendance %, average grade) | P2 |
| `SmsGradeChart` | Subject-wise grade bar chart | P2 |
| `SmsBottomNav` | Bottom navigation bar (if multi-tab needed) | P2 |

---

## Navigation Architecture

### Route Graph

```
Root NavHost
├── splash                     → SplashScreen (auto-advances based on token)
├── login                      → LoginScreen (email + password)
└── main                       → MainScreen (authenticated parent shell)
    ├── main/dashboard         → DashboardScreen (children list)
    ├── main/child/{id}        → ChildDetailScreen (tabs: attendance, reports, schedule)
    ├── main/announcements     → AnnouncementsScreen (school news)
    └── main/profile           → ProfileScreen (parent profile, change password)
```

### Navigation Items

| Route | Label | Icon | Description |
|-------|-------|------|-------------|
| `main/dashboard` | Dashboard | `Home` | Children list + quick stats |
| `main/announcements` | Announcements | `Notifications` | School announcements |
| `main/profile` | Profile | `Person` | Parent info, change password, logout |

**Note**: Child detail screen is accessed by tapping a child card, not via bottom nav.

---

## Screen-by-Screen Plan

---

### Splash Screen

**File**: `presentation/screens/auth/SplashScreen.kt`

**Purpose**: Brand intro + auto-navigate to Login or Dashboard based on stored token.

**UX Flow**:
1. Display school logo (from config or default) + app name.
2. After 1500ms: check stored auth token via `SplashViewModel`.
3. If token valid → navigate to `main/dashboard`.
4. If no token → navigate to `login`.

**UI Elements**:
- Full-screen centered layout
- School logo (96dp, loaded from branding config or default)
- App name: "School Parent Portal" (or school-specific name)
- Subtitle: "Stay connected with your child's education"
- Fade-in animation on logo + text

**State/ViewModel**: `SplashViewModel` — checks `TokenStorage.getToken()` and validates.

---

### Login Screen

**File**: `presentation/screens/auth/LoginScreen.kt`

**Purpose**: Parent login with email and password.

**UX Flow**:
1. User sees school logo/branding at top.
2. Email and password input fields.
3. "Login" button triggers `LoginViewModel.login(email, password)`.
4. Loading state while API call in progress (`SmsLoadingIndicator`).
5. On success → navigate to `main/dashboard`.
6. On error → show `SmsErrorBanner` with error message.
7. "Forgot Password?" link (optional, future feature).

**UI Elements**:
- Top: School logo (from branding or default) + school name
- `SmsCard` with login form:
  - `SmsTextField` for email (email keyboard type, validation)
  - `SmsTextField` for password (password input, show/hide toggle)
  - `SmsButton` primary, full-width ("Login")
- `SmsErrorBanner` for error messages
- Footer: "Forgot Password?" text button (optional)

**Strings needed**:
```xml
<string name="login_title">Parent Login</string>
<string name="email_label">Email Address</string>
<string name="email_hint">parent@example.com</string>
<string name="password_label">Password</string>
<string name="password_hint">Enter your password</string>
<string name="login_button">Login</string>
<string name="forgot_password">Forgot Password?</string>
```

**State**: `LoginViewModel` with `LoginUiState` sealed interface (Idle, Loading, Success, Error).

---

### Dashboard Screen

**File**: `presentation/screens/main/DashboardScreen.kt`

**Purpose**: Parent's home screen showing all their children + quick navigation.

**UX Flow**:
1. Load: fetch parent's children from backend via `DashboardViewModel`.
2. Show greeting: "Welcome, [Parent Name]"
3. Display children as cards (2-column grid or vertical list).
4. Each child card shows: photo, name, grade/class, attendance % (quick stat), latest grade.
5. Tap child card → navigate to `main/child/{id}`.
6. Pull-to-refresh updates children list.

**UI Elements**:
- `SmsTopBar` with school logo + "Dashboard" title + profile icon (navigate to profile)
- Greeting text: "Welcome, John Doe"
- `SmsSectionHeader`: "My Children"
- `LazyVerticalGrid` (2 columns) or `LazyColumn` of `SmsStudentCard`:
  - Child photo (circular, 64dp)
  - Child name + grade/class
  - Attendance badge (90% - green, <75% - red)
  - Latest grade badge (A+, B, etc.)
- `SmsEmptyState` if parent has no children linked
- Pull-to-refresh (SwipeRefresh)

**Child Card (`SmsStudentCard`)**:
```kotlin
@Composable
fun SmsStudentCard(
    student: Student,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    SmsCard(
        onClick = onClick,
        modifier = modifier
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Photo
            AsyncImage(
                model = student.photo ?: R.drawable.default_student_avatar,
                contentDescription = student.fullName,
                modifier = Modifier
                    .size(64.dp)
                    .clip(CircleShape)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(student.fullName, style = MaterialTheme.typography.titleMedium)
                Text(student.gradeClass, style = MaterialTheme.typography.bodyMedium, color = NeutralGray)
                Spacer(modifier = Modifier.height(8.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    SmsBadge(
                        text = "${student.attendancePercentage}%",
                        color = if (student.attendancePercentage >= 90) AttendancePresent else AttendanceAbsent
                    )
                    student.latestGrade?.let {
                        SmsBadge(text = it, color = getGradeColor(it))
                    }
                }
            }
        }
    }
}
```

**Data sources**: REST (`GET /api/parent/children/`)

---

### Child Detail Screen

**File**: `presentation/screens/child/ChildDetailScreen.kt`

**Purpose**: Detailed view of a single child with tabs for Attendance, Reports, Schedule.

**UX Flow**:
1. Top section: Child's photo, name, grade, roll number.
2. Tab row: Attendance | Reports | Schedule.
3. Content area displays selected tab content.
4. Each tab loads data independently via `ChildDetailViewModel`.

**UI Elements**:
- `SmsTopBar` with back button + child name as title
- Child header section:
  - Large photo (128dp, circular)
  - Name (headline typography)
  - Grade/Class + Roll Number (body typography)
- `TabRow` with 3 tabs
- `HorizontalPager` or `AnimatedContent` for tab content

**Tabs**:
1. **Attendance Tab** → `AttendanceTabContent`
2. **Reports Tab** → `ReportsTabContent`
3. **Schedule Tab** → `ScheduleTabContent`

---

### Attendance Tab

**File**: `presentation/screens/child/tabs/AttendanceTabContent.kt`

**Purpose**: Monthly attendance calendar view.

**UX Flow**:
1. Month selector at top (previous/next month navigation).
2. Calendar grid showing attendance status per day.
3. Summary stats: Total days, Present, Absent, Late, Attendance %.
4. Tap day → show details in bottom sheet (status, remarks).

**UI Elements**:
- Month selector: `< April 2026 >`
- `SmsStatCard` row: Total Days | Present | Absent | Attendance %
- `SmsAttendanceCalendar`: 7-column grid (Sun-Sat)
  - Each day cell colored by status (green=present, red=absent, yellow=late, blue=excused, gray=no school)
- Bottom sheet for day details (when tapped)

**Attendance Calendar (`SmsAttendanceCalendar`)**:
```kotlin
@Composable
fun SmsAttendanceCalendar(
    month: YearMonth,
    attendanceRecords: Map<LocalDate, AttendanceStatus>,
    onDayClick: (LocalDate) -> Unit,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        // Day headers (S M T W T F S)
        Row {
            DayOfWeek.values().forEach { day ->
                Text(
                    text = day.getDisplayName(TextStyle.SHORT, Locale.getDefault()),
                    modifier = Modifier.weight(1f),
                    textAlign = TextAlign.Center,
                    style = MaterialTheme.typography.labelMedium
                )
            }
        }
        // Calendar grid
        LazyVerticalGrid(columns = GridCells.Fixed(7)) {
            // ... render each day with color based on attendanceRecords
        }
    }
}
```

**Data sources**: REST (`GET /api/attendance/student/{id}/?month=2026-04`)

---

### Reports Tab

**File**: `presentation/screens/child/tabs/ReportsTabContent.kt`

**Purpose**: List of report cards with download option.

**UX Flow**:
1. List all report cards (by term/semester).
2. Each card shows: Academic Year, Term, Overall Grade, Rank.
3. Tap card → navigate to `ReportDetailScreen` (full subject breakdown).
4. Download PDF button per report.

**UI Elements**:
- `LazyColumn` of `SmsReportCardItem`:
  - Term label (Q1, Q2, Final)
  - Overall grade badge (A+, B, etc.)
  - Rank + total students (e.g., "Rank 3/40")
  - Download icon button
- Tap row → navigate to detail screen
- `SmsEmptyState` if no reports available

**Report Card Item (`SmsReportCardItem`)**:
```kotlin
@Composable
fun SmsReportCardItem(
    reportCard: ReportCardSummary,
    onDownloadClick: () -> Unit,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    SmsCard(
        onClick = onClick,
        modifier = modifier
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text("${reportCard.academicYear} - ${reportCard.term}", style = MaterialTheme.typography.titleMedium)
                Spacer(modifier = Modifier.height(4.dp))
                Text("Overall: ${reportCard.overallGrade}", style = MaterialTheme.typography.bodyLarge)
                Text("Rank: ${reportCard.rank}/${reportCard.totalStudents}", style = MaterialTheme.typography.bodyMedium, color = NeutralGray)
            }
            IconButton(onClick = onDownloadClick) {
                Icon(Icons.Default.Download, contentDescription = "Download PDF")
            }
        }
    }
}
```

**Data sources**: REST (`GET /api/reports/student/{id}/`)

---

### Report Detail Screen

**File**: `presentation/screens/child/ReportDetailScreen.kt`

**Purpose**: Full report card with subject-wise grades and remarks.

**UX Flow**:
1. Top: Student name, Academic Year, Term.
2. Subject list with grades, scores, remarks.
3. Overall grade, percentage, rank.
4. Teacher remarks section.
5. Download PDF button.

**UI Elements**:
- `SmsTopBar` with back button + "Report Card" title + download action
- Header: Academic Year + Term + Issue Date
- `LazyColumn` of subject rows:
  - Subject name
  - Grade badge (A+, B, etc. with color)
  - Score/Max Score (e.g., 95/100)
  - Remarks (if any)
- Summary section:
  - Overall Grade
  - Overall Percentage
  - Rank
- Remarks section:
  - Class Teacher Remarks
  - Principal Remarks

**Data sources**: REST (`GET /api/reports/{report_id}/`)

---

### Schedule Tab

**File**: `presentation/screens/child/tabs/ScheduleTabContent.kt`

**Purpose**: Weekly class timetable.

**UX Flow**:
1. Day selector (horizontal scrollable: Mon, Tue, Wed, ...).
2. Selected day shows list of periods with subject, teacher, time.
3. Current period highlighted (if during school hours).

**UI Elements**:
- Day selector: `ScrollableTabRow` with days of week
- `LazyColumn` of `SmsScheduleItem`:
  - Period number badge
  - Time range (e.g., 08:00 - 08:45)
  - Subject name
  - Teacher name
- Highlight current period (if applicable)

**Schedule Item (`SmsScheduleItem`)**:
```kotlin
@Composable
fun SmsScheduleItem(
    period: SchedulePeriod,
    isCurrent: Boolean = false,
    modifier: Modifier = Modifier
) {
    SmsCard(
        modifier = modifier,
        containerColor = if (isCurrent) PrimaryBlueLight else MaterialTheme.colorScheme.surface
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            SmsBadge(text = period.period.toString(), color = PrimaryBlue)
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(period.subject, style = MaterialTheme.typography.titleMedium)
                Text(period.teacher, style = MaterialTheme.typography.bodyMedium, color = NeutralGray)
            }
            Text("${period.startTime} - ${period.endTime}", style = MaterialTheme.typography.bodySmall, color = NeutralGray)
        }
    }
}
```

**Data sources**: REST (`GET /api/schedule/student/{id}/`)

---

### Announcements Screen

**File**: `presentation/screens/announcements/AnnouncementsScreen.kt`

**Purpose**: List of school announcements.

**UX Flow**:
1. List all announcements (most recent first).
2. Each card shows: Title, Date, Priority badge.
3. Tap announcement → navigate to detail view.
4. Pull-to-refresh loads latest.

**UI Elements**:
- `SmsTopBar` with "Announcements" title
- `LazyColumn` of `SmsAnnouncementCard`:
  - Priority badge (HIGH=red, NORMAL=blue)
  - Title
  - Date posted
  - Short excerpt
- Tap card → navigate to `AnnouncementDetailScreen`
- `SmsEmptyState` if no announcements

**Announcement Card (`SmsAnnouncementCard`)**:
```kotlin
@Composable
fun SmsAnnouncementCard(
    announcement: Announcement,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    SmsCard(
        onClick = onClick,
        modifier = modifier
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(announcement.title, style = MaterialTheme.typography.titleMedium)
                if (announcement.priority == "HIGH") {
                    SmsBadge(text = "Important", color = ErrorRed)
                }
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(announcement.datePosted.format(), style = MaterialTheme.typography.bodySmall, color = NeutralGray)
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                announcement.excerpt,
                style = MaterialTheme.typography.bodyMedium,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis
            )
        }
    }
}
```

**Data sources**: REST (`GET /api/announcements/`)

---

### Announcement Detail Screen

**File**: `presentation/screens/announcements/AnnouncementDetailScreen.kt`

**Purpose**: Full announcement with content and attachments.

**UI Elements**:
- `SmsTopBar` with back button + announcement title
- Date posted
- Full content (HTML or Markdown rendered)
- Attachments list (if any) with download buttons

**Data sources**: REST (`GET /api/announcements/{id}/`)

---

### Profile Screen

**File**: `presentation/screens/profile/ProfileScreen.kt`

**Purpose**: Parent profile, change password, logout.

**UI Elements**:
- `SmsTopBar` with "Profile" title
- Parent info section (name, email, phone)
- `SmsButton` outline: "Change Password" → navigate to `ChangePasswordScreen`
- `SmsButton` danger: "Logout" → confirm dialog → clear token → navigate to login

---

### Change Password Screen

**File**: `presentation/screens/profile/ChangePasswordScreen.kt`

**Purpose**: Change parent password.

**UI Elements**:
- `SmsTopBar` with back button + "Change Password" title
- `SmsTextField` for current password
- `SmsTextField` for new password
- `SmsTextField` for confirm new password
- `SmsButton` primary: "Save" → call API → show success/error

---

## Component Catalog Screen (Dev-only)

**File**: `presentation/screens/catalog/ComponentCatalogScreen.kt`

**Purpose**: Visual reference for all `Sms*` components (dev builds only).

**Sections**:
- Colors (palette preview)
- Typography (text styles)
- Buttons (all variants)
- Badges (all colors)
- Cards (all variants)
- Text Fields (normal, error, disabled)
- Section Headers
- Empty States
- Loading Indicators
- Student Card
- Attendance Calendar
- Report Card Item
- Schedule Item
- Announcement Card

---

## Implementation Phases

### Phase 0: Foundation Setup
- [ ] Create Android project with Kotlin + Compose
- [ ] Set up Hilt for DI
- [ ] Define `presentation/theme/` (Color, Type, Shapes, Theme)
- [ ] Create base components: `SmsButton`, `SmsCard`, `SmsBadge`, `SmsTextField`, `SmsSectionHeader`, `SmsEmptyState`, `SmsLoadingIndicator`, `SmsTopBar`, `SmsErrorBanner`
- [ ] Build `ComponentCatalogScreen` for visual testing

### Phase 1: Authentication
- [ ] `SplashScreen` with token check
- [ ] `LoginScreen` with email/password input
- [ ] `AuthViewModel` + `LoginUseCase`
- [ ] Navigation setup (splash → login → dashboard)

### Phase 2: Dashboard & Children
- [ ] `DashboardScreen` with children list
- [ ] `SmsStudentCard` component
- [ ] Fetch children from API
- [ ] Navigate to child detail on tap

### Phase 3: Child Detail & Tabs
- [ ] `ChildDetailScreen` with tabs
- [ ] `AttendanceTabContent` with `SmsAttendanceCalendar`
- [ ] `ReportsTabContent` with `SmsReportCardItem`
- [ ] `ScheduleTabContent` with `SmsScheduleItem`
- [ ] `ReportDetailScreen` (full report card)

### Phase 4: Announcements & Profile
- [ ] `AnnouncementsScreen` with `SmsAnnouncementCard`
- [ ] `AnnouncementDetailScreen`
- [ ] `ProfileScreen`
- [ ] `ChangePasswordScreen`
- [ ] Logout functionality

### Phase 5: Polish & Advanced Features
- [ ] Offline caching (Room database)
- [ ] PDF download for report cards
- [ ] Push notifications (FCM)
- [ ] Pull-to-refresh on all lists
- [ ] Dark mode support
- [ ] Accessibility improvements

---

## Testing Strategy

- **Unit tests**: ViewModels, UseCases, Repositories
- **Compose tests**: UI components, screen rendering, user interactions
- **Integration tests**: API + Repository layer
- **Screenshot tests**: Visual regression testing for components

---

## Accessibility

- All interactive elements must have `contentDescription`
- Text contrast ratios meet WCAG AA standards
- Minimum touch target size: 48dp
- Support for screen readers (TalkBack)
- Keyboard navigation (external keyboard support)

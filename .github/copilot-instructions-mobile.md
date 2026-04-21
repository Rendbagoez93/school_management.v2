# Copilot Instructions — School Management System Mobile (Android)

## Project Overview

- **Platform**: Android
- **Language**: Kotlin 2.0+
- **UI Framework**: Jetpack Compose + Material 3
- **Min SDK**: 24 (Android 7.0) / **Target SDK**: 35 (Android 15)
- **Architecture**: Clean Architecture (Data → Domain → Presentation)
- **State Management**: ViewModel + StateFlow/LiveData
- **Dependency Injection**: Hilt
- **Network**: Retrofit 2 + OkHttp
- **Database**: Room (local caching) + DataStore (preferences)
- **Serialization**: Kotlinx Serialization (not Gson, not Moshi)
- **Testing**: JUnit 4 + Mockito + Kotest + Compose Testing
- **Build System**: Gradle (Kotlin DSL)
- **AGP**: 8.2+
- **IDE**: Android Studio (Jellyfish or later)

---

## Product Vision

### What Is School Management System Mobile?

School Management System mobile is the **Android parent portal app** for the School Management System. It enables **parents** to monitor their children's academic performance, attendance records, view class schedules, receive school announcements, and download report cards — all in real-time from their school's dedicated installation.

### Core Domain Concepts

| Concept | Description | Mobile Use Case |
|---|---|---|
| **School** | The educational institution running this installation. Provides branding (colors, logo, name). | App displays school-specific branding |
| **Parent** | Guardian account linked to one or more students. | Primary app user: views children's data |
| **Student** | Child enrolled in the school. Parent can have multiple children. | Parents select which child to view |
| **Academic Year** | School year (e.g., 2025-2026). | Filter reports and data by year |
| **Grade/Class** | Student's current class/grade level. | Display child's class information |
| **Attendance** | Daily attendance records with status (present, absent, late, excused). | Parents view monthly attendance summary |
| **Report Card** | Academic performance report per term with subject grades. | Parents download PDF reports |
| **Schedule** | Weekly class timetable showing subjects and timings. | View child's daily/weekly schedule |
| **Announcement** | School-wide or grade-specific notices, events, holidays. | Push notification + in-app message list |
| **Subject** | Curriculum subjects (Math, English, etc.). | Shown in schedule and report cards |
| **School Branding** | Custom colors, logo, and school name. | Dynamic theming based on school config |

### Future Goals / Roadmap

- **Phase 1 (MVP)**: Authentication (email+password)
- **Phase 2**: Dashboard & Children List (select child, view summary)
- **Phase 3**: Core Features (attendance, reports, schedule, announcements)
- **Phase 4**: Advanced Features (offline cache, fee payment, push notifications)

### Language Rules

- **UI Copy** (buttons, labels, messages) — **English** (or configurable per school)
- **API Responses** (`code`, `msg`) — **English**
- **Code** (variables, functions, comments, docstrings) — **English**
- **Class/Interface Names** — **English**
- **Compose String Resources** (`strings.xml`) — **English**

---

## Code Style

### General

- **Kotlin first**: No Java code. Use Kotlin idioms (data classes, sealed classes, extension functions, coroutines).
- **Static typing**: All function parameters and return types must have explicit types. Do not rely on type inference for public APIs.
- **No over-commenting**: Let function and class names explain intent. Add comments only when something is non-obvious, complex, or a workaround.
- **Use ktlint** for formatting and linting. Line length is **120 characters**.
- **Follow Clean Architecture**: Separate Data, Domain, and Presentation layers clearly.

### Kotlin Conventions

- Use `data class` for models with value semantics (POJOs, DTOs).
- Use `sealed class` or `sealed interface` for state/result hierarchies.
- Use `object` for singletons, constants, and utility groupings.
- Prefer `val` over `var` — immutability by default.
- Use `?.let { }` instead of null checks with `if (x != null)`.
- Use `when` exhaustively for sealed types (no `else` branch if all cases covered).
- Prefer extension functions over utility classes (e.g., `String.toPhoneNumber()` instead of `PhoneUtils.format()`).
- Use `by lazy` for expensive one-time initialization.
- Use `require()` / `check()` for preconditions and invariants.

### Jetpack Compose

- **Composable functions are PascalCase** (e.g., `LoginScreen`, `StudentCard`).
- **Composables should be stateless** when possible. Hoist state to ViewModels or parent composables.
- Use `remember { }` for local UI state (e.g., text field focus, dialog visibility).
- Use `rememberSaveable { }` for state that should survive configuration changes (e.g., scroll position).
- Avoid side effects in composables — use `LaunchedEffect`, `DisposableEffect`, `SideEffect` when needed.
- Pass callbacks as lambda parameters, not interfaces.
- Use `Modifier` parameters at the end of the function signature with a default value (`Modifier = Modifier`).
- **Component-first design**: Every reusable visual pattern must be extracted into a dedicated `@Composable` in `presentation/components/`. Never duplicate layout or styling code across screens. All project components use the `Sms` prefix (e.g., `SmsButton`, `SmsCard`, `SmsBadge`, `SmsSectionHeader`).

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| **Classes** | PascalCase | `StudentRepository`, `AuthViewModel`, `LoginScreen` |
| **Functions** | camelCase | `getStudentById()`, `validateEmail()` |
| **Variables** | camelCase | `studentName`, `authToken`, `isLoading` |
| **Constants** | UPPER_SNAKE_CASE | `API_BASE_URL`, `MAX_RETRY_ATTEMPTS` |
| **Composables** | PascalCase | `LoginButton`, `StudentCard`, `EmptyStateView` |
| **Sealed Classes** | PascalCase | `AuthState`, `ApiResult`, `UiEvent` |
| **Data Classes** | PascalCase | `Student`, `AuthRequest`, `Attendance` |
| **Interfaces** | PascalCase (no "I" prefix) | `AuthRepository`, `EmailValidator` |

### Package Structure

```
com.school.parentportal/
├── di/                          # Dependency injection modules (Hilt)
├── data/
│   ├── api/                     # Retrofit interfaces
│   │   ├── AuthApi.kt
│   │   ├── StudentApi.kt
│   │   ├── AttendanceApi.kt
│   │   └── interceptors/        # OkHttp interceptors
│   ├── local/                   # Room database
│   │   ├── dao/
│   │   ├── entities/
│   │   └── AppDatabase.kt
│   ├── model/                   # DTOs (API request/response models)
│   ├── repository/              # Repository implementations
│   └── storage/                 # SharedPreferences, DataStore
├── domain/
│   ├── model/                   # Domain models (business entities)
│   ├── repository/              # Repository interfaces
│   └── usecase/                 # Use cases (business logic)
├── presentation/
│   ├── screens/                 # Main screens (LoginScreen, DashboardScreen, etc.)
│   ├── components/              # Reusable Composables (Buttons, Cards, etc.)
│   ├── viewmodel/               # ViewModels
│   ├── navigation/              # Navigation setup
│   ├── theme/                   # Compose theme (colors, typography, shapes)
│   └── util/                    # UI-specific utilities (formatters, validators)
├── util/                        # General utilities (extensions, constants)
└── MainActivity.kt
```

---

## Architecture: Clean Architecture

### Layer Responsibilities

| Layer | Responsibility | Example |
|-------|---------------|---------|
| **Data** | API calls, database queries, external data sources. Implements repository interfaces. | `AuthRepositoryImpl` fetches from `AuthApi` and `AuthDao` |
| **Domain** | Business logic, entities, use cases. Independent of Android framework. | `LoginUseCase` validates credentials and calls repository |
| **Presentation** | UI components, ViewModels, state management. Observes domain layer. | `LoginViewModel` exposes `StateFlow<AuthState>` for UI |

### Data Layer

- **API clients** (`data/api/`): Retrofit interfaces for backend endpoints.
- **Local storage** (`data/local/`): Room DAOs for caching, DataStore for preferences.
- **DTOs** (`data/model/`): Request/response models with `@Serializable` annotation.
- **Repositories** (`data/repository/`): Implement domain repository interfaces. Coordinate between API and local storage.

```kotlin
// data/api/AuthApi.kt
interface AuthApi {
    @POST("auth/parent-login/")
    suspend fun parentLogin(@Body request: LoginRequest): ApiResponse<UserResponse>
}

// data/repository/AuthRepositoryImpl.kt
class AuthRepositoryImpl @Inject constructor(
    private val authApi: AuthApi,
    private val tokenStorage: TokenStorage
) : AuthRepository {
    override suspend fun login(email: String, password: String): Result<User> {
        return try {
            val response = authApi.parentLogin(LoginRequest(email, password))
            if (response.code == "ok") {
                tokenStorage.saveToken(response.data.token)
                Result.success(response.data.toDomain())
            } else {
                Result.failure(AuthException(response.msg))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Domain Layer

- **Models** (`domain/model/`): Business entities (e.g., `Student`, `Attendance`, `ReportCard`). No Android dependencies.
- **Repository interfaces** (`domain/repository/`): Define contracts for data access.
- **Use cases** (`domain/usecase/`): Encapsulate single business actions. Named with verb prefix (e.g., `GetStudentByIdUseCase`, `LoginUseCase`).

```kotlin
// domain/model/Student.kt
data class Student(
    val id: Int,
    val firstName: String,
    val lastName: String,
    val gradeClass: String,
    val rollNumber: String,
    val photo: String?
)

// domain/repository/StudentRepository.kt
interface StudentRepository {
    suspend fun getChildrenForParent(parentId: Int): Result<List<Student>>
    suspend fun getStudentById(studentId: Int): Result<Student>
}

// domain/usecase/GetChildrenUseCase.kt
class GetChildrenUseCase @Inject constructor(
    private val studentRepository: StudentRepository,
    private val authRepository: AuthRepository
) {
    suspend operator fun invoke(): Result<List<Student>> {
        val parentId = authRepository.getCurrentUserId() ?: return Result.failure(Exception("Not logged in"))
        return studentRepository.getChildrenForParent(parentId)
    }
}
```

### Presentation Layer

- **Screens** (`presentation/screens/`): Composable functions for full screens. Named `*Screen` (e.g., `LoginScreen`, `DashboardScreen`).
- **Components** (`presentation/components/`): Reusable UI elements (e.g., `SmsButton`, `StudentCard`).
- **ViewModels** (`presentation/viewmodel/`): Manage UI state and business logic. Expose `StateFlow` or `LiveData` for UI observation.
- **Navigation** (`presentation/navigation/`): Jetpack Navigation setup with `NavHost`, `NavController`.

```kotlin
// presentation/viewmodel/LoginViewModel.kt
@HiltViewModel
class LoginViewModel @Inject constructor(
    private val loginUseCase: LoginUseCase
) : ViewModel() {
    private val _authState = MutableStateFlow<AuthState>(AuthState.Idle)
    val authState: StateFlow<AuthState> = _authState.asStateFlow()

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            loginUseCase(email, password)
                .onSuccess { user -> _authState.value = AuthState.Success(user) }
                .onFailure { error -> _authState.value = AuthState.Error(error.message ?: "Login failed") }
        }
    }
}

sealed interface AuthState {
    data object Idle : AuthState
    data object Loading : AuthState
    data class Success(val user: User) : AuthState
    data class Error(val message: String) : AuthState
}

// presentation/screens/LoginScreen.kt
@Composable
fun LoginScreen(
    viewModel: LoginViewModel = hiltViewModel(),
    onNavigateToDashboard: () -> Unit
) {
    val authState by viewModel.authState.collectAsState()

    when (val state = authState) {
        is AuthState.Idle -> LoginContent(
            onLoginClick = { email, password -> viewModel.login(email, password) }
        )
        is AuthState.Loading -> LoadingIndicator()
        is AuthState.Success -> LaunchedEffect(Unit) { onNavigateToDashboard() }
        is AuthState.Error -> ErrorMessage(message = state.message)
    }
}
```

---

## Dependencies

### build.gradle.kts (Module-level)

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.serialization")
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp")
}

android {
    namespace = "com.school.parentportal"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.school.parentportal"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables.useSupportLibrary = true
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
        debug {
            isMinifyEnabled = false
            applicationIdSuffix = ".debug"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.8"
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    // Core Android
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.7.0")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
    implementation("androidx.activity:activity-compose:1.8.2")

    // Compose
    val composeBom = platform("androidx.compose:compose-bom:2024.02.00")
    implementation(composeBom)
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    debugImplementation("androidx.compose.ui:ui-tooling")
    debugImplementation("androidx.compose.ui:ui-test-manifest")

    // Navigation
    implementation("androidx.navigation:navigation-compose:2.7.6")

    // Networking
    implementation("com.squareup.retrofit2:retrofit:2.10.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // Serialization
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.2")
    implementation("com.jakewharton.retrofit2:retrofit2-kotlinx-serialization-converter:1.0.0")

    // Storage
    implementation("androidx.datastore:datastore-preferences:1.0.0")
    implementation("androidx.security:security-crypto:1.1.0-alpha06")
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1")

    // Dependency Injection
    implementation("com.google.dagger:hilt-android:2.50")
    ksp("com.google.dagger:hilt-compiler:2.50")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")

    // Image Loading
    implementation("io.coil-kt:coil-compose:2.6.0")

    // Firebase (for push notifications)
    val firebaseBom = platform("com.google.firebase:firebase-bom:33.0.0")
    implementation(firebaseBom)
    implementation("com.google.firebase:firebase-messaging-ktx")

    // Async
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

    // Logging
    implementation("com.jakewharton.timber:timber:5.0.1")

    // Testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.mockito.kotlin:mockito-kotlin:5.2.1")
    testImplementation("io.kotest:kotest-assertions-core:5.8.0")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation(composeBom)
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
}
```

---

## API Integration

### Base URL Configuration

```kotlin
// util/Constants.kt
object ApiConfig {
    const val BASE_URL = "http://10.0.2.2:8000/api/"  // Android emulator
    // For physical device: "http://<school-server-ip>:8000/api/"
    const val CONNECT_TIMEOUT = 30L
    const val READ_TIMEOUT = 30L
    const val WRITE_TIMEOUT = 30L
}
```

### Standard API Response Format

All API endpoints return one of three formats:

**Single Object:**
```json
{
  "code": "ok",
  "msg": "success",
  "data": { "id": 1, "firstName": "John", ... }
}
```

**List of Objects:**
```json
{
  "code": "ok",
  "msg": "success",
  "data": {
    "results": [ {...}, {...} ]
  }
}
```

**Paginated List:**
```json
{
  "code": "ok",
  "msg": "success",
  "data": {
    "results": [ {...}, {...} ],
    "pagination": {
      "totalItems": 100,
      "totalPages": 5,
      "currentPage": 1,
      "perPage": 20
    }
  }
}
```

**Error Response:**
```json
{
  "code": "error_code",
  "msg": "Human-readable message",
  "data": null
}
```

### API Models

```kotlin
// data/model/ApiResponse.kt
@Serializable
data class ApiResponse<T>(
    val code: String,
    val msg: String,
    val data: T?
)

@Serializable
data class ApiListResponse<T>(
    val code: String,
    val msg: String,
    val data: ListData<T>?
)

@Serializable
data class ListData<T>(
    val results: List<T>
)

@Serializable
data class PaginatedData<T>(
    val results: List<T>,
    val pagination: Pagination
)

@Serializable
data class Pagination(
    val totalItems: Int,
    val totalPages: Int,
    val currentPage: Int,
    val perPage: Int
)
```

---

## Design System

### Color Palette (Professional Education Theme)

```kotlin
// presentation/theme/Color.kt
val PrimaryBlue = Color(0xFF1976D2)      // Professional Blue
val PrimaryBlueDark = Color(0xFF0D47A1)  // Deep Blue
val PrimaryBlueLight = Color(0xFFBBDEFB) // Light Blue
val AccentOrange = Color(0xFFFFA726)     // Academic Orange/Gold
val AccentOrangeLight = Color(0xFFFFE0B2)

val SuccessGreen = Color(0xFF43A047)
val WarningYellow = Color(0xFFFBC02D)
val ErrorRed = Color(0xFFDC3545)
val InfoCyan = Color(0xFF0DCAF0)

val NeutralDark = Color(0xFF1E2328)
val NeutralLight = Color(0xFFF9FAFB)
val NeutralGray = Color(0xFF6B7280)
```

### Component Naming Convention

All reusable components use the `Sms` prefix (School Management System):
- `SmsButton` — Primary, outline, accent, ghost, danger variants
- `SmsCard` — Standard card with header, body, footer
- `SmsBadge` — Status badges (present, absent, passed, failed)
- `SmsTextField` — Form input fields
- `SmsSectionHeader` — Section dividers
- `SmsEmptyState` — Empty list placeholder
- `SmsLoadingIndicator` — Loading states
- `SmsTopBar` — App bar with logo and actions
- `SmsBottomNav` — Bottom navigation (if needed)

---

## Logging

Use Timber for structured logging:

```kotlin
// In Application class
class ParentPortalApp : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }
    }
}

// Usage
Timber.d("Student data loaded: %s", student.name)
Timber.e(exception, "Failed to load attendance")
```

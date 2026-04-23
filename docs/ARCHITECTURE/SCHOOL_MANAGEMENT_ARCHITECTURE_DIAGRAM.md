# School Management App Architecture Diagram

Date: April 23, 2026  
Scope: Current architecture with near-term module expansion points

## 1. System/Container Architecture

```mermaid
flowchart TB
    subgraph CLIENTS[Clients]
        WEB[Web Browser\nAdmin and Staff Portal]
        MOBILE[Android Parent App\nJetpack Compose]
        API_CONSUMER[API Clients\nSwagger/Redoc/Test Tools]
    end

    subgraph EDGE[Edge and Access]
        NGINX[Reverse Proxy / HTTPS Termination]
    end

    subgraph DJANGO[School Management Backend - Django ASGI]
        URLS[Routing Layer\nconfig/urls.py + config/api_urls.py]
        MIDDLEWARE[Middleware Layer\nSecurity, CORS, Session, Auth, SchoolUserMiddleware, ApiErrorMiddleware]
        API_LAYER[API Layer\nDRF Views/ViewSets + shared.api wrappers/parsers]
        DOMAIN[Domain Layer\napplications/* services and orchestrators]
        INFRA[Infrastructure Modules\nmodules/user, modules/auth, shared/*]
        ORM[Django ORM]
    end

    subgraph DATA[Data Stores]
        POSTGRES[(PostgreSQL)]
        STATIC[(Assets/Static Files)]
        MEDIA[(Media Files)]
    end

    subgraph DOCS[API Docs and Auth]
        OPENAPI[drf-spectacular\nOpenAPI schema]
        JWT[JWT Auth\nSimpleJWT]
    end

    WEB --> NGINX
    MOBILE --> NGINX
    API_CONSUMER --> NGINX

    NGINX --> URLS
    URLS --> MIDDLEWARE
    MIDDLEWARE --> API_LAYER

    API_LAYER --> JWT
    API_LAYER --> OPENAPI
    API_LAYER --> DOMAIN
    DOMAIN --> INFRA
    DOMAIN --> ORM
    INFRA --> ORM

    ORM --> POSTGRES
    API_LAYER --> STATIC
    API_LAYER --> MEDIA
```

## 2. Backend Internal Architecture

```mermaid
flowchart LR
    REQUEST[HTTP Request\n/api/*] --> ROUTER[URL Router\nconfig.api_urls]
    ROUTER --> MW[Middleware Chain]
    MW --> VIEW[DRF API View / ViewSet]

    VIEW --> PARSER[Pydantic Request Parsing\nshared.api.parsers]
    VIEW --> SERVICE[Application Service Layer\napplications/.../services.py]

    SERVICE --> MANAGER[Model Manager / QuerySet]
    SERVICE --> DOMAIN_RULES[Domain Rules\nvalidators, orchestrator]

    MANAGER --> MODEL[Django Models]
    DOMAIN_RULES --> MODEL
    MODEL --> DB[(PostgreSQL)]

    VIEW --> RESPONSE[Standard Response Wrapper\nshared.api.response]
    MW --> ERROR[ApiErrorMiddleware\nshared.api.middleware]
    ERROR --> RESPONSE

    RESPONSE --> OUT[JSON Response\ncode,msg,data]
```

## 3. Module Boundaries

- config: settings, ASGI/WSGI entry points, root and API URL composition.
- modules: reusable infrastructure components (custom user model, auth rules).
- applications: business domain modules (academic setup, user management, school management domains).
- shared: cross-cutting utilities (base models, API middleware/parsers/response, common helpers).
- assets/templates: web UI static and template resources.

## 4. Current Implemented Domain Modules

- applications.academic_setup
- applications.user_management
- applications.school_management.academic_management
- applications.school_management.grade_management
- applications.school_management.staff_management

## 5. Planned Expansion Modules (Architecture Extension Points)

- applications.school_config
- applications.auth_api
- applications.school_management.student_management
- applications.school_management.parent_management
- applications.school_management.attendance
- applications.school_management.reports
- applications.school_management.schedule
- applications.school_management.announcements

## 6. Key Architectural Characteristics

- Modular monolith: single deployable backend with clear module boundaries.
- API-first backend: standardized JSON envelope and explicit error handling.
- Role-based access control: custom user model + groups + role field.
- Single-instance school deployment: one installation serves one school.
- Mobile integration ready: JWT, OpenAPI docs, and consistent response contracts.

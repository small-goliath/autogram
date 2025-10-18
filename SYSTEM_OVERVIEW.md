# Autogram System Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Next.js Frontend (app/)          Admin Panel          Mobile App        │
│  ├── Public Pages                 ├── User Management  (Future)          │
│  ├── User Dashboard               ├── Helper Accounts                    │
│  └── Auth Pages                   └── Analytics                          │
│                                                                           │
└────────────────────────────┬──────────────────────────────────────────────┘
                             │ HTTPS/REST
                             │
┌────────────────────────────▼──────────────────────────────────────────────┐
│                        API LAYER (FastAPI)                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Public Routes              Admin Routes (JWT Auth)                      │
│  ├── /api/notices           ├── /api/admin/login                        │
│  ├── /api/requests-by-week  ├── /api/admin/sns-users                    │
│  ├── /api/user-action-...   ├── /api/admin/helpers                      │
│  ├── /api/consumer          └── /api/admin/me                           │
│  ├── /api/producer                                                       │
│  └── /api/unfollow-checker                                               │
│                                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│                       MIDDLEWARE LAYER                                    │
│  ├── CORS Handler           ├── Error Handler                           │
│  ├── JWT Validator           └── Logging                                 │
│  └── Request Logger                                                       │
└────────────────────────────┬──────────────────────────────────────────────┘
                             │
┌────────────────────────────▼──────────────────────────────────────────────┐
│                      SERVICE LAYER (Business Logic)                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  User Services                  Instagram Service                        │
│  ├── sns_raise_user_service     ├── get_helper_client()                 │
│  ├── request_by_week_service    ├── login_producer()                    │
│  └── verification_service       └── check_unfollowers()                  │
│                                                                           │
│  AI Services                    Auth Service                             │
│  ├── consumer_service           ├── authenticate_admin()                │
│  ├── producer_service           ├── create_token()                      │
│  └── unfollow_checker_service   └── verify_token()                      │
│                                                                           │
└──────┬────────────────────┬─────────────────────────┬──────────────────────┘
       │                    │                         │
       │                    │                         │
┌──────▼──────┐     ┌───────▼─────────┐      ┌──────▼───────────┐
│ REPOSITORY  │     │  INSTAGRAM      │      │  CACHE LAYER     │
│   LAYER     │     │  INTEGRATION    │      │  (Optional)      │
│             │     │                 │      │                  │
│ *_db.py     │     │ Instaloader     │      │ Redis            │
│ files       │     │ (Read Ops)      │      │ ├── Sessions     │
│             │     │                 │      │ ├── Rate Limits  │
│ Data Access │     │ Instagrapi      │      │ └── Cache        │
│ Objects     │     │ (Write Ops)     │      │                  │
└──────┬──────┘     └─────────────────┘      └──────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────────────────────┐
│                     DATABASE LAYER (PostgreSQL)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Core Tables                    AI Tables                           │
│  ├── sns_raise_user             ├── consumer                        │
│  ├── request_by_week            ├── producer                        │
│  ├── user_action_verification   └── helper                          │
│  └── admin                                                           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      BATCH PROCESSING LAYER                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Scheduled Jobs                                                      │
│  ├── weekly_verification_check.py  (Weekly)                         │
│  └── ai_comment_generator.py      (Hourly/Daily)                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Instagram API          OpenAI API (Future)      Email Service      │
│  ├── Read Posts         ├── Generate Comments    ├── Notifications  │
│  ├── Comment            └── AI Analysis          └── Alerts         │
│  └── Followers                                                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Request Flow Diagram

### Public API Request Flow

```
User → Frontend → API Router → Service → Repository → Database
                       ↓
                  Instagram API
                       ↓
                    Response
```

### Admin API Request Flow

```
Admin → Frontend → API Router → JWT Auth → Service → Repository → Database
                       ↓             ↓
                  Middleware    (validates token)
                       ↓
                    Response
```

## Database Entity Relationship Diagram

```
┌──────────────────┐
│  sns_raise_user  │
│ ──────────────── │
│ id (PK)         │
│ username (UK)    │
│ created_at      │
│ updated_at      │
└────────┬─────────┘
         │ 1
         │
         │ *
         ▼
┌────────────────────┐         ┌───────────────────────────┐
│ request_by_week    │         │ user_action_verification  │
│ ────────────────── │    ┌───►│ ───────────────────────── │
│ id (PK)           │    │    │ id (PK)                   │
│ user_id (FK) ─────┼────┘    │ user_id (FK) ─────────┐   │
│ week_number       │         │ request_id (FK) ◄──┐  │   │
│ year              │         │ is_verified        │  │   │
│ instagram_link    │         │ verified_at        │  │   │
│ created_at        │◄────────┤ created_at         │  │   │
└───────────────────┘         └────────────────────┘  │   │
                                        │              │   │
                                        └──────────────┘   │
                                                           │
                         ┌─────────────────────────────────┘
                         │
                         │
┌────────────────────┐  │       ┌─────────────────────┐
│      helper        │  │       │     consumer        │
│ ────────────────── │  │       │ ─────────────────── │
│ id (PK)           │  │       │ id (PK)            │
│ instagram_id (UK)  │  │       │ instagram_id (UK)   │
│ password          │  │       │ is_active          │
│ session_data      │  │       │ created_at         │
│ is_active         │  │       │ updated_at         │
│ last_used_at      │  │       └─────────────────────┘
│ created_at        │  │
└───────────────────┘  │       ┌─────────────────────┐
                        │       │     producer        │
┌───────────────────┐  │       │ ─────────────────── │
│      admin        │  │       │ id (PK)            │
│ ───────────────── │  │       │ instagram_id (UK)   │
│ id (PK)          │  │       │ password           │
│ username (UK)     │  │       │ verification_code   │
│ password_hash    │  │       │ is_verified        │
│ is_active        │  │       │ is_active          │
│ last_login_at    │  │       │ session_data       │
│ created_at       │  │       │ created_at         │
└──────────────────┘  │       │ updated_at         │
                       │       └─────────────────────┘
                       │
                       └──── Uses for read operations
```

## Technology Stack

### Backend (API)
```
┌─────────────────────────────────────┐
│ FastAPI 0.115.0                     │
│ ├── Pydantic 2.9.2 (validation)    │
│ ├── Uvicorn 0.31.0 (ASGI server)   │
│ └── Python 3.13                     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ SQLAlchemy 2.0.35 (ORM)             │
│ ├── AsyncPG 0.29.0 (async driver)  │
│ ├── Alembic 1.13.3 (migrations)    │
│ └── PostgreSQL 14+                  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Authentication & Security           │
│ ├── python-jose (JWT)               │
│ ├── passlib + bcrypt (passwords)   │
│ └── cryptography (encryption)       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Instagram Integration               │
│ ├── Instaloader 4.13 (read)        │
│ └── Instagrapi 2.1.2 (write)       │
└─────────────────────────────────────┘
```

### Frontend (App)
```
┌─────────────────────────────────────┐
│ Next.js 14.2.13                     │
│ ├── React 18.3.1                    │
│ ├── TypeScript 5.6.2                │
│ └── Tailwind CSS 3.4.12             │
└─────────────────────────────────────┘
```

## API Endpoints Summary

### Public Endpoints (No Auth)

| Endpoint | Method | Description | Key Parameters |
|----------|--------|-------------|----------------|
| `/api/notices` | GET | Get announcements | - |
| `/api/requests-by-week` | GET | Get weekly requests | username, week, year |
| `/api/user-action-verification` | GET | Get verifications | username, is_verified |
| `/api/consumer` | POST | Register consumer | instagram_id |
| `/api/producer` | POST | Register producer | instagram_id, password, code |
| `/api/unfollow-checker` | POST | Check unfollowers | instagram_id, password, code |

### Admin Endpoints (JWT Required)

| Endpoint | Method | Description | Key Parameters |
|----------|--------|-------------|----------------|
| `/api/admin/login` | POST | Admin login | username, password |
| `/api/admin/me` | GET | Get current admin | - |
| `/api/admin/sns-users` | GET | List users | skip, limit |
| `/api/admin/sns-users` | POST | Create user | username |
| `/api/admin/sns-users/{id}` | PUT | Update user | username |
| `/api/admin/sns-users/{id}` | DELETE | Delete user | - |
| `/api/admin/helpers` | GET | List helpers | skip, limit |
| `/api/admin/helpers` | POST | Create helper | instagram_id, password |
| `/api/admin/helpers/{id}` | DELETE | Delete helper | - |

## Directory Structure Overview

```
autogram-latest/
│
├── api/                    # FastAPI Backend
│   ├── core/              # Security, exceptions, middleware
│   ├── db/                # Models, repositories, session
│   │   ├── models/        # SQLAlchemy models
│   │   └── repositories/  # Data access layer (*_db.py)
│   ├── schemas/           # Pydantic validation models
│   ├── services/          # Business logic (*_service.py)
│   ├── integrations/      # Instagram clients
│   ├── routers/           # API endpoints
│   │   ├── public/        # No auth required
│   │   └── admin/         # JWT auth required
│   ├── config.py          # Settings
│   ├── dependencies.py    # DI setup
│   └── index.py           # Main app
│
├── app/                   # Next.js Frontend
│   ├── pages/             # Next.js pages
│   ├── components/        # React components
│   └── styles/            # CSS/Tailwind
│
├── batch/                 # Background jobs
│   ├── weekly_verification_check.py
│   └── ai_comment_generator.py
│
├── core/                  # Shared logic
│   ├── constants.py
│   └── utils.py
│
├── tests/                 # Test suite
│   ├── test_api/
│   ├── test_services/
│   └── test_repositories/
│
├── scripts/               # Utility scripts
│   ├── create_admin.py
│   ├── test_db_connection.py
│   └── ...
│
├── alembic/              # Database migrations
│   └── versions/
│
├── .env                  # Environment variables (gitignored)
├── .env.example          # Template
├── requirements.txt      # Python dependencies
└── package.json          # Node.js dependencies
```

## Code Architecture Patterns

### Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: Router (API Endpoint)                         │
│ ────────────────────────────────────────────────────── │
│ - Handles HTTP requests/responses                      │
│ - Validates input (Pydantic)                           │
│ - Calls service layer                                   │
│ - Returns formatted response                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 2: Service (Business Logic)                      │
│ ────────────────────────────────────────────────────── │
│ - Orchestrates business operations                      │
│ - Coordinates between repositories                      │
│ - Handles business rules and validation                 │
│ - Calls repository layer                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 3: Repository (Data Access)                      │
│ ────────────────────────────────────────────────────── │
│ - CRUD operations                                       │
│ - Database queries                                      │
│ - Works with SQLAlchemy models                          │
│ - Returns model instances                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 4: Database (PostgreSQL)                         │
│ ────────────────────────────────────────────────────── │
│ - Persistent storage                                    │
│ - ACID transactions                                     │
│ - Indexes and constraints                               │
└─────────────────────────────────────────────────────────┘
```

### File Naming Conventions

```
Models:         snake_case.py        (api/db/models/sns_raise_user.py)
Repositories:   *_db.py              (api/db/repositories/sns_raise_user_db.py)
Services:       *_service.py         (api/services/sns_raise_user_service.py)
Schemas:        snake_case.py        (api/schemas/sns_raise_user.py)
Routers:        snake_case.py        (api/routers/public/notices.py)
Tests:          test_*.py            (tests/test_api/test_notices.py)
Scripts:        snake_case.py        (scripts/create_admin.py)
```

## Security Architecture

### Authentication Flow

```
1. Admin Login
   │
   ├─► Validate credentials (username/password)
   │   ├─► Hash comparison (bcrypt)
   │   └─► Check is_active flag
   │
   ├─► Generate JWT token
   │   ├─► Payload: {sub: admin_id, exp: timestamp}
   │   └─► Sign with SECRET_KEY
   │
   └─► Return token to client

2. Authenticated Request
   │
   ├─► Extract token from Authorization header
   │   └─► Format: "Bearer <token>"
   │
   ├─► Verify token
   │   ├─► Decode with SECRET_KEY
   │   ├─► Check expiration
   │   └─► Extract admin_id
   │
   ├─► Load admin from database
   │   ├─► Check exists
   │   └─► Check is_active
   │
   └─► Proceed with request
```

### Password Security

```
Admin Passwords:
├── Hash with bcrypt (one-way)
├── Store hash in database
└── Never decrypt (compare hashes)

Instagram Passwords:
├── Encrypt with Fernet (reversible)
├── Store encrypted in database
└── Decrypt when needed for Instagram login
```

## Data Flow Examples

### Example 1: Creating a New SNS User (Admin)

```
1. Admin Frontend
   POST /api/admin/sns-users
   Headers: Authorization: Bearer <token>
   Body: { "username": "newuser" }
   │
   ▼
2. API Router (api/routers/admin/sns_users.py)
   - Validate JWT token
   - Parse request body (Pydantic)
   - Call service
   │
   ▼
3. Service (api/services/sns_raise_user_service.py)
   - Check for duplicates
   - Validate business rules
   - Call repository
   │
   ▼
4. Repository (api/db/repositories/sns_raise_user_db.py)
   - Create SQLAlchemy model
   - Insert into database
   - Return model instance
   │
   ▼
5. Response Flow (reverse)
   Repository → Service → Router → Frontend
   - Convert to Pydantic schema
   - Return 201 Created
   - JSON response
```

### Example 2: Checking Unfollowers (Public)

```
1. User Frontend
   POST /api/unfollow-checker
   Body: {
     "instagram_id": "user123",
     "password": "pass123",
     "verification_code": "ABC123"
   }
   │
   ▼
2. API Router (api/routers/public/unfollow_checker.py)
   - No JWT required (public endpoint)
   - Validate request body
   - Call service
   │
   ▼
3. Service (api/services/unfollow_checker_service.py)
   - Verify Instagram credentials
   - Call Instagram service
   │
   ▼
4. Instagram Service (api/services/instagram_service.py)
   - Login with Instaloader
   - Get followers list
   - Get following list
   - Calculate unfollowers
   │
   ▼
5. Instaloader Client (api/integrations/instaloader_client.py)
   - Make Instagram API calls
   - Handle rate limiting
   - Return data
   │
   ▼
6. Response Flow (reverse)
   Instagram → Service → Router → Frontend
   - Format response
   - Return unfollowers list
```

## Performance Considerations

### Database Optimization

```
Indexes:
├── Primary keys (id) - automatic
├── Unique constraints (username, instagram_id)
├── Foreign keys - recommended
└── Frequently queried columns (week_number, year)

Connection Pooling:
├── Pool size: 5 connections
├── Max overflow: 10 connections
├── Pool pre-ping: enabled
└── Async operations: non-blocking
```

### Instagram Rate Limiting

```
Strategy:
├── Request delay: 2 seconds between calls
├── Helper rotation: distribute load
├── Session reuse: avoid repeated logins
└── Exponential backoff: on rate limit errors

Limits (approximate):
├── Login attempts: ~5 per hour
├── API calls: ~200 per hour per account
└── Comments: ~60 per hour per account
```

### Caching Strategy (Future)

```
Redis Cache:
├── Session data (TTL: 1 hour)
├── Instagram data (TTL: 5 minutes)
├── Helper account rotation (TTL: 1 minute)
└── Rate limit counters (TTL: 1 hour)
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer                         │
│                   (Nginx/Caddy)                          │
└────────────────┬───────────────┬────────────────────────┘
                 │               │
        ┌────────▼──────┐  ┌────▼───────────┐
        │  Next.js App  │  │  FastAPI App   │
        │  (Port 3000)  │  │  (Port 8000)   │
        │               │  │                 │
        │  ├── Static   │  │  ├── Uvicorn   │
        │  └── SSR      │  │  └── Workers   │
        └───────────────┘  └────────┬────────┘
                                    │
                           ┌────────▼─────────┐
                           │   PostgreSQL     │
                           │   (Port 5432)    │
                           └──────────────────┘
```

## Monitoring & Logging

```
Application Logs:
├── Request logs (all endpoints)
├── Error logs (exceptions)
├── Security logs (auth failures)
└── Performance logs (slow queries)

Metrics to Track:
├── API response times
├── Database query times
├── Instagram API calls
├── Authentication failures
├── Active users
└── Error rates

Tools (recommended):
├── Logging: structlog or Python logging
├── Monitoring: Prometheus + Grafana
├── Error tracking: Sentry
└── APM: New Relic or DataDog
```

## Summary

This system provides:
- ✅ Modular, scalable FastAPI architecture
- ✅ Secure JWT-based authentication
- ✅ Instagram integration (read/write)
- ✅ Comprehensive data validation
- ✅ Async-first design
- ✅ Clean separation of concerns
- ✅ Production-ready patterns
- ✅ Extensive documentation

For detailed information, see:
- **ARCHITECTURE.md** - Complete technical architecture
- **IMPLEMENTATION_CHECKLIST.md** - Step-by-step implementation
- **QUICK_REFERENCE.md** - Code templates and examples
- **GETTING_STARTED.md** - Setup and installation guide

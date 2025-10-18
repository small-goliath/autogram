# Autogram Project Implementation Status

## ✅ Completed Components

### 1. Core Infrastructure (`@core` directory)
- ✅ **config.py** - Application settings and configuration
- ✅ **database.py** - SQLAlchemy async setup and session management
- ✅ **models.py** - All 8 database models (SnsRaiseUser, RequestByWeek, UserActionVerification, Helper, Consumer, Producer, Admin, Notice)
- ✅ **schemas.py** - Pydantic schemas for API validation
- ✅ **security.py** - Password hashing, JWT tokens, encryption utilities
- ✅ **instagram_helper.py** - Instagram API wrappers (instaloader + instagrapi)

### 2. Backend Setup (`@api` directory)
- ✅ **index.py** - FastAPI app with CORS, lifespan events
- ✅ **requirements.txt** - All Python dependencies

### 3. Configuration
- ✅ **.env.example** - Complete environment variable template

## 🚧 Remaining Implementation Tasks

### Priority 1: Backend API (2-3 days)
1. **Repository Layer** (`api/repositories/`)
   - `sns_user_repository.py` - CRUD for sns_raise_user
   - `request_repository.py` - CRUD for request_by_week
   - `verification_repository.py` - CRUD for user_action_verification
   - `helper_repository.py` - CRUD for helper accounts
   - `admin_repository.py` - CRUD for admin users
   - `consumer_repository.py` - CRUD for consumers
   - `producer_repository.py` - CRUD for producers
   - `notice_repository.py` - CRUD for notices

2. **Service Layer** (`api/services/`)
   - `sns_user_service.py` - Business logic for user management
   - `request_service.py` - Business logic for weekly requests
   - `verification_service.py` - Business logic for action verification
   - `helper_service.py` - Helper account management + Instagram login
   - `admin_service.py` - Admin authentication and authorization
   - `consumer_service.py` - Consumer registration
   - `producer_service.py` - Producer registration + Instagram login
   - `instagram_service.py` - Instagram operations (comments, unfollowers)
   - `notice_service.py` - Notice management

3. **API Routers** (`api/routers/`)
   - `admin_router.py` - Admin endpoints (login, user CRUD, helper CRUD)
   - `public_router.py` - Public endpoints (notices, status tables)
   - `ai_router.py` - AI comment endpoints (consumer, producer)
   - `unfollow_router.py` - Unfollow checker endpoint

### Priority 2: Batch Jobs (1-2 days)
1. **KakaoTalk Parser** (`batch/kakaotalk_parser.py`)
   - Parse KakaoTalk_latest.txt
   - Extract username and Instagram links
   - Save to request_by_week table

2. **Comment Verifier** (`batch/comment_verifier.py`)
   - Check all links in request_by_week
   - Verify if users commented
   - Save missing comments to user_action_verification

3. **Action Updater** (`batch/action_updater.py`)
   - Check user_action_verification table
   - Verify if comments were posted
   - Delete rows when comments found

4. **Batch Runner** (`batch/run_batch.py`)
   - Main batch orchestrator
   - Schedule all batch jobs
   - Error handling and logging

### Priority 3: Frontend (3-4 days)
1. **Setup**
   - Install additional dependencies (react-hook-form, zod, axios, etc.)
   - Set up Tailwind configuration with design system
   - Create TypeScript types

2. **Layouts**
   - Root layout with auth provider
   - Public layout with navigation
   - Admin layout with auth guard
   - Mobile navigation

3. **Public Pages**
   - Notices page (공지사항)
   - Last week status page (지난주 현황)
   - Exchange status page (품앗이 현황)
   - AI comment receive form
   - AI comment provide form
   - Unfollow checker page

4. **Admin Pages**
   - Login page
   - User management (CRUD)
   - Helper registration

5. **Shared Components**
   - UI components (Button, Input, Table, Card, etc.)
   - Form components
   - Table components with filtering

### Priority 4: Deployment (1 day)
1. **Database Setup**
   - Create database on PlanetScale/Railway
   - Run Alembic migrations
   - Create initial admin user

2. **Backend Deployment (Railway)**
   - Deploy FastAPI + batch jobs
   - Set up environment variables
   - Configure cron jobs

3. **Frontend Deployment (Vercel)**
   - Deploy Next.js app
   - Set up environment variables
   - Configure API proxy to Railway

## 📊 Architecture Summary

### Technology Stack
- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy (async) + Python 3.11+
- **Database**: PostgreSQL (recommended) or MySQL
- **Instagram**: instaloader (read) + instagrapi (write)
- **Deployment**: Vercel (frontend) + Railway (backend + batch)
- **Total Cost**: ~$5-7/month

### Database Tables (8 total)
1. `sns_raise_user` - Service participants
2. `request_by_week` - Weekly link submissions
3. `user_action_verification` - Comment tracking
4. `helper` - Helper Instagram accounts
5. `consumer` - AI comment receivers
6. `producer` - AI comment providers
7. `admin` - Admin users
8. `notice` - Announcements

### API Endpoints (13 total)
**Public (6):**
- GET `/api/py/notices` - Get announcements
- GET `/api/py/requests-by-week` - Get weekly requests (filterable)
- GET `/api/py/user-action-verification` - Get verification data (filterable)
- POST `/api/py/consumer` - Register consumer
- POST `/api/py/producer` - Register producer
- POST `/api/py/unfollow-checker` - Check unfollowers

**Admin (7 - JWT required):**
- POST `/api/py/admin/login` - Admin login
- GET `/api/py/admin/me` - Current admin info
- GET/POST/PUT/DELETE `/api/py/admin/sns-users` - User CRUD
- GET/POST/DELETE `/api/py/admin/helpers` - Helper management

## 🚀 Quick Start Guide

### 1. Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Generate keys
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

### 2. Database Setup
```bash
# Install Alembic
pip install alembic

# Initialize Alembic (if not done)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 3. Create Admin User
```python
# scripts/create_admin.py
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal
from core.models import Admin
from core.security import hash_password

async def create_admin():
    async with AsyncSessionLocal() as session:
        admin = Admin(
            username="admin",
            email="admin@autogram.com",
            password_hash=hash_password("your-password-here"),
            is_superadmin=True
        )
        session.add(admin)
        await session.commit()
        print(f"Admin created: {admin.username}")

asyncio.run(create_admin())
```

### 4. Run FastAPI
```bash
uvicorn api.index:app --reload --port 8000
```

### 5. Run Next.js
```bash
npm install
npm run dev
```

## 📝 Next Steps

1. **Implement Repository Layer** - Start with `api/repositories/`
2. **Implement Service Layer** - Start with `api/services/`
3. **Implement API Routers** - Start with `api/routers/`
4. **Implement Batch Jobs** - Start with `batch/`
5. **Implement Frontend** - Start with `app/`
6. **Deploy** - Railway (backend) + Vercel (frontend)

## 📚 Key Design Decisions

### Why Hybrid Deployment?
- **Vercel Hobby Plan** cannot run:
  - FastAPI with >10s timeout (Instagram scraping takes longer)
  - Scheduled cron jobs (batch processing)
  - Persistent sessions (stateless functions)

- **Railway ($5/mo)** provides:
  - ✅ No timeout limits
  - ✅ Persistent filesystem for sessions
  - ✅ Cron job support
  - ✅ Full FastAPI support

### Why async SQLAlchemy?
- Better performance with async/await
- Matches FastAPI's async nature
- Handles concurrent requests efficiently

### Why instaloader + instagrapi?
- **instaloader**: Stable, reliable for read operations
- **instagrapi**: Better for write operations (comments)
- Both support session management

## ⚠️ Important Notes

1. **Instagram Rate Limiting**: Implement delays between requests
2. **Session Management**: Store encrypted sessions securely
3. **Error Handling**: Instagram APIs can be unreliable
4. **2FA Support**: Handle verification codes for Instagram login
5. **GDPR Compliance**: Handle user data responsibly

## 📞 Support

For questions or issues:
1. Check FastAPI docs: https://fastapi.tiangolo.com
2. Check Next.js docs: https://nextjs.org/docs
3. Check SQLAlchemy docs: https://docs.sqlalchemy.org
4. Check Railway docs: https://docs.railway.app
5. Check Vercel docs: https://vercel.com/docs

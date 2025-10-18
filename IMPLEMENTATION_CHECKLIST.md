# Autogram Implementation Checklist

## Phase 1: Project Setup

### 1.1 Directory Structure
- [ ] Create all directories as specified in architecture
- [ ] Set up `__init__.py` files in all Python packages
- [ ] Create `.env.example` file
- [ ] Set up `.gitignore` for Python project

### 1.2 Dependencies
- [ ] Update `requirements.txt` with all dependencies
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Set up `pyproject.toml` for project metadata

### 1.3 Configuration
- [ ] Create `api/config.py` with Settings class
- [ ] Set up environment variables
- [ ] Generate SECRET_KEY and ENCRYPTION_KEY
- [ ] Configure database connection string

### 1.4 Database Setup
- [ ] Initialize Alembic: `alembic init alembic`
- [ ] Configure `alembic/env.py` for async engine
- [ ] Create `api/db/base.py` with Base class
- [ ] Create `api/db/session.py` with session management

## Phase 2: Core Infrastructure

### 2.1 Database Models
- [ ] Create `api/db/models/sns_raise_user.py`
- [ ] Create `api/db/models/request_by_week.py`
- [ ] Create `api/db/models/user_action_verification.py`
- [ ] Create `api/db/models/helper.py`
- [ ] Create `api/db/models/consumer.py`
- [ ] Create `api/db/models/producer.py`
- [ ] Create `api/db/models/admin.py`
- [ ] Import all models in `api/db/models/__init__.py`

### 2.2 Initial Migration
- [ ] Run `alembic revision --autogenerate -m "Initial migration"`
- [ ] Review generated migration
- [ ] Run `alembic upgrade head`
- [ ] Verify all tables created

### 2.3 Security & Auth
- [ ] Create `api/core/security.py` with JWT functions
- [ ] Create `api/core/exceptions.py` with custom exceptions
- [ ] Create `api/core/middleware.py` with error handlers
- [ ] Create `api/core/logging.py` for logging config

### 2.4 Dependencies
- [ ] Create `api/dependencies.py` with `get_db()`
- [ ] Add `get_current_admin()` dependency
- [ ] Add OAuth2 scheme configuration

## Phase 3: Pydantic Schemas

### 3.1 Common Schemas
- [ ] Create `api/schemas/common.py` (PaginatedResponse, etc.)
- [ ] Create `api/schemas/auth.py` (Token, AdminResponse)

### 3.2 Entity Schemas
- [ ] Create `api/schemas/sns_raise_user.py`
- [ ] Create `api/schemas/request_by_week.py`
- [ ] Create `api/schemas/user_action_verification.py`
- [ ] Create `api/schemas/helper.py`
- [ ] Create `api/schemas/consumer.py`
- [ ] Create `api/schemas/producer.py`
- [ ] Create `api/schemas/admin.py`
- [ ] Create `api/schemas/notice.py`
- [ ] Create `api/schemas/unfollow_checker.py`

## Phase 4: Repository Layer

### 4.1 Base Repository
- [ ] Create `api/db/repositories/base.py` with BaseRepository

### 4.2 Entity Repositories
- [ ] Create `api/db/repositories/sns_raise_user_db.py`
- [ ] Create `api/db/repositories/request_by_week_db.py`
- [ ] Create `api/db/repositories/user_action_verification_db.py`
- [ ] Create `api/db/repositories/helper_db.py`
- [ ] Create `api/db/repositories/consumer_db.py`
- [ ] Create `api/db/repositories/producer_db.py`
- [ ] Create `api/db/repositories/admin_db.py`
- [ ] Create `api/db/repositories/notice_db.py`

## Phase 5: Instagram Integration

### 5.1 Integration Clients
- [ ] Create `api/integrations/__init__.py`
- [ ] Create `api/integrations/instaloader_client.py`
- [ ] Create `api/integrations/instagrapi_client.py`
- [ ] Test Instaloader login and session save
- [ ] Test Instagrapi login and session save

### 5.2 Session Directories
- [ ] Create session storage directories
- [ ] Set proper permissions
- [ ] Add to `.gitignore`

## Phase 6: Service Layer

### 6.1 Core Services
- [ ] Create `api/services/auth_service.py`
- [ ] Create `api/services/instagram_service.py`
- [ ] Create `api/services/notice_service.py`

### 6.2 Entity Services
- [ ] Create `api/services/sns_raise_user_service.py`
- [ ] Create `api/services/request_by_week_service.py`
- [ ] Create `api/services/user_action_verification_service.py`
- [ ] Create `api/services/helper_service.py`
- [ ] Create `api/services/consumer_service.py`
- [ ] Create `api/services/producer_service.py`
- [ ] Create `api/services/unfollow_checker_service.py`

## Phase 7: API Routes - Admin

### 7.1 Admin Auth
- [ ] Create `api/routers/admin/__init__.py`
- [ ] Create `api/routers/admin/auth.py`
- [ ] Implement POST `/api/admin/login`
- [ ] Implement GET `/api/admin/me`
- [ ] Test admin authentication flow

### 7.2 SNS Users Admin
- [ ] Create `api/routers/admin/sns_users.py`
- [ ] Implement GET `/api/admin/sns-users`
- [ ] Implement POST `/api/admin/sns-users`
- [ ] Implement PUT `/api/admin/sns-users/{id}`
- [ ] Implement DELETE `/api/admin/sns-users/{id}`
- [ ] Test all CRUD operations

### 7.3 Helpers Admin
- [ ] Create `api/routers/admin/helpers.py`
- [ ] Implement GET `/api/admin/helpers`
- [ ] Implement POST `/api/admin/helpers` (with Instagram login)
- [ ] Implement DELETE `/api/admin/helpers/{id}`
- [ ] Test helper registration and session save

## Phase 8: API Routes - Public

### 8.1 Public Router Setup
- [ ] Create `api/routers/public/__init__.py`

### 8.2 Notice Endpoints
- [ ] Create `api/routers/public/notices.py`
- [ ] Implement GET `/api/notices`
- [ ] Test notice retrieval

### 8.3 Requests By Week
- [ ] Create `api/routers/public/requests_by_week.py`
- [ ] Implement GET `/api/requests-by-week`
- [ ] Add filtering by username, week, year
- [ ] Add pagination
- [ ] Test all filter combinations

### 8.4 User Action Verification
- [ ] Create `api/routers/public/user_action_verification.py`
- [ ] Implement GET `/api/user-action-verification`
- [ ] Add filtering by username, verification status
- [ ] Add pagination
- [ ] Test all filter combinations

### 8.5 Consumer Registration
- [ ] Create `api/routers/public/consumer.py`
- [ ] Implement POST `/api/consumer`
- [ ] Add validation
- [ ] Test consumer registration

### 8.6 Producer Registration
- [ ] Create `api/routers/public/producer.py`
- [ ] Implement POST `/api/producer`
- [ ] Add Instagram credential verification
- [ ] Add verification code validation
- [ ] Test producer registration flow

### 8.7 Unfollow Checker
- [ ] Create `api/routers/public/unfollow_checker.py`
- [ ] Implement POST `/api/unfollow-checker`
- [ ] Integrate Instaloader for follower/following retrieval
- [ ] Calculate unfollowers
- [ ] Test with real Instagram account

## Phase 9: Main App Configuration

### 9.1 Update Main App
- [ ] Update `api/index.py` with all routers
- [ ] Add CORS middleware
- [ ] Add exception handlers
- [ ] Configure OpenAPI documentation
- [ ] Add startup/shutdown events

### 9.2 Middleware Setup
- [ ] Add CORS configuration
- [ ] Add request logging middleware
- [ ] Add error handling middleware
- [ ] Add rate limiting (optional)

## Phase 10: Testing

### 10.1 Test Infrastructure
- [ ] Create `tests/conftest.py` with fixtures
- [ ] Set up test database
- [ ] Create test client fixture
- [ ] Create test data factories

### 10.2 Unit Tests
- [ ] Test all repository methods
- [ ] Test all service methods
- [ ] Test authentication logic
- [ ] Test Instagram client wrappers
- [ ] Test password encryption/decryption

### 10.3 Integration Tests
- [ ] Test all admin endpoints
- [ ] Test all public endpoints
- [ ] Test authentication flow
- [ ] Test error handling
- [ ] Test validation errors

### 10.4 Instagram Tests
- [ ] Test Instaloader integration (mocked)
- [ ] Test Instagrapi integration (mocked)
- [ ] Test session management
- [ ] Test helper rotation
- [ ] Test rate limiting

## Phase 11: Batch Jobs

### 11.1 Batch Infrastructure
- [ ] Create shared utilities in `core/`
- [ ] Set up batch job configuration

### 11.2 Batch Jobs
- [ ] Create `batch/weekly_verification_check.py`
- [ ] Create `batch/ai_comment_generator.py`
- [ ] Add scheduling mechanism (cron or scheduler)
- [ ] Test batch job execution

## Phase 12: Documentation

### 12.1 API Documentation
- [ ] Review auto-generated OpenAPI docs
- [ ] Add detailed descriptions to all endpoints
- [ ] Add example requests/responses
- [ ] Document authentication flow

### 12.2 Code Documentation
- [ ] Add docstrings to all functions
- [ ] Add type hints everywhere
- [ ] Document complex business logic
- [ ] Create README for each major module

### 12.3 Deployment Documentation
- [ ] Document environment setup
- [ ] Document database migration process
- [ ] Document secrets management
- [ ] Create deployment checklist

## Phase 13: Production Preparation

### 13.1 Security Audit
- [ ] Review all authentication logic
- [ ] Check password storage
- [ ] Verify JWT configuration
- [ ] Review CORS settings
- [ ] Check rate limiting

### 13.2 Performance Optimization
- [ ] Add database indexes
- [ ] Optimize slow queries
- [ ] Configure connection pooling
- [ ] Add caching where appropriate
- [ ] Load test critical endpoints

### 13.3 Monitoring & Logging
- [ ] Set up structured logging
- [ ] Add request ID tracking
- [ ] Configure error tracking (Sentry, etc.)
- [ ] Set up metrics collection
- [ ] Create health check endpoint

### 13.4 Database Preparation
- [ ] Run all migrations
- [ ] Create initial admin user
- [ ] Seed any required data
- [ ] Backup database
- [ ] Test rollback procedures

## Phase 14: Deployment

### 14.1 Environment Setup
- [ ] Set up production environment
- [ ] Configure environment variables
- [ ] Set up database connection
- [ ] Configure secrets
- [ ] Set up SSL/TLS

### 14.2 Application Deployment
- [ ] Deploy FastAPI application
- [ ] Configure Uvicorn/Gunicorn
- [ ] Set up reverse proxy (Nginx)
- [ ] Configure process manager (systemd/supervisor)
- [ ] Test deployment

### 14.3 Post-Deployment
- [ ] Smoke test all endpoints
- [ ] Monitor logs for errors
- [ ] Check performance metrics
- [ ] Verify Instagram integrations
- [ ] Document any issues

## Phase 15: Maintenance

### 15.1 Monitoring
- [ ] Set up alerts for errors
- [ ] Monitor API response times
- [ ] Track Instagram rate limits
- [ ] Monitor database performance
- [ ] Track user registrations

### 15.2 Regular Tasks
- [ ] Review and rotate logs
- [ ] Update dependencies
- [ ] Review security advisories
- [ ] Backup database regularly
- [ ] Monitor Instagram API changes

---

## Quick Start Commands

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your configuration

# 4. Generate encryption keys
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 5. Initialize database
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# 6. Create admin user (run Python script)
python scripts/create_admin.py

# 7. Run development server
uvicorn api.index:app --reload --port 8000

# 8. Run tests
pytest

# 9. Check API docs
# Open http://localhost:8000/api/py/docs
```

---

## Critical Path (Minimum Viable Product)

If you need to prioritize, implement in this order:

1. **Core Infrastructure** (Phase 1-2): Database, models, auth
2. **Admin Auth** (Phase 7.1): Admin login system
3. **SNS Users Admin** (Phase 7.2): User management
4. **Public APIs** (Phase 8.2-8.4): Notices, requests, verification
5. **Instagram Integration** (Phase 5): Basic Instaloader/Instagrapi
6. **Testing** (Phase 10.1-10.2): Basic unit tests

This gives you a working system with:
- Admin panel for user management
- Public APIs for data retrieval
- Basic Instagram integration
- Essential test coverage

Then iterate with remaining features:
- Consumer/Producer registration
- Unfollow checker
- Helper account management
- Batch jobs
- Production deployment

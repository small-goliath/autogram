# Autogram FastAPI Backend

This is the FastAPI backend for the Autogram Instagram comment exchange service.

## Architecture Overview

The backend follows a layered architecture:

```
Router Layer (HTTP) → Service Layer (Business Logic) → Repository Layer (Data Access) → Database
                           ↓
                   Instagram Integration Layer
```

### Directory Structure

```
api/
├── core/              # Core utilities (security, exceptions, middleware)
├── db/                # Database layer (models, repositories, session)
├── schemas/           # Pydantic models for request/response validation
├── services/          # Business logic (*_service.py pattern)
├── integrations/      # External API integrations (Instagram)
├── routers/           # API endpoint handlers
│   ├── public/        # Public APIs (no auth required)
│   └── admin/         # Admin APIs (JWT auth required)
├── config.py          # Application configuration
├── dependencies.py    # FastAPI dependencies (DB, auth, etc.)
└── index.py           # Main FastAPI application
```

## Key Principles

1. **Business logic goes in `*_service.py` files**
2. **Database access logic goes in `*_db.py` files**
3. **All database operations use SQLAlchemy async**
4. **Pydantic for all data validation**
5. **JWT authentication for admin routes**
6. **Type hints everywhere**

## Getting Started

### Prerequisites

- Python 3.13+
- PostgreSQL 14+
- Virtual environment

### Installation

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# venv\Scripts\activate  # On Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 4. Generate security keys
python scripts/generate_keys.py
# Copy the generated keys to .env

# 5. Set up database
createdb autogram  # Create PostgreSQL database

# 6. Initialize Alembic (first time only)
alembic init alembic

# 7. Configure Alembic
# Edit alembic/env.py to import Base and set sqlalchemy.url

# 8. Create initial migration
alembic revision --autogenerate -m "Initial migration"

# 9. Apply migrations
alembic upgrade head

# 10. Create admin user
python scripts/create_admin.py

# 11. Run development server
uvicorn api.index:app --reload --port 8000
```

### Verify Installation

```bash
# Test database connection
python scripts/test_db_connection.py

# Test API endpoints
python scripts/test_api.py

# View API documentation
# Open http://localhost:8000/api/py/docs
```

## API Endpoints

### Public APIs (No Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notices` | Get announcement information |
| GET | `/api/requests-by-week` | Get weekly request data |
| GET | `/api/user-action-verification` | Get verification data |
| POST | `/api/consumer` | Register for AI auto-comments |
| POST | `/api/producer` | Register to provide AI comments |
| POST | `/api/unfollow-checker` | Check who unfollowed you |

### Admin APIs (JWT Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/login` | Admin login (returns JWT) |
| GET | `/api/admin/me` | Get current admin info |
| GET | `/api/admin/sns-users` | List all SNS users |
| POST | `/api/admin/sns-users` | Create SNS user |
| PUT | `/api/admin/sns-users/{id}` | Update SNS user |
| DELETE | `/api/admin/sns-users/{id}` | Delete SNS user |
| GET | `/api/admin/helpers` | List helper accounts |
| POST | `/api/admin/helpers` | Register helper account |
| DELETE | `/api/admin/helpers/{id}` | Delete helper account |

## Authentication

Admin endpoints require JWT authentication:

1. **Login** to get a token:
   ```bash
   curl -X POST "http://localhost:8000/api/admin/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=your_password"
   ```

2. **Use the token** in subsequent requests:
   ```bash
   curl -X GET "http://localhost:8000/api/admin/sns-users" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

## Database Models

### Core Tables

- **sns_raise_user**: Users participating in the service
- **request_by_week**: Weekly link submissions from users
- **user_action_verification**: Tracks pending comment verifications
- **helper**: Helper Instagram accounts for read operations
- **consumer**: Users receiving AI auto-comments
- **producer**: Users providing accounts for AI commenting
- **admin**: Admin users for management panel

### Relationships

- `sns_raise_user` → `request_by_week` (one-to-many)
- `sns_raise_user` → `user_action_verification` (one-to-many)
- `request_by_week` → `user_action_verification` (one-to-many)

## Instagram Integration

### Read Operations (Instaloader)

Used for:
- Viewing posts
- Getting followers/following lists
- Checking unfollowers
- General read-only data

```python
from api.integrations.instaloader_client import InstaloaderClient

client = InstaloaderClient()
await client.login(username, password)
profile = await client.get_profile(username)
followers = await client.get_followers(username)
```

### Write Operations (Instagrapi)

Used for:
- Posting comments
- Liking posts
- Following/unfollowing

```python
from api.integrations.instagrapi_client import InstagrapiClient

client = InstagrapiClient()
await client.login(username, password)
await client.comment_post(post_id, "Great post!")
```

### Session Management

- Helper accounts: Sessions saved in database for reuse
- Producer accounts: Sessions saved after verification
- Session rotation: Helpers rotated to avoid rate limits

## Development

### Adding a New Feature

1. **Create database model** (if needed):
   ```python
   # api/db/models/my_model.py
   ```

2. **Create migration**:
   ```bash
   alembic revision --autogenerate -m "Add my_model"
   alembic upgrade head
   ```

3. **Create repository**:
   ```python
   # api/db/repositories/my_model_db.py
   ```

4. **Create schemas**:
   ```python
   # api/schemas/my_model.py
   ```

5. **Create service**:
   ```python
   # api/services/my_model_service.py
   ```

6. **Create router**:
   ```python
   # api/routers/public/my_route.py or api/routers/admin/my_route.py
   ```

7. **Register router** in `api/index.py`

8. **Write tests**:
   ```python
   # tests/test_api/test_my_route.py
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api tests/

# Run specific test file
pytest tests/test_api/test_sns_users.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black api/ tests/

# Lint code
ruff check api/ tests/

# Type checking
mypy api/
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show migration history
alembic history

# Show current version
alembic current
```

## Environment Variables

Key environment variables (see `.env.example` for full list):

| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection string | Yes |
| SECRET_KEY | JWT secret key (min 32 chars) | Yes |
| ENCRYPTION_KEY | Fernet key for password encryption | Yes |
| CORS_ORIGINS | Allowed frontend origins | Yes |
| INSTALOADER_SESSION_DIR | Directory for Instaloader sessions | No |
| INSTAGRAPI_SESSION_DIR | Directory for Instagrapi sessions | No |

## Logging

Logs are configured in `api/core/logging.py`:

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

Log level is controlled by `LOG_LEVEL` environment variable.

## Error Handling

Custom exceptions are defined in `api/core/exceptions.py`:

- `NotFoundException` (404)
- `DuplicateException` (409)
- `BadRequestException` (400)
- `UnauthorizedException` (401)
- `ForbiddenException` (403)
- `InstagramException` (503)
- `ValidationException` (422)

All exceptions are automatically caught and formatted by global error handlers.

## Performance

### Database

- Connection pooling configured (default: 5 connections)
- Indexes on frequently queried columns
- Async operations for non-blocking I/O

### Instagram

- Request delays between Instagram operations (default: 2 seconds)
- Helper account rotation to distribute load
- Session reuse to avoid repeated logins

### API

- Pagination on all list endpoints
- Efficient database queries (avoid N+1)
- Async/await throughout

## Security

- JWT tokens for admin authentication
- Bcrypt for admin password hashing
- Fernet encryption for Instagram passwords
- CORS protection
- Input validation with Pydantic
- SQL injection protection (SQLAlchemy parameterization)
- Rate limiting (recommended for production)

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Configure proper `CORS_ORIGINS`
- [ ] Set up HTTPS/SSL
- [ ] Configure production database
- [ ] Set up database backups
- [ ] Configure logging to file/service
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configure rate limiting
- [ ] Set up reverse proxy (Nginx)
- [ ] Use process manager (systemd, supervisor)
- [ ] Run migrations
- [ ] Create admin user

### Running in Production

```bash
# Using Gunicorn with Uvicorn workers
gunicorn api.index:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
python scripts/test_db_connection.py

# Check PostgreSQL is running
pg_isready

# Check database exists
psql -l | grep autogram
```

### Instagram Login Issues

- Disable 2FA on Instagram accounts
- Try logging in from the Instagram app first
- Wait if rate limited (24 hours typically)
- Use different helper accounts

### Migration Issues

```bash
# Reset migrations (WARNING: deletes all data)
alembic downgrade base
alembic upgrade head

# Fix conflicts
alembic history
alembic downgrade <previous_version>
# Edit migration file
alembic upgrade head
```

## Documentation

- **Architecture**: `/Users/iymaeng/Documents/private/autogram-latest/ARCHITECTURE.md`
- **Implementation Checklist**: `/Users/iymaeng/Documents/private/autogram-latest/IMPLEMENTATION_CHECKLIST.md`
- **Quick Reference**: `/Users/iymaeng/Documents/private/autogram-latest/QUICK_REFERENCE.md`
- **Example Scripts**: `/Users/iymaeng/Documents/private/autogram-latest/EXAMPLE_SCRIPTS.md`
- **API Docs** (when running): http://localhost:8000/api/py/docs

## Contributing

1. Follow the established patterns (*_service.py, *_db.py)
2. Add type hints to all functions
3. Write docstrings for all public functions
4. Add tests for new features
5. Run linters before committing
6. Update documentation

## License

See LICENSE file in project root.

## Support

For issues and questions:
- Check documentation files
- Review example scripts
- Consult API documentation at `/api/py/docs`
- Check logs for error messages

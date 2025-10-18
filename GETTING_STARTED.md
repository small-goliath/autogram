# Getting Started with Autogram

This guide will help you get the Autogram FastAPI backend up and running quickly.

## Overview

Autogram is an Instagram comment exchange service with:
- **FastAPI Backend** (`api/` directory) - REST API with admin and public endpoints
- **Next.js Frontend** (`app/` directory) - User interface
- **Batch Jobs** (`batch/` directory) - Background processing
- **Shared Logic** (`core/` directory) - Common utilities

## Prerequisites

### Required
- **Python 3.13+** - Check with `python3 --version`
- **PostgreSQL 14+** - Check with `psql --version`
- **Node.js 18+** - Check with `node --version`
- **npm or yarn** - Check with `npm --version`

### Optional (for deployment)
- **Redis** - For caching and rate limiting
- **Docker** - For containerization

## Quick Start (5 Minutes)

### 1. Clone and Navigate

```bash
cd /Users/iymaeng/Documents/private/autogram-latest
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Generate Security Keys

```bash
python scripts/generate_keys.py
```

Copy the output keys to your clipboard.

### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add:
# - DATABASE_URL (your PostgreSQL connection string)
# - SECRET_KEY (from step 3)
# - ENCRYPTION_KEY (from step 3)
nano .env  # or use any text editor
```

### 5. Set Up Database

```bash
# Create database
createdb autogram

# Or using psql
psql -U postgres -c "CREATE DATABASE autogram;"

# Initialize Alembic (first time only)
alembic init alembic

# Configure Alembic (edit alembic.ini and alembic/env.py)
# See detailed instructions in ARCHITECTURE.md

# Create and run migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 6. Create Admin User

```bash
python scripts/create_admin.py
# Enter username and password when prompted
```

### 7. Start the Server

```bash
# Start FastAPI backend
uvicorn api.index:app --reload --port 8000

# In another terminal, start Next.js frontend
npm run next-dev
```

### 8. Verify Installation

Open your browser:
- **API Documentation**: http://localhost:8000/api/py/docs
- **Frontend**: http://localhost:3000

Or run test script:
```bash
python scripts/test_api.py
```

## Detailed Setup Guide

### Database Setup (PostgreSQL)

#### Option 1: Local PostgreSQL

```bash
# Install PostgreSQL (Mac)
brew install postgresql@14
brew services start postgresql@14

# Install PostgreSQL (Ubuntu)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database
createdb autogram

# Create user (optional)
psql -U postgres
postgres=# CREATE USER autogram_user WITH PASSWORD 'your_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE autogram TO autogram_user;
postgres=# \q
```

Your `DATABASE_URL` will be:
```
postgresql+asyncpg://autogram_user:your_password@localhost:5432/autogram
```

#### Option 2: Docker PostgreSQL

```bash
docker run --name autogram-postgres \
  -e POSTGRES_DB=autogram \
  -e POSTGRES_USER=autogram_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -d postgres:14
```

### Alembic Configuration

#### 1. Edit `alembic.ini`

Replace:
```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

With:
```ini
# Comment this out - we'll use env variable instead
# sqlalchemy.url =
```

#### 2. Edit `alembic/env.py`

Add at the top:
```python
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.config import settings
from api.db.base import Base
from api.db.models import *  # Import all models
```

Replace the `config.get_main_option("sqlalchemy.url")` line:
```python
# Use async engine
from sqlalchemy.ext.asyncio import create_async_engine

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

For async support, update the `run_migrations_online()` function:
```python
def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async support"""
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async def do_run_migrations(connection):
        await connection.run_sync(run_migrations)

    asyncio.run(do_run_migrations(connectable))
```

### Environment Variables Explained

```bash
# .env file

# Database - Update with your actual credentials
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/autogram

# Security - Generate using scripts/generate_keys.py
SECRET_KEY=your-32-char-secret-key-here
ENCRYPTION_KEY=your-fernet-key-here

# CORS - Add your frontend URL
CORS_ORIGINS=http://localhost:3000

# Debug mode (set to False in production)
DEBUG=True

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
```

## Testing Your Setup

### 1. Test Database Connection

```bash
python scripts/test_db_connection.py
```

Expected output:
```
✓ Basic query successful
✓ Database version: PostgreSQL 14.x
✓ Found 7 tables:
  - admin
  - consumer
  - helper
  - producer
  - request_by_week
  - sns_raise_user
  - user_action_verification
✓ Database connection successful!
```

### 2. Test Instagram Integration

```bash
# Test read operations (Instaloader)
python scripts/test_instaloader_login.py

# Test write operations (Instagrapi)
python scripts/test_instagrapi_login.py
```

**Important**: Use test Instagram accounts, not your personal account.

### 3. Test API Endpoints

```bash
# Start server first
uvicorn api.index:app --reload --port 8000

# In another terminal
python scripts/test_api.py
```

### 4. Manual API Testing

Using curl:
```bash
# Test public endpoint
curl http://localhost:8000/api/py/helloFastApi

# Login as admin
curl -X POST "http://localhost:8000/api/admin/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your_password"

# Use returned token
export TOKEN="your_jwt_token_here"
curl -X GET "http://localhost:8000/api/admin/me" \
  -H "Authorization: Bearer $TOKEN"
```

## Development Workflow

### Day-to-Day Development

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Pull latest changes (if using git)
git pull

# 3. Install any new dependencies
pip install -r requirements.txt

# 4. Run any new migrations
alembic upgrade head

# 5. Start development servers
# Terminal 1: FastAPI
uvicorn api.index:app --reload --port 8000

# Terminal 2: Next.js
npm run next-dev

# 6. Run tests
pytest

# 7. Format code before committing
black api/ tests/
ruff check api/ tests/ --fix
```

### Adding a New Feature

1. **Plan the feature**: What tables, endpoints, and logic are needed?

2. **Create database model** (if needed):
   ```bash
   # Edit api/db/models/my_model.py
   # Create migration
   alembic revision --autogenerate -m "Add my_model"
   alembic upgrade head
   ```

3. **Create schemas**:
   ```bash
   # Edit api/schemas/my_model.py
   ```

4. **Create repository**:
   ```bash
   # Edit api/db/repositories/my_model_db.py
   ```

5. **Create service**:
   ```bash
   # Edit api/services/my_model_service.py
   ```

6. **Create router**:
   ```bash
   # Edit api/routers/public/my_route.py
   # or api/routers/admin/my_route.py
   ```

7. **Register router** in `api/index.py`

8. **Write tests**:
   ```bash
   # Edit tests/test_api/test_my_route.py
   pytest tests/test_api/test_my_route.py
   ```

9. **Update documentation**

## Common Tasks

### Creating Test Data

```bash
python scripts/seed_database.py
```

### Listing Admin Users

```bash
python scripts/list_admins.py
```

### Cleaning Database

```bash
python scripts/cleanup_database.py
```

### Checking Instagram Rate Limits

```bash
python scripts/check_rate_limits.py
```

### Viewing API Documentation

While server is running:
- **Swagger UI**: http://localhost:8000/api/py/docs
- **ReDoc**: http://localhost:8000/api/py/redoc

### Database Operations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

## Troubleshooting

### "ModuleNotFoundError"

**Problem**: Python can't find modules.

**Solution**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Database does not exist"

**Problem**: PostgreSQL database not created.

**Solution**:
```bash
createdb autogram
# or
psql -U postgres -c "CREATE DATABASE autogram;"
```

### "Connection refused" to database

**Problem**: PostgreSQL not running or wrong connection settings.

**Solution**:
```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL (Mac)
brew services start postgresql@14

# Start PostgreSQL (Ubuntu)
sudo systemctl start postgresql

# Verify connection string in .env
```

### "No module named 'api'"

**Problem**: Running scripts from wrong directory.

**Solution**:
```bash
# Always run scripts from project root
cd /Users/iymaeng/Documents/private/autogram-latest
python scripts/script_name.py
```

### Instagram Login Failed

**Problem**: Can't login to Instagram.

**Solutions**:
- Disable 2FA on Instagram account
- Use a test account, not your personal account
- Wait if rate limited (usually 24 hours)
- Try logging in from Instagram app first
- Check if account is blocked

### "JWT decode error"

**Problem**: Invalid or expired token.

**Solution**:
- Login again to get a new token
- Check SECRET_KEY in .env hasn't changed
- Token expires after 30 minutes (default)

### Port Already in Use

**Problem**: Port 8000 or 3000 already in use.

**Solution**:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn api.index:app --reload --port 8001
```

## Next Steps

### Learn the Architecture

Read these documents in order:

1. **ARCHITECTURE.md** - Complete architecture overview
2. **QUICK_REFERENCE.md** - Code templates and patterns
3. **IMPLEMENTATION_CHECKLIST.md** - Step-by-step implementation guide
4. **EXAMPLE_SCRIPTS.md** - Utility scripts documentation
5. **api/README.md** - API-specific documentation

### Implement Features

Follow the **IMPLEMENTATION_CHECKLIST.md** to build out all features:

1. ✅ Project setup (you just completed this!)
2. ⏭️ Core infrastructure
3. ⏭️ Database models
4. ⏭️ Pydantic schemas
5. ⏭️ Repository layer
6. ⏭️ Service layer
7. ⏭️ API routes
8. ⏭️ Testing
9. ⏭️ Deployment

### Join Development

If working with a team:

```bash
# Initialize git (if not already)
git init

# Add .gitignore
cat > .gitignore << EOF
venv/
__pycache__/
*.pyc
.env
.DS_Store
*.db
*.sqlite3
/tmp/
/instaloader_sessions/
/instagrapi_sessions/
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.mypy_cache/
.ruff_cache/
EOF

# Make first commit
git add .
git commit -m "Initial FastAPI architecture"
```

## Resources

### Documentation
- **Project Docs**: See files in project root
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Alembic Docs**: https://alembic.sqlalchemy.org/

### Tools
- **API Testing**: Swagger UI at http://localhost:8000/api/py/docs
- **Database GUI**: pgAdmin, DBeaver, or DataGrip
- **API Client**: Postman or Insomnia
- **Code Editor**: VS Code with Python extension

### Community
- FastAPI Discord
- SQLAlchemy Google Group
- Stack Overflow

## Summary

You should now have:
- ✅ Virtual environment set up
- ✅ Dependencies installed
- ✅ Database created and migrated
- ✅ Admin user created
- ✅ Development server running
- ✅ API documentation accessible

**API Docs**: http://localhost:8000/api/py/docs
**Frontend**: http://localhost:3000

Ready to start building! 🚀

For detailed architecture and implementation guides, see:
- `ARCHITECTURE.md` - Complete architecture documentation
- `IMPLEMENTATION_CHECKLIST.md` - Step-by-step implementation
- `QUICK_REFERENCE.md` - Code templates and examples
- `EXAMPLE_SCRIPTS.md` - Utility scripts

Happy coding!

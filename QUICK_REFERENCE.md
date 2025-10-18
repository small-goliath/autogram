# Autogram Quick Reference Guide

## Project File Paths

All paths are absolute from project root: `/Users/iymaeng/Documents/private/autogram-latest/`

## Architecture Overview

```
Request Flow:
Client → Router → Service → Repository → Database
                   ↓
              Instagram API
```

## Code Templates

### 1. Creating a New Database Model

```python
# File: api/db/models/my_model.py

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from api.db.base import Base

class MyModel(Base):
    __tablename__ = "my_table"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Add relationships if needed
    # items = relationship("RelatedModel", back_populates="my_model")
```

### 2. Creating a Repository

```python
# File: api/db/repositories/my_model_db.py

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.models.my_model import MyModel
from api.db.repositories.base import BaseRepository

class MyModelRepository(BaseRepository[MyModel]):
    def __init__(self, db: AsyncSession):
        super().__init__(MyModel, db)

    async def get_by_name(self, name: str) -> Optional[MyModel]:
        result = await self.db.execute(
            select(MyModel).where(MyModel.name == name)
        )
        return result.scalar_one_or_none()

    async def get_active(self) -> List[MyModel]:
        result = await self.db.execute(
            select(MyModel).where(MyModel.is_active == True)
        )
        return list(result.scalars().all())
```

### 3. Creating Pydantic Schemas

```python
# File: api/schemas/my_model.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class MyModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

class MyModelCreate(MyModelBase):
    pass

class MyModelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)

class MyModelResponse(MyModelBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
```

### 4. Creating a Service

```python
# File: api/services/my_model_service.py

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.repositories.my_model_db import MyModelRepository
from api.schemas.my_model import MyModelCreate, MyModelUpdate, MyModelResponse
from api.core.exceptions import NotFoundException, DuplicateException

class MyModelService:
    def __init__(self, db: AsyncSession):
        self.repository = MyModelRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[MyModelResponse]:
        items = await self.repository.get_all(skip=skip, limit=limit)
        return [MyModelResponse.model_validate(item) for item in items]

    async def get_by_id(self, item_id: int) -> MyModelResponse:
        item = await self.repository.get_by_id(item_id)
        if not item:
            raise NotFoundException(f"Item with id {item_id} not found")
        return MyModelResponse.model_validate(item)

    async def create(self, data: MyModelCreate) -> MyModelResponse:
        # Check for duplicates
        existing = await self.repository.get_by_name(data.name)
        if existing:
            raise DuplicateException(f"Item with name {data.name} already exists")

        item = await self.repository.create(data.model_dump())
        return MyModelResponse.model_validate(item)

    async def update(self, item_id: int, data: MyModelUpdate) -> MyModelResponse:
        item = await self.repository.get_by_id(item_id)
        if not item:
            raise NotFoundException(f"Item with id {item_id} not found")

        updated = await self.repository.update(item_id, data.model_dump(exclude_unset=True))
        return MyModelResponse.model_validate(updated)

    async def delete(self, item_id: int) -> bool:
        item = await self.repository.get_by_id(item_id)
        if not item:
            raise NotFoundException(f"Item with id {item_id} not found")
        return await self.repository.delete(item_id)
```

### 5. Creating a Public Router

```python
# File: api/routers/public/my_route.py

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from api.services.my_model_service import MyModelService
from api.schemas.my_model import MyModelCreate, MyModelResponse
from api.schemas.common import PaginatedResponse

router = APIRouter(prefix="/my-route", tags=["my-route"])

@router.get("", response_model=PaginatedResponse[MyModelResponse])
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Get all items with pagination"""
    service = MyModelService(db)
    items = await service.get_all(skip=skip, limit=limit)
    return PaginatedResponse(
        items=items,
        total=len(items),
        skip=skip,
        limit=limit
    )

@router.get("/{item_id}", response_model=MyModelResponse)
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get item by ID"""
    service = MyModelService(db)
    return await service.get_by_id(item_id)

@router.post("", response_model=MyModelResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: MyModelCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new item"""
    service = MyModelService(db)
    return await service.create(data)
```

### 6. Creating an Admin Router

```python
# File: api/routers/admin/my_route.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_admin
from api.services.my_model_service import MyModelService
from api.schemas.my_model import MyModelCreate, MyModelUpdate, MyModelResponse
from api.schemas.common import PaginatedResponse

router = APIRouter(prefix="/my-route", tags=["admin-my-route"])

@router.get("", response_model=PaginatedResponse[MyModelResponse])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """List all items (admin only)"""
    service = MyModelService(db)
    items = await service.get_all(skip=skip, limit=limit)
    return PaginatedResponse(
        items=items,
        total=len(items),
        skip=skip,
        limit=limit
    )

@router.post("", response_model=MyModelResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: MyModelCreate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Create item (admin only)"""
    service = MyModelService(db)
    return await service.create(data)

@router.put("/{item_id}", response_model=MyModelResponse)
async def update_item(
    item_id: int,
    data: MyModelUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Update item (admin only)"""
    service = MyModelService(db)
    return await service.update(item_id, data)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Delete item (admin only)"""
    service = MyModelService(db)
    await service.delete(item_id)
```

### 7. Creating a Database Migration

```bash
# After modifying models, create migration
alembic revision --autogenerate -m "Add my_table"

# Review the generated migration file in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### 8. Writing Tests

```python
# File: tests/test_api/test_my_route.py

import pytest
from httpx import AsyncClient
from api.index import app

@pytest.mark.asyncio
async def test_create_item(async_client: AsyncClient, test_db):
    """Test creating an item"""
    response = await async_client.post(
        "/api/my-route",
        json={"name": "Test Item"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_items(async_client: AsyncClient, test_db):
    """Test getting items"""
    response = await async_client.get("/api/my-route")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

@pytest.mark.asyncio
async def test_admin_access_without_token(async_client: AsyncClient):
    """Test admin endpoint without authentication"""
    response = await async_client.post(
        "/api/admin/my-route",
        json={"name": "Test"}
    )
    assert response.status_code == 401
```

## Common Patterns

### Async Database Query

```python
# Single result
result = await self.db.execute(
    select(Model).where(Model.id == id)
)
item = result.scalar_one_or_none()

# Multiple results
result = await self.db.execute(
    select(Model).where(Model.is_active == True)
)
items = list(result.scalars().all())

# With joins
result = await self.db.execute(
    select(Model)
    .join(RelatedModel)
    .where(Model.status == "active")
)

# Count
from sqlalchemy import func
result = await self.db.execute(
    select(func.count(Model.id))
)
count = result.scalar()
```

### Exception Handling

```python
from api.core.exceptions import NotFoundException, DuplicateException

# In service
async def get_item(self, item_id: int):
    item = await self.repository.get_by_id(item_id)
    if not item:
        raise NotFoundException(f"Item {item_id} not found")
    return item

# In router (automatic handling)
@router.get("/{item_id}")
async def get_item(item_id: int):
    service = MyService(db)
    return await service.get_item(item_id)  # 404 if not found
```

### Pagination

```python
# In repository
async def get_all_paginated(
    self,
    skip: int = 0,
    limit: int = 100
) -> tuple[List[Model], int]:
    # Get total count
    count_result = await self.db.execute(
        select(func.count(Model.id))
    )
    total = count_result.scalar()

    # Get paginated results
    result = await self.db.execute(
        select(Model).offset(skip).limit(limit)
    )
    items = list(result.scalars().all())

    return items, total

# In service
async def get_all(self, skip: int, limit: int):
    items, total = await self.repository.get_all_paginated(skip, limit)
    return {
        "items": [MyModelResponse.model_validate(item) for item in items],
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

### Instagram Operations

```python
# Using helper account
async def read_instagram_data(self, username: str):
    service = InstagramService(self.db)
    client = await service.get_helper_client()
    return await client.get_profile(username)

# Using producer account
async def write_comment(self, producer_id: int, post_id: str, text: str):
    producer = await self.producer_repo.get_by_id(producer_id)
    if not producer or not producer.session_data:
        raise ValidationException("Invalid producer")

    client = InstagrapiClient()
    await client.load_session(producer.session_data)
    return await client.comment_post(post_id, text)
```

## Environment Variables

```bash
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
SECRET_KEY=your-secret-key-min-32-chars
ENCRYPTION_KEY=your-fernet-key

# Optional with defaults
DEBUG=False
ACCESS_TOKEN_EXPIRE_MINUTES=30
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
```

## Useful Commands

```bash
# Development server
uvicorn api.index:app --reload --port 8000

# Run tests
pytest
pytest -v  # verbose
pytest tests/test_api/  # specific directory
pytest -k "test_admin"  # specific test pattern

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
alembic history
alembic current

# Create admin user (create this script)
python scripts/create_admin.py

# Check installed packages
pip list
pip freeze > requirements.txt

# Format code (install black first)
black api/ tests/

# Type checking (install mypy first)
mypy api/

# Linting (install ruff first)
ruff check api/ tests/
```

## API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/api/py/docs
- **ReDoc**: http://localhost:8000/api/py/redoc
- **OpenAPI JSON**: http://localhost:8000/api/py/openapi.json

## Debugging Tips

### Enable SQL Echo

```python
# In config.py
DB_ECHO = True  # Logs all SQL queries
```

### Add Debug Logging

```python
import logging
logger = logging.getLogger(__name__)

# In your code
logger.debug(f"Processing item: {item_id}")
logger.info(f"Created item: {item.id}")
logger.warning(f"Suspicious activity: {user_id}")
logger.error(f"Failed to process: {error}")
```

### Test Database Connection

```python
# Create a test script: scripts/test_db.py
import asyncio
from api.db.session import AsyncSessionLocal

async def test_connection():
    async with AsyncSessionLocal() as session:
        result = await session.execute("SELECT 1")
        print("Database connection successful!")

if __name__ == "__main__":
    asyncio.run(test_connection())
```

### Test Instagram Connection

```python
# Create a test script: scripts/test_instagram.py
import asyncio
from api.integrations.instaloader_client import InstaloaderClient

async def test_instaloader():
    client = InstaloaderClient()
    try:
        await client.login("username", "password")
        print("Instaloader login successful!")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_instaloader())
```

## Security Checklist

- [ ] Never commit `.env` file
- [ ] Use strong SECRET_KEY (min 32 characters)
- [ ] Use proper ENCRYPTION_KEY (Fernet.generate_key())
- [ ] Enable HTTPS in production
- [ ] Set proper CORS_ORIGINS (not "*" in production)
- [ ] Use environment variables for all secrets
- [ ] Encrypt Instagram passwords with Fernet
- [ ] Hash admin passwords with bcrypt
- [ ] Validate all user inputs with Pydantic
- [ ] Implement rate limiting for public endpoints
- [ ] Add request timeouts
- [ ] Log security events
- [ ] Regularly update dependencies
- [ ] Use SQL parameterization (SQLAlchemy does this)
- [ ] Implement proper session management

## Performance Tips

1. **Use database indexes** on frequently queried columns
2. **Use pagination** for all list endpoints
3. **Use select_in_loading** for relationships to avoid N+1
4. **Cache frequently accessed data** (Redis)
5. **Use connection pooling** (already configured)
6. **Add database query logging** in development to identify slow queries
7. **Use async operations** everywhere
8. **Batch Instagram operations** to avoid rate limits
9. **Implement caching** for Instagram data
10. **Monitor query performance** with tools like pgAdmin or DataGrip

## Common Issues & Solutions

### Issue: "RuntimeError: Event loop is closed"
**Solution**: Make sure all async functions use `await` and are called within async context.

### Issue: "asyncpg.exceptions.InvalidCatalogNameError"
**Solution**: Create the database first: `createdb autogram`

### Issue: "ModuleNotFoundError"
**Solution**: Activate virtual environment: `source venv/bin/activate`

### Issue: "Instagram login failed"
**Solution**: Check credentials, ensure no 2FA, try different account, check rate limits.

### Issue: "JWT decode error"
**Solution**: Verify SECRET_KEY is consistent and tokens haven't expired.

### Issue: "CORS error from frontend"
**Solution**: Add frontend URL to CORS_ORIGINS in .env

### Issue: "Database connection pool exhausted"
**Solution**: Increase DB_POOL_SIZE or fix connection leaks (ensure proper session cleanup).

## Project Structure Summary

```
api/
├── core/           # Security, exceptions, middleware, logging
├── db/             # Models, repositories, session management
├── schemas/        # Pydantic models for validation
├── services/       # Business logic (*_service.py)
├── integrations/   # External APIs (Instagram)
├── routers/        # API endpoints (public/ and admin/)
└── index.py        # Main FastAPI app

batch/              # Scheduled jobs
core/               # Shared utilities
tests/              # Test suite
```

---

**Quick Tip**: Always start from the data model, then build repository → service → router → tests.

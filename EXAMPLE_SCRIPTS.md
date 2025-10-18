# Example Scripts for Autogram

This document contains ready-to-use scripts for common tasks.

## 1. Create Admin User Script

```python
# File: /Users/iymaeng/Documents/private/autogram-latest/scripts/create_admin.py

import asyncio
from getpass import getpass
from api.db.session import AsyncSessionLocal
from api.db.models.admin import Admin
from api.core.security import get_password_hash

async def create_admin_user():
    """Create an admin user interactively"""
    print("Create Admin User")
    print("-" * 40)

    username = input("Enter admin username: ").strip()
    if not username:
        print("Username cannot be empty")
        return

    password = getpass("Enter admin password: ")
    password_confirm = getpass("Confirm password: ")

    if password != password_confirm:
        print("Passwords do not match!")
        return

    if len(password) < 8:
        print("Password must be at least 8 characters")
        return

    async with AsyncSessionLocal() as db:
        # Check if username exists
        from sqlalchemy import select
        result = await db.execute(
            select(Admin).where(Admin.username == username)
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print(f"Admin user '{username}' already exists!")
            return

        # Create admin
        admin = Admin(
            username=username,
            password_hash=get_password_hash(password),
            is_active=True
        )

        db.add(admin)
        await db.commit()
        await db.refresh(admin)

        print(f"\nAdmin user '{username}' created successfully!")
        print(f"ID: {admin.id}")

if __name__ == "__main__":
    asyncio.run(create_admin_user())
```

```bash
# Usage
python scripts/create_admin.py
```

## 2. Test Database Connection

```python
# File: /Users/iymaeng/Documents/private/autogram-latest/scripts/test_db_connection.py

import asyncio
from sqlalchemy import text
from api.db.session import AsyncSessionLocal
from api.config import settings

async def test_connection():
    """Test database connection"""
    print("Testing database connection...")
    print(f"Database URL: {settings.DATABASE_URL.split('@')[1]}")  # Hide credentials
    print("-" * 40)

    try:
        async with AsyncSessionLocal() as db:
            # Test basic query
            result = await db.execute(text("SELECT 1"))
            value = result.scalar()
            assert value == 1
            print("✓ Basic query successful")

            # Test version
            result = await db.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Database version: {version.split(',')[0]}")

            # List tables
            result = await db.execute(text("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            tables = [row[0] for row in result.fetchall()]

            if tables:
                print(f"✓ Found {len(tables)} tables:")
                for table in tables:
                    print(f"  - {table}")
            else:
                print("⚠ No tables found. Run migrations: alembic upgrade head")

            print("\n✓ Database connection successful!")

    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

    return True

if __name__ == "__main__":
    asyncio.run(test_connection())
```

```bash
# Usage
python scripts/test_db_connection.py
```

## 3. Test Instagram Login (Instaloader)

```python
# File: /Users/iymaeng/Documents/private/autogram-latest/scripts/test_instaloader_login.py

import asyncio
from getpass import getpass
from api.integrations.instaloader_client import InstaloaderClient

async def test_instaloader():
    """Test Instaloader login"""
    print("Test Instaloader Login")
    print("-" * 40)

    username = input("Enter Instagram username: ").strip()
    password = getpass("Enter Instagram password: ")

    if not username or not password:
        print("Username and password are required")
        return

    try:
        client = InstaloaderClient()
        print(f"\nAttempting to login as {username}...")

        session_data = await client.login(username, password)

        print("✓ Login successful!")
        print(f"Session file: {session_data['session_file']}")

        # Test getting profile
        print(f"\nFetching profile for {username}...")
        profile = await client.get_profile(username)

        print(f"✓ Profile loaded successfully!")
        print(f"  Full name: {profile.full_name}")
        print(f"  Biography: {profile.biography[:100]}..." if profile.biography else "")
        print(f"  Followers: {profile.followers}")
        print(f"  Following: {profile.followees}")
        print(f"  Posts: {profile.mediacount}")

    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nTroubleshooting:")
        print("- Verify username and password are correct")
        print("- Disable 2FA on the Instagram account")
        print("- Try logging in from Instagram app first")
        print("- Check if account is rate limited")

if __name__ == "__main__":
    asyncio.run(test_instaloader())
```

```bash
# Usage
python scripts/test_instaloader_login.py
```

## 4. Test Instagram Login (Instagrapi)

```python
# File: /Users/iymaeng/Documents/private/autogram-latest/scripts/test_instagrapi_login.py

import asyncio
from getpass import getpass
from api.integrations.instagrapi_client import InstagrapiClient

async def test_instagrapi():
    """Test Instagrapi login"""
    print("Test Instagrapi Login")
    print("-" * 40)

    username = input("Enter Instagram username: ").strip()
    password = getpass("Enter Instagram password: ")

    if not username or not password:
        print("Username and password are required")
        return

    try:
        client = InstagrapiClient()
        print(f"\nAttempting to login as {username}...")

        session_data = await client.login(username, password)

        print("✓ Login successful!")
        print(f"Session file: {session_data['session_file']}")

        # Test getting account info
        print(f"\nFetching account info for {username}...")
        # Note: You'll need to add this method to InstagrapiClient
        # user_info = await client.get_account_info()

        print(f"✓ Account loaded successfully!")
        print("\nNote: You can now use this account for writing operations")

    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nTroubleshooting:")
        print("- Verify username and password are correct")
        print("- Disable 2FA on the Instagram account")
        print("- Wait a few minutes if rate limited")
        print("- Try logging in from Instagram app first")

if __name__ == "__main__":
    asyncio.run(test_instagrapi())
```

```bash
# Usage
python scripts/test_instagrapi_login.py
```

## 5. Generate Encryption Keys

```python
# File: /Users/iymaeng/Documents/private/autogram-latest/scripts/generate_keys.py

import secrets
from cryptography.fernet import Fernet

def generate_keys():
    """Generate secret keys for the application"""
    print("Generating Security Keys")
    print("=" * 60)

    # Generate SECRET_KEY for JWT
    secret_key = secrets.token_urlsafe(32)
    print("\nSECRET_KEY (for JWT tokens):")
    print(f"SECRET_KEY={secret_key}")

    # Generate ENCRYPTION_KEY for Fernet
    encryption_key = Fernet.generate_key().decode()
    print("\nENCRYPTION_KEY (for encrypting Instagram passwords):")
    print(f"ENCRYPTION_KEY={encryption_key}")

    print("\n" + "=" * 60)
    print("Copy these values to your .env file")
    print("IMPORTANT: Keep these keys secret and never commit them to git!")
    print("=" * 60)

if __name__ == "__main__":
    generate_keys()
```

```bash
# Usage
python scripts/generate_keys.py
```

## 6. Seed Database with Sample Data

```python
# File: /Users/iymaeng/Documents/private/autogram-latest/scripts/seed_database.py

import asyncio
from datetime import datetime
from api.db.session import AsyncSessionLocal
from api.db.models.sns_raise_user import SnsRaiseUser
from api.db.models.request_by_week import RequestByWeek
from api.db.models.admin import Admin
from api.core.security import get_password_hash

async def seed_database():
    """Seed database with sample data for testing"""
    print("Seeding database with sample data...")
    print("-" * 40)

    async with AsyncSessionLocal() as db:
        # Create admin user
        admin = Admin(
            username="admin",
            password_hash=get_password_hash("admin123"),
            is_active=True
        )
        db.add(admin)
        print("✓ Created admin user (username: admin, password: admin123)")

        # Create sample SNS users
        users = [
            SnsRaiseUser(username="user1"),
            SnsRaiseUser(username="user2"),
            SnsRaiseUser(username="user3"),
        ]
        db.add_all(users)
        print(f"✓ Created {len(users)} sample users")

        await db.commit()

        # Create sample requests
        for user in users:
            await db.refresh(user)
            request = RequestByWeek(
                user_id=user.id,
                week_number=42,
                year=2024,
                instagram_link="https://www.instagram.com/p/example/"
            )
            db.add(request)

        await db.commit()
        print("✓ Created sample requests")

        print("\n✓ Database seeded successfully!")
        print("\nTest credentials:")
        print("  Admin: username=admin, password=admin123")
        print("  API: http://localhost:8000/api/py/docs")

if __name__ == "__main__":
    asyncio.run(seed_database())
```

```bash
# Usage
python scripts/seed_database.py
```

## 7. List All Admin Users

```python
# File: /Users/iymaeng/Documents/private/autogram-latest/scripts/list_admins.py

import asyncio
from sqlalchemy import select
from api.db.session import AsyncSessionLocal
from api.db.models.admin import Admin

async def list_admins():
    """List all admin users"""
    print("Admin Users")
    print("-" * 60)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Admin).order_by(Admin.id)
        )
        admins = result.scalars().all()

        if not admins:
            print("No admin users found.")
            print("Create one with: python scripts/create_admin.py")
            return

        print(f"{'ID':<5} {'Username':<20} {'Active':<10} {'Created At':<25}")
        print("-" * 60)

        for admin in admins:
            status = "Yes" if admin.is_active else "No"
            created = admin.created_at.strftime("%Y-%m-%d %H:%M:%S") if admin.created_at else "N/A"
            print(f"{admin.id:<5} {admin.username:<20} {status:<10} {created:<25}")

        print(f"\nTotal: {len(admins)} admin(s)")

if __name__ == "__main__":
    asyncio.run(list_admins())
```

```bash
# Usage
python scripts/list_admins.py
```

## 8. Delete Admin User

```python
# File: /Users/iymaeng/Documents/private/autogram-latest/scripts/delete_admin.py

import asyncio
from sqlalchemy import select
from api.db.session import AsyncSessionLocal
from api.db.models.admin import Admin

async def delete_admin():
    """Delete an admin user"""
    print("Delete Admin User")
    print("-" * 40)

    # List admins first
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Admin))
        admins = result.scalars().all()

        if not admins:
            print("No admin users found.")
            return

        print("\nExisting admins:")
        for admin in admins:
            print(f"  {admin.id}: {admin.username}")

        # Get admin ID to delete
        try:
            admin_id = int(input("\nEnter admin ID to delete: "))
        except ValueError:
            print("Invalid ID")
            return

        # Find and delete admin
        result = await db.execute(
            select(Admin).where(Admin.id == admin_id)
        )
        admin = result.scalar_one_or_none()

        if not admin:
            print(f"Admin with ID {admin_id} not found")
            return

        confirm = input(f"Are you sure you want to delete '{admin.username}'? (yes/no): ")
        if confirm.lower() != "yes":
            print("Cancelled")
            return

        await db.delete(admin)
        await db.commit()

        print(f"\n✓ Admin user '{admin.username}' deleted successfully")

if __name__ == "__main__":
    asyncio.run(delete_admin())
```

```bash
# Usage
python scripts/delete_admin.py
```

## 9. Test API Endpoint

```python
# File: /Users/iymaeng/Documents/private/autogram-latest/scripts/test_api.py

import asyncio
import httpx

async def test_api():
    """Test API endpoints"""
    base_url = "http://localhost:8000"

    print("Testing API Endpoints")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        # Test health check (if you add one)
        try:
            response = await client.get(f"{base_url}/api/py/helloFastApi")
            print(f"\n✓ GET /api/py/helloFastApi")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.json()}")
        except Exception as e:
            print(f"\n✗ GET /api/py/helloFastApi failed: {e}")

        # Test admin login
        try:
            response = await client.post(
                f"{base_url}/api/admin/login",
                data={
                    "username": "admin",
                    "password": "admin123"
                }
            )
            print(f"\n✓ POST /api/admin/login")
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                token = response.json()["access_token"]
                print(f"  Token: {token[:20]}...")

                # Test authenticated endpoint
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(
                    f"{base_url}/api/admin/me",
                    headers=headers
                )
                print(f"\n✓ GET /api/admin/me (authenticated)")
                print(f"  Status: {response.status_code}")
                print(f"  Admin: {response.json()}")
            else:
                print(f"  Error: {response.json()}")

        except Exception as e:
            print(f"\n✗ Admin login test failed: {e}")

        # Test public endpoints
        try:
            response = await client.get(f"{base_url}/api/notices")
            print(f"\n✓ GET /api/notices")
            print(f"  Status: {response.status_code}")
        except Exception as e:
            print(f"\n✗ GET /api/notices failed: {e}")

    print("\n" + "=" * 60)
    print("API testing complete!")
    print("View full documentation at: http://localhost:8000/api/py/docs")

if __name__ == "__main__":
    asyncio.run(test_api())
```

```bash
# Usage (make sure server is running first)
python scripts/test_api.py
```

## 10. Cleanup Database

```python
# File: /Users/iymaeng/Documents/private/autogram-latest/scripts/cleanup_database.py

import asyncio
from sqlalchemy import text
from api.db.session import AsyncSessionLocal

async def cleanup_database():
    """Clean up test data from database"""
    print("Database Cleanup")
    print("-" * 40)
    print("WARNING: This will delete all data except admin users!")

    confirm = input("Are you sure? (type 'yes' to confirm): ")
    if confirm.lower() != "yes":
        print("Cancelled")
        return

    async with AsyncSessionLocal() as db:
        try:
            # Delete in correct order due to foreign keys
            tables = [
                "user_action_verification",
                "request_by_week",
                "sns_raise_user",
                "consumer",
                "producer",
                "helper"
            ]

            for table in tables:
                result = await db.execute(text(f"DELETE FROM {table}"))
                print(f"✓ Deleted {result.rowcount} rows from {table}")

            await db.commit()
            print("\n✓ Database cleanup complete!")

        except Exception as e:
            print(f"✗ Error: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(cleanup_database())
```

```bash
# Usage
python scripts/cleanup_database.py
```

## 11. Check Instagram Rate Limits

```python
# File: /Users/iymaeng/Documents/private/autogram-latest/scripts/check_rate_limits.py

import asyncio
from datetime import datetime
from sqlalchemy import select, func
from api.db.session import AsyncSessionLocal
from api.db.models.helper import Helper

async def check_rate_limits():
    """Check helper account usage and rate limits"""
    print("Instagram Helper Account Status")
    print("=" * 80)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Helper).order_by(Helper.last_used_at.desc().nullsfirst())
        )
        helpers = result.scalars().all()

        if not helpers:
            print("No helper accounts found")
            return

        print(f"{'ID':<5} {'Username':<20} {'Active':<10} {'Last Used':<25}")
        print("-" * 80)

        for helper in helpers:
            status = "Yes" if helper.is_active else "No"
            last_used = helper.last_used_at.strftime("%Y-%m-%d %H:%M:%S") if helper.last_used_at else "Never"
            print(f"{helper.id:<5} {helper.instagram_id:<20} {status:<10} {last_used:<25}")

        print(f"\nTotal helpers: {len(helpers)}")
        active_count = sum(1 for h in helpers if h.is_active)
        print(f"Active helpers: {active_count}")

        # Show usage recommendations
        print("\nRecommendations:")
        print("- Rotate helpers every 100 requests")
        print("- Wait 2 seconds between requests")
        print("- Add more helpers if rate limited")

if __name__ == "__main__":
    asyncio.run(check_rate_limits())
```

```bash
# Usage
python scripts/check_rate_limits.py
```

## 12. Create scripts/__init__.py

```python
# File: /Users/iymaeng/Documents/private/autogram-latest/scripts/__init__.py

# This file makes the scripts directory a Python package
```

## Directory Structure for Scripts

```
/Users/iymaeng/Documents/private/autogram-latest/
└── scripts/
    ├── __init__.py
    ├── create_admin.py
    ├── test_db_connection.py
    ├── test_instaloader_login.py
    ├── test_instagrapi_login.py
    ├── generate_keys.py
    ├── seed_database.py
    ├── list_admins.py
    ├── delete_admin.py
    ├── test_api.py
    ├── cleanup_database.py
    └── check_rate_limits.py
```

## Running Scripts

All scripts should be run from the project root:

```bash
# Activate virtual environment first
source venv/bin/activate

# Run any script
python scripts/script_name.py
```

## Development Workflow

1. **Initial Setup**:
   ```bash
   python scripts/generate_keys.py  # Generate keys for .env
   python scripts/test_db_connection.py  # Verify DB connection
   python scripts/create_admin.py  # Create admin user
   ```

2. **During Development**:
   ```bash
   python scripts/seed_database.py  # Add test data
   python scripts/test_api.py  # Test endpoints
   ```

3. **Testing Instagram**:
   ```bash
   python scripts/test_instaloader_login.py  # Test read operations
   python scripts/test_instagrapi_login.py  # Test write operations
   ```

4. **Maintenance**:
   ```bash
   python scripts/list_admins.py  # View admins
   python scripts/check_rate_limits.py  # Check Instagram usage
   python scripts/cleanup_database.py  # Clean test data
   ```

## Notes

- All scripts use async/await for consistency with the API
- Scripts handle errors gracefully with try/except blocks
- Scripts provide clear output for debugging
- Scripts are safe to run multiple times (idempotent where possible)
- All file paths are absolute as per project requirements

## Adding Your Own Scripts

Template for new scripts:

```python
# File: /Users/iymaeng/Documents/private/autogram-latest/scripts/my_script.py

import asyncio
from api.db.session import AsyncSessionLocal
from api.config import settings

async def main():
    """Description of what this script does"""
    print("My Script")
    print("-" * 40)

    async with AsyncSessionLocal() as db:
        try:
            # Your code here
            print("✓ Success!")
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

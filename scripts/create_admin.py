"""Script to create an admin user."""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import AsyncSessionLocal
from core.models import Admin
from core.security import hash_password


async def create_admin(username: str, email: str, password: str, is_superadmin: bool = True):
    """Create an admin user."""
    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        from sqlalchemy import select
        result = await session.execute(
            select(Admin).where(Admin.username == username)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"❌ Admin user '{username}' already exists")
            return

        # Create new admin
        admin = Admin(
            username=username,
            email=email,
            password_hash=hash_password(password),
            is_active=True,
            is_superadmin=is_superadmin
        )

        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        print(f"✅ Admin user created successfully!")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Superadmin: {admin.is_superadmin}")


if __name__ == "__main__":
    import getpass

    print("=" * 50)
    print("Create Admin User")
    print("=" * 50)

    username = input("Username: ")
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    password_confirm = getpass.getpass("Confirm Password: ")

    if password != password_confirm:
        print("❌ Passwords do not match")
        sys.exit(1)

    if len(password) < 8:
        print("❌ Password must be at least 8 characters")
        sys.exit(1)

    asyncio.run(create_admin(username, email, password))

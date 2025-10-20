"""Setup database and create admin account."""
import asyncio
import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_migrations():
    """Run Alembic migrations."""
    print("=" * 50)
    print("Running Database Migrations")
    print("=" * 50)

    result = subprocess.run(
        ["python", "-m", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    if result.returncode != 0:
        print(f"❌ Migration failed with code {result.returncode}")
        return False

    print("✅ Migrations completed successfully")
    return True


async def create_admin():
    """Create admin account."""
    print("\n" + "=" * 50)
    print("Creating Admin Account")
    print("=" * 50)

    from core.database import AsyncSessionLocal
    from core.models import Admin
    from core.security import hash_password
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        # Check if admin exists
        result = await db.execute(
            select(Admin).where(Admin.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("ℹ️  Admin account already exists")
            print(f"   Username: admin")
            return True

        # Create admin
        admin = Admin(
            username="admin",
            hashed_password=hash_password("admin123!@#"),
            is_active=True
        )

        db.add(admin)
        await db.commit()

        print("✅ Admin account created successfully")
        print(f"   Username: admin")
        print(f"   Password: admin123!@#")
        print("\n⚠️  Please change the password after first login!")
        return True


async def main():
    """Run all setup tasks."""
    print("=" * 50)
    print("Database Setup Script")
    print("=" * 50)

    try:
        # Run migrations
        if not run_migrations():
            sys.exit(1)

        # Create admin account
        if not await create_admin():
            sys.exit(1)

        print("\n" + "=" * 50)
        print("✅ Database setup completed successfully!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

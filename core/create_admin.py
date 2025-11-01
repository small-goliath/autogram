import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from passlib.context import CryptContext
from datetime import datetime

# Import models
from core.models import Admin
from core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if admin already exists
        result = await session.execute(
            select(Admin).where(Admin.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("Admin user 'admin' already exists!")
            return

        # Create new admin
        hashed_password = pwd_context.hash("admin1234")
        admin = Admin(
            username="admin",
            password=hashed_password
        )

        session.add(admin)
        await session.commit()
        print(f"✅ Admin created successfully!")
        print(f"   Username: admin")
        print(f"   Password: admin1234")

if __name__ == "__main__":
    asyncio.run(create_admin())

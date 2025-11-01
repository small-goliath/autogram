"""
Utility script to create an admin account.
Usage: python scripts/create_admin.py
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.database import get_session_maker
from core.crypto import hash_password
from core.db import admin_db


async def create_admin_account(username: str, password: str):
    """Create an admin account."""
    session_maker = get_session_maker()
    async with session_maker() as db:
        try:
            # Check if admin already exists
            existing = await admin_db.get_admin_by_username(db, username)
            if existing:
                print(f"Error: Admin '{username}' already exists!")
                return

            # Hash password
            hashed_password = hash_password(password)

            # Create admin
            admin = await admin_db.create_admin(db, username, hashed_password)
            await db.commit()

            print(f"Successfully created admin account:")
            print(f"  Username: {admin.username}")
            print(f"  ID: {admin.id}")
            print(f"  Created: {admin.created_at}")

        except Exception as e:
            await db.rollback()
            print(f"Error creating admin: {str(e)}")


def main():
    """Main function."""
    print("=== Create Admin Account ===\n")

    username = input("Enter admin username: ").strip()
    if not username:
        print("Username cannot be empty!")
        return

    password = input("Enter admin password (min 8 characters): ").strip()
    if len(password) < 8:
        print("Password must be at least 8 characters!")
        return

    confirm_password = input("Confirm password: ").strip()
    if password != confirm_password:
        print("Passwords do not match!")
        return

    # Run async function
    asyncio.run(create_admin_account(username, password))


if __name__ == "__main__":
    main()

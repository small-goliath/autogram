"""Test batch jobs with manual data."""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import AsyncSessionLocal
from core.models import SnsRaiseUser, RequestByWeek
from sqlalchemy import select


async def create_test_users():
    """Create test SNS users."""
    print("\n" + "=" * 50)
    print("Creating Test SNS Users")
    print("=" * 50)

    async with AsyncSessionLocal() as db:
        # Check if users exist
        result = await db.execute(select(SnsRaiseUser))
        existing = result.scalars().all()

        if existing:
            print(f"✅ Found {len(existing)} existing users:")
            for user in existing:
                print(f"   - {user.username} (@{user.instagram_id})")
            return

        # Create test users
        test_users = [
            SnsRaiseUser(
                username="유경식",
                instagram_id="gangggi_e_you",
                email="test1@example.com",
                is_active=True
            ),
            SnsRaiseUser(
                username="이유성",
                instagram_id="luckybellaaa",
                email="test2@example.com",
                is_active=True
            ),
            SnsRaiseUser(
                username="팽유미",
                instagram_id="pink.yoom",
                email="test3@example.com",
                is_active=True
            ),
        ]

        for user in test_users:
            db.add(user)

        await db.commit()
        print(f"✅ Created {len(test_users)} test users")


async def create_test_requests():
    """Create test weekly requests."""
    print("\n" + "=" * 50)
    print("Creating Test Weekly Requests")
    print("=" * 50)

    async with AsyncSessionLocal() as db:
        # Get users
        result = await db.execute(select(SnsRaiseUser))
        users = result.scalars().all()

        if not users:
            print("❌ No users found. Run create_test_users first.")
            return

        # Check existing requests
        result = await db.execute(select(RequestByWeek))
        existing = result.scalars().all()

        if existing:
            print(f"✅ Found {len(existing)} existing requests:")
            for req in existing:
                print(f"   - {req.username}: {req.instagram_link}")
            return

        # Create test requests for last week
        today = datetime.now()
        last_monday = today - timedelta(days=today.weekday() + 7)
        last_sunday = last_monday + timedelta(days=6)

        test_requests = [
            RequestByWeek(
                user_id=users[0].id,
                instagram_link="https://www.instagram.com/p/test123/",
                request_date=last_monday,
                week_start_date=last_monday,
                week_end_date=last_sunday,
                status="pending",
                comment_count=0
            ),
            RequestByWeek(
                user_id=users[1].id,
                instagram_link="https://www.instagram.com/p/test456/",
                request_date=last_monday + timedelta(days=1),
                week_start_date=last_monday,
                week_end_date=last_sunday,
                status="pending",
                comment_count=0
            ),
        ]

        for req in test_requests:
            db.add(req)

        await db.commit()
        print(f"✅ Created {len(test_requests)} test requests")
        print(f"   Week: {last_monday.date()} ~ {last_sunday.date()}")


async def verify_data():
    """Verify test data in database."""
    print("\n" + "=" * 50)
    print("Verifying Data in Supabase")
    print("=" * 50)

    async with AsyncSessionLocal() as db:
        # Count users
        result = await db.execute(select(SnsRaiseUser))
        users = result.scalars().all()
        print(f"\n👥 SNS Users: {len(users)}")
        for user in users:
            print(f"   - {user.username} (@{user.instagram_id}) - Active: {user.is_active}")

        # Count requests
        result = await db.execute(select(RequestByWeek))
        requests = result.scalars().all()
        print(f"\n📋 Weekly Requests: {len(requests)}")
        for req in requests:
            user = await db.get(SnsRaiseUser, req.user_id)
            print(f"   - {user.username if user else 'Unknown'}: {req.instagram_link}")
            print(f"     Status: {req.status}, Comments: {req.comment_count}")


async def main():
    """Run all tests."""
    print("=" * 50)
    print("Batch Jobs Test Suite")
    print("=" * 50)

    try:
        await create_test_users()
        await create_test_requests()
        await verify_data()

        print("\n" + "=" * 50)
        print("✅ All Tests Completed Successfully!")
        print("=" * 50)
        print("\n💡 Next steps:")
        print("1. Check Supabase dashboard to verify data")
        print("2. Test actual batch jobs with real KakaoTalk data")
        print("3. Deploy to Railway + Vercel")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

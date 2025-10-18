"""Test Supabase database connection."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from core.database import engine, get_db


async def test_connection():
    """Test database connection and list tables."""
    print("=" * 50)
    print("Testing Supabase Connection")
    print("=" * 50)

    try:
        # Test basic connection
        async with engine.begin() as conn:
            # Get database version
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"\n✅ Connected to PostgreSQL!")
            print(f"📊 Database version: {version[:50]}...")

            # Get current database name
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"🗄️  Database name: {db_name}")

            # List all tables
            result = await conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            tables = result.fetchall()

            if tables:
                print(f"\n📋 Found {len(tables)} tables:")
                for i, (table,) in enumerate(tables, 1):
                    print(f"   {i}. {table}")
            else:
                print("\n⚠️  No tables found. Run migrations first:")
                print("   alembic upgrade head")

            # Test connection pool
            print(f"\n🏊 Connection pool info:")
            print(f"   Pool size: {engine.pool.size()}")
            print(f"   Checked out connections: {engine.pool.checkedout()}")

        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Connection failed!")
        print(f"Error: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("1. Check your DATABASE_URL in .env file")
        print("2. Verify Supabase project is running")
        print("3. Ensure password is correct")
        print("4. Check SUPABASE_SETUP.md for detailed guide")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection())

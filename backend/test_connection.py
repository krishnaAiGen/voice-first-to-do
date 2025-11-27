"""
Test database connection and create tables
Run this first to verify your database configuration
"""

import asyncio
from sqlalchemy import text
from app.clients.database_client import DatabaseClient
from app.models.task import Base

async def test_and_setup():
    """Test database connection and create tables"""
    
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    
    try:
        # Create database client
        db_client = DatabaseClient()
        
        # Test connection
        print("\n1️⃣ Testing connection...")
        async with db_client.async_session_maker() as session:
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected successfully!")
            print(f"   PostgreSQL version: {version}")
        
        # Create tables
        print("\n2️⃣ Creating tables...")
        async with db_client.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Tables created/verified!")
        print("\n📋 Tables in database:")
        for table in Base.metadata.sorted_tables:
            print(f"   - {table.name}")
            for column in table.columns:
                print(f"     • {column.name} ({column.type})")
        
        # Verify table exists
        print("\n3️⃣ Verifying toDoList table...")
        async with db_client.async_session_maker() as session:
            result = await session.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_name = 'toDoList'
            """))
            count = result.scalar()
            
            if count > 0:
                print("✅ toDoList table exists!")
                
                # Count rows
                result = await session.execute(text('SELECT COUNT(*) FROM "toDoList"'))
                row_count = result.scalar()
                print(f"   Current rows: {row_count}")
            else:
                print("❌ toDoList table not found!")
        
        print("\n" + "=" * 60)
        print("✅ Database setup complete!")
        print("=" * 60)
        print("\nYou can now start the backend server:")
        print("  uvicorn app.main:app --reload")
        
        await db_client.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your DATABASE_URL in .env file")
        print("   2. Verify your PostgreSQL credentials")
        print("   3. Ensure the database exists")
        print("   4. Check network connectivity to database")
        raise

if __name__ == "__main__":
    asyncio.run(test_and_setup())


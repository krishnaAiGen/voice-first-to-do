"""
Script to create database tables automatically
Run this after setting up your .env file
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.task import Base
from app.core.config import settings

async def create_tables():
    """Create all tables in the database"""
    print("Creating database tables...")
    print(f"Database URL: {settings.database_url.split('@')[1]}")  # Hide credentials
    
    try:
        # Create engine
        engine = create_async_engine(
            settings.database_url,
            echo=True,  # Show SQL statements
        )
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("\n✅ Successfully created all tables!")
        print("Tables created:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_tables())


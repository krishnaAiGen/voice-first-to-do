"""Run database migrations"""

import asyncio
import asyncpg
from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


async def run_migration():
    """Run database migration from SQL file"""
    try:
        # Parse database URL
        db_url = settings.database_url
        # Remove the +asyncpg suffix for asyncpg.connect
        db_url_clean = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        logger.info("Connecting to database...")
        conn = await asyncpg.connect(db_url_clean)
        
        # Read migration SQL file
        logger.info("Reading migration file...")
        with open('migrations/001_add_authentication.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        logger.info("Executing migration...")
        await conn.execute(migration_sql)
        
        logger.info("✅ Migration completed successfully!")
        
        # Close connection
        await conn.close()
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(run_migration())


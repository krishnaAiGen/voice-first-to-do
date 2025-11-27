"""Database client and connection management"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool
from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseClient:
    """Database connection manager"""
    
    def __init__(self, database_url: str = None, create_tables: bool = False):
        """
        Initialize database client
        
        Args:
            database_url: Database URL (defaults to settings)
            create_tables: Whether to auto-create tables on init
        """
        self.database_url = database_url or settings.database_url
        
        # Create async engine with appropriate pool settings
        engine_kwargs = {
            "echo": settings.is_development,
            "pool_pre_ping": True,
        }
        
        # Only add pool settings if not using NullPool
        if settings.is_development:
            engine_kwargs["poolclass"] = NullPool
        else:
            engine_kwargs["pool_size"] = 10
            engine_kwargs["max_overflow"] = 20
        
        self.engine = create_async_engine(
            self.database_url,
            **engine_kwargs
        )
        
        # Create session factory
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        logger.info("Database client initialized")
        
        # Auto-create tables if requested
        if create_tables:
            import asyncio
            from app.models.task import Base
            
            async def _create_tables():
                async with self.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                    logger.info("Database tables created/verified")
            
            try:
                asyncio.create_task(_create_tables())
            except Exception as e:
                logger.warning(f"Could not auto-create tables: {e}")
    
    async def get_session(self) -> AsyncSession:
        """Get a new database session"""
        async with self.async_session_maker() as session:
            return session
    
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()
        logger.info("Database connections closed")


# Global database client instance
db_client = DatabaseClient()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get database session
    
    Yields:
        Database session
    """
    async with db_client.async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


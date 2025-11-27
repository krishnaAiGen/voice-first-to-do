"""User repository for database operations"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class UserRepository:
    """Repository for user database operations"""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize user repository
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def create(self, email: str, hashed_password: str, display_name: Optional[str] = None) -> User:
        """
        Create a new user
        
        Args:
            email: User email (should be lowercase)
            hashed_password: Hashed password
            display_name: Optional display name
        
        Returns:
            Created user
        """
        user = User(
            email=email,
            hashed_password=hashed_password,
            display_name=display_name
        )
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        logger.info(f"Created user: {user.email}")
        return user
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User UUID
        
        Returns:
            User if found, None otherwise
        """
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User email (case-insensitive)
        
        Returns:
            User if found, None otherwise
        """
        query = select(User).where(User.email == email.lower())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def update_last_login(self, user_id: UUID) -> None:
        """
        Update user's last login timestamp
        
        Args:
            user_id: User UUID
        """
        user = await self.get_by_id(user_id)
        if user:
            user.last_login_at = datetime.utcnow()
            await self.session.commit()
            logger.info(f"Updated last login for user: {user.email}")
    
    async def update(self, user_id: UUID, **kwargs) -> Optional[User]:
        """
        Update user fields
        
        Args:
            user_id: User UUID
            **kwargs: Fields to update
        
        Returns:
            Updated user if found, None otherwise
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        await self.session.commit()
        await self.session.refresh(user)
        
        logger.info(f"Updated user: {user.email}")
        return user


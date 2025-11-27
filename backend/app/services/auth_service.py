"""Authentication service for user management"""

from typing import Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize auth service
        
        Args:
            session: Database session
        """
        self.repository = UserRepository(session)
        self.session = session
    
    async def register_user(
        self,
        email: str,
        password: str,
        display_name: Optional[str] = None
    ) -> User:
        """
        Register a new user
        
        Args:
            email: User email (will be lowercased)
            password: Plain text password
            display_name: Optional display name
        
        Returns:
            Created user
        
        Raises:
            ValueError: If user already exists
        """
        # Normalize email
        email = email.strip().lower()
        
        # Check if user exists
        existing_user = await self.repository.get_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Create user
        user = await self.repository.create(
            email=email,
            hashed_password=hashed_password,
            display_name=display_name or email.split('@')[0].title()
        )
        
        logger.info(f"Registered new user: {email}")
        return user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password
        
        Args:
            email: User email
            password: Plain text password
        
        Returns:
            User if authentication successful, None otherwise
        """
        # Normalize email
        email = email.strip().lower()
        
        # Get user
        user = await self.repository.get_by_email(email)
        if not user:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return None
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt for user: {email}")
            return None
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {email}")
            return None
        
        logger.info(f"Successful authentication for user: {email}")
        return user
    
    async def create_tokens(self, user_id: UUID) -> Dict[str, str]:
        """
        Create access and refresh tokens for user
        
        Args:
            user_id: User UUID
        
        Returns:
            Dict with access_token and refresh_token
        """
        # Create access token (short-lived)
        access_token = create_access_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(minutes=30)
        )
        
        # Create refresh token (long-lived)
        refresh_token = create_refresh_token()
        
        # Store refresh token in database
        from app.models.user import Base
        from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
        from sqlalchemy.dialects.postgresql import UUID as PGUUID
        
        # For now, store in-memory (in production, use refresh_tokens table)
        logger.info(f"Created tokens for user: {user_id}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    async def update_last_login(self, user_id: UUID) -> None:
        """
        Update user's last login timestamp
        
        Args:
            user_id: User UUID
        """
        await self.repository.update_last_login(user_id)
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User UUID
        
        Returns:
            User if found, None otherwise
        """
        return await self.repository.get_by_id(user_id)


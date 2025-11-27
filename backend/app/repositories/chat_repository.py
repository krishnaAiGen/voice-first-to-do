"""Chat message repository for database operations"""

from typing import List
from uuid import UUID
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat_message import ChatMessage
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ChatRepository:
    """Repository for chat message database operations"""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize chat repository
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def create(
        self,
        user_id: UUID,
        message_type: str,
        content: str,
        transcript: str = None,
        latency_ms: int = None
    ) -> ChatMessage:
        """
        Create a new chat message
        
        Args:
            user_id: User UUID
            message_type: Type of message (user, assistant, error)
            content: Message content
            transcript: Original voice transcript (optional)
            latency_ms: Response latency (optional)
        
        Returns:
            Created chat message
        """
        message = ChatMessage(
            user_id=user_id,
            message_type=message_type,
            content=content,
            transcript=transcript,
            latency_ms=latency_ms
        )
        
        self.session.add(message)
        await self.session.commit()
        # Removed refresh() - no need to SELECT after INSERT (saves ~3s per message)
        
        logger.debug(f"Created chat message for user {user_id}: {message_type}")
        return message
    
    async def get_history(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatMessage]:
        """
        Get chat history for a user
        
        Args:
            user_id: User UUID
            limit: Maximum number of messages to return
            offset: Offset for pagination
        
        Returns:
            List of chat messages ordered by created_at DESC
        """
        query = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(query)
        messages = result.scalars().all()
        
        # Reverse to get chronological order (oldest first)
        return list(reversed(messages))
    
    async def count_messages(self, user_id: UUID) -> int:
        """
        Count total messages for a user
        
        Args:
            user_id: User UUID
        
        Returns:
            Total message count
        """
        query = select(func.count(ChatMessage.id)).where(ChatMessage.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one()
    
    async def delete_user_history(self, user_id: UUID) -> int:
        """
        Delete all chat history for a user
        
        Args:
            user_id: User UUID
        
        Returns:
            Number of messages deleted
        """
        query = select(ChatMessage).where(ChatMessage.user_id == user_id)
        result = await self.session.execute(query)
        messages = result.scalars().all()
        
        count = len(messages)
        for message in messages:
            await self.session.delete(message)
        
        await self.session.commit()
        logger.info(f"Deleted {count} chat messages for user {user_id}")
        
        return count


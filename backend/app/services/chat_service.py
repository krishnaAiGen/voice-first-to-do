"""Chat service for managing conversation history"""

from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.chat_repository import ChatRepository
from app.models.chat_message import ChatMessage
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ChatService:
    """Service for chat message operations"""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize chat service
        
        Args:
            session: Database session
        """
        self.repository = ChatRepository(session)
    
    async def save_message(
        self,
        user_id: UUID,
        message_type: str,
        content: str,
        transcript: str = None,
        latency_ms: int = None
    ) -> ChatMessage:
        """
        Save a chat message
        
        Args:
            user_id: User UUID
            message_type: Type (user, assistant, error)
            content: Message content
            transcript: Original voice transcript
            latency_ms: Response latency
        
        Returns:
            Saved chat message
        """
        return await self.repository.create(
            user_id=user_id,
            message_type=message_type,
            content=content,
            transcript=transcript,
            latency_ms=latency_ms
        )
    
    async def save_conversation(
        self,
        user_id: UUID,
        user_message: str,
        assistant_message: str,
        transcript: str = None,
        latency_ms: int = None
    ) -> List[ChatMessage]:
        """
        Save a complete conversation (user + assistant messages)
        
        Args:
            user_id: User UUID
            user_message: User's message content
            assistant_message: Assistant's response
            transcript: Original voice transcript
            latency_ms: Response latency
        
        Returns:
            List of saved messages [user_msg, assistant_msg]
        """
        # Save user message
        user_msg = await self.repository.create(
            user_id=user_id,
            message_type="user",
            content=user_message,
            transcript=transcript
        )
        
        # Save assistant message
        assistant_msg = await self.repository.create(
            user_id=user_id,
            message_type="assistant",
            content=assistant_message,
            latency_ms=latency_ms
        )
        
        logger.info(f"Saved conversation for user {user_id}")
        return [user_msg, assistant_msg]
    
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
            limit: Maximum messages to return
            offset: Offset for pagination
        
        Returns:
            List of chat messages
        """
        return await self.repository.get_history(user_id, limit, offset)
    
    async def get_message_count(self, user_id: UUID) -> int:
        """
        Get total message count for a user
        
        Args:
            user_id: User UUID
        
        Returns:
            Total message count
        """
        return await self.repository.count_messages(user_id)
    
    async def clear_history(self, user_id: UUID) -> int:
        """
        Clear all chat history for a user
        
        Args:
            user_id: User UUID
        
        Returns:
            Number of messages deleted
        """
        count = await self.repository.delete_user_history(user_id)
        logger.info(f"Cleared {count} messages for user {user_id}")
        return count


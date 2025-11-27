"""Chat message database model"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from app.models.task import Base


class ChatMessage(Base):
    """Chat message model for storing conversation history"""
    
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    message_type = Column(String(20), nullable=False)  # user, assistant, error
    content = Column(Text, nullable=False)
    transcript = Column(Text, nullable=True)  # Original voice transcript for user messages
    latency_ms = Column(Integer, nullable=True)  # Response time for assistant messages
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    
    __table_args__ = (
        CheckConstraint(
            "message_type IN ('user', 'assistant', 'error')",
            name='check_message_type'
        ),
    )
    
    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, type='{self.message_type}', user_id={self.user_id})>"


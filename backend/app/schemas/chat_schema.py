"""Chat message schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message"""
    
    message_type: str = Field(..., description="Message type: user, assistant, or error")
    content: str = Field(..., description="Message content")
    transcript: Optional[str] = Field(None, description="Original voice transcript (for user messages)")
    latency_ms: Optional[int] = Field(None, description="Response latency (for assistant messages)")


class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    
    id: str
    user_id: str
    message_type: str
    content: str
    transcript: Optional[str]
    latency_ms: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Schema for chat history response"""
    
    messages: List[ChatMessageResponse]
    total: int


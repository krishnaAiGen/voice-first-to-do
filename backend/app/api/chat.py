"""Chat history API endpoints"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.chat_schema import ChatHistoryResponse, ChatMessageResponse
from app.services.chat_service import ChatService
from app.clients.database_client import get_db
from app.dependencies.auth import get_current_user
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    """Dependency to create ChatService"""
    return ChatService(db)


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = 50,
    offset: int = 0,
    user_id: str = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Get chat history for authenticated user
    
    Headers:
        Authorization: Bearer <access_token>
    
    Query params:
        limit: Max messages to return (default: 50)
        offset: Offset for pagination (default: 0)
    
    Response:
    {
        "messages": [
            {
                "id": "uuid",
                "user_id": "uuid",
                "message_type": "user",
                "content": "Show me my tasks",
                "transcript": "Show me my tasks",
                "created_at": "2025-11-26T10:00:00Z"
            },
            {
                "id": "uuid",
                "user_id": "uuid",
                "message_type": "assistant",
                "content": "Here are your tasks...",
                "latency_ms": 7500,
                "created_at": "2025-11-26T10:00:07Z"
            }
        ],
        "total": 42
    }
    """
    try:
        user_uuid = UUID(user_id)
        
        # Get messages
        messages = await chat_service.get_history(user_uuid, limit, offset)
        
        # Get total count
        total = await chat_service.get_message_count(user_uuid)
        
        # Convert to response schema
        message_responses = [
            ChatMessageResponse(
                id=str(msg.id),
                user_id=str(msg.user_id),
                message_type=msg.message_type,
                content=msg.content,
                transcript=msg.transcript,
                latency_ms=msg.latency_ms,
                created_at=msg.created_at
            )
            for msg in messages
        ]
        
        return ChatHistoryResponse(
            messages=message_responses,
            total=total
        )
    
    except Exception as e:
        logger.error(f"Failed to get chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )


@router.delete("/history")
async def clear_chat_history(
    user_id: str = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Clear all chat history for authenticated user
    
    Headers:
        Authorization: Bearer <access_token>
    
    Response:
    {
        "message": "Cleared 42 messages",
        "count": 42
    }
    """
    try:
        user_uuid = UUID(user_id)
        count = await chat_service.clear_history(user_uuid)
        
        return {
            "message": f"Cleared {count} messages",
            "count": count
        }
    
    except Exception as e:
        logger.error(f"Failed to clear chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear chat history"
        )


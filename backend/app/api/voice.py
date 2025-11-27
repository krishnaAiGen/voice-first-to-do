"""Voice API endpoints"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.voice_schema import VoiceCommandRequest, VoiceCommandResponse, ErrorResponse
from app.services.voice_service import VoiceService
from app.services.intent_service import IntentService
from app.services.query_executor import QueryExecutor
from app.services.chat_service import ChatService
from app.clients.deepgram_client import DeepgramClient
from app.clients.gemini_client import GeminiClient
from app.clients.database_client import get_db
from app.repositories.task_repository import TaskRepository
from app.builders.query_builder import SafeQueryBuilder
from app.parsers.intent_parser import IntentParser
from app.dependencies.auth import get_current_user
from app.core.config import settings
from app.utils.logger import setup_logger
from app.utils.errors import VoiceAppException

logger = setup_logger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])


def get_voice_service(db: AsyncSession = Depends(get_db)) -> VoiceService:
    """
    Dependency to create VoiceService with all dependencies
    
    Args:
        db: Database session
    
    Returns:
        VoiceService instance
    """
    # Initialize clients
    deepgram_client = DeepgramClient()
    gemini_client = GeminiClient()
    
    # Initialize parsers and builders
    intent_parser = IntentParser(gemini_client)
    query_builder = SafeQueryBuilder(db)
    
    # Initialize repository
    repository = TaskRepository(db)
    
    # Initialize services
    intent_service = IntentService(intent_parser)
    query_executor = QueryExecutor(repository, query_builder)
    
    # Create voice service
    return VoiceService(
        deepgram_client=deepgram_client,
        intent_service=intent_service,
        query_executor=query_executor
    )


@router.post("/process", response_model=VoiceCommandResponse)
async def process_voice_command(
    request: VoiceCommandRequest,
    user_id: str = Depends(get_current_user),  # Now requires authentication
    voice_service: VoiceService = Depends(get_voice_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Process voice command (PRIMARY ENDPOINT - REQUIRES AUTHENTICATION)
    
    This endpoint:
    1. Transcribes voice → text (STT with Deepgram)
    2. Parses intent → specification (LLM with Gemini)
    3. Executes operation → result (Safe query builder)
    4. Saves conversation to chat history
    5. Returns response
    
    Headers:
        Authorization: Bearer <access_token>
    
    Args:
        request: Voice command request with audio
        user_id: Authenticated user ID from JWT token
        voice_service: Voice service dependency
        db: Database session
    
    Returns:
        VoiceCommandResponse with results
    """
    try:
        logger.info(f"Processing voice command for user: {user_id}")
        
        # Fetch recent chat history for context
        from app.services.chat_service import ChatService
        from app.core.config import settings
        
        chat_service_temp = ChatService(db)
        recent_messages = await chat_service_temp.get_history(
            UUID(user_id),
            limit=settings.conversation_history
        )
        
        # Format chat history for LLM context
        chat_history = [
            {"type": msg.message_type, "content": msg.content}
            for msg in recent_messages
        ]
        
        # Process command with authenticated user and chat history
        result = await voice_service.process_command(
            audio_base64=request.audio_base64,
            user_id=user_id,
            chat_history=chat_history
        )
        
        # Save conversation to chat history
        chat_service = ChatService(db)
        await chat_service.save_conversation(
            user_id=UUID(user_id),
            user_message=result.transcript,
            assistant_message=result.natural_response,
            transcript=result.transcript,
            latency_ms=int(result.latency_ms)
        )
        
        # Convert to response
        return VoiceCommandResponse(
            success=result.success,
            transcript=result.transcript,
            result=result.result,
            natural_response=result.natural_response,
            latency_ms=result.latency_ms
        )
        
    except VoiceAppException as e:
        error_message = str(e.message) if hasattr(e, 'message') else str(e)
        logger.warning(f"Voice command issue: {error_message}")
        
        # Determine if this is a user-friendly error (STT issues) or a system error
        friendly_errors = [
            "No speech detected",
            "audio",
            "recording",
            "microphone"
        ]
        is_friendly_error = any(keyword in error_message.lower() for keyword in friendly_errors)
        
        if is_friendly_error:
            # Return a friendly response instead of throwing error
            friendly_message = "I couldn't hear you clearly. Please try again and speak a bit louder."
            
            # Save friendly message to chat history
            try:
                chat_service = ChatService(db)
                await chat_service.save_message(
                    user_id=UUID(user_id),
                    message_type="assistant",
                    content=friendly_message
                )
            except Exception:
                pass
            
            # Return successful response with friendly message
            return VoiceCommandResponse(
                success=True,
                transcript="",
                result=None,
                natural_response=friendly_message,
                latency_ms=0
            )
        else:
            # For system errors, save to chat but return error
            try:
                chat_service = ChatService(db)
                await chat_service.save_message(
                    user_id=UUID(user_id),
                    message_type="error",
                    content=error_message
                )
            except Exception:
                pass
            
            error_response = ErrorResponse.from_exception(e)
            raise HTTPException(
                status_code=400,
                detail=error_response.model_dump()
            )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        error_response = ErrorResponse(
            error={
                "type": "InternalError",
                "message": "An unexpected error occurred",
                "details": str(e) if settings.is_development else None
            }
        )
        raise HTTPException(
            status_code=500,
            detail=error_response.model_dump()
        )


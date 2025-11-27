"""Voice API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.voice_schema import VoiceCommandRequest, VoiceCommandResponse, ErrorResponse
from app.services.voice_service import VoiceService
from app.services.intent_service import IntentService
from app.services.query_executor import QueryExecutor
from app.clients.deepgram_client import DeepgramClient
from app.clients.gemini_client import GeminiClient
from app.clients.database_client import get_db
from app.repositories.task_repository import TaskRepository
from app.builders.query_builder import SafeQueryBuilder
from app.parsers.intent_parser import IntentParser
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
    voice_service: VoiceService = Depends(get_voice_service)
):
    """
    Process voice command (PRIMARY ENDPOINT)
    
    This endpoint:
    1. Transcribes voice → text (STT with Deepgram)
    2. Parses intent → specification (LLM with Gemini)
    3. Executes operation → result (Safe query builder)
    4. Returns response
    
    Args:
        request: Voice command request with audio
        voice_service: Voice service dependency
    
    Returns:
        VoiceCommandResponse with results
    """
    try:
        logger.info("Processing voice command")
        
        # Get user ID (default for demo)
        user_id = request.user_id or settings.default_user_id
        
        # Process command
        result = await voice_service.process_command(
            audio_base64=request.audio_base64,
            user_id=user_id
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
        logger.error(f"Voice command failed: {e}")
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


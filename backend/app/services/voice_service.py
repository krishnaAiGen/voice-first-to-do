"""Voice service for orchestrating voice command processing"""

import time
from typing import Any
from app.clients.deepgram_client import DeepgramClient
from app.services.intent_service import IntentService
from app.services.query_executor import QueryExecutor
from app.utils.logger import setup_logger
from app.utils.errors import VoiceAppException

logger = setup_logger(__name__)


class VoiceCommandResult:
    """Result of voice command processing"""
    
    def __init__(
        self,
        success: bool,
        transcript: str,
        result: Any,
        natural_response: str,
        latency_ms: float
    ):
        self.success = success
        self.transcript = transcript
        self.result = result
        self.natural_response = natural_response
        self.latency_ms = latency_ms
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "success": self.success,
            "transcript": self.transcript,
            "result": self.result,
            "natural_response": self.natural_response,
            "latency_ms": self.latency_ms
        }


class VoiceService:
    """Orchestrate voice command processing"""
    
    def __init__(
        self,
        deepgram_client: DeepgramClient,
        intent_service: IntentService,
        query_executor: QueryExecutor
    ):
        """
        Initialize voice service
        
        Args:
            deepgram_client: Deepgram client for STT
            intent_service: Intent parsing service
            query_executor: Query executor
        """
        self.deepgram_client = deepgram_client
        self.intent_service = intent_service
        self.query_executor = query_executor
    
    def _get_field(self, obj, field: str, default=None):
        """Helper to get field from dict or object"""
        if isinstance(obj, dict):
            return obj.get(field, default)
        return getattr(obj, field, default)
    
    def _enrich_response(self, base_response: str, data: Any, operation: str = None) -> str:
        """
        Enrich the natural response with actual task data
        
        Args:
            base_response: Base response from LLM
            data: Execution result data (can be list of dicts/objects, single dict/object, etc)
            operation: Operation type (read, create, update, delete)
        
        Returns:
            Enriched natural response with task details
        """
        if not data:
            return base_response
        
        # Handle list of tasks (read operations)
        if isinstance(data, list) and operation == 'read':
            if len(data) == 0:
                return "No tasks found matching your criteria."
            
            # Format task details
            enriched = base_response + "\n\n"
            for task in data[:5]:  # Limit to 5 tasks
                title = self._get_field(task, 'title', 'Untitled')
                status = self._get_field(task, 'status', 'pending').replace('_', ' ').title()
                priority_map = {0: '', 1: '🔵 Low', 2: '🟡 Medium', 3: '🔴 High'}
                priority = priority_map.get(self._get_field(task, 'priority', 0), '')
                
                enriched += f"📋 **{title}**\n"
                if priority:
                    enriched += f"   Priority: {priority}\n"
                enriched += f"   Status: {status}\n"
                
                description = self._get_field(task, 'description')
                if description:
                    desc = description[:100]
                    if len(description) > 100:
                        desc += '...'
                    enriched += f"   {desc}\n"
                
                category = self._get_field(task, 'category')
                if category:
                    enriched += f"   Category: {category}\n"
                
                scheduled_time = self._get_field(task, 'scheduled_time')
                if scheduled_time:
                    from datetime import datetime
                    # Handle both string and datetime objects
                    if isinstance(scheduled_time, str):
                        scheduled = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                    else:
                        scheduled = scheduled_time
                    enriched += f"   Scheduled: {scheduled.strftime('%B %d, %Y at %I:%M %p')}\n"
                
                enriched += "\n"
            
            if len(data) > 5:
                enriched += f"...and {len(data) - 5} more tasks."
            
            return enriched.strip()
        
        # Handle single task (create/update operations)
        elif isinstance(data, dict) or hasattr(data, '__dict__'):
            title = self._get_field(data, 'title', 'Task')
            return f"{base_response}\n\n✅ {title}"
        
        # Handle count or other numeric data
        elif isinstance(data, (int, float)):
            return f"{base_response} (Count: {data})"
        
        return base_response
    
    async def process_command(
        self,
        audio_base64: str,
        user_id: str
    ) -> VoiceCommandResult:
        """
        Process voice command end-to-end
        
        Args:
            audio_base64: Base64-encoded audio data
            user_id: User ID
        
        Returns:
            VoiceCommandResult
        
        Raises:
            VoiceAppException: If processing fails
        """
        start_time = time.time()
        
        try:
            # Step 1: Speech to Text
            logger.info("Step 1: Transcribing audio")
            transcript = await self.deepgram_client.transcribe(audio_base64)
            logger.info(f"Transcript: {transcript}")
            
            # Step 2: Parse Intent
            logger.info("Step 2: Parsing intent")
            intent_result = await self.intent_service.parse_intent(
                transcript,
                user_id
            )
            logger.info(f"Intent result: {intent_result}")
            
            # Step 3: Execute Query
            logger.info("Step 3: Executing query")
            execution_result = await self.query_executor.execute(
                intent_result.specification,
                user_id
            )
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            logger.info(f"Total latency: {latency_ms:.2f}ms")
            
            # Handle failure cases with friendly messages
            if not execution_result.success:
                error_message = execution_result.message or "I was not able to complete this task."
                
                # Make error messages more user-friendly
                if "No tasks found" in error_message:
                    friendly_error = (
                        "I couldn't find any tasks matching your description. "
                        "Try being more specific or check if the task exists in your list."
                    )
                elif "required" in error_message.lower():
                    friendly_error = (
                        "I was not able to complete this task. "
                        "Please try again with more details."
                    )
                else:
                    friendly_error = f"I was not able to complete this task. {error_message}"
                
                return VoiceCommandResult(
                    success=False,
                    transcript=transcript,
                    result=None,
                    natural_response=friendly_error,
                    latency_ms=latency_ms
                )
            
            # Enrich natural response with actual data for successful operations
            natural_response = intent_result.specification.natural_response
            if execution_result.success and execution_result.data:
                natural_response = self._enrich_response(
                    natural_response,
                    execution_result.data,
                    intent_result.specification.steps[0].operation if intent_result.specification.steps else None
                )
            
            return VoiceCommandResult(
                success=execution_result.success,
                transcript=transcript,
                result=execution_result.data,
                natural_response=natural_response,
                latency_ms=latency_ms
            )
            
        except VoiceAppException:
            raise
        except Exception as e:
            logger.error(f"Voice command processing failed: {e}")
            raise VoiceAppException(
                "Failed to process voice command",
                details=str(e)
            )


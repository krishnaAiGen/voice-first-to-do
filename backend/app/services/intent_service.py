"""Intent service for parsing user commands"""

from typing import Dict, Any, Optional
from datetime import datetime
from app.parsers.intent_parser import IntentParser
from app.models.query_spec import IntentResult
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class IntentService:
    """Service for parsing user intents"""
    
    def __init__(self, intent_parser: IntentParser):
        """
        Initialize intent service
        
        Args:
            intent_parser: Intent parser instance
        """
        self.intent_parser = intent_parser
    
    async def parse_intent(
        self,
        command: str,
        user_id: str,
        timezone: str = "UTC"
    ) -> IntentResult:
        """
        Parse user command into intent
        
        Args:
            command: User command text
            user_id: User ID
            timezone: User timezone
        
        Returns:
            IntentResult with specification
        """
        logger.info(f"Parsing intent for command: {command}")
        
        # Build user context
        user_context = {
            "user_id": user_id,
            "timezone": timezone,
            "current_datetime": datetime.now().isoformat()
        }
        
        # Parse with LLM
        intent_result = await self.intent_parser.parse(command, user_context)
        logger.info(f"Intent parsed: {intent_result.specification.complexity}")
        return intent_result


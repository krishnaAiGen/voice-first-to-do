"""Google Gemini client for LLM operations"""

import json
from typing import Optional
import google.generativeai as genai
from app.core.config import settings
from app.utils.logger import setup_logger
from app.utils.errors import IntentParsingException

logger = setup_logger(__name__)


class GeminiClient:
    """Wrapper for Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google API key (defaults to settings)
        """
        self.api_key = api_key or settings.google_api_key
        genai.configure(api_key=self.api_key)
        
        # Use Gemini 2.5 Flash for speed
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def generate_intent(self, prompt: str) -> dict:
        """
        Generate intent specification from prompt
        
        Args:
            prompt: Complete prompt with user command
        
        Returns:
            Parsed JSON response as dictionary
        
        Raises:
            IntentParsingException: If generation or parsing fails
        """
        try:
            logger.info("Generating intent with Gemini")
            
            # Configure for JSON output
            generation_config = {
                "temperature": 0.1,  # Low temperature for consistent parsing
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract text
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            try:
                intent_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {response_text}")
                raise IntentParsingException(
                    "Failed to parse LLM response as JSON",
                    details=f"JSON error: {str(e)}\nResponse: {response_text}"
                )
            
            logger.info(f"Intent generated successfully: {intent_data.get('complexity', 'unknown')}")
            return intent_data
            
        except IntentParsingException:
            raise
        except Exception as e:
            logger.error(f"Gemini generation failed: {str(e)}")
            raise IntentParsingException(
                "Failed to generate intent with LLM",
                details=str(e)
            )


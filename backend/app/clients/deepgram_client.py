"""Deepgram client for speech-to-text"""

import base64
from typing import Optional
from deepgram import DeepgramClient as DGClient
from deepgram.core.api_error import ApiError

from app.core.config import settings
from app.utils.logger import setup_logger
from app.utils.errors import STTException

logger = setup_logger(__name__)


class DeepgramClient:
    """Wrapper for Deepgram API (SDK v5+)"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Deepgram client
        
        Args:
            api_key: Deepgram API key (defaults to settings)
        """
        self.api_key = api_key or settings.deepgram_api_key
        self.client = DGClient(api_key=self.api_key)
    
    async def transcribe(self, audio_base64: str) -> str:
        """
        Transcribe audio to text using Deepgram Nova-2
        Uses Deepgram SDK v5+ API structure
        
        Args:
            audio_base64: Base64-encoded audio data
        
        Returns:
            Transcribed text
        
        Raises:
            STTException: If transcription fails
        """
        try:
            logger.info("Starting Deepgram transcription")
            
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_base64)
            
            # Use Deepgram SDK v5+ API structure
            # Based on: client.listen.v1.media.transcribe_file(request=audio_bytes, model="nova-2")
            response = self.client.listen.v1.media.transcribe_file(
                request=audio_bytes,
                model="nova-2",
                smart_format=True,
                punctuate=True,
                language="en",
            )
            
            # Extract transcript from response
            # SDK v5+ returns an object with .results attribute
            if hasattr(response, 'results'):
                transcript = response.results.channels[0].alternatives[0].transcript
            else:
                raise STTException(
                    "Unexpected response format from Deepgram",
                    details=f"Response type: {type(response)}"
                )
            
            if not transcript:
                raise STTException(
                    "No speech detected in audio",
                    details="Deepgram returned empty transcript"
                )
            
            # Log with green color for success
            print(f"\033[92m✓ Transcription: {transcript}\033[0m")
            logger.info(f"Transcription successful: {transcript}")
            return transcript
            
        except ApiError as e:
            logger.error(f"Deepgram API error: Status {e.status_code}, {e.body}")
            raise STTException(
                f"Deepgram API error (Status {e.status_code})",
                details=str(e.body)
            )
        except STTException:
            raise
        except Exception as e:
            logger.error(f"Deepgram transcription failed: {str(e)}")
            raise STTException(
                "Failed to transcribe audio",
                details=str(e)
            )


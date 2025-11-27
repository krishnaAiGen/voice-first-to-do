"""Pydantic schemas for Voice API"""

from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


class VoiceCommandRequest(BaseModel):
    """Request schema for voice command processing"""
    
    audio_base64: str = Field(..., description="Base64-encoded audio data")
    user_id: Optional[str] = None  # Optional, falls back to default


class VoiceCommandResponse(BaseModel):
    """Response schema for voice command processing"""
    
    success: bool
    transcript: str
    result: Any  # Can be list of tasks, confirmation, etc.
    natural_response: str
    latency_ms: Optional[float] = None
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response schema"""
    
    success: bool = False
    error: Dict[str, Any]
    
    @classmethod
    def from_exception(
        cls,
        exc: Exception,
        suggestions: Optional[List[str]] = None
    ) -> "ErrorResponse":
        """Create error response from exception"""
        error_dict = {
            "type": exc.__class__.__name__,
            "message": str(exc),
            "details": getattr(exc, "details", None),
        }
        
        if suggestions:
            error_dict["suggestions"] = suggestions
        elif hasattr(exc, "suggestions"):
            error_dict["suggestions"] = exc.suggestions
        
        return cls(error=error_dict)


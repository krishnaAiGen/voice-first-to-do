"""Custom exception classes"""

from typing import List, Optional


class VoiceAppException(Exception):
    """Base exception for the application"""
    
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class STTException(VoiceAppException):
    """Speech-to-text processing errors"""
    pass


class IntentParsingException(VoiceAppException):
    """Intent parsing errors"""
    
    def __init__(
        self,
        message: str,
        details: Optional[str] = None,
        suggestions: Optional[List[str]] = None
    ):
        super().__init__(message, details)
        self.suggestions = suggestions or [
            "Try saying 'Show me all tasks'",
            "Try saying 'Create a task to buy groceries'"
        ]


class QueryValidationException(VoiceAppException):
    """Query validation errors"""
    pass


class TaskNotFoundException(VoiceAppException):
    """Task not found error"""
    pass


class UnauthorizedException(VoiceAppException):
    """User not authorized error"""
    pass


class DatabaseException(VoiceAppException):
    """Database operation errors"""
    pass


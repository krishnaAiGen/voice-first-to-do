"""Base operation interface"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID


class OperationResult:
    """Result of an operation"""
    
    def __init__(self, success: bool, data: Any = None, message: str = ""):
        self.success = success
        self.data = data
        self.message = message
    
    def __repr__(self) -> str:
        return f"<OperationResult(success={self.success}, message='{self.message}')>"


class BaseOperation(ABC):
    """Abstract base class for all operations"""
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any], user_id: UUID) -> OperationResult:
        """
        Execute the operation
        
        Args:
            params: Operation parameters
            user_id: User ID
        
        Returns:
            OperationResult
        """
        pass
    
    @abstractmethod
    def validate(self, params: Dict[str, Any]) -> bool:
        """
        Validate operation parameters
        
        Args:
            params: Operation parameters
        
        Returns:
            True if valid
        
        Raises:
            QueryValidationException: If validation fails
        """
        pass


"""Delete operation"""

from typing import Dict, Any
from uuid import UUID
from app.operations.base_operation import BaseOperation, OperationResult
from app.repositories.task_repository import TaskRepository
from app.utils.logger import setup_logger
from app.utils.errors import QueryValidationException, TaskNotFoundException

logger = setup_logger(__name__)


class DeleteOperation(BaseOperation):
    """Delete a task"""
    
    def __init__(self, repository: TaskRepository):
        """
        Initialize delete operation
        
        Args:
            repository: Task repository
        """
        self.repository = repository
    
    def validate(self, params: Dict[str, Any]) -> bool:
        """
        Validate delete parameters
        
        Args:
            params: Parameters with 'task_id'
        
        Returns:
            True if valid
        
        Raises:
            QueryValidationException: If validation fails
        """
        if not params.get("task_id"):
            raise QueryValidationException(
                "Task ID is required for delete",
                details="params must include 'task_id' field"
            )
        
        return True
    
    async def execute(self, params: Dict[str, Any], user_id: UUID) -> OperationResult:
        """
        Execute delete operation
        
        Args:
            params: Delete parameters including task_id
            user_id: User ID
        
        Returns:
            OperationResult
        """
        try:
            # Validate
            self.validate(params)
            
            # Extract task_id
            task_id = UUID(params["task_id"])
            
            # Delete from database
            success = await self.repository.delete(task_id, user_id)
            
            logger.info(f"Deleted task: {task_id}")
            return OperationResult(
                success=True,
                data={"deleted": True, "task_id": str(task_id)},
                message=f"Deleted task"
            )
            
        except TaskNotFoundException as e:
            logger.error(f"Task not found: {e}")
            return OperationResult(
                success=False,
                message=str(e)
            )
        except Exception as e:
            logger.error(f"Delete operation failed: {e}")
            return OperationResult(
                success=False,
                message=str(e)
            )


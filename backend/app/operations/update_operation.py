"""Update operation"""

from typing import Dict, Any
from uuid import UUID
from app.operations.base_operation import BaseOperation, OperationResult
from app.repositories.task_repository import TaskRepository
from app.schemas.task_schema import TaskUpdate
from app.utils.logger import setup_logger
from app.utils.errors import QueryValidationException, TaskNotFoundException

logger = setup_logger(__name__)


class UpdateOperation(BaseOperation):
    """Update a task"""
    
    def __init__(self, repository: TaskRepository):
        """
        Initialize update operation
        
        Args:
            repository: Task repository
        """
        self.repository = repository
    
    def validate(self, params: Dict[str, Any]) -> bool:
        """
        Validate update parameters
        
        Args:
            params: Parameters with 'task_id' and fields to update
        
        Returns:
            True if valid
        
        Raises:
            QueryValidationException: If validation fails
        """
        if not params.get("task_id"):
            raise QueryValidationException(
                "Task ID is required for update",
                details="params must include 'task_id' field"
            )
        
        return True
    
    async def execute(self, params: Dict[str, Any], user_id: UUID) -> OperationResult:
        """
        Execute update operation
        
        Args:
            params: Update parameters including task_id
            user_id: User ID
        
        Returns:
            OperationResult with updated task
        """
        try:
            # Validate
            self.validate(params)
            
            # Extract task_id and update fields
            task_id = UUID(params["task_id"])
            update_fields = {k: v for k, v in params.items() if k != "task_id"}
            
            # Create update schema
            task_data = TaskUpdate(**update_fields)
            
            # Update in database
            task = await self.repository.update(task_id, task_data, user_id)
            
            logger.info(f"Updated task: {task.title}")
            return OperationResult(
                success=True,
                data=task,
                message=f"Updated task '{task.title}'"
            )
            
        except TaskNotFoundException as e:
            logger.error(f"Task not found: {e}")
            return OperationResult(
                success=False,
                message=str(e)
            )
        except Exception as e:
            logger.error(f"Update operation failed: {e}")
            return OperationResult(
                success=False,
                message=str(e)
            )


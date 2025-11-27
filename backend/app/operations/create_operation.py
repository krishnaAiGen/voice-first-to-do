"""Create operation"""

from typing import Dict, Any
from uuid import UUID
from app.operations.base_operation import BaseOperation, OperationResult
from app.repositories.task_repository import TaskRepository
from app.schemas.task_schema import TaskCreate
from app.utils.logger import setup_logger
from app.utils.errors import QueryValidationException

logger = setup_logger(__name__)


class CreateOperation(BaseOperation):
    """Create a new task"""
    
    def __init__(self, repository: TaskRepository):
        """
        Initialize create operation
        
        Args:
            repository: Task repository
        """
        self.repository = repository
    
    def validate(self, params: Dict[str, Any]) -> bool:
        """
        Validate create parameters
        
        Args:
            params: Parameters with 'title' at minimum
        
        Returns:
            True if valid
        
        Raises:
            QueryValidationException: If validation fails
        """
        if not params.get("title"):
            raise QueryValidationException(
                "Task title is required",
                details="params must include 'title' field"
            )
        
        # Validate priority if provided
        priority = params.get("priority", 0)
        if not isinstance(priority, int) or priority < 0 or priority > 3:
            raise QueryValidationException(
                "Priority must be 0-3",
                details=f"Got priority={priority}"
            )
        
        return True
    
    async def execute(self, params: Dict[str, Any], user_id: UUID) -> OperationResult:
        """
        Execute create operation
        
        Args:
            params: Task parameters
            user_id: User ID
        
        Returns:
            OperationResult with created task
        """
        try:
            # Validate
            self.validate(params)
            
            # Create task schema
            task_data = TaskCreate(**params)
            
            # Create in database
            task = await self.repository.create(task_data, user_id)
            
            logger.info(f"Created task: {task.title}")
            return OperationResult(
                success=True,
                data=task,
                message=f"Created task '{task.title}'"
            )
            
        except Exception as e:
            logger.error(f"Create operation failed: {e}")
            return OperationResult(
                success=False,
                message=str(e)
            )


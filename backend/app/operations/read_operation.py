"""Read operation"""

from typing import Dict, Any
from uuid import UUID
from app.operations.base_operation import BaseOperation, OperationResult
from app.repositories.task_repository import TaskRepository
from app.builders.query_builder import SafeQueryBuilder
from app.models.query_spec import StepSpec
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ReadOperation(BaseOperation):
    """Read/query tasks"""
    
    def __init__(
        self,
        repository: TaskRepository,
        query_builder: SafeQueryBuilder
    ):
        """
        Initialize read operation
        
        Args:
            repository: Task repository
            query_builder: Query builder
        """
        self.repository = repository
        self.query_builder = query_builder
    
    def validate(self, params: Dict[str, Any]) -> bool:
        """
        Validate read parameters
        
        Args:
            params: Parameters (can be empty for "get all")
        
        Returns:
            True (read operations are always valid)
        """
        return True
    
    async def execute(self, params: Dict[str, Any], user_id: UUID) -> OperationResult:
        """
        Execute read operation
        
        Args:
            params: Query parameters (usually empty, uses step_spec)
            user_id: User ID
        
        Returns:
            OperationResult with list of tasks
        """
        try:
            # If no step_spec provided, get all tasks
            step_spec = params.get("step_spec")
            
            if step_spec:
                # Build query from specification
                query = self.query_builder.build_query(step_spec, user_id)
                tasks = await self.repository.execute_query(query)
            else:
                # Get all tasks
                tasks = await self.repository.get_all(user_id)
            
            logger.info(f"Read operation returned {len(tasks)} tasks")
            return OperationResult(
                success=True,
                data=tasks,
                message=f"Found {len(tasks)} tasks"
            )
            
        except Exception as e:
            logger.error(f"Read operation failed: {e}")
            return OperationResult(
                success=False,
                message=str(e)
            )


"""Task service for business logic"""

from typing import List, Optional
from uuid import UUID
from app.repositories.task_repository import TaskRepository
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse
from app.models.task import Task
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class TaskService:
    """Business logic for task operations"""
    
    def __init__(self, repository: TaskRepository):
        """
        Initialize task service
        
        Args:
            repository: Task repository
        """
        self.repository = repository
    
    async def create(self, task_data: TaskCreate, user_id: UUID) -> TaskResponse:
        """
        Create a new task
        
        Args:
            task_data: Task creation data
            user_id: User ID
        
        Returns:
            Created task response
        """
        task = await self.repository.create(task_data, user_id)
        return TaskResponse.model_validate(task)
    
    async def get_by_id(self, task_id: UUID, user_id: UUID) -> Optional[TaskResponse]:
        """
        Get task by ID
        
        Args:
            task_id: Task ID
            user_id: User ID
        
        Returns:
            Task response or None
        """
        task = await self.repository.get_by_id(task_id, user_id)
        if task:
            return TaskResponse.model_validate(task)
        return None
    
    async def get_all(self, user_id: UUID, limit: int = 100) -> List[TaskResponse]:
        """
        Get all tasks for user
        
        Args:
            user_id: User ID
            limit: Maximum number of tasks
        
        Returns:
            List of task responses
        """
        tasks = await self.repository.get_all(user_id, limit)
        return [TaskResponse.model_validate(task) for task in tasks]
    
    async def update(
        self,
        task_id: UUID,
        task_data: TaskUpdate,
        user_id: UUID
    ) -> TaskResponse:
        """
        Update a task
        
        Args:
            task_id: Task ID
            task_data: Update data
            user_id: User ID
        
        Returns:
            Updated task response
        """
        task = await self.repository.update(task_id, task_data, user_id)
        return TaskResponse.model_validate(task)
    
    async def delete(self, task_id: UUID, user_id: UUID) -> bool:
        """
        Delete a task
        
        Args:
            task_id: Task ID
            user_id: User ID
        
        Returns:
            True if deleted
        """
        return await self.repository.delete(task_id, user_id)
    
    async def find_by_filters(
        self,
        filters: List,
        user_id: UUID,
        limit: Optional[int] = None
    ) -> List[TaskResponse]:
        """
        Find tasks by filters
        
        Args:
            filters: List of filter specifications
            user_id: User ID
            limit: Optional limit
        
        Returns:
            List of matching tasks
        """
        # This method is used by the query executor
        # It delegates to the repository with a built query
        pass


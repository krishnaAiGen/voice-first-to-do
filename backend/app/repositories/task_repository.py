"""Task repository for database operations"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.utils.logger import setup_logger
from app.utils.errors import DatabaseException, TaskNotFoundException

logger = setup_logger(__name__)


class TaskRepository:
    """Repository for Task database operations"""
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository
        
        Args:
            session: Database session
        """
        self.session = session
    
    async def create(self, task_data: TaskCreate, user_id: UUID) -> Task:
        """
        Create a new task
        
        Args:
            task_data: Task creation data
            user_id: User ID
        
        Returns:
            Created task
        
        Raises:
            DatabaseException: If creation fails
        """
        try:
            task = Task(
                user_id=user_id,
                **task_data.model_dump()
            )
            
            self.session.add(task)
            await self.session.commit()
            await self.session.refresh(task)
            
            logger.info(f"Created task {task.id}")
            return task
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create task: {e}")
            raise DatabaseException(
                "Failed to create task",
                details=str(e)
            )
    
    async def get_by_id(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """
        Get task by ID
        
        Args:
            task_id: Task ID
            user_id: User ID
        
        Returns:
            Task or None if not found
        """
        try:
            query = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise DatabaseException(
                "Failed to retrieve task",
                details=str(e)
            )
    
    async def get_all(self, user_id: UUID, limit: int = 100) -> List[Task]:
        """
        Get all tasks for user
        
        Args:
            user_id: User ID
            limit: Maximum number of tasks
        
        Returns:
            List of tasks
        """
        try:
            query = select(Task).where(
                Task.user_id == user_id
            ).order_by(Task.created_at.desc()).limit(limit)
            
            result = await self.session.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            raise DatabaseException(
                "Failed to retrieve tasks",
                details=str(e)
            )
    
    async def update(
        self,
        task_id: UUID,
        task_data: TaskUpdate,
        user_id: UUID
    ) -> Task:
        """
        Update a task
        
        Args:
            task_id: Task ID
            task_data: Update data
            user_id: User ID
        
        Returns:
            Updated task
        
        Raises:
            TaskNotFoundException: If task not found
            DatabaseException: If update fails
        """
        try:
            # Check task exists
            task = await self.get_by_id(task_id, user_id)
            if not task:
                raise TaskNotFoundException(
                    f"Task {task_id} not found",
                    details=f"User {user_id} has no task with ID {task_id}"
                )
            
            # Update fields
            update_data = task_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(task, field, value)
            
            await self.session.commit()
            await self.session.refresh(task)
            
            logger.info(f"Updated task {task_id}")
            return task
            
        except TaskNotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update task {task_id}: {e}")
            raise DatabaseException(
                "Failed to update task",
                details=str(e)
            )
    
    async def delete(self, task_id: UUID, user_id: UUID) -> bool:
        """
        Delete a task
        
        Args:
            task_id: Task ID
            user_id: User ID
        
        Returns:
            True if deleted
        
        Raises:
            TaskNotFoundException: If task not found
            DatabaseException: If deletion fails
        """
        try:
            # Check task exists
            task = await self.get_by_id(task_id, user_id)
            if not task:
                raise TaskNotFoundException(
                    f"Task {task_id} not found",
                    details=f"User {user_id} has no task with ID {task_id}"
                )
            
            await self.session.delete(task)
            await self.session.commit()
            
            logger.info(f"Deleted task {task_id}")
            return True
            
        except TaskNotFoundException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to delete task {task_id}: {e}")
            raise DatabaseException(
                "Failed to delete task",
                details=str(e)
            )
    
    async def execute_query(self, query) -> List[Task]:
        """
        Execute a custom query
        
        Args:
            query: SQLAlchemy query
        
        Returns:
            List of tasks
        """
        try:
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise DatabaseException(
                "Failed to execute query",
                details=str(e)
            )
    
    async def update_batch(
        self,
        task_ids: List[UUID],
        modifications: dict,
        user_id: UUID
    ) -> int:
        """
        Update multiple tasks at once
        
        Args:
            task_ids: List of task IDs
            modifications: Fields to update
            user_id: User ID
        
        Returns:
            Number of tasks updated
        """
        try:
            stmt = (
                update(Task)
                .where(
                    Task.id.in_(task_ids),
                    Task.user_id == user_id
                )
                .values(**modifications)
            )
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            count = result.rowcount
            logger.info(f"Updated {count} tasks")
            return count
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to batch update tasks: {e}")
            raise DatabaseException(
                "Failed to batch update tasks",
                details=str(e)
            )


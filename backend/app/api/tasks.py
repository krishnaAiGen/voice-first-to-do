"""REST API endpoints for tasks (fallback)"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.task_schema import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse
)
from app.services.task_service import TaskService
from app.repositories.task_repository import TaskRepository
from app.clients.database_client import get_db
from app.dependencies.auth import get_current_user
from app.core.config import settings
from app.utils.logger import setup_logger
from app.utils.errors import TaskNotFoundException, DatabaseException

logger = setup_logger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    """
    Dependency to create TaskService
    
    Args:
        db: Database session
    
    Returns:
        TaskService instance
    """
    repository = TaskRepository(db)
    return TaskService(repository)


@router.get("", response_model=TaskListResponse)
async def get_tasks(
    limit: int = Query(100, ge=1, le=500),
    user_id: str = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Get all tasks for authenticated user (used for initial page load)
    
    Headers:
        Authorization: Bearer <access_token>
    
    Args:
        limit: Maximum number of tasks
        user_id: Authenticated user ID from JWT
        task_service: Task service dependency
    
    Returns:
        TaskListResponse with tasks
    """
    try:
        user_uuid = UUID(user_id)
        tasks = await task_service.get_all(user_uuid, limit)
        
        return TaskListResponse(
            tasks=tasks,
            total=len(tasks)
        )
        
    except Exception as e:
        logger.error(f"Failed to get tasks: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve tasks: {str(e)}"
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    user_id: Optional[str] = Query(None),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Get a single task by ID
    
    Args:
        task_id: Task ID
        user_id: User ID (optional)
        task_service: Task service dependency
    
    Returns:
        TaskResponse
    """
    try:
        user_uuid = UUID(user_id or settings.default_user_id)
        
        task = await task_service.get_by_id(task_id, user_uuid)
        
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve task: {str(e)}"
        )


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    user_id: Optional[str] = Query(None),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Create a new task (manual creation, not primary flow)
    
    Args:
        task_data: Task creation data
        user_id: User ID (optional)
        task_service: Task service dependency
    
    Returns:
        Created TaskResponse
    """
    try:
        user_uuid = UUID(user_id or settings.default_user_id)
        
        task = await task_service.create(task_data, user_uuid)
        
        logger.info(f"Created task: {task.title}")
        return task
        
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create task: {str(e)}"
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    user_id: Optional[str] = Query(None),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Update a task (manual editing, not primary flow)
    
    Args:
        task_id: Task ID
        task_data: Update data
        user_id: User ID (optional)
        task_service: Task service dependency
    
    Returns:
        Updated TaskResponse
    """
    try:
        user_uuid = UUID(user_id or settings.default_user_id)
        
        task = await task_service.update(task_id, task_data, user_uuid)
        
        logger.info(f"Updated task: {task.title}")
        return task
        
    except TaskNotFoundException as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update task {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update task: {str(e)}"
        )


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    user_id: Optional[str] = Query(None),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Delete a task (manual deletion, not primary flow)
    
    Args:
        task_id: Task ID
        user_id: User ID (optional)
        task_service: Task service dependency
    
    Returns:
        No content
    """
    try:
        user_uuid = UUID(user_id or settings.default_user_id)
        
        await task_service.delete(task_id, user_uuid)
        
        logger.info(f"Deleted task: {task_id}")
        return None
        
    except TaskNotFoundException as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to delete task {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete task: {str(e)}"
        )


"""Pydantic schemas for Task API"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from uuid import UUID


class TaskBase(BaseModel):
    """Base task schema with common fields"""
    
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    priority: int = Field(default=0, ge=0, le=3)
    status: str = Field(default="pending")
    scheduled_time: Optional[datetime] = None
    
    @validator("status")
    def validate_status(cls, v):
        """Validate status field"""
        allowed = {"pending", "in_progress", "completed"}
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v


class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task (all fields optional)"""
    
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    priority: Optional[int] = Field(None, ge=0, le=3)
    status: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    
    @validator("status")
    def validate_status(cls, v):
        """Validate status field"""
        if v is not None:
            allowed = {"pending", "in_progress", "completed"}
            if v not in allowed:
                raise ValueError(f"Status must be one of {allowed}")
        return v


class TaskResponse(TaskBase):
    """Schema for task response"""
    
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    display_order: Optional[int] = None
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for list of tasks"""
    
    tasks: List[TaskResponse]
    total: int
    
    class Config:
        from_attributes = True


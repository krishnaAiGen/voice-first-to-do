"""Task database model"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Text, DateTime, 
    CheckConstraint, Index, text, Computed
)
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Task(Base):
    """Task model for PostgreSQL database"""
    
    __tablename__ = "toDoList"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()")
    )
    
    # User association
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Core fields
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    
    # Priority: 0=none, 1=low, 2=medium, 3=high
    priority = Column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0")
    )
    
    # Status: pending, in_progress, completed
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        server_default=text("'pending'")
    )
    
    # Scheduling
    scheduled_time = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()")
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default=text("NOW()"),
        onupdate=datetime.utcnow
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Display ordering
    display_order = Column(Integer, nullable=True)
    
    # Full-text search vector (generated column in PostgreSQL)
    # Computed column - PostgreSQL generates this automatically
    search_vector = Column(
        TSVECTOR,
        Computed(
            "to_tsvector('english', "
            "coalesce(title, '') || ' ' || "
            "coalesce(description, '') || ' ' || "
            "coalesce(category, ''))",
            persisted=True
        ),
        nullable=True
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "priority >= 0 AND priority <= 3",
            name="check_priority_range"
        ),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed')",
            name="check_status_values"
        ),
        # Indexes for performance
        Index("idx_tasks_user_id", "user_id"),
        Index(
            "idx_tasks_scheduled",
            "user_id", "scheduled_time",
            postgresql_where=text("scheduled_time IS NOT NULL")
        ),
        Index("idx_tasks_status", "user_id", "status"),
        Index("idx_tasks_priority", "user_id", "priority"),
        Index("idx_tasks_category", "user_id", "category"),
        Index(
            "idx_tasks_search",
            "search_vector",
            postgresql_using="gin"
        ),
        Index("idx_tasks_created", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"


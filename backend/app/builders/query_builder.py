"""Safe query builder for constructing database queries"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task
from app.models.query_spec import StepSpec
from app.builders.filter_builder import FilterBuilder
from app.utils.logger import setup_logger
from app.utils.errors import QueryValidationException

logger = setup_logger(__name__)


class SafeQueryBuilder:
    """Build safe, parameterized SQL queries from specifications"""
    
    # Whitelist of allowed order columns
    ALLOWED_ORDER_COLUMNS = [
        'priority', 'scheduled_time', 'created_at', 
        'updated_at', 'title', 'status'
    ]
    
    def __init__(self, session: AsyncSession):
        """
        Initialize query builder
        
        Args:
            session: Database session
        """
        self.session = session
        self.filter_builder = FilterBuilder()
    
    def build_query(self, step: StepSpec, user_id: UUID) -> select:
        """
        Build a safe query from step specification
        
        Args:
            step: Step specification
            user_id: User ID for scoping
        
        Returns:
            SQLAlchemy select statement
        """
        # Start with user-scoped base query
        query = select(Task).where(Task.user_id == user_id)
        
        # Apply filters
        for filter_spec in step.filters:
            query = self.filter_builder.apply_filter(query, filter_spec)
        
        # Apply ordering (default: created_at desc)
        query = query.order_by(desc(Task.created_at))
        
        # Apply limit
        if step.limit:
            query = query.limit(step.limit)
        
        logger.info(f"Built query with {len(step.filters)} filters")
        return query
    
    def validate_order_column(self, column: str) -> bool:
        """
        Validate order column is in whitelist
        
        Args:
            column: Column name
        
        Returns:
            True if valid
        
        Raises:
            QueryValidationException: If column not allowed
        """
        if column not in self.ALLOWED_ORDER_COLUMNS:
            raise QueryValidationException(
                f"Order column '{column}' is not allowed",
                details=f"Allowed columns: {self.ALLOWED_ORDER_COLUMNS}"
            )
        return True


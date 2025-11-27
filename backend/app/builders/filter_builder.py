"""Filter builder for constructing query filters"""

from datetime import datetime
from typing import Any, Callable, Dict
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Query
from app.models.task import Task
from app.models.query_spec import FilterSpec
from app.utils.logger import setup_logger
from app.utils.errors import QueryValidationException

logger = setup_logger(__name__)


class FilterBuilder:
    """Build safe, parameterized filters for queries"""
    
    # Whitelist of allowed filter types with their implementations
    ALLOWED_FILTERS: Dict[str, Callable] = {}
    
    def __init__(self):
        """Initialize filter builder with whitelisted filters"""
        self.ALLOWED_FILTERS = {
            'is_overdue': self._filter_is_overdue,
            'is_today': self._filter_is_today,
            'is_completed': self._filter_is_completed,
            'priority_min': self._filter_priority_min,
            'priority_max': self._filter_priority_max,
            'priority_equals': self._filter_priority_equals,
            'category': self._filter_category,
            'status': self._filter_status,
            'keyword': self._filter_keyword,
            'scheduled_after': self._filter_scheduled_after,
            'scheduled_before': self._filter_scheduled_before,
            'created_after': self._filter_created_after,
            'created_before': self._filter_created_before,
        }
    
    def apply_filter(self, query: Query, filter_spec: FilterSpec) -> Query:
        """
        Apply a single filter to the query
        
        Args:
            query: SQLAlchemy query object
            filter_spec: Filter specification
        
        Returns:
            Modified query
        
        Raises:
            QueryValidationException: If filter type is not allowed
        """
        if filter_spec.type not in self.ALLOWED_FILTERS:
            raise QueryValidationException(
                f"Filter type '{filter_spec.type}' is not allowed",
                details=f"Allowed types: {list(self.ALLOWED_FILTERS.keys())}"
            )
        
        # Get filter function and apply it
        filter_func = self.ALLOWED_FILTERS[filter_spec.type]
        
        try:
            return filter_func(query, filter_spec.value)
        except Exception as e:
            logger.error(f"Failed to apply filter {filter_spec.type}: {e}")
            raise QueryValidationException(
                f"Failed to apply filter '{filter_spec.type}'",
                details=str(e)
            )
    
    # Filter implementations (all use parameterized queries)
    
    def _filter_is_overdue(self, query: Query, value: Any) -> Query:
        """Filter for overdue tasks"""
        now = datetime.utcnow()
        return query.where(
            and_(
                Task.scheduled_time < now,
                Task.status != 'completed'
            )
        )
    
    def _filter_is_today(self, query: Query, value: Any) -> Query:
        """Filter for tasks scheduled today"""
        now = datetime.utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return query.where(
            and_(
                Task.scheduled_time >= start_of_day,
                Task.scheduled_time <= end_of_day
            )
        )
    
    def _filter_is_completed(self, query: Query, value: Any) -> Query:
        """Filter for completed tasks"""
        return query.where(Task.status == 'completed')
    
    def _filter_priority_min(self, query: Query, value: int) -> Query:
        """Filter for minimum priority"""
        if not isinstance(value, int) or value < 0 or value > 3:
            raise QueryValidationException("priority_min value must be 0-3")
        return query.where(Task.priority >= value)
    
    def _filter_priority_max(self, query: Query, value: int) -> Query:
        """Filter for maximum priority"""
        if not isinstance(value, int) or value < 0 or value > 3:
            raise QueryValidationException("priority_max value must be 0-3")
        return query.where(Task.priority <= value)
    
    def _filter_priority_equals(self, query: Query, value: int) -> Query:
        """Filter for exact priority"""
        if not isinstance(value, int) or value < 0 or value > 3:
            raise QueryValidationException("priority_equals value must be 0-3")
        return query.where(Task.priority == value)
    
    def _filter_category(self, query: Query, value: str) -> Query:
        """Filter for category (case-insensitive partial match)"""
        if not isinstance(value, str):
            raise QueryValidationException("category value must be a string")
        return query.where(Task.category.ilike(f'%{value}%'))
    
    def _filter_status(self, query: Query, value: str) -> Query:
        """Filter for exact status"""
        allowed_statuses = {'pending', 'in_progress', 'completed'}
        if value not in allowed_statuses:
            raise QueryValidationException(
                f"status value must be one of {allowed_statuses}"
            )
        return query.where(Task.status == value)
    
    def _filter_keyword(self, query: Query, value: str) -> Query:
        """Filter using full-text search"""
        if not isinstance(value, str):
            raise QueryValidationException("keyword value must be a string")
        
        # Use PostgreSQL full-text search
        return query.where(
            Task.search_vector.op('@@')(
                func.plainto_tsquery('english', value)
            )
        )
    
    def _filter_scheduled_after(self, query: Query, value: str) -> Query:
        """Filter for tasks scheduled after a date"""
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            raise QueryValidationException("scheduled_after value must be ISO 8601 datetime")
        return query.where(Task.scheduled_time >= dt)
    
    def _filter_scheduled_before(self, query: Query, value: str) -> Query:
        """Filter for tasks scheduled before a date"""
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            raise QueryValidationException("scheduled_before value must be ISO 8601 datetime")
        return query.where(Task.scheduled_time <= dt)
    
    def _filter_created_after(self, query: Query, value: str) -> Query:
        """Filter for tasks created after a date"""
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            raise QueryValidationException("created_after value must be ISO 8601 datetime")
        return query.where(Task.created_at >= dt)
    
    def _filter_created_before(self, query: Query, value: str) -> Query:
        """Filter for tasks created before a date"""
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            raise QueryValidationException("created_before value must be ISO 8601 datetime")
        return query.where(Task.created_at <= dt)


"""Query specification models for LLM-generated specifications"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime


@dataclass
class FilterSpec:
    """Specification for a single filter"""
    
    type: str  # e.g., "is_overdue", "priority_min", "keyword"
    value: Optional[Any] = None  # Optional value for the filter
    
    def __post_init__(self):
        """Validate filter specification"""
        allowed_types = {
            'is_overdue', 'is_today', 'is_completed',
            'priority_min', 'priority_max', 'priority_equals',
            'category', 'status', 'keyword',
            'scheduled_after', 'scheduled_before',
            'created_after', 'created_before'
        }
        
        if self.type not in allowed_types:
            raise ValueError(f"Invalid filter type: {self.type}")


@dataclass
class StepSpec:
    """Specification for a single execution step"""
    
    order: int
    operation: Literal["create", "read", "update", "delete", "update_batch"]
    params: Dict[str, Any] = field(default_factory=dict)
    filters: List[FilterSpec] = field(default_factory=list)
    limit: Optional[int] = None
    save_result_as: Optional[str] = None
    use_result_from: Optional[str] = None
    selector: Optional[str] = None  # "first_N", "last_N", "by_index"
    index: Optional[int] = None  # For "by_index" selector
    modifications: Optional[Dict[str, Any]] = None  # For update_batch


@dataclass
class QuerySpecification:
    """Complete specification for query execution"""
    
    complexity: Literal["simple", "multi_step", "interactive"]
    strategy: Literal["sequential", "interactive"]
    steps: List[StepSpec]
    natural_response: str
    
    def __post_init__(self):
        """Validate specification"""
        if not self.steps:
            raise ValueError("Query specification must have at least one step")
        
        if self.complexity == "simple" and len(self.steps) > 1:
            raise ValueError("Simple queries should have only one step")


@dataclass
class IntentResult:
    """Result of intent parsing"""
    
    specification: QuerySpecification
    confidence: float = 1.0
    parsed_at: datetime = field(default_factory=datetime.utcnow)
    raw_llm_response: Optional[str] = None


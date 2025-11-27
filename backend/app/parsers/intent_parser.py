"""Intent parser using LLM to convert commands to specifications"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from app.clients.gemini_client import GeminiClient
from app.models.query_spec import (
    QuerySpecification,
    StepSpec,
    FilterSpec,
    IntentResult
)
from app.utils.logger import setup_logger
from app.utils.errors import IntentParsingException

logger = setup_logger(__name__)


class IntentParser:
    """Parse user intent using LLM"""
    
    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize intent parser
        
        Args:
            gemini_client: Gemini client instance
        """
        self.gemini_client = gemini_client
    
    def _build_prompt(self, command: str, user_context: Dict[str, Any]) -> str:
        """
        Build prompt for LLM
        
        Args:
            command: User command text
            user_context: Context like timezone, current time
        
        Returns:
            Formatted prompt
        """
        current_datetime = user_context.get("current_datetime", datetime.now().isoformat())
        user_timezone = user_context.get("timezone", "UTC")
        
        return f"""You are a task management intent parser. Convert the user's command into a structured specification.

Current date/time: {current_datetime}
User timezone: {user_timezone}

User command: "{command}"

Respond with JSON only (no markdown, no explanations):
{{
  "complexity": "simple" | "multi_step" | "interactive",
  "strategy": "sequential" | "interactive",
  "steps": [
    {{
      "order": 1,
      "operation": "create" | "read" | "update" | "delete" | "update_batch",
      "params": {{
        "title": "string",
        "description": "string",
        "priority": 0-3,
        "category": "string",
        "scheduled_time": "ISO 8601 string or null"
      }},
      "filters": [
        {{"type": "is_overdue"}},
        {{"type": "priority_min", "value": 2}},
        {{"type": "keyword", "value": "client"}},
        {{"type": "category", "value": "admin"}},
        {{"type": "scheduled_after", "value": "ISO 8601"}},
        {{"type": "created_after", "value": "ISO 8601"}},
        {{"type": "status", "value": "pending" | "completed"}}
      ],
      "limit": integer or null,
      "save_result_as": "variable_name" or null,
      "use_result_from": "variable_name" or null,
      "selector": "first_N" | "last_N" | null,
      "index": integer or null,
      "modifications": {{}} or null
    }}
  ],
  "natural_response": "User-friendly confirmation message"
}}

Available filter types:
- is_overdue: Tasks past scheduled_time and not completed
- is_today: Tasks scheduled for today
- is_completed: Completed tasks
- priority_min, priority_max, priority_equals: Priority filtering
- category: Category filter (case-insensitive partial match)
- status: Status filter (exact match)
- keyword: Full-text search across title, description, category
- scheduled_after, scheduled_before: Date range for scheduled_time
- created_after, created_before: Date range for created_at

Rules:
1. For simple queries (create one task, show filtered tasks), use complexity="simple" with single step
2. For multi-operation queries (show X and mark Y), use complexity="multi_step" with sequential steps
3. For queries needing intermediate analysis, use complexity="interactive" (rare)
4. Always include natural_response for user feedback
5. Parse relative dates: "tomorrow" = +1 day, "next week" = +7 days, "in 3 hours" = +3 hours
6. Priority: "high"/"urgent" = 3, "medium" = 2, "low" = 1, unspecified = 0
7. If user says "4th task" or "task 5", use selector="by_index" with index value

Examples:

Command: "Create a task to buy groceries tomorrow at 2pm"
{{
  "complexity": "simple",
  "strategy": "sequential",
  "steps": [{{
    "order": 1,
    "operation": "create",
    "params": {{
      "title": "Buy groceries",
      "scheduled_time": "{(datetime.now().replace(hour=14, minute=0, second=0) + timedelta(days=1)).isoformat()}",
      "priority": 0
    }},
    "filters": [],
    "limit": null
  }}],
  "natural_response": "Created task 'Buy groceries' scheduled for tomorrow at 2pm"
}}

Command: "Show me overdue tasks"
{{
  "complexity": "simple",
  "strategy": "sequential",
  "steps": [{{
    "order": 1,
    "operation": "read",
    "params": {{}},
    "filters": [
      {{"type": "is_overdue"}}
    ],
    "limit": 50
  }}],
  "natural_response": "Here are your overdue tasks"
}}

Command: "Delete the 4th task"
{{
  "complexity": "simple",
  "strategy": "sequential",
  "steps": [{{
    "order": 1,
    "operation": "delete",
    "params": {{}},
    "filters": [],
    "selector": "by_index",
    "index": 4
  }}],
  "natural_response": "Deleted the 4th task"
}}

Command: "Move my reading paper task to tomorrow"
{{
  "complexity": "multi_step",
  "strategy": "sequential",
  "steps": [{{
    "order": 1,
    "operation": "read",
    "params": {{}},
    "filters": [
      {{"type": "keyword", "value": "reading paper"}}
    ],
    "limit": 1,
    "save_result_as": "task_to_update"
  }}, {{
    "order": 2,
    "operation": "update",
    "params": {{}},
    "use_result_from": "task_to_update",
    "filters": [],
    "modifications": {{
      "scheduled_time": "{(datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0).isoformat()}"
    }}
  }}],
  "natural_response": "Moved your reading paper task to tomorrow"
}}

Command: "Mark all overdue tasks as completed"
{{
  "complexity": "multi_step",
  "strategy": "sequential",
  "steps": [{{
    "order": 1,
    "operation": "read",
    "params": {{}},
    "filters": [
      {{"type": "is_overdue"}}
    ],
    "save_result_as": "overdue_tasks"
  }}, {{
    "order": 2,
    "operation": "update_batch",
    "use_result_from": "overdue_tasks",
    "modifications": {{
      "status": "completed"
    }}
  }}],
  "natural_response": "Marked all overdue tasks as completed"
}}

Command: "Delete my grocery task"
{{
  "complexity": "multi_step",
  "strategy": "sequential",
  "steps": [{{
    "order": 1,
    "operation": "read",
    "params": {{}},
    "filters": [
      {{"type": "keyword", "value": "grocery"}}
    ],
    "limit": 1,
    "save_result_as": "task_to_delete"
  }}, {{
    "order": 2,
    "operation": "delete",
    "params": {{}},
    "use_result_from": "task_to_delete"
  }}],
  "natural_response": "Deleted your grocery task"
}}

Command: "Change my project task to high priority and move it to next Monday"
{{
  "complexity": "multi_step",
  "strategy": "sequential",
  "steps": [{{
    "order": 1,
    "operation": "read",
    "params": {{}},
    "filters": [
      {{"type": "keyword", "value": "project"}}
    ],
    "limit": 1,
    "save_result_as": "task"
  }}, {{
    "order": 2,
    "operation": "update",
    "params": {{}},
    "use_result_from": "task",
    "modifications": {{
      "priority": 3,
      "scheduled_time": "{(datetime.now() + timedelta(days=((7 - datetime.now().weekday()) % 7))).replace(hour=0, minute=0, second=0).isoformat()}"
    }}
  }}],
  "natural_response": "Changed your project task to high priority and moved it to next Monday"
}}

Additional Rules:
8. For update/delete operations with search terms (e.g., "move my X task"), ALWAYS use multi_step:
   - Step 1: read with keyword filter to find the task, save_result_as="task_to_update" or "task_to_delete"
   - Step 2: update/delete using use_result_from
9. When updating, put all changed fields in modifications (not params). Never use both params and modifications.
10. For status changes: use "completed", "in_progress", or "pending". Set completed_at when marking complete.
11. Use keyword filter for task name searches - it's more flexible than exact matching
12. For batch operations affecting multiple tasks, use update_batch with use_result_from
"""
    
    async def parse(self, command: str, user_context: Optional[Dict[str, Any]] = None) -> IntentResult:
        """
        Parse user command into intent result
        
        Args:
            command: User command text
            user_context: Optional user context
        
        Returns:
            IntentResult with specification
        
        Raises:
            IntentParsingException: If parsing fails
        """
        user_context = user_context or {}
        
        # Add current datetime if not present
        if "current_datetime" not in user_context:
            user_context["current_datetime"] = datetime.now().isoformat()
        
        # Build prompt
        prompt = self._build_prompt(command, user_context)
        
        # Generate with LLM
        raw_response = await self.gemini_client.generate_intent(prompt)
        
        # Parse specification
        try:
            specification = self._parse_specification(raw_response)
        except Exception as e:
            logger.error(f"Failed to parse specification: {e}")
            raise IntentParsingException(
                "Failed to parse intent specification",
                details=str(e)
            )
        
        return IntentResult(
            specification=specification,
            confidence=1.0,
            raw_llm_response=str(raw_response)
        )
    
    def _parse_specification(self, data: Dict[str, Any]) -> QuerySpecification:
        """
        Parse raw LLM response into QuerySpecification
        
        Args:
            data: Raw LLM response dictionary
        
        Returns:
            QuerySpecification object
        """
        # Parse steps
        steps = []
        for step_data in data.get("steps", []):
            # Parse filters
            filters = []
            for filter_data in step_data.get("filters", []):
                filters.append(FilterSpec(
                    type=filter_data["type"],
                    value=filter_data.get("value")
                ))
            
            # Create step spec
            step = StepSpec(
                order=step_data["order"],
                operation=step_data["operation"],
                params=step_data.get("params", {}),
                filters=filters,
                limit=step_data.get("limit"),
                save_result_as=step_data.get("save_result_as"),
                use_result_from=step_data.get("use_result_from"),
                selector=step_data.get("selector"),
                index=step_data.get("index"),
                modifications=step_data.get("modifications")
            )
            steps.append(step)
        
        # Create specification
        return QuerySpecification(
            complexity=data["complexity"],
            strategy=data["strategy"],
            steps=steps,
            natural_response=data["natural_response"]
        )


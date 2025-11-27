"""Query executor service for executing specifications"""

from typing import Dict, Any, List
from uuid import UUID
from app.models.query_spec import QuerySpecification, StepSpec
from app.operations.create_operation import CreateOperation
from app.operations.read_operation import ReadOperation
from app.operations.update_operation import UpdateOperation
from app.operations.delete_operation import DeleteOperation
from app.operations.base_operation import OperationResult
from app.repositories.task_repository import TaskRepository
from app.builders.query_builder import SafeQueryBuilder
from app.schemas.task_schema import TaskResponse
from app.utils.logger import setup_logger
from app.utils.errors import QueryValidationException

logger = setup_logger(__name__)


class ExecutionResult:
    """Result of specification execution"""
    
    def __init__(
        self,
        success: bool,
        results: List[Any],
        message: str = "",
        data: Any = None
    ):
        self.success = success
        self.results = results
        self.message = message
        self.data = data


class QueryExecutor:
    """Execute query specifications"""
    
    def __init__(
        self,
        repository: TaskRepository,
        query_builder: SafeQueryBuilder
    ):
        """
        Initialize query executor
        
        Args:
            repository: Task repository
            query_builder: Query builder
        """
        self.repository = repository
        self.query_builder = query_builder
        
        # Initialize operations
        self.operations = {
            "create": CreateOperation(repository),
            "read": ReadOperation(repository, query_builder),
            "update": UpdateOperation(repository),
            "delete": DeleteOperation(repository),
        }
    
    async def execute(
        self,
        specification: QuerySpecification,
        user_id: str
    ) -> ExecutionResult:
        """
        Execute a query specification
        
        Args:
            specification: Query specification
            user_id: User ID
        
        Returns:
            ExecutionResult
        """
        user_uuid = UUID(user_id)
        
        logger.info(
            f"Executing specification: {specification.complexity} "
            f"with {len(specification.steps)} steps"
        )
        
        if specification.complexity == "simple":
            return await self._execute_simple(specification, user_uuid)
        elif specification.complexity == "multi_step":
            return await self._execute_sequential(specification, user_uuid)
        else:  # interactive
            return await self._execute_interactive(specification, user_uuid)
    
    async def _execute_simple(
        self,
        specification: QuerySpecification,
        user_id: UUID
    ) -> ExecutionResult:
        """
        Execute a simple single-step specification
        
        Args:
            specification: Query specification
            user_id: User ID
        
        Returns:
            ExecutionResult
        """
        step = specification.steps[0]
        result = await self._execute_step(step, user_id, {})
        
        # Format result data
        data = self._format_result_data(result)
        
        return ExecutionResult(
            success=result.success,
            results=[result],
            message=specification.natural_response,
            data=data
        )
    
    async def _execute_sequential(
        self,
        specification: QuerySpecification,
        user_id: UUID
    ) -> ExecutionResult:
        """
        Execute multiple steps sequentially
        
        Args:
            specification: Query specification
            user_id: User ID
        
        Returns:
            ExecutionResult
        """
        results = []
        context = {}  # Store intermediate results
        
        for step in specification.steps:
            # Execute step with context
            result = await self._execute_step(step, user_id, context)
            results.append(result)
            
            # Store result if needed for next step
            if step.save_result_as:
                context[step.save_result_as] = result.data
            
            # If step failed, stop execution
            if not result.success:
                logger.warning(f"Step {step.order} failed, stopping execution")
                break
        
        # Format final result
        final_result = results[-1] if results else None
        data = self._format_result_data(final_result) if final_result else None
        
        return ExecutionResult(
            success=all(r.success for r in results),
            results=results,
            message=specification.natural_response,
            data=data
        )
    
    async def _execute_interactive(
        self,
        specification: QuerySpecification,
        user_id: UUID
    ) -> ExecutionResult:
        """
        Execute with interactive tool use (rare case)
        
        Args:
            specification: Query specification
            user_id: User ID
        
        Returns:
            ExecutionResult
        """
        # For now, treat as sequential
        # In production, this would involve multiple LLM rounds
        return await self._execute_sequential(specification, user_id)
    
    async def _execute_step(
        self,
        step: StepSpec,
        user_id: UUID,
        context: Dict[str, Any]
    ) -> OperationResult:
        """
        Execute a single step
        
        Args:
            step: Step specification
            user_id: User ID
            context: Execution context with stored results
        
        Returns:
            OperationResult
        """
        logger.info(f"Executing step {step.order}: {step.operation}")
        
        # Handle special operations
        if step.operation == "update_batch":
            return await self._execute_update_batch(step, user_id, context)
        
        # Get operation
        operation = self.operations.get(step.operation)
        if not operation:
            raise QueryValidationException(
                f"Unknown operation: {step.operation}"
            )
        
        # Handle read operation specially (needs step_spec)
        if step.operation == "read":
            params = {"step_spec": step}
            return await operation.execute(params, user_id)
        
        # Handle update operation with filters (search then update)
        if step.operation == "update" and step.filters and not step.params.get("task_id") and not step.use_result_from:
            return await self._execute_update_with_search(step, user_id)
        
        # Handle delete by index
        if step.operation == "delete" and step.selector == "by_index":
            return await self._execute_delete_by_index(step, user_id)
        
        # Handle delete operation with filters (search then delete)
        if step.operation == "delete" and step.filters and not step.params.get("task_id") and not step.use_result_from:
            return await self._execute_delete_with_search(step, user_id)
        
        # Handle operations that use results from previous steps
        if step.use_result_from:
            if step.use_result_from not in context:
                return OperationResult(
                    success=False,
                    message=f"No data found from previous step '{step.use_result_from}'"
                )
            
            previous_data = context[step.use_result_from]
            
            # Check if previous step returned empty results
            if not previous_data:
                return OperationResult(
                    success=False,
                    message="No tasks found matching your criteria. Please try a different search."
                )
            
            # Handle update operation with previous result
            if step.operation == "update":
                # If previous data is a list, get first item
                if isinstance(previous_data, list):
                    if len(previous_data) == 0:
                        return OperationResult(
                            success=False,
                            message="No tasks found to update."
                        )
                    task_to_update = previous_data[0]
                else:
                    task_to_update = previous_data
                
                # Merge modifications into params
                params = {
                    "task_id": str(task_to_update.id),
                    **step.modifications
                }
                return await operation.execute(params, user_id)
            
            # Handle delete operation with previous result
            if step.operation == "delete":
                if isinstance(previous_data, list):
                    if len(previous_data) == 0:
                        return OperationResult(
                            success=False,
                            message="No tasks found to delete."
                        )
                    task_to_delete = previous_data[0]
                else:
                    task_to_delete = previous_data
                
                params = {"task_id": str(task_to_delete.id)}
                return await operation.execute(params, user_id)
        
        # Execute operation
        return await operation.execute(step.params, user_id)
    
    async def _execute_update_batch(
        self,
        step: StepSpec,
        user_id: UUID,
        context: Dict[str, Any]
    ) -> OperationResult:
        """
        Execute batch update operation
        
        Args:
            step: Step specification
            user_id: User ID
            context: Execution context
        
        Returns:
            OperationResult
        """
        # Get tasks from context
        if not step.use_result_from or step.use_result_from not in context:
            return OperationResult(
                success=False,
                message="No tasks found in context for batch update"
            )
        
        tasks = context[step.use_result_from]
        if not isinstance(tasks, list):
            return OperationResult(
                success=False,
                message="Invalid task list for batch update"
            )
        
        # Extract task IDs
        task_ids = [task.id for task in tasks]
        
        # Perform batch update
        count = await self.repository.update_batch(
            task_ids,
            step.modifications,
            user_id
        )
        
        return OperationResult(
            success=True,
            data={"updated_count": count},
            message=f"Updated {count} tasks"
        )
    
    async def _execute_delete_by_index(
        self,
        step: StepSpec,
        user_id: UUID
    ) -> OperationResult:
        """
        Delete task by index (e.g., "delete 4th task")
        
        Args:
            step: Step specification
            user_id: User ID
        
        Returns:
            OperationResult
        """
        # Get all tasks
        tasks = await self.repository.get_all(user_id)
        
        # Check index
        index = step.index - 1  # Convert to 0-based
        if index < 0 or index >= len(tasks):
            return OperationResult(
                success=False,
                message=f"Task index {step.index} out of range"
            )
        
        # Get task at index
        task = tasks[index]
        
        # Delete it
        await self.repository.delete(task.id, user_id)
        
        return OperationResult(
            success=True,
            data={"deleted": True, "task_id": str(task.id)},
            message=f"Deleted task '{task.title}'"
        )
    
    async def _execute_update_with_search(
        self,
        step: StepSpec,
        user_id: UUID
    ) -> OperationResult:
        """
        Update operation with filters - search first, then update
        
        Args:
            step: Step specification with filters
            user_id: User ID
        
        Returns:
            OperationResult
        """
        # First, search for the task using filters
        search_step = StepSpec(
            order=1,
            operation="read",
            params={},
            filters=step.filters,
            limit=1,
            save_result_as=None,
            use_result_from=None,
            selector=None,
            index=None,
            modifications=None
        )
        
        # Execute search
        search_result = await self.operations["read"].execute(
            {"step_spec": search_step},
            user_id
        )
        
        if not search_result.success or not search_result.data:
            return OperationResult(
                success=False,
                message="No tasks found matching your criteria. Please try a different search."
            )
        
        # Get the first task from results
        tasks = search_result.data
        if isinstance(tasks, list):
            if len(tasks) == 0:
                return OperationResult(
                    success=False,
                    message="No tasks found to update."
                )
            task_to_update = tasks[0]
        else:
            task_to_update = tasks
        
        # Now update the task
        update_params = {
            "task_id": str(task_to_update.id),
            **step.modifications
        }
        
        return await self.operations["update"].execute(update_params, user_id)
    
    async def _execute_delete_with_search(
        self,
        step: StepSpec,
        user_id: UUID
    ) -> OperationResult:
        """
        Delete operation with filters - search first, then delete
        
        Args:
            step: Step specification with filters
            user_id: User ID
        
        Returns:
            OperationResult
        """
        # First, search for the task using filters
        search_step = StepSpec(
            order=1,
            operation="read",
            params={},
            filters=step.filters,
            limit=1,
            save_result_as=None,
            use_result_from=None,
            selector=None,
            index=None,
            modifications=None
        )
        
        # Execute search
        search_result = await self.operations["read"].execute(
            {"step_spec": search_step},
            user_id
        )
        
        if not search_result.success or not search_result.data:
            return OperationResult(
                success=False,
                message="No tasks found matching your criteria. Please try a different search."
            )
        
        # Get the first task from results
        tasks = search_result.data
        if isinstance(tasks, list):
            if len(tasks) == 0:
                return OperationResult(
                    success=False,
                    message="No tasks found to delete."
                )
            task_to_delete = tasks[0]
        else:
            task_to_delete = tasks
        
        # Now delete the task
        delete_params = {"task_id": str(task_to_delete.id)}
        
        return await self.operations["delete"].execute(delete_params, user_id)
    
    def _format_result_data(self, result: OperationResult) -> Any:
        """
        Format result data for API response
        
        Args:
            result: Operation result
        
        Returns:
            Formatted data
        """
        if not result or not result.data:
            return None
        
        data = result.data
        
        # If it's a list of tasks, convert to TaskResponse
        if isinstance(data, list):
            return [
                TaskResponse.model_validate(task) if hasattr(task, "id") else task
                for task in data
            ]
        
        # If it's a single task, convert to TaskResponse
        if hasattr(data, "id"):
            return TaskResponse.model_validate(data)
        
        # Return as-is (e.g., dict)
        return data


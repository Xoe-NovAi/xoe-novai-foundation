#!/usr/bin/env python3
"""
Task Coordinator for XNAi Foundation

This script coordinates complex multi-step tasks across multiple agent accounts,
managing dependencies, workflows, and result aggregation.

Author: XNAi Foundation
License: AGPL-3.0-only
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, asdict
import redis.asyncio as redis
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskState(str, Enum):
    """Task state enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(int, Enum):
    """Task priority enumeration"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskStep:
    """Individual task step"""
    step_id: str
    step_type: str
    description: str
    command: str
    dependencies: List[str]
    timeout: int
    retry_count: int
    max_retries: int
    assigned_agent: Optional[str]
    status: TaskState
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[Dict[str, Any]]
    error: Optional[str]


@dataclass
class WorkflowTask:
    """Complete workflow task"""
    task_id: str
    name: str
    description: str
    priority: TaskPriority
    steps: List[TaskStep]
    status: TaskState
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    metadata: Dict[str, Any]


class TaskCoordinator:
    """Coordinates complex multi-step tasks across agents"""
    
    def __init__(self, config_path: str = "configs/multi-agent-config.yaml"):
        """
        Initialize the task coordinator
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config: Optional[Dict] = None
        self.redis_client: Optional[redis.Redis] = None
        
        # Task management
        self.tasks: Dict[str, WorkflowTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Agent coordination
        self.agent_tasks: Dict[str, List[str]] = {}  # agent_id -> task_ids
        
        # Event handlers
        self.on_task_started: Optional[Callable[[str], Awaitable[None]]] = None
        self.on_task_completed: Optional[Callable[[str, Dict], Awaitable[None]]] = None
        self.on_task_failed: Optional[Callable[[str, str], Awaitable[None]]] = None
        
        # Configuration
        self.max_concurrent_tasks = 10
        self.task_timeout = 3600  # 1 hour
        self.step_timeout = 600   # 10 minutes
    
    async def load_config(self) -> None:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            self.config = config_data.get('multi_agent', {})
            
            # Update task coordination settings
            if 'coordination' in self.config:
                coord_config = self.config['coordination']
                self.max_concurrent_tasks = coord_config.get('max_concurrent_tasks', 10)
                self.task_timeout = coord_config.get('task_timeout', 3600)
                self.step_timeout = coord_config.get('step_timeout', 600)
            
            logger.info("Loaded task coordinator configuration")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    async def initialize(self) -> None:
        """Initialize the task coordinator"""
        await self.load_config()
        
        # Initialize Redis connection
        await self._init_redis()
        
        # Load existing tasks
        await self._load_tasks()
        
        logger.info("Task coordinator initialized")
    
    async def _init_redis(self) -> None:
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                os.getenv('REDIS_URL', 'redis://localhost:6379'),
                decode_responses=False
            )
            await self.redis_client.ping()
            logger.info("Redis connection established for task coordination")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def _load_tasks(self) -> None:
        """Load existing tasks from Redis"""
        try:
            task_keys = await self.redis_client.keys("task:*")
            for key in task_keys:
                task_data = await self.redis_client.get(key)
                if task_data:
                    task_dict = json.loads(task_data.decode())
                    # Convert datetime strings back to datetime objects
                    task_dict['created_at'] = datetime.fromisoformat(task_dict['created_at'])
                    if task_dict['started_at']:
                        task_dict['started_at'] = datetime.fromisoformat(task_dict['started_at'])
                    if task_dict['completed_at']:
                        task_dict['completed_at'] = datetime.fromisoformat(task_dict['completed_at'])
                    
                    # Convert steps
                    for step_dict in task_dict['steps']:
                        step_dict['started_at'] = datetime.fromisoformat(step_dict['started_at']) if step_dict['started_at'] else None
                        step_dict['completed_at'] = datetime.fromisoformat(step_dict['completed_at']) if step_dict['completed_at'] else None
                    
                    task = WorkflowTask(**task_dict)
                    self.tasks[task.task_id] = task
            
            logger.info(f"Loaded {len(self.tasks)} existing tasks")
            
        except Exception as e:
            logger.error(f"Failed to load tasks: {e}")
    
    async def create_workflow_task(self, name: str, description: str, steps: List[Dict[str, Any]], 
                                 priority: TaskPriority = TaskPriority.MEDIUM, 
                                 metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new workflow task
        
        Args:
            name: Task name
            description: Task description
            steps: List of step definitions
            priority: Task priority
            metadata: Additional metadata
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        
        # Create task steps
        task_steps = []
        for i, step_def in enumerate(steps):
            step = TaskStep(
                step_id=f"{task_id}_step_{i}",
                step_type=step_def.get('type', 'command'),
                description=step_def.get('description', f'Step {i+1}'),
                command=step_def.get('command', ''),
                dependencies=step_def.get('dependencies', []),
                timeout=step_def.get('timeout', self.step_timeout),
                retry_count=0,
                max_retries=step_def.get('max_retries', 3),
                assigned_agent=None,
                status=TaskState.PENDING,
                started_at=None,
                completed_at=None,
                result=None,
                error=None
            )
            task_steps.append(step)
        
        # Create workflow task
        task = WorkflowTask(
            task_id=task_id,
            name=name,
            description=description,
            priority=priority,
            steps=task_steps,
            status=TaskState.PENDING,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            result=None,
            error=None,
            metadata=metadata or {}
        )
        
        self.tasks[task_id] = task
        await self._save_task(task)
        
        logger.info(f"Created workflow task: {task_id} - {name}")
        return task_id
    
    async def execute_task(self, task_id: str) -> bool:
        """
        Execute a workflow task
        
        Args:
            task_id: Task ID to execute
            
        Returns:
            True if execution started successfully
        """
        if task_id not in self.tasks:
            logger.error(f"Task not found: {task_id}")
            return False
        
        task = self.tasks[task_id]
        
        # Check if task is already running
        if task.status == TaskState.RUNNING:
            logger.warning(f"Task {task_id} is already running")
            return False
        
        # Check concurrent task limit
        if len(self.running_tasks) >= self.max_concurrent_tasks:
            logger.warning(f"Maximum concurrent tasks ({self.max_concurrent_tasks}) reached")
            return False
        
        # Start task execution
        task.status = TaskState.RUNNING
        task.started_at = datetime.now()
        await self._save_task(task)
        
        # Create execution task
        execution_task = asyncio.create_task(self._execute_workflow(task))
        self.running_tasks[task_id] = execution_task
        
        # Notify task started
        if self.on_task_started:
            await self.on_task_started(task_id)
        
        logger.info(f"Started executing task: {task_id}")
        return True
    
    async def _execute_workflow(self, task: WorkflowTask) -> None:
        """Execute a complete workflow"""
        try:
            # Execute steps in dependency order
            execution_order = self._get_execution_order(task.steps)
            
            for step_id in execution_order:
                step = next(s for s in task.steps if s.step_id == step_id)
                
                # Wait for dependencies to complete
                await self._wait_for_dependencies(task, step)
                
                # Execute step
                success = await self._execute_step(task, step)
                
                if not success:
                    # Step failed, mark task as failed
                    task.status = TaskState.FAILED
                    task.error = f"Step {step.step_id} failed after {step.max_retries} retries"
                    task.completed_at = datetime.now()
                    await self._save_task(task)
                    
                    # Notify task failed
                    if self.on_task_failed:
                        await self.on_task_failed(task.task_id, task.error)
                    
                    return
            
            # All steps completed successfully
            task.status = TaskState.COMPLETED
            task.completed_at = datetime.now()
            task.result = self._aggregate_results(task)
            await self._save_task(task)
            
            # Notify task completed
            if self.on_task_completed:
                await self.on_task_completed(task.task_id, task.result)
            
            logger.info(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error executing task {task.task_id}: {e}")
            task.status = TaskState.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            await self._save_task(task)
            
            # Notify task failed
            if self.on_task_failed:
                await self.on_task_failed(task.task_id, task.error)
        
        finally:
            # Clean up running task
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
    
    def _get_execution_order(self, steps: List[TaskStep]) -> List[str]:
        """Get execution order based on dependencies using topological sort"""
        # Build dependency graph
        graph = {step.step_id: step.dependencies for step in steps}
        
        # Topological sort
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(node_id: str):
            if node_id in temp_visited:
                raise ValueError(f"Circular dependency detected for step {node_id}")
            if node_id not in visited:
                temp_visited.add(node_id)
                for dep in graph.get(node_id, []):
                    visit(dep)
                temp_visited.remove(node_id)
                visited.add(node_id)
                order.append(node_id)
        
        for step in steps:
            if step.step_id not in visited:
                visit(step.step_id)
        
        return order
    
    async def _wait_for_dependencies(self, task: WorkflowTask, step: TaskStep) -> None:
        """Wait for step dependencies to complete"""
        for dep_id in step.dependencies:
            # Find dependency step
            dep_step = next((s for s in task.steps if s.step_id == dep_id), None)
            if not dep_step:
                raise ValueError(f"Dependency step {dep_id} not found")
            
            # Wait for dependency to complete
            while dep_step.status not in [TaskState.COMPLETED, TaskState.FAILED]:
                await asyncio.sleep(1)
            
            if dep_step.status == TaskState.FAILED:
                raise ValueError(f"Dependency step {dep_id} failed")
    
    async def _execute_step(self, task: WorkflowTask, step: TaskStep) -> bool:
        """Execute a single task step"""
        step.status = TaskState.RUNNING
        step.started_at = datetime.now()
        await self._save_task(task)
        
        # Find suitable agent for this step
        agent_id = await self._find_suitable_agent(step)
        if not agent_id:
            step.status = TaskState.FAILED
            step.error = "No suitable agent available"
            step.completed_at = datetime.now()
            await self._save_task(task)
            return False
        
        # Assign step to agent
        step.assigned_agent = agent_id
        if agent_id not in self.agent_tasks:
            self.agent_tasks[agent_id] = []
        self.agent_tasks[agent_id].append(task.task_id)
        
        try:
            # Send step to agent
            step_result = await self._send_step_to_agent(task, step, agent_id)
            
            if step_result['success']:
                step.status = TaskState.COMPLETED
                step.result = step_result['result']
                step.completed_at = datetime.now()
                await self._save_task(task)
                return True
            else:
                step.error = step_result['error']
                step.retry_count += 1
                
                if step.retry_count >= step.max_retries:
                    step.status = TaskState.FAILED
                    step.completed_at = datetime.now()
                    await self._save_task(task)
                    return False
                
                # Retry after delay
                await asyncio.sleep(5)
                return await self._execute_step(task, step)
        
        except Exception as e:
            step.error = str(e)
            step.retry_count += 1
            
            if step.retry_count >= step.max_retries:
                step.status = TaskState.FAILED
                step.completed_at = datetime.now()
                await self._save_task(task)
                return False
            
            # Retry after delay
            await asyncio.sleep(5)
            return await self._execute_step(task, step)
        
        finally:
            # Remove task from agent's active tasks
            if agent_id in self.agent_tasks and task.task_id in self.agent_tasks[agent_id]:
                self.agent_tasks[agent_id].remove(task.task_id)
    
    async def _find_suitable_agent(self, step: TaskStep) -> Optional[str]:
        """Find a suitable agent for a step"""
        # This would integrate with the multi-agent coordinator
        # For now, return a placeholder
        return "placeholder_agent_id"
    
    async def _send_step_to_agent(self, task: WorkflowTask, step: TaskStep, agent_id: str) -> Dict[str, Any]:
        """Send step to agent and wait for result"""
        # This would integrate with the agent communication system
        # For now, return a mock result
        await asyncio.sleep(2)  # Simulate step execution time
        
        return {
            'success': True,
            'result': {'step_id': step.step_id, 'output': 'Step completed successfully'},
            'error': None
        }
    
    def _aggregate_results(self, task: WorkflowTask) -> Dict[str, Any]:
        """Aggregate results from all steps"""
        results = {}
        for step in task.steps:
            if step.status == TaskState.COMPLETED and step.result:
                results[step.step_id] = step.result
        
        return {
            'task_id': task.task_id,
            'name': task.name,
            'total_steps': len(task.steps),
            'completed_steps': len([s for s in task.steps if s.status == TaskState.COMPLETED]),
            'failed_steps': len([s for s in task.steps if s.status == TaskState.FAILED]),
            'step_results': results,
            'execution_time': (task.completed_at - task.started_at).total_seconds() if task.started_at and task.completed_at else None
        }
    
    async def _save_task(self, task: WorkflowTask) -> None:
        """Save task to Redis"""
        try:
            task_data = asdict(task)
            # Convert datetime objects to strings
            task_data['created_at'] = task_data['created_at'].isoformat()
            if task_data['started_at']:
                task_data['started_at'] = task_data['started_at'].isoformat()
            if task_data['completed_at']:
                task_data['completed_at'] = task_data['completed_at'].isoformat()
            
            for step_data in task_data['steps']:
                if step_data['started_at']:
                    step_data['started_at'] = step_data['started_at'].isoformat()
                if step_data['completed_at']:
                    step_data['completed_at'] = step_data['completed_at'].isoformat()
            
            await self.redis_client.set(f"task:{task.task_id}", json.dumps(task_data))
            
        except Exception as e:
            logger.error(f"Failed to save task {task.task_id}: {e}")
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and progress"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        
        # Calculate progress
        total_steps = len(task.steps)
        completed_steps = len([s for s in task.steps if s.status == TaskState.COMPLETED])
        failed_steps = len([s for s in task.steps if s.status == TaskState.FAILED])
        
        return {
            'task_id': task.task_id,
            'name': task.name,
            'description': task.description,
            'status': task.status.value,
            'priority': task.priority.value,
            'created_at': task.created_at.isoformat(),
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'progress': {
                'total_steps': total_steps,
                'completed_steps': completed_steps,
                'failed_steps': failed_steps,
                'pending_steps': total_steps - completed_steps - failed_steps
            },
            'result': task.result,
            'error': task.error,
            'metadata': task.metadata
        }
    
    async def list_tasks(self, status: Optional[TaskState] = None) -> List[Dict[str, Any]]:
        """List all tasks, optionally filtered by status"""
        tasks = []
        for task in self.tasks.values():
            if status is None or task.status == status:
                task_info = await self.get_task_status(task.task_id)
                if task_info:
                    tasks.append(task_info)
        
        # Sort by priority and creation time
        tasks.sort(key=lambda t: (t['priority'], t['created_at']))
        return tasks
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id not in self.running_tasks:
            logger.warning(f"Task {task_id} is not running")
            return False
        
        # Cancel the running task
        task = self.running_tasks[task_id]
        task.cancel()
        
        # Update task status
        if task_id in self.tasks:
            self.tasks[task_id].status = TaskState.CANCELLED
            self.tasks[task_id].completed_at = datetime.now()
            await self._save_task(self.tasks[task_id])
        
        # Clean up
        del self.running_tasks[task_id]
        
        logger.info(f"Cancelled task: {task_id}")
        return True
    
    async def cleanup_completed_tasks(self, hours_old: int = 24) -> int:
        """Clean up completed tasks older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours_old)
        deleted_count = 0
        
        tasks_to_delete = []
        for task_id, task in self.tasks.items():
            if (task.status in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED] and
                task.completed_at and task.completed_at < cutoff_time):
                tasks_to_delete.append(task_id)
        
        for task_id in tasks_to_delete:
            # Remove from Redis
            await self.redis_client.delete(f"task:{task_id}")
            
            # Remove from memory
            del self.tasks[task_id]
            
            deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old tasks")
        
        return deleted_count


async def main():
    """Main entry point for testing"""
    coordinator = TaskCoordinator()
    await coordinator.initialize()
    
    # Example workflow task
    workflow_steps = [
        {
            'type': 'command',
            'description': 'Initialize environment',
            'command': 'echo "Initializing..."',
            'dependencies': [],
            'timeout': 60,
            'max_retries': 2
        },
        {
            'type': 'command', 
            'description': 'Run analysis',
            'command': 'echo "Analyzing..."',
            'dependencies': ['step_0'],
            'timeout': 120,
            'max_retries': 1
        },
        {
            'type': 'command',
            'description': 'Generate report',
            'command': 'echo "Reporting..."',
            'dependencies': ['step_1'],
            'timeout': 60,
            'max_retries': 1
        }
    ]
    
    # Create and execute workflow
    task_id = await coordinator.create_workflow_task(
        name="Example Workflow",
        description="Example multi-step workflow",
        steps=workflow_steps,
        priority=TaskPriority.HIGH
    )
    
    success = await coordinator.execute_task(task_id)
    if success:
        print(f"Started workflow task: {task_id}")
        
        # Monitor task progress
        while True:
            status = await coordinator.get_task_status(task_id)
            if status:
                print(f"Task {task_id}: {status['status']} - {status['progress']}")
                if status['status'] in ['completed', 'failed', 'cancelled']:
                    break
            await asyncio.sleep(5)
    else:
        print("Failed to start workflow task")


if __name__ == "__main__":
    asyncio.run(main())
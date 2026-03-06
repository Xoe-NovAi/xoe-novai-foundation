#!/usr/bin/env python3
"""
Multi-Agent Coordinator for XNAi Foundation

This script coordinates multiple CLI agent accounts to perform parallel development tasks,
avoiding rate limiting and improving productivity through intelligent task distribution.

Author: XNAi Foundation
License: AGPL-3.0-only
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
import uuid
from asyncio import Queue, Task
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Awaitable
from pathlib import Path

import redis.asyncio as redis
import yaml
from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class TaskPriority(int, Enum):
    """Task priority enumeration"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentInfo:
    """Agent information"""
    agent_id: str
    name: str
    role: str
    capabilities: List[str]
    status: AgentStatus
    last_heartbeat: datetime
    current_task: Optional[str]
    performance_metrics: Dict[str, float]


@dataclass
class TaskInfo:
    """Task information"""
    task_id: str
    task_type: str
    description: str
    priority: TaskPriority
    required_capabilities: List[str]
    assigned_agent: Optional[str]
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[Dict[str, Any]]
    error: Optional[str]


class MultiAgentConfig(BaseModel):
    """Multi-agent configuration model"""
    enabled: bool = True
    coordination_backend: str = "redis_streams"
    task_queue: str = "xnai:agent_tasks"
    result_aggregator: str = "xnai:agent_results"
    heartbeat_interval: int = 30
    timeout: int = 300
    
    accounts: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    coordination: Dict[str, Any] = Field(default_factory=dict)
    communication: Dict[str, Any] = Field(default_factory=dict)
    security: Dict[str, Any] = Field(default_factory=dict)
    monitoring: Dict[str, Any] = Field(default_factory=dict)
    error_handling: Dict[str, Any] = Field(default_factory=dict)
    performance: Dict[str, Any] = Field(default_factory=dict)
    logging: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('coordination_backend')
    def validate_backend(cls, v):
        if v not in ['redis_streams', 'rabbitmq', 'kafka']:
            raise ValueError('Invalid coordination backend')
        return v


class MultiAgentCoordinator:
    """Main multi-agent coordinator class"""
    
    def __init__(self, config_path: str = "configs/multi-agent-config.yaml"):
        """
        Initialize the multi-agent coordinator
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config: Optional[MultiAgentConfig] = None
        self.redis_client: Optional[redis.Redis] = None
        self.agents: Dict[str, AgentInfo] = {}
        self.tasks: Dict[str, TaskInfo] = {}
        self.task_queue: Queue = Queue()
        self.running = False
        self.tasks: Dict[str, Task] = {}
        
        # Event handlers
        self.on_task_completed: Optional[Callable[[TaskInfo], Awaitable[None]]] = None
        self.on_agent_status_changed: Optional[Callable[[AgentInfo], Awaitable[None]]] = None
        
    async def load_config(self) -> None:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Get environment-specific overrides
            env = os.getenv('XNAI_ENV', 'development')
            if 'environments' in config_data and env in config_data['environments']:
                env_config = config_data['environments'][env]
                # Deep merge environment config
                self._deep_merge(config_data, env_config)
            
            self.config = MultiAgentConfig(**config_data['multi_agent'])
            logger.info(f"Loaded configuration for environment: {env}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """Deep merge override dict into base dict"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    async def initialize(self) -> None:
        """Initialize the coordinator"""
        if not self.config:
            await self.load_config()
        
        if not self.config.enabled:
            logger.info("Multi-agent coordination is disabled")
            return
        
        # Initialize Redis connection
        await self._init_redis()
        
        # Initialize agents
        await self._init_agents()
        
        # Start background tasks
        self.tasks['heartbeat'] = asyncio.create_task(self._heartbeat_loop())
        self.tasks['task_processor'] = asyncio.create_task(self._task_processor())
        self.tasks['agent_monitor'] = asyncio.create_task(self._agent_monitor())
        self.tasks['result_collector'] = asyncio.create_task(self._result_collector())
        
        logger.info("Multi-agent coordinator initialized")
    
    async def _init_redis(self) -> None:
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                os.getenv('REDIS_URL', 'redis://localhost:6379'),
                decode_responses=False  # Keep binary for proper serialization
            )
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def _init_agents(self) -> None:
        """Initialize agent registry"""
        for account_name, account_config in self.config.accounts.items():
            agent_info = AgentInfo(
                agent_id=f"{account_name}_{uuid.uuid4().hex[:8]}",
                name=account_config['name'],
                role=account_config['role'],
                capabilities=account_config['capabilities'],
                status=AgentStatus.IDLE,
                last_heartbeat=datetime.now(),
                current_task=None,
                performance_metrics={}
            )
            self.agents[agent_info.agent_id] = agent_info
            
            # Register agent in Redis
            await self._register_agent(agent_info)
        
        logger.info(f"Initialized {len(self.agents)} agents")
    
    async def _register_agent(self, agent_info: AgentInfo) -> None:
        """Register agent in Redis"""
        agent_data = {
            'agent_id': agent_info.agent_id,
            'name': agent_info.name,
            'role': agent_info.role,
            'capabilities': agent_info.capabilities,
            'status': agent_info.status.value,
            'last_heartbeat': agent_info.last_heartbeat.isoformat(),
            'current_task': agent_info.current_task,
            'performance_metrics': agent_info.performance_metrics
        }
        
        await self.redis_client.hset(
            f"agent:{agent_info.agent_id}",
            mapping=agent_data
        )
        await self.redis_client.expire(f"agent:{agent_info.agent_id}", 300)  # 5 minute expiry
    
    async def _heartbeat_loop(self) -> None:
        """Main heartbeat loop"""
        while self.running:
            try:
                await self._send_heartbeats()
                await self._check_agent_health()
                await asyncio.sleep(self.config.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                await asyncio.sleep(5)
    
    async def _send_heartbeats(self) -> None:
        """Send heartbeats for all agents"""
        for agent_id, agent_info in self.agents.items():
            try:
                agent_info.last_heartbeat = datetime.now()
                await self._register_agent(agent_info)
            except Exception as e:
                logger.error(f"Failed to send heartbeat for agent {agent_id}: {e}")
    
    async def _check_agent_health(self) -> None:
        """Check agent health and update status"""
        now = datetime.now()
        for agent_id, agent_info in self.agents.items():
            time_since_heartbeat = now - agent_info.last_heartbeat
            
            if time_since_heartbeat > timedelta(seconds=self.config.heartbeat_interval * 3):
                if agent_info.status != AgentStatus.OFFLINE:
                    logger.warning(f"Agent {agent_id} is offline (no heartbeat for {time_since_heartbeat})")
                    agent_info.status = AgentStatus.OFFLINE
                    await self._notify_agent_status_changed(agent_info)
    
    async def _task_processor(self) -> None:
        """Main task processing loop"""
        while self.running:
            try:
                # Get next task from queue
                task_info = await self.task_queue.get()
                
                # Find suitable agent
                agent_id = await self._find_suitable_agent(task_info)
                if not agent_id:
                    logger.warning(f"No suitable agent found for task {task_info.task_id}")
                    await self._complete_task(task_info, TaskStatus.FAILED, error="No suitable agent available")
                    continue
                
                # Assign task to agent
                await self._assign_task(task_info, agent_id)
                
                # Send task to agent
                await self._send_task_to_agent(task_info, agent_id)
                
            except Exception as e:
                logger.error(f"Task processor error: {e}")
                await asyncio.sleep(1)
    
    async def _find_suitable_agent(self, task_info: TaskInfo) -> Optional[str]:
        """Find the most suitable agent for a task"""
        suitable_agents = []
        
        for agent_id, agent_info in self.agents.items():
            # Check if agent is available
            if agent_info.status != AgentStatus.IDLE:
                continue
            
            # Check capability match
            required_caps = set(task_info.required_capabilities)
            agent_caps = set(agent_info.capabilities)
            
            if required_caps.issubset(agent_caps):
                suitable_agents.append((agent_id, agent_info))
        
        if not suitable_agents:
            return None
        
        # Sort by priority and performance
        suitable_agents.sort(key=lambda x: (
            -x[1].performance_metrics.get('success_rate', 0.5),  # Higher success rate first
            x[1].performance_metrics.get('avg_response_time', 300)  # Lower response time first
        ))
        
        return suitable_agents[0][0]
    
    async def _assign_task(self, task_info: TaskInfo, agent_id: str) -> None:
        """Assign task to agent"""
        task_info.assigned_agent = agent_id
        task_info.status = TaskStatus.IN_PROGRESS
        task_info.started_at = datetime.now()
        
        # Update agent status
        agent_info = self.agents[agent_id]
        agent_info.status = AgentStatus.BUSY
        agent_info.current_task = task_info.task_id
        
        # Update in Redis
        await self._register_agent(agent_info)
    
    async def _send_task_to_agent(self, task_info: TaskInfo, agent_id: str) -> None:
        """Send task to agent via Redis Streams"""
        task_message = {
            'task_id': task_info.task_id,
            'task_type': task_info.task_type,
            'description': task_info.description,
            'priority': task_info.priority.value,
            'required_capabilities': task_info.required_capabilities,
            'assigned_agent': agent_id,
            'created_at': task_info.created_at.isoformat(),
            'timeout': self.config.timeout
        }
        
        await self.redis_client.xadd(
            f"agent:{agent_id}:tasks",
            task_message
        )
        
        logger.info(f"Assigned task {task_info.task_id} to agent {agent_id}")
    
    async def _agent_monitor(self) -> None:
        """Monitor agent status and handle events"""
        while self.running:
            try:
                # Monitor agent streams for status updates
                await self._monitor_agent_streams()
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Agent monitor error: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_agent_streams(self) -> None:
        """Monitor agent streams for status updates and results"""
        for agent_id in self.agents.keys():
            try:
                # Check for new messages from agent
                messages = await self.redis_client.xread(
                    {f"agent:{agent_id}:results": "$"},
                    count=1,
                    block=100  # 100ms timeout
                )
                
                for stream, msgs in messages:
                    for msg_id, fields in msgs:
                        await self._handle_agent_result(agent_id, fields)
                        
            except Exception as e:
                logger.debug(f"No messages from agent {agent_id}: {e}")
    
    async def _handle_agent_result(self, agent_id: str, result_data: Dict[str, bytes]) -> None:
        """Handle agent result"""
        try:
            # Parse result data
            task_id = result_data[b'task_id'].decode()
            status = result_data[b'status'].decode()
            result = json.loads(result_data[b'result'].decode())
            error = result_data.get(b'error', b'').decode() if b'error' in result_data else None
            
            # Find task
            if task_id not in self.tasks:
                logger.warning(f"Unknown task result: {task_id}")
                return
            
            task_info = self.tasks[task_id]
            
            # Complete task
            await self._complete_task(task_info, TaskStatus(status), result, error)
            
            # Update agent status
            agent_info = self.agents[agent_id]
            agent_info.status = AgentStatus.IDLE
            agent_info.current_task = None
            
            await self._register_agent(agent_info)
            
        except Exception as e:
            logger.error(f"Error handling agent result: {e}")
    
    async def _result_collector(self) -> None:
        """Collect and aggregate results"""
        while self.running:
            try:
                # Check for completed tasks
                await self._collect_results()
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Result collector error: {e}")
                await asyncio.sleep(5)
    
    async def _collect_results(self) -> None:
        """Collect completed task results"""
        completed_tasks = [
            task for task in self.tasks.values()
            if task.status == TaskStatus.COMPLETED
        ]
        
        if completed_tasks:
            logger.info(f"Collected {len(completed_tasks)} completed tasks")
            
            # Notify completion handler
            for task in completed_tasks:
                if self.on_task_completed:
                    await self.on_task_completed(task)
    
    async def _complete_task(self, task_info: TaskInfo, status: TaskStatus, result: Optional[Dict] = None, error: Optional[str] = None) -> None:
        """Complete a task"""
        task_info.status = status
        task_info.completed_at = datetime.now()
        task_info.result = result
        task_info.error = error
        
        logger.info(f"Task {task_info.task_id} completed with status: {status}")
        
        # Notify completion handler
        if self.on_task_completed:
            await self.on_task_completed(task_info)
    
    async def _notify_agent_status_changed(self, agent_info: AgentInfo) -> None:
        """Notify agent status change"""
        if self.on_agent_status_changed:
            await self.on_agent_status_changed(agent_info)
    
    async def submit_task(self, task_type: str, description: str, priority: TaskPriority = TaskPriority.MEDIUM, required_capabilities: List[str] = None) -> str:
        """Submit a new task for processing"""
        if not self.config.enabled:
            raise Exception("Multi-agent coordination is disabled")
        
        task_id = str(uuid.uuid4())
        task_info = TaskInfo(
            task_id=task_id,
            task_type=task_type,
            description=description,
            priority=priority,
            required_capabilities=required_capabilities or [],
            assigned_agent=None,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            result=None,
            error=None
        )
        
        self.tasks[task_id] = task_info
        await self.task_queue.put(task_info)
        
        logger.info(f"Submitted task {task_id}: {description}")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[TaskInfo]:
        """Get task status"""
        return self.tasks.get(task_id)
    
    async def get_agent_status(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent status"""
        return self.agents.get(agent_id)
    
    async def list_agents(self) -> List[AgentInfo]:
        """List all agents"""
        return list(self.agents.values())
    
    async def list_tasks(self) -> List[TaskInfo]:
        """List all tasks"""
        return list(self.tasks.values())
    
    async def shutdown(self) -> None:
        """Shutdown the coordinator"""
        logger.info("Shutting down multi-agent coordinator...")
        
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks.values():
            task.cancel()
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Multi-agent coordinator shutdown complete")


async def main():
    """Main entry point"""
    coordinator = MultiAgentCoordinator()
    
    # Handle shutdown gracefully
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(coordinator.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await coordinator.initialize()
        coordinator.running = True
        
        # Example usage
        logger.info("Multi-agent coordinator is running")
        
        # Submit some example tasks
        task1 = await coordinator.submit_task(
            task_type="documentation",
            description="Generate API documentation for RAG service",
            priority=TaskPriority.HIGH,
            required_capabilities=["documentation"]
        )
        
        task2 = await coordinator.submit_task(
            task_type="code_generation",
            description="Implement FAISS optimization for Ryzen processors",
            priority=TaskPriority.MEDIUM,
            required_capabilities=["code_generation", "optimization"]
        )
        
        # Monitor tasks
        while coordinator.running:
            await asyncio.sleep(10)
            
            # Check task status
            status1 = await coordinator.get_task_status(task1)
            status2 = await coordinator.get_task_status(task2)
            
            if status1:
                logger.info(f"Task {task1}: {status1.status}")
            if status2:
                logger.info(f"Task {task2}: {status2.status}")
    
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        await coordinator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
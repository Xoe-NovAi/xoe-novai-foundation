#!/usr/bin/env python3
"""
Unified Agent Awareness Protocol (UAAP)
======================================

Comprehensive agent awareness system for the Omega Stack.
Provides environmental awareness, capability discovery, and cross-agent coordination.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

import redis
from prometheus_client import Gauge, Counter, Histogram

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of agents in the ecosystem."""
    GEMINI_CLI = "gemini_cli"
    CLINE_CLI = "cline_cli"
    COPILOT_CLI = "copilot_cli"
    OPENCODE_CLI = "opencode_cli"
    CLINE_EXTENSION = "cline_extension"
    COPILOT_EXTENSION = "copilot_extension"
    LOCAL_MODEL = "local_model"
    PERSISTENT_ENTITY = "persistent_entity"

class AgentCapability(Enum):
    """Capabilities available to agents."""
    MULTIMODAL = "multimodal"
    PROJECT_CONTEXT = "project_context"
    SUBDIRECTORY_AWARENESS = "subdirectory_awareness"
    FILE_OPERATIONS = "file_operations"
    AGENT_BUS_COMMUNICATION = "agent_bus_communication"
    LONG_CONTEXT = "long_context"
    AI_COMPRESSION = "ai_compression"
    VULKAN_ACCELERATION = "vulkan_acceleration"
    GTT_ADRENALINE = "gtt_adrenaline"
    HIERARCHICAL_MEMORY = "hierarchical_memory"
    MCP_INTEGRATION = "mcp_integration"

@dataclass
class AgentProfile:
    """Complete profile of an agent."""
    agent_id: str
    agent_type: AgentType
    capabilities: List[AgentCapability]
    environment_access: List[str]
    last_seen: float
    status: str  # active, idle, busy, offline
    resource_usage: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    session_context: Dict[str, Any]

class UnifiedAgentAwarenessProtocol:
    """
    Core UAAP implementation for comprehensive agent awareness.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/1"):
        self.redis_client = redis.from_url(redis_url)
        self.environment_map_path = Path("data/agent_environment_map.json")
        self.capability_registry_path = Path("data/agent_capabilities.json")
        
        # Ensure directories exist
        self.environment_map_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prometheus metrics
        self.agent_status_gauge = Gauge('uaap_agent_status', 'Agent status', ['agent_id', 'agent_type'])
        self.agent_resource_usage = Gauge('uaap_agent_resource_usage', 'Agent resource usage', ['agent_id', 'resource_type'])
        self.agent_performance = Gauge('uaap_agent_performance', 'Agent performance metrics', ['agent_id', 'metric_type'])
        self.session_quality = Histogram('uaap_session_quality', 'Session quality metrics', ['agent_id'])
        
        # Initialize
        self._load_environment_map()
        self._load_capability_registry()
        
    def _load_environment_map(self):
        """Load the environment map from disk."""
        if self.environment_map_path.exists():
            try:
                with open(self.environment_map_path, 'r') as f:
                    self.environment_map = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load environment map: {e}")
                self.environment_map = {}
        else:
            self.environment_map = {}
            
    def _save_environment_map(self):
        """Save the environment map to disk."""
        try:
            with open(self.environment_map_path, 'w') as f:
                json.dump(self.environment_map, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save environment map: {e}")
            
    def _load_capability_registry(self):
        """Load the capability registry from disk."""
        if self.capability_registry_path.exists():
            try:
                with open(self.capability_registry_path, 'r') as f:
                    self.capability_registry = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load capability registry: {e}")
                self.capability_registry = {}
        else:
            self.capability_registry = {}
            
    def _save_capability_registry(self):
        """Save the capability registry to disk."""
        try:
            with open(self.capability_registry_path, 'w') as f:
                json.dump(self.capability_registry, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save capability registry: {e}")
    
    async def register_agent(self, agent_profile: AgentProfile) -> bool:
        """Register an agent with the UAAP system."""
        try:
            # Update agent profile
            agent_profile.last_seen = time.time()
            
            # Store in Redis
            key = f"uaap:agent:{agent_profile.agent_id}"
            self.redis_client.setex(
                key, 
                300,  # 5 minute TTL
                json.dumps(asdict(agent_profile), default=str)
            )
            
            # Update environment map
            self.environment_map[agent_profile.agent_id] = {
                "type": agent_profile.agent_type.value,
                "capabilities": [cap.value for cap in agent_profile.capabilities],
                "environment_access": agent_profile.environment_access,
                "last_seen": agent_profile.last_seen,
                "status": agent_profile.status
            }
            self._save_environment_map()
            
            # Update capability registry
            for capability in agent_profile.capabilities:
                if capability.value not in self.capability_registry:
                    self.capability_registry[capability.value] = []
                if agent_profile.agent_id not in self.capability_registry[capability.value]:
                    self.capability_registry[capability.value].append(agent_profile.agent_id)
            self._save_capability_registry()
            
            # Update Prometheus metrics
            self.agent_status_gauge.labels(
                agent_id=agent_profile.agent_id,
                agent_type=agent_profile.agent_type.value
            ).set(1 if agent_profile.status == "active" else 0)
            
            logger.info(f"Registered agent: {agent_profile.agent_id} ({agent_profile.agent_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_profile.agent_id}: {e}")
            return False
    
    async def get_agent_profile(self, agent_id: str) -> Optional[AgentProfile]:
        """Get an agent's profile."""
        try:
            key = f"uaap:agent:{agent_id}"
            data = self.redis_client.get(key)
            if data:
                profile_data = json.loads(data)
                return AgentProfile(**profile_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get agent profile for {agent_id}: {e}")
            return None
    
    async def update_agent_status(self, agent_id: str, status: str, resource_usage: Dict[str, Any] = None) -> bool:
        """Update an agent's status and resource usage."""
        try:
            profile = await self.get_agent_profile(agent_id)
            if not profile:
                return False
                
            profile.status = status
            profile.last_seen = time.time()
            if resource_usage:
                profile.resource_usage.update(resource_usage)
            
            return await self.register_agent(profile)
        except Exception as e:
            logger.error(f"Failed to update agent status for {agent_id}: {e}")
            return False
    
    async def get_agents_by_capability(self, capability: AgentCapability) -> List[str]:
        """Get all agents that have a specific capability."""
        return self.capability_registry.get(capability.value, [])
    
    async def get_agents_by_type(self, agent_type: AgentType) -> List[str]:
        """Get all agents of a specific type."""
        agents = []
        for agent_id, env_data in self.environment_map.items():
            if env_data.get("type") == agent_type.value:
                agents.append(agent_id)
        return agents
    
    async def get_environment_awareness(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive environmental awareness for an agent."""
        try:
            profile = await self.get_agent_profile(agent_id)
            if not profile:
                return {}
            
            # Get system-wide agent status
            all_agents = await self.get_all_agents()
            
            # Calculate resource availability
            resource_availability = await self._calculate_resource_availability()
            
            # Get relevant environment context
            environment_context = {
                "agent_profile": asdict(profile),
                "active_agents": [a for a in all_agents if a["status"] == "active"],
                "resource_availability": resource_availability,
                "environment_map": self.environment_map,
                "timestamp": time.time()
            }
            
            return environment_context
            
        except Exception as e:
            logger.error(f"Failed to get environment awareness for {agent_id}: {e}")
            return {}
    
    async def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all registered agents."""
        agents = []
        for agent_id in self.environment_map:
            profile = await self.get_agent_profile(agent_id)
            if profile:
                agents.append(asdict(profile))
        return agents
    
    async def _calculate_resource_availability(self) -> Dict[str, Any]:
        """Calculate available system resources."""
        try:
            # Get resource usage from all agents
            all_agents = await self.get_all_agents()
            
            total_cpu = 0
            total_memory = 0
            total_gpu = 0
            active_agents = 0
            
            for agent in all_agents:
                if agent["status"] == "active":
                    active_agents += 1
                    resource_usage = agent.get("resource_usage", {})
                    total_cpu += resource_usage.get("cpu_usage", 0)
                    total_memory += resource_usage.get("memory_usage", 0)
                    total_gpu += resource_usage.get("gpu_usage", 0)
            
            # Calculate availability (assuming system limits)
            system_limits = {
                "max_cpu": 100.0,  # 100%
                "max_memory": 16.0,  # 16GB
                "max_gpu": 8.0  # 8GB VRAM
            }
            
            availability = {
                "cpu_available": max(0, system_limits["max_cpu"] - total_cpu),
                "memory_available": max(0, system_limits["max_memory"] - total_memory),
                "gpu_available": max(0, system_limits["max_gpu"] - total_gpu),
                "active_agents": active_agents,
                "system_load": {
                    "cpu_utilization": (total_cpu / system_limits["max_cpu"]) * 100,
                    "memory_utilization": (total_memory / system_limits["max_memory"]) * 100,
                    "gpu_utilization": (total_gpu / system_limits["max_gpu"]) * 100
                }
            }
            
            return availability
            
        except Exception as e:
            logger.error(f"Failed to calculate resource availability: {e}")
            return {}
    
    async def coordinate_agents(self, task_type: str, required_capabilities: List[AgentCapability]) -> List[str]:
        """Coordinate agents for a specific task."""
        try:
            suitable_agents = []
            
            # Find agents with required capabilities
            for capability in required_capabilities:
                agents_with_capability = await self.get_agents_by_capability(capability)
                suitable_agents.extend(agents_with_capability)
            
            # Remove duplicates and filter by status
            suitable_agents = list(set(suitable_agents))
            active_agents = []
            
            for agent_id in suitable_agents:
                profile = await self.get_agent_profile(agent_id)
                if profile and profile.status == "active":
                    active_agents.append(agent_id)
            
            # Sort by performance metrics
            active_agents.sort(key=lambda x: self._get_agent_priority(x), reverse=True)
            
            logger.info(f"Coordinated {len(active_agents)} agents for task: {task_type}")
            return active_agents
            
        except Exception as e:
            logger.error(f"Failed to coordinate agents for {task_type}: {e}")
            return []
    
    def _get_agent_priority(self, agent_id: str) -> float:
        """Calculate priority score for an agent."""
        try:
            profile = asyncio.run(self.get_agent_profile(agent_id))
            if not profile:
                return 0.0
            
            # Calculate priority based on performance metrics
            metrics = profile.performance_metrics
            success_rate = metrics.get("success_rate", 0.5)
            response_time = metrics.get("avg_response_time", 10.0)
            
            # Higher success rate and lower response time = higher priority
            priority = success_rate * (1.0 / max(response_time, 0.1))
            
            return priority
            
        except Exception as e:
            logger.error(f"Failed to calculate priority for {agent_id}: {e}")
            return 0.0
    
    async def cleanup_expired_agents(self):
        """Clean up expired agents from the registry."""
        try:
            current_time = time.time()
            expired_agents = []
            
            for agent_id, env_data in self.environment_map.items():
                last_seen = env_data.get("last_seen", 0)
                if current_time - last_seen > 600:  # 10 minutes
                    expired_agents.append(agent_id)
            
            # Remove expired agents
            for agent_id in expired_agents:
                del self.environment_map[agent_id]
                # Remove from capability registry
                for capability_list in self.capability_registry.values():
                    if agent_id in capability_list:
                        capability_list.remove(agent_id)
            
            if expired_agents:
                self._save_environment_map()
                self._save_capability_registry()
                logger.info(f"Cleaned up {len(expired_agents)} expired agents")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired agents: {e}")
    
    async def start_background_monitoring(self):
        """Start background monitoring of agent status."""
        logger.info("Starting UAAP background monitoring")
        
        while True:
            try:
                # Clean up expired agents
                await self.cleanup_expired_agents()
                
                # Update metrics
                all_agents = await self.get_all_agents()
                for agent in all_agents:
                    # Update Prometheus metrics
                    self.agent_status_gauge.labels(
                        agent_id=agent["agent_id"],
                        agent_type=agent["agent_type"]
                    ).set(1 if agent["status"] == "active" else 0)
                    
                    # Update resource usage metrics
                    for resource_type, usage in agent.get("resource_usage", {}).items():
                        self.agent_resource_usage.labels(
                            agent_id=agent["agent_id"],
                            resource_type=resource_type
                        ).set(usage)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in background monitoring: {e}")
                await asyncio.sleep(60)

# Global UAAP instance
_uaap_instance: Optional[UnifiedAgentAwarenessProtocol] = None

def get_uaap() -> UnifiedAgentAwarenessProtocol:
    """Get the global UAAP instance."""
    global _uaap_instance
    if _uaap_instance is None:
        _uaap_instance = UnifiedAgentAwarenessProtocol()
    return _uaap_instance

# Convenience functions
async def register_agent(agent_profile: AgentProfile) -> bool:
    """Register an agent with the UAAP system."""
    uaap = get_uaap()
    return await uaap.register_agent(agent_profile)

async def get_agent_profile(agent_id: str) -> Optional[AgentProfile]:
    """Get an agent's profile."""
    uaap = get_uaap()
    return await uaap.get_agent_profile(agent_id)

async def update_agent_status(agent_id: str, status: str, resource_usage: Dict[str, Any] = None) -> bool:
    """Update an agent's status and resource usage."""
    uaap = get_uaap()
    return await uaap.update_agent_status(agent_id, status, resource_usage)

async def get_environment_awareness(agent_id: str) -> Dict[str, Any]:
    """Get comprehensive environmental awareness for an agent."""
    uaap = get_uaap()
    return await uaap.get_environment_awareness(agent_id)

async def coordinate_agents(task_type: str, required_capabilities: List[AgentCapability]) -> List[str]:
    """Coordinate agents for a specific task."""
    uaap = get_uaap()
    return await uaap.coordinate_agents(task_type, required_capabilities)
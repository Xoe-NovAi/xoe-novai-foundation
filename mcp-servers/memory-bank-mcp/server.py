#!/usr/bin/env python3
"""
Memory Bank MCP Server
======================
Provides sovereign, offline-first memory bank access for deep inter-agent communication.
Implements progressive loading, context engineering, and A2A protocol patterns.

Key Features:
- Progressive context loading (Hot/Warm/Cold tiers)
- Agent capability discovery and registration
- Context versioning and synchronization
- Memory isolation with cross-agent sharing
- Event-driven updates for real-time coordination
"""

import asyncio
import json
import logging
import time
import hashlib
from typing import Dict, Any, List, Optional, AsyncGenerator, Generator
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import httpx
from redis.asyncio import Redis
import yaml

# MCP Server imports
from mcp.server import Server
from mcp.server.models import (
    InitializationOptions,
    Tool,
    ToolCallResult,
    TextContent,
    ToolUseContent,
)
from mcp.server.server import Server as MCPServer
from mcp.server.stdio import stdio_server

# XNAi Foundation imports
from app.XNAi_rag_app.core.config_loader import load_config
from app.XNAi_rag_app.core.logging_config import get_logger
from app.XNAi_rag_app.core.dependencies import get_vectorstore, get_llm_async
from app.XNAi_rag_app.core.agent_bus import AgentBusClient

logger = get_logger(__name__)

class ContextTier(str, Enum):
    """Memory bank context tiers for progressive loading."""
    HOT = "hot"      # Frequently accessed, <100MB
    WARM = "warm"    # Moderately accessed, <500MB  
    COLD = "cold"    # Rarely accessed, <2GB

class ContextType(str, Enum):
    """Types of context stored in memory bank."""
    PROJECT = "project"
    TECHNICAL = "technical"
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"
    TEMPORAL = "temporal"

@dataclass
class AgentCapability:
    """Agent capability registration."""
    agent_id: str
    capabilities: List[str]
    memory_limit_gb: float
    last_seen: datetime
    performance_score: float = 0.0

@dataclass
class ContextMetadata:
    """Metadata for context entries."""
    context_id: str
    agent_id: str
    context_type: ContextType
    tier: ContextTier
    version: int
    created_at: datetime
    last_modified: datetime
    size_bytes: int
    access_count: int = 0
    relevance_score: float = 0.0

@dataclass
class ContextSync:
    """Context synchronization request."""
    source_agent: str
    target_agent: str
    context_id: str
    sync_type: str  # "full", "delta", "stream"
    priority: int = 1

class MemoryBankMCP:
    """Memory Bank MCP Server implementation."""
    
    def __init__(self):
        self.config = load_config()
        self.redis_url = self.config.get('redis', {}).get('url', 'redis://localhost:6379')
        self.memory_bank_path = Path(self.config.get('paths', {}).get('memory_bank', './memory_bank'))
        self.max_memory_gb = 4.0  # Conservative limit for 6GB constraint
        
        # Redis connection
        self.redis: Optional[Redis] = None
        
        # Agent registry
        self.agents: Dict[str, AgentCapability] = {}
        self.agent_heartbeat_interval = 30  # seconds
        
        # Context management
        self.context_cache: Dict[str, Dict] = {}
        self.context_versions: Dict[str, int] = {}
        
        # Progressive loading
        self.tier_thresholds = {
            ContextTier.HOT: 100 * 1024 * 1024,    # 100MB
            ContextTier.WARM: 500 * 1024 * 1024,   # 500MB
            ContextTier.COLD: 2 * 1024 * 1024 * 1024  # 2GB
        }
        
        # Performance tracking
        self.performance_metrics = {
            'context_loads': 0,
            'sync_operations': 0,
            'agent_registrations': 0,
            'memory_efficiency': 0.0
        }
        
        logger.info("Memory Bank MCP Server initialized")

    async def initialize(self):
        """Initialize server components."""
        try:
            # Initialize Redis connection
            self.redis = Redis.from_url(self.redis_url)
            await self.redis.ping()
            logger.info("Redis connection established")
            
            # Initialize memory bank directory
            self.memory_bank_path.mkdir(parents=True, exist_ok=True)
            
            # Start background tasks
            asyncio.create_task(self._agent_heartbeat_monitor())
            asyncio.create_task(self._context_cleanup_task())
            
            logger.info("Memory Bank MCP Server fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Memory Bank MCP: {e}")
            raise

    async def _agent_heartbeat_monitor(self):
        """Monitor agent heartbeats and clean up stale agents."""
        while True:
            try:
                current_time = datetime.now()
                stale_threshold = timedelta(seconds=self.agent_heartbeat_interval * 3)
                
                # Remove stale agents
                stale_agents = [
                    agent_id for agent_id, agent in self.agents.items()
                    if current_time - agent.last_seen > stale_threshold
                ]
                
                for agent_id in stale_agents:
                    del self.agents[agent_id]
                    logger.info(f"Removed stale agent: {agent_id}")
                
                await asyncio.sleep(self.agent_heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Agent heartbeat monitor error: {e}")
                await asyncio.sleep(5)

    async def _context_cleanup_task(self):
        """Clean up old context versions and optimize memory usage."""
        while True:
            try:
                # Clean up old context versions (keep last 3 versions)
                for context_id, version in self.context_versions.items():
                    if version > 3:
                        # Remove old versions from Redis
                        for old_version in range(1, version - 2):
                            key = f"memory_bank:context:{context_id}:v{old_version}"
                            await self.redis.delete(key)
                
                # Update memory efficiency metrics
                total_memory = sum(meta.get('size_bytes', 0) for meta in self.context_cache.values())
                self.performance_metrics['memory_efficiency'] = min(1.0, total_memory / (self.max_memory_gb * 1024**3))
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Context cleanup task error: {e}")
                await asyncio.sleep(30)

    async def register_agent(self, agent_id: str, capabilities: List[str], memory_limit_gb: float) -> Dict[str, Any]:
        """Register an agent with its capabilities."""
        try:
            capability = AgentCapability(
                agent_id=agent_id,
                capabilities=capabilities,
                memory_limit_gb=memory_limit_gb,
                last_seen=datetime.now(),
                performance_score=0.0
            )
            
            self.agents[agent_id] = capability
            
            # Store in Redis for persistence
            await self.redis.hset(
                f"memory_bank:agents:{agent_id}",
                mapping=asdict(capability)
            )
            
            self.performance_metrics['agent_registrations'] += 1
            
            logger.info(f"Registered agent: {agent_id} with capabilities: {capabilities}")
            
            return {
                "status": "success",
                "agent_id": agent_id,
                "capabilities": capabilities,
                "memory_limit_gb": memory_limit_gb,
                "registration_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            return {"status": "error", "message": str(e)}

    async def get_context(self, agent_id: str, context_type: str, tier: str = "hot") -> Dict[str, Any]:
        """Get context for an agent with progressive loading."""
        try:
            self.performance_metrics['context_loads'] += 1
            
            # Validate agent
            if agent_id not in self.agents:
                return {"status": "error", "message": f"Agent {agent_id} not registered"}
            
            # Determine context tier
            try:
                context_tier = ContextTier(tier)
            except ValueError:
                context_tier = ContextTier.HOT
            
            # Generate context ID
            context_id = f"{agent_id}:{context_type}:{context_tier.value}"
            
            # Check cache first
            if context_id in self.context_cache:
                cached_context = self.context_cache[context_id]
                cached_context['access_count'] += 1
                cached_context['last_accessed'] = datetime.now().isoformat()
                
                logger.info(f"Cache hit for context: {context_id}")
                return {
                    "status": "success",
                    "context_id": context_id,
                    "context": cached_context,
                    "source": "cache",
                    "tier": context_tier.value
                }
            
            # Load from persistent storage
            context_data = await self._load_context_from_storage(context_id, context_tier)
            
            if context_data:
                # Cache the loaded context
                self.context_cache[context_id] = context_data
                self.context_versions[context_id] = context_data.get('version', 1)
                
                logger.info(f"Loaded context from storage: {context_id}")
                return {
                    "status": "success",
                    "context_id": context_id,
                    "context": context_data,
                    "source": "storage",
                    "tier": context_tier.value
                }
            
            # If not found, create empty context
            empty_context = {
                "context_id": context_id,
                "agent_id": agent_id,
                "context_type": context_type,
                "tier": context_tier.value,
                "version": 1,
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "size_bytes": 0,
                "access_count": 1,
                "relevance_score": 0.0,
                "content": {}
            }
            
            self.context_cache[context_id] = empty_context
            self.context_versions[context_id] = 1
            
            logger.info(f"Created empty context: {context_id}")
            return {
                "status": "success",
                "context_id": context_id,
                "context": empty_context,
                "source": "empty",
                "tier": context_tier.value
            }
            
        except Exception as e:
            logger.error(f"Failed to get context for {agent_id}: {e}")
            return {"status": "error", "message": str(e)}

    async def update_context(self, agent_id: str, context_type: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update context for an agent."""
        try:
            # Validate agent
            if agent_id not in self.agents:
                return {"status": "error", "message": f"Agent {agent_id} not registered"}
            
            # Generate context ID
            context_id = f"{agent_id}:{context_type}:hot"
            
            # Update version
            current_version = self.context_versions.get(context_id, 0) + 1
            
            # Create updated context
            updated_context = {
                "context_id": context_id,
                "agent_id": agent_id,
                "context_type": context_type,
                "tier": "hot",
                "version": current_version,
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "size_bytes": len(json.dumps(context_data).encode()),
                "access_count": 0,
                "relevance_score": context_data.get('relevance_score', 0.0),
                "content": context_data
            }
            
            # Update cache
            self.context_cache[context_id] = updated_context
            self.context_versions[context_id] = current_version
            
            # Store in Redis
            await self.redis.set(
                f"memory_bank:context:{context_id}:v{current_version}",
                json.dumps(updated_context)
            )
            
            # Publish update event
            await self.redis.publish(
                "memory_bank:context_updates",
                json.dumps({
                    "event_type": "context_updated",
                    "context_id": context_id,
                    "agent_id": agent_id,
                    "version": current_version,
                    "timestamp": datetime.now().isoformat()
                })
            )
            
            logger.info(f"Updated context: {context_id} (version {current_version})")
            
            return {
                "status": "success",
                "context_id": context_id,
                "version": current_version,
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update context for {agent_id}: {e}")
            return {"status": "error", "message": str(e)}

    async def sync_context(self, source_agent: str, target_agent: str, context_id: str, sync_type: str = "full") -> Dict[str, Any]:
        """Synchronize context between agents."""
        try:
            self.performance_metrics['sync_operations'] += 1
            
            # Validate agents
            if source_agent not in self.agents:
                return {"status": "error", "message": f"Source agent {source_agent} not registered"}
            if target_agent not in self.agents:
                return {"status": "error", "message": f"Target agent {target_agent} not registered"}
            
            # Get source context
            source_context = self.context_cache.get(context_id)
            if not source_context:
                return {"status": "error", "message": f"Context {context_id} not found"}
            
            # Create sync request
            sync_request = ContextSync(
                source_agent=source_agent,
                target_agent=target_agent,
                context_id=context_id,
                sync_type=sync_type
            )
            
            # Store sync request in Redis
            sync_key = f"memory_bank:sync:{context_id}:{target_agent}"
            await self.redis.set(
                sync_key,
                json.dumps(asdict(sync_request))
            )
            
            # Publish sync event
            await self.redis.publish(
                "memory_bank:sync_requests",
                json.dumps({
                    "event_type": "sync_requested",
                    "sync_request": asdict(sync_request),
                    "timestamp": datetime.now().isoformat()
                })
            )
            
            logger.info(f"Context sync requested: {context_id} from {source_agent} to {target_agent}")
            
            return {
                "status": "success",
                "sync_request": asdict(sync_request),
                "message": "Sync request queued"
            }
            
        except Exception as e:
            logger.error(f"Failed to sync context: {e}")
            return {"status": "error", "message": str(e)}

    async def _load_context_from_storage(self, context_id: str, tier: ContextTier) -> Optional[Dict[str, Any]]:
        """Load context from persistent storage with tier-specific optimization."""
        try:
            # Try to load from Redis first
            for version in range(self.context_versions.get(context_id, 1), 0, -1):
                key = f"memory_bank:context:{context_id}:v{version}"
                data = await self.redis.get(key)
                if data:
                    return json.loads(data)
            
            # If not in Redis, try file system
            context_file = self.memory_bank_path / f"{context_id}.json"
            if context_file.exists():
                with open(context_file, 'r') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load context {context_id} from storage: {e}")
            return None

    async def get_capabilities(self) -> List[Tool]:
        """Get MCP server capabilities."""
        return [
            Tool(
                name="register_agent",
                description="Register an agent with its capabilities for memory bank access",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Unique identifier for the agent"
                        },
                        "capabilities": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of capabilities the agent supports"
                        },
                        "memory_limit_gb": {
                            "type": "number",
                            "description": "Maximum memory the agent can use in GB"
                        }
                    },
                    "required": ["agent_id", "capabilities", "memory_limit_gb"]
                }
            ),
            Tool(
                name="get_context",
                description="Get context for an agent with progressive loading support",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent identifier"
                        },
                        "context_type": {
                            "type": "string",
                            "enum": [ct.value for ct in ContextType],
                            "description": "Type of context to retrieve"
                        },
                        "tier": {
                            "type": "string",
                            "enum": [ct.value for ct in ContextTier],
                            "description": "Memory tier (hot/warm/cold) for progressive loading"
                        }
                    },
                    "required": ["agent_id", "context_type"]
                }
            ),
            Tool(
                name="update_context",
                description="Update context for an agent with versioning",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "Agent identifier"
                        },
                        "context_type": {
                            "type": "string",
                            "enum": [ct.value for ct in ContextType],
                            "description": "Type of context to update"
                        },
                        "context_data": {
                            "type": "object",
                            "description": "Context data to store"
                        }
                    },
                    "required": ["agent_id", "context_type", "context_data"]
                }
            ),
            Tool(
                name="sync_context",
                description="Synchronize context between agents",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source_agent": {
                            "type": "string",
                            "description": "Source agent identifier"
                        },
                        "target_agent": {
                            "type": "string",
                            "description": "Target agent identifier"
                        },
                        "context_id": {
                            "type": "string",
                            "description": "Context identifier to sync"
                        },
                        "sync_type": {
                            "type": "string",
                            "enum": ["full", "delta", "stream"],
                            "description": "Type of synchronization"
                        }
                    },
                    "required": ["source_agent", "target_agent", "context_id"]
                }
            ),
            Tool(
                name="get_performance_metrics",
                description="Get performance metrics for memory bank operations",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> ToolCallResult:
        """Handle MCP tool calls."""
        try:
            if name == "register_agent":
                result = await self.register_agent(
                    arguments["agent_id"],
                    arguments["capabilities"],
                    arguments["memory_limit_gb"]
                )
                return ToolCallResult(
                    content=json.dumps(result),
                    isError=result.get("status") == "error"
                )
            
            elif name == "get_context":
                result = await self.get_context(
                    arguments["agent_id"],
                    arguments["context_type"],
                    arguments.get("tier", "hot")
                )
                return ToolCallResult(
                    content=json.dumps(result),
                    isError=result.get("status") == "error"
                )
            
            elif name == "update_context":
                result = await self.update_context(
                    arguments["agent_id"],
                    arguments["context_type"],
                    arguments["context_data"]
                )
                return ToolCallResult(
                    content=json.dumps(result),
                    isError=result.get("status") == "error"
                )
            
            elif name == "sync_context":
                result = await self.sync_context(
                    arguments["source_agent"],
                    arguments["target_agent"],
                    arguments["context_id"],
                    arguments.get("sync_type", "full")
                )
                return ToolCallResult(
                    content=json.dumps(result),
                    isError=result.get("status") == "error"
                )
            
            elif name == "get_performance_metrics":
                return ToolCallResult(
                    content=json.dumps(self.performance_metrics),
                    isError=False
                )
            
            else:
                return ToolCallResult(
                    content=json.dumps({"status": "error", "message": f"Unknown tool: {name}"}),
                    isError=True
                )
                
        except Exception as e:
            logger.error(f"Tool call error: {e}")
            return ToolCallResult(
                content=json.dumps({"status": "error", "message": str(e)}),
                isError=True
            )

async def main():
    """Main entry point for Memory Bank MCP Server."""
    server = Server("memory-bank-mcp")
    
    # Initialize memory bank MCP
    memory_bank_mcp = MemoryBankMCP()
    await memory_bank_mcp.initialize()
    
    # Register capabilities
    capabilities = await memory_bank_mcp.get_capabilities()
    for tool in capabilities:
        server.add_tool(tool)
    
    # Handle tool calls
    @server.list_tools()
    async def list_tools():
        return await memory_bank_mcp.get_capabilities()
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]):
        return await memory_bank_mcp.handle_tool_call(name, arguments)
    
    # Start server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
        )

if __name__ == "__main__":
    asyncio.run(main())
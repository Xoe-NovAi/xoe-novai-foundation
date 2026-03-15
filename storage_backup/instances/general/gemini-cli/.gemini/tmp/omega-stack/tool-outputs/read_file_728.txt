#!/usr/bin/env python3
"""
Memory Bank MCP Server
======================
Provides sovereign, offline-first memory bank access for deep inter-agent communication.
Implements progressive loading, context engineering, and A2A protocol patterns.
Refactored for SSE transport using FastAPI.
"""

import asyncio
import json
import logging
import time
import hashlib
import sys
import os
from collections import OrderedDict
from typing import Dict, Any, List, Optional, AsyncGenerator, Generator
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
import httpx
from redis.asyncio import Redis
from pydantic import BaseModel, Field

# FastAPI and MCP Server imports
from fastapi import FastAPI, Request
from starlette.responses import Response
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
)
from mcp.server.sse import SseServerTransport

# XNAi Foundation imports
from XNAi_rag_app.core.config_loader import load_config
from XNAi_rag_app.core.logging_config import get_logger

try:
    from XNAi_rag_app.core.dependencies import get_vectorstore, get_llm_async
except ImportError:
    get_vectorstore = None
    get_llm_async = None

try:
    from XNAi_rag_app.core.agent_bus import AgentBusClient
except ImportError:
    AgentBusClient = None

from memory_bank_fallback import MemoryBankFallbackWrapper
from memory_bank_store import MemoryBankStore

# Setup logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = get_logger(__name__)
logger.info("Memory Bank MCP Script Started")

class ContextTier(str, Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"

class ContextType(str, Enum):
    PROJECT = "project"
    TECHNICAL = "technical"
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"
    TEMPORAL = "temporal"

@dataclass
class AgentCapability:
    agent_id: str
    capabilities: List[str]
    memory_limit_gb: float
    last_seen: datetime
    performance_score: float = 0.0

class MemoryBankMCP:
    def __init__(self):
        try:
            self.config = load_config()
        except:
            self.config = {}
        self.redis_url = self._get_redis_url()
        self.redis = None
        self.agents: Dict[str, AgentCapability] = {}
        # SESS-01: Synchronized storage path to /storage
        self.memory_bank_path = Path("/storage/memory_bank")
        # SESS-02: LRU Cache for context
        self.context_cache = OrderedDict()
        self.cache_limit = 100 # Max 100 context objects in memory
        self.performance_metrics = {
            "hits": 0,
            "misses": 0,
            "latency_ms": []
        }

    def _get_redis_url(self) -> str:
        host = os.getenv("REDIS_HOST", "localhost")
        port = os.getenv("REDIS_PORT", 6379)
        password = os.getenv("REDIS_PASSWORD", "")
        # SESS-02: Enforce rediss:// and ssl_cert_reqs=none for Metropolis Mesh
        protocol = "rediss" if password else "redis"
        url = f"{protocol}://:{password}@{host}:{port}/0"
        if protocol == "rediss":
            url += "?ssl_cert_reqs=none"
        return url

    async def initialize(self) -> bool:
        """Initialize connections and storage."""
        try:
            if not self.redis:
                # SESS-02: Standardize decode_responses=True and handle TLS
                self.redis = Redis.from_url(
                    self.redis_url, 
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            
            # Test connection
            await self.redis.ping()
            
            # SESS-01: Synchronized storage path
            self.memory_bank_path.mkdir(parents=True, exist_ok=True)
            logger.info("Memory Bank MCP initialized with Redis backend")
            return True
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            self.redis = None # Reset so next call tries again
            return False

    async def _ensure_redis(self) -> bool:
        """Ensure Redis is connected, attempt reconnection if not."""
        if self.redis:
            try:
                await self.redis.ping()
                return True
            except:
                logger.warning("Redis connection lost, attempting to reconnect...")
                self.redis = None
        
        return await self.initialize()

    async def register_agent(self, agent_id: str, capabilities: list, memory_limit_gb: float) -> dict:
        """Register an agent and persist metadata in Redis."""
        now = datetime.now(timezone.utc)
        capability = AgentCapability(
            agent_id=agent_id,
            capabilities=capabilities,
            memory_limit_gb=memory_limit_gb,
            last_seen=now
        )
        self.agents[agent_id] = capability
        
        # SESS-02: Persist in Redis
        if await self._ensure_redis():
            try:
                agent_data = asdict(capability)
                agent_data["last_seen"] = now.isoformat()
                await self.redis.hset("xnai:agents", agent_id, json.dumps(agent_data))
            except Exception as e:
                logger.warning(f"Failed to persist agent in Redis: {e}")

        return {"status": "success", "agent_id": agent_id}

    async def get_context(self, agent_id: str, context_type: str, tier: str = "hot", keys: list = None) -> dict:
        """Get context from LRU Cache, Redis, or Filesystem."""
        context_id = f"{agent_id}:{context_type}:{tier}"
        redis_key = f"xnai:ctx:{context_id}"
        
        # 1. Try LRU Cache
        if context_id in self.context_cache:
            self.performance_metrics["hits"] += 1
            self.context_cache.move_to_end(context_id)
            data = self.context_cache[context_id]
            if keys:
                return {k: data.get(k) for k in keys if k in data}
            return data

        self.performance_metrics["misses"] += 1
        
        # 2. Try Redis
        data = None
        if await self._ensure_redis():
            try:
                data_str = await self.redis.get(redis_key)
                if data_str:
                    data = json.loads(data_str)
            except Exception as e:
                logger.warning(f"Redis get_context failed: {e}")

        # 3. Fallback to Filesystem
        if not data:
            context_file = self.memory_bank_path / f"{agent_id}_{context_type}_{tier}.json"
            if context_file.exists():
                try:
                    with open(context_file, 'r') as f:
                        data = json.load(f)
                        # Sync back to Redis
                        if self.redis:
                            await self.redis.set(redis_key, json.dumps(data))
                except Exception as e:
                    logger.error(f"Filesystem read failed: {e}")

        if data:
            # Update LRU Cache
            self.context_cache[context_id] = data
            if len(self.context_cache) > self.cache_limit:
                self.context_cache.popitem(last=False)
            
            if keys:
                return {k: data.get(k) for k in keys if k in data}
            return data

        return {"status": "success", "content": {}, "source": "empty"}

    async def update_context(self, agent_id: str, context_type: str, context_data: dict, tier: str = "hot") -> dict:
        """Update context with Write-Through (LRU + Redis + Filesystem)."""
        context_id = f"{agent_id}:{context_type}:{tier}"
        redis_key = f"xnai:ctx:{context_id}"
        context_file = self.memory_bank_path / f"{agent_id}_{context_type}_{tier}.json"
        
        # Load existing data (Try Cache -> Redis -> Filesystem)
        existing_data = await self.get_context(agent_id, context_type, tier)
        if isinstance(existing_data, dict) and "status" in existing_data and existing_data["status"] == "success" and "content" in existing_data:
            existing_data = {} # Reset if it was just the empty template
        
        # Update
        existing_data.update(context_data)
        data_json = json.dumps(existing_data)
        
        # 1. Update LRU Cache
        self.context_cache[context_id] = existing_data
        self.context_cache.move_to_end(context_id)
        if len(self.context_cache) > self.cache_limit:
            self.context_cache.popitem(last=False)
        
        # 2. Update Redis
        if await self._ensure_redis():
            try:
                await self.redis.set(redis_key, data_json)
            except Exception as e:
                logger.error(f"Redis update failed: {e}")

        # 3. Update Filesystem (Durability)
        try:
            with open(context_file, 'w') as f:
                f.write(data_json)
        except Exception as e:
            logger.error(f"Filesystem write failed: {e}")
        
        return {"status": "success", "context_id": context_id}

    async def checkpoint_session(self, session_id: str, agent_id: str) -> dict:
        """Trigger a manual checkpoint/summary for a session via Agent Bus."""
        if AgentBusClient:
            async with AgentBusClient(agent_id) as bus:
                payload = {"session_id": session_id, "agent_id": agent_id, "timestamp": datetime.now().isoformat()}
                task_id = await bus.send_task(target_did="worker:librarian:*", task_type="manual_checkpoint", payload=payload)
                return {"status": "success", "task_id": task_id, "message": f"Checkpoint task {task_id} sent to Librarian."}
        return {"status": "error", "message": "AgentBusClient not available"}

    async def rehydrate_session(self, session_id: str, agent_id: str) -> dict:
        """Request the Librarian to rehydrate a session from archives."""
        if AgentBusClient:
            async with AgentBusClient(agent_id) as bus:
                payload = {"session_id": session_id, "agent_id": agent_id, "timestamp": datetime.now().isoformat()}
                task_id = await bus.send_task(target_did="worker:librarian:*", task_type="rehydrate_session", payload=payload)
                return {"status": "success", "task_id": task_id, "message": f"Rehydration task {task_id} sent to Librarian."}
        return {"status": "error", "message": "AgentBusClient not available"}

    async def get_capabilities(self) -> List[Tool]:
        """Return list of available tools."""
        return [
            Tool(
                name="register_agent",
                description="Register a new agent with capabilities and memory limits",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string"},
                        "capabilities": {"type": "array", "items": {"type": "string"}},
                        "memory_limit_gb": {"type": "number"}
                    },
                    "required": ["agent_id", "capabilities", "memory_limit_gb"]
                }
            ),
            Tool(
                name="get_context",
                description="Retrieve context for an agent",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string"},
                        "context_type": {"type": "string"},
                        "tier": {"type": "string", "enum": ["hot", "warm", "cold"]},
                        "keys": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["agent_id", "context_type"]
                }
            ),
            Tool(
                name="update_context",
                description="Update context with new data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string"},
                        "context_type": {"type": "string"},
                        "context_data": {"type": "object"},
                        "tier": {"type": "string", "enum": ["hot", "warm", "cold"]}
                    },
                    "required": ["agent_id", "context_type", "context_data"]
                }
            ),
            Tool(
                name="checkpoint_session",
                description="Trigger a manual checkpoint/summary for a session",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "agent_id": {"type": "string"}
                    },
                    "required": ["session_id", "agent_id"]
                }
            ),
            Tool(
                name="rehydrate_session",
                description="Rehydrate a session from archives",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "agent_id": {"type": "string"}
                    },
                    "required": ["session_id", "agent_id"]
                }
            )
        ]

async def create_mcp_server():
    server = Server("memory-bank-mcp")
    mcp_instance = MemoryBankMCP()
    fallback_store = MemoryBankStore()
    memory_bank_mcp = MemoryBankFallbackWrapper(mcp_instance, fallback_store)
    
    _initialized = False
    
    async def _ensure_initialized():
        nonlocal _initialized
        if not _initialized:
            try:
                await memory_bank_mcp.initialize()
                _initialized = True
            except Exception as e:
                logger.error(f"Initialization failed: {e}")
                _initialized = True

    @server.list_tools()
    async def list_tools():
        return await mcp_instance.get_capabilities()

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]):
        await _ensure_initialized()
        return await memory_bank_mcp.handle_tool_call(name, arguments)
    
    return server

app = FastAPI(title="Memory Bank MCP Server (SSE)")
sse = SseServerTransport("/messages/")

@app.get("/sse")
async def handle_sse(request: Request):
    server = await create_mcp_server()
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options()
        )

@app.post("/messages/")
async def handle_messages(request: Request):
    await sse.handle_post_message(request.scope, request.receive, request._send)
    return Response(status_code=204)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_keep_alive=65)

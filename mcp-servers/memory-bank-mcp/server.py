#!/usr/bin/env python3
"""
Memory Bank MCP Server
======================
Provides sovereign, offline-first memory bank access for deep inter-agent communication.
Implements progressive loading, context engineering, and A2A protocol patterns.
Supports both SSE (FastAPI) and stdio transports.
"""

import asyncio
import json
import logging
import time
import hashlib
import sys
import os
import argparse
from collections import OrderedDict
from typing import Dict, Any, List, Optional, AsyncGenerator, Generator
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
import httpx
from redis.asyncio import Redis
from pydantic import BaseModel, Field

# MCP Server imports
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
)
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server

# FastAPI imports
try:
    from fastapi import FastAPI, Request
    from starlette.responses import Response
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

# XNAi Foundation imports
try:
    from XNAi_rag_app.core.config_loader import load_config
    from XNAi_rag_app.core.logging_config import get_logger
except ImportError:
    def load_config(): return {}
    def get_logger(name): return logging.getLogger(name)

from memory_bank_fallback import MemoryBankFallbackWrapper
from memory_bank_store import MemoryBankStore

# Setup logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = get_logger(__name__)

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
        # Centralized storage path
        self.memory_bank_path = Path("/storage/memory_bank")
        if not self.memory_bank_path.exists():
            # Fallback for host-side execution
            self.memory_bank_path = Path("./storage/memory_bank")
            
        self.context_cache = OrderedDict()
        self.cache_limit = 100
        self.performance_metrics = {
            "hits": 0,
            "misses": 0,
            "latency_ms": []
        }

    def _get_redis_url(self) -> str:
        host = os.getenv("REDIS_HOST", "localhost")
        port = os.getenv("REDIS_PORT", 6379)
        password = os.getenv("REDIS_PASSWORD", "")
        protocol = "rediss" if password else "redis"
        url = f"{protocol}://:{password}@{host}:{port}/0"
        if protocol == "rediss":
            url += "?ssl_cert_reqs=none"
        return url

    async def initialize(self) -> bool:
        """Initialize connections and storage."""
        try:
            if not self.redis:
                self.redis = Redis.from_url(
                    self.redis_url, 
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            await self.redis.ping()
            self.memory_bank_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Memory Bank MCP initialized. Storage: {self.memory_bank_path}")
            return True
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            self.redis = None
            # Ensure path exists even if Redis fails (fallback mode)
            self.memory_bank_path.mkdir(parents=True, exist_ok=True)
            return False

    async def _ensure_redis(self) -> bool:
        if self.redis:
            try:
                await self.redis.ping()
                return True
            except:
                self.redis = None
        return await self.initialize()

    async def register_agent(self, agent_id: str, capabilities: list, memory_limit_gb: float) -> dict:
        now = datetime.now(timezone.utc)
        capability = AgentCapability(agent_id=agent_id, capabilities=capabilities, memory_limit_gb=memory_limit_gb, last_seen=now)
        self.agents[agent_id] = capability
        if await self._ensure_redis():
            try:
                agent_data = asdict(capability)
                agent_data["last_seen"] = now.isoformat()
                await self.redis.hset("xnai:agents", agent_id, json.dumps(agent_data))
            except Exception as e:
                logger.warning(f"Failed to persist agent in Redis: {e}")
        return {"status": "success", "agent_id": agent_id}

    async def get_context(self, agent_id: str, context_type: str, tier: str = "hot", keys: list = None) -> dict:
        context_id = f"{agent_id}:{context_type}:{tier}"
        redis_key = f"xnai:ctx:{context_id}"
        if context_id in self.context_cache:
            self.performance_metrics["hits"] += 1
            self.context_cache.move_to_end(context_id)
            data = self.context_cache[context_id]
            return {k: data.get(k) for k in keys if k in data} if keys else data
        self.performance_metrics["misses"] += 1
        data = None
        if await self._ensure_redis():
            try:
                data_str = await self.redis.get(redis_key)
                if data_str: data = json.loads(data_str)
            except Exception as e:
                logger.warning(f"Redis get_context failed: {e}")
        if not data:
            context_file = self.memory_bank_path / f"{agent_id}_{context_type}_{tier}.json"
            if context_file.exists():
                try:
                    with open(context_file, 'r') as f:
                        data = json.load(f)
                        if self.redis: await self.redis.set(redis_key, json.dumps(data))
                except Exception as e:
                    logger.error(f"Filesystem read failed: {e}")
        if data:
            self.context_cache[context_id] = data
            if len(self.context_cache) > self.cache_limit: self.context_cache.popitem(last=False)
            return {k: data.get(k) for k in keys if k in data} if keys else data
        return {"status": "success", "content": {}, "source": "empty"}

    async def update_context(self, agent_id: str, context_type: str, context_data: dict, tier: str = "hot") -> dict:
        context_id = f"{agent_id}:{context_type}:{tier}"
        redis_key = f"xnai:ctx:{context_id}"
        context_file = self.memory_bank_path / f"{agent_id}_{context_type}_{tier}.json"
        existing_data = await self.get_context(agent_id, context_type, tier)
        if isinstance(existing_data, dict) and existing_data.get("status") == "success" and "content" in existing_data:
            existing_data = {}
        existing_data.update(context_data)
        data_json = json.dumps(existing_data)
        self.context_cache[context_id] = existing_data
        self.context_cache.move_to_end(context_id)
        if len(self.context_cache) > self.cache_limit: self.context_cache.popitem(last=False)
        if await self._ensure_redis():
            try: await self.redis.set(redis_key, data_json)
            except Exception as e: logger.error(f"Redis update failed: {e}")
        try:
            with open(context_file, 'w') as f: f.write(data_json)
        except Exception as e: logger.error(f"Filesystem write failed: {e}")
        return {"status": "success", "context_id": context_id}

    async def get_capabilities(self) -> List[Tool]:
        return [
            Tool(name="register_agent", description="Register a new agent", inputSchema={"type": "object", "properties": {"agent_id": {"type": "string"}, "capabilities": {"type": "array", "items": {"type": "string"}}, "memory_limit_gb": {"type": "number"}}, "required": ["agent_id", "capabilities", "memory_limit_gb"]}),
            Tool(name="get_context", description="Retrieve context", inputSchema={"type": "object", "properties": {"agent_id": {"type": "string"}, "context_type": {"type": "string"}, "tier": {"type": "string", "enum": ["hot", "warm", "cold"]}, "keys": {"type": "array", "items": {"type": "string"}}}, "required": ["agent_id", "context_type"]}),
            Tool(name="update_context", description="Update context", inputSchema={"type": "object", "properties": {"agent_id": {"type": "string"}, "context_type": {"type": "string"}, "context_data": {"type": "object"}, "tier": {"type": "string", "enum": ["hot", "warm", "cold"]}}, "required": ["agent_id", "context_type", "context_data"]})
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
            await memory_bank_mcp.initialize()
            _initialized = True
    @server.list_tools()
    async def list_tools(): return await mcp_instance.get_capabilities()
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]):
        await _ensure_initialized()
        return await memory_bank_mcp.handle_tool_call(name, arguments)
    return server

# FastAPI App for SSE
if HAS_FASTAPI:
    app = FastAPI(title="Memory Bank MCP Server (SSE)")
    sse = SseServerTransport("/messages/")
    @app.get("/sse")
    async def handle_sse(request: Request):
        server = await create_mcp_server()
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(streams[0], streams[1], server.create_initialization_options())
    @app.post("/messages/")
    async def handle_messages(request: Request):
        await sse.handle_post_message(request.scope, request.receive, request._send)
        return Response(status_code=204)
    @app.get("/health")
    async def health(): return {"status": "ok"}

async def run_stdio():
    """Run the server in stdio mode."""
    server = await create_mcp_server()
    async with stdio_server() as (read_stream, write_streams):
        await server.run(read_stream, write_streams, server.create_initialization_options())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Memory Bank MCP Server")
    parser.add_argument("--stdio", action="store_true", help="Run in stdio mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for SSE mode")
    args = parser.parse_args()

    if args.stdio:
        asyncio.run(run_stdio())
    elif HAS_FASTAPI:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=args.port, timeout_keep_alive=65)
    else:
        logger.error("FastAPI not installed. Use --stdio mode or install fastapi.")
        sys.exit(1)

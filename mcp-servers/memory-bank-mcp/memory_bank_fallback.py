#!/usr/bin/env python3
"""
Memory Bank MCP Fallback Wrapper
=================================
Wraps the MemoryBankMCP server and provides automatic fallback to SQLite when
the primary Redis backend becomes unavailable.

Implements circuit breaker pattern with graceful degradation.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta

from memory_bank_store import MemoryBankStore, ContextTier, ContextType

logger = logging.getLogger(__name__)

class FallbackCircuitBreaker:
    """Circuit breaker for MCP server health."""
    
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half_open
        self.half_open_calls = 0

    def record_success(self) -> None:
        """Record a successful call."""
        self.failure_count = 0
        self.state = "closed"
        self.half_open_calls = 0

    def record_failure(self) -> None:
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

    def check_can_attempt(self) -> bool:
        """Check if we can attempt a call."""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            # Check if recovery timeout has elapsed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed > self.recovery_timeout:
                    self.state = "half_open"
                    self.half_open_calls = 0
                    logger.info("Circuit breaker entering half-open state")
                    return True
            return False
        
        if self.state == "half_open":
            # Allow limited calls to test recovery
            if self.half_open_calls < self.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False
        
        return False

class MemoryBankFallbackWrapper:
    """
    Wraps MCP server and provides SQLite fallback.
    
    Architecture:
    1. Try primary MCP server
    2. On failure, open circuit and switch to SQLite fallback
    3. Periodically attempt to reconnect to primary
    4. Return to primary when healthy
    """

    def __init__(
        self,
        mcp_server: Any = None,
        fallback_store: Optional[MemoryBankStore] = None
    ):
        """
        Initialize the fallback wrapper.
        
        Args:
            mcp_server: The MCP server instance (optional for primary operations)
            fallback_store: Pre-initialized MemoryBankStore instance
        """
        self.mcp_server = mcp_server
        self.fallback_store = fallback_store or MemoryBankStore()
        self.circuit_breaker = FallbackCircuitBreaker()
        self._fallback_mode = False

    def __getattr__(self, name):
        """Proxy missing methods to the primary MCP server."""
        if self.mcp_server and hasattr(self.mcp_server, name):
            return getattr(self.mcp_server, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    async def initialize(self) -> bool:
        """Initialize both MCP server and fallback store."""
        try:
            # Initialize fallback store (always)
            store_ok = await self.fallback_store.initialize()
            logger.info(f"Fallback store initialized: {store_ok}")

            # Try to initialize MCP server if provided
            if self.mcp_server and hasattr(self.mcp_server, 'initialize'):
                try:
                    # Don't use wait_for here as MemoryBankMCP.initialize handles its own timeouts/errors
                    await self.mcp_server.initialize()
                    self._fallback_mode = False
                    logger.info("MCP server primary backend initialized")
                except Exception as e:
                    logger.warning(f"MCP server initialization failed: {e}")
                    self._fallback_mode = True

            return store_ok

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False

    async def register_agent(
        self,
        agent_id: str,
        capabilities: list,
        memory_limit_gb: float
    ) -> Dict[str, Any]:
        """
        Register agent with automatic fallback.
        """
        if not self.circuit_breaker.check_can_attempt() or self._fallback_mode:
            return await self.fallback_store.register_agent(
                agent_id, capabilities, memory_limit_gb
            )

        try:
            if self.mcp_server:
                result = await self.mcp_server.register_agent(agent_id, capabilities, memory_limit_gb)
                if result.get("status") == "success":
                    self.circuit_breaker.record_success()
                    return result
        except Exception as e:
            logger.warning(f"MCP server failed, using fallback: {e}")
            self.circuit_breaker.record_failure()

        return await self.fallback_store.register_agent(
            agent_id, capabilities, memory_limit_gb
        )

    async def get_context(
        self,
        agent_id: str,
        context_type: str,
        tier: str = "hot",
        keys: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get context with automatic fallback.
        """
        if not self.circuit_breaker.check_can_attempt() or self._fallback_mode:
            return await self.fallback_store.get_context(agent_id, context_type, tier)

        try:
            if self.mcp_server:
                result = await self.mcp_server.get_context(agent_id, context_type, tier, keys)
                if result.get("status") == "success":
                    self.circuit_breaker.record_success()
                    # Optional: Sync to fallback store
                    return result
        except Exception as e:
            logger.warning(f"MCP server failed, using fallback: {e}")
            self.circuit_breaker.record_failure()

        return await self.fallback_store.get_context(agent_id, context_type, tier)

    async def update_context(
        self,
        agent_id: str,
        context_type: str,
        context_data: Dict[str, Any],
        tier: str = "hot"
    ) -> Dict[str, Any]:
        """
        Update context with automatic fallback.
        """
        # Always store in fallback first for durability
        fallback_result = await self.fallback_store.set_context(
            agent_id, context_type, tier, context_data, 1
        )

        if not self.circuit_breaker.check_can_attempt() or self._fallback_mode:
            return fallback_result

        try:
            if self.mcp_server:
                result = await self.mcp_server.update_context(agent_id, context_type, context_data, tier)
                if result.get("status") == "success":
                    self.circuit_breaker.record_success()
                    return result
        except Exception as e:
            logger.warning(f"MCP update failed: {e}")
            self.circuit_breaker.record_failure()

        return fallback_result

    async def sync_context(self, source_agent: str, target_agent: str, context_id: str, sync_type: str = "full") -> Dict[str, Any]:
        """Sync context (Proxy to MCP server, fallback is no-op or local log)."""
        if not self.circuit_breaker.check_can_attempt() or self._fallback_mode:
            return {"status": "error", "message": "Sync unavailable in fallback mode"}
        
        try:
            return await self.mcp_server.sync_context(source_agent, target_agent, context_id, sync_type)
        except Exception as e:
            self.circuit_breaker.record_failure()
            return {"status": "error", "message": str(e)}

    async def query_agent_memory(self, target_agent_id: str, query: str, requesting_agent_id: str) -> Dict[str, Any]:
        """A2A Memory Query with fallback to local search."""
        if not self.circuit_breaker.check_can_attempt() or self._fallback_mode:
            # Fallback to store search
            search_results = await self.fallback_store.search_context(query, target_agent_id)
            return {
                "status": "success",
                "source": "fallback_store",
                "matches": search_results.get("results", [])
            }

        try:
            return await self.mcp_server.query_agent_memory(target_agent_id, query, requesting_agent_id)
        except Exception as e:
            self.circuit_breaker.record_failure()
            return {"status": "error", "message": str(e)}

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Handle MCP tool calls by routing through fallback logic with S2 support."""
        if name == "register_agent":
            result = await self.register_agent(
                arguments["agent_id"],
                arguments["capabilities"],
                arguments["memory_limit_gb"]
            )
        elif name == "get_context":
            result = await self.get_context(
                arguments["agent_id"],
                arguments["context_type"],
                arguments.get("tier", "hot"),
                arguments.get("keys")
            )
        elif name == "update_context":
            result = await self.update_context(
                arguments["agent_id"],
                arguments["context_type"],
                arguments["context_data"],
                arguments.get("tier", "hot")
            )
        elif name == "sync_context":
            result = await self.sync_context(
                arguments["source_agent"],
                arguments["target_agent"],
                arguments["context_id"],
                arguments.get("sync_type", "full")
            )
        elif name == "query_agent_memory":
            result = await self.query_agent_memory(
                arguments["target_agent_id"],
                arguments["query"],
                arguments["requesting_agent_id"]
            )
        elif name == "checkpoint_session":
            result = await self.mcp_server.checkpoint_session(
                arguments["session_id"],
                arguments["agent_id"]
            )
        elif name == "rehydrate_session":
            result = await self.mcp_server.rehydrate_session(
                arguments["session_id"],
                arguments["agent_id"]
            )
        elif name == "get_performance_metrics":
            if self._fallback_mode:
                result = await self.fallback_store.get_metrics()
            else:
                result = await self.mcp_server.get_performance_metrics()
        elif name == "get_fallback_status":
            result = await self.get_fallback_status()
        else:
            # Fallback for any other tools that might be added to MemoryBankMCP
            if hasattr(self.mcp_server, "handle_tool_call"):
                return await self.mcp_server.handle_tool_call(name, arguments)
            return {"status": "error", "message": f"Unknown tool: {name}"}

        # Format result for MCP (same as server.py)
        from mcp.types import TextContent
        import json
        return [TextContent(type="text", text=json.dumps(result))]

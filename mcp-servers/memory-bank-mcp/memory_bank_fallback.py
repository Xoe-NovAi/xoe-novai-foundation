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
from typing import Dict, Any, Optional, Callable
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

    async def initialize(self) -> bool:
        """Initialize both MCP server and fallback store."""
        try:
            # Initialize fallback store (always)
            store_ok = await self.fallback_store.initialize()
            logger.info(f"Fallback store initialized: {store_ok}")

            # Try to initialize MCP server if provided
            if self.mcp_server and hasattr(self.mcp_server, 'initialize'):
                try:
                    mcp_ok = await asyncio.wait_for(
                        self.mcp_server.initialize(),
                        timeout=5.0
                    )
                    if mcp_ok:
                        self._fallback_mode = False
                        logger.info("MCP server primary backend available")
                        return store_ok  # Both OK
                except asyncio.TimeoutError:
                    logger.warning("MCP server initialization timeout - using fallback")
                    self._fallback_mode = True
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
        
        Tries MCP server first, falls back to SQLite if unavailable.
        """
        if not self.circuit_breaker.check_can_attempt() or self._fallback_mode:
            logger.info(f"Using fallback store for agent registration: {agent_id}")
            return await self.fallback_store.register_agent(
                agent_id, capabilities, memory_limit_gb
            )

        try:
            # Try MCP server
            if self.mcp_server:
                result = await asyncio.wait_for(
                    self.mcp_server.register_agent(agent_id, capabilities, memory_limit_gb),
                    timeout=5.0
                )
                self.circuit_breaker.record_success()
                logger.info(f"Agent registered via MCP: {agent_id}")
                return result
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning(f"MCP server failed, using fallback: {e}")
            self.circuit_breaker.record_failure()
            self._fallback_mode = True

        # Fallback to SQLite
        return await self.fallback_store.register_agent(
            agent_id, capabilities, memory_limit_gb
        )

    async def get_context(
        self,
        agent_id: str,
        context_type: str,
        tier: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get context with automatic fallback.
        
        Priority: Cache → Primary Server → Fallback Store
        """
        if not self.circuit_breaker.check_can_attempt() or self._fallback_mode:
            logger.info(f"Using fallback store for context: {agent_id}:{context_type}")
            return await self.fallback_store.get_context(agent_id, context_type, tier)

        try:
            # Try MCP server
            if self.mcp_server:
                result = await asyncio.wait_for(
                    self.mcp_server.get_context(agent_id, context_type, tier),
                    timeout=5.0
                )
                
                if result.get("status") == "success":
                    self.circuit_breaker.record_success()
                    # Also cache in fallback store for quick recovery
                    if tier is None:
                        tier = "hot"
                    await self.fallback_store.set_context(
                        agent_id, context_type, tier,
                        result.get("context", {}),
                        result.get("version", 1)
                    )
                    return result

        except asyncio.TimeoutError:
            logger.warning("MCP server timeout retrieving context")
            self.circuit_breaker.record_failure()
            self._fallback_mode = True
        except Exception as e:
            logger.warning(f"MCP server failed, using fallback: {e}")
            self.circuit_breaker.record_failure()
            self._fallback_mode = True

        # Fallback to SQLite
        return await self.fallback_store.get_context(agent_id, context_type, tier)

    async def set_context(
        self,
        agent_id: str,
        context_type: str,
        tier: str,
        content: Dict[str, Any],
        version: int = 1
    ) -> Dict[str, Any]:
        """
        Set context with automatic fallback.
        
        Always stores in fallback store to ensure persistence.
        Also tries to sync with MCP server if available.
        """
        # Always store in fallback first (ensures durability)
        fallback_result = await self.fallback_store.set_context(
            agent_id, context_type, tier, content, version
        )

        # Try to sync with MCP server if available
        if not self._fallback_mode and self.mcp_server:
            try:
                await asyncio.wait_for(
                    self.mcp_server.update_context(agent_id, context_type, content),
                    timeout=5.0
                )
                self.circuit_breaker.record_success()
                logger.info(f"Context synced to MCP: {agent_id}:{context_type}")
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"MCP sync failed: {e} - content preserved in fallback")
                self.circuit_breaker.record_failure()

        return fallback_result

    async def search_context(
        self,
        query: str,
        agent_id: Optional[str] = None,
        context_type: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search across contexts using local full-text search.
        
        Note: Uses fallback store FTS, as MCP server may not support search.
        """
        return await self.fallback_store.search_context(
            query, agent_id, context_type, limit
        )

    async def get_fallback_status(self) -> Dict[str, Any]:
        """Get status of fallback system."""
        store_metrics = await self.fallback_store.get_metrics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "fallback_mode_active": self._fallback_mode,
            "circuit_breaker_state": self.circuit_breaker.state,
            "circuit_breaker_failures": self.circuit_breaker.failure_count,
            "fallback_store": store_metrics,
            "mcp_server_available": self.mcp_server is not None
        }

    async def close(self) -> None:
        """Close connections."""
        await self.fallback_store.close()

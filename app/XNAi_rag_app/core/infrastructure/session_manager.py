"""
Unified Session Manager for XNAi Foundation
===========================================

Provides session management with Redis persistence and in-memory fallback.
Designed for use by Chainlit UI, voice interface, and MC agent interfaces.

CLAUDE STANDARD: Uses AnyIO for structured concurrency.
TORCH-FREE: No PyTorch dependencies.

Features:
- Redis persistence with automatic fallback to in-memory
- Conversation history management with bounded storage
- Session TTL support
- Graceful degradation when Redis unavailable
"""

import anyio
import asyncio
import logging
import os
import json
import uuid
from collections import deque
from datetime import datetime
from typing import Optional, Dict, Any, List, Union

logger = logging.getLogger(__name__)

# Try to import Redis (optional dependency)
try:
    import redis.asyncio as redis
    from redis.asyncio import Redis, ConnectionPool

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    Redis = None
    ConnectionPool = None
    logger.warning(
        "Redis not available - session persistence will use in-memory fallback"
    )


class SessionConfig:
    """Configuration for session management."""

    def __init__(
        self,
        session_ttl: int = 3600,  # 1 hour
        max_conversation_turns: int = 100,
        redis_url: Optional[str] = None,
        redis_host: str = "redis",
        redis_port: int = 6379,
        redis_password: Optional[str] = None,
        redis_db: int = 0,
        connection_timeout: int = 5,
        socket_timeout: int = 10,
    ):
        self.session_ttl = session_ttl
        self.max_conversation_turns = max_conversation_turns
        self.redis_url = redis_url
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.redis_db = redis_db
        self.connection_timeout = connection_timeout
        self.socket_timeout = socket_timeout


class SessionManager:
    """
    Unified session management with Redis persistence and in-memory fallback.

    Priority: Redis (persistent) → In-memory (transient)

    Usage:
        config = SessionConfig(redis_url="redis://localhost:6379")
        manager = SessionManager(config)
        await manager.initialize()

        # Store data
        await manager.set("user_id", "12345")

        # Get conversation context
        context = await manager.get_conversation_context(max_turns=5)

        # Add interaction
        await manager.add_interaction("user", "Hello!")
        await manager.add_interaction("assistant", "Hi there!")

    Redis Key Patterns:
        - xnai:session:{session_id}:data - Full session data
        - xnai:session:{session_id}:conversation - Conversation history
    """

    KEY_PREFIX = "xnai:session"

    def __init__(
        self,
        config: Optional[SessionConfig] = None,
        session_id: Optional[str] = None,
    ):
        self.config = config or SessionConfig()
        self.session_id = session_id or self._generate_session_id()

        # Redis connection
        self._redis_client: Optional[Redis] = None
        self._connection_pool: Optional[ConnectionPool] = None
        self._use_redis = False

        # In-memory fallback storage
        self._memory_store: Dict[str, Any] = {}
        self._conversation_history: deque = deque(
            maxlen=self.config.max_conversation_turns
        )
        self._initialized = False

        # Session metadata
        self._session_data: Dict[str, Any] = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "metadata": {},
            "metrics": {
                "total_interactions": 0,
                "total_user_messages": 0,
                "total_assistant_messages": 0,
            },
        }

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return str(uuid.uuid4())[:8]

    async def initialize(self) -> bool:
        """
        Initialize session manager with Redis connection.

        Returns:
            True if initialized successfully (Redis or fallback)
        """
        if self._initialized:
            return True

        # Check if Redis is enabled via feature flag
        redis_enabled = os.getenv("FEATURE_REDIS_SESSIONS", "true").lower() == "true"

        if not redis_enabled or not REDIS_AVAILABLE:
            logger.info(
                "Redis sessions disabled or unavailable - using in-memory fallback"
            )
            self._initialized = True
            return True

        # Try to connect to Redis
        try:
            if self.config.redis_url:
                self._connection_pool = ConnectionPool.from_url(
                    self.config.redis_url,
                    max_connections=20,
                    decode_responses=True,
                )
            else:
                self._connection_pool = ConnectionPool(
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                    password=self.config.redis_password,
                    db=self.config.redis_db,
                    max_connections=20,
                    decode_responses=True,
                )

            self._redis_client = Redis(connection_pool=self._connection_pool)

            # Test connection with timeout
            async with anyio.move_on_after(self.config.connection_timeout):
                await self._redis_client.ping()
                self._use_redis = True
                logger.info(
                    f"Session manager connected to Redis: {self.config.redis_host}:{self.config.redis_port}"
                )

        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory fallback: {e}")
            self._use_redis = False
            self._redis_client = None
            self._connection_pool = None

        self._initialized = True
        return True

    async def close(self) -> None:
        """Close Redis connection if open."""
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None

        if self._connection_pool:
            await self._connection_pool.disconnect()
            self._connection_pool = None

        self._use_redis = False
        self._initialized = False
        logger.info("Session manager closed")

    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._use_redis and self._redis_client is not None

    @property
    def is_initialized(self) -> bool:
        """Check if session manager is initialized."""
        return self._initialized

    def _get_redis_key(self, key_type: str = "data") -> str:
        """Generate Redis key with namespace."""
        return f"{self.KEY_PREFIX}:{self.session_id}:{key_type}"

    # ========================================================================
    # Core Session Operations
    # ========================================================================

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from session storage.

        Args:
            key: The key to retrieve

        Returns:
            The stored value or None if not found
        """
        if self._use_redis:
            try:
                redis_key = self._get_redis_key("data")
                data = await self._redis_client.hget(redis_key, key)
                if data:
                    return json.loads(data)
                return None
            except Exception as e:
                logger.error(f"Redis get failed: {e}")
                # Fall through to memory fallback

        return self._memory_store.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store a value in session storage.

        Args:
            key: The key to store
            value: The value to store
            ttl: Optional TTL in seconds

        Returns:
            True if stored successfully
        """
        success = False

        if self._use_redis:
            try:
                redis_key = self._get_redis_key("data")
                serialized = json.dumps(value, default=str)
                await self._redis_client.hset(redis_key, key, serialized)

                # Set TTL on the hash
                effective_ttl = ttl or self.config.session_ttl
                await self._redis_client.expire(redis_key, effective_ttl)
                success = True
            except Exception as e:
                logger.error(f"Redis set failed: {e}")

        # Always store in memory as backup
        self._memory_store[key] = value

        return success or True  # Always succeed with memory fallback

    async def delete(self, key: str) -> bool:
        """Delete a value from session storage."""
        if self._use_redis:
            try:
                redis_key = self._get_redis_key("data")
                await self._redis_client.hdel(redis_key, key)
            except Exception as e:
                logger.error(f"Redis delete failed: {e}")

        if key in self._memory_store:
            del self._memory_store[key]

        return True

    # ========================================================================
    # Conversation Management
    # ========================================================================

    async def add_interaction(
        self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a conversation turn to history.

        Args:
            role: "user" or "assistant"
            content: The message content
            metadata: Optional metadata (e.g., tokens, model)

        Returns:
            True if added successfully
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "metadata": metadata or {},
        }

        # Add to in-memory history
        self._conversation_history.append(interaction)

        # Update metrics
        self._session_data["metrics"]["total_interactions"] += 1
        if role == "user":
            self._session_data["metrics"]["total_user_messages"] += 1
        elif role == "assistant":
            self._session_data["metrics"]["total_assistant_messages"] += 1

        # Update last activity
        self._session_data["last_activity"] = datetime.now().isoformat()

        # Persist to Redis
        if self._use_redis:
            try:
                conv_key = self._get_redis_key("conversation")
                await self._redis_client.rpush(
                    conv_key, json.dumps(interaction, default=str)
                )
                await self._redis_client.expire(conv_key, self.config.session_ttl)

                # Also save session data
                data_key = self._get_redis_key("data")
                await self._redis_client.hset(
                    data_key,
                    "session_data",
                    json.dumps(self._session_data, default=str),
                )
                await self._redis_client.expire(data_key, self.config.session_ttl)
            except Exception as e:
                logger.error(f"Failed to persist interaction to Redis: {e}")

        return True

    async def get_conversation_context(
        self, max_turns: int = 10, include_metadata: bool = False
    ) -> str:
        """
        Get conversation history formatted for LLM context.

        Args:
            max_turns: Maximum number of turns to include
            include_metadata: Whether to include metadata in output

        Returns:
            Formatted conversation history string
        """
        # Try to load from Redis first
        if self._use_redis:
            try:
                conv_key = self._get_redis_key("conversation")
                interactions = await self._redis_client.lrange(conv_key, -max_turns, -1)

                if interactions:
                    context_parts = []
                    for interaction_json in interactions:
                        interaction = json.loads(interaction_json)
                        role = interaction.get("role", "unknown")
                        content = interaction.get("content", "")

                        if include_metadata and interaction.get("metadata"):
                            context_parts.append(
                                f"{role}: {content} {interaction['metadata']}"
                            )
                        else:
                            context_parts.append(f"{role}: {content}")

                    return "\n".join(context_parts)
            except Exception as e:
                logger.error(f"Failed to load conversation from Redis: {e}")

        # Fall back to in-memory history
        history = list(self._conversation_history)
        recent = history[-max_turns:] if len(history) > max_turns else history

        context_parts = []
        for turn in recent:
            role = turn.get("role", "unknown")
            content = turn.get("content", "")

            if include_metadata and turn.get("metadata"):
                context_parts.append(f"{role}: {content} {turn['metadata']}")
            else:
                context_parts.append(f"{role}: {content}")

        return "\n".join(context_parts)

    async def get_conversation_history(
        self, max_turns: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history as list of interactions.

        Args:
            max_turns: Maximum number of turns to return (None = all)

        Returns:
            List of interaction dictionaries
        """
        # Try to load from Redis first
        if self._use_redis:
            try:
                conv_key = self._get_redis_key("conversation")

                if max_turns:
                    interactions = await self._redis_client.lrange(
                        conv_key, -max_turns, -1
                    )
                else:
                    interactions = await self._redis_client.lrange(conv_key, 0, -1)

                if interactions:
                    return [json.loads(i) for i in interactions]
            except Exception as e:
                logger.error(f"Failed to load conversation history from Redis: {e}")

        # Fall back to in-memory history
        history = list(self._conversation_history)
        if max_turns:
            return history[-max_turns:]
        return history

    async def clear_conversation(self) -> bool:
        """Clear conversation history."""
        self._conversation_history.clear()

        if self._use_redis:
            try:
                conv_key = self._get_redis_key("conversation")
                await self._redis_client.delete(conv_key)
            except Exception as e:
                logger.error(f"Failed to clear conversation in Redis: {e}")

        return True

    # ========================================================================
    # Session Lifecycle
    # ========================================================================

    async def clear_session(self) -> bool:
        """Clear all session data."""
        self._memory_store.clear()
        self._conversation_history.clear()
        self._session_data = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "metadata": {},
            "metrics": {
                "total_interactions": 0,
                "total_user_messages": 0,
                "total_assistant_messages": 0,
            },
        }

        if self._use_redis:
            try:
                # Delete all keys for this session
                pattern = self._get_redis_key("*")
                keys = []
                async for key in self._redis_client.scan_iter(match=pattern):
                    keys.append(key)

                if keys:
                    await self._redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Failed to clear session in Redis: {e}")

        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        return {
            "session_id": self.session_id,
            "connected": self.is_connected,
            "initialized": self._initialized,
            "created_at": self._session_data.get("created_at"),
            "last_activity": self._session_data.get("last_activity"),
            "total_interactions": self._session_data["metrics"]["total_interactions"],
            "total_user_messages": self._session_data["metrics"]["total_user_messages"],
            "total_assistant_messages": self._session_data["metrics"][
                "total_assistant_messages"
            ],
            "conversation_turns": len(self._conversation_history),
            "memory_store_keys": len(self._memory_store),
        }

    async def extend_ttl(self, ttl: Optional[int] = None) -> bool:
        """Extend the TTL for the session."""
        effective_ttl = ttl or self.config.session_ttl

        if self._use_redis:
            try:
                data_key = self._get_redis_key("data")
                conv_key = self._get_redis_key("conversation")

                await self._redis_client.expire(data_key, effective_ttl)
                await self._redis_client.expire(conv_key, effective_ttl)
                return True
            except Exception as e:
                logger.error(f"Failed to extend TTL: {e}")
                return False

        return True  # In-memory has no TTL


# ============================================================================
# Factory Functions
# ============================================================================


async def create_session_manager(
    session_id: Optional[str] = None, redis_url: Optional[str] = None, **kwargs
) -> SessionManager:
    """
    Create and initialize a session manager.

    Args:
        session_id: Optional session ID (auto-generated if not provided)
        redis_url: Optional Redis URL
        **kwargs: Additional configuration options

    Returns:
        Initialized SessionManager instance
    """
    config = SessionConfig(redis_url=redis_url, **kwargs)
    manager = SessionManager(config=config, session_id=session_id)
    await manager.initialize()
    return manager


# ============================================================================
# Chainlit Integration Helper
# ============================================================================


def get_chainlit_session_key(session_id: str) -> str:
    """Generate a key for storing session manager in Chainlit user_session."""
    return f"xnai_session_manager:{session_id}"

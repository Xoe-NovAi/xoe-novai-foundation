#!/usr/bin/env python3
# ============================================================================
# Xoe-NovAi Phase 4.2.4 - Transaction Logging Service
# ============================================================================
# Purpose: Persistent audit trail for all RAG and LLM operations via Redis Streams
# Features:
#   - Redis Streams integration (xadd) for high-performance logging
#   - Structured JSON payloads for audit analysis
#   - Integration with degradation tiers (logs active tier)
#   - Asynchronous logging to prevent blocking the query path
# ============================================================================

import json
import logging
import time
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import redis

from .tier_config import tier_config_factory

logger = logging.getLogger(__name__)

class TransactionLogger:
    """
    Sovereign Transaction Logging Service.
    Records every interaction to a Redis Stream for auditing and recovery.
    """
    
    STREAM_NAME = "xnai_audit_trail"
    MAX_STREAM_LEN = 10000  # Cap stream size to prevent OOM
    
    def __init__(
        self, 
        redis_host: str = "redis", 
        redis_port: int = 6379, 
        redis_password: Optional[str] = None
    ):
        self._redis_config = {
            "host": redis_host,
            "port": redis_port,
            "password": redis_password,
        }
        self._redis_client: Optional[redis.Redis] = None
        self._connect()

    def _connect(self):
        """Connect to Redis for streaming logs."""
        try:
            self._redis_client = redis.Redis(
                **self._redis_config,
                decode_responses=True,
                socket_timeout=2,
                socket_connect_timeout=2
            )
            self._redis_client.ping()
            logger.info(f"TransactionLogger connected to Redis at {self._redis_config['host']}")
        except Exception as e:
            logger.warning(f"TransactionLogger failed to connect to Redis: {e}")
            self._redis_client = None

    async def log_transaction(
        self,
        transaction_type: str,
        query: str,
        response: str,
        sources: List[str],
        metrics: Dict[str, Any],
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Asynchronously log a transaction to the Redis Stream.
        """
        if not self._redis_client:
            # Try to reconnect if client is missing
            await asyncio.to_thread(self._connect)
            if not self._redis_client:
                logger.error("Skipping transaction log: Redis unavailable")
                return

        try:
            current_tier = tier_config_factory.get_current_tier()
            
            payload = {
                "timestamp": datetime.now().isoformat(),
                "type": transaction_type,
                "session_id": session_id or "anonymous",
                "tier": current_tier,
                "query": query,
                "response_preview": response[:200] + "..." if len(response) > 200 else response,
                "sources": json.dumps(sources),
                "metrics": json.dumps(metrics),
                "metadata": json.dumps(metadata or {})
            }
            
            # Use XADD to append to the stream
            # approx=True allows Redis to prune exactly when it's efficient
            await asyncio.to_thread(
                self._redis_client.xadd,
                self.STREAM_NAME,
                payload,
                maxlen=self.MAX_STREAM_LEN,
                approximate=True
            )
            
            logger.debug(f"Logged {transaction_type} transaction to {self.STREAM_NAME}")
            
        except Exception as e:
            logger.error(f"Failed to log transaction: {e}")

# Global instance
transaction_logger = TransactionLogger()

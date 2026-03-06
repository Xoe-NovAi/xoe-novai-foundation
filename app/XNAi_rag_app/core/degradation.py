import os
import logging
import anyio
import time
import psutil
from typing import Dict, Any, Optional
from .dependencies import get_redis_client

logger = logging.getLogger(__name__)

class DegradationTierManager:
    """
    Monitors system resources and manages service degradation tiers.
    
    Tiers:
    1: Normal - Full context, all features enabled.
    2: Constrained - Reduced context window, disabling non-essential features.
    3: Critical - Minimal context, cache-only mode for some services.
    4: Failover - Emergency read-only mode.
    
    CLAUDE STANDARD: Uses AnyIO for structured concurrency.
    """
    
    def __init__(self, redis_client=None):
        self._redis = redis_client
        self.current_tier = 1
        self.stream_name = os.getenv("DEGRADATION_STREAM", "xnai_degradation")
        self.mem_thresholds = {
            2: 85.0,  # Tier 2 at 85% RAM
            3: 92.0,  # Tier 3 at 92% RAM
            4: 97.0   # Tier 4 at 97% RAM
        }
        self._running = False
        self._cancel_scope: Optional[anyio.CancelScope] = None

    @property
    def redis(self):
        """Lazy access to Redis client."""
        if self._redis is None:
            try:
                self._redis = get_redis_client()
            except Exception as e:
                logger.warning(f"Degradation manager could not connect to Redis: {e}")
        return self._redis

    async def start_monitoring(self):
        """Start the background monitoring task.
        
        CLAUDE STANDARD: Uses TaskGroup for structured concurrency.
        """
        if self._running:
            return
        
        self._running = True
        async with anyio.create_task_group() as tg:
            self._cancel_scope = tg.cancel_scope
            tg.start_soon(self._run_monitor)
        logger.info("🚀 Degradation Monitor started")

    async def stop_monitoring(self):
        """Stop the background monitoring task.
        
        CLAUDE STANDARD: Cancel via CancelScope for clean shutdown.
        """
        self._running = False
        if self._cancel_scope:
            self._cancel_scope.cancel()
            self._cancel_scope = None
        logger.info("🛑 Degradation Monitor stopped")

    async def _run_monitor(self):
        """Periodically check resources and broadcast tier changes."""
        while self._running:
            try:
                # 1. Check Memory
                mem = psutil.virtual_memory()
                cpu = psutil.cpu_percent(interval=None)
                
                # 2. Determine Tier
                new_tier = 1
                if mem.percent >= self.mem_thresholds[4]:
                    new_tier = 4
                elif mem.percent >= self.mem_thresholds[3]:
                    new_tier = 3
                elif mem.percent >= self.mem_thresholds[2]:
                    new_tier = 2
                
                # 3. Handle Transition
                if new_tier != self.current_tier:
                    await self._transition_to(new_tier, mem.percent, cpu)
                
                await anyio.sleep(5)  # Poll every 5 seconds
            except anyio.get_cancelled_exc_class():
                break
            except Exception as e:
                logger.error(f"Error in degradation monitor: {e}")
                await anyio.sleep(10)

    async def _transition_to(self, tier: int, mem_p: float, cpu_p: float):
        """Broadcast tier transition."""
        logger.warning(f"⚠️ DEGRADATION TIER CHANGE: {self.current_tier} -> {tier} (RAM: {mem_p}%, CPU: {cpu_p}%)")
        self.current_tier = tier
        
        try:
            if self.redis:
                data = {
                    "tier": str(tier),
                    "memory_percent": str(mem_p),
                    "cpu_percent": str(cpu_p),
                    "timestamp": str(time.time())
                }
                # Use Redis Stream for history + PubSub for real-time
                await self.redis.xadd(self.stream_name, data, maxlen=100)
                await self.redis.publish("xnai_degradation_events", str(tier))
                logger.info(f"✅ Broadcasted tier {tier} to Redis")
        except Exception as e:
            logger.error(f"Failed to broadcast degradation tier: {e}")

# Global manager instance
degradation_manager = DegradationTierManager()

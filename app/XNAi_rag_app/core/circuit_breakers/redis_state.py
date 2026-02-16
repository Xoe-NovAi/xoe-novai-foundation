"""
Redis State Management for Circuit Breakers
Handles Redis connection management and state persistence with fallback patterns.
"""

import asyncio
import logging
import os
from typing import Optional, Dict, Any, Union
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool

from .circuit_breaker import CircuitBreakerError, CircuitBreakerConfig, CircuitStateData

logger = logging.getLogger(__name__)

class RedisConnectionManager:
    """Manages Redis connections with fallback and health checking"""
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        host: str = "redis",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
        max_connections: int = 50,
        health_check_interval: int = 30,
        adaptive_timeout: bool = True,
        connection_timeout: int = 5,
        socket_timeout: int = 10
    ):
        self.redis_url = redis_url
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.max_connections = max_connections
        self.health_check_interval = health_check_interval
        self.adaptive_timeout = adaptive_timeout
        self.connection_timeout = connection_timeout
        self.socket_timeout = socket_timeout
        
        self._redis_client: Optional[Redis] = None
        self._connection_pool: Optional[ConnectionPool] = None
        self._is_connected = False
        self._health_check_task: Optional[asyncio.Task] = None
        self._fallback_mode = False
        
        # Connection retry settings
        self._retry_attempts = 3
        self._retry_delay = 1.0  # seconds
        
        # Performance metrics
        self._connection_latency = []
        self._health_check_latency = []
        self._last_health_check = 0.0
        self._health_check_failures = 0
        
        # Adaptive timeout settings
        self._base_timeout = connection_timeout
        self._max_timeout = 30  # Maximum timeout for adaptive mode
        self._timeout_multiplier = 1.5  # Multiplier for failed connections
        
        logger.info(f"Redis Connection Manager initialized for {host}:{port} with adaptive timeout: {adaptive_timeout}")
    
    async def connect(self) -> bool:
        """Establish Redis connection with retry logic"""
        if self._redis_client and self._is_connected:
            return True
        
        for attempt in range(self._retry_attempts):
            try:
                if self.redis_url:
                    # Use Redis URL
                    self._connection_pool = ConnectionPool.from_url(
                        self.redis_url,
                        max_connections=self.max_connections,
                        decode_responses=False
                    )
                else:
                    # Use individual parameters
                    self._connection_pool = ConnectionPool(
                        host=self.host,
                        port=self.port,
                        password=self.password,
                        db=self.db,
                        max_connections=self.max_connections,
                        decode_responses=False
                    )
                
                self._redis_client = Redis(connection_pool=self._connection_pool)
                
                # Test connection
                await self._redis_client.ping()
                self._is_connected = True
                self._fallback_mode = False
                
                logger.info(f"Redis connection established: {self.host}:{self.port}")
                
                # Start health check task
                if self._health_check_task is None:
                    self._health_check_task = asyncio.create_task(self._health_check_loop())
                
                return True
                
            except Exception as e:
                logger.warning(f"Redis connection attempt {attempt + 1} failed: {e}")
                if attempt < self._retry_attempts - 1:
                    await asyncio.sleep(self._retry_delay * (2 ** attempt))  # Exponential backoff
        
        logger.error("Failed to establish Redis connection after all attempts")
        self._fallback_mode = True
        return False
    
    async def disconnect(self):
        """Close Redis connection"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
        
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None
        
        if self._connection_pool:
            await self._connection_pool.disconnect()
            self._connection_pool = None
        
        self._is_connected = False
        logger.info("Redis connection closed")
    
    async def _health_check_loop(self):
        """Background health check loop"""
        while True:
            try:
                if self._is_connected and self._redis_client:
                    await self._redis_client.ping()
                    if self._fallback_mode:
                        logger.info("Redis connection restored, exiting fallback mode")
                        self._fallback_mode = False
                else:
                    if not self._fallback_mode:
                        logger.warning("Redis connection lost, entering fallback mode")
                        self._fallback_mode = True
            except Exception as e:
                if not self._fallback_mode:
                    logger.warning(f"Redis health check failed: {e}, entering fallback mode")
                    self._fallback_mode = True
            
            await asyncio.sleep(self.health_check_interval)
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._is_connected and not self._fallback_mode
    
    @property
    def fallback_mode(self) -> bool:
        """Check if in fallback mode"""
        return self._fallback_mode
    
    @asynccontextmanager
    async def get_client(self):
        """Get Redis client with connection management"""
        if not self.is_connected:
            await self.connect()
        
        if self._redis_client:
            yield self._redis_client
        else:
            raise CircuitBreakerError("Redis client not available")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get Redis health status"""
        return {
            "connected": self.is_connected,
            "fallback_mode": self.fallback_mode,
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "max_connections": self.max_connections,
            "pool_size": len(self._connection_pool._created_connections) if self._connection_pool else 0
        }

class CircuitBreakerStateManager:
    """Manages circuit breaker state with Redis persistence and fallback"""
    
    def __init__(self, redis_manager: RedisConnectionManager, key_prefix: str = "circuit_breaker:"):
        self.redis_manager = redis_manager
        self.key_prefix = key_prefix
        self._fallback_states: Dict[str, CircuitStateData] = {}
        self._fallback_lock = asyncio.Lock()
    
    async def get_state(self, circuit_name: str) -> Optional[CircuitStateData]:
        """Get circuit state with Redis fallback"""
        try:
            if self.redis_manager.is_connected:
                async with self.redis_manager.get_client() as client:
                    key = f"{self.key_prefix}{circuit_name}"
                    data = await client.get(key)
                    
                    if data:
                        state_dict = self._deserialize_state(data)
                        return CircuitStateData(**state_dict)
            else:
                logger.warning(f"Redis not available, using fallback storage for {circuit_name}")
        except Exception as e:
            logger.error(f"Failed to get state from Redis for {circuit_name}: {e}")
        
        # Fallback to in-memory storage
        async with self._fallback_lock:
            return self._fallback_states.get(circuit_name)
    
    async def set_state(self, circuit_name: str, state_data: CircuitStateData) -> bool:
        """Set circuit state with Redis fallback"""
        success = False
        
        try:
            if self.redis_manager.is_connected:
                async with self.redis_manager.get_client() as client:
                    key = f"{self.key_prefix}{circuit_name}"
                    data = self._serialize_state(state_data)
                    
                    # Use SET with expiration for automatic cleanup
                    await client.setex(key, 3600, data)  # 1 hour expiration
                    success = True
        except Exception as e:
            logger.error(f"Failed to set state in Redis for {circuit_name}: {e}")
        
        # Always update fallback storage
        async with self._fallback_lock:
            self._fallback_states[circuit_name] = state_data
        
        if not success:
            logger.warning(f"State for {circuit_name} stored in fallback only")
        
        return success
    
    async def delete_state(self, circuit_name: str) -> bool:
        """Delete circuit state with Redis fallback"""
        success = False
        
        try:
            if self.redis_manager.is_connected:
                async with self.redis_manager.get_client() as client:
                    key = f"{self.key_prefix}{circuit_name}"
                    await client.delete(key)
                    success = True
        except Exception as e:
            logger.error(f"Failed to delete state from Redis for {circuit_name}: {e}")
        
        # Always update fallback storage
        async with self._fallback_lock:
            if circuit_name in self._fallback_states:
                del self._fallback_states[circuit_name]
        
        return success
    
    def _serialize_state(self, state_data: CircuitStateData) -> bytes:
        """Serialize state data to bytes"""
        import json
        return json.dumps(state_data.__dict__).encode('utf-8')
    
    def _deserialize_state(self, data: bytes) -> Dict[str, Any]:
        """Deserialize state data from bytes"""
        import json
        return json.loads(data.decode('utf-8'))
    
    async def get_all_states(self) -> Dict[str, CircuitStateData]:
        """Get all circuit states"""
        states = {}
        
        try:
            if self.redis_manager.is_connected:
                async with self.redis_manager.get_client() as client:
                    keys = await client.keys(f"{self.key_prefix}*")
                    for key in keys:
                        circuit_name = key.decode('utf-8').replace(self.key_prefix, '')
                        data = await client.get(key)
                        if data:
                            state_dict = self._deserialize_state(data)
                            states[circuit_name] = CircuitStateData(**state_dict)
        except Exception as e:
            logger.error(f"Failed to get all states from Redis: {e}")
        
        # Merge with fallback states
        async with self._fallback_lock:
            for name, state in self._fallback_states.items():
                if name not in states:
                    states[name] = state
        
        return states
    
    async def cleanup_expired_states(self):
        """Clean up expired states from fallback storage"""
        current_time = asyncio.get_event_loop().time()
        async with self._fallback_lock:
            # Remove states older than 1 hour
            expired_keys = [
                name for name, state in self._fallback_states.items()
                if current_time - max(state.last_failure_time, state.last_success_time) > 3600
            ]
            
            for key in expired_keys:
                del self._fallback_states[key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired states from fallback storage")
    
    async def get_fallback_status(self) -> Dict[str, Any]:
        """Get fallback storage status"""
        async with self._fallback_lock:
            return {
                "fallback_states_count": len(self._fallback_states),
                "fallback_states": list(self._fallback_states.keys())
            }

class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers with Redis state"""
    
    def __init__(self, redis_manager: RedisConnectionManager):
        self.redis_manager = redis_manager
        self.state_manager = CircuitBreakerStateManager(redis_manager)
        self.circuit_breakers: Dict[str, Any] = {}  # Will hold CircuitBreaker instances
        self._registry_lock = asyncio.Lock()
    
    async def register_circuit_breaker(
        self,
        name: str,
        config: CircuitBreakerConfig,
        fallback_func: Optional[callable] = None
    ):
        """Register a circuit breaker with Redis state management"""
        from .circuit_breaker import CircuitBreaker, RedisCircuitStateStore
        
        async with self._registry_lock:
            if name in self.circuit_breakers:
                logger.warning(f"Circuit breaker {name} already registered")
                return
            
            # Create state store with our state manager
            state_store = RedisCircuitStateStore(
                redis_client=None,  # Will be set dynamically
                key_prefix=self.state_manager.key_prefix
            )
            
            # Create circuit breaker
            breaker = CircuitBreaker(config, state_store, fallback_func)
            self.circuit_breakers[name] = breaker
            
            logger.info(f"Registered circuit breaker: {name}")
    
    async def get_circuit_breaker(self, name: str):
        """Get registered circuit breaker"""
        return self.circuit_breakers.get(name)
    
    async def call_with_circuit_breaker(self, name: str, func: callable):
        """Call function with circuit breaker protection"""
        breaker = await self.get_circuit_breaker(name)
        if breaker:
            return await breaker.call(func)
        else:
            # No circuit breaker, execute directly
            return await func()
    
    async def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status including Redis health"""
        redis_status = await self.redis_manager.get_health_status()
        fallback_status = await self.state_manager.get_fallback_status()
        
        return {
            "redis_status": redis_status,
            "fallback_status": fallback_status,
            "registered_circuits": list(self.circuit_breakers.keys()),
            "total_circuits": len(self.circuit_breakers)
        }
    
    async def cleanup(self):
        """Clean up registry resources"""
        await self.state_manager.cleanup_expired_states()
        await self.redis_manager.disconnect()

# Factory function for easy setup
async def create_circuit_breaker_registry(
    redis_url: Optional[str] = None,
    host: str = "redis",
    port: int = 6379,
    password: Optional[str] = None,
    db: int = 0
) -> CircuitBreakerRegistry:
    """Create circuit breaker registry with Redis connection"""
    redis_manager = RedisConnectionManager(
        redis_url=redis_url,
        host=host,
        port=port,
        password=password,
        db=db
    )
    
    # Try to connect
    await redis_manager.connect()
    
    registry = CircuitBreakerRegistry(redis_manager)
    return registry
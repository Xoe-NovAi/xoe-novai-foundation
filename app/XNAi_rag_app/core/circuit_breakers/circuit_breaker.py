"""
Circuit Breaker Implementation for Xoe-NovAi Foundation Stack
Redis-backed with graceful degradation patterns and async safety.
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar, Union, Awaitable
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio import Redis

# Import unified exception hierarchy
try:
    from ...api.exceptions import XNAiException
    from ...schemas.errors import ErrorCategory
    UNIFIED_EXCEPTIONS_AVAILABLE = True
except ImportError:
    # Fallback for standalone testing or different path structure
    try:
        from app.XNAi_rag_app.api.exceptions import XNAiException
        from app.XNAi_rag_app.schemas.errors import ErrorCategory
        UNIFIED_EXCEPTIONS_AVAILABLE = True
    except ImportError:
        UNIFIED_EXCEPTIONS_AVAILABLE = False

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit open, blocking calls
    HALF_OPEN = "half_open"  # Testing if service recovered

if UNIFIED_EXCEPTIONS_AVAILABLE:
    class CircuitBreakerError(XNAiException):
        """Base exception for circuit breaker operations"""
        def __init__(self, message: str, category: Optional[ErrorCategory] = None, **kwargs):
            super().__init__(
                message=message,
                category=category or ErrorCategory.INTERNAL_ERROR,
                **kwargs
            )

    class CircuitOpenError(CircuitBreakerError):
        """Raised when circuit is open and call is blocked"""
        def __init__(self, service_name: str, retry_after: float = 0):
            super().__init__(
                message=f"Circuit breaker open for service: {service_name}",
                category=ErrorCategory.CIRCUIT_OPEN,
                details={"service_name": service_name, "retry_after": retry_after}
            )

    class CircuitTimeoutError(CircuitBreakerError):
        """Raised when circuit breaker operation times out"""
        def __init__(self, message: str):
            super().__init__(
                message=message,
                category=ErrorCategory.TIMEOUT
            )
else:
    class CircuitBreakerError(Exception):
        """Base exception for circuit breaker operations"""
        pass

    class CircuitOpenError(CircuitBreakerError):
        """Raised when circuit is open and call is blocked"""
        pass

    class CircuitTimeoutError(CircuitBreakerError):
        """Raised when circuit breaker operation times out"""
        pass

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    half_open_max_calls: int = 3
    timeout: int = 30  # seconds
    expected_exception: Union[type, tuple] = Exception
    name: str = "default"

@dataclass
class CircuitStateData:
    """Circuit breaker state data"""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0.0
    success_count: int = 0
    last_success_time: float = 0.0
    total_calls: int = 0
    total_failures: int = 0
    total_successes: int = 0

class CircuitStateStore(ABC):
    """Abstract base class for circuit state storage"""
    
    @abstractmethod
    async def get_state(self, circuit_name: str) -> Optional[CircuitStateData]:
        """Get circuit state"""
        pass
    
    @abstractmethod
    async def set_state(self, circuit_name: str, state_data: CircuitStateData) -> bool:
        """Set circuit state"""
        pass
    
    @abstractmethod
    async def delete_state(self, circuit_name: str) -> bool:
        """Delete circuit state"""
        pass

class RedisCircuitStateStore(CircuitStateStore):
    """Redis-based circuit state storage"""
    
    def __init__(self, redis_client: Redis, key_prefix: str = "circuit_breaker:"):
        self.redis_client = redis_client
        self.key_prefix = key_prefix
        self.lock_timeout = 5.0  # seconds
    
    async def get_state(self, circuit_name: str) -> Optional[CircuitStateData]:
        """Get circuit state from Redis"""
        try:
            key = f"{self.key_prefix}{circuit_name}"
            data = await self.redis_client.get(key)
            
            if data:
                state_dict = json.loads(data)
                # Convert state string back to Enum
                if 'state' in state_dict and isinstance(state_dict['state'], str):
                    state_dict['state'] = CircuitState(state_dict['state'])
                return CircuitStateData(**state_dict)
            
            return None
        except Exception as e:
            logger.error(f"Failed to get circuit state {circuit_name}: {e}")
            return None
    
    async def set_state(self, circuit_name: str, state_data: CircuitStateData) -> bool:
        """Set circuit state in Redis"""
        try:
            key = f"{self.key_prefix}{circuit_name}"
            
            # Handle Enum serialization
            state_dict = state_data.__dict__.copy()
            if isinstance(state_dict['state'], CircuitState):
                state_dict['state'] = state_dict['state'].value
                
            data = json.dumps(state_dict)
            
            # Use SET with NX (not exists) and EX (expire) for atomic operation
            result = await self.redis_client.set(
                key, data, ex=int(self.lock_timeout * 2), nx=True
            )
            
            if not result:
                # Key exists, try to update with expiration
                await self.redis_client.setex(key, int(self.lock_timeout * 2), data)
            
            return True
        except Exception as e:
            logger.error(f"Failed to set circuit state {circuit_name}: {e}")
            return False
    
    async def delete_state(self, circuit_name: str) -> bool:
        """Delete circuit state from Redis"""
        try:
            key = f"{self.key_prefix}{circuit_name}"
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete circuit state {circuit_name}: {e}")
            return False

class InMemoryCircuitStateStore(CircuitStateStore):
    """In-memory circuit state storage (fallback)"""
    
    def __init__(self):
        self._states: Dict[str, CircuitStateData] = {}
        self._lock = asyncio.Lock()
    
    async def get_state(self, circuit_name: str) -> Optional[CircuitStateData]:
        """Get circuit state from memory"""
        async with self._lock:
            return self._states.get(circuit_name)
    
    async def set_state(self, circuit_name: str, state_data: CircuitStateData) -> bool:
        """Set circuit state in memory"""
        async with self._lock:
            self._states[circuit_name] = state_data
            return True
    
    async def delete_state(self, circuit_name: str) -> bool:
        """Delete circuit state from memory"""
        async with self._lock:
            if circuit_name in self._states:
                del self._states[circuit_name]
                return True
            return False

class CircuitBreaker:
    """
    Circuit Breaker implementation with Redis-backed state persistence
    and graceful degradation patterns.
    """
    
    def __init__(
        self,
        config: CircuitBreakerConfig,
        state_store: CircuitStateStore,
        fallback_func: Optional[Callable] = None
    ):
        self.config = config
        self.state_store = state_store
        self.fallback_func = fallback_func
        self._lock = asyncio.Lock()
        
        # Metrics
        self._metrics = {
            "calls": 0,
            "failures": 0,
            "successes": 0,
            "blocked": 0,
            "fallbacks": 0
        }
    
    async def _get_or_create_state(self) -> CircuitStateData:
        """Get existing state or create new one"""
        state = await self.state_store.get_state(self.config.name)
        if state is None:
            state = CircuitStateData()
            await self.state_store.set_state(self.config.name, state)
        return state
    
    async def _update_state(self, state: CircuitStateData) -> bool:
        """Update circuit state"""
        return await self.state_store.set_state(self.config.name, state)
    
    def _should_open_circuit(self, state: CircuitStateData) -> bool:
        """Check if circuit should be opened"""
        return state.failure_count >= self.config.failure_threshold
    
    def _should_close_circuit(self, state: CircuitStateData) -> bool:
        """Check if circuit should be closed"""
        return state.success_count >= self.config.half_open_max_calls
    
    async def _transition_state(self, state: CircuitStateData, new_state: CircuitState):
        """Transition circuit to new state with detailed logging and metrics"""
        old_state = state.state
        transition_time = time.time()
        
        logger.info(
            f"Circuit {self.config.name} transitioning from {old_state.value} to {new_state.value}",
            extra={
                "circuit_name": self.config.name,
                "old_state": old_state.value,
                "new_state": new_state.value,
                "failure_count": state.failure_count,
                "total_failures": state.total_failures,
                "total_calls": state.total_calls,
                "transition_time": transition_time,
                "time_since_last_failure": transition_time - state.last_failure_time,
                "time_since_last_success": transition_time - state.last_success_time
            }
        )
        
        state.state = new_state
        if new_state == CircuitState.CLOSED:
            # Reset counters on close
            state.failure_count = 0
            state.success_count = 0
            state.last_failure_time = 0.0
        elif new_state == CircuitState.OPEN:
            # Set failure time to current to respect recovery timeout
            state.last_failure_time = transition_time
        elif new_state == CircuitState.HALF_OPEN:
            # Reset success count for half-open
            state.success_count = 0
        
        # Update transition metrics
        if not hasattr(state, 'transitions'):
            state.transitions = []
        
        state.transitions.append({
            'from_state': old_state.value,
            'to_state': new_state.value,
            'timestamp': transition_time,
            'failure_count': state.failure_count,
            'total_failures': state.total_failures,
            'total_calls': state.total_calls
        })
        
        # Keep only last 10 transitions to prevent memory growth
        if len(state.transitions) > 10:
            state.transitions = state.transitions[-10:]
        
        await self._update_state(state)
    
    async def _execute_with_timeout(self, func: Callable[[], Any]) -> T:
        """Execute function with timeout"""
        try:
            # Check if func is a coroutine function or returns a coroutine
            if asyncio.iscoroutinefunction(func):
                return await asyncio.wait_for(func(), timeout=self.config.timeout)
            
            # Execute and check if result is a coroutine
            result = func()
            if asyncio.iscoroutine(result):
                return await asyncio.wait_for(result, timeout=self.config.timeout)
            
            return result
        except asyncio.TimeoutError:
            raise CircuitTimeoutError(f"Operation timed out after {self.config.timeout}s")
    
    async def call(self, func: Callable[[], Awaitable[T]]) -> T:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Async function to execute
            
        Returns:
            Function result
            
        Raises:
            CircuitOpenError: When circuit is open and no fallback available
            CircuitTimeoutError: When operation times out
            Exception: Original exception from function
        """
        async with self._lock:
            state = await self._get_or_create_state()
            
            # Update metrics
            self._metrics["calls"] += 1
            state.total_calls += 1
            
            # Check circuit state
            current_time = time.time()
            
            if state.state == CircuitState.OPEN:
                # Check if we should try half-open
                if current_time - state.last_failure_time >= self.config.recovery_timeout:
                    await self._transition_state(state, CircuitState.HALF_OPEN)
                    logger.info(f"Circuit {self.config.name} transitioning to HALF_OPEN")
                else:
                    self._metrics["blocked"] += 1
                    state.total_failures += 1
                    
                    if self.fallback_func:
                        self._metrics["fallbacks"] += 1
                        logger.warning(f"Circuit {self.config.name} OPEN, using fallback")
                        return await self.fallback_func()
                    else:
                        retry_after = max(0, self.config.recovery_timeout - (current_time - state.last_failure_time))
                        raise CircuitOpenError(self.config.name, retry_after=retry_after)
            
            elif state.state == CircuitState.HALF_OPEN:
                # Check if we've exceeded max calls in half-open
                if state.success_count >= self.config.half_open_max_calls:
                    await self._transition_state(state, CircuitState.CLOSED)
                    logger.info(f"Circuit {self.config.name} transitioning to CLOSED")
            
            # Execute the function
            try:
                result = await self._execute_with_timeout(func)
                
                # Success path
                if state.state == CircuitState.HALF_OPEN:
                    state.success_count += 1
                    if self._should_close_circuit(state):
                        await self._transition_state(state, CircuitState.CLOSED)
                else:
                    # Reset failure count on success in CLOSED state
                    state.failure_count = 0
                
                state.last_success_time = current_time
                state.total_successes += 1
                self._metrics["successes"] += 1
                
                await self._update_state(state)
                return result
                
            except self.config.expected_exception as e:
                # Failure path
                state.failure_count += 1
                state.last_failure_time = current_time
                state.total_failures += 1
                self._metrics["failures"] += 1
                
                # Check if we should open circuit
                if self._should_open_circuit(state):
                    await self._transition_state(state, CircuitState.OPEN)
                    logger.error(f"Circuit {self.config.name} OPENED due to {state.failure_count} failures")
                
                await self._update_state(state)
                raise e
    
    @asynccontextmanager
    async def context(self):
        """Context manager for circuit breaker"""
        async with self._lock:
            state = await self._get_or_create_state()
            self._metrics["calls"] += 1
            state.total_calls += 1
            
            yield
            
            # Success - reset failure count
            state.failure_count = 0
            state.last_success_time = time.time()
            state.total_successes += 1
            self._metrics["successes"] += 1
            
            await self._update_state(state)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics"""
        return {
            "name": self.config.name,
            "metrics": self._metrics.copy(),
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "half_open_max_calls": self.config.half_open_max_calls,
                "timeout": self.config.timeout
            }
        }
    
    async def reset(self):
        """Reset circuit breaker state"""
        async with self._lock:
            state = CircuitStateData()
            await self.state_store.set_state(self.config.name, state)
            self._metrics = {k: 0 for k in self._metrics}
            logger.info(f"Circuit {self.config.name} reset")
    
    async def force_open(self):
        """Force circuit breaker to open"""
        async with self._lock:
            state = await self._get_or_create_state()
            await self._transition_state(state, CircuitState.OPEN)
            logger.warning(f"Circuit {self.config.name} forced OPEN")
    
    async def force_close(self):
        """Force circuit breaker to close"""
        async with self._lock:
            state = await self._get_or_create_state()
            await self._transition_state(state, CircuitState.CLOSED)
            logger.info(f"Circuit {self.config.name} forced CLOSED")

class GracefulDegradationManager:
    """
    Manager for graceful degradation patterns across multiple services
    """
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.degradation_strategies: Dict[str, Callable] = {}
    
    def register_circuit_breaker(
        self,
        name: str,
        config: CircuitBreakerConfig,
        state_store: CircuitStateStore,
        fallback_func: Optional[Callable] = None
    ):
        """Register a circuit breaker"""
        breaker = CircuitBreaker(config, state_store, fallback_func)
        self.circuit_breakers[name] = breaker
        
        if fallback_func:
            self.degradation_strategies[name] = fallback_func
        
        logger.info(f"Registered circuit breaker: {name}")
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get registered circuit breaker"""
        return self.circuit_breakers.get(name)
    
    async def call_with_degradation(self, service_name: str, func: Callable[[], Awaitable[T]]) -> T:
        """Call function with graceful degradation"""
        breaker = self.circuit_breakers.get(service_name)
        if breaker:
            return await breaker.call(func)
        else:
            # No circuit breaker, execute directly
            return await func()
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all circuit breakers"""
        return {
            name: breaker.get_metrics()
            for name, breaker in self.circuit_breakers.items()
        }
    
    async def reset_all(self):
        """Reset all circuit breakers"""
        for breaker in self.circuit_breakers.values():
            await breaker.reset()
        logger.info("All circuit breakers reset")
    
    async def force_open_all(self):
        """Force all circuit breakers open"""
        for breaker in self.circuit_breakers.values():
            await breaker.force_open()
        logger.warning("All circuit breakers forced OPEN")
    
    async def force_close_all(self):
        """Force all circuit breakers closed"""
        for breaker in self.circuit_breakers.values():
            await breaker.force_close()
        logger.info("All circuit breakers forced CLOSED")

# Factory functions for common patterns
def create_redis_circuit_breaker(
    name: str,
    redis_client: Redis,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    timeout: int = 30,
    fallback_func: Optional[Callable] = None
) -> CircuitBreaker:
    """Create Redis-backed circuit breaker"""
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        timeout=timeout,
        name=name
    )
    
    state_store = RedisCircuitStateStore(redis_client)
    return CircuitBreaker(config, state_store, fallback_func)

def create_inmemory_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    timeout: int = 30,
    fallback_func: Optional[Callable] = None
) -> CircuitBreaker:
    """Create in-memory circuit breaker (fallback)"""
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        timeout=timeout,
        name=name
    )
    
    state_store = InMemoryCircuitStateStore()
    return CircuitBreaker(config, state_store, fallback_func)

# Common fallback functions
async def fallback_return_none():
    """Fallback that returns None"""
    logger.warning("Using fallback: return None")
    return None

async def fallback_return_empty_dict():
    """Fallback that returns empty dict"""
    logger.warning("Using fallback: return empty dict")
    return {}

async def fallback_return_empty_list():
    """Fallback that returns empty list"""
    logger.warning("Using fallback: return empty list")
    return []

async def fallback_raise_service_unavailable():
    """Fallback that raises service unavailable"""
    logger.error("Using fallback: raise Service Unavailable")
    raise CircuitBreakerError("Service temporarily unavailable")
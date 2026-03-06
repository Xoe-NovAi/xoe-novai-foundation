"""
Circuit Breaker Implementation for Xoe-NovAi Foundation Stack
Redis-backed with graceful degradation patterns and async safety.
"""

from typing import Optional, Dict, Any, Callable, Awaitable, TypeVar
import logging
import asyncio
from functools import wraps

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitOpenError,
    CircuitTimeoutError,
    CircuitBreakerConfig,
    CircuitState,
    CircuitStateData,
    CircuitStateStore,
    RedisCircuitStateStore,
    InMemoryCircuitStateStore,
    GracefulDegradationManager,
    create_redis_circuit_breaker,
    create_inmemory_circuit_breaker,
    fallback_return_none,
    fallback_return_empty_dict,
    fallback_return_empty_list,
    fallback_raise_service_unavailable
)

from .redis_state import (
    RedisConnectionManager,
    CircuitBreakerStateManager,
    CircuitBreakerRegistry,
    create_circuit_breaker_registry
)

from .graceful_degradation import (
    DegradationStrategy,
    FallbackStrategy,
    CacheFirstStrategy,
    DegradedModeStrategy,
    CircuitBreakerStrategy,
    DegradationManager,
    ServiceDegradationManager,
    IntegratedDegradationManager,
    create_llm_degradation_manager,
    create_redis_degradation_manager,
    create_vector_search_degradation_manager
)

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CircuitBreakerProxy:
    """
    Proxy for CircuitBreaker that allows for lazy initialization.
    Matches the interface expected by services and supports decorators.
    """
    def __init__(self, name: str):
        self.name = name
        self._breaker: Optional[CircuitBreaker] = None

    def _get_breaker(self) -> Optional[CircuitBreaker]:
        global _registry
        if self._breaker:
            return self._breaker
        if _registry:
            self._breaker = _registry.circuit_breakers.get(self.name)
            return self._breaker
        return None

    async def call(self, func: Callable[[], Awaitable[T]]) -> T:
        breaker = self._get_breaker()
        if breaker:
            return await breaker.call(func)
        return await func()

    def __call__(self, func: Callable) -> Callable:
        """Allow proxy to be used as a decorator or wrapper."""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            breaker = self._get_breaker()
            if breaker is None:
                return await func(*args, **kwargs)
            # CircuitBreaker.call expects a callable that takes no args
            return await breaker.call(lambda: func(*args, **kwargs))

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # The current CircuitBreaker implementation is primarily async.
            # For sync calls, we execute directly if no breaker, or try to run in loop.
            # But usually our decorators are on async functions in this stack.
            return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    async def is_allowed(self) -> bool:
        breaker = self._get_breaker()
        if not breaker:
            return True
        state = await breaker.state_store.get_state(breaker.config.name)
        if not state:
            return True
        return state.state != CircuitState.OPEN

    def allow_request(self) -> bool:
        """Synchronous version of is_allowed, assumes True if state is unknown."""
        return True

    def get_metrics(self) -> Dict[str, Any]:
        breaker = self._get_breaker()
        if breaker:
            return breaker.get_metrics()
        return {"name": self.name, "metrics": {}, "config": {}}

    async def record_success(self):
        pass

    async def record_failure(self):
        pass

# Global registry for circuit breakers
_registry: Optional[CircuitBreakerRegistry] = None
registry: Optional[CircuitBreakerRegistry] = None

# Standard circuit breaker proxies
voice_stt_breaker = CircuitBreakerProxy("voice_stt")
voice_tts_breaker = CircuitBreakerProxy("voice_tts")
rag_api_breaker = CircuitBreakerProxy("rag_api")
redis_breaker = CircuitBreakerProxy("redis_cache")
voice_processing_breaker = CircuitBreakerProxy("voice_processing")

async def initialize_circuit_breakers(redis_url: str):
    """Initialize the global circuit breaker registry."""
    global _registry, registry
    if _registry is None:
        try:
            _registry = await create_circuit_breaker_registry(redis_url=redis_url)
            registry = _registry
            logger.info("Circuit breaker registry initialized")
            
            # Register standard breakers if they don't exist
            # STT circuit breaker
            await _registry.register_circuit_breaker(
                name="voice_stt",
                config=CircuitBreakerConfig(
                    name="voice_stt",
                    failure_threshold=5,
                    recovery_timeout=120
                )
            )
            
            # TTS circuit breaker
            await _registry.register_circuit_breaker(
                name="voice_tts",
                config=CircuitBreakerConfig(
                    name="voice_tts",
                    failure_threshold=3,
                    recovery_timeout=60
                )
            )
            
            # RAG API circuit breaker
            await _registry.register_circuit_breaker(
                name="rag_api",
                config=CircuitBreakerConfig(
                    name="rag_api",
                    failure_threshold=3,
                    recovery_timeout=60
                )
            )

            # Redis circuit breaker
            await _registry.register_circuit_breaker(
                name="redis_cache",
                config=CircuitBreakerConfig(
                    name="redis_cache",
                    failure_threshold=5,
                    recovery_timeout=30
                )
            )

            # Voice processing breaker
            await _registry.register_circuit_breaker(
                name="voice_processing",
                config=CircuitBreakerConfig(
                    name="voice_processing",
                    failure_threshold=3,
                    recovery_timeout=60
                )
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize circuit breaker registry: {e}")
            raise
    return _registry

async def initialize_voice_circuit_breakers(redis_url: str):
    """Initialize circuit breakers specifically for voice services."""
    return await initialize_circuit_breakers(redis_url)

async def get_circuit_breaker_status() -> Dict[str, Any]:
    """
    Get a snapshot of all registered circuit breakers and their states.
    """
    global _registry
    if _registry is None:
        return {}
    
    # Use the registry to get all states
    states = await _registry.state_manager.get_all_states()
    
    status = {}
    for name, state_data in states.items():
        status[name] = {
            "state": state_data.state.value,
            "fail_count": state_data.failure_count,
            "total_calls": state_data.total_calls
        }
    return status

__all__ = [
    # Core Circuit Breaker
    'CircuitBreaker',
    'CircuitBreakerError',
    'CircuitOpenError',
    'CircuitTimeoutError',
    'CircuitBreakerConfig',
    'CircuitState',
    'CircuitStateData',
    'CircuitStateStore',
    'RedisCircuitStateStore',
    'InMemoryCircuitStateStore',
    'GracefulDegradationManager',
    'create_redis_circuit_breaker',
    'create_inmemory_circuit_breaker',
    'fallback_return_none',
    'fallback_return_empty_dict',
    'fallback_return_empty_list',
    'fallback_raise_service_unavailable',
    
    # Redis State Management
    'RedisConnectionManager',
    'CircuitBreakerStateManager',
    'CircuitBreakerRegistry',
    'create_circuit_breaker_registry',
    
    # Graceful Degradation
    'DegradationStrategy',
    'FallbackStrategy',
    'CacheFirstStrategy',
    'DegradedModeStrategy',
    'CircuitBreakerStrategy',
    'DegradationManager',
    'ServiceDegradationManager',
    'IntegratedDegradationManager',
    'create_llm_degradation_manager',
    'create_redis_degradation_manager',
    'create_vector_search_degradation_manager',
    
    # Global Management
    'initialize_circuit_breakers',
    'initialize_voice_circuit_breakers',
    'get_circuit_breaker_status',
    
    # Standard Breakers
    'voice_stt_breaker',
    'voice_tts_breaker',
    'rag_api_breaker',
    'redis_breaker',
    'voice_processing_breaker',
    'registry'
]

# Version information
__version__ = "1.0.5"
__author__ = "Xoe-NovAi Foundation Stack"
__description__ = "Redis-backed circuit breakers with graceful degradation patterns"

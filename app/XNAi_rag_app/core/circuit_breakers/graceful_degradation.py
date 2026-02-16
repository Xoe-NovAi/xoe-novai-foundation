"""
Graceful Degradation Patterns for Xoe-NovAi Foundation Stack
Provides fallback strategies and degradation patterns for service resilience.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, Awaitable

from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitBreakerError

logger = logging.getLogger(__name__)

T = TypeVar('T')

class DegradationStrategy(ABC):
    """Abstract base class for degradation strategies"""
    
    @abstractmethod
    async def execute(self, func: Callable[[], Awaitable[T]], context: Dict[str, Any]) -> T:
        """Execute function with degradation strategy"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get strategy name"""
        pass

class FallbackStrategy(DegradationStrategy):
    """Simple fallback strategy"""
    
    def __init__(self, fallback_func: Callable[[], Awaitable[T]]):
        self.fallback_func = fallback_func
    
    async def execute(self, func: Callable[[], Awaitable[T]], context: Dict[str, Any]) -> T:
        try:
            return await func()
        except Exception as e:
            logger.warning(f"Primary function failed, using fallback: {e}")
            return await self.fallback_func()
    
    def get_strategy_name(self) -> str:
        return "fallback"

class CacheFirstStrategy(DegradationStrategy):
    """Cache-first strategy with fallback to primary"""
    
    def __init__(
        self,
        cache_func: Callable[[], Awaitable[Optional[T]]],
        fallback_func: Optional[Callable[[], Awaitable[T]]] = None,
        cache_timeout: float = 300.0  # 5 minutes
    ):
        self.cache_func = cache_func
        self.fallback_func = fallback_func
        self.cache_timeout = cache_timeout
        self._last_cache_time: float = 0
        self._cached_value: Optional[T] = None
    
    async def execute(self, func: Callable[[], Awaitable[T]], context: Dict[str, Any]) -> T:
        current_time = time.time()
        
        # Try cache first if not expired
        if (self._cached_value is not None and 
            current_time - self._last_cache_time < self.cache_timeout):
            try:
                cached_value = await self.cache_func()
                if cached_value is not None:
                    logger.info("Using cached value")
                    return cached_value
            except Exception as e:
                logger.warning(f"Cache retrieval failed: {e}")
        
        # Try primary function
        try:
            result = await func()
            self._cached_value = result
            self._last_cache_time = current_time
            return result
        except Exception as e:
            logger.warning(f"Primary function failed: {e}")
            
            # Try fallback
            if self.fallback_func:
                try:
                    return await self.fallback_func()
                except Exception as fallback_e:
                    logger.error(f"Fallback also failed: {fallback_e}")
            
            raise CircuitBreakerError("All strategies failed")
    
    def get_strategy_name(self) -> str:
        return "cache_first"

class DegradedModeStrategy(DegradationStrategy):
    """Degraded mode strategy - returns simplified responses"""
    
    def __init__(self, degraded_response: T):
        self.degraded_response = degraded_response
    
    async def execute(self, func: Callable[[], Awaitable[T]], context: Dict[str, Any]) -> T:
        try:
            return await func()
        except Exception as e:
            logger.warning(f"Service degraded, returning simplified response: {e}")
            return self.degraded_response
    
    def get_strategy_name(self) -> str:
        return "degraded_mode"

class CircuitBreakerStrategy(DegradationStrategy):
    """Circuit breaker strategy"""
    
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.circuit_breaker = circuit_breaker
    
    async def execute(self, func: Callable[[], Awaitable[T]], context: Dict[str, Any]) -> T:
        return await self.circuit_breaker.call(func)
    
    def get_strategy_name(self) -> str:
        return "circuit_breaker"

class DegradationManager:
    """Manages multiple degradation strategies with priority ordering"""
    
    def __init__(self):
        self.strategies: List[DegradationStrategy] = []
        self._strategy_lock = asyncio.Lock()
    
    def add_strategy(self, strategy: DegradationStrategy, priority: int = 1):
        """Add degradation strategy with priority (higher = more important)"""
        self.strategies.append((strategy, priority))
        # Sort by priority (descending)
        self.strategies.sort(key=lambda x: x[1], reverse=True)
    
    def remove_strategy(self, strategy_name: str):
        """Remove strategy by name"""
        self.strategies = [s for s in self.strategies if s[0].get_strategy_name() != strategy_name]
    
    async def execute_with_degradation(
        self,
        func: Callable[[], Awaitable[T]],
        context: Optional[Dict[str, Any]] = None
    ) -> T:
        """Execute function with degradation strategies"""
        if context is None:
            context = {}
        
        # Try strategies in priority order
        for strategy, priority in self.strategies:
            try:
                logger.info(f"Trying strategy: {strategy.get_strategy_name()}")
                return await strategy.execute(func, context)
            except Exception as e:
                logger.warning(f"Strategy {strategy.get_strategy_name()} failed: {e}")
                continue
        
        # All strategies failed
        raise CircuitBreakerError("All degradation strategies failed")
    
    def get_strategy_status(self) -> List[Dict[str, Any]]:
        """Get status of all strategies"""
        status = []
        for strategy, priority in self.strategies:
            strategy_info = {
                "name": strategy.get_strategy_name(),
                "priority": priority
            }
            
            # Add strategy-specific info
            if isinstance(strategy, CircuitBreakerStrategy):
                strategy_info["circuit_breaker_metrics"] = strategy.circuit_breaker.get_metrics()
            
            status.append(strategy_info)
        
        return status

class ServiceDegradationManager:
    """Manager for service-level degradation patterns"""
    
    def __init__(self):
        self.service_managers: Dict[str, DegradationManager] = {}
        self.global_manager = DegradationManager()
    
    def register_service(self, service_name: str):
        """Register a service for degradation management"""
        if service_name not in self.service_managers:
            self.service_managers[service_name] = DegradationManager()
            logger.info(f"Registered service for degradation: {service_name}")
    
    def add_service_strategy(
        self,
        service_name: str,
        strategy: DegradationStrategy,
        priority: int = 1
    ):
        """Add degradation strategy for specific service"""
        if service_name not in self.service_managers:
            self.register_service(service_name)
        
        self.service_managers[service_name].add_strategy(strategy, priority)
    
    def add_global_strategy(
        self,
        strategy: DegradationStrategy,
        priority: int = 1
    ):
        """Add global degradation strategy"""
        self.global_manager.add_strategy(strategy, priority)
    
    async def call_service(
        self,
        service_name: str,
        func: Callable[[], Awaitable[T]],
        context: Optional[Dict[str, Any]] = None
    ) -> T:
        """Call service with degradation management"""
        if context is None:
            context = {}
        
        context["service_name"] = service_name
        
        # Try service-specific strategies first
        if service_name in self.service_managers:
            try:
                return await self.service_managers[service_name].execute_with_degradation(func, context)
            except Exception as e:
                logger.warning(f"Service-specific degradation failed for {service_name}: {e}")
        
        # Try global strategies
        try:
            return await self.global_manager.execute_with_degradation(func, context)
        except Exception as e:
            logger.error(f"All degradation strategies failed for {service_name}: {e}")
            raise CircuitBreakerError(f"Service {service_name} unavailable")
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get degradation status for specific service"""
        if service_name in self.service_managers:
            return {
                "service_name": service_name,
                "strategies": self.service_managers[service_name].get_strategy_status()
            }
        else:
            return {
                "service_name": service_name,
                "error": "Service not registered"
            }
    
    def get_global_status(self) -> Dict[str, Any]:
        """Get global degradation status"""
        return {
            "global_strategies": self.global_manager.get_strategy_status(),
            "registered_services": list(self.service_managers.keys())
        }

# Common degradation patterns factory functions
def create_llm_degradation_manager() -> ServiceDegradationManager:
    """Create degradation manager for LLM services"""
    manager = ServiceDegradationManager()
    
    # Add global fallbacks
    async def llm_fallback():
        return {"response": "Service temporarily unavailable", "degraded": True}
    
    manager.add_global_strategy(DegradedModeStrategy(llm_fallback()))
    
    return manager

def create_redis_degradation_manager() -> ServiceDegradationManager:
    """Create degradation manager for Redis services"""
    manager = ServiceDegradationManager()
    
    # Add in-memory fallback for Redis
    async def redis_fallback():
        logger.warning("Redis unavailable, using in-memory storage")
        return {}
    
    manager.add_global_strategy(FallbackStrategy(redis_fallback()))
    
    return manager

def create_vector_search_degradation_manager() -> ServiceDegradationManager:
    """Create degradation manager for vector search services"""
    manager = ServiceDegradationManager()
    
    # Add cache-first strategy for vector search
    async def cache_func():
        # Implement cache retrieval logic
        return None
    
    async def degraded_response():
        return {"results": [], "degraded": True, "message": "Search temporarily limited"}
    
    manager.add_global_strategy(CacheFirstStrategy(cache_func, degraded_response))
    
    return manager

# Integration with existing circuit breaker system
class IntegratedDegradationManager:
    """Integrated degradation manager that works with circuit breakers"""
    
    def __init__(self):
        self.service_manager = ServiceDegradationManager()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def register_circuit_breaker_service(
        self,
        service_name: str,
        circuit_breaker: CircuitBreaker,
        fallback_func: Optional[Callable[[], Awaitable[T]]] = None
    ):
        """Register service with circuit breaker and degradation"""
        # Add circuit breaker strategy
        cb_strategy = CircuitBreakerStrategy(circuit_breaker)
        self.service_manager.add_service_strategy(service_name, cb_strategy, priority=10)
        
        # Add fallback if provided
        if fallback_func:
            fallback_strategy = FallbackStrategy(fallback_func)
            self.service_manager.add_service_strategy(service_name, fallback_strategy, priority=5)
        
        self.circuit_breakers[service_name] = circuit_breaker
        logger.info(f"Registered circuit breaker service: {service_name}")
    
    async def call_with_integrated_protection(
        self,
        service_name: str,
        func: Callable[[], Awaitable[T]],
        context: Optional[Dict[str, Any]] = None
    ) -> T:
        """Call service with integrated circuit breaker and degradation"""
        return await self.service_manager.call_service(service_name, func, context)
    
    def get_integrated_status(self) -> Dict[str, Any]:
        """Get integrated status including circuit breakers and degradation"""
        return {
            "circuit_breakers": {
                name: cb.get_metrics() 
                for name, cb in self.circuit_breakers.items()
            },
            "degradation_status": self.service_manager.get_global_status()
        }

# Example usage patterns
async def example_usage():
    """Example of how to use the degradation system"""
    
    # Create integrated manager
    integrated_manager = IntegratedDegradationManager()
    
    # Create circuit breaker for LLM service
    from .circuit_breaker import CircuitBreakerConfig, create_redis_circuit_breaker
    import redis.asyncio as redis
    
    redis_client = redis.Redis(host="redis", port=6379, db=0)
    llm_config = CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=60,
        timeout=30,
        name="llm_service"
    )
    
    llm_circuit_breaker = create_redis_circuit_breaker(
        "llm_service",
        redis_client,
        failure_threshold=5,
        recovery_timeout=60,
        timeout=30
    )
    
    # Register with integrated manager
    async def llm_fallback():
        return {"response": "Service temporarily unavailable", "degraded": True}
    
    integrated_manager.register_circuit_breaker_service(
        "llm_service",
        llm_circuit_breaker,
        fallback_func=llm_fallback
    )
    
    # Example function to protect
    async def call_llm_api():
        # Simulate LLM API call
        raise Exception("LLM service temporarily unavailable")
    
    # Call with protection
    try:
        result = await integrated_manager.call_with_integrated_protection(
            "llm_service",
            call_llm_api
        )
        print(f"Result: {result}")
    except Exception as e:
        print(f"Service failed: {e}")
    
    # Get status
    status = integrated_manager.get_integrated_status()
    print(f"Status: {status}")

if __name__ == "__main__":
    asyncio.run(example_usage())
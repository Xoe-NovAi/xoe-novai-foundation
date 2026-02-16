"""
Test Suite for Enhanced Circuit Breaker Implementation
Tests the enhanced circuit breaker functionality with Redis persistence,
detailed logging, adaptive timeouts, and Prometheus metrics integration.
"""

import asyncio
import pytest
import time
import logging
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

from app.XNAi_rag_app.core.circuit_breakers.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitOpenError,
    CircuitTimeoutError,
    CircuitState,
    CircuitStateData,
    RedisCircuitStateStore,
    InMemoryCircuitStateStore,
    GracefulDegradationManager
)
from app.XNAi_rag_app.core.circuit_breakers.redis_state import (
    CircuitBreakerRegistry,
    RedisConnectionManager,
    CircuitBreakerStateManager
)
from app.XNAi_rag_app.core.health.health_monitoring import (
    EnhancedHealthChecker
)

# Configure test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestCircuitBreakerEnhancements:
    """Test enhanced circuit breaker functionality"""
    
    @pytest.fixture
    def circuit_config(self):
        """Test circuit breaker configuration"""
        return CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=10,
            half_open_max_calls=2,
            timeout=5,
            name="test_circuit"
        )
    
    @pytest.fixture
    def inmemory_state_store(self):
        """In-memory state store for testing"""
        return InMemoryCircuitStateStore()
    
    @pytest.fixture
    def circuit_breaker(self, circuit_config, inmemory_state_store):
        """Test circuit breaker instance"""
        return CircuitBreaker(circuit_config, inmemory_state_store)
    
    @pytest.mark.asyncio
    async def test_enhanced_state_transitions(self, circuit_breaker):
        """Test enhanced state transitions with detailed logging"""
        # Test initial state
        state = await circuit_breaker._get_or_create_state()
        assert state.state == CircuitState.CLOSED
        assert state.failure_count == 0
        assert state.transitions == []
        
        # Force state transition to OPEN
        await circuit_breaker._transition_state(state, CircuitState.OPEN)
        
        # Verify transition was logged and recorded
        assert state.state == CircuitState.OPEN
        assert len(state.transitions) == 1
        transition = state.transitions[0]
        assert transition['from_state'] == 'closed'
        assert transition['to_state'] == 'open'
        assert 'timestamp' in transition
        assert 'failure_count' in transition
        assert 'total_failures' in transition
        assert 'total_calls' in transition
    
    @pytest.mark.asyncio
    async def test_transition_history_limit(self, circuit_breaker):
        """Test that transition history is limited to prevent memory growth"""
        state = await circuit_breaker._get_or_create_state()
        
        # Add more than 10 transitions
        for i in range(15):
            new_state = CircuitState.HALF_OPEN if i % 2 == 0 else CircuitState.OPEN
            await circuit_breaker._transition_state(state, new_state)
        
        # Should only keep last 10 transitions
        assert len(state.transitions) == 10
    
    @pytest.mark.asyncio
    async def test_enhanced_metrics_collection(self, circuit_breaker):
        """Test enhanced metrics collection"""
        metrics = circuit_breaker.get_metrics()
        
        assert 'name' in metrics
        assert 'metrics' in metrics
        assert 'config' in metrics
        assert metrics['name'] == 'test_circuit'
        
        # Test metrics are properly initialized
        assert metrics['metrics']['calls'] == 0
        assert metrics['metrics']['failures'] == 0
        assert metrics['metrics']['successes'] == 0
        assert metrics['metrics']['blocked'] == 0
        assert metrics['metrics']['fallbacks'] == 0
    
    @pytest.mark.asyncio
    async def test_enhanced_error_handling(self, circuit_breaker):
        """Test enhanced error handling with detailed context"""
        async def failing_func():
            raise ValueError("Test error")
        
        # Call function that fails
        with pytest.raises(ValueError):
            await circuit_breaker.call(failing_func)
        
        # Verify failure was recorded
        state = await circuit_breaker._get_or_create_state()
        assert state.failure_count == 1
        assert state.total_failures == 1
    
    @pytest.mark.asyncio
    async def test_circuit_open_with_fallback(self, circuit_config, inmemory_state_store):
        """Test circuit breaker opening with fallback function"""
        async def fallback_func():
            return "fallback_result"
        
        circuit_breaker = CircuitBreaker(circuit_config, inmemory_state_store, fallback_func)
        
        # Force circuit to OPEN state
        state = await circuit_breaker._get_or_create_state()
        await circuit_breaker._transition_state(state, CircuitState.OPEN)
        
        # Call should use fallback
        result = await circuit_breaker.call(lambda: "should_not_be_called")
        assert result == "fallback_result"
        
        # Verify fallback was recorded
        metrics = circuit_breaker.get_metrics()
        assert metrics['metrics']['fallbacks'] == 1
    
    @pytest.mark.asyncio
    async def test_circuit_open_without_fallback(self, circuit_config, inmemory_state_store):
        """Test circuit breaker opening without fallback function"""
        circuit_breaker = CircuitBreaker(circuit_config, inmemory_state_store)
        
        # Force circuit to OPEN state
        state = await circuit_breaker._get_or_create_state()
        await circuit_breaker._transition_state(state, CircuitState.OPEN)
        
        # Call should raise CircuitOpenError
        with pytest.raises(CircuitOpenError) as exc_info:
            await circuit_breaker.call(lambda: "should_not_be_called")
        
        assert "test_circuit" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_half_open_to_closed_transition(self, circuit_config, inmemory_state_store):
        """Test transition from HALF_OPEN to CLOSED on success"""
        circuit_breaker = CircuitBreaker(circuit_config, inmemory_state_store)
        
        # Force circuit to HALF_OPEN state
        state = await circuit_breaker._get_or_create_state()
        await circuit_breaker._transition_state(state, CircuitState.HALF_OPEN)
        
        # Call successful function
        result = await circuit_breaker.call(lambda: "success")
        assert result == "success"
        
        # Verify transition to CLOSED
        state = await circuit_breaker._get_or_create_state()
        assert state.state == CircuitState.CLOSED
        assert state.success_count == 0  # Reset on transition
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, circuit_config, inmemory_state_store):
        """Test timeout handling with CircuitTimeoutError"""
        circuit_config.timeout = 1  # Short timeout for testing
        circuit_breaker = CircuitBreaker(circuit_config, inmemory_state_store)
        
        async def slow_func():
            await asyncio.sleep(2)  # Longer than timeout
            return "should_not_return"
        
        # Call should timeout and raise CircuitTimeoutError
        with pytest.raises(CircuitTimeoutError):
            await circuit_breaker.call(slow_func)
        
        # Verify failure was recorded
        state = await circuit_breaker._get_or_create_state()
        assert state.failure_count == 1
        assert state.total_failures == 1

class TestRedisConnectionManager:
    """Test enhanced Redis connection manager"""
    
    @pytest.fixture
    def redis_manager(self):
        """Test Redis connection manager"""
        return RedisConnectionManager(
            host="redis",
            port=6379,
            adaptive_timeout=True,
            connection_timeout=5,
            socket_timeout=10
        )
    
    @pytest.mark.asyncio
    async def test_connection_metrics_tracking(self, redis_manager):
        """Test connection metrics tracking"""
        # Verify metrics attributes are initialized
        assert hasattr(redis_manager, '_connection_latency')
        assert hasattr(redis_manager, '_health_check_latency')
        assert hasattr(redis_manager, '_health_check_failures')
        assert hasattr(redis_manager, '_base_timeout')
        assert hasattr(redis_manager, '_max_timeout')
        assert hasattr(redis_manager, '_timeout_multiplier')
    
    @pytest.mark.asyncio
    async def test_adaptive_timeout_configuration(self):
        """Test adaptive timeout configuration"""
        redis_manager = RedisConnectionManager(
            host="redis",
            port=6379,
            adaptive_timeout=True,
            connection_timeout=3,
            socket_timeout=8
        )
        
        assert redis_manager.adaptive_timeout == True
        assert redis_manager.connection_timeout == 3
        assert redis_manager.socket_timeout == 8
        assert redis_manager._base_timeout == 3
        assert redis_manager._max_timeout == 30
        assert redis_manager._timeout_multiplier == 1.5

class TestCircuitBreakerRegistry:
    """Test enhanced circuit breaker registry"""
    
    @pytest.fixture
    def mock_redis_manager(self):
        """Mock Redis connection manager"""
        manager = Mock()
        manager.is_connected = True
        return manager
    
    @pytest.fixture
    def circuit_breaker_registry(self, mock_redis_manager):
        """Test circuit breaker registry"""
        return CircuitBreakerRegistry(mock_redis_manager)
    
    @pytest.mark.asyncio
    async def test_registry_status(self, circuit_breaker_registry):
        """Test registry status reporting"""
        status = await circuit_breaker_registry.get_registry_status()
        
        assert 'redis_status' in status
        assert 'fallback_status' in status
        assert 'registered_circuits' in status
        assert 'total_circuits' in status
        assert status['registered_circuits'] == []
        assert status['total_circuits'] == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_registration(self, circuit_breaker_registry):
        """Test circuit breaker registration"""
        config = CircuitBreakerConfig(name="test_service", failure_threshold=5)
        
        await circuit_breaker_registry.register_circuit_breaker(
            "test_service",
            config,
            fallback_func=None
        )
        
        # Verify circuit breaker was registered
        assert "test_service" in circuit_breaker_registry.circuit_breakers
        
        # Verify registry status updated
        status = await circuit_breaker_registry.get_registry_status()
        assert "test_service" in status['registered_circuits']
        assert status['total_circuits'] == 1

class TestEnhancedHealthChecker:
    """Test enhanced health checker with Prometheus metrics"""
    
    @pytest.fixture
    def health_checker_config(self):
        """Test health checker configuration"""
        return {
            'targets': ['llm', 'redis', 'memory'],
            'interval_seconds': 5,
            'response_time_threshold': 2.0,
            'error_rate_threshold': 0.1,
            'memory_threshold': 0.8,
            'cpu_threshold': 0.8
        }
    
    @pytest.fixture
    def enhanced_health_checker(self, health_checker_config):
        """Test enhanced health checker"""
        return EnhancedHealthChecker(health_checker_config)
    
    @pytest.mark.asyncio
    async def test_health_checker_initialization(self, enhanced_health_checker):
        """Test enhanced health checker initialization"""
        assert enhanced_health_checker._response_time_threshold == 2.0
        assert enhanced_health_checker._error_rate_threshold == 0.1
        assert enhanced_health_checker._memory_threshold == 0.8
        assert enhanced_health_checker._cpu_threshold == 0.8
        assert enhanced_health_checker.service_health == {}
        assert enhanced_health_checker._response_times == {}
        assert enhanced_health_checker._error_counts == {}
    
    @pytest.mark.asyncio
    async def test_service_health_tracking(self, enhanced_health_checker):
        """Test service health tracking"""
        # Simulate health check for a service
        await enhanced_health_checker._update_service_metrics(
            "test_service",
            True,  # is_healthy
            1.5,   # response_time
            {'test': 'details'}
        )
        
        # Verify service health was created
        assert "test_service" in enhanced_health_checker.service_health
        
        health = enhanced_health_checker.service_health["test_service"]
        assert health.service_name == "test_service"
        assert health.status == "healthy"
        assert health.response_time == 1.5
        assert health.error_count == 0
        assert health.details == {'test': 'details'}
    
    @pytest.mark.asyncio
    async def test_health_status_determination(self, enhanced_health_checker):
        """Test health status determination logic"""
        # Test healthy status
        await enhanced_health_checker._update_service_metrics(
            "healthy_service", True, 1.0, {}
        )
        
        health = enhanced_health_checker.service_health["healthy_service"]
        assert health.status == "healthy"
        
        # Test degraded status (high response time)
        await enhanced_health_checker._update_service_metrics(
            "degraded_service", True, 3.0, {}  # Above threshold
        )
        
        health = enhanced_health_checker.service_health["degraded_service"]
        assert health.status == "degraded"
        
        # Test unhealthy status (failure)
        await enhanced_health_checker._update_service_metrics(
            "unhealthy_service", False, 1.0, {}
        )
        
        health = enhanced_health_checker.service_health["unhealthy_service"]
        assert health.status == "unhealthy"
    
    @pytest.mark.asyncio
    async def test_error_history_tracking(self, enhanced_health_checker):
        """Test error history tracking"""
        # Simulate multiple failures
        for i in range(3):
            await enhanced_health_checker._update_service_metrics(
                "failing_service", False, 2.0, {'error': f'error_{i}'}
            )
        
        health = enhanced_health_checker.service_health["failing_service"]
        assert health.error_count == 3
        assert len(health.error_history) == 3
        
        # Verify error history contains correct data
        for i, error in enumerate(health.error_history):
            assert 'timestamp' in error
            assert 'error_details' in error
            assert 'response_time' in error

class TestGracefulDegradationManager:
    """Test graceful degradation manager"""
    
    @pytest.fixture
    def degradation_manager(self):
        """Test degradation manager"""
        return GracefulDegradationManager()
    
    @pytest.mark.asyncio
    async def test_degradation_manager_registration(self, degradation_manager):
        """Test degradation manager circuit breaker registration"""
        config = CircuitBreakerConfig(name="test_service", failure_threshold=3)
        state_store = InMemoryCircuitStateStore()
        
        await degradation_manager.register_circuit_breaker(
            "test_service",
            config,
            state_store,
            fallback_func=None
        )
        
        # Verify circuit breaker was registered
        assert "test_service" in degradation_manager.circuit_breakers
        
        # Verify degradation strategy was added
        assert "test_service" in degradation_manager.degradation_strategies
    
    @pytest.mark.asyncio
    async def test_degradation_manager_call(self, degradation_manager):
        """Test degradation manager call with circuit breaker"""
        config = CircuitBreakerConfig(name="test_service", failure_threshold=3)
        state_store = InMemoryCircuitStateStore()
        
        await degradation_manager.register_circuit_breaker(
            "test_service",
            config,
            state_store,
            fallback_func=lambda: "fallback"
        )
        
        # Test successful call
        result = await degradation_manager.call_with_degradation(
            "test_service",
            lambda: "success"
        )
        assert result == "success"
        
        # Test fallback call
        result = await degradation_manager.call_with_degradation(
            "test_service",
            lambda: (_ for _ in ()).throw(ValueError("test error"))
        )
        assert result == "fallback"

class TestIntegration:
    """Integration tests for enhanced circuit breaker system"""
    
    @pytest.mark.asyncio
    async def test_full_circuit_breaker_workflow(self):
        """Test complete circuit breaker workflow with all enhancements"""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=5,
            half_open_max_calls=1,
            timeout=3,
            name="integration_test"
        )
        
        state_store = InMemoryCircuitStateStore()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        # Test successful calls
        for i in range(3):
            result = await circuit_breaker.call(lambda: f"success_{i}")
            assert result == f"success_{i}"
        
        # Test failure accumulation
        for i in range(2):
            try:
                await circuit_breaker.call(lambda: (_ for _ in ()).throw(ValueError(f"error_{i}")))
            except ValueError:
                pass
        
        # Verify circuit is open
        state = await circuit_breaker._get_or_create_state()
        assert state.state == CircuitState.OPEN
        assert state.failure_count == 2
        assert state.total_failures == 2
        
        # Test fallback when circuit is open
        async def fallback():
            return "circuit_open_fallback"
        
        circuit_breaker_fallback = CircuitBreaker(config, state_store, fallback)
        result = await circuit_breaker_fallback.call(lambda: "should_not_be_called")
        assert result == "circuit_open_fallback"
        
        # Verify metrics
        metrics = circuit_breaker.get_metrics()
        assert metrics['metrics']['calls'] >= 5
        assert metrics['metrics']['failures'] == 2
        assert metrics['metrics']['fallbacks'] == 1
    
    @pytest.mark.asyncio
    async def test_redis_fallback_functionality(self):
        """Test Redis fallback functionality"""
        # Test with Redis unavailable
        redis_manager = RedisConnectionManager(
            host="nonexistent",
            port=6379,
            adaptive_timeout=True
        )
        
        # Should fail to connect
        connected = await redis_manager.connect()
        assert not connected
        assert redis_manager.fallback_mode == True
        
        # Test state manager with fallback
        state_manager = CircuitBreakerStateManager(redis_manager)
        
        # Should use fallback storage
        test_state = CircuitStateData(
            state=CircuitState.OPEN,
            failure_count=5,
            total_failures=10
        )
        
        success = await state_manager.set_state("test_circuit", test_state)
        assert success  # Should succeed with fallback
        
        retrieved_state = await state_manager.get_state("test_circuit")
        assert retrieved_state is not None
        assert retrieved_state.state == CircuitState.OPEN
        assert retrieved_state.failure_count == 5

# Performance tests
class TestPerformance:
    """Performance tests for enhanced circuit breaker"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_performance(self):
        """Test circuit breaker performance under load"""
        config = CircuitBreakerConfig(
            failure_threshold=10,
            recovery_timeout=30,
            half_open_max_calls=5,
            timeout=1,
            name="performance_test"
        )
        
        state_store = InMemoryCircuitStateStore()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        start_time = time.time()
        
        # Perform many successful calls
        for i in range(100):
            result = await circuit_breaker.call(lambda: f"result_{i}")
            assert result == f"result_{i}"
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly (less than 1 second for 100 calls)
        assert duration < 1.0
        
        # Verify metrics
        metrics = circuit_breaker.get_metrics()
        assert metrics['metrics']['calls'] == 100
        assert metrics['metrics']['successes'] == 100
        assert metrics['metrics']['failures'] == 0
    
    @pytest.mark.asyncio
    async def test_state_transition_performance(self):
        """Test state transition performance"""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=10,
            half_open_max_calls=3,
            timeout=2,
            name="transition_test"
        )
        
        state_store = InMemoryCircuitStateStore()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        start_time = time.time()
        
        # Perform many state transitions
        for i in range(50):
            state = await circuit_breaker._get_or_create_state()
            new_state = CircuitState.HALF_OPEN if i % 2 == 0 else CircuitState.OPEN
            await circuit_breaker._transition_state(state, new_state)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly
        assert duration < 0.5
        
        # Verify transition history is limited
        state = await circuit_breaker._get_or_create_state()
        assert len(state.transitions) <= 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
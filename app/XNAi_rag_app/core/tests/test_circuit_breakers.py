"""
Test suite for Circuit Breakers module
Tests Redis-backed circuit breakers with graceful degradation patterns.
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, AsyncMock, patch
import redis.asyncio as redis

from app.XNAi_rag_app.core.circuit_breakers import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitOpenError,
    CircuitTimeoutError,
    CircuitBreakerConfig,
    CircuitState,
    CircuitStateData,
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


class TestCircuitBreakerConfig:
    """Test CircuitBreakerConfig validation and defaults"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = CircuitBreakerConfig()
        
        assert config.failure_threshold == 5
        assert config.recovery_timeout == 60
        assert config.half_open_max_calls == 3
        assert config.timeout == 30
        assert config.expected_exception == Exception
        assert config.name == "default"
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=120,
            half_open_max_calls=5,
            timeout=60,
            expected_exception=RuntimeError,
            name="custom_service"
        )
        
        assert config.failure_threshold == 3
        assert config.recovery_timeout == 120
        assert config.half_open_max_calls == 5
        assert config.timeout == 60
        assert config.expected_exception == RuntimeError
        assert config.name == "custom_service"


class TestCircuitStateData:
    """Test CircuitStateData initialization and defaults"""
    
    def test_default_state(self):
        """Test default state initialization"""
        state = CircuitStateData()
        
        assert state.state == CircuitState.CLOSED
        assert state.failure_count == 0
        assert state.last_failure_time == 0.0
        assert state.success_count == 0
        assert state.last_success_time == 0.0
        assert state.total_calls == 0
        assert state.total_failures == 0
        assert state.total_successes == 0


class TestRedisCircuitStateStore:
    """Test Redis-based state storage"""
    
    @pytest.fixture
    async def redis_store(self):
        """Create Redis state store for testing"""
        # Use in-memory Redis for testing
        redis_client = redis.Redis(host="localhost", port=6379, db=15, decode_responses=False)
        store = RedisCircuitStateStore(redis_client, "test_circuit:")
        yield store
        await store.redis_client.flushdb()
        await store.redis_client.close()
    
    @pytest.mark.asyncio
    async def test_get_set_state(self, redis_store):
        """Test state persistence and retrieval"""
        state_data = CircuitStateData(
            state=CircuitState.OPEN,
            failure_count=5,
            last_failure_time=time.time()
        )
        
        # Set state
        result = await redis_store.set_state("test_circuit", state_data)
        assert result is True
        
        # Get state
        retrieved_state = await redis_store.get_state("test_circuit")
        assert retrieved_state is not None
        assert retrieved_state.state == CircuitState.OPEN
        assert retrieved_state.failure_count == 5
    
    @pytest.mark.asyncio
    async def test_delete_state(self, redis_store):
        """Test state deletion"""
        state_data = CircuitStateData()
        await redis_store.set_state("test_circuit", state_data)
        
        # Delete state
        result = await redis_store.delete_state("test_circuit")
        assert result is True
        
        # Verify deletion
        retrieved_state = await redis_store.get_state("test_circuit")
        assert retrieved_state is None
    
    @pytest.mark.asyncio
    async def test_missing_state(self, redis_store):
        """Test behavior when state doesn't exist"""
        state = await redis_store.get_state("nonexistent_circuit")
        assert state is None


class TestInMemoryCircuitStateStore:
    """Test in-memory state storage (fallback)"""
    
    @pytest.fixture
    def memory_store(self):
        """Create in-memory state store for testing"""
        return InMemoryCircuitStateStore()
    
    @pytest.mark.asyncio
    async def test_get_set_state(self, memory_store):
        """Test state persistence and retrieval"""
        state_data = CircuitStateData(
            state=CircuitState.HALF_OPEN,
            success_count=2,
            last_success_time=time.time()
        )
        
        # Set state
        result = await memory_store.set_state("test_circuit", state_data)
        assert result is True
        
        # Get state
        retrieved_state = await memory_store.get_state("test_circuit")
        assert retrieved_state is not None
        assert retrieved_state.state == CircuitState.HALF_OPEN
        assert retrieved_state.success_count == 2
    
    @pytest.mark.asyncio
    async def test_delete_state(self, memory_store):
        """Test state deletion"""
        state_data = CircuitStateData()
        await memory_store.set_state("test_circuit", state_data)
        
        # Delete state
        result = await memory_store.delete_state("test_circuit")
        assert result is True
        
        # Verify deletion
        retrieved_state = await memory_store.get_state("test_circuit")
        assert retrieved_state is None


class TestCircuitBreaker:
    """Test CircuitBreaker functionality"""
    
    @pytest.fixture
    def circuit_breaker_config(self):
        """Create test circuit breaker configuration"""
        return CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1,  # Short timeout for testing
            timeout=0.5,         # Short timeout for testing
            name="test_service"
        )
    
    @pytest.fixture
    def memory_store(self):
        """Create in-memory state store"""
        return InMemoryCircuitStateStore()
    
    @pytest.fixture
    def circuit_breaker(self, circuit_breaker_config, memory_store):
        """Create test circuit breaker"""
        return CircuitBreaker(circuit_breaker_config, memory_store)
    
    @pytest.mark.asyncio
    async def test_successful_calls(self, circuit_breaker):
        """Test successful calls don't trigger circuit breaker"""
        async def success_func():
            return "success"
        
        # Make successful calls
        for i in range(5):
            result = await circuit_breaker.call(success_func)
            assert result == "success"
        
        # Check metrics
        metrics = circuit_breaker.get_metrics()
        assert metrics["metrics"]["calls"] == 5
        assert metrics["metrics"]["successes"] == 5
        assert metrics["metrics"]["failures"] == 0
        assert metrics["metrics"]["blocked"] == 0
    
    @pytest.mark.asyncio
    async def test_failure_threshold(self, circuit_breaker):
        """Test circuit opens after failure threshold"""
        async def failure_func():
            raise RuntimeError("Service failed")
        
        # Make calls that fail
        for i in range(3):
            try:
                await circuit_breaker.call(failure_func)
            except RuntimeError:
                pass
        
        # Circuit should be open now
        try:
            await circuit_breaker.call(failure_func)
        except CircuitOpenError:
            pass  # Expected
        
        # Check metrics
        metrics = circuit_breaker.get_metrics()
        assert metrics["metrics"]["failures"] == 3
        assert metrics["metrics"]["blocked"] == 1
    
    @pytest.mark.asyncio
    async def test_circuit_recovery(self, circuit_breaker):
        """Test circuit recovery after timeout"""
        async def failure_func():
            raise RuntimeError("Service failed")
        
        # Make calls that fail to open circuit
        for i in range(3):
            try:
                await circuit_breaker.call(failure_func)
            except RuntimeError:
                pass
        
        # Wait for recovery timeout
        await asyncio.sleep(1.1)
        
        # Circuit should be half-open now
        async def success_func():
            return "recovered"
        
        result = await circuit_breaker.call(success_func)
        assert result == "recovered"
    
    @pytest.mark.asyncio
    async def test_fallback_function(self, circuit_breaker_config, memory_store):
        """Test fallback function execution"""
        async def fallback_func():
            return "fallback_result"
        
        circuit_breaker = CircuitBreaker(
            circuit_breaker_config,
            memory_store,
            fallback_func
        )
        
        async def failure_func():
            raise RuntimeError("Service failed")
        
        # Make calls that fail
        for i in range(3):
            try:
                await circuit_breaker.call(failure_func)
            except RuntimeError:
                pass
        
        # Circuit should be open, fallback should execute
        result = await circuit_breaker.call(failure_func)
        assert result == "fallback_result"
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, circuit_breaker_config, memory_store):
        """Test timeout handling"""
        circuit_breaker = CircuitBreaker(
            circuit_breaker_config,
            memory_store
        )
        
        async def slow_func():
            await asyncio.sleep(1.0)  # Longer than timeout
            return "should_not_return"
        
        # Should timeout
        with pytest.raises(CircuitTimeoutError):
            await circuit_breaker.call(slow_func)
    
    @pytest.mark.asyncio
    async def test_context_manager(self, circuit_breaker):
        """Test context manager usage"""
        async def success_func():
            return "success"
        
        async with circuit_breaker.context():
            result = await success_func()
            assert result == "success"
        
        # Check metrics
        metrics = circuit_breaker.get_metrics()
        assert metrics["metrics"]["successes"] == 1
    
    @pytest.mark.asyncio
    async def test_force_operations(self, circuit_breaker):
        """Test force open/close operations"""
        # Force open
        await circuit_breaker.force_open()
        
        # Should be open
        with pytest.raises(CircuitOpenError):
            await circuit_breaker.call(lambda: "test")
        
        # Force close
        await circuit_breaker.force_close()
        
        # Should work again
        result = await circuit_breaker.call(lambda: "success")
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_reset(self, circuit_breaker):
        """Test circuit breaker reset"""
        async def failure_func():
            raise RuntimeError("Service failed")
        
        # Make some failures
        for i in range(2):
            try:
                await circuit_breaker.call(failure_func)
            except RuntimeError:
                pass
        
        # Reset
        await circuit_breaker.reset()
        
        # Should work again
        result = await circuit_breaker.call(lambda: "success")
        assert result == "success"


class TestGracefulDegradationManager:
    """Test graceful degradation patterns"""
    
    @pytest.fixture
    def degradation_manager(self):
        """Create degradation manager for testing"""
        return GracefulDegradationManager()
    
    @pytest.mark.asyncio
    async def test_register_circuit_breaker(self, degradation_manager):
        """Test circuit breaker registration"""
        config = CircuitBreakerConfig(name="test_service")
        state_store = InMemoryCircuitStateStore()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        degradation_manager.register_circuit_breaker(
            "test_service",
            config,
            state_store
        )
        
        # Should be able to get the circuit breaker
        retrieved = degradation_manager.get_circuit_breaker("test_service")
        assert retrieved is not None
    
    @pytest.mark.asyncio
    async def test_call_with_degradation(self, degradation_manager):
        """Test calling with degradation"""
        config = CircuitBreakerConfig(name="test_service")
        state_store = InMemoryCircuitStateStore()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        degradation_manager.register_circuit_breaker(
            "test_service",
            config,
            state_store
        )
        
        async def success_func():
            return "success"
        
        result = await degradation_manager.call_with_degradation(
            "test_service",
            success_func
        )
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_get_all_metrics(self, degradation_manager):
        """Test getting metrics for all circuit breakers"""
        config = CircuitBreakerConfig(name="test_service")
        state_store = InMemoryCircuitStateStore()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        degradation_manager.register_circuit_breaker(
            "test_service",
            config,
            state_store
        )
        
        metrics = degradation_manager.get_all_metrics()
        assert "test_service" in metrics
        assert "metrics" in metrics["test_service"]
    
    @pytest.mark.asyncio
    async def test_reset_all(self, degradation_manager):
        """Test resetting all circuit breakers"""
        config = CircuitBreakerConfig(name="test_service")
        state_store = InMemoryCircuitStateStore()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        degradation_manager.register_circuit_breaker(
            "test_service",
            config,
            state_store
        )
        
        # Reset all
        await degradation_manager.reset_all()
        
        # Should still be registered but reset
        metrics = degradation_manager.get_all_metrics()
        assert "test_service" in metrics


class TestFactoryFunctions:
    """Test factory functions for circuit breakers"""
    
    @pytest.mark.asyncio
    async def test_create_inmemory_circuit_breaker(self):
        """Test creating in-memory circuit breaker"""
        circuit_breaker = create_inmemory_circuit_breaker(
            name="test_service",
            failure_threshold=2,
            recovery_timeout=30,
            timeout=10
        )
        
        assert circuit_breaker.config.name == "test_service"
        assert circuit_breaker.config.failure_threshold == 2
        assert circuit_breaker.config.recovery_timeout == 30
        assert circuit_breaker.config.timeout == 10
    
    @pytest.mark.asyncio
    async def test_fallback_functions(self):
        """Test fallback function implementations"""
        # Test return None
        result = await fallback_return_none()
        assert result is None
        
        # Test return empty dict
        result = await fallback_return_empty_dict()
        assert result == {}
        
        # Test return empty list
        result = await fallback_return_empty_list()
        assert result == []
        
        # Test raise service unavailable
        with pytest.raises(CircuitBreakerError, match="Service temporarily unavailable"):
            await fallback_raise_service_unavailable()


class TestCircuitBreakerIntegration:
    """Integration tests for circuit breaker patterns"""
    
    @pytest.mark.asyncio
    async def test_complex_failure_scenario(self):
        """Test complex failure and recovery scenario"""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=0.5,
            timeout=0.1
        )
        state_store = InMemoryCircuitStateStore()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        # Initial failures
        async def failure_func():
            raise RuntimeError("Service down")
        
        for i in range(2):
            try:
                await circuit_breaker.call(failure_func)
            except RuntimeError:
                pass
        
        # Circuit should be open
        with pytest.raises(CircuitOpenError):
            await circuit_breaker.call(failure_func)
        
        # Wait for recovery
        await asyncio.sleep(0.6)
        
        # Should be half-open
        async def success_func():
            return "recovered"
        
        result = await circuit_breaker.call(success_func)
        assert result == "recovered"
    
    @pytest.mark.asyncio
    async def test_concurrent_access(self):
        """Test concurrent access to circuit breaker"""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=1,
            timeout=0.5
        )
        state_store = InMemoryCircuitStateStore()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        async def success_func():
            await asyncio.sleep(0.01)
            return "success"
        
        # Run multiple concurrent calls
        tasks = [circuit_breaker.call(success_func) for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all(result == "success" for result in results)
        
        # Check metrics
        metrics = circuit_breaker.get_metrics()
        assert metrics["metrics"]["calls"] == 10
        assert metrics["metrics"]["successes"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
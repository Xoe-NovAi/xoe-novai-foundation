"""
Basic Circuit Breaker Tests
Simple tests that validate the core functionality without requiring async frameworks.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.XNAi_rag_app.core.circuit_breakers.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitStateData,
    CircuitOpenError,
    CircuitTimeoutError
)

class TestCircuitBreakerBasic:
    """Basic tests for circuit breaker functionality"""
    
    def test_circuit_config_creation(self):
        """Test circuit breaker configuration creation"""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60,
            half_open_max_calls=3,
            timeout=30,
            name="test_circuit"
        )
        
        assert config.failure_threshold == 5
        assert config.recovery_timeout == 60
        assert config.half_open_max_calls == 3
        assert config.timeout == 30
        assert config.name == "test_circuit"
    
    def test_circuit_state_data_initialization(self):
        """Test circuit state data initialization"""
        state = CircuitStateData()
        
        assert state.state == CircuitState.CLOSED
        assert state.failure_count == 0
        assert state.last_failure_time == 0.0
        assert state.success_count == 0
        assert state.last_success_time == 0.0
        assert state.total_calls == 0
        assert state.total_failures == 0
        assert state.total_successes == 0
    
    def test_circuit_state_enum_values(self):
        """Test circuit state enum values"""
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"
    
    def test_circuit_open_error_creation(self):
        """Test circuit open error creation"""
        error = CircuitOpenError("test_service", retry_after=30)
        
        assert "test_service" in str(error)
        assert error.details["service_name"] == "test_service"
        assert error.details["retry_after"] == 30
    
    def test_circuit_timeout_error_creation(self):
        """Test circuit timeout error creation"""
        error = CircuitTimeoutError("Operation timed out")
        
        assert "Operation timed out" in str(error)
    
    def test_circuit_breaker_metrics_initialization(self):
        """Test circuit breaker metrics initialization"""
        config = CircuitBreakerConfig(name="test_circuit")
        state_store = Mock()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        metrics = circuit_breaker.get_metrics()
        
        assert metrics['name'] == 'test_circuit'
        assert 'metrics' in metrics
        assert 'config' in metrics
        assert metrics['metrics']['calls'] == 0
        assert metrics['metrics']['failures'] == 0
        assert metrics['metrics']['successes'] == 0
        assert metrics['metrics']['blocked'] == 0
        assert metrics['metrics']['fallbacks'] == 0
    
    def test_circuit_breaker_config_in_metrics(self):
        """Test that circuit breaker config is included in metrics"""
        config = CircuitBreakerConfig(
            failure_threshold=10,
            recovery_timeout=120,
            half_open_max_calls=5,
            timeout=60,
            name="config_test"
        )
        state_store = Mock()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        metrics = circuit_breaker.get_metrics()
        
        assert metrics['config']['failure_threshold'] == 10
        assert metrics['config']['recovery_timeout'] == 120
        assert metrics['config']['half_open_max_calls'] == 5
        assert metrics['config']['timeout'] == 60

class TestCircuitBreakerStateTransitions:
    """Test circuit breaker state transition logic"""
    
    def test_should_open_circuit(self):
        """Test circuit opening logic"""
        config = CircuitBreakerConfig(failure_threshold=3)
        state_store = Mock()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        # Test with failure count below threshold
        state = CircuitStateData(failure_count=2)
        assert not circuit_breaker._should_open_circuit(state)
        
        # Test with failure count at threshold
        state.failure_count = 3
        assert circuit_breaker._should_open_circuit(state)
        
        # Test with failure count above threshold
        state.failure_count = 5
        assert circuit_breaker._should_open_circuit(state)
    
    def test_should_close_circuit(self):
        """Test circuit closing logic"""
        config = CircuitBreakerConfig(half_open_max_calls=3)
        state_store = Mock()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        # Test with success count below threshold
        state = CircuitStateData(success_count=2)
        assert not circuit_breaker._should_close_circuit(state)
        
        # Test with success count at threshold
        state.success_count = 3
        assert circuit_breaker._should_close_circuit(state)
        
        # Test with success count above threshold
        state.success_count = 5
        assert circuit_breaker._should_close_circuit(state)

class TestCircuitBreakerExceptions:
    """Test circuit breaker exception handling"""
    
    def test_circuit_open_error_attributes(self):
        """Test CircuitOpenError attributes"""
        error = CircuitOpenError("redis_service", retry_after=45)
        
        assert error.message == "Circuit breaker open for service: redis_service"
        assert error.details["service_name"] == "redis_service"
        assert error.details["retry_after"] == 45
    
    def test_circuit_timeout_error_attributes(self):
        """Test CircuitTimeoutError attributes"""
        error = CircuitTimeoutError("Database connection timeout")
        
        assert error.message == "Database connection timeout"

class TestCircuitBreakerIntegration:
    """Integration tests for circuit breaker components"""
    
    def test_circuit_breaker_with_mock_state_store(self):
        """Test circuit breaker with mocked state store"""
        config = CircuitBreakerConfig(name="integration_test")
        state_store = Mock()
        
        # Mock state store methods
        state_store.get_state.return_value = CircuitStateData()
        state_store.set_state.return_value = True
        
        circuit_breaker = CircuitBreaker(config, state_store)
        
        # Test that state store methods are called
        state = circuit_breaker._get_or_create_state()
        assert state is not None
        
        # Test metrics
        metrics = circuit_breaker.get_metrics()
        assert metrics['name'] == 'integration_test'
    
    def test_circuit_breaker_reset(self):
        """Test circuit breaker reset functionality"""
        config = CircuitBreakerConfig(name="reset_test")
        state_store = Mock()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        # Mock the reset operation
        circuit_breaker._lock = Mock()
        
        # Test reset method exists and can be called
        try:
            circuit_breaker.reset()
        except Exception as e:
            pytest.fail(f"Circuit breaker reset failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
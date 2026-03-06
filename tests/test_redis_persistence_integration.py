import pytest
import asyncio
import redis.asyncio as redis
from app.XNAi_rag_app.core.circuit_breakers.redis_state import RedisConnectionManager, CircuitBreakerStateManager
from app.XNAi_rag_app.core.circuit_breakers.circuit_breaker import CircuitBreakerConfig, CircuitState, CircuitStateData

@pytest.mark.asyncio
async def test_redis_persistence_lifecycle():
    """Test that circuit breaker state persists in Redis."""
    # Use standard redis host from docker-compose if available, else localhost
    redis_url = "redis://redis:6379/0"
    
    manager = RedisConnectionManager(redis_url=redis_url)
    state_manager = CircuitBreakerStateManager(manager)
    
    # Check if redis is actually reachable
    is_up = await manager.connect()
    if not is_up:
        pytest.skip("Redis not available at redis:6379")

    cb_name = "test-persistence-cb"
    
    # 1. Force state to OPEN
    state_data_open = CircuitStateData(state=CircuitState.OPEN)
    await state_manager.set_state(cb_name, state_data_open)
    
    # 2. Verify state in Redis
    state_data = await state_manager.get_state(cb_name)
    assert state_data is not None
    assert state_data.state == CircuitState.OPEN
    
    # 3. Reset to CLOSED
    state_data_closed = CircuitStateData(state=CircuitState.CLOSED)
    await state_manager.set_state(cb_name, state_data_closed)
    state_data = await state_manager.get_state(cb_name)
    assert state_data.state == CircuitState.CLOSED

@pytest.mark.asyncio
async def test_redis_fallback_to_memory():
    """Test that it falls back to memory when Redis is down."""
    # Intentional bad URL
    bad_manager = RedisConnectionManager(redis_url="redis://non-existent:6379/0")
    state_manager = CircuitBreakerStateManager(bad_manager)
    
    cb_name = "test-fallback-cb"
    
    # Should not raise exception, but use internal memory
    state_data_half = CircuitStateData(state=CircuitState.HALF_OPEN)
    await state_manager.set_state(cb_name, state_data_half)
    state_data = await state_manager.get_state(cb_name)
    
    assert state_data is not None
    assert state_data.state == CircuitState.HALF_OPEN

---
last_updated: 2026-02-15
status: COMPLETE
persona_focus: DevOps Engineers, Distributed Systems Architects, Resilience Engineers
title: "Redis State Management: Circuit Breaker Persistence & Fallback"
---

# Redis State Management: Circuit Breaker Persistence & Fallback

**Version**: 1.0.0  
**Pattern**: Adaptive Resilience with Fallback (Phase 4.2.5)  
**Location**: `app/XNAi_rag_app/core/circuit_breakers/redis_state.py` (410 lines)

---

## Taxonomy & Purpose

The Redis State Management module provides **distributed circuit breaker state persistence with automatic in-memory fallback**, ensuring service stability across Redis connection failures. This is the cornerstone of the Phase 4.2.5 Hardened Circuit Breakers initiative.

### Ma'at Alignment
This module embodies three of the 42 Ideals:
- **Ideal #8 (Resilience)**: Automatic fallback ensures service continuity during infrastructure degradation
- **Ideal #17 (Cooperation)**: Circuit breaker states coordinate across multiple service instances
- **Ideal #33 (Evolution)**: Adaptive timeout mechanisms improve reliability over time

---

## Concepts & Architecture

### Three-Layer State Management

```
┌─────────────────────────────────────────────────────────────┐
│ Circuit Breaker Registry (Coordinator)                       │
│ - Orchestrates multiple circuit breakers                     │
│ - Health monitoring across all circuits                      │
└────────┬──────────────────────────────────────────────────┬──┘
         │                                                  │
    ┌────▼────────────────────┐               ┌────────────▼─────┐
    │ Redis Connection Manager │               │ Circuit Breaker   │
    │ - Connection pooling     │               │ State Manager     │
    │ - Health checking        │               │ - Persistence     │
    │ - Adaptive timeouts      │               │ - Fallback logic  │
    │ - Fallback mode detection│               └───────────────────┘
    └────┬────────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │ Redis Database                     │
    │ - HSETs for state (if available)   │
    │ - Automatic expiration (TTL)       │
    └────────────────────────────────────┘
         
    ┌────────────────────────────────────┐
    │ In-Memory Fallback (Always Active) │
    │ - Dictionary-based storage         │
    │ - Async lock protection            │
    │ - Automatic cleanup of old entries │
    └────────────────────────────────────┘
```

### State Data Model

Each circuit breaker maintains `CircuitStateData`:

```python
@dataclass
class CircuitStateData:
    state: str                           # "closed" | "open" | "half_open"
    failure_count: int                   # Failures since last success
    success_count: int                   # Successes since last failure
    last_failure_time: float             # Unix timestamp
    last_success_time: float             # Unix timestamp
    last_state_change: float             # Timestamp of state transition
```

### Health Check Architecture

The `RedisConnectionManager` runs a background health check loop:

```python
async def _health_check_loop(self):
    """
    Runs every health_check_interval (default 30s)
    - Pings Redis continuously
    - Auto-enters fallback if Redis unavailable
    - Automatically recovers when Redis restores
    """
    while True:
        try:
            if self._is_connected and self._redis_client:
                await self._redis_client.ping()
                # If we reach here and were in fallback, restore
                if self._fallback_mode:
                    self._fallback_mode = False
                    logger.info("Redis restored from fallback")
            else:
                # Connection was lost
                if not self._fallback_mode:
                    logger.warning("Redis unavailable, entering fallback")
                    self._fallback_mode = True
        except Exception as e:
            if not self._fallback_mode:
                logger.warning(f"Health check failed: {e}, fallback activated")
                self._fallback_mode = True
        
        await asyncio.sleep(self.health_check_interval)
```

### Adaptive Timeout Tuning

For high-latency or resource-constrained environments (Ryzen 7 5700U):

```python
class RedisConnectionManager:
    def __init__(self, adaptive_timeout: bool = True, ...):
        self.adaptive_timeout = adaptive_timeout
        self._base_timeout = connection_timeout          # 5s default
        self._max_timeout = 30                           # Don't exceed 30s
        self._timeout_multiplier = 1.5                   # 50% increase per failure
```

**Timeout Adjustment**:
- Initial: 5s
- After 1 failure: 7.5s
- After 2 failures: 11.25s
- After 3+ failures: 30s (capped)

This prevents cascading timeouts on slow systems.

---

## Core Components

### 1. RedisConnectionManager: Connection Lifecycle

Manages Redis connection pooling with health awareness:

#### Initialization
```python
from app.XNAi_rag_app.core.circuit_breakers.redis_state import RedisConnectionManager

redis_mgr = RedisConnectionManager(
    redis_url=None,              # Or "redis://localhost:6379"
    host="redis",                # Docker service name
    port=6379,
    password=None,               # Set if Redis requires auth
    db=0,                        # Database index
    max_connections=50,          # Connection pool size
    health_check_interval=30,    # Check Redis every 30s
    adaptive_timeout=True,       # Enable adaptive timeouts
    connection_timeout=5,        # Initial connection timeout (sec)
    socket_timeout=10            # Socket I/O timeout (sec)
)
```

#### Connection Establishment
```python
# Connect with exponential backoff retry
connected = await redis_mgr.connect()

if redis_mgr.is_connected:
    print("✓ Redis connected")
elif redis_mgr.fallback_mode:
    print("⚠ Using in-memory fallback")
```

**Retry Logic**:
- Attempt 1: Immediate
- Attempt 2: Wait 1s (2^0)
- Attempt 3: Wait 2s (2^1)
- If all fail: Activate fallback mode

#### Health Status
```python
health = await redis_mgr.get_health_status()
print(health)
# Output:
{
    "connected": true,
    "fallback_mode": false,
    "host": "redis",
    "port": 6379,
    "db": 0,
    "max_connections": 50,
    "pool_size": 3
}
```

#### Graceful Disconnection
```python
await redis_mgr.disconnect()
# Cancels health check task, closes client and pool
```

### 2. CircuitBreakerStateManager: Dual-Layer Persistence

Implements circuit breaker state with Redis primary + in-memory fallback:

#### Get State
```python
from app.XNAi_rag_app.core.circuit_breakers import CircuitBreakerStateManager

state_mgr = CircuitBreakerStateManager(redis_mgr)

state = await state_mgr.get_state("my_circuit")
# Returns: CircuitStateData or None

if state:
    print(f"State: {state.state}")
    print(f"Failures: {state.failure_count}")
    print(f"Last failure: {state.last_failure_time}")
```

**Retrieval Priority**:
1. **Redis Available**: Fetch from Redis key `circuit_breaker:my_circuit`
2. **Redis Unavailable**: Use in-memory dictionary `_fallback_states`
3. **Not Found**: Return None (circuit doesn't exist yet)

#### Set State
```python
from app.XNAi_rag_app.core.circuit_breakers.circuit_breaker import CircuitStateData
import time

state = CircuitStateData(
    state="closed",
    failure_count=0,
    success_count=5,
    last_failure_time=0,
    last_success_time=time.time(),
    last_state_change=time.time()
)

success = await state_mgr.set_state("my_circuit", state)
# Returns: True if Redis write succeeded, False if using fallback
```

**Storage Behavior**:
1. **Redis Available**: 
   - Writes to `circuit_breaker:my_circuit` with 1-hour TTL
   - Also updates in-memory backup
2. **Redis Unavailable**:
   - Only in-memory write (logged as fallback)
   - Survives service restart if state_mgr persists

#### Delete State
```python
success = await state_mgr.delete_state("my_circuit")
# Removes from both Redis and in-memory
```

#### List All States
```python
all_states = await state_mgr.get_all_states()
# Output: {"circuit1": CircuitStateData(...), "circuit2": ...}
# Merges Redis + in-memory states, Redis takes precedence
```

#### Cleanup Expired States
```python
await state_mgr.cleanup_expired_states()
# Removes in-memory states older than 1 hour
# (Redis TTL handles server-side expiration automatically)
```

#### Fallback Status
```python
fallback_status = await state_mgr.get_fallback_status()
print(fallback_status)
# Output:
{
    "fallback_states_count": 3,
    "fallback_states": ["circuit1", "circuit2", "circuit3"]
}
```

### 3. CircuitBreakerRegistry: Multi-Circuit Orchestration

Manages all circuit breakers in a service:

#### Register Circuit Breaker
```python
from app.XNAi_rag_app.core.circuit_breakers import CircuitBreakerRegistry, CircuitBreakerConfig

registry = CircuitBreakerRegistry(redis_mgr)

config = CircuitBreakerConfig(
    failure_threshold=5,         # Open after 5 failures
    success_threshold=2,         # Close after 2 successes in half-open
    timeout=60,                  # Attempt half-open after 60s
    max_timeout=300
)

async def fallback_response():
    return {"status": "service unavailable", "fallback": True}

await registry.register_circuit_breaker(
    name="external_api",
    config=config,
    fallback_func=fallback_response
)
```

#### Call Through Circuit Breaker
```python
async def call_external_api():
    # Make the actual API call
    response = await httpx.get("https://external-api.com/data")
    return response.json()

# Protected call
result = await registry.call_with_circuit_breaker("external_api", call_external_api)
# If circuit is open, returns fallback_response() instead
```

#### Registry Status
```python
status = await registry.get_registry_status()
print(status)
# Output:
{
    "redis_status": {
        "connected": true,
        "fallback_mode": false,
        "pool_size": 2
    },
    "fallback_status": {
        "fallback_states_count": 0,
        "fallback_states": []
    },
    "registered_circuits": ["external_api", "database", "cache"],
    "total_circuits": 3
}
```

#### Cleanup
```python
await registry.cleanup()
# Expires old states and closes Redis connection
```

### 4. Factory Function: Convenience Setup

```python
from app.XNAi_rag_app.core.circuit_breakers.redis_state import create_circuit_breaker_registry

registry = await create_circuit_breaker_registry(
    redis_url="redis://redis:6379/0",
    # OR individual params:
    host="redis",
    port=6379,
    password="secret",
    db=0
)

# Registry is ready to use
```

---

## Instructions: Implementation Patterns

### 1. **Basic Service Integration**

```python
from fastapi import FastAPI, HTTPException
from app.XNAi_rag_app.core.circuit_breakers.redis_state import create_circuit_breaker_registry
from app.XNAi_rag_app.core.circuit_breakers import CircuitBreakerConfig

app = FastAPI()

# Initialize at startup
registry = None

@app.on_event("startup")
async def startup():
    global registry
    registry = await create_circuit_breaker_registry(host="redis")
    
    # Register circuits for all external dependencies
    config = CircuitBreakerConfig(failure_threshold=5, timeout=60)
    await registry.register_circuit_breaker(
        "database",
        config,
        fallback_func=lambda: {"error": "database unavailable"}
    )

@app.on_event("shutdown")
async def shutdown():
    await registry.cleanup()

@app.get("/data")
async def get_data():
    async def fetch_from_db():
        # Actual database query
        return await db.query("SELECT * FROM users")
    
    try:
        result = await registry.call_with_circuit_breaker("database", fetch_from_db)
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service unavailable")
```

### 2. **Multi-Environment Configuration**

```python
import os

REDIS_CONFIG = {
    "development": {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "max_connections": 10,
        "health_check_interval": 60,
        "adaptive_timeout": True
    },
    "staging": {
        "host": os.getenv("REDIS_HOST", "redis-staging"),
        "port": 6379,
        "db": 0,
        "max_connections": 50,
        "health_check_interval": 30,
        "adaptive_timeout": True,
        "password": os.getenv("REDIS_PASSWORD")
    },
    "production": {
        "redis_url": os.getenv("REDIS_URL"),  # Use URL with SSL, replicas
        "max_connections": 100,
        "health_check_interval": 10,
        "adaptive_timeout": False  # Disable in prod, use static timeouts
    }
}

env = os.getenv("ENVIRONMENT", "development")
registry = await create_circuit_breaker_registry(**REDIS_CONFIG[env])
```

### 3. **Fallback Recovery Monitoring**

```python
import asyncio

async def monitor_fallback_status(registry, check_interval=60):
    """Alert if fallback is actively used"""
    while True:
        status = await registry.get_registry_status()
        redis_connected = status["redis_status"]["connected"]
        fallback_active = status["fallback_status"]["fallback_states_count"] > 0
        
        if not redis_connected:
            logger.warning(f"⚠ Redis unavailable, using fallback for {fallback_active} circuits")
            # Send alert (PagerDuty, Slack, etc.)
            alert_ops_team("Redis connection lost")
        elif fallback_active:
            logger.warning(f"⚠ Redis recovered but {fallback_active} circuits still in fallback")
            # Request manual validation
        else:
            logger.info("✓ All circuits healthy, Redis connected")
        
        await asyncio.sleep(check_interval)

# Start monitoring task
asyncio.create_task(monitor_fallback_status(registry))
```

### 4. **Graceful Degradation with Tiered Fallbacks**

```python
async def call_with_tiered_fallback(registry, circuit_name, func, fallback_tiers):
    """
    Implements cascading fallbacks:
    1. Try with circuit breaker
    2. If open, use memory cache
    3. If cache miss, use stale data
    4. If stale miss, return minimal response
    """
    try:
        return await registry.call_with_circuit_breaker(circuit_name, func)
    except Exception as e:
        logger.warning(f"Circuit {circuit_name} failed: {e}")
        
        # Tier 1: In-memory cache
        cached = await memory_cache.get(circuit_name)
        if cached:
            logger.info(f"Using cached response for {circuit_name}")
            return cached
        
        # Tier 2: Redis cache (independent from circuit breaker)
        stale = await redis_cache.get(f"{circuit_name}:stale")
        if stale:
            logger.warning(f"Using stale data for {circuit_name}")
            return stale
        
        # Tier 3: Minimal response
        if hasattr(fallback_tiers, circuit_name):
            logger.critical(f"Using minimal fallback for {circuit_name}")
            return getattr(fallback_tiers, circuit_name)
        
        raise
```

---

## Reference: Configuration Tuning for Ryzen 7 5700U

### Recommended Settings

```python
# For low-resource systems (6GB RAM, shared with other services)
LOW_RESOURCE_CONFIG = {
    "max_connections": 20,           # Limit pool size
    "health_check_interval": 60,     # Less frequent checks to save CPU
    "connection_timeout": 10,        # Longer timeout for I/O
    "socket_timeout": 15,
    "adaptive_timeout": True,        # Allow graceful degradation
}

# For standard systems (16GB+ RAM, dedicated service)
STANDARD_CONFIG = {
    "max_connections": 50,
    "health_check_interval": 30,
    "connection_timeout": 5,
    "socket_timeout": 10,
    "adaptive_timeout": False,       # Use fixed timeouts
}

# For high-performance systems (32GB+, Kubernetes)
HIGH_PERF_CONFIG = {
    "max_connections": 200,
    "health_check_interval": 10,
    "connection_timeout": 2,
    "socket_timeout": 5,
    "adaptive_timeout": False,
}
```

### Memory Impact

| Setting | Memory per Connection | Notes |
|---------|----------------------|-------|
| `max_connections: 20` | ~100KB per | Total: 2MB overhead |
| `max_connections: 50` | ~100KB per | Total: 5MB overhead |
| `max_connections: 100` | ~100KB per | Total: 10MB overhead |
| Fallback in-memory | Proportional to circuit count | ~5KB per circuit |

For Ryzen 7 5700U (6GB system), use `max_connections: 20-30`.

---

## Troubleshooting Guide

### Issue: "Redis connection failed after all attempts"
**Causes**:
1. Redis container not running
2. Hostname/port misconfiguration
3. Password mismatch

**Solution**:
```bash
# Check Redis status
docker ps | grep redis

# Test connectivity
redis-cli -h redis -p 6379 ping
# Should output: PONG

# Check environment variables
echo $REDIS_HOST $REDIS_PORT $REDIS_PASSWORD

# Verify in docker-compose.yml
docker-compose logs redis | tail -20
```

### Issue: "State stored in fallback only" warnings
**Cause**: Redis temporarily unavailable but being used; circuit breaker state not persisted  
**Impact**: If service restarts while Redis is down, circuit breaker resets to initial state

**Solution**:
```python
# Periodically flush fallback to Redis when it recovers
async def recover_fallback_states(state_mgr):
    fallback_status = await state_mgr.get_fallback_status()
    if fallback_status["fallback_states_count"] > 0:
        logger.info(f"Recovering {fallback_status['fallback_states_count']} states to Redis")
        all_states = await state_mgr.get_all_states()
        for name, state in all_states.items():
            try:
                await state_mgr.set_state(name, state)
            except Exception as e:
                logger.error(f"Failed to recover {name}: {e}")

# Call when Redis restores
if redis_mgr.is_connected and not was_connected_before:
    asyncio.create_task(recover_fallback_states(state_mgr))
```

### Issue: "Expired states not cleaning up"
**Cause**: In-memory cleanup only runs explicitly; Redis TTL expires server-side  
**Impact**: Long-running services accumulate old state entries

**Solution**:
```python
# Schedule periodic cleanup
import asyncio

async def cleanup_loop(state_mgr, interval=3600):  # Hourly
    while True:
        await state_mgr.cleanup_expired_states()
        logger.info("Cleaned up expired circuit breaker states")
        await asyncio.sleep(interval)

# Start at service startup
asyncio.create_task(cleanup_loop(state_mgr))
```

---

## Integration Points

### With Circuit Breaker Protection
```python
# See circuit-breaker-architecture.md for full details
from app.XNAi_rag_app.core.circuit_breakers import CircuitBreaker, RedisCircuitStateStore

# State manager is used by circuit breaker internally
state_store = RedisCircuitStateStore(redis_client, key_prefix="circuit_breaker:")
breaker = CircuitBreaker(config, state_store)
```

### With Monitoring & Alerting
```python
from prometheus_client import Gauge, Counter

redis_connected = Gauge("redis_connected", "Redis connection status")
fallback_states = Gauge("fallback_states_active", "Circuits in fallback")
state_persistence_failures = Counter("state_persistence_failures_total", "Failed Redis writes")

async def update_metrics(registry):
    status = await registry.get_registry_status()
    redis_connected.set(1 if status["redis_status"]["connected"] else 0)
    fallback_states.set(status["fallback_status"]["fallback_states_count"])

# Call periodically
asyncio.create_task(update_metrics_loop(registry))
```

---

## Testing

### Unit Test Example
```python
import pytest
from app.XNAi_rag_app.core.circuit_breakers.redis_state import (
    RedisConnectionManager, CircuitBreakerStateManager
)
from app.XNAi_rag_app.core.circuit_breakers.circuit_breaker import CircuitStateData
import time

@pytest.fixture
async def redis_mgr():
    mgr = RedisConnectionManager(host="redis", port=6379)
    await mgr.connect()
    yield mgr
    await mgr.disconnect()

@pytest.mark.asyncio
async def test_fallback_on_redis_disconnect(redis_mgr):
    state_mgr = CircuitBreakerStateManager(redis_mgr)
    
    # Create initial state
    state = CircuitStateData(
        state="closed",
        failure_count=0,
        success_count=5,
        last_failure_time=time.time(),
        last_success_time=time.time(),
        last_state_change=time.time()
    )
    
    # Set in Redis
    success = await state_mgr.set_state("test_circuit", state)
    assert success is True
    
    # Retrieve from Redis
    retrieved = await state_mgr.get_state("test_circuit")
    assert retrieved.state == "closed"
    
    # Simulate Redis disconnect
    await redis_mgr.disconnect()
    
    # Fallback should still work
    assert redis_mgr.fallback_mode is True
    retrieved_fallback = await state_mgr.get_state("test_circuit")
    assert retrieved_fallback.state == "closed"
```

---

## Performance Characteristics

| Operation | Time (ms) | Notes |
|-----------|-----------|-------|
| Connect (first time) | 50-200 | Includes retry logic |
| Get state (Redis hit) | 5-15 | Single Redis GET |
| Get state (fallback) | <1 | In-memory dictionary |
| Set state (Redis) | 10-25 | Redis SET + TTL |
| Set state (fallback) | <1 | Dictionary update |
| Health check | 5-10 | Background ping |

### Scalability

- **Circuits**: Can manage 100+ circuit breakers in single registry
- **Concurrent Calls**: Health check and state operations are async-safe
- **Memory**: ~5KB per circuit in fallback, 0 on Redis (TTL cleanup)

---

## Related Documentation

- **[Circuit Breaker Architecture](circuit-breaker-architecture.md)** - Consumes this state management
- **[IAM Database Management](04-iam-database-management.md)** - Similar persistence patterns
- **[Phase 4.2 Completion Report](../../PHASE-4.2-COMPLETION-REPORT.md)** - Implementation milestone
- **[Docker Compose Configuration](../../docker-compose.yml)** - Redis service definition

---

**Last Reviewed**: 2026-02-15  
**Next Review**: 2026-03-15 (Fallback performance analysis under load)

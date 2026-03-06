# Xoe-NovAi Foundation Stack - Core Module

Comprehensive circuit breakers, health monitoring, and graceful degradation system for the Xoe-NovAi Foundation Stack.

## Overview

This module provides enterprise-grade resilience patterns for the Xoe-NovAi Foundation Stack, including:

- **Circuit Breakers**: Redis-backed with graceful degradation and async safety
- **Health Monitoring**: Comprehensive service health checking with automated recovery
- **Graceful Degradation**: Multiple fallback strategies for service resilience

## Architecture

```
Core Module
├── Circuit Breakers
│   ├── Redis State Management
│   ├── Graceful Degradation Patterns
│   └── Service Registry
└── Health Monitoring
    ├── Health Checkers
    └── Recovery Manager
```

## Quick Start

### Basic Circuit Breaker Usage

```python
from app.XNAi_rag_app.core import create_redis_circuit_breaker, fallback_return_none
import redis.asyncio as redis

# Create Redis client
redis_client = redis.Redis(host="redis", port=6379, db=0)

# Create circuit breaker
circuit_breaker = create_redis_circuit_breaker(
    name="llm_service",
    redis_client=redis_client,
    failure_threshold=5,
    recovery_timeout=60,
    timeout=30,
    fallback_func=fallback_return_none
)

# Use circuit breaker
async def call_llm_service():
    return await circuit_breaker.call(
        lambda: expensive_llm_operation()
    )
```

### Health Monitoring Setup

```python
from app.XNAi_rag_app.core import HealthMonitor, create_rag_api_health_checker

# Create health monitor
monitor = HealthMonitor(check_interval=30.0)

# Add health checkers
monitor.add_checker(create_rag_api_health_checker())
monitor.add_checker(create_redis_health_checker(redis_client))

# Start monitoring
await monitor.start_monitoring()

# Get health report
report = monitor.get_health_report()
```

### Graceful Degradation

```python
from app.XNAi_rag_app.core import ServiceDegradationManager, FallbackStrategy

# Create degradation manager
degradation_manager = ServiceDegradationManager()

# Add fallback strategy
async def llm_fallback():
    return {"response": "Service temporarily unavailable", "degraded": True}

degradation_manager.add_service_strategy(
    "llm_service",
    FallbackStrategy(llm_fallback),
    priority=10
)

# Use with degradation
result = await degradation_manager.call_service(
    "llm_service",
    expensive_llm_operation
)
```

## Circuit Breaker Features

### Redis-Backed State Persistence
- Automatic Redis connection management with fallback
- State persistence across service restarts
- Health monitoring with automatic recovery

### Graceful Degradation Patterns
- **Fallback Strategy**: Simple fallback function execution
- **Cache-First Strategy**: Try cache before primary, with fallback
- **Degraded Mode Strategy**: Return simplified responses
- **Circuit Breaker Strategy**: Integrated with circuit breaker system

### Async Safety
- Thread-safe operations with asyncio locks
- Proper resource cleanup and context management
- Memory-safe buffer implementations

## Health Monitoring Features

### Comprehensive Health Checks
- **HTTP Health Checker**: Monitor HTTP endpoints
- **Redis Health Checker**: Monitor Redis connectivity and performance
- **Database Health Checker**: Monitor PostgreSQL health
- **Custom Health Checker**: User-defined health checks

### Automated Recovery
- **Service Restart**: Automatic service restart on failure
- **Cache Clearing**: Clear stale cache data
- **Database Reconnection**: Reconnect to databases
- **Configuration Reload**: Reload service configuration
- **Manual Intervention**: Escalate to manual intervention

### Recovery Rules
- Configurable failure thresholds
- Multiple retry attempts with exponential backoff
- Cooldown periods to prevent thrashing
- Custom recovery functions

## Configuration

### Circuit Breaker Configuration

```python
from app.XNAi_rag_app.core import CircuitBreakerConfig

config = CircuitBreakerConfig(
    failure_threshold=5,      # Number of failures before opening
    recovery_timeout=60,      # Seconds before trying half-open
    half_open_max_calls=3,    # Max calls in half-open state
    timeout=30,              # Operation timeout in seconds
    expected_exception=Exception,
    name="my_service"
)
```

### Redis Configuration

```python
from app.XNAi_rag_app.core import RedisConnectionManager

redis_manager = RedisConnectionManager(
    redis_url="redis://localhost:6379/0",
    max_connections=50,
    health_check_interval=30
)
```

### Health Monitor Configuration

```python
from app.XNAi_rag_app.core import HealthMonitor

monitor = HealthMonitor(
    check_interval=30.0,      # Seconds between checks
    alert_thresholds={
        "success_rate": 95,    # Alert if success rate drops below 95%
        "response_time": 5.0   # Alert if response time exceeds 5s
    }
)
```

## Integration Examples

### RAG API Integration

```python
from app.XNAi_rag_app.core import (
    create_redis_circuit_breaker,
    create_rag_api_health_checker,
    HealthMonitor
)
import redis.asyncio as redis

async def setup_rag_api_protection():
    # Setup Redis
    redis_client = redis.Redis(host="redis", port=6379, db=0)
    
    # Create circuit breaker for RAG API
    rag_circuit_breaker = create_redis_circuit_breaker(
        name="rag_api",
        redis_client=redis_client,
        failure_threshold=3,
        recovery_timeout=60,
        timeout=30
    )
    
    # Create health monitor
    monitor = HealthMonitor(check_interval=30.0)
    monitor.add_checker(create_rag_api_health_checker())
    
    # Add recovery callback
    async def rag_recovery_callback(service_name: str):
        logger.info(f"RAG API recovered, clearing cache")
        # Clear cache logic here
    
    monitor.add_recovery_callback("rag_api", rag_recovery_callback)
    
    return rag_circuit_breaker, monitor
```

### Chainlit UI Integration

```python
from app.XNAi_rag_app.core import (
    create_chainlit_ui_health_checker,
    create_redis_circuit_breaker
)

async def setup_chainlit_protection():
    # Create health checker for Chainlit UI
    chainlit_checker = create_chainlit_ui_health_checker()
    
    # Create circuit breaker for UI operations
    ui_circuit_breaker = create_redis_circuit_breaker(
        name="chainlit_ui",
        redis_client=redis_client,
        failure_threshold=2,
        recovery_timeout=30,
        timeout=10
    )
    
    return chainlit_checker, ui_circuit_breaker
```

## Monitoring and Observability

### Health Reports

```python
# Get comprehensive health report
report = monitor.get_health_report()

# Report structure
{
    "timestamp": 1234567890.123,
    "monitoring_active": true,
    "services": {
        "rag_api": {
            "status": "healthy",
            "last_check": 1234567890.123,
            "response_time": 0.123,
            "consecutive_failures": 0,
            "consecutive_successes": 150,
            "total_checks": 150,
            "details": {...}
        }
    },
    "summary": {
        "total": 4,
        "healthy": 4,
        "degraded": 0,
        "unhealthy": 0,
        "unknown": 0
    }
}
```

### Recovery Statistics

```python
# Get recovery statistics
stats = recovery_manager.get_recovery_stats()

# Stats structure
{
    "total_attempts": 15,
    "success_rate": 0.8,
    "average_recovery_time": 45.2,
    "actions_by_type": {
        "restart_service": 10,
        "clear_cache": 3,
        "manual_intervention": 2
    },
    "recent_failures": [...]
}
```

## Best Practices

### Circuit Breaker Usage
1. **Set Appropriate Thresholds**: Balance between responsiveness and stability
2. **Implement Meaningful Fallbacks**: Provide useful degraded responses
3. **Monitor Circuit States**: Track circuit breaker metrics
4. **Test Recovery**: Verify recovery mechanisms work correctly

### Health Monitoring
1. **Comprehensive Coverage**: Monitor all critical services
2. **Appropriate Intervals**: Balance monitoring frequency with resource usage
3. **Meaningful Alerts**: Configure alerts for actionable issues
4. **Recovery Testing**: Regularly test recovery procedures

### Graceful Degradation
1. **Prioritize User Experience**: Always provide some level of service
2. **Cache Strategically**: Use caching to improve resilience
3. **Monitor Degradation**: Track when and why degradation occurs
4. **Plan for Recovery**: Ensure degraded services can recover

## Troubleshooting

### Common Issues

#### Redis Connection Problems
```python
# Check Redis connection
redis_manager = RedisConnectionManager(...)
await redis_manager.connect()
status = await redis_manager.get_health_status()
print(f"Redis connected: {status['connected']}")
```

#### Circuit Breaker Stuck Open
```python
# Force circuit breaker closed
await circuit_breaker.force_close()

# Check circuit state
metrics = circuit_breaker.get_metrics()
print(f"Circuit state: {metrics['state']}")
```

#### Health Checks Failing
```python
# Trigger manual health check
result = await monitor.trigger_manual_check("service_name")
print(f"Health check result: {result.status}")
```

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check circuit breaker metrics:
```python
metrics = circuit_breaker.get_metrics()
print(json.dumps(metrics, indent=2))
```

## Performance Considerations

### Circuit Breaker Performance
- Circuit breaker checks add ~1-2ms overhead per call
- Redis operations are async and non-blocking
- Memory usage is bounded by configuration

### Health Monitoring Performance
- Health checks run in background tasks
- Check intervals should balance responsiveness with resource usage
- Consider staggering checks to avoid thundering herd

### Recovery Performance
- Recovery actions should be fast and reliable
- Implement proper timeouts for recovery operations
- Use exponential backoff for retry logic

## Security Considerations

### Redis Security
- Use Redis authentication in production
- Implement network security for Redis connections
- Monitor Redis for unusual activity

### Health Check Security
- Secure health check endpoints
- Implement authentication for sensitive health data
- Avoid exposing sensitive information in health responses

### Circuit Breaker Security
- Validate fallback responses
- Implement proper error handling
- Monitor for circuit breaker abuse

## Future Enhancements

### Planned Features
- **Metrics Integration**: Prometheus/Grafana integration
- **Alerting**: Slack/Email/PagerDuty integration
- **Auto-scaling**: Integration with Kubernetes auto-scaling
- **Machine Learning**: ML-based anomaly detection

### Extension Points
- Custom health check implementations
- Additional recovery action types
- Integration with external monitoring systems
- Advanced degradation strategies

## Contributing

When contributing to this module:

1. Follow the existing code patterns and conventions
2. Add comprehensive tests for new features
3. Update documentation for any public APIs
4. Ensure backward compatibility
5. Test with the full Xoe-NovAi Foundation Stack

## License

This module is part of the Xoe-NovAi Foundation Stack and follows the same licensing terms.
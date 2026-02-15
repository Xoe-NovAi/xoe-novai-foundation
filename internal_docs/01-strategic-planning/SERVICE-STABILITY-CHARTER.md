# SERVICE-STABILITY-CHARTER

**Version**: 1.0.0  
**Status**: DRAFT  
**Priority**: P0 - CRITICAL  
**Owner**: Cline_CLI-Kat  
**Created**: 2026-02-13  
**Ma'at Alignment**: #18 Balance (Service Equilibrium)

## Executive Summary

Establish comprehensive service stability and error handling patterns for the Xoe-NovAi Foundation stack. This charter focuses on implementing circuit breakers, graceful degradation, and robust error recovery mechanisms across all services, with special attention to Redis resilience and service health monitoring.

## Objectives

### Primary Goals
- [ ] **Circuit Breaker Implementation**: Deploy circuit breakers across all external service calls
- [ ] **Graceful Degradation**: Implement fallback mechanisms for critical services
- [ ] **Redis Resilience**: Create robust Redis connection patterns with automatic failover
- [ ] **Service Health Monitoring**: Establish comprehensive health checks and alerting

### Success Criteria
- [ ] 99.9% service availability with graceful degradation
- [ ] Zero single points of failure for critical services
- [ ] Sub-5-second recovery time for service failures
- [ ] Complete error handling coverage across all services

## Architecture

### System Components

#### 1. Circuit Breaker Framework
```python
# Comprehensive circuit breaker implementation
import asyncio
import time
import logging
from typing import Any, Callable, Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: tuple = (Exception,)
    timeout: int = 30
    name: str = "default"

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.success_count = 0
        self.half_open_max_calls = 3
        self.logger = logging.getLogger(f"CircuitBreaker.{config.name}")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                self.logger.info(f"Circuit breaker {self.config.name} transitioning to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise Exception(f"Circuit breaker {self.config.name} is OPEN")
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            self._on_success()
            return result
            
        except self.config.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful execution"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_max_calls:
                self.logger.info(f"Circuit breaker {self.config.name} transitioning to CLOSED")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        self.logger.warning(
            f"Circuit breaker {self.config.name} failure {self.failure_count}/{self.config.failure_threshold}"
        )
        
        if self.failure_count >= self.config.failure_threshold:
            self.logger.error(f"Circuit breaker {self.config.name} OPENING")
            self.state = CircuitState.OPEN

# Decorator for easy use
def circuit_breaker(config: CircuitBreakerConfig):
    breaker = CircuitBreaker(config)
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator
```

#### 2. Redis Resilience Layer
```python
# Enhanced Redis connection with comprehensive resilience
import redis
import time
import json
import logging
from typing import Optional, Any, Dict, List
from dataclasses import dataclass
from enum import Enum

class RedisConnectionState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    FALLBACK = "fallback"

@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    socket_connect_timeout: int = 5
    socket_timeout: int = 5
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    max_retries: int = 3
    fallback_enabled: bool = True

class ResilientRedisManager:
    def __init__(self, config: RedisConfig):
        self.config = config
        self.connection = None
        self.state = RedisConnectionState.HEALTHY
        self.last_health_check = 0
        self.connection_attempts = 0
        self.fallback_storage = LocalRedisFallback()
        self.logger = logging.getLogger("ResilientRedisManager")
    
    async def get_connection(self) -> redis.Redis:
        """Get Redis connection with resilience"""
        current_time = time.time()
        
        # Check if we need health check
        if current_time - self.last_health_check > self.config.health_check_interval:
            await self._perform_health_check()
        
        # Try to get connection
        if self.state in [RedisConnectionState.HEALTHY, RedisConnectionState.DEGRADED]:
            try:
                if not self.connection or not await self._is_connection_healthy():
                    self.connection = await self._create_connection()
                    self.state = RedisConnectionState.HEALTHY
                    self.connection_attempts = 0
                return self.connection
            except Exception as e:
                self.logger.error(f"Redis connection failed: {e}")
                self.state = RedisConnectionState.FAILED
                self.connection_attempts += 1
        
        # Use fallback if enabled
        if self.config.fallback_enabled:
            self.logger.warning("Using fallback storage due to Redis failure")
            return self.fallback_storage
        
        # No fallback available, raise error
        raise ConnectionError("Redis unavailable and no fallback configured")
    
    async def _perform_health_check(self):
        """Perform comprehensive health check"""
        try:
            if self.connection:
                # Test connection with ping
                await asyncio.to_thread(self.connection.ping)
                self.state = RedisConnectionState.HEALTHY
                self.connection_attempts = 0
            else:
                self.state = RedisConnectionState.FAILED
        except Exception as e:
            self.logger.warning(f"Redis health check failed: {e}")
            if self.connection_attempts > self.config.max_retries:
                self.state = RedisConnectionState.FAILED
            else:
                self.state = RedisConnectionState.DEGRADED
        finally:
            self.last_health_check = time.time()
    
    async def _create_connection(self) -> redis.Redis:
        """Create new Redis connection"""
        try:
            connection = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                socket_connect_timeout=self.config.socket_connect_timeout,
                socket_timeout=self.config.socket_timeout,
                retry_on_timeout=self.config.retry_on_timeout,
                health_check_interval=self.config.health_check_interval
            )
            # Test connection
            await asyncio.to_thread(connection.ping)
            self.logger.info("Redis connection established successfully")
            return connection
        except Exception as e:
            self.logger.error(f"Failed to create Redis connection: {e}")
            raise
    
    async def _is_connection_healthy(self) -> bool:
        """Check if current connection is healthy"""
        try:
            await asyncio.to_thread(self.connection.ping)
            return True
        except Exception:
            return False
    
    async def get(self, key: str, fallback_value: Any = None) -> Any:
        """Get value with fallback"""
        try:
            conn = await self.get_connection()
            value = await asyncio.to_thread(conn.get, key)
            return value if value is not None else fallback_value
        except Exception as e:
            self.logger.error(f"Redis GET failed for key {key}: {e}")
            return fallback_value
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value with TTL and fallback"""
        try:
            conn = await self.get_connection()
            result = await asyncio.to_thread(conn.setex, key, ttl, value)
            return result
        except Exception as e:
            self.logger.error(f"Redis SET failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key with fallback"""
        try:
            conn = await self.get_connection()
            result = await asyncio.to_thread(conn.delete, key)
            return result
        except Exception as e:
            self.logger.error(f"Redis DELETE failed for key {key}: {e}")
            return False

class LocalRedisFallback:
    """Local file-based fallback for Redis operations"""
    
    def __init__(self, fallback_dir: str = "/tmp/redis_fallback"):
        self.fallback_dir = Path(fallback_dir)
        self.fallback_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("LocalRedisFallback")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from local fallback"""
        file_path = self.fallback_dir / f"{key}.json"
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Check TTL
                    if time.time() < data.get('expires_at', float('inf')):
                        return data['value']
                    else:
                        file_path.unlink()  # Expired
            except Exception as e:
                self.logger.error(f"Failed to read fallback for key {key}: {e}")
        return None
    
    def setex(self, key: str, ttl: int, value: Any) -> bool:
        """Set value with TTL in local fallback"""
        try:
            file_path = self.fallback_dir / f"{key}.json"
            data = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
            with open(file_path, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            self.logger.error(f"Failed to write fallback for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from local fallback"""
        try:
            file_path = self.fallback_dir / f"{key}.json"
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete fallback for key {key}: {e}")
            return False
```

#### 3. Service Health Monitoring
```python
# Comprehensive service health monitoring
import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    name: str
    check_function: callable
    timeout: int = 30
    interval: int = 60
    failure_threshold: int = 3
    warning_threshold: int = 2

class ServiceHealthMonitor:
    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_status: Dict[str, Dict[str, Any]] = {}
        self.alert_callbacks: List[callable] = []
        self.logger = logging.getLogger("ServiceHealthMonitor")
    
    def add_health_check(self, name: str, check_function: callable, **kwargs):
        """Add a new health check"""
        self.health_checks[name] = HealthCheck(name=name, check_function=check_function, **kwargs)
        self.health_status[name] = {
            'status': ServiceStatus.UNKNOWN,
            'last_check': 0,
            'failure_count': 0,
            'success_count': 0,
            'last_error': None,
            'response_time': 0
        }
    
    def add_alert_callback(self, callback: callable):
        """Add alert callback for health status changes"""
        self.alert_callbacks.append(callback)
    
    async def start_monitoring(self):
        """Start health monitoring loop"""
        self.logger.info("Starting service health monitoring")
        
        while True:
            await self._perform_health_checks()
            await asyncio.sleep(10)  # Check every 10 seconds
    
    async def _perform_health_checks(self):
        """Perform all health checks"""
        current_time = time.time()
        
        for name, check in self.health_checks.items():
            try:
                # Perform health check with timeout
                start_time = time.time()
                result = await asyncio.wait_for(
                    check.check_function(),
                    timeout=check.timeout
                )
                response_time = time.time() - start_time
                
                # Update status
                self._update_health_status(name, True, response_time, None)
                
            except Exception as e:
                response_time = time.time() - start_time
                self._update_health_status(name, False, response_time, str(e))
    
    def _update_health_status(self, name: str, success: bool, response_time: float, error: Optional[str]):
        """Update health status for a service"""
        status_info = self.health_status[name]
        
        if success:
            status_info['success_count'] += 1
            status_info['failure_count'] = 0
            status_info['last_error'] = None
            new_status = ServiceStatus.HEALTHY
        else:
            status_info['failure_count'] += 1
            status_info['success_count'] = 0
            status_info['last_error'] = error
            
            if status_info['failure_count'] >= self.health_checks[name].failure_threshold:
                new_status = ServiceStatus.UNHEALTHY
            elif status_info['failure_count'] >= self.health_checks[name].warning_threshold:
                new_status = ServiceStatus.DEGRADED
            else:
                new_status = ServiceStatus.DEGRADED
        
        # Check for status change
        old_status = status_info['status']
        if old_status != new_status:
            self.logger.warning(f"Service {name} status changed: {old_status.value} -> {new_status.value}")
            self._trigger_alerts(name, old_status, new_status, error)
        
        # Update status info
        status_info.update({
            'status': new_status,
            'last_check': time.time(),
            'response_time': response_time
        })
    
    def _trigger_alerts(self, name: str, old_status: ServiceStatus, new_status: ServiceStatus, error: Optional[str]):
        """Trigger alerts for status changes"""
        alert_data = {
            'service': name,
            'old_status': old_status.value,
            'new_status': new_status.value,
            'error': error,
            'timestamp': time.time(),
            'severity': self._calculate_severity(new_status)
        }
        
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
    
    def _calculate_severity(self, status: ServiceStatus) -> str:
        """Calculate alert severity based on status"""
        if status == ServiceStatus.UNHEALTHY:
            return "critical"
        elif status == ServiceStatus.DEGRADED:
            return "warning"
        else:
            return "info"
    
    def get_overall_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        critical_services = []
        degraded_services = []
        healthy_services = []
        
        for name, status_info in self.health_status.items():
            status = status_info['status']
            if status == ServiceStatus.UNHEALTHY:
                critical_services.append(name)
            elif status == ServiceStatus.DEGRADED:
                degraded_services.append(name)
            else:
                healthy_services.append(name)
        
        overall_status = ServiceStatus.HEALTHY
        if critical_services:
            overall_status = ServiceStatus.UNHEALTHY
        elif degraded_services:
            overall_status = ServiceStatus.DEGRADED
        
        return {
            'overall_status': overall_status.value,
            'healthy_services': healthy_services,
            'degraded_services': degraded_services,
            'critical_services': critical_services,
            'total_services': len(self.health_status),
            'timestamp': time.time()
        }
    
    def get_service_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get status for specific service"""
        return self.health_status.get(name)

# Example health check functions
async def check_redis_health():
    """Check Redis connection health"""
    from app.XNAi_rag_app.services.redis.resilient_manager import get_redis_manager
    
    redis_manager = get_redis_manager()
    conn = await redis_manager.get_connection()
    await asyncio.to_thread(conn.ping)
    return True

async def check_vikunja_health():
    """Check Vikunja API health"""
    import requests
    import os
    
    vikunja_url = os.getenv('VIKUNJA_URL', 'http://localhost:3456')
    api_token = os.getenv('VIKUNJA_API_TOKEN')
    
    if not api_token:
        raise Exception("VIKUNJA_API_TOKEN not configured")
    
    headers = {'Authorization': f'Bearer {api_token}'}
    response = requests.get(f"{vikunja_url}/api/v1/tasks", headers=headers, timeout=10)
    response.raise_for_status()
    return True

async def check_prometheus_health():
    """Check Prometheus health"""
    import requests
    
    prometheus_url = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')
    response = requests.get(f"{prometheus_url}/api/v1/status/config", timeout=10)
    response.raise_for_status()
    return True
```

### Integration Points

#### Error Recovery Patterns
- **Circuit Breaker**: Automatic failure detection and recovery
- **Retry Logic**: Exponential backoff with jitter
- **Fallback Mechanisms**: Graceful degradation when services fail
- **Caching**: Local caching to reduce external dependencies

#### Service Discovery
- **Health Check Endpoints**: Standardized health check endpoints
- **Service Registry**: Dynamic service discovery and registration
- **Load Balancing**: Intelligent load distribution
- **Failover**: Automatic failover to backup services

#### Monitoring Integration
- **Prometheus Metrics**: Custom metrics for service health
- **Grafana Dashboards**: Visual monitoring of service status
- **Alert Manager**: Automated alerting and notification
- **Log Aggregation**: Centralized logging for troubleshooting

## Implementation Steps

### Phase 1: Circuit Breaker Implementation (Week 1)

#### Step 1.1: Core Circuit Breaker Library
```bash
# Create core circuit breaker library
cat > app/XNAi_rag_app/services/circuit_breaker.py << 'EOF'
"""
Circuit Breaker Service
Provides circuit breaker patterns for service resilience
"""

import asyncio
import time
import logging
from typing import Any, Callable, Optional, Tuple, Type
from dataclasses import dataclass
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: Tuple[Type[Exception], ...] = (Exception,)
    timeout: int = 30
    name: str = "default"
    half_open_max_calls: int = 3

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.success_count = 0
        self.logger = logging.getLogger(f"CircuitBreaker.{config.name}")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                self.logger.info(f"Circuit breaker {self.config.name} transitioning to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise Exception(f"Circuit breaker {self.config.name} is OPEN")
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            self._on_success()
            return result
            
        except self.config.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful execution"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.half_open_max_calls:
                self.logger.info(f"Circuit breaker {self.config.name} transitioning to CLOSED")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        self.logger.warning(
            f"Circuit breaker {self.config.name} failure {self.failure_count}/{self.config.failure_threshold}"
        )
        
        if self.failure_count >= self.config.failure_threshold:
            self.logger.error(f"Circuit breaker {self.config.name} OPENING")
            self.state = CircuitState.OPEN

def circuit_breaker(config: CircuitBreakerConfig):
    """Decorator for applying circuit breaker to functions"""
    breaker = CircuitBreaker(config)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator

# Pre-configured circuit breakers for common services
redis_circuit_breaker = circuit_breaker(CircuitBreakerConfig(
    name="redis",
    failure_threshold=3,
    recovery_timeout=30,
    expected_exception=(ConnectionError, TimeoutError),
    timeout=10
))

vikunja_circuit_breaker = circuit_breaker(CircuitBreakerConfig(
    name="vikunja",
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=(requests.exceptions.RequestException,),
    timeout=30
))

prometheus_circuit_breaker = circuit_breaker(CircuitBreakerConfig(
    name="prometheus",
    failure_threshold=3,
    recovery_timeout=30,
    expected_exception=(requests.exceptions.RequestException,),
    timeout=15
))
EOF
```

#### Step 1.2: Service Integration
```bash
# Integrate circuit breakers with existing services
cat > app/XNAi_rag_app/services/service_resilience.py << 'EOF'
"""
Service Resilience Layer
Integrates circuit breakers with existing services
"""

import asyncio
import logging
from typing import Any, Dict, Optional
from .circuit_breaker import (
    circuit_breaker, CircuitBreakerConfig,
    redis_circuit_breaker, vikunja_circuit_breaker
)

logger = logging.getLogger(__name__)

class ServiceResilience:
    """Service resilience wrapper for existing services"""
    
    def __init__(self):
        self.redis_config = CircuitBreakerConfig(
            name="redis",
            failure_threshold=3,
            recovery_timeout=30,
            expected_exception=(ConnectionError, TimeoutError),
            timeout=10
        )
        self.vikunja_config = CircuitBreakerConfig(
            name="vikunja",
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=(Exception,),
            timeout=30
        )
    
    @redis_circuit_breaker
    async def resilient_redis_get(self, key: str, fallback_value: Any = None) -> Any:
        """Redis GET with circuit breaker protection"""
        from app.XNAi_rag_app.services.redis.resilient_manager import get_redis_manager
        
        redis_manager = get_redis_manager()
        return await redis_manager.get(key, fallback_value)
    
    @redis_circuit_breaker
    async def resilient_redis_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Redis SET with circuit breaker protection"""
        from app.XNAi_rag_app.services.redis.resilient_manager import get_redis_manager
        
        redis_manager = get_redis_manager()
        return await redis_manager.set(key, value, ttl)
    
    @vikunja_circuit_breaker
    async def resilient_vikunja_api_call(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Any:
        """Vikunja API call with circuit breaker protection"""
        import requests
        import os
        
        vikunja_url = os.getenv('VIKUNJA_URL', 'http://localhost:3456')
        api_token = os.getenv('VIKUNJA_API_TOKEN')
        
        if not api_token:
            raise ValueError("VIKUNJA_API_TOKEN not configured")
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{vikunja_url}{endpoint}"
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=30)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()

# Usage example
async def example_usage():
    resilience = ServiceResilience()
    
    try:
        # Redis operations with circuit breaker
        value = await resilience.resilient_redis_get("test_key", "default_value")
        await resilience.resilient_redis_set("test_key", "new_value", ttl=3600)
        
        # Vikunja API calls with circuit breaker
        tasks = await resilience.resilient_vikunja_api_call("/api/v1/tasks")
        print(f"Retrieved {len(tasks)} tasks")
        
    except Exception as e:
        logger.error(f"Service call failed: {e}")
        # Circuit breaker will handle the failure and provide fallback
EOF
```

### Phase 2: Redis Resilience Implementation (Week 2)

#### Step 2.1: Enhanced Redis Manager
```bash
# Create enhanced Redis manager with comprehensive resilience
cat > app/XNAi_rag_app/services/redis/resilient_manager.py << 'EOF'
"""
Resilient Redis Manager
Provides comprehensive Redis resilience with fallback mechanisms
"""

import redis
import time
import json
import logging
import asyncio
from pathlib import Path
from typing import Any, Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RedisConnectionState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    FALLBACK = "fallback"

@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    socket_connect_timeout: int = 5
    socket_timeout: int = 5
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    max_retries: int = 3
    fallback_enabled: bool = True
    fallback_dir: str = "/tmp/redis_fallback"

class LocalRedisFallback:
    """Local file-based fallback for Redis operations"""
    
    def __init__(self, fallback_dir: str = "/tmp/redis_fallback"):
        self.fallback_dir = Path(fallback_dir)
        self.fallback_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("LocalRedisFallback")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from local fallback"""
        file_path = self.fallback_dir / f"{key}.json"
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Check TTL
                    if time.time() < data.get('expires_at', float('inf')):
                        return data['value']
                    else:
                        file_path.unlink()  # Expired
            except Exception as e:
                self.logger.error(f"Failed to read fallback for key {key}: {e}")
        return None
    
    async def setex(self, key: str, ttl: int, value: Any) -> bool:
        """Set value with TTL in local fallback"""
        try:
            file_path = self.fallback_dir / f"{key}.json"
            data = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
            with open(file_path, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            self.logger.error(f"Failed to write fallback for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from local fallback"""
        try:
            file_path = self.fallback_dir / f"{key}.json"
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete fallback for key {key}: {e}")
            return False

class ResilientRedisManager:
    def __init__(self, config: RedisConfig):
        self.config = config
        self.connection = None
        self.state = RedisConnectionState.HEALTHY
        self.last_health_check = 0
        self.connection_attempts = 0
        self.fallback_storage = LocalRedisFallback(config.fallback_dir)
        self.logger = logging.getLogger("ResilientRedisManager")
    
    async def get_connection(self) -> redis.Redis:
        """Get Redis connection with resilience"""
        current_time = time.time()
        
        # Check if we need health check
        if current_time - self.last_health_check > self.config.health_check_interval:
            await self._perform_health_check()
        
        # Try to get connection
        if self.state in [RedisConnectionState.HEALTHY, RedisConnectionState.DEGRADED]:
            try:
                if not self.connection or not await self._is_connection_healthy():
                    self.connection = await self._create_connection()
                    self.state = RedisConnectionState.HEALTHY
                    self.connection_attempts = 0
                return self.connection
            except Exception as e:
                self.logger.error(f"Redis connection failed: {e}")
                self.state = RedisConnectionState.FAILED
                self.connection_attempts += 1
        
        # Use fallback if enabled
        if self.config.fallback_enabled:
            self.logger.warning("Using fallback storage due to Redis failure")
            return self.fallback_storage
        
        # No fallback available, raise error
        raise ConnectionError("Redis unavailable and no fallback configured")
    
    async def _perform_health_check(self):
        """Perform comprehensive health check"""
        try:
            if self.connection:
                # Test connection with ping
                await asyncio.to_thread(self.connection.ping)
                self.state = RedisConnectionState.HEALTHY
                self.connection_attempts = 0
            else:
                self.state = RedisConnectionState.FAILED
        except Exception as e:
            self.logger.warning(f"Redis health check failed: {e}")
            if self.connection_attempts > self.config.max_retries:
                self.state = RedisConnectionState.FAILED
            else:
                self.state = RedisConnectionState.DEGRADED
        finally:
            self.last_health_check = time.time()
    
    async def _create_connection(self) -> redis.Redis:
        """Create new Redis connection"""
        try:
            connection = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                socket_connect_timeout=self.config.socket_connect_timeout,
                socket_timeout=self.config.socket_timeout,
                retry_on_timeout=self.config.retry_on_timeout,
                health_check_interval=self.config.health_check_interval
            )
            # Test connection
            await asyncio.to_thread(connection.ping)
            self.logger.info("Redis connection established successfully")
            return connection
        except Exception as e:
            self.logger.error(f"Failed to create Redis connection: {e}")
            raise
    
    async def _is_connection_healthy(self) -> bool:
        """Check if current connection is healthy"""
        try:
            await asyncio.to_thread(self.connection.ping)
            return True
        except Exception:
            return False
    
    async def get(self, key: str, fallback_value: Any = None) -> Any:
        """Get value with fallback"""
        try:
            conn = await self.get_connection()
            if hasattr(conn, 'get'):
                # Redis connection
                value = await asyncio.to_thread(conn.get, key)
                return value if value is not None else fallback_value
            else:
                # Fallback storage
                return await conn.get(key)
        except Exception as e:
            self.logger.error(f"Redis GET failed for key {key}: {e}")
            return fallback_value
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value with TTL and fallback"""
        try:
            conn = await self.get_connection()
            if hasattr(conn, 'setex'):
                # Redis connection
                result = await asyncio.to_thread(conn.setex, key, ttl, value)
                return result
            else:
                # Fallback storage
                return await conn.setex(key, ttl, value)
        except Exception as e:
            self.logger.error(f"Redis SET failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key with fallback"""
        try:
            conn = await self.get_connection()
            if hasattr(conn, 'delete'):
                # Redis connection
                result = await asyncio.to_thread(conn.delete, key)
                return result
            else:
                # Fallback storage
                return await conn.delete(key)
        except Exception as e:
            self.logger.error(f"Redis DELETE failed for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            conn = await self.get_connection()
            if hasattr(conn, 'exists'):
                # Redis connection
                result = await asyncio.to_thread(conn.exists, key)
                return bool(result)
            else:
                # Fallback storage
                file_path = Path(self.config.fallback_dir) / f"{key}.json"
                return file_path.exists()
        except Exception as e:
            self.logger.error(f"Redis EXISTS failed for key {key}: {e}")
            return False
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern"""
        try:
            conn = await self.get_connection()
            if hasattr(conn, 'keys'):
                # Redis connection
                result = await asyncio.to_thread(conn.keys, pattern)
                return [key.decode() if isinstance(key, bytes) else key for key in result]
            else:
                # Fallback storage
                import glob
                pattern_path = Path(self.config.fallback_dir) / f"{pattern}.json"
                files = glob.glob(str(pattern_path))
                return [Path(f).stem for f in files]
        except Exception as e:
            self.logger.error(f"Redis KEYS failed for pattern {pattern}: {e}")
            return []
    
    async def flush_fallback(self):
        """Flush fallback storage"""
        try:
            import shutil
            shutil.rmtree(self.config.fallback_dir)
            Path(self.config.fallback_dir).mkdir(parents=True, exist_ok=True)
            self.logger.info("Fallback storage flushed")
        except Exception as e:
            self.logger.error(f"Failed to flush fallback storage: {e}")

# Global instance
_redis_manager = None

def get_redis_manager() -> ResilientRedisManager:
    """Get global Redis manager instance"""
    global _redis_manager
    if _redis_manager is None:
        from app.XNAi_rag_app.config import get_config
        config = get_config()
        redis_config = RedisConfig(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_db,
            fallback_enabled=True
        )
        _redis_manager = ResilientRedisManager(redis_config)
    return _redis_manager
EOF
```

### Phase 3: Service Health Monitoring (Week 3)

#### Step 3.1: Health Monitoring Service
```bash
# Create comprehensive health monitoring service
cat > app/XNAi_rag_app/services/health_monitor.py << 'EOF'
"""
Service Health Monitor
Comprehensive health monitoring for all services
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    name: str
    check_function: Callable
    timeout: int = 30
    interval: int = 60
    failure_threshold: int = 3
    warning_threshold: int = 2

class ServiceHealthMonitor:
    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_status: Dict[str, Dict[str, Any]] = {}
        self.alert_callbacks: List[Callable] = []
        self.monitoring_task = None
        self.logger = logging.getLogger("ServiceHealthMonitor")
    
    def add_health_check(self, name: str, check_function: Callable, **kwargs):
        """Add a new health check"""
        self.health_checks[name] = HealthCheck(name=name, check_function=check_function, **kwargs)
        self.health_status[name] = {
            'status': ServiceStatus.UNKNOWN,
            'last_check': 0,
            'failure_count': 0,
            'success_count': 0,
            'last_error': None,
            'response_time': 0
        }
    
    def add_alert_callback(self, callback: Callable):
        """Add alert callback for health status changes"""
        self.alert_callbacks.append(callback)
    
    async def start_monitoring(self):
        """Start health monitoring loop"""
        if self.monitoring_task is not None:
            self.logger.warning("Health monitoring already started")
            return
        
        self.logger.info("Starting service health monitoring")
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        if self.monitoring_task is not None:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
            self.logger.info("Health monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(10)  # Check every 10 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def _perform_health_checks(self):
        """Perform all health checks"""
        current_time = time.time()
        
        for name, check in self.health_checks.items():
            try:
                # Perform health check with timeout
                start_time = time.time()
                result = await asyncio.wait_for(
                    check.check_function(),
                    timeout=check.timeout
                )
                response_time = time.time() - start_time
                
                # Update status
                self._update_health_status(name, True, response_time, None)
                
            except Exception as e:
                response_time = time.time() - start_time
                self._update_health_status(name, False, response_time, str(e))
    
    def _update_health_status(self, name: str, success: bool, response_time: float, error: Optional[str]):
        """Update health status for a service"""
        status_info = self.health_status[name]
        
        if success:
            status_info['success_count'] += 1
            status_info['failure_count'] = 0
            status_info['last_error'] = None
            new_status = ServiceStatus.HEALTHY
        else:
            status_info['failure_count'] += 1
            status_info['success_count'] = 0
            status_info['last_error'] = error
            
            if status_info['failure_count'] >= self.health_checks[name].failure_threshold:
                new_status = ServiceStatus.UNHEALTHY
            elif status_info['failure_count'] >= self.health_checks[name].warning_threshold:
                new_status = ServiceStatus.DEGRADED
            else:
                new_status = ServiceStatus.DEGRADED
        
        # Check for status change
        old_status = status_info['status']
        if old_status != new_status:
            self.logger.warning(f"Service {name} status changed: {old_status.value} -> {new_status.value}")
            self._trigger_alerts(name, old_status, new_status, error)
        
        # Update status info
        status_info.update({
            'status': new_status,
            'last_check': time.time(),
            'response_time': response_time
        })
    
    def _trigger_alerts(self, name: str, old_status: ServiceStatus, new_status: ServiceStatus, error: Optional[str]):
        """Trigger alerts for status changes"""
        alert_data = {
            'service': name,
            'old_status': old_status.value,
            'new_status': new_status.value,
            'error': error,
            'timestamp': time.time(),
            'severity': self._calculate_severity(new_status)
        }
        
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
    
    def _calculate_severity(self, status: ServiceStatus) -> str:
        """Calculate alert severity based on status"""
        if status == ServiceStatus.UNHEALTHY:
            return "critical"
        elif status == ServiceStatus.DEGRADED:
            return "warning"
        else:
            return "info"
    
    def get_overall_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        critical_services = []
        degraded_services = []
        healthy_services = []
        
        for name, status_info in self.health_status.items():
            status = status_info['status']
            if status == ServiceStatus.UNHEALTHY:
                critical_services.append(name)
            elif status == ServiceStatus.DEGRADED:
                degraded_services.append(name)
            else:
                healthy_services.append(name)
        
        overall_status = ServiceStatus.HEALTHY
        if critical_services:
            overall_status = ServiceStatus.UNHEALTHY
        elif degraded_services:
            overall_status = ServiceStatus.DEGRADED
        
        return {
            'overall_status': overall_status.value,
            'healthy_services': healthy_services,
            'degraded_services': degraded_services,
            'critical_services': critical_services,
            'total_services': len(self.health_status),
            'timestamp': time.time()
        }
    
    def get_service_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get status for specific service"""
        return self.health_status.get(name)
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        return {
            'timestamp': time.time(),
            'overall_status': self.get_overall_status(),
            'services': self.health_status,
            'monitoring_active': self.monitoring_task is not None
        }

# Example health check functions
async def check_redis_health():
    """Check Redis connection health"""
    from app.XNAi_rag_app.services.redis.resilient_manager import get_redis_manager
    
    redis_manager = get_redis_manager()
    try:
        conn = await redis_manager.get_connection()
        if hasattr(conn, 'ping'):
            await asyncio.to_thread(conn.ping)
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        raise

async def check_vikunja_health():
    """Check Vikunja API health"""
    import requests
    import os
    
    vikunja_url = os.getenv('VIKUNJA_URL', 'http://localhost:3456')
    api_token = os.getenv('VIKUNJA_API_TOKEN')
    
    if not api_token:
        raise Exception("VIKUNJA_API_TOKEN not configured")
    
    headers = {'Authorization': f'Bearer {api_token}'}
    response = requests.get(f"{vikunja_url}/api/v1/tasks", headers=headers, timeout=10)
    response.raise_for_status()
    return True

async def check_prometheus_health():
    """Check Prometheus health"""
    import requests
    
    prometheus_url = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')
    response = requests.get(f"{prometheus_url}/api/v1/status/config", timeout=10)
    response.raise_for_status()
    return True

async def check_disk_space():
    """Check disk space health"""
    import shutil
    
    total, used, free = shutil.disk_usage("/")
    free_percent = (free / total) * 100
    
    if free_percent < 10:
        raise Exception(f"Disk space critically low: {free_percent:.1f}% free")
    elif free_percent < 20:
        raise Exception(f"Disk space low: {free_percent:.1f}% free")
    
    return True

# Global health monitor instance
_health_monitor = None

def get_health_monitor() -> ServiceHealthMonitor:
    """Get global health monitor instance"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = ServiceHealthMonitor()
        
        # Add default health checks
        _health_monitor.add_health_check("redis", check_redis_health, interval=30)
        _health_monitor.add_health_check("vikunja", check_vikunja_health, interval=60)
        _health_monitor.add_health_check("prometheus", check_prometheus_health, interval=60)
        _health_monitor.add_health_check("disk_space", check_disk_space, interval=300)
    
    return _health_monitor
EOF
```

## Test Plan

### Unit Tests
```bash
# Create test suite for service stability
cat > tests/test_service_stability.py << 'EOF'
#!/usr/bin/env python3
"""
Test suite for service stability system
"""

import pytest
import asyncio
import time
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from app.XNAi_rag_app.services.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from app.XNAi_rag_app.services.redis.resilient_manager import ResilientRedisManager, RedisConfig
from app.XNAi_rag_app.services.health_monitor import ServiceHealthMonitor

class TestCircuitBreaker:
    def setup_method(self):
        self.config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1,
            timeout=1,
            name="test"
        )
        self.breaker = CircuitBreaker(self.config)
    
    @pytest.mark.asyncio
    async def test_successful_calls(self):
        """Test successful calls keep circuit closed"""
        async def success_func():
            return "success"
        
        for _ in range(5):
            result = await self.breaker.call(success_func)
            assert result == "success"
            assert self.breaker.state == "closed"
            assert self.breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_failure_threshold(self):
        """Test circuit opens after failure threshold"""
        async def failure_func():
            raise Exception("test failure")
        
        # Fail 3 times (threshold is 3)
        for i in range(3):
            with pytest.raises(Exception):
                await self.breaker.call(failure_func)
            assert self.breaker.failure_count == i + 1
        
        # Circuit should be open
        assert self.breaker.state == "open"
        
        # Next call should fail immediately
        with pytest.raises(Exception, match="Circuit breaker test is OPEN"):
            await self.breaker.call(failure_func)
    
    @pytest.mark.asyncio
    async def test_recovery_timeout(self):
        """Test circuit recovers after timeout"""
        async def failure_func():
            raise Exception("test failure")
        
        # Fail to open circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await self.breaker.call(failure_func)
        
        assert self.breaker.state == "open"
        
        # Wait for recovery timeout
        await asyncio.sleep(1.1)
        
        # Circuit should be half-open
        async def success_func():
            return "success"
        
        result = await self.breaker.call(success_func)
        assert result == "success"
        assert self.breaker.state == "closed"

class TestResilientRedisManager:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = RedisConfig(
            host="localhost",
            port=6379,
            fallback_dir=self.temp_dir,
            fallback_enabled=True
        )
        self.manager = ResilientRedisManager(self.config)
    
    @pytest.mark.asyncio
    async def test_fallback_storage(self):
        """Test fallback storage functionality"""
        # Test set and get with fallback
        result = await self.manager.fallback_storage.setex("test_key", 3600, "test_value")
        assert result == True
        
        value = await self.manager.fallback_storage.get("test_key")
        assert value == "test_value"
    
    @pytest.mark.asyncio
    async def test_fallback_expiration(self):
        """Test fallback storage expiration"""
        # Set value with short TTL
        await self.manager.fallback_storage.setex("test_key", 1, "test_value")
        
        # Should be available immediately
        value = await self.manager.fallback_storage.get("test_key")
        assert value == "test_value"
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Should be expired
        value = await self.manager.fallback_storage.get("test_key")
        assert value is None

class TestServiceHealthMonitor:
    def setup_method(self):
        self.monitor = ServiceHealthMonitor()
    
    def test_add_health_check(self):
        """Test adding health checks"""
        async def test_check():
            return True
        
        self.monitor.add_health_check("test_service", test_check, interval=30)
        
        assert "test_service" in self.monitor.health_checks
        assert "test_service" in self.monitor.health_status
        
        status_info = self.monitor.health_status["test_service"]
        assert status_info['status'] == "unknown"
        assert status_info['failure_count'] == 0
        assert status_info['success_count'] == 0
    
    def test_overall_status(self):
        """Test overall status calculation"""
        # Initially unknown
        status = self.monitor.get_overall_status()
        assert status['overall_status'] == "unknown"
        
        # Add some services
        self.monitor.health_status['service1'] = {'status': "healthy"}
        self.monitor.health_status['service2'] = {'status': "degraded"}
        self.monitor.health_status['service3'] = {'status': "unhealthy"}
        
        status = self.monitor.get_overall_status()
        assert status['overall_status'] == "unhealthy"
        assert "service1" in status['healthy_services']
        assert "service2" in status['degraded_services']
        assert "service3" in status['critical_services']

if __name__ == '__main__':
    pytest.main([__file__])
EOF
```

### Integration Tests
```bash
# Create integration test script
cat > scripts/test-service-stability-integration.py << 'EOF'
#!/usr/bin/env python3
"""
Integration test for service stability system
"""

import asyncio
import time
import json
from pathlib import Path
from app.XNAi_rag_app.services.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from app.XNAi_rag_app.services.redis.resilient_manager import ResilientRedisManager, RedisConfig
from app.XNAi_rag_app.services.health_monitor import ServiceHealthMonitor

async def test_circuit_breaker_integration():
    """Test circuit breaker integration"""
    print("Testing circuit breaker integration...")
    
    config = CircuitBreakerConfig(
        failure_threshold=2,
        recovery_timeout=2,
        timeout=1,
        name="integration_test"
    )
    breaker = CircuitBreaker(config)
    
    # Test successful calls
    async def success_func():
        return "success"
    
    result = await breaker.call(success_func)
    assert result == "success"
    print("✅ Circuit breaker handles successful calls")
    
    # Test failure threshold
    async def failure_func():
        raise Exception("test failure")
    
    try:
        await breaker.call(failure_func)
    except Exception:
        pass
    
    try:
        await breaker.call(failure_func)
    except Exception:
        pass
    
    assert breaker.state == "open"
    print("✅ Circuit breaker opens after threshold")
    
    # Test recovery
    await asyncio.sleep(2.1)
    
    result = await breaker.call(success_func)
    assert result == "success"
    assert breaker.state == "closed"
    print("✅ Circuit breaker recovers after timeout")

async def test_redis_resilience_integration():
    """Test Redis resilience integration"""
    print("Testing Redis resilience integration...")
    
    temp_dir = "/tmp/test_redis_fallback"
    config = RedisConfig(
        host="nonexistent-redis-server",
        port=6379,
        fallback_dir=temp_dir,
        fallback_enabled=True
    )
    manager = ResilientRedisManager(config)
    
    # Test fallback storage
    result = await manager.set("test_key", "test_value", ttl=3600)
    assert result == True
    print("✅ Redis fallback storage works")
    
    value = await manager.get("test_key")
    assert value == "test_value"
    print("✅ Redis fallback retrieval works")
    
    exists = await manager.exists("test_key")
    assert exists == True
    print("✅ Redis fallback exists check works")

async def test_health_monitor_integration():
    """Test health monitor integration"""
    print("Testing health monitor integration...")
    
    monitor = ServiceHealthMonitor()
    
    # Add test health check
    async def test_health_check():
        return True
    
    monitor.add_health_check("test_service", test_health_check, interval=10)
    
    # Test status
    status = monitor.get_service_status("test_service")
    assert status is not None
    assert status['status'] == "unknown"
    print("✅ Health monitor tracks service status")
    
    # Test overall status
    overall = monitor.get_overall_status()
    assert overall['total_services'] == 1
    print("✅ Health monitor calculates overall status")

async def main():
    """Main integration test"""
    print("Running service stability integration tests...")
    
    await test_circuit_breaker_integration()
    await test_redis_resilience_integration()
    await test_health_monitor_integration()
    
    print("🎉 All integration tests passed!")

if __name__ == '__main__':
    asyncio.run(main())
EOF
chmod +x scripts/test-service-stability-integration.py
```

## Risks & Mitigations

### Risk 1: Circuit Breaker False Positives
**Impact**: Circuit breakers may open unnecessarily, blocking legitimate requests
**Mitigation**:
- Tune failure thresholds based on service characteristics
- Implement adaptive thresholds that learn from historical patterns
- Use multiple failure indicators before opening
- Provide manual override capabilities

### Risk 2: Fallback Storage Corruption
**Impact**: Local fallback storage may become corrupted, leading to data loss
**Mitigation**:
- Implement checksums for fallback data
- Regular backup and validation of fallback storage
- Automatic cleanup of corrupted fallback files
- Monitor fallback storage health

### Risk 3: Health Check Overhead
**Impact**: Frequent health checks may add overhead to services
**Mitigation**:
- Optimize health check intervals based on service criticality
- Use lightweight health check methods
- Implement caching for expensive health checks
- Monitor health check performance

### Risk 4: Alert Fatigue
**Impact**: Too many alerts may cause important alerts to be ignored
**Mitigation**:
- Implement alert deduplication and aggregation
- Use severity-based alert routing
- Provide alert suppression during maintenance
- Implement alert escalation policies

## Ma'at Alignment Validation

### Principle #18: Balance (Service Equilibrium)
**Alignment**: This charter ensures balanced service operation by:
- Distributing load across healthy services
- Implementing graceful degradation during failures
- Maintaining equilibrium between performance and reliability
- Ensuring no single service becomes a bottleneck

**Validation Criteria**:
- [ ] Services maintain functionality during partial failures
- [ ] Load distribution prevents service overload
- [ ] Performance balanced with reliability requirements
- [ ] No single point of service failure exists

### Principle #7: Truth (System Integrity)
**Alignment**: This charter ensures truthful system operation by:
- Providing accurate health status reporting
- Implementing comprehensive error detection
- Maintaining complete audit trails for failures
- Ensuring transparent failure recovery

**Validation Criteria**:
- [ ] Health status accurately reflects service state
- [ ] All failures are detected and logged
- [ ] Complete audit trail maintained for all incidents
- [ ] Failure recovery is transparent and verifiable

## Implementation Timeline

### Week 1: Circuit Breaker Implementation
- [ ] Create core circuit breaker library
- [ ] Integrate circuit breakers with existing services
- [ ] Implement service-specific circuit breaker configurations
- [ ] Test circuit breaker functionality

### Week 2: Redis Resilience Implementation
- [ ] Create enhanced Redis manager with fallback
- [ ] Implement local fallback storage mechanisms
- [ ] Add Redis health monitoring and recovery
- [ ] Test Redis resilience under failure conditions

### Week 3: Service Health Monitoring
- [ ] Create comprehensive health monitoring service
- [ ] Implement service-specific health checks
- [ ] Add alerting and notification systems
- [ ] Create health dashboards and reporting

### Week 4: Validation & Optimization
- [ ] Comprehensive testing and validation
- [ ] Performance optimization for monitoring overhead
- [ ] Security hardening for health check endpoints
- [ ] Documentation and training materials

## Success Metrics

### Technical Metrics
- [ ] Service availability: 99.9%
- [ ] Recovery time: <5 seconds
- [ ] Circuit breaker accuracy: >95%
- [ ] Health check overhead: <1% of service capacity

### Business Metrics
- [ ] Zero single points of failure
- [ ] Complete error handling coverage
- [ ] Graceful degradation for all critical services
- [ ] Automated recovery for common failure scenarios

### Operational Metrics
- [ ] Mean time to detection: <30 seconds
- [ ] Mean time to recovery: <5 minutes
- [ ] Alert accuracy: >90%
- [ ] False positive rate: <5%

## Next Steps

1. **Immediate**: Begin circuit breaker implementation
2. **Week 1**: Complete circuit breaker library and integration
3. **Week 2**: Implement Redis resilience with fallback mechanisms
4. **Week 3**: Deploy comprehensive health monitoring system
5. **Week 4**: Final validation and optimization

**Status**: Ready for implementation
**Priority**: P0 - CRITICAL
**Dependencies**: Service configuration, monitoring infrastructure
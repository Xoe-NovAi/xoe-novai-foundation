"""
Health Checker for Xoe-NovAi Foundation Stack
Provides comprehensive health monitoring for all services with automated recovery.
"""

import asyncio
import anyio
import json
import logging
import time
from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum
from contextlib import asynccontextmanager

import aiohttp
import redis.asyncio as redis
from aiohttp import ClientTimeout

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Health check result data structure"""

    service_name: str
    status: HealthStatus
    response_time: float
    details: Dict[str, Any]
    timestamp: float
    error_message: Optional[str] = None


@dataclass
class ServiceHealth:
    """Service health state"""

    name: str
    status: HealthStatus
    last_check: float
    response_time: float
    consecutive_failures: int
    consecutive_successes: int
    total_checks: int
    details: Dict[str, Any]


class HealthChecker:
    """Base health checker class"""

    def __init__(self, service_name: str, timeout: float = 30.0):
        self.service_name = service_name
        self.timeout = timeout
        self._last_result: Optional[HealthCheckResult] = None

    async def check(self) -> HealthCheckResult:
        """Perform health check"""
        start_time = time.time()
        try:
            # Enforce timeout at the base class level
            result = await asyncio.wait_for(self._perform_check(), timeout=self.timeout)
            response_time = time.time() - start_time

            return HealthCheckResult(
                service_name=self.service_name,
                status=HealthStatus.HEALTHY,
                response_time=response_time,
                details=result,
                timestamp=time.time(),
            )
        except Exception as e:
            response_time = time.time() - start_time

            # Identify if it was a timeout
            msg = str(e)
            if isinstance(e, (asyncio.TimeoutError, TimeoutError)):
                msg = f"Health check timeout after {self.timeout}s"

            return HealthCheckResult(
                service_name=self.service_name,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                details={},
                timestamp=time.time(),
                error_message=msg,
            )

    async def _perform_check(self) -> Dict[str, Any]:
        """Abstract method to be implemented by subclasses"""
        raise NotImplementedError

    def get_last_result(self) -> Optional[HealthCheckResult]:
        """Get last health check result"""
        return self._last_result


class HTTPHealthChecker(HealthChecker):
    """HTTP endpoint health checker"""

    def __init__(
        self,
        service_name: str,
        url: str,
        expected_status: int = 200,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(service_name, timeout)
        self.url = url
        self.expected_status = expected_status
        self.headers = headers or {}

    async def _perform_check(self) -> Dict[str, Any]:
        """Perform HTTP health check"""
        timeout = ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(self.url, headers=self.headers) as response:
                if response.status != self.expected_status:
                    raise Exception(f"Unexpected status: {response.status}")

                try:
                    data = await response.json()
                except Exception:
                    data = {"status": "ok"}

                return {
                    "status_code": response.status,
                    "response_data": data,
                    "headers": dict(response.headers),
                }


class RedisHealthChecker(HealthChecker):
    """Redis health checker"""

    def __init__(
        self, service_name: str, redis_client: redis.Redis, timeout: float = 30.0
    ):
        super().__init__(service_name, timeout)
        self.redis_client = redis_client

    async def _perform_check(self) -> Dict[str, Any]:
        """Perform Redis health check"""
        # Test basic connectivity
        await self.redis_client.ping()

        # Get Redis info
        info = await self.redis_client.info()

        # Check memory usage
        memory_info = await self.redis_client.memory_usage("test_key", samples=1)

        return {
            "ping": "PONG",
            "redis_version": info.get("redis_version"),
            "used_memory_human": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "memory_usage": memory_info,
        }


class DatabaseHealthChecker(HealthChecker):
    """Database health checker (PostgreSQL)"""

    def __init__(
        self, service_name: str, connection_string: str, timeout: float = 30.0
    ):
        super().__init__(service_name, timeout)
        self.connection_string = connection_string

    async def _perform_check(self) -> Dict[str, Any]:
        """Perform database health check"""
        import asyncpg

        try:
            conn = await asyncpg.connect(self.connection_string, timeout=self.timeout)

            # Test basic query
            result = await conn.fetchval("SELECT 1")

            # Get database stats
            stats = await conn.fetchrow("""
                SELECT 
                    datname,
                    numbackends,
                    xact_commit,
                    xact_rollback,
                    blks_read,
                    blks_hit
                FROM pg_stat_database 
                WHERE datname = current_database()
            """)

            await conn.close()

            return {
                "connection_test": result,
                "database_stats": dict(stats) if stats else {},
                "status": "connected",
            }

        except Exception as e:
            raise Exception(f"Database connection failed: {e}")


class CustomHealthChecker(HealthChecker):
    """Custom health checker with user-defined check function"""

    def __init__(
        self,
        service_name: str,
        check_func: Callable[[], Dict[str, Any]],
        timeout: float = 30.0,
    ):
        super().__init__(service_name, timeout)
        self.check_func = check_func

    async def _perform_check(self) -> Dict[str, Any]:
        """Perform custom health check"""
        return await self.check_func()


class HealthMonitor:
    """Main health monitoring system"""

    def __init__(self, check_interval: float = 30.0):
        self.check_interval = check_interval
        self.checkers: Dict[str, HealthChecker] = {}
        self.health_states: Dict[str, ServiceHealth] = {}
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._recovery_callbacks: Dict[str, Callable] = {}
        self._health_callbacks: Dict[str, Callable] = {}

        logger.info(
            f"Health Monitor initialized with check interval: {check_interval}s"
        )

    def add_checker(self, checker: HealthChecker):
        """Add health checker"""
        self.checkers[checker.service_name] = checker
        self.health_states[checker.service_name] = ServiceHealth(
            name=checker.service_name,
            status=HealthStatus.UNKNOWN,
            last_check=0.0,
            response_time=0.0,
            consecutive_failures=0,
            consecutive_successes=0,
            total_checks=0,
            details={},
        )
        logger.info(f"Added health checker: {checker.service_name}")

    def add_recovery_callback(self, service_name: str, callback: Callable):
        """Add recovery callback for service"""
        self._recovery_callbacks[service_name] = callback
        logger.info(f"Added recovery callback for: {service_name}")

    def add_health_callback(self, service_name: str, callback: Callable):
        """Add health status callback for service"""
        self._health_callbacks[service_name] = callback
        logger.info(f"Added health callback for: {service_name}")

    async def start_monitoring(self):
        """Start health monitoring"""
        if self._monitoring:
            logger.warning("Health monitoring already started")
            return

        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Health monitoring started")

    async def stop_monitoring(self):
        """Stop health monitoring"""
        if not self._monitoring:
            logger.warning("Health monitoring not started")
            return

        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None

        logger.info("Health monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def _perform_health_checks(self):
        """Perform health checks for all services"""
        for service_name, checker in self.checkers.items():
            try:
                # Capture old status before check
                old_status = self.health_states[service_name].status

                result = await checker.check()
                checker._last_result = result

                # Update health state
                await self._update_health_state(service_name, result)

                # Check for state transitions using captured old status
                await self._handle_state_transition(service_name, old_status, result)

            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")

    async def _update_health_state(self, service_name: str, result: HealthCheckResult):
        """Update service health state"""
        state = self.health_states[service_name]

        state.last_check = result.timestamp
        state.response_time = result.response_time
        state.total_checks += 1
        state.details = result.details

        # Update status
        state.status = result.status

        if result.status == HealthStatus.HEALTHY:
            state.consecutive_successes += 1
            state.consecutive_failures = 0
        else:
            state.consecutive_failures += 1
            state.consecutive_successes = 0

    async def _handle_state_transition(
        self, service_name: str, old_status: HealthStatus, result: HealthCheckResult
    ):
        """Handle health state transitions"""
        new_status = result.status

        if old_status != new_status:
            logger.info(
                f"Service {service_name} status changed: {old_status.value} -> {new_status.value}"
            )

            # Call health callback
            if service_name in self._health_callbacks:
                try:
                    await self._health_callbacks[service_name](
                        service_name, old_status, new_status, result
                    )
                except Exception as e:
                    logger.error(f"Health callback failed for {service_name}: {e}")

            # Handle recovery
            if (
                old_status != HealthStatus.HEALTHY
                and new_status == HealthStatus.HEALTHY
            ):
                await self._handle_recovery(service_name)

    async def _handle_recovery(self, service_name: str):
        """Handle service recovery"""
        logger.info(f"Service {service_name} recovered")

        if service_name in self._recovery_callbacks:
            try:
                await self._recovery_callbacks[service_name](service_name)
            except Exception as e:
                logger.error(f"Recovery callback failed for {service_name}: {e}")

    def get_health_status(
        self, service_name: Optional[str] = None
    ) -> Union[ServiceHealth, Dict[str, ServiceHealth]]:
        """Get health status for service or all services"""
        if service_name:
            return self.health_states.get(service_name)
        else:
            return self.health_states.copy()

    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        report = {
            "timestamp": time.time(),
            "monitoring_active": self._monitoring,
            "services": {},
            "summary": {
                "total": len(self.health_states),
                "healthy": 0,
                "degraded": 0,
                "unhealthy": 0,
                "unknown": 0,
            },
        }

        for service_name, state in self.health_states.items():
            service_report = {
                "status": state.status.value,
                "last_check": state.last_check,
                "response_time": state.response_time,
                "consecutive_failures": state.consecutive_failures,
                "consecutive_successes": state.consecutive_successes,
                "total_checks": state.total_checks,
                "details": state.details,
            }

            report["services"][service_name] = service_report
            report["summary"][state.status.value] += 1

        return report

    async def trigger_manual_check(
        self, service_name: str
    ) -> Optional[HealthCheckResult]:
        """Trigger manual health check for specific service"""
        if service_name not in self.checkers:
            logger.warning(f"No checker found for service: {service_name}")
            return None

        # Capture old status
        old_status = self.health_states[service_name].status

        checker = self.checkers[service_name]
        result = await checker.check()
        checker._last_result = result

        await self._update_health_state(service_name, result)
        await self._handle_state_transition(service_name, old_status, result)

        return result


# Factory functions for common health checkers
def create_rag_api_health_checker(
    base_url: str = "http://localhost:8000",
) -> HTTPHealthChecker:
    """Create health checker for RAG API"""
    return HTTPHealthChecker(
        service_name="rag_api",
        url=f"{base_url}/health",
        expected_status=200,
        timeout=30.0,
    )


def create_chainlit_ui_health_checker(
    base_url: str = "http://localhost:8001",
) -> HTTPHealthChecker:
    """Create health checker for Chainlit UI"""
    return HTTPHealthChecker(
        service_name="chainlit_ui",
        url=f"{base_url}/health",
        expected_status=200,
        timeout=30.0,
    )


def create_redis_health_checker(redis_client: redis.Redis) -> RedisHealthChecker:
    """Create health checker for Redis"""
    return RedisHealthChecker(
        service_name="redis", redis_client=redis_client, timeout=30.0
    )


def create_vikunja_health_checker(
    base_url: str = "http://localhost:3456",
) -> HTTPHealthChecker:
    """Create health checker for Vikunja"""
    return HTTPHealthChecker(
        service_name="vikunja",
        url=f"{base_url}/api/v1/info",
        expected_status=200,
        timeout=30.0,
    )


def create_caddy_health_checker(
    base_url: str = "http://localhost:8000",
) -> HTTPHealthChecker:
    """Create health checker for Caddy"""
    return HTTPHealthChecker(
        service_name="caddy",
        url=f"{base_url}/health",
        expected_status=200,
        timeout=30.0,
    )


# Example usage
async def example_usage():
    """Example of how to use the health monitoring system"""

    # Create health monitor
    monitor = HealthMonitor(check_interval=30.0)

    # Create Redis client
    redis_client = redis.Redis(host="redis", port=6379, db=0)

    # Add health checkers
    monitor.add_checker(create_rag_api_health_checker())
    monitor.add_checker(create_chainlit_ui_health_checker())
    monitor.add_checker(create_redis_health_checker(redis_client))
    monitor.add_checker(create_vikunja_health_checker())
    monitor.add_checker(create_caddy_health_checker())

    # Add recovery callback
    async def recovery_callback(service_name: str):
        logger.info(f"Service {service_name} recovered, triggering additional checks")
        await monitor.trigger_manual_check(service_name)

    monitor.add_recovery_callback("redis", recovery_callback)

    # Add health callback
    async def health_callback(
        service_name: str,
        old_status: HealthStatus,
        new_status: HealthStatus,
        result: HealthCheckResult,
    ):
        logger.info(
            f"Health change for {service_name}: {old_status.value} -> {new_status.value}"
        )

        if new_status == HealthStatus.UNHEALTHY:
            logger.error(f"Service {service_name} is unhealthy: {result.error_message}")

    monitor.add_health_callback("rag_api", health_callback)

    # Start monitoring
    await monitor.start_monitoring()

    try:
        # Monitor for 5 minutes
        await asyncio.sleep(300)
    finally:
        await monitor.stop_monitoring()

    # Get final report
    report = monitor.get_health_report()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    anyio.run(example_usage)

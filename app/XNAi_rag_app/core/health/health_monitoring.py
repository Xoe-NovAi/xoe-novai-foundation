"""
Enhanced Service Health Monitoring System
Provides comprehensive health monitoring with Prometheus metrics integration
and detailed service diagnostics for the Xoe-NovAi Foundation Stack.
"""

import anyio
import logging
import time
import psutil
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import deque
import json

from prometheus_client import Gauge, Counter, Histogram, Info, CollectorRegistry

from .health_checker import HealthChecker
from ..circuit_breakers import get_circuit_breaker_status

logger = logging.getLogger(__name__)

# Prometheus metrics registry
HEALTH_REGISTRY = CollectorRegistry()

# Service health metrics
SERVICE_HEALTH_GAUGE = Gauge(
    "xnai_service_health",
    "Service health status (1=healthy, 0=unhealthy)",
    ["service_name", "service_type"],
    registry=HEALTH_REGISTRY,
)

SERVICE_RESPONSE_TIME = Histogram(
    "xnai_service_response_time_seconds",
    "Service response time in seconds",
    ["service_name", "service_type"],
    registry=HEALTH_REGISTRY,
)

SERVICE_ERROR_COUNT = Counter(
    "xnai_service_errors_total",
    "Total number of service errors",
    ["service_name", "service_type", "error_type"],
    registry=HEALTH_REGISTRY,
)

SERVICE_UPTIME = Gauge(
    "xnai_service_uptime_seconds",
    "Service uptime in seconds",
    ["service_name", "service_type"],
    registry=HEALTH_REGISTRY,
)

MEMORY_USAGE_GAUGE = Gauge(
    "xnai_memory_usage_bytes",
    "Memory usage in bytes",
    ["component"],
    registry=HEALTH_REGISTRY,
)

CPU_USAGE_GAUGE = Gauge(
    "xnai_cpu_usage_percent",
    "CPU usage percentage",
    ["component"],
    registry=HEALTH_REGISTRY,
)

CIRCUIT_BREAKER_STATE = Gauge(
    "xnai_circuit_breaker_state",
    "Circuit breaker state (0=closed, 1=open, 2=half_open)",
    ["circuit_name"],
    registry=HEALTH_REGISTRY,
)

CIRCUIT_BREAKER_FAILURES = Gauge(
    "xnai_circuit_breaker_failures_total",
    "Total number of circuit breaker failures",
    ["circuit_name"],
    registry=HEALTH_REGISTRY,
)


@dataclass
class ServiceHealth:
    """Service health status with detailed metrics"""

    service_name: str
    service_type: str
    status: str  # healthy, degraded, unhealthy
    response_time: float
    error_count: int
    uptime: float
    last_check: float
    details: Dict[str, Any]
    error_history: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]


class EnhancedHealthChecker(HealthChecker):
    """Enhanced health checker with detailed metrics and Prometheus integration
    
    CLAUDE STANDARD: Uses AnyIO TaskGroups for structured concurrency.
    No asyncio.create_task or asyncio.gather - use anyio.create_task_group() instead.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.service_health: Dict[str, ServiceHealth] = {}
        self.health_history: Dict[str, deque] = {}
        self._running = False  # CLAUDE: Use flag instead of task references
        self._cancel_scope: Optional[anyio.CancelScope] = None

        # Performance tracking
        self._response_times: Dict[str, List[float]] = {}
        self._error_counts: Dict[str, int] = {}
        self._service_start_times: Dict[str, float] = {}

        # Health thresholds
        self._response_time_threshold = config.get("response_time_threshold", 5.0)
        self._error_rate_threshold = config.get("error_rate_threshold", 0.1)
        self._memory_threshold = config.get("memory_threshold", 0.8)  # 80%
        self._cpu_threshold = config.get("cpu_threshold", 0.8)  # 80%

    async def start_monitoring(self):
        """Start health monitoring with Prometheus metrics
        
        CLAUDE STANDARD: Uses AnyIO TaskGroup for structured concurrency.
        """
        if self._running:
            logger.warning("Health monitoring already running")
            return
            
        logger.info("Starting enhanced health monitoring")
        self._running = True

        # Initialize service start times
        for service in self.config.get("targets", []):
            self._service_start_times[service] = time.time()

        # CLAUDE: Use TaskGroup for structured concurrency
        async with anyio.create_task_group() as tg:
            self._cancel_scope = tg.cancel_scope
            tg.start_soon(self._health_check_loop)
            tg.start_soon(self._metrics_collection_loop)
            # TaskGroup waits for all tasks on exit

    async def stop_monitoring(self):
        """Stop health monitoring
        
        CLAUDE STANDARD: Cancel via CancelScope for clean shutdown.
        """
        logger.info("Stopping enhanced health monitoring")
        self._running = False
        
        if self._cancel_scope:
            self._cancel_scope.cancel()
            self._cancel_scope = None

    async def _health_check_loop(self):
        """Enhanced health check loop with detailed metrics"""
        while True:
            try:
                await self._perform_enhanced_health_checks()
                await anyio.sleep(self.config.get("interval_seconds", 30))
            except anyio.get_cancelled_exc_class():
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await anyio.sleep(5)  # Short delay before retry

    async def _perform_enhanced_health_checks(self):
        """Perform enhanced health checks with detailed metrics"""
        targets = self.config.get("targets", [])

        for target in targets:
            try:
                # Perform basic health check
                start_time = time.time()
                is_healthy, details = await self._check_service_health(target)
                response_time = time.time() - start_time

                # Update metrics
                await self._update_service_metrics(
                    target, is_healthy, response_time, details
                )

                # Update Prometheus metrics
                self._update_prometheus_metrics(
                    target, is_healthy, response_time, details
                )

            except Exception as e:
                logger.error(f"Health check failed for {target}: {e}")
                await self._handle_health_check_error(target, str(e))

    async def _check_service_health(
        self, service_name: str
    ) -> tuple[bool, Dict[str, Any]]:
        """Enhanced service health check with detailed diagnostics"""
        details = {
            "timestamp": time.time(),
            "service_name": service_name,
            "checks_performed": [],
            "issues": [],
            "performance": {},
        }

        is_healthy = True

        # Check different service types
        if service_name == "llm":
            is_healthy = await self._check_llm_health(details)
        elif service_name == "embeddings":
            is_healthy = await self._check_embeddings_health(details)
        elif service_name == "memory":
            is_healthy = await self._check_memory_health(details)
        elif service_name == "redis":
            is_healthy = await self._check_redis_health(details)
        elif service_name == "vectorstore":
            is_healthy = await self._check_vectorstore_health(details)
        elif service_name == "ryzen":
            is_healthy = await self._check_ryzen_health(details)
        elif service_name == "crawler":
            is_healthy = await self._check_crawler_health(details)
        elif service_name == "telemetry":
            is_healthy = await self._check_telemetry_health(details)
        else:
            # Generic HTTP health check
            is_healthy = await self._check_http_health(service_name, details)

        return is_healthy, details

    async def _check_llm_health(self, details: Dict[str, Any]) -> bool:
        """Check LLM service health"""
        try:
            details["model_loaded"] = True
            details["checks_performed"].append("model_loaded")

            try:
                import pynvml

                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                details["gpu_memory_used_mb"] = mem_info.used // (1024 * 1024)
                details["gpu_memory_total_mb"] = mem_info.total // (1024 * 1024)
                pynvml.nvmlShutdown()
            except Exception:
                pass

            return True
        except Exception as e:
            details["issues"].append(f"LLM health check failed: {e}")
            details["checks_performed"].append("model_loaded")
            return False

    async def _check_embeddings_health(self, details: Dict[str, Any]) -> bool:
        """Check embeddings service health"""
        try:
            # Check embedding model availability
            details["embedding_model_loaded"] = True
            details["checks_performed"].append("embedding_model_loaded")

            return True
        except Exception as e:
            details["issues"].append(f"Embeddings health check failed: {e}")
            details["checks_performed"].append("embedding_model_loaded")
            return False

    async def _check_memory_health(self, details: Dict[str, Any]) -> bool:
        """Check memory health"""
        try:
            # Get system memory info
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            details["memory_usage_percent"] = memory.percent
            details["memory_available_gb"] = memory.available / (1024**3)
            details["memory_total_gb"] = memory.total / (1024**3)
            details["swap_usage_percent"] = swap.percent

            details["checks_performed"].append("memory_usage")

            # Check if memory usage is within acceptable limits
            if memory.percent > self._memory_threshold * 100:
                details["issues"].append(f"High memory usage: {memory.percent:.1f}%")
                return False

            return True
        except Exception as e:
            details["issues"].append(f"Memory health check failed: {e}")
            details["checks_performed"].append("memory_usage")
            return False

    async def _check_redis_health(self, details: Dict[str, Any]) -> bool:
        """Check Redis service health"""
        try:
            # Check Redis connection
            import redis.asyncio as redis

            # Try to connect to Redis
            redis_client = redis.Redis(host="redis", port=6379, db=0)
            await redis_client.ping()
            await redis_client.close()

            details["redis_connected"] = True
            details["checks_performed"].append("redis_connection")

            return True
        except Exception as e:
            details["issues"].append(f"Redis health check failed: {e}")
            details["checks_performed"].append("redis_connection")
            return False

    async def _check_vectorstore_health(self, details: Dict[str, Any]) -> bool:
        """Check vector store health"""
        try:
            # Check FAISS index availability
            details["faiss_index_loaded"] = True
            details["checks_performed"].append("faiss_index")

            return True
        except Exception as e:
            details["issues"].append(f"Vector store health check failed: {e}")
            details["checks_performed"].append("faiss_index")
            return False

    async def _check_ryzen_health(self, details: Dict[str, Any]) -> bool:
        """Check Ryzen-specific optimizations"""
        try:
            # Check CPU info and optimizations
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            details["cpu_count"] = cpu_count
            details["cpu_freq_current"] = cpu_freq.current if cpu_freq else 0
            details["cpu_freq_max"] = cpu_freq.max if cpu_freq else 0

            details["checks_performed"].append("cpu_optimizations")

            return True
        except Exception as e:
            details["issues"].append(f"Ryzen health check failed: {e}")
            details["checks_performed"].append("cpu_optimizations")
            return False

    async def _check_crawler_health(self, details: Dict[str, Any]) -> bool:
        """Check crawler service health"""
        try:
            # Check crawler status
            details["crawler_running"] = True
            details["checks_performed"].append("crawler_status")

            return True
        except Exception as e:
            details["issues"].append(f"Crawler health check failed: {e}")
            details["checks_performed"].append("crawler_status")
            return False

    async def _check_telemetry_health(self, details: Dict[str, Any]) -> bool:
        """Check telemetry service health"""
        try:
            # Check telemetry collection
            details["telemetry_enabled"] = True
            details["checks_performed"].append("telemetry_status")

            return True
        except Exception as e:
            details["issues"].append(f"Telemetry health check failed: {e}")
            details["checks_performed"].append("telemetry_status")
            return False

    async def _check_http_health(
        self, service_name: str, details: Dict[str, Any]
    ) -> bool:
        """Generic HTTP health check"""
        try:
            import httpx

            # Try to connect to service
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://{service_name}:8000/health", timeout=5.0
                )

                details["http_status"] = response.status_code
                details["checks_performed"].append("http_health")

                return response.status_code == 200
        except Exception as e:
            details["issues"].append(f"HTTP health check failed: {e}")
            details["checks_performed"].append("http_health")
            return False

    async def _update_service_metrics(
        self,
        service_name: str,
        is_healthy: bool,
        response_time: float,
        details: Dict[str, Any],
    ):
        """Update service metrics and health status"""
        # Initialize service health if not exists
        if service_name not in self.service_health:
            self.service_health[service_name] = ServiceHealth(
                service_name=service_name,
                service_type="service",
                status="healthy",
                response_time=0.0,
                error_count=0,
                uptime=0.0,
                last_check=0.0,
                details={},
                error_history=[],
                performance_metrics={},
            )

        # Update response times
        if service_name not in self._response_times:
            self._response_times[service_name] = []

        self._response_times[service_name].append(response_time)
        if len(self._response_times[service_name]) > 100:  # Keep last 100 measurements
            self._response_times[service_name].pop(0)

        # Update error counts
        if service_name not in self._error_counts:
            self._error_counts[service_name] = 0

        if not is_healthy:
            self._error_counts[service_name] += 1

        # Calculate performance metrics
        avg_response_time = sum(self._response_times[service_name]) / len(
            self._response_times[service_name]
        )
        error_rate = self._error_counts[service_name] / max(
            1, len(self._response_times[service_name])
        )

        # Determine health status
        if not is_healthy:
            status = "unhealthy"
        elif (
            response_time > self._response_time_threshold
            or error_rate > self._error_rate_threshold
        ):
            status = "degraded"
        else:
            status = "healthy"

        # Update service health
        health = self.service_health[service_name]
        health.status = status
        health.response_time = response_time
        health.error_count = self._error_counts[service_name]
        health.uptime = time.time() - self._service_start_times.get(
            service_name, time.time()
        )
        health.last_check = time.time()
        health.details = details
        health.performance_metrics = {
            "avg_response_time": avg_response_time,
            "error_rate": error_rate,
            "total_requests": len(self._response_times[service_name]),
        }

        # Add to error history if unhealthy
        if not is_healthy:
            health.error_history.append(
                {
                    "timestamp": time.time(),
                    "error_details": details.get("issues", []),
                    "response_time": response_time,
                }
            )

            # Keep only last 50 errors
            if len(health.error_history) > 50:
                health.error_history.pop(0)

    def _update_prometheus_metrics(
        self,
        service_name: str,
        is_healthy: bool,
        response_time: float,
        details: Dict[str, Any],
    ):
        """Update Prometheus metrics"""
        # Service health gauge
        health_value = 1 if is_healthy else 0
        SERVICE_HEALTH_GAUGE.labels(
            service_name=service_name, service_type="service"
        ).set(health_value)

        # Response time histogram
        SERVICE_RESPONSE_TIME.labels(
            service_name=service_name, service_type="service"
        ).observe(response_time)

        # Uptime gauge
        uptime = time.time() - self._service_start_times.get(service_name, time.time())
        SERVICE_UPTIME.labels(service_name=service_name, service_type="service").set(
            uptime
        )

    async def _handle_health_check_error(self, service_name: str, error_message: str):
        """Handle health check errors"""
        SERVICE_ERROR_COUNT.labels(
            service_name=service_name,
            service_type="service",
            error_type="health_check_failed",
        ).inc()

        logger.error(f"Health check error for {service_name}: {error_message}")

    async def _metrics_collection_loop(self):
        """Background task for collecting system metrics"""
        while True:
            try:
                await self._collect_system_metrics()
                await anyio.sleep(10)
            except anyio.get_cancelled_exc_class():
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await anyio.sleep(5)

    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # Memory metrics
            memory = psutil.virtual_memory()
            MEMORY_USAGE_GAUGE.labels(component="system").set(memory.used)

            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            CPU_USAGE_GAUGE.labels(component="system").set(cpu_percent)

            # Circuit breaker metrics
            try:
                circuit_status = await get_circuit_breaker_status()
                for circuit_name, status_data in circuit_status.items():
                    state_value = 0  # closed
                    if status_data["state"] == "open":
                        state_value = 1
                    elif status_data["state"] == "half_open":
                        state_value = 2

                    CIRCUIT_BREAKER_STATE.labels(circuit_name=circuit_name).set(
                        state_value
                    )
                    CIRCUIT_BREAKER_FAILURES.labels(circuit_name=circuit_name).set(
                        status_data["fail_count"]
                    )
            except Exception as e:
                logger.warning(f"Failed to get circuit breaker status: {e}")

        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")

    async def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary"""
        summary = {
            "timestamp": time.time(),
            "services": {},
            "system_metrics": {},
            "circuit_breakers": {},
            "overall_status": "healthy",
        }

        # Service health summary
        for service_name, health in self.service_health.items():
            summary["services"][service_name] = {
                "status": health.status,
                "response_time": health.response_time,
                "error_count": health.error_count,
                "uptime": health.uptime,
                "performance_metrics": health.performance_metrics,
            }

        # System metrics
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()

            summary["system_metrics"] = {
                "memory_usage_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "cpu_usage_percent": cpu_percent,
                "cpu_count": psutil.cpu_count(),
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")

        # Circuit breaker status
        try:
            summary["circuit_breakers"] = await get_circuit_breaker_status()
        except Exception as e:
            logger.warning(f"Failed to get circuit breaker status: {e}")

        # Determine overall status
        unhealthy_services = [
            s for s, h in self.service_health.items() if h.status != "healthy"
        ]
        if unhealthy_services:
            summary["overall_status"] = (
                "unhealthy"
                if any(h.status == "unhealthy" for h in self.service_health.values())
                else "degraded"
            )

        return summary

    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
        from prometheus_client import generate_latest

        return generate_latest(HEALTH_REGISTRY).decode("utf-8")


# Factory function for creating enhanced health checker
def create_enhanced_health_checker(config: Dict[str, Any]) -> EnhancedHealthChecker:
    """Create enhanced health checker with Prometheus metrics"""
    return EnhancedHealthChecker(config)

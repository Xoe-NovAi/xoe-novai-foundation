"""
Database Connection Pool Manager with Health Checks and Failover
==================================================================

Multi-tier connection pooling for PostgreSQL, Redis, and Qdrant with
automatic health monitoring and cascading failover.

CLAUDE STANDARD: Uses AnyIO for structured concurrency.
TORCH-FREE: No external dependencies beyond standard database drivers.

Features:
- Connection pooling for PostgreSQL, Redis, and Qdrant
- Health checks with 30-second interval, 5-second timeout
- Automatic failover cascade: PostgreSQL → Redis → Qdrant → Local
- Failure logging and automatic recovery (60-second retry)
- Sub-100ms connection establishment target
- Performance metrics and benchmarking
"""

import anyio
import asyncio
import logging
import os
import time
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable, Tuple
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)

# Optional database imports
try:
    import psycopg2
    from psycopg2 import pool as psycopg_pool
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None
    psycopg_pool = None
    logger.debug("psycopg2 not available - PostgreSQL pooling disabled")

try:
    import redis.asyncio as redis
    from redis.asyncio import Redis, ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    Redis = None
    ConnectionPool = None
    logger.debug("redis not available - Redis pooling disabled")

try:
    from qdrant_client import QdrantClient as QdrantClientSDK
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClientSDK = None
    logger.debug("qdrant-client not available - Qdrant pooling disabled")


# ============================================================================
# Enums and Data Structures
# ============================================================================


class DatabaseType(str, Enum):
    """Supported database types"""
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    QDRANT = "qdrant"
    LOCAL = "local"


class ConnectionStatus(str, Enum):
    """Connection status states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    RECOVERING = "recovering"


@dataclass
class HealthCheckConfig:
    """Configuration for health checks"""
    check_interval: int = 30  # seconds
    timeout: int = 5  # seconds
    recovery_interval: int = 60  # seconds
    failure_threshold: int = 3  # failures before marking unhealthy


@dataclass
class ConnectionMetrics:
    """Metrics for a single connection"""
    total_checks: int = 0
    successful_checks: int = 0
    failed_checks: int = 0
    consecutive_failures: int = 0
    last_check_time: Optional[float] = None
    last_failure_time: Optional[float] = None
    avg_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    check_history: List[Tuple[float, bool]] = field(default_factory=lambda: deque(maxlen=100))

    def update_check(self, success: bool, response_time: float) -> None:
        """Update metrics with check result"""
        self.total_checks += 1
        self.last_check_time = time.time()
        self.check_history.append((response_time, success))

        if success:
            self.successful_checks += 1
            self.consecutive_failures = 0
        else:
            self.failed_checks += 1
            self.consecutive_failures += 1
            self.last_failure_time = time.time()

        # Update response time stats
        self.min_response_time = min(self.min_response_time, response_time)
        self.max_response_time = max(self.max_response_time, response_time)
        
        # Update average
        if self.successful_checks > 0:
            all_times = [t for t, _ in self.check_history]
            self.avg_response_time = sum(all_times) / len(all_times)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_checks": self.total_checks,
            "successful_checks": self.successful_checks,
            "failed_checks": self.failed_checks,
            "consecutive_failures": self.consecutive_failures,
            "success_rate": self.successful_checks / max(self.total_checks, 1),
            "avg_response_time_ms": round(self.avg_response_time * 1000, 2),
            "min_response_time_ms": round(self.min_response_time * 1000, 2) if self.min_response_time != float('inf') else None,
            "max_response_time_ms": round(self.max_response_time * 1000, 2),
            "last_check_time": self.last_check_time,
            "last_failure_time": self.last_failure_time,
        }


@dataclass
class DatabaseConfig:
    """Configuration for a single database connection"""
    db_type: DatabaseType
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    url: Optional[str] = None  # For Redis and Qdrant
    pool_size: int = 5
    max_overflow: int = 10
    timeout: int = 5
    enabled: bool = True


# ============================================================================
# PostgreSQL Connection Pool
# ============================================================================


class PostgreSQLPool:
    """PostgreSQL connection pool using psycopg2"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool = None
        self.metrics = ConnectionMetrics()
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize PostgreSQL connection pool"""
        if not PSYCOPG2_AVAILABLE:
            logger.warning("psycopg2 not available - PostgreSQL pool disabled")
            return False

        if self._initialized:
            return True

        try:
            # Create connection pool
            self.pool = psycopg_pool.SimpleConnectionPool(
                1,  # minconn
                self.config.pool_size,  # maxconn
                host=self.config.host,
                port=self.config.port or 5432,
                user=self.config.username,
                password=self.config.password,
                database=self.config.database,
                connect_timeout=self.config.timeout,
            )
            self._initialized = True
            logger.info(
                f"PostgreSQL pool initialized: {self.config.host}:{self.config.port}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL pool: {e}")
            return False

    async def health_check(self) -> Tuple[bool, float]:
        """Check PostgreSQL health with timing"""
        if not self.pool:
            return False, 0.0

        start_time = time.time()
        try:
            conn = self.pool.getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            self.pool.putconn(conn)
            response_time = time.time() - start_time
            return True, response_time
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            response_time = time.time() - start_time
            return False, response_time

    async def close(self) -> None:
        """Close all connections in pool"""
        if self.pool:
            try:
                self.pool.closeall()
                self.pool = None
                self._initialized = False
                logger.info("PostgreSQL pool closed")
            except Exception as e:
                logger.error(f"Error closing PostgreSQL pool: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get pool status"""
        return {
            "type": self.config.db_type.value,
            "initialized": self._initialized,
            "pool_size": self.config.pool_size,
            "metrics": self.metrics.to_dict(),
        }


# ============================================================================
# Redis Connection Pool
# ============================================================================


class RedisPool:
    """Redis connection pool using redis-py"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool = None
        self.client = None
        self.metrics = ConnectionMetrics()
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize Redis connection pool"""
        if not REDIS_AVAILABLE:
            logger.warning("redis-py not available - Redis pool disabled")
            return False

        if self._initialized:
            return True

        try:
            # Create connection pool
            if self.config.url:
                self.pool = ConnectionPool.from_url(
                    self.config.url,
                    max_connections=self.config.pool_size,
                    decode_responses=True,
                    socket_connect_timeout=self.config.timeout,
                    socket_timeout=self.config.timeout,
                )
            else:
                self.pool = ConnectionPool(
                    host=self.config.host or "localhost",
                    port=self.config.port or 6379,
                    password=self.config.password,
                    db=0,
                    max_connections=self.config.pool_size,
                    decode_responses=True,
                    socket_connect_timeout=self.config.timeout,
                    socket_timeout=self.config.timeout,
                )

            self.client = Redis(connection_pool=self.pool)

            # Test connection
            async with anyio.move_on_after(self.config.timeout):
                await self.client.ping()

            self._initialized = True
            logger.info(
                f"Redis pool initialized: {self.config.host or 'url'}:{self.config.port or 'default'}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Redis pool: {e}")
            self.pool = None
            self.client = None
            return False

    async def health_check(self) -> Tuple[bool, float]:
        """Check Redis health with timing"""
        if not self.client:
            return False, 0.0

        start_time = time.time()
        try:
            async with anyio.move_on_after(self.config.timeout):
                await self.client.ping()
            response_time = time.time() - start_time
            return True, response_time
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            response_time = time.time() - start_time
            return False, response_time

    async def close(self) -> None:
        """Close all connections in pool"""
        if self.client:
            try:
                await self.client.close()
                self.client = None
            except Exception as e:
                logger.error(f"Error closing Redis client: {e}")

        if self.pool:
            try:
                await self.pool.disconnect()
                self.pool = None
                self._initialized = False
                logger.info("Redis pool closed")
            except Exception as e:
                logger.error(f"Error closing Redis pool: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get pool status"""
        return {
            "type": self.config.db_type.value,
            "initialized": self._initialized,
            "pool_size": self.config.pool_size,
            "metrics": self.metrics.to_dict(),
        }


# ============================================================================
# Qdrant Connection Pool
# ============================================================================


class QdrantPool:
    """Qdrant connection pool"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.client = None
        self.metrics = ConnectionMetrics()
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize Qdrant connection"""
        if not QDRANT_AVAILABLE:
            logger.warning("qdrant-client not available - Qdrant pool disabled")
            return False

        if self._initialized:
            return True

        try:
            # Create Qdrant client
            self.client = QdrantClientSDK(
                url=self.config.url or f"http://{self.config.host}:{self.config.port or 6333}",
                timeout=self.config.timeout,
            )

            # Test connection
            await anyio.to_thread.run_sync(self.client.get_collections)

            self._initialized = True
            logger.info(f"Qdrant client initialized: {self.config.url}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            self.client = None
            return False

    async def health_check(self) -> Tuple[bool, float]:
        """Check Qdrant health with timing"""
        if not self.client:
            return False, 0.0

        start_time = time.time()
        try:
            async with anyio.move_on_after(self.config.timeout):
                await anyio.to_thread.run_sync(self.client.get_collections)
            response_time = time.time() - start_time
            return True, response_time
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            response_time = time.time() - start_time
            return False, response_time

    async def close(self) -> None:
        """Close Qdrant connection"""
        if self.client:
            try:
                self.client.close()
                self.client = None
                self._initialized = False
                logger.info("Qdrant connection closed")
            except Exception as e:
                logger.error(f"Error closing Qdrant connection: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get pool status"""
        return {
            "type": self.config.db_type.value,
            "initialized": self._initialized,
            "url": self.config.url,
            "metrics": self.metrics.to_dict(),
        }


# ============================================================================
# Multi-Database Connection Manager with Failover
# ============================================================================


class DatabaseConnectionPool:
    """
    Unified database connection manager with multi-tier failover.

    Priority: PostgreSQL → Redis → Qdrant → Local

    Usage:
        config = {
            'postgresql': DatabaseConfig(
                db_type=DatabaseType.POSTGRESQL,
                host='localhost',
                port=5432,
                username='user',
                password='pass',
                database='xnai'
            ),
            'redis': DatabaseConfig(
                db_type=DatabaseType.REDIS,
                host='localhost',
                port=6379,
            ),
            'qdrant': DatabaseConfig(
                db_type=DatabaseType.QDRANT,
                url='http://localhost:6333',
            ),
        }

        pool = DatabaseConnectionPool(config)
        await pool.initialize()
        await pool.start_health_checks()

        # Use first available database
        primary_db = pool.get_primary()

        # Check status
        status = pool.get_status()
    """

    def __init__(
        self,
        configs: Dict[str, DatabaseConfig],
        health_check_config: Optional[HealthCheckConfig] = None,
    ):
        self.configs = configs
        self.health_config = health_check_config or HealthCheckConfig()

        # Database pools
        self.pools: Dict[str, Any] = {}
        self.pool_order: List[str] = []  # Priority order

        # Status tracking
        self.status: Dict[str, ConnectionStatus] = {}
        self.last_recovery_attempt: Dict[str, float] = {}

        # Health check state
        self._health_check_task: Optional[anyio.CancelScope] = None
        self._initialized = False

        # Initialize pools based on priority
        self._initialize_pools()

    def _initialize_pools(self) -> None:
        """Initialize pool objects (not connections)"""
        # Define priority order
        priority_order = [
            DatabaseType.POSTGRESQL,
            DatabaseType.REDIS,
            DatabaseType.QDRANT,
            DatabaseType.LOCAL,
        ]

        for db_type in priority_order:
            for name, config in self.configs.items():
                if config.db_type == db_type and config.enabled:
                    if config.db_type == DatabaseType.POSTGRESQL:
                        self.pools[name] = PostgreSQLPool(config)
                    elif config.db_type == DatabaseType.REDIS:
                        self.pools[name] = RedisPool(config)
                    elif config.db_type == DatabaseType.QDRANT:
                        self.pools[name] = QdrantPool(config)
                    elif config.db_type == DatabaseType.LOCAL:
                        # Local is a fallback marker
                        self.pools[name] = None

                    self.pool_order.append(name)
                    self.status[name] = ConnectionStatus.DEGRADED
                    self.last_recovery_attempt[name] = 0

    async def initialize(self) -> bool:
        """Initialize all database connections"""
        if self._initialized:
            return True

        initialized_any = False

        for name in self.pool_order:
            pool = self.pools.get(name)
            if pool is None:
                # Local fallback
                self.status[name] = ConnectionStatus.HEALTHY
                initialized_any = True
                logger.info(f"Local fallback available: {name}")
                continue

            try:
                success = await pool.initialize()
                if success:
                    self.status[name] = ConnectionStatus.HEALTHY
                    initialized_any = True
                    logger.info(f"Database initialized: {name}")
                else:
                    self.status[name] = ConnectionStatus.UNHEALTHY
                    logger.warning(f"Failed to initialize: {name}")
            except Exception as e:
                logger.error(f"Error initializing {name}: {e}")
                self.status[name] = ConnectionStatus.UNHEALTHY

        self._initialized = initialized_any
        return initialized_any

    async def start_health_checks(self) -> None:
        """Start background health check task"""
        if self._health_check_task:
            return

        async def health_check_loop():
            while True:
                try:
                    await self._perform_health_checks()
                    await anyio.sleep(self.health_config.check_interval)
                except Exception as e:
                    logger.error(f"Health check loop error: {e}")
                    await anyio.sleep(5)

        self._health_check_task = anyio.CancelScope()
        try:
            await health_check_loop()
        except asyncio.CancelledError:
            pass

    async def _perform_health_checks(self) -> None:
        """Perform health checks on all databases"""
        current_time = time.time()

        for name in self.pool_order:
            pool = self.pools.get(name)
            if pool is None:
                # Local fallback always healthy
                continue

            try:
                # Attempt recovery if marked for retry
                if self.status[name] == ConnectionStatus.UNHEALTHY:
                    time_since_failure = current_time - self.last_recovery_attempt.get(name, 0)
                    if time_since_failure < self.health_config.recovery_interval:
                        continue

                    logger.info(f"Attempting recovery for {name}")
                    self.status[name] = ConnectionStatus.RECOVERING

                # Perform health check with timeout
                success = False
                response_time = 0.0
                try:
                    with anyio.fail_after(self.health_config.timeout):
                        success, response_time = await pool.health_check()
                except TimeoutError:
                    success, response_time = False, self.health_config.timeout

                pool.metrics.update_check(success, response_time)

                if success:
                    if self.status[name] in [
                        ConnectionStatus.UNHEALTHY,
                        ConnectionStatus.RECOVERING,
                    ]:
                        logger.info(f"Database recovered: {name}")
                    self.status[name] = ConnectionStatus.HEALTHY
                else:
                    pool.metrics.consecutive_failures += 1
                    if (
                        pool.metrics.consecutive_failures
                        >= self.health_config.failure_threshold
                    ):
                        logger.warning(
                            f"Database marked unhealthy: {name} "
                            f"({pool.metrics.consecutive_failures} failures)"
                        )
                        self.status[name] = ConnectionStatus.UNHEALTHY
                        self.last_recovery_attempt[name] = current_time
                    else:
                        self.status[name] = ConnectionStatus.DEGRADED

            except Exception as e:
                logger.error(f"Health check error for {name}: {e}")
                self.status[name] = ConnectionStatus.UNHEALTHY
                self.last_recovery_attempt[name] = current_time

    def get_primary(self) -> Optional[str]:
        """Get name of primary (first healthy) database"""
        for name in self.pool_order:
            if self.status[name] == ConnectionStatus.HEALTHY:
                return name
        return None

    def get_available_databases(self) -> List[str]:
        """Get list of available databases in priority order"""
        available = []
        for name in self.pool_order:
            if self.status[name] in [ConnectionStatus.HEALTHY, ConnectionStatus.DEGRADED]:
                available.append(name)
        return available

    async def close(self) -> None:
        """Close all database connections"""
        if self._health_check_task:
            self._health_check_task.cancel()
            self._health_check_task = None

        for name in self.pool_order:
            pool = self.pools.get(name)
            if pool:
                try:
                    await pool.close()
                except Exception as e:
                    logger.error(f"Error closing {name}: {e}")

        self._initialized = False
        logger.info("Database connection pool closed")

    def get_status(self) -> Dict[str, Any]:
        """Get status of all database connections"""
        status = {
            "initialized": self._initialized,
            "primary": self.get_primary(),
            "available": self.get_available_databases(),
            "databases": {},
            "timestamp": datetime.now().isoformat(),
        }

        for name in self.pool_order:
            pool = self.pools.get(name)
            if pool:
                status["databases"][name] = {
                    "status": self.status[name].value,
                    **pool.get_status(),
                }
            else:
                status["databases"][name] = {
                    "status": self.status[name].value,
                    "type": "local_fallback",
                }

        return status

    def get_metrics(self) -> Dict[str, Any]:
        """Get detailed metrics for all databases"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "databases": {},
        }

        for name in self.pool_order:
            pool = self.pools.get(name)
            if pool:
                metrics["databases"][name] = pool.metrics.to_dict()

        return metrics


# ============================================================================
# Factory Functions
# ============================================================================


async def create_pool_from_env() -> Optional[DatabaseConnectionPool]:
    """Create connection pool from environment variables"""
    configs = {}

    # PostgreSQL configuration
    pg_enabled = os.getenv("DATABASE_POSTGRESQL_ENABLED", "false").lower() == "true"
    if pg_enabled:
        configs["postgresql"] = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host=os.getenv("DATABASE_POSTGRESQL_HOST", "localhost"),
            port=int(os.getenv("DATABASE_POSTGRESQL_PORT", "5432")),
            username=os.getenv("DATABASE_POSTGRESQL_USER", "postgres"),
            password=os.getenv("DATABASE_POSTGRESQL_PASSWORD", ""),
            database=os.getenv("DATABASE_POSTGRESQL_DB", "xnai"),
            pool_size=int(os.getenv("DATABASE_POSTGRESQL_POOL_SIZE", "5")),
            enabled=True,
        )

    # Redis configuration
    redis_enabled = os.getenv("DATABASE_REDIS_ENABLED", "true").lower() == "true"
    if redis_enabled:
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            configs["redis"] = DatabaseConfig(
                db_type=DatabaseType.REDIS,
                url=redis_url,
                pool_size=int(os.getenv("DATABASE_REDIS_POOL_SIZE", "5")),
                enabled=True,
            )
        else:
            configs["redis"] = DatabaseConfig(
                db_type=DatabaseType.REDIS,
                host=os.getenv("DATABASE_REDIS_HOST", "localhost"),
                port=int(os.getenv("DATABASE_REDIS_PORT", "6379")),
                password=os.getenv("DATABASE_REDIS_PASSWORD"),
                pool_size=int(os.getenv("DATABASE_REDIS_POOL_SIZE", "5")),
                enabled=True,
            )

    # Qdrant configuration
    qdrant_enabled = os.getenv("DATABASE_QDRANT_ENABLED", "true").lower() == "true"
    if qdrant_enabled:
        qdrant_url = os.getenv(
            "QDRANT_URL", "http://localhost:6333"
        )
        configs["qdrant"] = DatabaseConfig(
            db_type=DatabaseType.QDRANT,
            url=qdrant_url,
            enabled=True,
        )

    # Local fallback always available
    configs["local"] = DatabaseConfig(
        db_type=DatabaseType.LOCAL,
        enabled=True,
    )

    if not configs:
        logger.error("No database configurations found")
        return None

    pool = DatabaseConnectionPool(configs)
    await pool.initialize()
    return pool

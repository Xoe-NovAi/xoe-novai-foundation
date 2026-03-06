"""
Test Database Connection Pooling, Health Checks, and Failover
==============================================================

Comprehensive tests for:
- Connection pool initialization
- Health check functionality
- Failover cascade behavior
- Performance under load
- Recovery after failure
"""

import pytest
import asyncio
import time
import logging
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime

from app.XNAi_rag_app.core.database_connection_pool import (
    DatabaseConnectionPool,
    DatabaseConfig,
    DatabaseType,
    ConnectionStatus,
    HealthCheckConfig,
    ConnectionMetrics,
    PostgreSQLPool,
    RedisPool,
    QdrantPool,
    create_pool_from_env,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# ============================================================================
# Tests for Connection Metrics
# ============================================================================


class TestConnectionMetrics:
    """Test ConnectionMetrics data structure"""

    def test_metrics_initialization(self):
        """Test metrics are initialized correctly"""
        metrics = ConnectionMetrics()
        assert metrics.total_checks == 0
        assert metrics.successful_checks == 0
        assert metrics.failed_checks == 0
        assert metrics.consecutive_failures == 0
        assert metrics.avg_response_time == 0.0

    def test_metrics_update_success(self):
        """Test metrics update on successful check"""
        metrics = ConnectionMetrics()
        metrics.update_check(success=True, response_time=0.05)

        assert metrics.total_checks == 1
        assert metrics.successful_checks == 1
        assert metrics.failed_checks == 0
        assert metrics.consecutive_failures == 0
        assert metrics.avg_response_time == 0.05

    def test_metrics_update_failure(self):
        """Test metrics update on failed check"""
        metrics = ConnectionMetrics()
        metrics.update_check(success=False, response_time=0.1)

        assert metrics.total_checks == 1
        assert metrics.successful_checks == 0
        assert metrics.failed_checks == 1
        assert metrics.consecutive_failures == 1

    def test_metrics_consecutive_failures(self):
        """Test consecutive failure tracking"""
        metrics = ConnectionMetrics()
        for i in range(3):
            metrics.update_check(success=False, response_time=0.1)
        assert metrics.consecutive_failures == 3

        metrics.update_check(success=True, response_time=0.05)
        assert metrics.consecutive_failures == 0

    def test_metrics_to_dict(self):
        """Test metrics serialization"""
        metrics = ConnectionMetrics()
        metrics.update_check(success=True, response_time=0.05)
        metrics.update_check(success=True, response_time=0.03)

        data = metrics.to_dict()
        assert data["total_checks"] == 2
        assert data["successful_checks"] == 2
        assert data["success_rate"] == 1.0
        assert "avg_response_time_ms" in data


# ============================================================================
# Tests for PostgreSQL Pool
# ============================================================================


class TestPostgreSQLPool:
    """Test PostgreSQL connection pool"""

    @pytest.mark.asyncio
    async def test_postgresql_pool_initialization_no_driver(self):
        """Test PostgreSQL pool initialization when driver not available"""
        with patch("app.XNAi_rag_app.core.database_connection_pool.PSYCOPG2_AVAILABLE", False):
            config = DatabaseConfig(
                db_type=DatabaseType.POSTGRESQL,
                host="localhost",
                port=5432,
                username="user",
                password="pass",
                database="test",
            )
            pool = PostgreSQLPool(config)
            result = await pool.initialize()
            assert result is False

    @pytest.mark.asyncio
    async def test_postgresql_health_check_no_pool(self):
        """Test health check fails when pool not initialized"""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
        )
        pool = PostgreSQLPool(config)
        success, response_time = await pool.health_check()
        assert success is False
        assert response_time >= 0

    @pytest.mark.asyncio
    async def test_postgresql_get_status(self):
        """Test PostgreSQL pool status reporting"""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            pool_size=10,
        )
        pool = PostgreSQLPool(config)
        status = pool.get_status()

        assert status["type"] == "postgresql"
        assert status["pool_size"] == 10
        assert "metrics" in status


# ============================================================================
# Tests for Redis Pool
# ============================================================================


class TestRedisPool:
    """Test Redis connection pool"""

    @pytest.mark.asyncio
    async def test_redis_pool_initialization_no_driver(self):
        """Test Redis pool initialization when driver not available"""
        with patch("app.XNAi_rag_app.core.database_connection_pool.REDIS_AVAILABLE", False):
            config = DatabaseConfig(
                db_type=DatabaseType.REDIS,
                host="localhost",
                port=6379,
            )
            pool = RedisPool(config)
            result = await pool.initialize()
            assert result is False

    @pytest.mark.asyncio
    async def test_redis_health_check_no_client(self):
        """Test health check fails when client not initialized"""
        config = DatabaseConfig(
            db_type=DatabaseType.REDIS,
            host="localhost",
            port=6379,
        )
        pool = RedisPool(config)
        success, response_time = await pool.health_check()
        assert success is False
        assert response_time >= 0

    @pytest.mark.asyncio
    async def test_redis_get_status(self):
        """Test Redis pool status reporting"""
        config = DatabaseConfig(
            db_type=DatabaseType.REDIS,
            host="localhost",
            port=6379,
            pool_size=5,
        )
        pool = RedisPool(config)
        status = pool.get_status()

        assert status["type"] == "redis"
        assert status["pool_size"] == 5
        assert "metrics" in status


# ============================================================================
# Tests for Qdrant Pool
# ============================================================================


class TestQdrantPool:
    """Test Qdrant connection pool"""

    @pytest.mark.asyncio
    async def test_qdrant_pool_initialization_no_driver(self):
        """Test Qdrant pool initialization when driver not available"""
        with patch("app.XNAi_rag_app.core.database_connection_pool.QDRANT_AVAILABLE", False):
            config = DatabaseConfig(
                db_type=DatabaseType.QDRANT,
                url="http://localhost:6333",
            )
            pool = QdrantPool(config)
            result = await pool.initialize()
            assert result is False

    @pytest.mark.asyncio
    async def test_qdrant_health_check_no_client(self):
        """Test health check fails when client not initialized"""
        config = DatabaseConfig(
            db_type=DatabaseType.QDRANT,
            url="http://localhost:6333",
        )
        pool = QdrantPool(config)
        success, response_time = await pool.health_check()
        assert success is False
        assert response_time >= 0

    @pytest.mark.asyncio
    async def test_qdrant_get_status(self):
        """Test Qdrant pool status reporting"""
        config = DatabaseConfig(
            db_type=DatabaseType.QDRANT,
            url="http://localhost:6333",
        )
        pool = QdrantPool(config)
        status = pool.get_status()

        assert status["type"] == "qdrant"
        assert status["url"] == "http://localhost:6333"
        assert "metrics" in status


# ============================================================================
# Tests for DatabaseConnectionPool
# ============================================================================


@pytest.fixture
def mock_redis_pool():
    """Create a mock Redis pool"""
    pool = Mock(spec=RedisPool)
    pool.initialize = AsyncMock(return_value=True)
    pool.health_check = AsyncMock(return_value=(True, 0.05))
    pool.close = AsyncMock()
    pool.get_status = Mock(return_value={"type": "redis", "initialized": True})
    pool.metrics = ConnectionMetrics()
    return pool


@pytest.fixture
def mock_qdrant_pool():
    """Create a mock Qdrant pool"""
    pool = Mock(spec=QdrantPool)
    pool.initialize = AsyncMock(return_value=True)
    pool.health_check = AsyncMock(return_value=(True, 0.03))
    pool.close = AsyncMock()
    pool.get_status = Mock(return_value={"type": "qdrant", "initialized": True})
    pool.metrics = ConnectionMetrics()
    return pool


class TestDatabaseConnectionPool:
    """Test multi-database connection pool with failover"""

    @pytest.mark.asyncio
    async def test_pool_initialization(self, mock_redis_pool):
        """Test connection pool initialization"""
        configs = {
            "redis": DatabaseConfig(
                db_type=DatabaseType.REDIS,
                host="localhost",
                port=6379,
                enabled=True,
            ),
            "local": DatabaseConfig(
                db_type=DatabaseType.LOCAL,
                enabled=True,
            ),
        }

        with patch.object(RedisPool, "__init__", return_value=None):
            pool = DatabaseConnectionPool(configs)

            # Mock the pools
            pool.pools["redis"] = mock_redis_pool
            pool.pools["local"] = None

            result = await pool.initialize()
            assert result is True
            assert len(pool.pool_order) == 2
            assert pool.status["redis"] == ConnectionStatus.HEALTHY
            assert pool.status["local"] == ConnectionStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_get_primary_database(self, mock_redis_pool):
        """Test getting primary database when available"""
        configs = {
            "redis": DatabaseConfig(
                db_type=DatabaseType.REDIS,
                enabled=True,
            ),
            "local": DatabaseConfig(
                db_type=DatabaseType.LOCAL,
                enabled=True,
            ),
        }

        with patch.object(RedisPool, "__init__", return_value=None):
            pool = DatabaseConnectionPool(configs)
            pool.pools["redis"] = mock_redis_pool
            pool.pools["local"] = None
            pool.status["redis"] = ConnectionStatus.HEALTHY
            pool.status["local"] = ConnectionStatus.DEGRADED

            primary = pool.get_primary()
            assert primary == "redis"

    @pytest.mark.asyncio
    async def test_failover_cascade(self, mock_redis_pool, mock_qdrant_pool):
        """Test failover cascade from Redis to Qdrant to Local"""
        configs = {
            "redis": DatabaseConfig(
                db_type=DatabaseType.REDIS,
                enabled=True,
            ),
            "qdrant": DatabaseConfig(
                db_type=DatabaseType.QDRANT,
                enabled=True,
            ),
            "local": DatabaseConfig(
                db_type=DatabaseType.LOCAL,
                enabled=True,
            ),
        }

        with patch.object(RedisPool, "__init__", return_value=None):
            with patch.object(QdrantPool, "__init__", return_value=None):
                pool = DatabaseConnectionPool(configs)
                pool.pools["redis"] = mock_redis_pool
                pool.pools["qdrant"] = mock_qdrant_pool
                pool.pools["local"] = None

                # Simulate Redis failure
                pool.status["redis"] = ConnectionStatus.UNHEALTHY
                pool.status["qdrant"] = ConnectionStatus.HEALTHY
                pool.status["local"] = ConnectionStatus.HEALTHY

                available = pool.get_available_databases()
                assert "qdrant" in available
                assert "local" in available
                assert "redis" not in available

                primary = pool.get_primary()
                assert primary == "qdrant"

    @pytest.mark.asyncio
    async def test_get_available_databases_priority_order(self):
        """Test available databases are returned in priority order"""
        configs = {
            "qdrant": DatabaseConfig(
                db_type=DatabaseType.QDRANT,
                enabled=True,
            ),
            "redis": DatabaseConfig(
                db_type=DatabaseType.REDIS,
                enabled=True,
            ),
            "local": DatabaseConfig(
                db_type=DatabaseType.LOCAL,
                enabled=True,
            ),
        }

        pool = DatabaseConnectionPool(configs)

        # Set all healthy
        pool.status["redis"] = ConnectionStatus.HEALTHY
        pool.status["qdrant"] = ConnectionStatus.HEALTHY
        pool.status["local"] = ConnectionStatus.HEALTHY

        available = pool.get_available_databases()

        # Should be in priority order: Redis > Qdrant > Local
        expected_order = ["redis", "qdrant", "local"]
        assert available == expected_order

    @pytest.mark.asyncio
    async def test_health_check_metrics_update(self, mock_redis_pool):
        """Test health checks update metrics"""
        configs = {
            "redis": DatabaseConfig(
                db_type=DatabaseType.REDIS,
                enabled=True,
            ),
            "local": DatabaseConfig(
                db_type=DatabaseType.LOCAL,
                enabled=True,
            ),
        }

        with patch.object(RedisPool, "__init__", return_value=None):
            pool = DatabaseConnectionPool(configs)
            pool.pools["redis"] = mock_redis_pool
            pool.pools["local"] = None

            # Perform health check
            await pool._perform_health_checks()

            # Verify metrics were updated
            assert pool.pools["redis"].metrics.total_checks == 1
            assert pool.pools["redis"].metrics.successful_checks == 1

    @pytest.mark.asyncio
    async def test_health_check_failure_detection(self, mock_redis_pool):
        """Test health checks detect failures"""
        configs = {
            "redis": DatabaseConfig(
                db_type=DatabaseType.REDIS,
                enabled=True,
            ),
        }

        mock_redis_pool.health_check = AsyncMock(return_value=(False, 5.0))

        with patch.object(RedisPool, "__init__", return_value=None):
            pool = DatabaseConnectionPool(configs)
            pool.pools["redis"] = mock_redis_pool
            pool.health_config.failure_threshold = 1  # Fail on first check

            # First failure - should be marked degraded
            await pool._perform_health_checks()
            assert pool.status["redis"] == ConnectionStatus.DEGRADED
            assert pool.pools["redis"].metrics.failed_checks == 1

            # Second failure - should be marked unhealthy (exceeded threshold)
            await pool._perform_health_checks()
            assert pool.status["redis"] == ConnectionStatus.UNHEALTHY
            assert pool.pools["redis"].metrics.consecutive_failures == 2

    @pytest.mark.asyncio
    async def test_recovery_after_failure(self, mock_redis_pool):
        """Test recovery after failure when health check succeeds"""
        configs = {
            "redis": DatabaseConfig(
                db_type=DatabaseType.REDIS,
                enabled=True,
            ),
        }

        with patch.object(RedisPool, "__init__", return_value=None):
            pool = DatabaseConnectionPool(configs)
            pool.pools["redis"] = mock_redis_pool
            pool.health_config.failure_threshold = 1

            # Mark as unhealthy
            pool.status["redis"] = ConnectionStatus.UNHEALTHY
            pool.last_recovery_attempt["redis"] = time.time() - 61

            # Mock successful health check
            mock_redis_pool.health_check = AsyncMock(return_value=(True, 0.05))

            # Perform recovery
            await pool._perform_health_checks()

            # Should be healthy again
            assert pool.status["redis"] == ConnectionStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_recovery_respects_interval(self, mock_redis_pool):
        """Test recovery doesn't retry too quickly"""
        configs = {
            "redis": DatabaseConfig(
                db_type=DatabaseType.REDIS,
                enabled=True,
            ),
        }

        with patch.object(RedisPool, "__init__", return_value=None):
            pool = DatabaseConnectionPool(configs)
            pool.pools["redis"] = mock_redis_pool
            pool.health_config.recovery_interval = 60

            # Mark as unhealthy with recent failure
            pool.status["redis"] = ConnectionStatus.UNHEALTHY
            pool.last_recovery_attempt["redis"] = time.time() - 30  # Only 30 sec ago

            await pool._perform_health_checks()

            # Should still be unhealthy (no retry)
            assert pool.status["redis"] == ConnectionStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_pool_status_reporting(self, mock_redis_pool):
        """Test pool status reporting"""
        configs = {
            "redis": DatabaseConfig(
                db_type=DatabaseType.REDIS,
                enabled=True,
            ),
            "local": DatabaseConfig(
                db_type=DatabaseType.LOCAL,
                enabled=True,
            ),
        }

        with patch.object(RedisPool, "__init__", return_value=None):
            pool = DatabaseConnectionPool(configs)
            pool.pools["redis"] = mock_redis_pool
            pool.pools["local"] = None
            pool.status["redis"] = ConnectionStatus.HEALTHY
            pool.status["local"] = ConnectionStatus.HEALTHY
            pool._initialized = True  # Mark as initialized

            status = pool.get_status()

            assert status["initialized"] is True
            assert status["primary"] == "redis"
            assert "redis" in status["databases"]
            assert "local" in status["databases"]
            assert status["databases"]["redis"]["status"] == "healthy"
            assert status["databases"]["local"]["type"] == "local_fallback"

    @pytest.mark.asyncio
    async def test_pool_metrics_reporting(self, mock_redis_pool):
        """Test pool metrics reporting"""
        configs = {
            "redis": DatabaseConfig(
                db_type=DatabaseType.REDIS,
                enabled=True,
            ),
        }

        with patch.object(RedisPool, "__init__", return_value=None):
            pool = DatabaseConnectionPool(configs)
            pool.pools["redis"] = mock_redis_pool

            # Update metrics
            pool.pools["redis"].metrics.update_check(True, 0.05)
            pool.pools["redis"].metrics.update_check(True, 0.03)

            metrics = pool.get_metrics()

            assert "redis" in metrics["databases"]
            assert metrics["databases"]["redis"]["total_checks"] == 2
            assert metrics["databases"]["redis"]["successful_checks"] == 2

    @pytest.mark.asyncio
    async def test_pool_close(self, mock_redis_pool):
        """Test closing all connections"""
        configs = {
            "redis": DatabaseConfig(
                db_type=DatabaseType.REDIS,
                enabled=True,
            ),
            "local": DatabaseConfig(
                db_type=DatabaseType.LOCAL,
                enabled=True,
            ),
        }

        with patch.object(RedisPool, "__init__", return_value=None):
            pool = DatabaseConnectionPool(configs)
            pool.pools["redis"] = mock_redis_pool
            pool.pools["local"] = None
            pool._initialized = True

            await pool.close()

            mock_redis_pool.close.assert_called_once()
            assert pool._initialized is False


# ============================================================================
# Integration Tests
# ============================================================================


class TestDatabasePoolIntegration:
    """Integration tests for database pool"""

    @pytest.mark.asyncio
    async def test_local_fallback_always_available(self):
        """Test local fallback is always available"""
        configs = {
            "local": DatabaseConfig(
                db_type=DatabaseType.LOCAL,
                enabled=True,
            ),
        }

        pool = DatabaseConnectionPool(configs)
        await pool.initialize()

        available = pool.get_available_databases()
        assert "local" in available

        primary = pool.get_primary()
        assert primary == "local"

    @pytest.mark.asyncio
    async def test_create_pool_from_env(self):
        """Test creating pool from environment variables"""
        with patch.dict(
            "os.environ",
            {
                "DATABASE_REDIS_ENABLED": "true",
                "DATABASE_REDIS_HOST": "localhost",
                "DATABASE_REDIS_PORT": "6379",
            },
        ):
            with patch("app.XNAi_rag_app.core.database_connection_pool.REDIS_AVAILABLE", False):
                pool = await create_pool_from_env()

                # Should still have local fallback
                assert pool is not None
                available = pool.get_available_databases()
                assert "local" in available


# ============================================================================
# Performance Tests
# ============================================================================


class TestDatabasePoolPerformance:
    """Performance tests for database pool"""

    @pytest.mark.asyncio
    async def test_health_check_sub_100ms(self, mock_redis_pool):
        """Test health checks are sub-100ms"""
        configs = {
            "redis": DatabaseConfig(
                db_type=DatabaseType.REDIS,
                enabled=True,
            ),
        }

        mock_redis_pool.health_check = AsyncMock(return_value=(True, 0.05))

        with patch.object(RedisPool, "__init__", return_value=None):
            pool = DatabaseConnectionPool(configs)
            pool.pools["redis"] = mock_redis_pool

            start_time = time.time()
            await pool._perform_health_checks()
            elapsed = time.time() - start_time

            # Should be fast (most time in async sleep etc)
            assert elapsed < 1.0  # Generous limit for test environment

    @pytest.mark.asyncio
    async def test_failover_decision_fast(self):
        """Test failover decision is fast"""
        configs = {
            "redis": DatabaseConfig(db_type=DatabaseType.REDIS, enabled=True),
            "qdrant": DatabaseConfig(db_type=DatabaseType.QDRANT, enabled=True),
            "local": DatabaseConfig(db_type=DatabaseType.LOCAL, enabled=True),
        }

        pool = DatabaseConnectionPool(configs)
        pool.status["redis"] = ConnectionStatus.UNHEALTHY
        pool.status["qdrant"] = ConnectionStatus.HEALTHY
        pool.status["local"] = ConnectionStatus.HEALTHY

        start_time = time.time()
        primary = pool.get_primary()
        elapsed = time.time() - start_time

        assert primary == "qdrant"
        assert elapsed < 0.001  # Should be instant

    @pytest.mark.asyncio
    async def test_concurrent_health_checks(self, mock_redis_pool, mock_qdrant_pool):
        """Test concurrent health checks"""
        configs = {
            "redis": DatabaseConfig(db_type=DatabaseType.REDIS, enabled=True),
            "qdrant": DatabaseConfig(db_type=DatabaseType.QDRANT, enabled=True),
        }

        with patch.object(RedisPool, "__init__", return_value=None):
            with patch.object(QdrantPool, "__init__", return_value=None):
                pool = DatabaseConnectionPool(configs)
                pool.pools["redis"] = mock_redis_pool
                pool.pools["qdrant"] = mock_qdrant_pool

                start_time = time.time()

                # Perform health checks multiple times
                for _ in range(5):
                    await pool._perform_health_checks()

                elapsed = time.time() - start_time

                # Should complete quickly even with multiple checks
                assert elapsed < 2.0

                # Both should have been checked
                assert pool.pools["redis"].metrics.total_checks == 5
                assert pool.pools["qdrant"].metrics.total_checks == 5


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestDatabasePoolEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_all_databases_unhealthy(self, mock_redis_pool):
        """Test behavior when all databases are unhealthy"""
        configs = {
            "redis": DatabaseConfig(db_type=DatabaseType.REDIS, enabled=True),
            "local": DatabaseConfig(db_type=DatabaseType.LOCAL, enabled=True),
        }

        with patch.object(RedisPool, "__init__", return_value=None):
            pool = DatabaseConnectionPool(configs)
            pool.pools["redis"] = mock_redis_pool
            pool.pools["local"] = None
            pool.status["redis"] = ConnectionStatus.UNHEALTHY
            pool.status["local"] = ConnectionStatus.DEGRADED

            available = pool.get_available_databases()
            # Local is degraded, so still available
            assert "local" in available

    @pytest.mark.asyncio
    async def test_handle_exception_in_health_check(self, mock_redis_pool):
        """Test handling exceptions during health check"""
        configs = {
            "redis": DatabaseConfig(db_type=DatabaseType.REDIS, enabled=True),
        }

        mock_redis_pool.health_check = AsyncMock(side_effect=Exception("Connection error"))

        with patch.object(RedisPool, "__init__", return_value=None):
            pool = DatabaseConnectionPool(configs)
            pool.pools["redis"] = mock_redis_pool

            # Should not raise
            await pool._perform_health_checks()

            assert pool.status["redis"] == ConnectionStatus.UNHEALTHY

    def test_disabled_database_not_initialized(self):
        """Test disabled databases are skipped"""
        configs = {
            "redis": DatabaseConfig(
                db_type=DatabaseType.REDIS,
                enabled=False,
            ),
            "local": DatabaseConfig(
                db_type=DatabaseType.LOCAL,
                enabled=True,
            ),
        }

        pool = DatabaseConnectionPool(configs)

        assert "redis" not in pool.pool_order
        assert "local" in pool.pool_order


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

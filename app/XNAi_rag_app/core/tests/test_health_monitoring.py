"""
Test suite for Health Monitoring module
Tests comprehensive health monitoring and automated recovery.
"""

import asyncio
import pytest
import time
import json
from unittest.mock import Mock, AsyncMock, MagicMock, patch
import aiohttp
import redis.asyncio as redis

from app.XNAi_rag_app.core.health import (
    HealthChecker,
    HealthStatus,
    HealthCheckResult,
    ServiceHealth,
    HTTPHealthChecker,
    RedisHealthChecker,
    DatabaseHealthChecker,
    CustomHealthChecker,
    HealthMonitor,
    RecoveryManager,
    RecoveryAction,
    RecoveryRule,
    RecoveryAttempt,
    create_rag_api_health_checker,
    create_chainlit_ui_health_checker,
    create_redis_health_checker,
    create_vikunja_health_checker,
    create_caddy_health_checker
)


class TestHealthChecker:
    """Test base HealthChecker functionality"""
    
    @pytest.fixture
    def health_checker(self):
        """Create base health checker for testing"""
        return HealthChecker("test_service", timeout=1.0)
    
    @pytest.mark.asyncio
    async def test_successful_check(self, health_checker):
        """Test successful health check"""
        async def mock_check():
            return {"status": "ok"}
        
        health_checker._perform_check = mock_check
        
        result = await health_checker.check()
        
        assert result.service_name == "test_service"
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time > 0
        assert result.details == {"status": "ok"}
        assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_failed_check(self, health_checker):
        """Test failed health check"""
        async def mock_check():
            raise Exception("Service unavailable")
        
        health_checker._perform_check = mock_check
        
        result = await health_checker.check()
        
        assert result.service_name == "test_service"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.response_time > 0
        assert result.details == {}
        assert result.error_message == "Service unavailable"
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, health_checker):
        """Test timeout handling in health checks"""
        async def slow_check():
            await asyncio.sleep(2.0)  # Longer than timeout
            return {"status": "ok"}
        
        health_checker._perform_check = slow_check
        
        result = await health_checker.check()
        
        assert result.status == HealthStatus.UNHEALTHY
        assert "timeout" in result.error_message.lower()


class TestHTTPHealthChecker:
    """Test HTTP health checker"""
    
    @pytest.mark.asyncio
    async def test_successful_http_check(self):
        """Test successful HTTP health check"""
        checker = HTTPHealthChecker(
            service_name="test_http",
            url="http://httpbin.org/status/200",
            expected_status=200,
            timeout=5.0
        )
        
        result = await checker.check()
        
        assert result.service_name == "test_http"
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time > 0
        assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_unexpected_status(self):
        """Test handling of unexpected HTTP status"""
        checker = HTTPHealthChecker(
            service_name="test_http",
            url="http://httpbin.org/status/500",
            expected_status=200,
            timeout=5.0
        )
        
        result = await checker.check()
        
        assert result.status == HealthStatus.UNHEALTHY
        assert "unexpected status" in result.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_invalid_url(self):
        """Test handling of invalid URL"""
        checker = HTTPHealthChecker(
            service_name="test_http",
            url="http://invalid-url-that-does-not-exist:12345",
            expected_status=200,
            timeout=1.0
        )
        
        result = await checker.check()
        
        assert result.status == HealthStatus.UNHEALTHY
        assert result.error_message is not None


class TestRedisHealthChecker:
    """Test Redis health checker"""
    
    @pytest.mark.asyncio
    async def test_successful_redis_check(self):
        """Test successful Redis health check"""
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = "PONG"
        mock_redis.info.return_value = {
            "redis_version": "6.2.0",
            "used_memory_human": "1M",
            "connected_clients": 1
        }
        mock_redis.memory_usage.return_value = 100
        
        checker = RedisHealthChecker(
            service_name="test_redis",
            redis_client=mock_redis,
            timeout=1.0
        )
        
        result = await checker.check()
        
        assert result.service_name == "test_redis"
        assert result.status == HealthStatus.HEALTHY
        assert result.response_time > 0
        assert "ping" in result.details
        assert result.details["ping"] == "PONG"
    
    @pytest.mark.asyncio
    async def test_redis_connection_failure(self):
        """Test Redis connection failure"""
        # Mock Redis client that fails
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = Exception("Connection failed")
        
        checker = RedisHealthChecker(
            service_name="test_redis",
            redis_client=mock_redis,
            timeout=1.0
        )
        
        result = await checker.check()
        
        assert result.status == HealthStatus.UNHEALTHY
        assert "connection failed" in result.error_message.lower()


class TestDatabaseHealthChecker:
    """Test database health checker"""
    
    @pytest.mark.asyncio
    async def test_successful_database_check(self):
        """Test successful database health check"""
        # Mock database connection
        mock_conn = AsyncMock()
        mock_conn.fetchval.return_value = 1
        
        # Use MagicMock for the row to support __getitem__
        mock_row = MagicMock()
        mock_row.__getitem__.side_effect = lambda key: {
            "datname": "test_db",
            "numbackends": 1,
            "xact_commit": 100,
            "xact_rollback": 0,
            "blks_read": 50,
            "blks_hit": 950
        }[key]
        
        mock_conn.fetchrow.return_value = mock_row
        mock_conn.close = AsyncMock()
        
        with patch('asyncpg.connect', return_value=mock_conn):
            checker = DatabaseHealthChecker(
                service_name="test_db",
                connection_string="postgresql://user:pass@localhost/db",
                timeout=1.0
            )
            
            result = await checker.check()
            
            assert result.service_name == "test_db"
            assert result.status == HealthStatus.HEALTHY
            assert result.response_time > 0
            assert "connection_test" in result.details
            assert result.details["connection_test"] == 1
    
    @pytest.mark.asyncio
    async def test_database_connection_failure(self):
        """Test database connection failure"""
        with patch('asyncpg.connect', side_effect=Exception("Connection failed")):
            checker = DatabaseHealthChecker(
                service_name="test_db",
                connection_string="postgresql://user:pass@localhost/db",
                timeout=1.0
            )
            
            result = await checker.check()
            
            assert result.status == HealthStatus.UNHEALTHY
            assert "connection failed" in result.error_message.lower()


class TestCustomHealthChecker:
    """Test custom health checker"""
    
    @pytest.mark.asyncio
    async def test_custom_check_success(self):
        """Test successful custom health check"""
        async def custom_check():
            return {"custom": "check", "status": "ok"}
        
        checker = CustomHealthChecker(
            service_name="test_custom",
            check_func=custom_check,
            timeout=1.0
        )
        
        result = await checker.check()
        
        assert result.service_name == "test_custom"
        assert result.status == HealthStatus.HEALTHY
        assert result.details == {"custom": "check", "status": "ok"}
    
    @pytest.mark.asyncio
    async def test_custom_check_failure(self):
        """Test failed custom health check"""
        async def custom_check():
            raise Exception("Custom check failed")
        
        checker = CustomHealthChecker(
            service_name="test_custom",
            check_func=custom_check,
            timeout=1.0
        )
        
        result = await checker.check()
        
        assert result.status == HealthStatus.UNHEALTHY
        assert "custom check failed" in result.error_message.lower()


class TestHealthMonitor:
    """Test HealthMonitor functionality"""
    
    @pytest.fixture
    def health_monitor(self):
        """Create health monitor for testing"""
        return HealthMonitor(check_interval=0.1)  # Short interval for testing
    
    @pytest.fixture
    def mock_checker(self):
        """Create mock health checker"""
        checker = AsyncMock(spec=HealthChecker)
        checker.service_name = "mock_service"
        checker.check.return_value = HealthCheckResult(
            service_name="mock_service",
            status=HealthStatus.HEALTHY,
            response_time=0.1,
            details={"status": "ok"},
            timestamp=time.time()
        )
        return checker
    
    @pytest.mark.asyncio
    async def test_add_checker(self, health_monitor, mock_checker):
        """Test adding health checker"""
        health_monitor.add_checker(mock_checker)
        
        assert "mock_service" in health_monitor.checkers
        assert "mock_service" in health_monitor.health_states
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, health_monitor, mock_checker):
        """Test starting and stopping monitoring"""
        health_monitor.add_checker(mock_checker)
        
        # Start monitoring
        await health_monitor.start_monitoring()
        assert health_monitor._monitoring is True
        assert health_monitor._monitor_task is not None
        
        # Stop monitoring
        await health_monitor.stop_monitoring()
        assert health_monitor._monitoring is False
        assert health_monitor._monitor_task is None
    
    @pytest.mark.asyncio
    async def test_get_health_status(self, health_monitor, mock_checker):
        """Test getting health status"""
        health_monitor.add_checker(mock_checker)
        
        # Get single service status
        status = health_monitor.get_health_status("mock_service")
        assert status is not None
        assert status.name == "mock_service"
        
        # Get all services status
        all_status = health_monitor.get_health_status()
        assert "mock_service" in all_status
    
    @pytest.mark.asyncio
    async def test_get_health_report(self, health_monitor, mock_checker):
        """Test getting health report"""
        health_monitor.add_checker(mock_checker)
        
        report = health_monitor.get_health_report()
        
        assert "timestamp" in report
        assert "monitoring_active" in report
        assert "services" in report
        assert "summary" in report
        assert "mock_service" in report["services"]
    
    @pytest.mark.asyncio
    async def test_trigger_manual_check(self, health_monitor, mock_checker):
        """Test triggering manual health check"""
        health_monitor.add_checker(mock_checker)
        
        result = await health_monitor.trigger_manual_check("mock_service")
        
        assert result is not None
        assert result.service_name == "mock_service"
        assert result.status == HealthStatus.HEALTHY


class TestRecoveryManager:
    """Test RecoveryManager functionality"""
    
    @pytest.fixture
    def recovery_manager(self):
        """Create recovery manager for testing"""
        return RecoveryManager()
    
    @pytest.fixture
    def recovery_rule(self):
        """Create recovery rule for testing"""
        return RecoveryRule(
            service_name="test_service",
            failure_threshold=3,
            recovery_action=RecoveryAction.RESTART_SERVICE,
            retry_attempts=2,
            retry_delay=0.1,
            cooldown_period=1.0
        )
    
    @pytest.mark.asyncio
    async def test_add_recovery_rule(self, recovery_manager, recovery_rule):
        """Test adding recovery rule"""
        recovery_manager.add_recovery_rule(recovery_rule)
        
        assert "test_service" in recovery_manager.recovery_rules
        assert len(recovery_manager.recovery_rules["test_service"]) == 1
        assert recovery_manager.recovery_rules["test_service"][0] == recovery_rule
    
    @pytest.mark.asyncio
    async def test_handle_service_failure(self, recovery_manager, recovery_rule):
        """Test handling service failure"""
        recovery_manager.add_recovery_rule(recovery_rule)
        
        health_result = HealthCheckResult(
            service_name="test_service",
            status=HealthStatus.UNHEALTHY,
            response_time=0.5,
            details={"error": "service down"},
            timestamp=time.time(),
            error_message="Service unavailable"
        )
        
        # Should trigger recovery after 3 failures
        for i in range(3):
            await recovery_manager.handle_service_failure("test_service", health_result, i + 1)
        
        # Check recovery history
        history = recovery_manager.get_recovery_history("test_service")
        assert len(history) > 0
    
    @pytest.mark.asyncio
    async def test_recovery_stats(self, recovery_manager):
        """Test getting recovery statistics"""
        stats = recovery_manager.get_recovery_stats()
        
        assert "total_attempts" in stats
        assert "success_rate" in stats
        assert "average_recovery_time" in stats
        assert "actions_by_type" in stats
        assert "recent_failures" in stats
    
    @pytest.mark.asyncio
    async def test_cleanup_old_history(self, recovery_manager):
        """Test cleaning up old recovery history"""
        # Add some old recovery attempts
        old_attempt = RecoveryAttempt(
            service_name="test_service",
            action=RecoveryAction.RESTART_SERVICE,
            attempt_number=1,
            timestamp=time.time() - 7200,  # 2 hours ago
            success=True
        )
        recovery_manager.recovery_history.append(old_attempt)
        
        # Cleanup old history
        await recovery_manager.cleanup_old_history(max_age_hours=1)
        
        # Old attempt should be removed
        history = recovery_manager.get_recovery_history()
        assert len(history) == 0


class TestRecoveryActions:
    """Test specific recovery actions"""
    
    @pytest.mark.asyncio
    async def test_restart_service_success(self):
        """Test successful service restart"""
        recovery_manager = RecoveryManager()
        
        # Mock successful restart
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b"Restarted", b"")
            mock_subprocess.return_value = mock_process
            
            success = await recovery_manager._restart_service("test_service")
            
            assert success is True
    
    @pytest.mark.asyncio
    async def test_restart_service_failure(self):
        """Test failed service restart"""
        recovery_manager = RecoveryManager()
        
        # Mock failed restart
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.communicate.return_value = (b"", b"Error")
            mock_subprocess.return_value = mock_process
            
            success = await recovery_manager._restart_service("test_service")
            
            assert success is False


class TestFactoryFunctions:
    """Test factory functions for health checkers"""
    
    def test_create_rag_api_health_checker(self):
        """Test creating RAG API health checker"""
        checker = create_rag_api_health_checker("http://localhost:8000")
        
        assert checker.service_name == "rag_api"
        assert checker.url == "http://localhost:8000/health"
        assert checker.expected_status == 200
    
    def test_create_chainlit_ui_health_checker(self):
        """Test creating Chainlit UI health checker"""
        checker = create_chainlit_ui_health_checker("http://localhost:8001")
        
        assert checker.service_name == "chainlit_ui"
        assert checker.url == "http://localhost:8001/health"
        assert checker.expected_status == 200
    
    def test_create_redis_health_checker(self):
        """Test creating Redis health checker"""
        mock_redis = Mock()
        checker = create_redis_health_checker(mock_redis)
        
        assert checker.service_name == "redis"
        assert checker.redis_client == mock_redis
    
    def test_create_vikunja_health_checker(self):
        """Test creating Vikunja health checker"""
        checker = create_vikunja_health_checker("http://localhost:3456")
        
        assert checker.service_name == "vikunja"
        assert checker.url == "http://localhost:3456/api/v1/info"
        assert checker.expected_status == 200
    
    def test_create_caddy_health_checker(self):
        """Test creating Caddy health checker"""
        checker = create_caddy_health_checker("http://localhost:8000")
        
        assert checker.service_name == "caddy"
        assert checker.url == "http://localhost:8000/health"
        assert checker.expected_status == 200


class TestHealthMonitorIntegration:
    """Integration tests for health monitoring"""
    
    @pytest.mark.asyncio
    async def test_monitoring_with_multiple_services(self):
        """Test monitoring multiple services"""
        monitor = HealthMonitor(check_interval=0.1)
        
        # Create mock checkers
        checker1 = AsyncMock(spec=HealthChecker)
        checker1.service_name = "service1"
        checker1.check.return_value = HealthCheckResult(
            service_name="service1",
            status=HealthStatus.HEALTHY,
            response_time=0.1,
            details={"status": "ok"},
            timestamp=time.time()
        )
        
        checker2 = AsyncMock(spec=HealthChecker)
        checker2.service_name = "service2"
        checker2.check.return_value = HealthCheckResult(
            service_name="service2",
            status=HealthStatus.HEALTHY,
            response_time=0.2,
            details={"status": "ok"},
            timestamp=time.time()
        )
        
        monitor.add_checker(checker1)
        monitor.add_checker(checker2)
        
        # Start monitoring
        await monitor.start_monitoring()
        await asyncio.sleep(0.3)  # Run for a short time
        await monitor.stop_monitoring()
        
        # Check that both services were checked
        assert checker1.check.call_count > 0
        assert checker2.check.call_count > 0
    
    @pytest.mark.asyncio
    async def test_health_callback_integration(self):
        """Test health status callback integration"""
        monitor = HealthMonitor(check_interval=0.1)
        
        callback_called = False
        callback_args = []
        
        async def health_callback(service_name, old_status, new_status, result):
            nonlocal callback_called, callback_args
            callback_called = True
            callback_args = [service_name, old_status, new_status, result]
        
        monitor.add_health_callback("test_service", health_callback)
        
        # Create checker that fails
        checker = AsyncMock(spec=HealthChecker)
        checker.service_name = "test_service"
        checker.check.return_value = HealthCheckResult(
            service_name="test_service",
            status=HealthStatus.UNHEALTHY,
            response_time=0.1,
            details={"error": "failed"},
            timestamp=time.time(),
            error_message="Service failed"
        )
        
        monitor.add_checker(checker)
        
        # Start monitoring
        await monitor.start_monitoring()
        await asyncio.sleep(0.2)
        await monitor.stop_monitoring()
        
        # Check callback was called
        assert callback_called is True
        assert callback_args[0] == "test_service"
        assert callback_args[2] == HealthStatus.UNHEALTHY


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
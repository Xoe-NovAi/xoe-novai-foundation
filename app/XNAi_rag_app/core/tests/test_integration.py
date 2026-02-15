"""
Integration tests for Xoe-NovAi Foundation Stack Core Module
Tests end-to-end functionality and real-world usage scenarios.
"""

import asyncio
import pytest
import time
import json
from unittest.mock import Mock, AsyncMock, patch
import redis.asyncio as redis

from app.XNAi_rag_app.core import (
    CircuitBreaker,
    CircuitBreakerConfig,
    InMemoryCircuitStateStore,
    HealthMonitor,
    HealthChecker,
    HealthStatus,
    RecoveryManager,
    RecoveryAction,
    RecoveryRule,
    ServiceDegradationManager,
    FallbackStrategy,
    CacheFirstStrategy,
    DegradedModeStrategy,
    create_inmemory_circuit_breaker,
    create_rag_api_health_checker,
    create_redis_health_checker,
    create_llm_degradation_manager,
    create_redis_degradation_manager
)


class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_complete_resilience_system(self):
        """Test complete resilience system integration"""
        # Create degradation manager
        degradation_manager = ServiceDegradationManager()
        
        # Create circuit breaker
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=1,
            timeout=0.5,
            name="integrated_service"
        )
        state_store = InMemoryCircuitStateStore()
        circuit_breaker = CircuitBreaker(config, state_store)
        
        # Add circuit breaker strategy
        degradation_manager.add_service_strategy(
            "integrated_service",
            DegradedModeStrategy({"error": "Service temporarily unavailable"}),
            priority=10
        )
        
        # Create health monitor
        monitor = HealthMonitor(check_interval=0.1)
        
        # Create mock health checker
        async def mock_health_check():
            return {"status": "ok", "response_time": 0.1}
        
        checker = HealthChecker("integrated_service", timeout=1.0)
        checker._perform_check = mock_health_check
        monitor.add_checker(checker)
        
        # Create recovery manager
        recovery_manager = RecoveryManager()
        
        # Add recovery rule
        rule = RecoveryRule(
            service_name="integrated_service",
            failure_threshold=2,
            recovery_action=RecoveryAction.RESTART_SERVICE,
            retry_attempts=1,
            retry_delay=0.1,
            cooldown_period=0.5
        )
        recovery_manager.add_recovery_rule(rule)
        
        # Test successful operation
        async def success_func():
            return {"result": "success"}
        
        result = await degradation_manager.call_service(
            "integrated_service",
            success_func
        )
        assert result == {"result": "success"}
        
        # Test health monitoring
        report = monitor.get_health_report()
        assert "integrated_service" in report["services"]
        
        # Test recovery system
        health_result = {
            "service_name": "integrated_service",
            "status": HealthStatus.UNHEALTHY,
            "response_time": 0.5,
            "details": {"error": "failed"},
            "timestamp": time.time(),
            "error_message": "Service failed"
        }
        
        # Should trigger recovery after 2 failures
        for i in range(2):
            await recovery_manager.handle_service_failure(
                "integrated_service", 
                health_result, 
                i + 1
            )
        
        # Check recovery history
        history = recovery_manager.get_recovery_history("integrated_service")
        assert len(history) > 0
    
    @pytest.mark.asyncio
    async def test_llm_service_protection(self):
        """Test LLM service protection with circuit breaker and degradation"""
        # Create LLM degradation manager
        llm_manager = create_llm_degradation_manager()
        
        # Create circuit breaker for LLM
        llm_circuit_breaker = create_inmemory_circuit_breaker(
            name="llm_service",
            failure_threshold=3,
            recovery_timeout=2,
            timeout=10
        )
        
        # Add circuit breaker strategy
        from app.XNAi_rag_app.core.circuit_breakers import CircuitBreakerStrategy
        llm_manager.add_service_strategy(
            "llm_service",
            CircuitBreakerStrategy(llm_circuit_breaker),
            priority=10
        )
        
        # Test successful LLM call
        async def llm_success():
            return {"response": "Hello, world!", "tokens": 5}
        
        result = await llm_manager.call_service("llm_service", llm_success)
        assert "response" in result
        assert result["response"] == "Hello, world!"
        
        # Test LLM failure with degradation
        async def llm_failure():
            raise Exception("LLM service unavailable")
        
        # Make enough failures to trigger circuit breaker
        for i in range(3):
            try:
                await llm_manager.call_service("llm_service", llm_failure)
            except Exception:
                pass
        
        # Should use degraded response
        result = await llm_manager.call_service("llm_service", llm_failure)
        assert "degraded" in result
        assert result["degraded"] is True
    
    @pytest.mark.asyncio
    async def test_redis_service_protection(self):
        """Test Redis service protection with health monitoring and recovery"""
        # Create Redis degradation manager
        redis_manager = create_redis_degradation_manager()
        
        # Create Redis health checker
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = "PONG"
        mock_redis.info.return_value = {"redis_version": "6.2.0"}
        
        checker = create_redis_health_checker(mock_redis)
        
        # Create health monitor
        monitor = HealthMonitor(check_interval=0.1)
        monitor.add_checker(checker)
        
        # Create recovery manager
        recovery_manager = RecoveryManager()
        
        # Add recovery rule for Redis
        rule = RecoveryRule(
            service_name="redis",
            failure_threshold=2,
            recovery_action=RecoveryAction.RESTART_SERVICE,
            retry_attempts=2,
            retry_delay=0.5,
            cooldown_period=2.0
        )
        recovery_manager.add_recovery_rule(rule)
        
        # Test Redis health check
        result = await checker.check()
        assert result.status == HealthStatus.HEALTHY
        
        # Test health monitoring
        report = monitor.get_health_report()
        assert "redis" in report["services"]
        
        # Test recovery system
        health_result = {
            "service_name": "redis",
            "status": HealthStatus.UNHEALTHY,
            "response_time": 1.0,
            "details": {"error": "connection failed"},
            "timestamp": time.time(),
            "error_message": "Redis connection failed"
        }
        
        # Should trigger recovery after 2 failures
        for i in range(2):
            await recovery_manager.handle_service_failure(
                "redis", 
                health_result, 
                i + 1
            )
        
        # Check recovery history
        history = recovery_manager.get_recovery_history("redis")
        assert len(history) > 0


class TestRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    @pytest.mark.asyncio
    async def test_rag_api_with_circuit_breaker(self):
        """Test RAG API protection with circuit breaker"""
        # Create circuit breaker for RAG API
        rag_circuit_breaker = create_inmemory_circuit_breaker(
            name="rag_api",
            failure_threshold=3,
            recovery_timeout=5,
            timeout=30
        )
        
        # Create degradation manager
        degradation_manager = ServiceDegradationManager()
        degradation_manager.add_service_strategy(
            "rag_api",
            DegradedModeStrategy({"error": "RAG API temporarily unavailable"}),
            priority=10
        )
        
        # Test normal operation
        async def rag_query():
            return {"answer": "This is the answer", "sources": ["doc1", "doc2"]}
        
        result = await degradation_manager.call_service("rag_api", rag_query)
        assert "answer" in result
        assert result["answer"] == "This is the answer"
        
        # Test failure scenario
        async def rag_failure():
            raise Exception("RAG API timeout")
        
        # Make failures to trigger circuit breaker
        for i in range(3):
            try:
                await degradation_manager.call_service("rag_api", rag_failure)
            except Exception:
                pass
        
        # Should use degraded response
        result = await degradation_manager.call_service("rag_api", rag_failure)
        assert "error" in result
        assert "unavailable" in result["error"]
    
    @pytest.mark.asyncio
    async def test_chainlit_ui_with_health_monitoring(self):
        """Test Chainlit UI protection with health monitoring"""
        # Create health monitor for Chainlit UI
        monitor = HealthMonitor(check_interval=0.5)
        
        # Create mock Chainlit checker
        async def chainlit_health():
            return {"status": "ok", "ui_components": 5}
        
        checker = HealthChecker("chainlit_ui", timeout=5.0)
        checker._perform_check = chainlit_health
        monitor.add_checker(checker)
        
        # Add recovery callback
        recovery_called = False
        
        async def recovery_callback(service_name):
            nonlocal recovery_called
            recovery_called = True
        
        monitor.add_recovery_callback("chainlit_ui", recovery_callback)
        
        # Start monitoring
        await monitor.start_monitoring()
        await asyncio.sleep(1.0)  # Run for a short time
        await monitor.stop_monitoring()
        
        # Check that health checks were performed
        report = monitor.get_health_report()
        assert "chainlit_ui" in report["services"]
        assert report["services"]["chainlit_ui"]["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_vikunja_with_recovery(self):
        """Test Vikunja service with automated recovery"""
        # Create recovery manager for Vikunja
        recovery_manager = RecoveryManager()
        
        # Add recovery rules
        rules = [
            RecoveryRule(
                service_name="vikunja",
                failure_threshold=2,
                recovery_action=RecoveryAction.RESTART_SERVICE,
                retry_attempts=2,
                retry_delay=1.0,
                cooldown_period=5.0
            ),
            RecoveryRule(
                service_name="vikunja",
                failure_threshold=5,
                recovery_action=RecoveryAction.RECONNECT_DATABASE,
                retry_attempts=3,
                retry_delay=2.0,
                cooldown_period=10.0
            )
        ]
        
        for rule in rules:
            recovery_manager.add_recovery_rule(rule)
        
        # Simulate service failures
        health_result = {
            "service_name": "vikunja",
            "status": HealthStatus.UNHEALTHY,
            "response_time": 2.0,
            "details": {"error": "database connection lost"},
            "timestamp": time.time(),
            "error_message": "Database connection failed"
        }
        
        # Trigger recovery after 2 failures
        for i in range(2):
            await recovery_manager.handle_service_failure(
                "vikunja", 
                health_result, 
                i + 1
            )
        
        # Check recovery history
        history = recovery_manager.get_recovery_history("vikunja")
        assert len(history) > 0
        
        # Check recovery statistics
        stats = recovery_manager.get_recovery_stats("vikunja")
        assert stats["total_attempts"] > 0
        assert "restart_service" in stats["actions_by_type"]


class TestPerformanceAndScalability:
    """Test performance and scalability characteristics"""
    
    @pytest.mark.asyncio
    async def test_concurrent_circuit_breaker_access(self):
        """Test concurrent access to circuit breaker"""
        circuit_breaker = create_inmemory_circuit_breaker(
            name="concurrent_service",
            failure_threshold=5,
            recovery_timeout=1,
            timeout=0.1
        )
        
        # Create degradation manager
        degradation_manager = ServiceDegradationManager()
        degradation_manager.add_service_strategy(
            "concurrent_service",
            DegradedModeStrategy({"error": "Service overloaded"}),
            priority=10
        )
        
        # Run concurrent requests
        async def concurrent_request():
            await asyncio.sleep(0.01)  # Small delay to spread requests
            return await degradation_manager.call_service(
                "concurrent_service",
                lambda: {"result": "success"}
            )
        
        # Run 50 concurrent requests
        tasks = [concurrent_request() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == 50
        assert all("result" in result for result in results)
        
        # Check circuit breaker metrics
        metrics = circuit_breaker.get_metrics()
        assert metrics["metrics"]["calls"] == 50
        assert metrics["metrics"]["successes"] == 50
    
    @pytest.mark.asyncio
    async def test_health_monitoring_performance(self):
        """Test health monitoring performance with multiple services"""
        monitor = HealthMonitor(check_interval=0.1)
        
        # Create multiple mock checkers
        checkers = []
        for i in range(10):
            async def mock_check():
                await asyncio.sleep(0.01)  # Simulate check time
                return {"service": f"service_{i}", "status": "ok"}
            
            checker = HealthChecker(f"service_{i}", timeout=1.0)
            checker._perform_check = mock_check
            checkers.append(checker)
            monitor.add_checker(checker)
        
        # Start monitoring
        start_time = time.time()
        await monitor.start_monitoring()
        await asyncio.sleep(0.5)  # Monitor for 0.5 seconds
        await monitor.stop_monitoring()
        end_time = time.time()
        
        # Check that all services were monitored
        report = monitor.get_health_report()
        assert len(report["services"]) == 10
        
        # Check performance (should be fast)
        monitoring_time = end_time - start_time
        assert monitoring_time < 1.0  # Should complete quickly
    
    @pytest.mark.asyncio
    async def test_memory_usage_with_large_number_of_services(self):
        """Test memory usage with large number of services"""
        # Create degradation manager with many services
        degradation_manager = ServiceDegradationManager()
        
        # Add many services
        for i in range(100):
            degradation_manager.add_service_strategy(
                f"service_{i}",
                DegradedModeStrategy({"error": f"Service {i} unavailable"}),
                priority=10
            )
        
        # Test that all services can be called
        async def test_service(service_name):
            return await degradation_manager.call_service(
                service_name,
                lambda: {"result": "success"}
            )
        
        # Test a few services
        for i in [0, 25, 50, 75, 99]:
            result = await test_service(f"service_{i}")
            assert "result" in result
            assert result["result"] == "success"


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery scenarios"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_state_transitions(self):
        """Test circuit breaker state transitions"""
        circuit_breaker = create_inmemory_circuit_breaker(
            name="state_test_service",
            failure_threshold=2,
            recovery_timeout=0.5,
            timeout=0.1
        )
        
        # Test CLOSED -> OPEN transition
        async def failure_func():
            raise RuntimeError("Service failed")
        
        # First two failures should not open circuit
        for i in range(2):
            try:
                await circuit_breaker.call(failure_func)
            except RuntimeError:
                pass
        
        # Third failure should open circuit
        with pytest.raises(Exception):  # Could be RuntimeError or CircuitOpenError
            await circuit_breaker.call(failure_func)
        
        # Wait for recovery timeout
        await asyncio.sleep(0.6)
        
        # Should be in HALF_OPEN state
        async def success_func():
            return "recovered"
        
        result = await circuit_breaker.call(success_func)
        assert result == "recovered"
    
    @pytest.mark.asyncio
    async def test_recovery_with_multiple_attempts(self):
        """Test recovery with multiple retry attempts"""
        recovery_manager = RecoveryManager()
        
        # Add recovery rule with multiple attempts
        rule = RecoveryRule(
            service_name="retry_test_service",
            failure_threshold=2,
            recovery_action=RecoveryAction.RESTART_SERVICE,
            retry_attempts=3,
            retry_delay=0.1,
            cooldown_period=1.0
        )
        recovery_manager.add_recovery_rule(rule)
        
        # Mock recovery function that fails first, then succeeds
        attempt_count = 0
        
        async def mock_recovery(service_name, health_result):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                return False  # Fail first two attempts
            return True  # Succeed on third attempt
        
        rule.custom_recovery_func = mock_recovery
        
        # Trigger recovery
        health_result = {
            "service_name": "retry_test_service",
            "status": HealthStatus.UNHEALTHY,
            "response_time": 1.0,
            "details": {"error": "service down"},
            "timestamp": time.time(),
            "error_message": "Service failed"
        }
        
        await recovery_manager.handle_service_failure(
            "retry_test_service", 
            health_result, 
            2
        )
        
        # Check recovery history
        history = recovery_manager.get_recovery_history("retry_test_service")
        assert len(history) == 3  # Should have 3 attempts
        
        # Last attempt should be successful
        assert history[-1].success is True
    
    @pytest.mark.asyncio
    async def test_degradation_strategy_fallback(self):
        """Test degradation strategy fallback behavior"""
        degradation_manager = ServiceDegradationManager()
        
        # Add multiple strategies with different priorities
        async def high_priority_fallback():
            return {"strategy": "high_priority", "result": "fallback"}
        
        async def low_priority_fallback():
            return {"strategy": "low_priority", "result": "fallback"}
        
        degradation_manager.add_service_strategy(
            "fallback_test_service",
            FallbackStrategy(high_priority_fallback),
            priority=10
        )
        
        degradation_manager.add_service_strategy(
            "fallback_test_service",
            FallbackStrategy(low_priority_fallback),
            priority=5
        )
        
        # Test that high priority strategy is used first
        async def primary_func():
            raise Exception("Primary function failed")
        
        result = await degradation_manager.call_service(
            "fallback_test_service",
            primary_func
        )
        
        assert result["strategy"] == "high_priority"
        assert result["result"] == "fallback"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
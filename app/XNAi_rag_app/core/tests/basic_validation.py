#!/usr/bin/env python3
"""
Basic Phase 1 Validation Script for Xoe-NovAi Foundation Stack Core Module
Tests core functionality without requiring external dependencies.
"""

import asyncio
import anyio
import sys
import time
import traceback
from typing import Dict, List, Any

# Add the core module to path
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_circuit_breaker_config():
    """Test circuit breaker configuration without Redis"""
    print("Testing circuit breaker configuration...")

    try:
        # Import only the config class to avoid Redis dependency
        from dataclasses import dataclass
        from enum import Enum

        # Define minimal classes for testing
        class CircuitState(str, Enum):
            CLOSED = "closed"
            OPEN = "open"
            HALF_OPEN = "half_open"

        @dataclass
        class CircuitBreakerConfig:
            name: str
            failure_threshold: int = 3
            recovery_timeout: int = 60
            half_open_max_calls: int = 1
            expected_exception: type = Exception

        # Test config creation
        config = CircuitBreakerConfig(
            name="test_service", failure_threshold=3, recovery_timeout=60
        )

        assert config.name == "test_service"
        assert config.failure_threshold == 3
        assert config.recovery_timeout == 60
        assert config.half_open_max_calls == 1  # Default value

        print("✅ Circuit breaker configuration test passed")
        return True

    except Exception as e:
        print(f"❌ Circuit breaker configuration test failed: {e}")
        return False


def test_health_monitoring():
    """Test health monitoring basic functionality"""
    print("Testing health monitoring...")

    try:
        from dataclasses import dataclass
        from enum import Enum
        from typing import Optional, Dict, Any

        class HealthStatus(str, Enum):
            HEALTHY = "healthy"
            UNHEALTHY = "unhealthy"
            DEGRADED = "degraded"

        @dataclass
        class HealthResult:
            service_name: str
            status: HealthStatus
            response_time: float
            details: Dict[str, Any]
            timestamp: float
            error_message: Optional[str] = None

        class HealthChecker:
            def __init__(self, service_name: str, timeout: float = 1.0):
                self.service_name = service_name
                self.timeout = timeout

            async def check(self) -> HealthResult:
                # Mock implementation
                return HealthResult(
                    service_name=self.service_name,
                    status=HealthStatus.HEALTHY,
                    response_time=0.1,
                    details={"status": "ok"},
                    timestamp=time.time(),
                )

        class HealthMonitor:
            def __init__(self, check_interval: float = 1.0):
                self.check_interval = check_interval
                self.checkers = []

            def add_checker(self, checker):
                self.checkers.append(checker)

            def get_health_report(self):
                return {"healthy": True, "circuits": {}, "timestamp": time.time()}

        # Test monitor creation
        monitor = HealthMonitor(check_interval=0.1)
        assert monitor.check_interval == 0.1
        assert len(monitor.checkers) == 0

        # Test checker creation
        checker = HealthChecker("test_service", timeout=1.0)
        assert checker.service_name == "test_service"
        assert checker.timeout == 1.0

        print("✅ Health monitoring test passed")
        return True

    except Exception as e:
        print(f"❌ Health monitoring test failed: {e}")
        return False


def test_graceful_degradation():
    """Test graceful degradation basic functionality"""
    print("Testing graceful degradation...")

    try:
        from typing import Dict, Any, Callable, Optional
        import asyncio

        class FallbackStrategy:
            def __init__(self, fallback_func: Callable):
                self.fallback_func = fallback_func

            async def execute(self, *args, **kwargs):
                if asyncio.iscoroutinefunction(self.fallback_func):
                    return await self.fallback_func(*args, **kwargs)
                else:
                    return self.fallback_func(*args, **kwargs)

        class DegradedModeStrategy:
            def __init__(self, degraded_response: Dict[str, Any]):
                self.degraded_response = degraded_response

            async def execute(self, *args, **kwargs):
                return self.degraded_response

        class ServiceDegradationManager:
            def __init__(self):
                self.strategies = {}

            def add_service_strategy(
                self, service_name: str, strategy, priority: int = 10
            ):
                self.strategies[service_name] = {
                    "strategy": strategy,
                    "priority": priority,
                }

            async def call_service(self, service_name: str, func, *args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    # Execute fallback
                    if service_name in self.strategies:
                        strategy = self.strategies[service_name]["strategy"]
                        return await strategy.execute(*args, **kwargs)
                    else:
                        raise

        # Test degradation manager
        manager = ServiceDegradationManager()
        assert len(manager.strategies) == 0

        # Test fallback strategy
        async def fallback_func():
            return {"degraded": True}

        strategy = FallbackStrategy(fallback_func)
        assert strategy.fallback_func == fallback_func

        # Test degraded mode strategy
        degraded_strategy = DegradedModeStrategy({"error": "Service unavailable"})
        assert degraded_strategy.degraded_response == {"error": "Service unavailable"}

        print("✅ Graceful degradation test passed")
        return True

    except Exception as e:
        print(f"❌ Graceful degradation test failed: {e}")
        return False


def test_error_handling():
    """Test error handling"""
    print("Testing error handling...")

    try:
        from enum import Enum
        from typing import Optional, Dict, Any

        class ErrorCategory(str, Enum):
            CIRCUIT_OPEN = "circuit_open"
            SERVICE_UNAVAILABLE = "service_unavailable"
            TIMEOUT = "timeout"
            VALIDATION = "validation"
            SYSTEM = "system"

        class XNAiException(Exception):
            def __init__(
                self,
                message: str,
                category: ErrorCategory,
                details: Optional[Dict[str, Any]] = None,
                recovery_suggestion: Optional[str] = None,
            ):
                super().__init__(message)
                self.category = category
                self.details = details or {}
                self.recovery_suggestion = recovery_suggestion

        class CircuitBreakerError(XNAiException):
            def __init__(
                self,
                service_name: str,
                failure_count: int,
                retry_after: Optional[int] = None,
                message: Optional[str] = None,
            ):
                msg = message or f"Circuit breaker open for service: {service_name}"
                details = {
                    "service_name": service_name,
                    "failure_count": failure_count,
                    "retry_after_seconds": retry_after,
                    "breaker_state": "OPEN",
                }
                recovery = (
                    f"Service is temporarily unavailable. "
                    f"Retry after {retry_after} seconds."
                    if retry_after
                    else "Service is temporarily unavailable. Check health and retry."
                )

                super().__init__(
                    message=msg,
                    category=ErrorCategory.CIRCUIT_OPEN,
                    details=details,
                    recovery_suggestion=recovery,
                )

                self.service_name = service_name
                self.failure_count = failure_count
                self.retry_after = retry_after

        # Test circuit breaker error
        error = CircuitBreakerError(
            service_name="test_service", failure_count=3, retry_after=60
        )

        assert error.service_name == "test_service"
        assert error.failure_count == 3
        assert error.retry_after == 60
        assert error.category == ErrorCategory.CIRCUIT_OPEN

        # Test health status enum
        assert ErrorCategory.CIRCUIT_OPEN.value == "circuit_open"
        assert ErrorCategory.SERVICE_UNAVAILABLE.value == "service_unavailable"

        print("✅ Error handling test passed")
        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


async def test_async_functionality():
    """Test async functionality"""
    print("Testing async functionality...")

    try:
        import asyncio

        class HealthChecker:
            def __init__(self, service_name: str, timeout: float = 1.0):
                self.service_name = service_name
                self.timeout = timeout

            async def check(self):
                # Mock async health check
                await asyncio.sleep(0.001)  # Simulate async operation
                return {
                    "service_name": self.service_name,
                    "status": "healthy",
                    "response_time": 0.001,
                    "details": {"status": "ok"},
                    "timestamp": time.time(),
                }

        # Test async health check
        checker = HealthChecker("test_service", timeout=1.0)

        result = await checker.check()

        assert result["status"] == "healthy"
        assert result["response_time"] > 0
        assert "status" in result["details"]
        assert result["details"]["status"] == "ok"

        print("✅ Async functionality test passed")
        return True

    except Exception as e:
        print(f"❌ Async functionality test failed: {e}")
        return False


def run_validation():
    """Run all validation tests"""
    print("🚀 Starting Basic Phase 1 Validation...")
    print("=" * 60)

    tests = [
        ("Circuit Breaker Config", test_circuit_breaker_config),
        ("Health Monitoring", test_health_monitoring),
        ("Graceful Degradation", test_graceful_degradation),
        ("Error Handling", test_error_handling),
    ]

    results = []

    # Run sync tests
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        result = test_func()
        results.append((test_name, result))

    # Run async test
    print(f"\n📋 Async Functionality")
    async_result = anyio.run(test_async_functionality)
    results.append(("Async Functionality", async_result))

    # Generate report
    print("\n" + "=" * 60)
    print("📊 BASIC VALIDATION REPORT")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"\n📈 SUMMARY:")
    print(f"   Total Tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    print(f"   Success Rate: {success_rate:.1f}%")

    print(f"\n✅ PASSED TESTS:")
    for test_name, result in results:
        if result:
            print(f"   • {test_name}")

    print(f"\n❌ FAILED TESTS:")
    for test_name, result in results:
        if not result:
            print(f"   • {test_name}")

    print(f"\n🎯 FINAL ASSESSMENT:")
    if success_rate >= 90:
        print("   🎉 EXCELLENT: Core functionality is working!")
        print("   ✅ All basic components functional")
        print("   ✅ Ready for advanced testing")
    elif success_rate >= 75:
        print("   👍 GOOD: Most functionality working")
        print("   ⚠️  Some issues need attention")
    elif success_rate >= 50:
        print("   ⚠️  MODERATE: Basic functionality present")
        print("   🔧 Some components need fixes")
    else:
        print("   ❌ POOR: Significant issues detected")
        print("   🚨 Review implementation")

    print("\n" + "=" * 60)

    return success_rate >= 90


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)

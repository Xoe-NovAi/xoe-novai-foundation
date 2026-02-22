#!/usr/bin/env python3
"""
Simple Phase 1 Validation Script for Xoe-NovAi Foundation Stack Core Module
Tests basic functionality without requiring Redis or complex dependencies.
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


def test_basic_imports():
    """Test that all core modules can be imported"""
    print("Testing basic imports...")

    try:
        # Test circuit breakers
        from circuit_breakers import (
            CircuitBreakerConfig,
            CircuitBreakerError,
            CircuitState,
        )

        print("✅ Circuit breaker imports successful")

        # Test health monitoring
        from health import HealthMonitor, HealthChecker, HealthStatus, RecoveryManager

        print("✅ Health monitoring imports successful")

        # Test graceful degradation
        from circuit_breakers.graceful_degradation import (
            ServiceDegradationManager,
            FallbackStrategy,
            DegradedModeStrategy,
        )

        print("✅ Graceful degradation imports successful")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_circuit_breaker_config():
    """Test circuit breaker configuration"""
    print("Testing circuit breaker configuration...")

    try:
        from circuit_breakers import CircuitBreakerConfig, CircuitState

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
        from health import HealthMonitor, HealthChecker, HealthStatus

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
        from circuit_breakers.graceful_degradation import (
            ServiceDegradationManager,
            FallbackStrategy,
            DegradedModeStrategy,
        )

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
        from circuit_breakers import CircuitBreakerError
        from health import HealthStatus

        # Test circuit breaker error
        error = CircuitBreakerError(
            service_name="test_service", failure_count=3, retry_after=60
        )

        assert error.service_name == "test_service"
        assert error.failure_count == 3
        assert error.retry_after == 60

        # Test health status enum
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.DEGRADED.value == "degraded"

        print("✅ Error handling test passed")
        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


async def test_async_functionality():
    """Test async functionality"""
    print("Testing async functionality...")

    try:
        from health import HealthChecker, HealthStatus

        # Test async health check
        async def mock_health_check():
            await asyncio.sleep(0.001)  # Simulate async operation
            return {"status": "ok", "response_time": 0.001}

        checker = HealthChecker("test_service", timeout=1.0)
        checker._perform_check = mock_health_check

        result = await checker.check()

        assert result.status == HealthStatus.HEALTHY
        assert result.response_time > 0
        assert "status" in result.details
        assert result.details["status"] == "ok"

        print("✅ Async functionality test passed")
        return True

    except Exception as e:
        print(f"❌ Async functionality test failed: {e}")
        return False


def run_validation():
    """Run all validation tests"""
    print("🚀 Starting Simple Phase 1 Validation...")
    print("=" * 60)

    tests = [
        ("Basic Imports", test_basic_imports),
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
    print("📊 SIMPLE VALIDATION REPORT")
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

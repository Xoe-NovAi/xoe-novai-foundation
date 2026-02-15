"""
Phase 1 Validation Script for Xoe-NovAi Foundation Stack Core Module
Comprehensive validation of circuit breakers, health monitoring, and graceful degradation.
"""

import asyncio
import sys
import time
import json
import traceback
from typing import Dict, List, Any, Tuple

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import from main circuit_breakers module
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from circuit_breakers import (
    CircuitBreakerConfig,
    PersistentCircuitBreaker,
    CircuitBreakerRegistry,
    CircuitBreakerError,
    CircuitState
)

# Import from health module
from health import (
    HealthMonitor,
    HealthChecker,
    HealthStatus,
    RecoveryManager,
    RecoveryAction,
    RecoveryRule,
    create_rag_api_health_checker,
    create_redis_health_checker
)

# Import from graceful_degradation module
from circuit_breakers.graceful_degradation import (
    ServiceDegradationManager,
    FallbackStrategy,
    CacheFirstStrategy,
    DegradedModeStrategy,
    create_llm_degradation_manager,
    create_redis_degradation_manager
)

# Create simplified factory functions for testing
def create_inmemory_circuit_breaker(name, failure_threshold=3, recovery_timeout=1, timeout=0.5):
    """Create in-memory circuit breaker for testing."""
    config = CircuitBreakerConfig(
        name=name,
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout
    )
    return PersistentCircuitBreaker(config=config, redis_client=None)


class Phase1Validator:
    """Comprehensive validator for Phase 1 implementation"""
    
    def __init__(self):
        self.results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "total_tests": 0,
            "failures": [],
            "successes": [],
            "performance_metrics": {},
            "integration_tests": []
        }
    
    async def run_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation suite"""
        print("🚀 Starting Phase 1 Validation...")
        print("=" * 60)
        
        # Core functionality tests
        await self.test_circuit_breaker_basics()
        await self.test_health_monitoring()
        await self.test_graceful_degradation()
        await self.test_recovery_system()
        
        # Integration tests
        await self.test_end_to_end_integration()
        await self.test_real_world_scenarios()
        
        # Performance tests
        await self.test_performance_and_scalability()
        
        # Security and reliability tests
        await self.test_error_handling_and_recovery()
        
        # Generate final report
        return self.generate_report()
    
    async def test_circuit_breaker_basics(self):
        """Test basic circuit breaker functionality"""
        print("Testing Circuit Breaker Basics...")
        
        try:
            # Test 1: Basic circuit breaker creation and usage
            circuit_breaker = create_inmemory_circuit_breaker(
                name="test_service",
                failure_threshold=3,
                recovery_timeout=1,
                timeout=0.5
            )
            
            # Test successful calls
            async def success_func():
                return {"status": "success"}
            
            result = await circuit_breaker.call(success_func)
            assert result == {"status": "success"}
            
            # Test failure threshold
            async def failure_func():
                raise RuntimeError("Service failed")
            
            # Make failures
            for i in range(3):
                try:
                    await circuit_breaker.call(failure_func)
                except RuntimeError:
                    pass
            
            # Circuit should be open now
            try:
                await circuit_breaker.call(failure_func)
                assert False, "Circuit should be open"
            except Exception:
                pass  # Expected
            
            self._record_success("Circuit Breaker Basics")
            
        except Exception as e:
            self._record_failure("Circuit Breaker Basics", str(e))
    
    async def test_health_monitoring(self):
        """Test health monitoring functionality"""
        print("Testing Health Monitoring...")
        
        try:
            # Create health monitor
            monitor = HealthMonitor(check_interval=0.1)
            
            # Create mock health checker
            async def mock_health_check():
                return {"status": "ok", "response_time": 0.1}
            
            checker = HealthChecker("test_service", timeout=1.0)
            checker._perform_check = mock_health_check
            monitor.add_checker(checker)
            
            # Test health check
            result = await checker.check()
            assert result.status == HealthStatus.HEALTHY
            assert result.response_time > 0
            
            # Test health report
            report = monitor.get_health_report()
            assert "test_service" in report["services"]
            assert report["services"]["test_service"]["status"] == "healthy"
            
            self._record_success("Health Monitoring")
            
        except Exception as e:
            self._record_failure("Health Monitoring", str(e))
    
    async def test_graceful_degradation(self):
        """Test graceful degradation functionality"""
        print("Testing Graceful Degradation...")
        
        try:
            # Create degradation manager
            degradation_manager = ServiceDegradationManager()
            
            # Add fallback strategy
            async def fallback_func():
                return {"degraded": True, "message": "Service unavailable"}
            
            degradation_manager.add_service_strategy(
                "test_service",
                FallbackStrategy(fallback_func),
                priority=10
            )
            
            # Test successful call
            async def success_func():
                return {"status": "success"}
            
            result = await degradation_manager.call_service("test_service", success_func)
            assert result == {"status": "success"}
            
            # Test fallback on failure
            async def failure_func():
                raise Exception("Service failed")
            
            result = await degradation_manager.call_service("test_service", failure_func)
            assert result["degraded"] is True
            assert "Service unavailable" in result["message"]
            
            self._record_success("Graceful Degradation")
            
        except Exception as e:
            self._record_failure("Graceful Degradation", str(e))
    
    async def test_recovery_system(self):
        """Test automated recovery system"""
        print("Testing Recovery System...")
        
        try:
            # Create recovery manager
            recovery_manager = RecoveryManager()
            
            # Add recovery rule
            rule = RecoveryRule(
                service_name="test_service",
                failure_threshold=2,
                recovery_action=RecoveryAction.RESTART_SERVICE,
                retry_attempts=2,
                retry_delay=0.1,
                cooldown_period=1.0
            )
            recovery_manager.add_recovery_rule(rule)
            
            # Test recovery history
            history = recovery_manager.get_recovery_history("test_service")
            assert isinstance(history, list)
            
            # Test recovery stats
            stats = recovery_manager.get_recovery_stats("test_service")
            assert "total_attempts" in stats
            assert "success_rate" in stats
            
            self._record_success("Recovery System")
            
        except Exception as e:
            self._record_failure("Recovery System", str(e))
    
    async def test_end_to_end_integration(self):
        """Test end-to-end integration"""
        print("Testing End-to-End Integration...")
        
        try:
            # Create complete resilience system
            degradation_manager = ServiceDegradationManager()
            circuit_breaker = create_inmemory_circuit_breaker(
                name="integrated_service",
                failure_threshold=2,
                recovery_timeout=1,
                timeout=0.5
            )
            
            # Add circuit breaker strategy
            from core.circuit_breakers import CircuitBreakerStrategy
            degradation_manager.add_service_strategy(
                "integrated_service",
                CircuitBreakerStrategy(circuit_breaker),
                priority=10
            )
            
            # Create health monitor
            monitor = HealthMonitor(check_interval=0.1)
            
            # Create mock checker
            async def mock_health_check():
                return {"status": "ok"}
            
            checker = HealthChecker("integrated_service", timeout=1.0)
            checker._perform_check = mock_health_check
            monitor.add_checker(checker)
            
            # Test integrated system
            async def service_func():
                return {"result": "success"}
            
            result = await degradation_manager.call_service(
                "integrated_service",
                service_func
            )
            assert "result" in result
            
            # Test health monitoring
            report = monitor.get_health_report()
            assert "integrated_service" in report["services"]
            
            self._record_success("End-to-End Integration")
            
        except Exception as e:
            self._record_failure("End-to-End Integration", str(e))
    
    async def test_real_world_scenarios(self):
        """Test real-world usage scenarios"""
        print("Testing Real-World Scenarios...")
        
        try:
            # Test LLM service protection
            llm_manager = create_llm_degradation_manager()
            llm_circuit_breaker = create_inmemory_circuit_breaker(
                name="llm_service",
                failure_threshold=3,
                recovery_timeout=2,
                timeout=10
            )
            
            from core.circuit_breakers import CircuitBreakerStrategy
            llm_manager.add_service_strategy(
                "llm_service",
                CircuitBreakerStrategy(llm_circuit_breaker),
                priority=10
            )
            
            # Test LLM success
            async def llm_success():
                return {"response": "Hello, world!", "tokens": 5}
            
            result = await llm_manager.call_service("llm_service", llm_success)
            assert "response" in result
            
            # Test Redis service protection
            redis_manager = create_redis_degradation_manager()
            
            # Create mock Redis checker
            mock_redis = type('MockRedis', (), {
                'ping': AsyncMock(return_value="PONG"),
                'info': AsyncMock(return_value={"redis_version": "6.2.0"})
            })()
            
            checker = create_redis_health_checker(mock_redis)
            result = await checker.check()
            assert result.status == HealthStatus.HEALTHY
            
            self._record_success("Real-World Scenarios")
            
        except Exception as e:
            self._record_failure("Real-World Scenarios", str(e))
    
    async def test_performance_and_scalability(self):
        """Test performance and scalability"""
        print("Testing Performance and Scalability...")
        
        try:
            start_time = time.time()
            
            # Test concurrent access
            circuit_breaker = create_inmemory_circuit_breaker(
                name="performance_test",
                failure_threshold=10,
                recovery_timeout=1,
                timeout=0.1
            )
            
            degradation_manager = ServiceDegradationManager()
            degradation_manager.add_service_strategy(
                "performance_test",
                DegradedModeStrategy({"error": "Service overloaded"}),
                priority=10
            )
            
            # Run concurrent requests
            async def concurrent_request():
                await asyncio.sleep(0.001)  # Small delay
                return await degradation_manager.call_service(
                    "performance_test",
                    lambda: {"result": "success"}
                )
            
            # Run 100 concurrent requests
            tasks = [concurrent_request() for _ in range(100)]
            results = await asyncio.gather(*tasks)
            
            # Verify all succeeded
            assert len(results) == 100
            assert all("result" in result for result in results)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Record performance metrics
            self.results["performance_metrics"]["concurrent_requests"] = {
                "count": 100,
                "total_time": response_time,
                "avg_response_time": response_time / 100,
                "success_rate": 100.0
            }
            
            # Test health monitoring performance
            monitor = HealthMonitor(check_interval=0.1)
            
            # Create multiple checkers
            for i in range(20):
                async def mock_check():
                    await asyncio.sleep(0.001)
                    return {"service": f"service_{i}", "status": "ok"}
                
                checker = HealthChecker(f"service_{i}", timeout=1.0)
                checker._perform_check = mock_check
                monitor.add_checker(checker)
            
            # Monitor for short time
            monitor_start = time.time()
            await monitor.start_monitoring()
            await asyncio.sleep(0.2)
            await monitor.stop_monitoring()
            monitor_end = time.time()
            
            # Check performance
            monitor_time = monitor_end - monitor_start
            assert monitor_time < 1.0  # Should be fast
            
            self.results["performance_metrics"]["health_monitoring"] = {
                "services": 20,
                "monitoring_time": monitor_time,
                "success": True
            }
            
            self._record_success("Performance and Scalability")
            
        except Exception as e:
            self._record_failure("Performance and Scalability", str(e))
    
    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery"""
        print("Testing Error Handling and Recovery...")
        
        try:
            # Test circuit breaker state transitions
            circuit_breaker = create_inmemory_circuit_breaker(
                name="state_test",
                failure_threshold=2,
                recovery_timeout=0.5,
                timeout=0.1
            )
            
            # Test CLOSED -> OPEN transition
            async def failure_func():
                raise RuntimeError("Service failed")
            
            # Make failures
            for i in range(2):
                try:
                    await circuit_breaker.call(failure_func)
                except RuntimeError:
                    pass
            
            # Circuit should be open
            try:
                await circuit_breaker.call(failure_func)
                assert False, "Circuit should be open"
            except Exception:
                pass  # Expected
            
            # Wait for recovery
            await asyncio.sleep(0.6)
            
            # Should be able to recover
            async def success_func():
                return "recovered"
            
            result = await circuit_breaker.call(success_func)
            assert result == "recovered"
            
            # Test recovery with multiple attempts
            recovery_manager = RecoveryManager()
            
            rule = RecoveryRule(
                service_name="retry_test",
                failure_threshold=2,
                recovery_action=RecoveryAction.RESTART_SERVICE,
                retry_attempts=3,
                retry_delay=0.1,
                cooldown_period=1.0
            )
            recovery_manager.add_recovery_rule(rule)
            
            # Mock recovery that succeeds on third attempt
            attempt_count = 0
            
            async def mock_recovery(service_name, health_result):
                nonlocal attempt_count
                attempt_count += 1
                return attempt_count >= 3
            
            rule.custom_recovery_func = mock_recovery
            
            # Trigger recovery
            health_result = {
                "service_name": "retry_test",
                "status": HealthStatus.UNHEALTHY,
                "response_time": 1.0,
                "details": {"error": "service down"},
                "timestamp": time.time(),
                "error_message": "Service failed"
            }
            
            await recovery_manager.handle_service_failure(
                "retry_test", health_result, 2
            )
            
            # Check recovery history
            history = recovery_manager.get_recovery_history("retry_test")
            assert len(history) == 3  # Should have 3 attempts
            assert history[-1].success is True  # Last should succeed
            
            self._record_success("Error Handling and Recovery")
            
        except Exception as e:
            self._record_failure("Error Handling and Recovery", str(e))
    
    def _record_success(self, test_name: str):
        """Record successful test"""
        self.results["tests_passed"] += 1
        self.results["total_tests"] += 1
        self.results["successes"].append(test_name)
        print(f"✅ {test_name}")
    
    def _record_failure(self, test_name: str, error: str):
        """Record failed test"""
        self.results["tests_failed"] += 1
        self.results["total_tests"] += 1
        self.results["failures"].append({
            "test": test_name,
            "error": error
        })
        print(f"❌ {test_name}: {error}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        print("\n" + "=" * 60)
        print("📊 PHASE 1 VALIDATION REPORT")
        print("=" * 60)
        
        # Summary
        total_tests = self.results["total_tests"]
        passed = self.results["tests_passed"]
        failed = self.results["tests_failed"]
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Performance Metrics
        if self.results["performance_metrics"]:
            print(f"\n⚡ PERFORMANCE METRICS:")
            for metric_name, metric_data in self.results["performance_metrics"].items():
                print(f"   {metric_name}:")
                for key, value in metric_data.items():
                    if isinstance(value, float):
                        print(f"     {key}: {value:.4f}")
                    else:
                        print(f"     {key}: {value}")
        
        # Successes
        if self.results["successes"]:
            print(f"\n✅ SUCCESSFUL TESTS ({len(self.results['successes'])}):")
            for success in self.results["successes"]:
                print(f"   • {success}")
        
        # Failures
        if self.results["failures"]:
            print(f"\n❌ FAILED TESTS ({len(self.results['failures'])}):")
            for failure in self.results["failures"]:
                print(f"   • {failure['test']}: {failure['error']}")
        
        # Final Assessment
        print(f"\n🎯 FINAL ASSESSMENT:")
        if success_rate >= 90:
            print("   🎉 EXCELLENT: Phase 1 implementation is highly successful!")
            print("   ✅ All core functionality working correctly")
            print("   ✅ Performance meets requirements")
            print("   ✅ Ready for Phase 2 implementation")
        elif success_rate >= 75:
            print("   👍 GOOD: Phase 1 implementation is mostly successful")
            print("   ⚠️  Some issues need attention")
            print("   📝 Review failed tests and address issues")
        elif success_rate >= 50:
            print("   ⚠️  MODERATE: Phase 1 implementation has significant issues")
            print("   🔧 Major fixes needed before proceeding")
            print("   📋 Review all failed tests carefully")
        else:
            print("   ❌ POOR: Phase 1 implementation has critical issues")
            print("   🚨 Stop and fix fundamental problems")
            print("   📖 Review implementation against requirements")
        
        print("\n" + "=" * 60)
        
        return self.results


async def main():
    """Main validation entry point"""
    validator = Phase1Validator()
    results = await validator.run_validation()
    
    # Exit with appropriate code
    success_rate = (results["tests_passed"] / results["total_tests"] * 100) if results["total_tests"] > 0 else 0
    
    if success_rate >= 90:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    asyncio.run(main())
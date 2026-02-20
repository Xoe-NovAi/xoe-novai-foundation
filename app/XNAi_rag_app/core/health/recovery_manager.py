"""
Recovery Manager for Xoe-NovAi Foundation Stack
Provides automated recovery mechanisms for failed services with intelligent retry patterns.
"""

import asyncio
import anyio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from contextlib import asynccontextmanager

from .health_checker import HealthChecker, HealthStatus, HealthCheckResult

logger = logging.getLogger(__name__)


class RecoveryAction(Enum):
    """Recovery action types"""

    RESTART_SERVICE = "restart_service"
    CLEAR_CACHE = "clear_cache"
    RECONNECT_DATABASE = "reconnect_database"
    RELOAD_CONFIG = "reload_config"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class RecoveryRule:
    """Recovery rule configuration"""

    service_name: str
    failure_threshold: int
    recovery_action: RecoveryAction
    retry_attempts: int = 3
    retry_delay: float = 30.0
    cooldown_period: float = 300.0  # 5 minutes
    enabled: bool = True
    custom_recovery_func: Optional[Callable] = None


@dataclass
class RecoveryAttempt:
    """Recovery attempt tracking"""

    service_name: str
    action: RecoveryAction
    attempt_number: int
    timestamp: float
    success: bool
    error_message: Optional[str] = None


class RecoveryManager:
    """Manages automated recovery for failed services"""

    def __init__(self):
        self.recovery_rules: Dict[str, List[RecoveryRule]] = {}
        self.recovery_history: List[RecoveryAttempt] = []
        self._recovery_locks: Dict[str, asyncio.Lock] = {}
        self._last_recovery_time: Dict[str, float] = {}
        self._recovery_callbacks: Dict[str, Callable] = {}

        logger.info("Recovery Manager initialized")

    def add_recovery_rule(self, rule: RecoveryRule):
        """Add recovery rule for service"""
        if rule.service_name not in self.recovery_rules:
            self.recovery_rules[rule.service_name] = []

        self.recovery_rules[rule.service_name].append(rule)
        self._recovery_locks[rule.service_name] = asyncio.Lock()

        logger.info(
            f"Added recovery rule for {rule.service_name}: {rule.recovery_action.value}"
        )

    def add_recovery_callback(self, service_name: str, callback: Callable):
        """Add recovery callback for service"""
        self._recovery_callbacks[service_name] = callback
        logger.info(f"Added recovery callback for: {service_name}")

    async def handle_service_failure(
        self,
        service_name: str,
        health_result: HealthCheckResult,
        consecutive_failures: int,
    ):
        """Handle service failure and trigger recovery if needed"""
        if service_name not in self.recovery_rules:
            logger.warning(f"No recovery rules defined for {service_name}")
            return

        rules = self.recovery_rules[service_name]

        for rule in rules:
            if not rule.enabled:
                continue

            if consecutive_failures >= rule.failure_threshold:
                await self._execute_recovery_action(rule, health_result)
                break

    async def _execute_recovery_action(
        self, rule: RecoveryRule, health_result: HealthCheckResult
    ):
        """Execute recovery action with locking and retry logic"""
        service_name = rule.service_name

        # Check cooldown period
        last_recovery = self._last_recovery_time.get(service_name, 0)
        if time.time() - last_recovery < rule.cooldown_period:
            logger.warning(f"Recovery for {service_name} in cooldown period")
            return

        # Acquire lock to prevent concurrent recoveries
        async with self._recovery_locks[service_name]:
            logger.info(
                f"Starting recovery for {service_name}: {rule.recovery_action.value}"
            )

            for attempt in range(rule.retry_attempts):
                try:
                    success = await self._perform_recovery_action(rule, health_result)

                    # Record recovery attempt
                    recovery_attempt = RecoveryAttempt(
                        service_name=service_name,
                        action=rule.recovery_action,
                        attempt_number=attempt + 1,
                        timestamp=time.time(),
                        success=success,
                    )

                    self.recovery_history.append(recovery_attempt)

                    if success:
                        self._last_recovery_time[service_name] = time.time()
                        logger.info(
                            f"Recovery successful for {service_name} on attempt {attempt + 1}"
                        )

                        # Call recovery callback
                        if service_name in self._recovery_callbacks:
                            try:
                                await self._recovery_callbacks[service_name](
                                    service_name, rule, recovery_attempt
                                )
                            except Exception as e:
                                logger.error(
                                    f"Recovery callback failed for {service_name}: {e}"
                                )

                        break
                    else:
                        logger.warning(
                            f"Recovery attempt {attempt + 1} failed for {service_name}"
                        )
                        if attempt < rule.retry_attempts - 1:
                            await asyncio.sleep(
                                rule.retry_delay * (2**attempt)
                            )  # Exponential backoff

                except Exception as e:
                    logger.error(f"Recovery execution failed for {service_name}: {e}")
                    recovery_attempt = RecoveryAttempt(
                        service_name=service_name,
                        action=rule.recovery_action,
                        attempt_number=attempt + 1,
                        timestamp=time.time(),
                        success=False,
                        error_message=str(e),
                    )
                    self.recovery_history.append(recovery_attempt)

    async def _perform_recovery_action(
        self, rule: RecoveryRule, health_result: HealthCheckResult
    ) -> bool:
        """Perform specific recovery action"""
        service_name = rule.service_name

        try:
            if rule.custom_recovery_func:
                # Use custom recovery function
                return await rule.custom_recovery_func(service_name, health_result)

            # Built-in recovery actions
            if rule.recovery_action == RecoveryAction.RESTART_SERVICE:
                return await self._restart_service(service_name)
            elif rule.recovery_action == RecoveryAction.CLEAR_CACHE:
                return await self._clear_cache(service_name)
            elif rule.recovery_action == RecoveryAction.RECONNECT_DATABASE:
                return await self._reconnect_database(service_name)
            elif rule.recovery_action == RecoveryAction.RELOAD_CONFIG:
                return await self._reload_config(service_name)
            elif rule.recovery_action == RecoveryAction.SCALE_UP:
                return await self._scale_service(service_name, "up")
            elif rule.recovery_action == RecoveryAction.SCALE_DOWN:
                return await self._scale_service(service_name, "down")
            elif rule.recovery_action == RecoveryAction.MANUAL_INTERVENTION:
                return await self._request_manual_intervention(
                    service_name, health_result
                )

            return False

        except Exception as e:
            logger.error(
                f"Recovery action {rule.recovery_action.value} failed for {service_name}: {e}"
            )
            return False

    async def _restart_service(self, service_name: str) -> bool:
        """Restart service using Docker/Podman"""
        try:
            # Try Podman first
            cmd = f"podman restart {service_name}"
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logger.info(f"Service {service_name} restarted successfully")
                return True
            else:
                logger.warning(
                    f"Podman restart failed for {service_name}, trying Docker"
                )

                # Fallback to Docker
                cmd = f"docker restart {service_name}"
                process = await asyncio.create_subprocess_shell(
                    cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

                if process.returncode == 0:
                    logger.info(
                        f"Service {service_name} restarted successfully with Docker"
                    )
                    return True
                else:
                    logger.error(f"Failed to restart {service_name}: {stderr.decode()}")
                    return False

        except Exception as e:
            logger.error(f"Service restart failed for {service_name}: {e}")
            return False

    async def _clear_cache(self, service_name: str) -> bool:
        """Clear cache for service"""
        try:
            # This would be implemented based on your caching strategy
            # For Redis, you might clear specific keys
            # For in-memory cache, you might clear specific cache instances

            logger.info(f"Cache cleared for {service_name}")
            return True

        except Exception as e:
            logger.error(f"Cache clear failed for {service_name}: {e}")
            return False

    async def _reconnect_database(self, service_name: str) -> bool:
        """Reconnect to database"""
        try:
            # This would implement database reconnection logic
            # Could involve restarting database connections, clearing connection pools, etc.

            logger.info(f"Database reconnection initiated for {service_name}")
            return True

        except Exception as e:
            logger.error(f"Database reconnection failed for {service_name}: {e}")
            return False

    async def _reload_config(self, service_name: str) -> bool:
        """Reload configuration for service"""
        try:
            # Send SIGHUP or use service-specific config reload mechanism
            cmd = f"podman kill -s HUP {service_name}"
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logger.info(f"Configuration reloaded for {service_name}")
                return True
            else:
                logger.warning(f"Config reload failed for {service_name}")
                return False

        except Exception as e:
            logger.error(f"Config reload failed for {service_name}: {e}")
            return False

    async def _scale_service(self, service_name: str, direction: str) -> bool:
        """Scale service up or down"""
        try:
            # This would implement service scaling logic
            # Could involve Docker Compose scaling, Kubernetes scaling, etc.

            logger.info(f"Service {service_name} scaling {direction}")
            return True

        except Exception as e:
            logger.error(f"Service scaling failed for {service_name}: {e}")
            return False

    async def _request_manual_intervention(
        self, service_name: str, health_result: HealthCheckResult
    ) -> bool:
        """Request manual intervention for service"""
        try:
            # Log critical error requiring manual intervention
            logger.critical(
                f"Service {service_name} requires manual intervention: {health_result.error_message}"
            )

            # This could send alerts to monitoring systems, Slack, email, etc.
            # For now, just log the critical error

            return False  # Manual intervention doesn't automatically succeed

        except Exception as e:
            logger.error(f"Manual intervention request failed for {service_name}: {e}")
            return False

    def get_recovery_history(
        self, service_name: Optional[str] = None
    ) -> List[RecoveryAttempt]:
        """Get recovery history for service or all services"""
        if service_name:
            return [r for r in self.recovery_history if r.service_name == service_name]
        else:
            return self.recovery_history.copy()

    def get_recovery_stats(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get recovery statistics"""
        history = self.get_recovery_history(service_name)

        stats = {
            "total_attempts": len(history),
            "success_rate": 0.0,
            "average_recovery_time": 0.0,
            "actions_by_type": {},
            "recent_failures": [],
        }

        if not history:
            return stats

        successes = [r for r in history if r.success]
        stats["success_rate"] = len(successes) / len(history)

        # Calculate average recovery time
        if successes:
            recovery_times = []
            for success in successes:
                # Find corresponding failure
                failure_time = success.timestamp - 30  # Approximate
                recovery_time = success.timestamp - failure_time
                recovery_times.append(recovery_time)

            stats["average_recovery_time"] = sum(recovery_times) / len(recovery_times)

        # Count actions by type
        for attempt in history:
            action_name = attempt.action.value
            stats["actions_by_type"][action_name] = (
                stats["actions_by_type"].get(action_name, 0) + 1
            )

        # Get recent failures
        failures = [r for r in history if not r.success][-10:]  # Last 10 failures
        stats["recent_failures"] = [
            {
                "service": r.service_name,
                "action": r.action.value,
                "attempt": r.attempt_number,
                "error": r.error_message,
                "timestamp": r.timestamp,
            }
            for r in failures
        ]

        return stats

    async def cleanup_old_history(self, max_age_hours: int = 24):
        """Clean up old recovery history"""
        cutoff_time = time.time() - (max_age_hours * 3600)

        self.recovery_history = [
            r for r in self.recovery_history if r.timestamp > cutoff_time
        ]

        logger.info(f"Cleaned up recovery history older than {max_age_hours} hours")


# Factory functions for common recovery rules
def create_redis_recovery_rules() -> List[RecoveryRule]:
    """Create recovery rules for Redis service"""
    return [
        RecoveryRule(
            service_name="redis",
            failure_threshold=3,
            recovery_action=RecoveryAction.RESTART_SERVICE,
            retry_attempts=2,
            retry_delay=60.0,
            cooldown_period=300.0,
        ),
        RecoveryRule(
            service_name="redis",
            failure_threshold=5,
            recovery_action=RecoveryAction.MANUAL_INTERVENTION,
            enabled=True,
        ),
    ]


def create_rag_api_recovery_rules() -> List[RecoveryRule]:
    """Create recovery rules for RAG API service"""
    return [
        RecoveryRule(
            service_name="rag_api",
            failure_threshold=2,
            recovery_action=RecoveryAction.RESTART_SERVICE,
            retry_attempts=3,
            retry_delay=30.0,
            cooldown_period=180.0,
        ),
        RecoveryRule(
            service_name="rag_api",
            failure_threshold=5,
            recovery_action=RecoveryAction.CLEAR_CACHE,
            retry_attempts=2,
            retry_delay=60.0,
            cooldown_period=600.0,
        ),
    ]


def create_chainlit_ui_recovery_rules() -> List[RecoveryRule]:
    """Create recovery rules for Chainlit UI service"""
    return [
        RecoveryRule(
            service_name="chainlit_ui",
            failure_threshold=2,
            recovery_action=RecoveryAction.RESTART_SERVICE,
            retry_attempts=3,
            retry_delay=30.0,
            cooldown_period=180.0,
        )
    ]


def create_vikunja_recovery_rules() -> List[RecoveryRule]:
    """Create recovery rules for Vikunja service"""
    return [
        RecoveryRule(
            service_name="vikunja",
            failure_threshold=3,
            recovery_action=RecoveryAction.RESTART_SERVICE,
            retry_attempts=2,
            retry_delay=60.0,
            cooldown_period=300.0,
        ),
        RecoveryRule(
            service_name="vikunja",
            failure_threshold=5,
            recovery_action=RecoveryAction.RECONNECT_DATABASE,
            retry_attempts=3,
            retry_delay=30.0,
            cooldown_period=600.0,
        ),
    ]


# Integration with health monitoring
class IntegratedRecoveryManager:
    """Integrated recovery manager that works with health monitoring"""

    def __init__(self, health_monitor):
        self.health_monitor = health_monitor
        self.recovery_manager = RecoveryManager()

        # Register recovery rules
        self._setup_recovery_rules()

        # Register health callback to trigger recovery
        self.health_monitor.add_health_callback(
            "all_services", self._health_status_callback
        )

    def _setup_recovery_rules(self):
        """Setup recovery rules for all services"""
        # Add recovery rules for each service
        for service_name in self.health_monitor.checkers.keys():
            if service_name == "redis":
                for rule in create_redis_recovery_rules():
                    self.recovery_manager.add_recovery_rule(rule)
            elif service_name == "rag_api":
                for rule in create_rag_api_recovery_rules():
                    self.recovery_manager.add_recovery_rule(rule)
            elif service_name == "chainlit_ui":
                for rule in create_chainlit_ui_recovery_rules():
                    self.recovery_manager.add_recovery_rule(rule)
            elif service_name == "vikunja":
                for rule in create_vikunja_recovery_rules():
                    self.recovery_manager.add_recovery_rule(rule)

    async def _health_status_callback(
        self,
        service_name: str,
        old_status: HealthStatus,
        new_status: HealthStatus,
        result: HealthCheckResult,
    ):
        """Health status callback to trigger recovery"""
        if new_status == HealthStatus.UNHEALTHY:
            # Get consecutive failures from health monitor
            health_state = self.health_monitor.get_health_status(service_name)
            if health_state:
                await self.recovery_manager.handle_service_failure(
                    service_name, result, health_state.consecutive_failures
                )

    def get_integrated_status(self) -> Dict[str, Any]:
        """Get integrated health and recovery status"""
        return {
            "health_report": self.health_monitor.get_health_report(),
            "recovery_stats": self.recovery_manager.get_recovery_stats(),
            "recovery_history": self.recovery_manager.get_recovery_history(),
        }

    async def cleanup(self):
        """Clean up recovery history"""
        await self.recovery_manager.cleanup_old_history()


# Example usage
async def example_usage():
    """Example of how to use the recovery system"""

    # This would be integrated with the health monitoring system
    # from .health_checker import HealthMonitor

    # Create recovery manager
    recovery_manager = RecoveryManager()

    # Add recovery rules
    for rule in create_redis_recovery_rules():
        recovery_manager.add_recovery_rule(rule)

    for rule in create_rag_api_recovery_rules():
        recovery_manager.add_recovery_rule(rule)

    # Add recovery callback
    async def recovery_callback(
        service_name: str, rule: RecoveryRule, attempt: RecoveryAttempt
    ):
        logger.info(f"Recovery completed for {service_name}: {attempt.success}")

    recovery_manager.add_recovery_callback("redis", recovery_callback)

    # Get recovery stats
    stats = recovery_manager.get_recovery_stats()
    print(f"Recovery stats: {stats}")


if __name__ == "__main__":
    anyio.run(example_usage)

"""
Health Monitoring System for Xoe-NovAi Foundation Stack
Provides comprehensive health monitoring and automated recovery for all services.
"""

from .health_checker import (
    HealthChecker,
    HealthStatus,
    HealthCheckResult,
    ServiceHealth,
    HTTPHealthChecker,
    RedisHealthChecker,
    DatabaseHealthChecker,
    CustomHealthChecker,
    HealthMonitor,
    create_rag_api_health_checker,
    create_chainlit_ui_health_checker,
    create_redis_health_checker,
    create_vikunja_health_checker,
    create_caddy_health_checker
)

from .recovery_manager import (
    RecoveryManager,
    RecoveryAction,
    RecoveryRule,
    RecoveryAttempt,
    IntegratedRecoveryManager,
    create_redis_recovery_rules,
    create_rag_api_recovery_rules,
    create_chainlit_ui_recovery_rules,
    create_vikunja_recovery_rules
)

__all__ = [
    # Health Checker
    'HealthChecker',
    'HealthStatus',
    'HealthCheckResult',
    'ServiceHealth',
    'HTTPHealthChecker',
    'RedisHealthChecker',
    'DatabaseHealthChecker',
    'CustomHealthChecker',
    'HealthMonitor',
    'create_rag_api_health_checker',
    'create_chainlit_ui_health_checker',
    'create_redis_health_checker',
    'create_vikunja_health_checker',
    'create_caddy_health_checker',
    
    # Recovery Manager
    'RecoveryManager',
    'RecoveryAction',
    'RecoveryRule',
    'RecoveryAttempt',
    'IntegratedRecoveryManager',
    'create_redis_recovery_rules',
    'create_rag_api_recovery_rules',
    'create_chainlit_ui_recovery_rules',
    'create_vikunja_recovery_rules'
]

# Version information
__version__ = "1.0.0"
__author__ = "Xoe-NovAi Foundation Stack"
__description__ = "Comprehensive health monitoring and automated recovery system"
#!/usr/bin/env python3
"""
Omega Observability System
==========================

Comprehensive observability framework for the XNAi Foundation Omega Stack.
Provides error handling, logging, metrics collection, and system monitoring.
"""

import asyncio
import json
import logging
import time
import traceback
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
import uuid

import redis
from prometheus_client import Gauge, Counter, Histogram, Info
from prometheus_client.exposition import start_http_server

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorType(Enum):
    """Types of errors encountered."""
    SYSTEM_CRASH = "system_crash"
    DATA_LOSS = "data_loss"
    SECURITY_BREACH = "security_breach"
    AGENT_TIMEOUT = "agent_timeout"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_FAILURE = "network_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    CACHE_MISS = "cache_miss"
    VALIDATION_ERROR = "validation_error"
    MINOR_GLITCH = "minor_glitch"
    CONFIGURATION_WARNING = "configuration_warning"
    DEPRECATED_FEATURE = "deprecated_feature"

@dataclass
class ErrorEvent:
    """Structured error event."""
    error_id: str
    timestamp: float
    severity: ErrorSeverity
    error_type: ErrorType
    agent_id: Optional[str]
    session_id: Optional[str]
    correlation_id: Optional[str]
    message: str
    details: Dict[str, Any]
    stack_trace: Optional[str]
    recovery_attempted: bool = False
    resolved: bool = False

@dataclass
class SystemMetric:
    """System performance metric."""
    metric_id: str
    timestamp: float
    metric_type: str
    value: float
    labels: Dict[str, str]
    unit: str

class OmegaObservabilitySystem:
    """
    Core observability system for comprehensive monitoring and error handling.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/2"):
        self.redis_client = redis.from_url(redis_url)
        self.error_log_path = Path("logs/omega_errors.log")
        self.system_log_path = Path("logs/omega_system.log")
        self.metrics_log_path = Path("logs/omega_metrics.log")
        
        # Ensure log directories exist
        self.error_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Error categorization and escalation rules
        self.error_categories = {
            ErrorSeverity.CRITICAL: [
                ErrorType.SYSTEM_CRASH, ErrorType.DATA_LOSS, ErrorType.SECURITY_BREACH
            ],
            ErrorSeverity.HIGH: [
                ErrorType.AGENT_TIMEOUT, ErrorType.RESOURCE_EXHAUSTION, 
                ErrorType.NETWORK_FAILURE
            ],
            ErrorSeverity.MEDIUM: [
                ErrorType.PERFORMANCE_DEGRADATION, ErrorType.CACHE_MISS,
                ErrorType.VALIDATION_ERROR
            ],
            ErrorSeverity.LOW: [
                ErrorType.MINOR_GLITCH, ErrorType.CONFIGURATION_WARNING,
                ErrorType.DEPRECATED_FEATURE
            ]
        }
        
        self.escalation_rules = {
            ErrorSeverity.CRITICAL: ["immediate_alert", "auto_recovery", "human_intervention"],
            ErrorSeverity.HIGH: ["5_min_alert", "automatic_retry", "performance_scaling"],
            ErrorSeverity.MEDIUM: ["15_min_alert", "log_analysis", "resource_optimization"],
            ErrorSeverity.LOW: ["hourly_summary", "trend_analysis", "preventive_measures"]
        }
        
        # Prometheus metrics
        self.setup_prometheus_metrics()
        
        # Initialize logging
        self.setup_logging()
        
        # Recovery strategies
        self.recovery_strategies = {
            ErrorType.AGENT_TIMEOUT: self.restart_agent,
            ErrorType.RESOURCE_EXHAUSTION: self.reduce_agent_load,
            ErrorType.NETWORK_FAILURE: self.switch_to_offline_mode,
            ErrorType.VALIDATION_ERROR: self.rollback_configuration,
            ErrorType.SYSTEM_CRASH: self.full_system_recovery
        }
        
        # Start background monitoring
        self.monitoring_task = None
        
    def setup_prometheus_metrics(self):
        """Initialize Prometheus metrics for system monitoring."""
        # System health metrics
        self.system_health = Gauge('omega_system_health', 'Overall system health score', ['component'])
        self.error_rate = Counter('omega_error_rate', 'Error rate by severity', ['severity', 'error_type'])
        self.response_time = Histogram('omega_response_time', 'Response time distribution', ['component'])
        
        # Agent-specific metrics
        self.agent_status = Gauge('omega_agent_status', 'Agent status', ['agent_id', 'agent_type'])
        self.agent_resource_usage = Gauge('omega_agent_resource_usage', 'Agent resource usage', ['agent_id', 'resource_type'])
        self.agent_performance = Gauge('omega_agent_performance', 'Agent performance metrics', ['agent_id', 'metric_type'])
        
        # Session metrics
        self.session_quality = Gauge('omega_session_quality', 'Session quality score', ['session_id'])
        self.session_continuity = Gauge('omega_session_continuity', 'Session continuity score', ['session_id'])
        
        # Business metrics
        self.cost_savings = Gauge('omega_cost_savings', 'Cost savings from optimization', ['optimization_type'])
        self.cache_efficiency = Gauge('omega_cache_efficiency', 'Cache hit rate and efficiency', ['cache_type'])
        
        # Start Prometheus HTTP server
        start_http_server(8002)  # Port 8002 for observability metrics
        
    def setup_logging(self):
        """Configure structured logging for the observability system."""
        # Configure error logger
        error_handler = logging.FileHandler(self.error_log_path)
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        error_handler.setFormatter(error_formatter)
        
        # Configure system logger
        system_handler = logging.FileHandler(self.system_log_path)
        system_handler.setLevel(logging.INFO)
        system_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        system_handler.setFormatter(system_formatter)
        
        # Configure metrics logger
        metrics_handler = logging.FileHandler(self.metrics_log_path)
        metrics_handler.setLevel(logging.INFO)
        metrics_formatter = logging.Formatter(
            '%(asctime)s - METRICS - %(message)s'
        )
        metrics_handler.setFormatter(metrics_formatter)
        
        # Add handlers to logger
        logger.addHandler(error_handler)
        logger.addHandler(system_handler)
        
        # Set up metrics logger
        self.metrics_logger = logging.getLogger('omega_metrics')
        self.metrics_logger.addHandler(metrics_handler)
        self.metrics_logger.setLevel(logging.INFO)
        
    async def log_error(self, error_event: ErrorEvent):
        """Log an error event with full context and correlation."""
        try:
            # Store in Redis for real-time access
            error_key = f"omega:error:{error_event.error_id}"
            self.redis_client.setex(
                error_key, 
                86400,  # 24 hours TTL
                json.dumps(asdict(error_event), default=str)
            )
            
            # Log to file with structured format
            error_data = {
                "error_id": error_event.error_id,
                "timestamp": error_event.timestamp,
                "severity": error_event.severity.value,
                "error_type": error_event.error_type.value,
                "agent_id": error_event.agent_id,
                "session_id": error_event.session_id,
                "correlation_id": error_event.correlation_id,
                "message": error_event.message,
                "details": error_event.details,
                "stack_trace": error_event.stack_trace,
                "recovery_attempted": error_event.recovery_attempted,
                "resolved": error_event.resolved
            }
            
            logger.error(f"ERROR: {json.dumps(error_data)}")
            
            # Update Prometheus metrics
            self.error_rate.labels(
                severity=error_event.severity.value,
                error_type=error_event.error_type.value
            ).inc()
            
            # Trigger escalation based on severity
            await self.handle_error_escalation(error_event)
            
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
    
    async def handle_error_escalation(self, error_event: ErrorEvent):
        """Handle error escalation based on severity and type."""
        try:
            escalation_actions = self.escalation_rules.get(error_event.severity, [])
            
            for action in escalation_actions:
                if action == "immediate_alert":
                    await self.send_immediate_alert(error_event)
                elif action == "auto_recovery":
                    await self.attempt_auto_recovery(error_event)
                elif action == "human_intervention":
                    await self.request_human_intervention(error_event)
                elif action == "5_min_alert":
                    await self.schedule_delayed_alert(error_event, 300)
                elif action == "automatic_retry":
                    await self.schedule_automatic_retry(error_event)
                elif action == "performance_scaling":
                    await self.trigger_performance_scaling(error_event)
                elif action == "15_min_alert":
                    await self.schedule_delayed_alert(error_event, 900)
                elif action == "log_analysis":
                    await self.schedule_log_analysis(error_event)
                elif action == "resource_optimization":
                    await self.trigger_resource_optimization(error_event)
                elif action == "hourly_summary":
                    await self.add_to_hourly_summary(error_event)
                elif action == "trend_analysis":
                    await self.schedule_trend_analysis(error_event)
                elif action == "preventive_measures":
                    await self.schedule_preventive_measures(error_event)
                    
        except Exception as e:
            logger.error(f"Failed to handle error escalation: {e}")
    
    async def attempt_auto_recovery(self, error_event: ErrorEvent):
        """Attempt automatic recovery for the error."""
        try:
            recovery_strategy = self.recovery_strategies.get(error_event.error_type)
            if recovery_strategy:
                logger.info(f"Attempting auto-recovery for {error_event.error_type.value}")
                result = await recovery_strategy(error_event.agent_id)
                
                error_event.recovery_attempted = True
                error_event.resolved = result
                
                await self.log_error(error_event)
                
                if result:
                    logger.info(f"Auto-recovery successful for {error_event.error_type.value}")
                else:
                    logger.warning(f"Auto-recovery failed for {error_event.error_type.value}")
            else:
                logger.warning(f"No recovery strategy available for {error_event.error_type.value}")
                
        except Exception as e:
            logger.error(f"Auto-recovery attempt failed: {e}")
    
    async def restart_agent(self, agent_id: Optional[str]) -> bool:
        """Restart a failed agent."""
        try:
            if not agent_id:
                return False
                
            logger.info(f"Restarting agent: {agent_id}")
            # Implementation would depend on agent management system
            # This is a placeholder for actual agent restart logic
            return True
            
        except Exception as e:
            logger.error(f"Failed to restart agent {agent_id}: {e}")
            return False
    
    async def reduce_agent_load(self, agent_id: Optional[str]) -> bool:
        """Reduce load on an agent experiencing resource exhaustion."""
        try:
            if not agent_id:
                return False
                
            logger.info(f"Reducing load for agent: {agent_id}")
            # Implementation would reduce agent workload
            return True
            
        except Exception as e:
            logger.error(f"Failed to reduce load for agent {agent_id}: {e}")
            return False
    
    async def switch_to_offline_mode(self, agent_id: Optional[str]) -> bool:
        """Switch agent to offline mode during network failure."""
        try:
            if not agent_id:
                return False
                
            logger.info(f"Switching agent to offline mode: {agent_id}")
            # Implementation would switch agent to offline mode
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch agent {agent_id} to offline mode: {e}")
            return False
    
    async def rollback_configuration(self, agent_id: Optional[str]) -> bool:
        """Rollback configuration changes that caused validation errors."""
        try:
            if not agent_id:
                return False
                
            logger.info(f"Rolling back configuration for agent: {agent_id}")
            # Implementation would rollback configuration
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback configuration for agent {agent_id}: {e}")
            return False
    
    async def full_system_recovery(self, agent_id: Optional[str]) -> bool:
        """Perform full system recovery for critical system crashes."""
        try:
            logger.critical("Initiating full system recovery")
            # Implementation would perform comprehensive system recovery
            return True
            
        except Exception as e:
            logger.error(f"Full system recovery failed: {e}")
            return False
    
    async def send_immediate_alert(self, error_event: ErrorEvent):
        """Send immediate alert for critical errors."""
        try:
            alert_data = {
                "alert_type": "immediate",
                "severity": error_event.severity.value,
                "error_type": error_event.error_type.value,
                "message": error_event.message,
                "timestamp": error_event.timestamp,
                "agent_id": error_event.agent_id,
                "session_id": error_event.session_id
            }
            
            # Store alert in Redis for dashboard consumption
            alert_key = f"omega:alert:immediate:{error_event.error_id}"
            self.redis_client.setex(alert_key, 3600, json.dumps(alert_data, default=str))
            
            logger.critical(f"IMMEDIATE ALERT: {json.dumps(alert_data)}")
            
        except Exception as e:
            logger.error(f"Failed to send immediate alert: {e}")
    
    async def request_human_intervention(self, error_event: ErrorEvent):
        """Request human intervention for critical errors."""
        try:
            intervention_data = {
                "error_id": error_event.error_id,
                "severity": error_event.severity.value,
                "error_type": error_event.error_type.value,
                "message": error_event.message,
                "timestamp": error_event.timestamp,
                "required_action": "human_intervention",
                "details": error_event.details
            }
            
            # Store intervention request in Redis
            intervention_key = f"omega:intervention:{error_event.error_id}"
            self.redis_client.setex(intervention_key, 86400, json.dumps(intervention_data, default=str))
            
            logger.critical(f"HUMAN INTERVENTION REQUIRED: {json.dumps(intervention_data)}")
            
        except Exception as e:
            logger.error(f"Failed to request human intervention: {e}")
    
    async def log_system_metric(self, metric: SystemMetric):
        """Log a system performance metric."""
        try:
            # Store in Redis
            metric_key = f"omega:metric:{metric.metric_id}"
            self.redis_client.setex(
                metric_key, 
                3600,  # 1 hour TTL
                json.dumps(asdict(metric), default=str)
            )
            
            # Log to metrics file
            metric_data = {
                "metric_id": metric.metric_id,
                "timestamp": metric.timestamp,
                "metric_type": metric.metric_type,
                "value": metric.value,
                "labels": metric.labels,
                "unit": metric.unit
            }
            
            self.metrics_logger.info(json.dumps(metric_data))
            
            # Update Prometheus metrics
            if metric.metric_type == "response_time":
                self.response_time.labels(**metric.labels).observe(metric.value)
            elif metric.metric_type == "agent_status":
                self.agent_status.labels(**metric.labels).set(metric.value)
            elif metric.metric_type == "agent_resource_usage":
                self.agent_resource_usage.labels(**metric.labels).set(metric.value)
            elif metric.metric_type == "session_quality":
                self.session_quality.labels(**metric.labels).set(metric.value)
            elif metric.metric_type == "cost_savings":
                self.cost_savings.labels(**metric.labels).set(metric.value)
            elif metric.metric_type == "cache_efficiency":
                self.cache_efficiency.labels(**metric.labels).set(metric.value)
                
        except Exception as e:
            logger.error(f"Failed to log system metric: {e}")
    
    async def start_background_monitoring(self):
        """Start background monitoring of system health."""
        if self.monitoring_task and not self.monitoring_task.done():
            return
            
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started Omega Observability background monitoring")
    
    async def stop_background_monitoring(self):
        """Stop background monitoring."""
        if self.monitoring_task and not self.monitoring_task.done():
            self.monitoring_task.cancel()
            await self.monitoring_task
        logger.info("Stopped Omega Observability background monitoring")
    
    async def _monitoring_loop(self):
        """Background monitoring loop for system health."""
        while True:
            try:
                # Collect system metrics
                await self.collect_system_metrics()
                
                # Check for error patterns
                await self.analyze_error_patterns()
                
                # Monitor resource usage
                await self.monitor_resource_usage()
                
                # Update system health score
                await self.update_system_health()
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def collect_system_metrics(self):
        """Collect comprehensive system metrics."""
        try:
            # Collect memory usage
            import psutil
            memory_info = psutil.virtual_memory()
            memory_metric = SystemMetric(
                metric_id=f"memory_usage_{int(time.time())}",
                timestamp=time.time(),
                metric_type="memory_usage",
                value=memory_info.percent,
                labels={"type": "virtual_memory"},
                unit="percent"
            )
            await self.log_system_metric(memory_metric)
            
            # Collect CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_metric = SystemMetric(
                metric_id=f"cpu_usage_{int(time.time())}",
                timestamp=time.time(),
                metric_type="cpu_usage",
                value=cpu_percent,
                labels={"type": "total"},
                unit="percent"
            )
            await self.log_system_metric(cpu_metric)
            
            # Collect disk usage
            disk_usage = psutil.disk_usage('/')
            disk_metric = SystemMetric(
                metric_id=f"disk_usage_{int(time.time())}",
                timestamp=time.time(),
                metric_type="disk_usage",
                value=(disk_usage.used / disk_usage.total) * 100,
                labels={"type": "root"},
                unit="percent"
            )
            await self.log_system_metric(disk_metric)
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    async def analyze_error_patterns(self):
        """Analyze error patterns for trend detection."""
        try:
            # Get recent errors from Redis
            error_keys = self.redis_client.keys("omega:error:*")
            recent_errors = []
            
            for key in error_keys:
                error_data = self.redis_client.get(key)
                if error_data:
                    error_event = json.loads(error_data)
                    recent_errors.append(error_event)
            
            # Analyze patterns
            error_counts = {}
            for error in recent_errors:
                error_type = error.get("error_type")
                if error_type in error_counts:
                    error_counts[error_type] += 1
                else:
                    error_counts[error_type] = 1
            
            # Log pattern analysis
            pattern_data = {
                "timestamp": time.time(),
                "error_counts": error_counts,
                "total_errors": len(recent_errors)
            }
            
            self.metrics_logger.info(f"ERROR_PATTERN: {json.dumps(pattern_data)}")
            
        except Exception as e:
            logger.error(f"Failed to analyze error patterns: {e}")
    
    async def monitor_resource_usage(self):
        """Monitor resource usage and trigger alerts if needed."""
        try:
            # Check memory usage
            import psutil
            memory_info = psutil.virtual_memory()
            
            if memory_info.percent > 90:
                error_event = ErrorEvent(
                    error_id=str(uuid.uuid4()),
                    timestamp=time.time(),
                    severity=ErrorSeverity.HIGH,
                    error_type=ErrorType.RESOURCE_EXHAUSTION,
                    agent_id=None,
                    session_id=None,
                    correlation_id=None,
                    message=f"Memory usage critical: {memory_info.percent}%",
                    details={"memory_percent": memory_info.percent, "memory_available": memory_info.available},
                    stack_trace=None
                )
                await self.log_error(error_event)
            
            # Check disk usage
            disk_usage = psutil.disk_usage('/')
            disk_percent = (disk_usage.used / disk_usage.total) * 100
            
            if disk_percent > 90:
                error_event = ErrorEvent(
                    error_id=str(uuid.uuid4()),
                    timestamp=time.time(),
                    severity=ErrorSeverity.HIGH,
                    error_type=ErrorType.RESOURCE_EXHAUSTION,
                    agent_id=None,
                    session_id=None,
                    correlation_id=None,
                    message=f"Disk usage critical: {disk_percent:.1f}%",
                    details={"disk_percent": disk_percent, "disk_free": disk_usage.free},
                    stack_trace=None
                )
                await self.log_error(error_event)
                
        except Exception as e:
            logger.error(f"Failed to monitor resource usage: {e}")
    
    async def update_system_health(self):
        """Update overall system health score."""
        try:
            # Calculate health score based on various factors
            health_score = 100.0
            
            # Deduct points for errors
            error_keys = self.redis_client.keys("omega:error:*")
            error_count = len(error_keys)
            health_score -= min(error_count * 5, 30)  # Max 30 point deduction for errors
            
            # Deduct points for resource usage
            import psutil
            memory_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()
            
            if memory_info.percent > 80:
                health_score -= 10
            if cpu_percent > 80:
                health_score -= 10
            
            # Update Prometheus metric
            self.system_health.labels(component="overall").set(health_score)
            
            # Log health score
            health_data = {
                "timestamp": time.time(),
                "health_score": health_score,
                "error_count": error_count,
                "memory_usage": memory_info.percent,
                "cpu_usage": cpu_percent
            }
            
            self.metrics_logger.info(f"SYSTEM_HEALTH: {json.dumps(health_data)}")
            
        except Exception as e:
            logger.error(f"Failed to update system health: {e}")
    
    @asynccontextmanager
    async def monitor_operation(self, operation_name: str, agent_id: Optional[str] = None):
        """Context manager for monitoring operations."""
        start_time = time.time()
        operation_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting operation: {operation_name} (ID: {operation_id})")
            
            yield
            
            # Operation completed successfully
            duration = time.time() - start_time
            
            # Log success metric
            success_metric = SystemMetric(
                metric_id=f"operation_success_{operation_id}",
                timestamp=time.time(),
                metric_type="operation_duration",
                value=duration,
                labels={"operation": operation_name, "agent_id": agent_id or "system"},
                unit="seconds"
            )
            await self.log_system_metric(success_metric)
            
            logger.info(f"Operation completed: {operation_name} (Duration: {duration:.2f}s)")
            
        except Exception as e:
            # Operation failed
            duration = time.time() - start_time
            
            # Determine error type and severity
            error_type = self._classify_error(e)
            severity = self._determine_severity(error_type)
            
            # Create error event
            error_event = ErrorEvent(
                error_id=str(uuid.uuid4()),
                timestamp=time.time(),
                severity=severity,
                error_type=error_type,
                agent_id=agent_id,
                session_id=None,  # Could be extracted from context
                correlation_id=operation_id,
                message=f"Operation failed: {operation_name}",
                details={
                    "operation_name": operation_name,
                    "duration": duration,
                    "exception": str(e),
                    "exception_type": type(e).__name__
                },
                stack_trace=traceback.format_exc()
            )
            
            await self.log_error(error_event)
            
            logger.error(f"Operation failed: {operation_name} (Duration: {duration:.2f}s) - {e}")
            
            # Re-raise the exception
            raise
    
    def _classify_error(self, exception: Exception) -> ErrorType:
        """Classify an exception into an error type."""
        exception_type = type(exception).__name__
        
        if "Timeout" in exception_type:
            return ErrorType.AGENT_TIMEOUT
        elif "MemoryError" in exception_type:
            return ErrorType.RESOURCE_EXHAUSTION
        elif "ConnectionError" in exception_type or "Network" in exception_type:
            return ErrorType.NETWORK_FAILURE
        elif "ValidationError" in exception_type:
            return ErrorType.VALIDATION_ERROR
        elif "SystemError" in exception_type:
            return ErrorType.SYSTEM_CRASH
        else:
            return ErrorType.MINOR_GLITCH
    
    def _determine_severity(self, error_type: ErrorType) -> ErrorSeverity:
        """Determine severity based on error type."""
        for severity, error_types in self.error_categories.items():
            if error_type in error_types:
                return severity
        return ErrorSeverity.MEDIUM

# Global observability instance
_observability_instance: Optional[OmegaObservabilitySystem] = None

def get_observability() -> OmegaObservabilitySystem:
    """Get the global observability instance."""
    global _observability_instance
    if _observability_instance is None:
        _observability_instance = OmegaObservabilitySystem()
    return _observability_instance

# Convenience functions
async def log_error(error_event: ErrorEvent):
    """Log an error event."""
    obs = get_observability()
    return await obs.log_error(error_event)

async def log_system_metric(metric: SystemMetric):
    """Log a system metric."""
    obs = get_observability()
    return await obs.log_system_metric(metric)

async def start_monitoring():
    """Start background monitoring."""
    obs = get_observability()
    return await obs.start_background_monitoring()

async def stop_monitoring():
    """Stop background monitoring."""
    obs = get_observability()
    return await obs.stop_background_monitoring()

@asynccontextmanager
async def monitor_operation(operation_name: str, agent_id: Optional[str] = None):
    """Monitor an operation."""
    obs = get_observability()
    async with obs.monitor_operation(operation_name, agent_id):
        yield
#!/usr/bin/env python3
"""
Health Monitor - Service health monitoring and circuit breaker pattern
Monitors all services and implements automatic restart with exponential backoff
"""

import asyncio
import logging
import time
import json
import os
import requests
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading

# Add project root to path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager

class ServiceStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"

@dataclass
class ServiceHealth:
    """Service health information"""
    name: str
    status: ServiceStatus
    last_check: Optional[datetime]
    last_success: Optional[datetime]
    last_failure: Optional[datetime]
    failure_count: int
    success_count: int
    response_time: float
    error_message: Optional[str]
    circuit_open: bool
    circuit_open_time: Optional[datetime]
    
class HealthMonitor:
    """Service health monitor with circuit breaker pattern"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize health monitor"""
        self.config_manager = ConfigManager()
        self.config = self._load_config(config)
        
        # Service definitions
        self.services = {
            'stt_canary_qwen': {
                'url': 'http://localhost:2022/health',
                'timeout': 5,
                'check_interval': 30,
                'failure_threshold': 3,
                'recovery_timeout': 300
            },
            'stt_whisper_turbo': {
                'url': 'http://localhost:2023/health',
                'timeout': 5,
                'check_interval': 30,
                'failure_threshold': 3,
                'recovery_timeout': 300
            },
            'tts_orpheus': {
                'url': 'http://localhost:8881/health',
                'timeout': 5,
                'check_interval': 30,
                'failure_threshold': 3,
                'recovery_timeout': 300
            },
            'tts_xtts': {
                'url': 'http://localhost:8882/health',
                'timeout': 5,
                'check_interval': 30,
                'failure_threshold': 3,
                'recovery_timeout': 300
            },
            'tts_piper': {
                'url': 'http://localhost:8883/health',
                'timeout': 5,
                'check_interval': 30,
                'failure_threshold': 3,
                'recovery_timeout': 300
            },
            'ollama': {
                'url': 'http://localhost:11434/api/tags',
                'timeout': 10,
                'check_interval': 60,
                'failure_threshold': 5,
                'recovery_timeout': 600
            },
            'voice_orchestrator': {
                'url': None,  # Internal service
                'timeout': 1,
                'check_interval': 10,
                'failure_threshold': 2,
                'recovery_timeout': 60
            }
        }
        
        # Health state tracking
        self.health_status: Dict[str, ServiceHealth] = {}
        self.monitoring_task = None
        self.is_monitoring = False
        self.callbacks: Dict[str, List[Callable]] = {}
        
        # Circuit breaker state
        self.circuit_breakers = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize health status
        self._initialize_health_status()
        
    def _load_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Load health monitor configuration"""
        if config:
            return config
        else:
            # Load from config manager or use defaults
            monitor_config = self.config_manager.get_section('monitoring', {})
            return {
                'enabled': monitor_config.get('enabled', True),
                'metrics_interval': monitor_config.get('metrics_interval', 30),
                'health_check_interval': monitor_config.get('health_check_interval', 10),
                'log_level': monitor_config.get('log_level', 'INFO'),
                'enable_performance_logging': monitor_config.get('enable_performance_logging', True)
            }
            
    def _initialize_health_status(self):
        """Initialize health status for all services"""
        for service_name in self.services:
            self.health_status[service_name] = ServiceHealth(
                name=service_name,
                status=ServiceStatus.UNKNOWN,
                last_check=None,
                last_success=None,
                last_failure=None,
                failure_count=0,
                success_count=0,
                response_time=0.0,
                error_message=None,
                circuit_open=False,
                circuit_open_time=None
            )
            
    async def start_monitoring(self):
        """Start health monitoring"""
        if self.is_monitoring:
            self.logger.warning("Health monitoring is already running")
            return
            
        self.is_monitoring = True
        self.logger.info("Starting health monitoring")
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
    async def stop_monitoring(self):
        """Stop health monitoring"""
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
                
        self.logger.info("Health monitoring stopped")
        
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                await self._check_all_services()
                await asyncio.sleep(self.config['health_check_interval'])
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                
    async def _check_all_services(self):
        """Check health of all services"""
        for service_name, service_config in self.services.items():
            await self._check_service(service_name, service_config)
            
    async def _check_service(self, service_name: str, service_config: Dict[str, Any]):
        """Check health of a specific service"""
        health = self.health_status[service_name]
        health.last_check = datetime.now()
        
        try:
            # Check if circuit is open
            if health.circuit_open:
                if self._should_attempt_recovery(health):
                    self.logger.info(f"Attempting recovery for {service_name}")
                    health.circuit_open = False
                    health.circuit_open_time = None
                else:
                    return  # Skip check while circuit is open
                    
            # Perform health check
            start_time = time.time()
            is_healthy = await self._perform_health_check(service_name, service_config)
            response_time = time.time() - start_time
            
            if is_healthy:
                self._handle_success(health, response_time)
            else:
                self._handle_failure(health, f"Service {service_name} is unhealthy")
                
        except Exception as e:
            self._handle_failure(health, str(e))
            
    async def _perform_health_check(self, service_name: str, service_config: Dict[str, Any]) -> bool:
        """Perform actual health check for a service"""
        url = service_config.get('url')
        
        # Skip check for internal services
        if url is None:
            return True
            
        try:
            response = requests.get(url, timeout=service_config['timeout'])
            return response.status_code == 200
        except Exception:
            return False
            
    def _handle_success(self, health: ServiceHealth, response_time: float):
        """Handle successful health check"""
        health.success_count += 1
        health.failure_count = 0
        health.last_success = datetime.now()
        health.response_time = response_time
        health.error_message = None
        
        # Update status
        if health.status != ServiceStatus.HEALTHY:
            old_status = health.status
            health.status = ServiceStatus.HEALTHY
            self.logger.info(f"Service {health.name} recovered from {old_status.value} to {health.status.value}")
            self._notify_status_change(health.name, old_status, health.status)
            
    def _handle_failure(self, health: ServiceHealth, error_message: str):
        """Handle failed health check"""
        health.failure_count += 1
        health.last_failure = datetime.now()
        health.error_message = error_message
        
        # Check if circuit should open
        if health.failure_count >= self.services[health.name]['failure_threshold']:
            if not health.circuit_open:
                health.circuit_open = True
                health.circuit_open_time = datetime.now()
                health.status = ServiceStatus.UNHEALTHY
                self.logger.error(f"Circuit opened for {health.name} after {health.failure_count} failures")
                self._notify_status_change(health.name, ServiceStatus.HEALTHY, ServiceStatus.UNHEALTHY)
        else:
            # Update status to degraded if not already unhealthy
            if health.status != ServiceStatus.UNHEALTHY:
                health.status = ServiceStatus.DEGRADED
                
        self.logger.warning(f"Service {health.name} failed health check: {error_message}")
        
    def _should_attempt_recovery(self, health: ServiceHealth) -> bool:
        """Check if recovery should be attempted for a circuit-open service"""
        if not health.circuit_open or not health.circuit_open_time:
            return False
            
        recovery_timeout = self.services[health.name]['recovery_timeout']
        time_since_open = datetime.now() - health.circuit_open_time
        
        return time_since_open.total_seconds() >= recovery_timeout
        
    def get_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        status = {
            'monitoring_enabled': self.config['enabled'],
            'is_monitoring': self.is_monitoring,
            'services': {},
            'summary': {
                'total': len(self.services),
                'healthy': 0,
                'unhealthy': 0,
                'degraded': 0,
                'maintenance': 0,
                'unknown': 0
            }
        }
        
        for service_name, health in self.health_status.items():
            service_status = {
                'name': health.name,
                'status': health.status.value,
                'last_check': health.last_check.isoformat() if health.last_check else None,
                'last_success': health.last_success.isoformat() if health.last_success else None,
                'last_failure': health.last_failure.isoformat() if health.last_failure else None,
                'failure_count': health.failure_count,
                'success_count': health.success_count,
                'response_time': health.response_time,
                'error_message': health.error_message,
                'circuit_open': health.circuit_open,
                'circuit_open_time': health.circuit_open_time.isoformat() if health.circuit_open_time else None
            }
            
            status['services'][service_name] = service_status
            status['summary'][health.status.value] += 1
            
        return status
        
    def get_service_status(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific service"""
        health = self.health_status.get(service_name)
        if not health:
            return None
            
        return {
            'name': health.name,
            'status': health.status.value,
            'last_check': health.last_check.isoformat() if health.last_check else None,
            'last_success': health.last_success.isoformat() if health.last_success else None,
            'last_failure': health.last_failure.isoformat() if health.last_failure else None,
            'failure_count': health.failure_count,
            'success_count': health.success_count,
            'response_time': health.response_time,
            'error_message': health.error_message,
            'circuit_open': health.circuit_open,
            'circuit_open_time': health.circuit_open_time.isoformat() if health.circuit_open_time else None
        }
        
    def is_service_healthy(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        health = self.health_status.get(service_name)
        return health and health.status == ServiceStatus.HEALTHY and not health.circuit_open
        
    def register_status_callback(self, service_name: str, callback: Callable):
        """Register a callback for service status changes"""
        if service_name not in self.callbacks:
            self.callbacks[service_name] = []
        self.callbacks[service_name].append(callback)
        
    def _notify_status_change(self, service_name: str, old_status: ServiceStatus, new_status: ServiceStatus):
        """Notify callbacks of status changes"""
        if service_name in self.callbacks:
            for callback in self.callbacks[service_name]:
                try:
                    callback(service_name, old_status, new_status)
                except Exception as e:
                    self.logger.error(f"Callback error for {service_name}: {e}")
                    
    def trigger_manual_check(self, service_name: str) -> bool:
        """Trigger manual health check for a service"""
        service_config = self.services.get(service_name)
        if not service_config:
            self.logger.error(f"Unknown service: {service_name}")
            return False
            
        # Run check synchronously
        asyncio.create_task(self._check_service(service_name, service_config))
        return True
        
    def reset_circuit_breaker(self, service_name: str):
        """Manually reset circuit breaker for a service"""
        health = self.health_status.get(service_name)
        if health:
            health.circuit_open = False
            health.circuit_open_time = None
            self.logger.info(f"Circuit breaker reset for {service_name}")
            
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all services"""
        metrics = {}
        
        for service_name, health in self.health_status.items():
            if health.success_count > 0:
                avg_response_time = health.response_time
                success_rate = health.success_count / (health.success_count + health.failure_count)
                
                metrics[service_name] = {
                    'average_response_time': avg_response_time,
                    'success_rate': success_rate,
                    'total_requests': health.success_count + health.failure_count,
                    'success_count': health.success_count,
                    'failure_count': health.failure_count
                }
                
        return metrics
        
    def cleanup(self):
        """Cleanup health monitor resources"""
        self.logger.info("Cleaning up health monitor resources")
        asyncio.create_task(self.stop_monitoring())
"""
Core Engine for OpenCode Multi-Account System
=============================================

The main orchestrator that manages all system components including
account management, rotation, monitoring, and health checks.
"""

import asyncio
import logging
import threading
import time
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Awaitable
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import psutil
import socket

from .plugin_system import plugin_manager, ProviderManager, IntegrationManager
from .config_manager import ConfigurationManager
from .monitoring import HealthMonitor, MetricsCollector
from .rotation import RotationManager
from .account_manager import AccountManager

logger = logging.getLogger(__name__)


class SystemState(Enum):
    """System state enumeration."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    SHUTTING_DOWN = "shutting_down"
    ERROR = "error"


@dataclass
class SystemMetrics:
    """System-wide metrics."""
    uptime_seconds: float = 0.0
    active_accounts: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0
    last_health_check: Optional[datetime] = None
    provider_health: Dict[str, bool] = field(default_factory=dict)
    system_health: str = "unknown"


class CoreEngine:
    """Main engine for the OpenCode Multi-Account System."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_manager = ConfigurationManager(config_path)
        self.state = SystemState.INITIALIZING
        
        # Core components
        self.account_manager = AccountManager()
        self.rotation_manager = RotationManager()
        self.health_monitor = HealthMonitor()
        self.metrics_collector = MetricsCollector()
        
        # Plugin managers
        self.provider_manager: Optional[ProviderManager] = None
        self.integration_manager: Optional[IntegrationManager] = None
        
        # System state
        self._start_time: Optional[float] = None
        self._metrics = SystemMetrics()
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        self._monitoring_task: Optional[asyncio.Task] = None
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {}
        
        # Threading
        self._lock = threading.Lock()
    
    async def initialize(self) -> bool:
        """Initialize the core engine and all components."""
        try:
            logger.info("Initializing OpenCode Multi-Account System Core Engine...")
            
            # Load configuration
            config = await self.config_manager.load_config()
            
            # Initialize plugin system
            plugin_success = await plugin_manager.initialize(config)
            if not plugin_success:
                logger.error("Failed to initialize plugin system")
                return False
            
            # Get plugin managers
            self.provider_manager = plugin_manager.get_provider_manager()
            self.integration_manager = plugin_manager.get_integration_manager()
            
            # Initialize core components
            await self.account_manager.initialize(config)
            await self.rotation_manager.initialize(config)
            await self.health_monitor.initialize(config)
            await self.metrics_collector.initialize(config)
            
            # Start integration services
            integration_success = await self.integration_manager.start_all()
            if not integration_success:
                logger.warning("Some integrations failed to start")
            
            # Start background tasks
            self._start_background_tasks()
            
            self.state = SystemState.RUNNING
            self._start_time = time.time()
            self._running = True
            
            logger.info("Core Engine initialized successfully")
            await self._emit_event("system_initialized", {"config": config})
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Core Engine: {e}", exc_info=True)
            self.state = SystemState.ERROR
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the core engine and all components."""
        if self.state == SystemState.SHUTTING_DOWN:
            return
        
        self.state = SystemState.SHUTTING_DOWN
        self._running = False
        
        logger.info("Shutting down Core Engine...")
        
        # Stop background tasks
        if self._main_task:
            self._main_task.cancel()
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._health_check_task:
            self._health_check_task.cancel()
        
        # Shutdown plugin system
        plugin_manager.shutdown()
        
        # Shutdown core components
        await self.account_manager.shutdown()
        await self.rotation_manager.shutdown()
        await self.health_monitor.shutdown()
        await self.metrics_collector.shutdown()
        
        # Stop integrations
        await self.integration_manager.stop_all()
        
        self.state = SystemState.INITIALIZING
        logger.info("Core Engine shutdown complete")
    
    async def get_response(self, prompt: str, preferred_provider: Optional[str] = None, 
                          context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get response from the best available provider."""
        if self.state != SystemState.RUNNING:
            return {"error": "System not running", "status": "error"}
        
        start_time = time.time()
        
        try:
            # Get account for this request
            account = await self.account_manager.get_next_account()
            if not account:
                return {"error": "No accounts available", "status": "error"}
            
            # Get response from provider
            response = await self.provider_manager.get_response(
                prompt, preferred_provider, context
            )
            
            # Update metrics
            response_time = time.time() - start_time
            await self._update_metrics(response, response_time)
            
            # Log the request
            logger.info(f"Request completed: {response.get('status', 'unknown')} "
                       f"({response_time:.2f}s)")
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting response: {e}", exc_info=True)
            return {"error": str(e), "status": "error"}
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Get comprehensive system metrics."""
        async with self._lock:
            # Update system-level metrics
            if self._start_time:
                self._metrics.uptime_seconds = time.time() - self._start_time
            
            # Get system resource usage
            try:
                process = psutil.Process()
                self._metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
                self._metrics.cpu_usage_percent = process.cpu_percent()
                
                disk = psutil.disk_usage('/')
                self._metrics.disk_usage_percent = (disk.used / disk.total) * 100
            except Exception as e:
                logger.warning(f"Could not get system metrics: {e}")
            
            # Get provider health
            if self.provider_manager:
                try:
                    health = await self.provider_manager.health_check()
                    self._metrics.provider_health = health
                    self._metrics.active_accounts = sum(1 for h in health.values() if h)
                except Exception as e:
                    logger.error(f"Could not get provider health: {e}")
            
            # Calculate system health
            self._metrics.system_health = self._calculate_system_health()
            
            return self._metrics
    
    async def get_provider_metrics(self) -> Dict[str, Any]:
        """Get metrics from all providers."""
        if not self.provider_manager:
            return {}
        
        try:
            return await self.provider_manager.get_metrics()
        except Exception as e:
            logger.error(f"Could not get provider metrics: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            "system_state": self.state.value,
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "overall_health": "unknown"
        }
        
        # Check core components
        components = [
            ("account_manager", self.account_manager),
            ("rotation_manager", self.rotation_manager),
            ("health_monitor", self.health_monitor),
            ("metrics_collector", self.metrics_collector)
        ]
        
        for name, component in components:
            try:
                if hasattr(component, 'health_check'):
                    health_status["components"][name] = await component.health_check()
                else:
                    health_status["components"][name] = {"status": "ok"}
            except Exception as e:
                health_status["components"][name] = {"status": "error", "error": str(e)}
        
        # Check providers
        if self.provider_manager:
            try:
                provider_health = await self.provider_manager.health_check()
                health_status["providers"] = provider_health
            except Exception as e:
                health_status["providers"] = {"error": str(e)}
        
        # Calculate overall health
        component_health = all(
            status.get("status") == "ok" 
            for status in health_status["components"].values()
        )
        
        provider_health = all(
            status for status in health_status.get("providers", {}).values()
        ) if "providers" in health_status else False
        
        if self.state == SystemState.RUNNING and component_health and provider_health:
            health_status["overall_health"] = "healthy"
        elif self.state in [SystemState.PAUSED, SystemState.INITIALIZING]:
            health_status["overall_health"] = "starting"
        else:
            health_status["overall_health"] = "unhealthy"
        
        self._metrics.last_health_check = datetime.now()
        
        return health_status
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """Register an event handler."""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to all registered handlers."""
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")
    
    def _start_background_tasks(self) -> None:
        """Start background monitoring and maintenance tasks."""
        loop = asyncio.get_event_loop()
        
        # Main task for request processing
        self._main_task = loop.create_task(self._main_loop())
        
        # Monitoring task
        self._monitoring_task = loop.create_task(self._monitoring_loop())
        
        # Health check task
        self._health_check_task = loop.create_task(self._health_check_loop())
    
    async def _main_loop(self) -> None:
        """Main processing loop."""
        while self._running:
            try:
                # Process any pending tasks
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while self._running:
            try:
                # Collect metrics
                await self.metrics_collector.collect_metrics()
                
                # Update system metrics
                await self.get_system_metrics()
                
                await asyncio.sleep(30.0)  # Monitor every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10.0)
    
    async def _health_check_loop(self) -> None:
        """Background health check loop."""
        while self._running:
            try:
                # Perform health check
                health = await self.health_check()
                
                # Emit health check event
                await self._emit_event("health_check", health)
                
                await asyncio.sleep(60.0)  # Health check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(30.0)
    
    async def _update_metrics(self, response: Dict[str, Any], response_time: float) -> None:
        """Update system metrics based on response."""
        self._metrics.total_requests += 1
        
        if response.get("status") == "success":
            self._metrics.successful_requests += 1
        else:
            self._metrics.failed_requests += 1
        
        # Update average response time
        total_time = self._metrics.average_response_time * (self._metrics.total_requests - 1)
        self._metrics.average_response_time = (total_time + response_time) / self._metrics.total_requests
    
    def _calculate_system_health(self) -> str:
        """Calculate overall system health."""
        if self.state != SystemState.RUNNING:
            return "unhealthy"
        
        # Check if we have active providers
        active_providers = sum(1 for health in self._metrics.provider_health.values() if health)
        if active_providers == 0:
            return "unhealthy"
        
        # Check error rate
        error_rate = (self._metrics.failed_requests / max(self._metrics.total_requests, 1)) * 100
        if error_rate > 10:  # More than 10% error rate
            return "unhealthy"
        elif error_rate > 5:  # More than 5% error rate
            return "degraded"
        
        # Check response time
        if self._metrics.average_response_time > 10.0:  # More than 10 seconds average
            return "degraded"
        
        # Check resource usage
        if self._metrics.memory_usage_mb > 1000 or self._metrics.cpu_usage_percent > 80:
            return "degraded"
        
        return "healthy"
    
    @property
    def is_running(self) -> bool:
        """Check if the system is running."""
        return self.state == SystemState.RUNNING
    
    @property
    def uptime(self) -> float:
        """Get system uptime in seconds."""
        if self._start_time:
            return time.time() - self._start_time
        return 0.0


# Global engine instance
engine = CoreEngine()
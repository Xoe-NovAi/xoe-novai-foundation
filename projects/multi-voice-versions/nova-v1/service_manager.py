#!/usr/bin/env python3
"""
Service Manager - Manages Ollama, STT, TTS, and other external services
Auto-starts services, monitors health, and provides unified service interface
"""

import asyncio
import subprocess
import logging
import json
import time
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import requests

logger = logging.getLogger(__name__)


class ServiceType(Enum):
    """Types of services"""
    OLLAMA = "ollama"
    STT = "stt"
    TTS = "tts"
    HEALTH_MONITOR = "health_monitor"


class ServiceStatus(Enum):
    """Service status"""
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"


@dataclass
class ServiceInfo:
    """Information about a service"""
    name: str
    type: ServiceType
    status: ServiceStatus
    port: Optional[int] = None
    pid: Optional[int] = None
    error: Optional[str] = None
    health_url: Optional[str] = None
    startup_command: Optional[str] = None


class ServiceManager:
    """Unified service management"""

    def __init__(self):
        """Initialize service manager"""
        self.services: Dict[str, ServiceInfo] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.health_check_interval = 30  # seconds
        self.monitoring_active = False
        self._setup_services()

    def _setup_services(self):
        """Setup known services"""
        services_config = [
            {
                "name": "ollama",
                "type": ServiceType.OLLAMA,
                "port": 11434,
                "health_url": "http://localhost:11434/api/tags",
                "startup_command": self._get_ollama_command(),
            },
        ]

        for config in services_config:
            service = ServiceInfo(
                name=config["name"],
                type=config["type"],
                status=ServiceStatus.STOPPED,
                port=config.get("port"),
                health_url=config.get("health_url"),
                startup_command=config.get("startup_command"),
            )
            self.services[config["name"]] = service

    def _get_ollama_command(self) -> str:
        """Get Ollama startup command based on platform"""
        import platform
        system = platform.system()

        if system == "Darwin":  # macOS
            # Check if Ollama is installed as app or brew
            if os.path.exists("/Applications/Ollama.app"):
                return "open -a Ollama"
            else:
                return "ollama serve"
        elif system == "Linux":
            return "ollama serve"
        elif system == "Windows":
            return "ollama serve"
        else:
            return "ollama serve"

    async def start_service(self, service_name: str, wait_for_ready: bool = True) -> bool:
        """Start a service
        
        Args:
            service_name: Name of service to start
            wait_for_ready: Wait for service to be ready
        
        Returns:
            True if service started successfully
        """
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False

        service = self.services[service_name]

        if service.status == ServiceStatus.RUNNING:
            logger.info(f"Service {service_name} already running")
            return True

        try:
            service.status = ServiceStatus.STARTING
            logger.info(f"Starting service {service_name}...")

            if service_name == "ollama":
                return await self._start_ollama(wait_for_ready)
            else:
                logger.warning(f"No startup logic for service {service_name}")
                return False

        except Exception as e:
            service.status = ServiceStatus.ERROR
            service.error = str(e)
            logger.error(f"Failed to start {service_name}: {e}")
            return False

    async def _start_ollama(self, wait_for_ready: bool = True) -> bool:
        """Start Ollama service"""
        service = self.services["ollama"]

        try:
            # Check if already running
            if await self._check_service_health("ollama"):
                service.status = ServiceStatus.RUNNING
                logger.info("Ollama already running")
                return True

            # Start Ollama
            cmd = service.startup_command
            if not cmd:
                logger.error("No startup command for Ollama")
                return False

            logger.info(f"Executing: {cmd}")

            # On macOS, 'open -a Ollama' starts the app asynchronously
            if cmd == "open -a Ollama":
                subprocess.Popen(cmd, shell=True)
            else:
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.processes["ollama"] = process
                service.pid = process.pid

            # Wait for service to be ready
            if wait_for_ready:
                for attempt in range(30):  # 30 seconds max
                    await asyncio.sleep(1)
                    if await self._check_service_health("ollama"):
                        service.status = ServiceStatus.RUNNING
                        logger.info("Ollama is ready")
                        return True
                    logger.debug(f"Waiting for Ollama... ({attempt + 1}/30)")

                # Timeout
                logger.error("Ollama startup timeout")
                service.status = ServiceStatus.ERROR
                service.error = "Startup timeout"
                return False
            else:
                service.status = ServiceStatus.RUNNING
                return True

        except Exception as e:
            service.status = ServiceStatus.ERROR
            service.error = str(e)
            logger.error(f"Error starting Ollama: {e}")
            return False

    async def stop_service(self, service_name: str) -> bool:
        """Stop a service
        
        Args:
            service_name: Name of service to stop
        
        Returns:
            True if service stopped successfully
        """
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False

        service = self.services[service_name]

        if service.status == ServiceStatus.STOPPED:
            return True

        try:
            service.status = ServiceStatus.STOPPING
            logger.info(f"Stopping service {service_name}...")

            if service_name in self.processes:
                process = self.processes[service_name]
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                del self.processes[service_name]

            service.status = ServiceStatus.STOPPED
            service.pid = None
            logger.info(f"Service {service_name} stopped")
            return True

        except Exception as e:
            service.status = ServiceStatus.ERROR
            service.error = str(e)
            logger.error(f"Error stopping {service_name}: {e}")
            return False

    async def _check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy
        
        Args:
            service_name: Name of service to check
        
        Returns:
            True if service is healthy
        """
        if service_name not in self.services:
            return False

        service = self.services[service_name]

        if not service.health_url:
            return False

        try:
            response = requests.get(service.health_url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    async def start_monitoring(self) -> None:
        """Start background service monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        logger.info("Starting service monitoring")

        try:
            while self.monitoring_active:
                await self._check_all_services()
                await asyncio.sleep(self.health_check_interval)
        except asyncio.CancelledError:
            pass
        finally:
            self.monitoring_active = False

    async def _check_all_services(self) -> None:
        """Check health of all services"""
        for service_name, service in self.services.items():
            if service.status == ServiceStatus.RUNNING:
                if not await self._check_service_health(service_name):
                    service.status = ServiceStatus.ERROR
                    service.error = "Health check failed"
                    logger.warning(f"Service {service_name} failed health check")

    async def stop_monitoring(self) -> None:
        """Stop service monitoring"""
        self.monitoring_active = False
        logger.info("Stopping service monitoring")

    async def ensure_service_running(
        self, service_name: str, start_if_needed: bool = True
    ) -> bool:
        """Ensure a service is running
        
        Args:
            service_name: Name of service
            start_if_needed: Start service if not running
        
        Returns:
            True if service is running
        """
        if service_name not in self.services:
            return False

        service = self.services[service_name]

        if service.status == ServiceStatus.RUNNING:
            # Verify it's actually healthy
            if await self._check_service_health(service_name):
                return True

        if start_if_needed:
            return await self.start_service(service_name)

        return False

    async def get_all_services_status(self) -> Dict[str, Any]:
        """Get status of all services
        
        Returns:
            Dictionary with service statuses
        """
        status = {}
        for name, service in self.services.items():
            status[name] = {
                "name": service.name,
                "type": service.type.value,
                "status": service.status.value,
                "port": service.port,
                "pid": service.pid,
                "error": service.error,
                "healthy": await self._check_service_health(name),
            }
        return status

    async def shutdown(self) -> None:
        """Shutdown all services"""
        logger.info("Shutting down service manager")
        await self.stop_monitoring()

        for service_name in list(self.services.keys()):
            await self.stop_service(service_name)


# Global service manager instance
_service_manager: Optional[ServiceManager] = None


def get_service_manager() -> ServiceManager:
    """Get global service manager instance"""
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager()
    return _service_manager


async def ensure_services_ready(services: List[str] = None) -> bool:
    """Ensure required services are running
    
    Args:
        services: List of service names to ensure (None = all)
    
    Returns:
        True if all services are ready
    """
    if services is None:
        services = ["ollama"]

    manager = get_service_manager()

    for service in services:
        logger.info(f"Ensuring {service} is ready...")
        if not await manager.ensure_service_running(service):
            logger.error(f"Failed to ensure {service} is running")
            return False

    return True


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    async def test():
        manager = get_service_manager()
        
        # Start monitoring
        monitor_task = asyncio.create_task(manager.start_monitoring())
        
        try:
            # Check initial status
            status = await manager.get_all_services_status()
            print("Initial status:", json.dumps(status, indent=2))
            
            # Ensure Ollama is running
            print("\nEnsuring Ollama is running...")
            if await manager.ensure_service_running("ollama"):
                print("Ollama is ready!")
            
            # Check status again
            status = await manager.get_all_services_status()
            print("\nFinal status:", json.dumps(status, indent=2))
            
        finally:
            await manager.stop_monitoring()
            await manager.shutdown()

    asyncio.run(test())

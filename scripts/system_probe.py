#!/usr/bin/env python3
"""
XNAi System Probe - Environmental Awareness Utility (v1.0.0)
===========================================================

Allows agents to "look around" their environment. Detects:
- Host hardware (CPU, RAM, Disk)
- Active Services (via local ports)
- Project Structure & Knowledge Hub state
- Model Server Availability
"""

import os
import sys
import json
import socket
import platform
import subprocess
from datetime import datetime
from typing import Dict, Any

# Optional psutil for richer hardware metrics
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class SystemProbe:
    def __init__(self):
        self.timestamp = datetime.now().isoformat()

    def probe_hardware(self) -> Dict[str, Any]:
        """Detect local hardware constraints."""
        hw_stats = {
            "os": platform.system(),
            "release": platform.release(),
            "cpu_count": os.cpu_count(),
        }
        
        if PSUTIL_AVAILABLE:
            vm = psutil.virtual_memory()
            du = psutil.disk_usage('/')
            hw_stats.update({
                "ram_total_gb": round(vm.total / (1024**3), 2),
                "ram_available_gb": round(vm.available / (1024**3), 2),
                "disk_free_gb": round(du.free / (1024**3), 2),
                "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else "N/A"
            })
        else:
            hw_stats["ram_total_gb"] = "psutil_missing"
            
        return hw_stats

    def probe_services(self) -> Dict[str, Any]:
        """Detect active ports and service health."""
        critical_ports = {
            8000: "Caddy Gateway",
            8001: "Chainlit UI",
            8080: "BookLore/Open WebUI",
            6333: "Qdrant",
            5432: "PostgreSQL",
            6379: "Redis"
        }
        active_services = {}
        for port, name in critical_ports.items():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                is_open = s.connect_ex(('127.0.0.1', port)) == 0
                active_services[name] = "running" if is_open else "stopped"
        return active_services

    def probe_stack_state(self) -> Dict[str, Any]:
        """Detect the state of the Foundation Knowledge Hub."""
        lib_path = "library/sorted"
        return {
            "docs_present": os.path.exists("docs/KNOWLEDGE-HUB.md"),
            "library_count": len(os.listdir(lib_path)) if os.path.exists(lib_path) else 0,
            "expert_registry_exists": os.path.exists("scripts/initialize_experts.py"),
            "agent_os_memory_active": os.path.exists("app/XNAi_rag_app/core/agent_memory.py")
        }

    def run(self):
        report = {
            "timestamp": self.timestamp,
            "hardware": self.probe_hardware(),
            "services": self.probe_services(),
            "stack_state": self.probe_stack_state()
        }
        print(json.dumps(report, indent=2))
        return report

if __name__ == "__main__":
    probe = SystemProbe()
    probe.run()

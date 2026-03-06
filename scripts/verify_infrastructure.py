#!/usr/bin/env python3
"""
XNAi Foundation Infrastructure Verification Script
Checks the status of all core services and reports completion status
"""

import requests
import json
import time
from typing import Dict, List, Tuple

# Service definitions with expected ports and health endpoints
SERVICES = {
    "consul": {
        "port": 8500,
        "endpoint": "/v1/status/leader",
        "description": "Service Discovery & Health Monitoring"
    },
    "redis": {
        "port": 6379,
        "endpoint": None,
        "description": "Cache & Streams Coordinator"
    },
    "victoriametrics": {
        "port": 8428,
        "endpoint": "/health",
        "description": "Time-Series Metrics Storage"
    },
    "openpipe": {
        "port": 3001,
        "endpoint": "/health",
        "description": "LLM Optimization Layer"
    },
    "qdrant": {
        "port": 6333,
        "endpoint": None,
        "description": "Vector Database"
    },
    "rag": {
        "port": 8000,
        "endpoint": "/health",
        "description": "FastAPI Backend"
    },
    "chainlit": {
        "port": 8001,
        "endpoint": "/",
        "description": "Voice-Enabled Frontend"
    },
    "vikunja-db": {
        "port": 5432,
        "endpoint": None,
        "description": "Project Management Database"
    },
    "vikunja": {
        "port": 3456,
        "endpoint": None,
        "description": "Project Management & Knowledge Base"
    },
    "caddy": {
        "port": 8000,
        "endpoint": "/config/",
        "description": "Unified Reverse Proxy"
    },
    "grafana": {
        "port": 3000,
        "endpoint": "/api/health",
        "description": "Observability Dashboards"
    }
}

def check_service(service_name: str, config: Dict) -> Tuple[bool, str]:
    """Check if a service is running and healthy"""
    try:
        if config["endpoint"]:
            url = f"http://localhost:{config['port']}{config['endpoint']}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True, "Healthy"
            return False, f"HTTP {response.status_code}"
        else:
            # For services without specific endpoints, just check if port is open
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('localhost', config['port']))
            sock.close()
            if result == 0:
                return True, "Port open"
            return False, "Port closed"
    except requests.exceptions.RequestException as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def check_local_models() -> Tuple[bool, str]:
    """Check for local GGUF models"""
    try:
        import os
        model_dir = "/models"
        if not os.path.exists(model_dir):
            return False, "Models directory not found"
        
        models = [f for f in os.listdir(model_dir) if f.endswith('.gguf')]
        if models:
            return True, f"Found {len(models)} models"
        return False, "No GGUF models found"
    except Exception as e:
        return False, str(e)

def check_cli_session_folders() -> Tuple[bool, str]:
    """Check for CLI session state folders"""
    try:
        import os
        user_home = os.path.expanduser("~")
        session_folders = [".cline", ".opencode", ".gemini"]
        found_folders = []
        
        for folder in session_folders:
            path = os.path.join(user_home, folder)
            if os.path.exists(path):
                found_folders.append(folder)
        
        if found_folders:
            return True, f"Found {len(found_folders)} CLI session folders"
        return False, "No CLI session folders found"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 80)
    print("XNAi Foundation Infrastructure Verification")
    print("=" * 80)
    print()
    
    # Check core services
    print("Checking core services...")
    healthy_services = 0
    for service, config in SERVICES.items():
        status, message = check_service(service, config)
        status_emoji = "✅" if status else "❌"
        print(f"  {status_emoji} {service:12} - {message}")
        if status:
            healthy_services += 1
    
    print()
    print(f"Core Services Health: {healthy_services}/{len(SERVICES)} services healthy")
    
    # Check local models
    print()
    print("Checking local model infrastructure...")
    status, message = check_local_models()
    status_emoji = "✅" if status else "❌"
    print(f"  {status_emoji} Local Models - {message}")
    
    # Check CLI session folders
    print()
    print("Checking CLI integration...")
    status, message = check_cli_session_folders()
    status_emoji = "✅" if status else "❌"
    print(f"  {status_emoji} CLI Session Folders - {message}")
    
    # Calculate completion status
    print()
    print("=" * 80)
    print("FINAL COMPLETION STATUS")
    print("=" * 80)
    
    # Calculate percentages
    core_services_complete = healthy_services / len(SERVICES) * 100
    local_models_complete = 100 if status else 0
    cli_integration_complete = 100 if status else 0
    
    # Overall completion calculation
    # Core services (40%) + Local models (30%) + CLI integration (30%)
    overall_completion = (core_services_complete * 0.4 + 
                         local_models_complete * 0.3 + 
                         cli_integration_complete * 0.3)
    
    print(f"Core Services: {core_services_complete:.1f}% complete")
    print(f"Local Model Infrastructure: {local_models_complete:.1f}% complete")
    print(f"CLI Integration: {cli_integration_complete:.1f}% complete")
    print()
    print(f"Overall Completion: {overall_completion:.1f}%")
    
    if overall_completion >= 95:
        print("XNAi Foundation is PRODUCTION-READY!")
        print("Ready for enterprise deployment with final enhancements")
    elif overall_completion >= 80:
        print("XNAi Foundation is PRODUCTION-READY with minor gaps")
        print("Ready for production with final enhancements")
    else:
        print("XNAi Foundation needs additional work")
        print("Not ready for production deployment")
    
    print()
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    if overall_completion < 95:
        print("CRITICAL GAPS:")
        if local_models_complete < 100:
            print("  - Deploy local GGUF models for offline capability")
        if cli_integration_complete < 100:
            print("  - Complete CLI session state integration")
        print()
    
    print("NEXT STEPS:")
    print("  - Deploy local GGUF models (24-48 hours)")
    print("  - Complete CLI integration documentation (24-48 hours)")
    print("  - Enhance observability with CLI metrics (1-2 weeks)")
    print("  - Document knowledge synthesis workflows (1-2 weeks)")
    print()
    print("STRATEGIC GOALS:")
    print("  - Implement agent bus system (2-4 weeks)")
    print("  - Add distributed tracing (2-4 weeks)")
    print("  - Optimize performance for Ryzen (2-4 weeks)")
    print("  - Harden security for zero-trust CLI (2-4 weeks)")
    
    print()
    print("=" * 80)
    print("SYSTEM INFORMATION")
    print("=" * 80)
    print(f"Script completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python version: {json.dumps({'version': platform.python_version()})}")
    print(f"Platform: {json.dumps({'system': platform.system(), 'release': platform.release()})}")
    print("=" * 80)

if __name__ == "__main__":
    import platform
    main()
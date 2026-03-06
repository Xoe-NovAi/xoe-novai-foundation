from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
import json
import subprocess
import sys
import os
from typing import Dict, Any, List
import psutil
import platform
from datetime import datetime
import logging
from pydantic import BaseModel
from enum import Enum
import socketio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Xoe-NovAi Omega Stack Installer",
    description="Beautiful modular installation system for Xoe-NovAi Omega Stack",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
sio_app = socketio.ASGIApp(sio)

class InstallationPhase(str, Enum):
    DISCOVERY = "discovery"
    INSTALLATION = "installation"
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    COMPLETE = "complete"

class ComponentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class SystemInfo(BaseModel):
    os: str
    cpu: str
    memory: str
    disk: str
    pythonVersion: str
    dockerAvailable: bool
    podmanAvailable: bool
    networkStatus: str

class InstallationProgress(BaseModel):
    phase: InstallationPhase
    currentStep: int
    totalSteps: int
    progress: float
    status: str
    message: str
    components: List[Dict[str, Any]]

# Global state
installation_state = {
    "is_running": False,
    "progress": InstallationProgress(
        phase=InstallationPhase.DISCOVERY,
        currentStep=0,
        totalSteps=0,
        progress=0.0,
        status="completed",
        message="Ready to install",
        components=[]
    )
}

async def broadcast_progress():
    """Broadcast current progress to all connected clients"""
    await sio.emit('installation_progress', installation_state["progress"].dict())

async def update_progress(phase: InstallationPhase, step: int, total: int, message: str, status: str = "running"):
    """Update installation progress and broadcast to clients"""
    installation_state["progress"] = InstallationProgress(
        phase=phase,
        currentStep=step,
        totalSteps=total,
        progress=(step / total) * 100 if total > 0 else 0,
        status=status,
        message=message,
        components=installation_state["progress"].components
    )
    await broadcast_progress()

async def run_command(command: str, description: str) -> bool:
    """Run a shell command and update progress"""
    try:
        logger.info(f"Running: {command}")
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            logger.info(f"✓ {description}")
            return True
        else:
            logger.error(f"✗ {description}: {stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return False

async def check_system_requirements():
    """Check if system meets minimum requirements"""
    try:
        # Check OS
        os_info = platform.system()
        
        # Check CPU
        cpu_info = platform.processor()
        cpu_count = psutil.cpu_count()
        
        # Check Memory
        memory = psutil.virtual_memory()
        memory_gb = round(memory.total / (1024**3), 1)
        
        # Check Disk
        disk = psutil.disk_usage('/')
        disk_gb = round(disk.free / (1024**3), 1)
        
        # Check Python version
        python_version = sys.version.split()[0]
        
        # Check Docker/Podman availability
        docker_available = await run_command("docker --version", "Checking Docker")
        podman_available = await run_command("podman --version", "Checking Podman")
        
        # Check network
        network_status = "online" if await run_command("ping -c 1 8.8.8.8", "Checking network") else "offline"
        
        system_info = SystemInfo(
            os=f"{os_info} {platform.release()}",
            cpu=f"{cpu_info} ({cpu_count} cores)",
            memory=f"{memory_gb} GB",
            disk=f"{disk_gb} GB free",
            pythonVersion=python_version,
            dockerAvailable=docker_available,
            podmanAvailable=podman_available,
            networkStatus=network_status
        )
        
        await sio.emit('system_info', system_info.dict())
        return system_info
        
    except Exception as e:
        logger.error(f"Error checking system requirements: {e}")
        return None

async def install_dependencies():
    """Install Python dependencies using existing wheelhouse system"""
    await update_progress(InstallationPhase.INSTALLATION, 1, 5, "Installing Python dependencies...")
    
    # Use existing wheelhouse system
    success = await run_command("make deps", "Installing dependencies from wheelhouse")
    
    if not success:
        # Fallback to pip
        success = await run_command("pip install -r requirements/requirements-api.txt", "Installing API dependencies")
        if success:
            success = await run_command("pip install -r requirements/requirements-chainlit.txt", "Installing Chainlit dependencies")
    
    return success

async def build_containers():
    """Build Docker/Podman containers using existing build system"""
    await update_progress(InstallationPhase.INSTALLATION, 2, 5, "Building container images...")
    
    # Use existing build system
    success = await run_command("make build", "Building container images with BuildKit")
    
    return success

async def setup_services(config: Dict[str, Any]):
    """Setup and configure services based on selection"""
    await update_progress(InstallationPhase.CONFIGURATION, 1, 3, "Configuring services...")
    
    # Generate docker-compose configuration based on selected services
    compose_config = generate_docker_compose(config)
    
    with open("docker-compose.installer.yml", "w") as f:
        f.write(compose_config)
    
    # Start selected services
    success = await run_command("podman-compose -f docker-compose.installer.yml up -d", "Starting services")
    
    return success

async def validate_installation():
    """Validate the installation"""
    await update_progress(InstallationPhase.VALIDATION, 1, 2, "Validating installation...")
    
    # Check if services are running
    services = ["rag-engine", "chainlit-ui", "redis-cache"]
    all_running = True
    
    for service in services:
        success = await run_command(f"podman ps --filter 'name={service}' --format 'table {{.Names}}\t{{.Status}}'", f"Checking {service}")
        if not success:
            all_running = False
    
    if all_running:
        await update_progress(InstallationPhase.VALIDATION, 2, 2, "Installation completed successfully!", "completed")
        await sio.emit('installation_complete')
    else:
        await update_progress(InstallationPhase.VALIDATION, 1, 2, "Some services failed to start", "failed")
        await sio.emit('installation_error', "Some services failed to start")
    
    return all_running

def generate_docker_compose(config: Dict[str, Any]) -> str:
    """Generate docker-compose configuration based on selected services"""
    services = config.get("services", [])
    providers = config.get("providers", [])
    
    compose = """
version: '3.8'
services:
"""
    
    # Core services (always included)
    compose += """
  rag-engine:
    image: xnai-rag-api:latest
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    depends_on:
      - redis-cache

  chainlit-ui:
    image: xnai-chainlit-ui:latest
    ports:
      - "8001:8001"
    environment:
      - CHAINLIT_HOST=0.0.0.0
      - CHAINLIT_PORT=8001
    volumes:
      - ./app:/app
    depends_on:
      - rag-engine

  redis-cache:
    image: redis:7.4.1
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
"""
    
    # Optional services
    if any(s["id"] == "postgres" and s["selected"] for s in services):
        compose += """
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: omega_stack
      POSTGRES_USER: omega
      POSTGRES_PASSWORD: omega_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
"""
    
    if any(s["id"] == "victoriametrics" and s["selected"] for s in services):
        compose += """
  victoriametrics:
    image: victoriametrics/victoria-metrics:latest
    ports:
      - "8428:8428"
    volumes:
      - vm_data:/victoria-metrics-data
"""
    
    compose += """
volumes:
  redis_data:
  postgres_data:
  vm_data:
"""
    
    return compose

@app.get("/")
async def root():
    return HTMLResponse("""
    <html>
        <head>
            <title>Xoe-NovAi Omega Stack Installer</title>
        </head>
        <body>
            <h1>Xoe-NovAi Omega Stack Installer</h1>
            <p>Backend server is running. Please use the frontend interface at <a href="http://localhost:3000">http://localhost:3000</a></p>
        </body>
    </html>
    """)

@app.post("/api/system-check")
async def system_check():
    """Perform system requirements check"""
    system_info = await check_system_requirements()
    if system_info:
        return {"success": True, "data": system_info}
    else:
        raise HTTPException(status_code=500, detail="Failed to check system requirements")

@app.post("/api/start-installation")
async def start_installation(config: Dict[str, Any]):
    """Start the installation process"""
    if installation_state["is_running"]:
        raise HTTPException(status_code=400, detail="Installation already in progress")
    
    installation_state["is_running"] = True
    
    try:
        # Phase 1: System Check
        await update_progress(InstallationPhase.DISCOVERY, 1, 1, "Checking system requirements...")
        system_info = await check_system_requirements()
        
        if not system_info:
            await update_progress(InstallationPhase.DISCOVERY, 1, 1, "System check failed", "failed")
            installation_state["is_running"] = False
            return {"success": False, "error": "System check failed"}
        
        # Phase 2: Dependencies
        success = await install_dependencies()
        if not success:
            await update_progress(InstallationPhase.INSTALLATION, 1, 5, "Failed to install dependencies", "failed")
            installation_state["is_running"] = False
            return {"success": False, "error": "Failed to install dependencies"}
        
        # Phase 3: Container Build
        success = await build_containers()
        if not success:
            await update_progress(InstallationPhase.INSTALLATION, 2, 5, "Failed to build containers", "failed")
            installation_state["is_running"] = False
            return {"success": False, "error": "Failed to build containers"}
        
        # Phase 4: Service Setup
        success = await setup_services(config)
        if not success:
            await update_progress(InstallationPhase.CONFIGURATION, 1, 3, "Failed to setup services", "failed")
            installation_state["is_running"] = False
            return {"success": False, "error": "Failed to setup services"}
        
        # Phase 5: Validation
        success = await validate_installation()
        
        installation_state["is_running"] = False
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Installation error: {e}")
        await update_progress(InstallationPhase.DISCOVERY, 1, 1, f"Installation failed: {str(e)}", "failed")
        installation_state["is_running"] = False
        return {"success": False, "error": str(e)}

@app.post("/api/pause-installation")
async def pause_installation():
    """Pause the installation process"""
    installation_state["is_running"] = False
    await update_progress(InstallationPhase.DISCOVERY, 1, 1, "Installation paused", "paused")
    return {"success": True}

@app.post("/api/cancel-installation")
async def cancel_installation():
    """Cancel the installation process"""
    installation_state["is_running"] = False
    await update_progress(InstallationPhase.DISCOVERY, 1, 1, "Installation cancelled", "failed")
    return {"success": True}

# Socket.IO events
@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")
    await sio.emit('installation_progress', installation_state["progress"].dict(), room=sid)

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

@sio.event
async def start_installation(sid, data):
    """Handle installation start via WebSocket"""
    await start_installation(data)

@sio.event
async def pause_installation(sid):
    """Handle installation pause via WebSocket"""
    await pause_installation()

@sio.event
async def cancel_installation(sid):
    """Handle installation cancel via WebSocket"""
    await cancel_installation()

if __name__ == "__main__":
    # Mount the frontend static files
    app.mount("/static", StaticFiles(directory="../frontend/dist"), name="static")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
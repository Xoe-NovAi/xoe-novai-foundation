#!/bin/bash
# Complete Voice Setup Installation Script
# Orchestrates installation of all components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root"
        exit 1
    fi
}

# Check system requirements
check_system_requirements() {
    header "System Requirements Check"
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log "Python version: $PYTHON_VERSION"
    
    # Check if Python version is >= 3.8
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        error "Python 3.8 or higher is required"
        exit 1
    fi
    
    # Check platform
    PLATFORM=$(uname -s)
    log "Platform: $PLATFORM"
    
    # Check available memory
    if [[ "$PLATFORM" == "Darwin" ]]; then
        TOTAL_MEM=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
    elif [[ "$PLATFORM" == "Linux" ]]; then
        TOTAL_MEM=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024/1024)}')
    else
        warning "Unable to determine available memory on this platform"
        TOTAL_MEM=8
    fi
    
    log "Total memory: ${TOTAL_MEM}GB"
    
    if [[ $TOTAL_MEM -lt 8 ]]; then
        warning "Recommended minimum 8GB RAM for optimal performance"
        warning "Some models may not run well with less memory"
    fi
    
    # Check disk space
    AVAILABLE_SPACE=$(df / | tail -1 | awk '{print int($4/1024/1024)}')
    log "Available disk space: ${AVAILABLE_SPACE}GB"
    
    if [[ $AVAILABLE_SPACE -lt 20 ]]; then
        error "Insufficient disk space. At least 20GB required for all models."
        exit 1
    fi
    
    # Check GPU (optional)
    if command -v nvidia-smi &> /dev/null; then
        log "NVIDIA GPU detected"
        NVIDIA_GPU=true
    elif [[ "$PLATFORM" == "Darwin" ]] && system_profiler SPDisplaysDataType | grep -q "Metal"; then
        log "Apple Silicon GPU detected"
        APPLE_SILICON=true
    else
        warning "No compatible GPU detected, will use CPU-only mode"
    fi
    
    success "System requirements check completed"
}

# Install system dependencies
install_system_dependencies() {
    header "Installing System Dependencies"
    
    PLATFORM=$(uname -s)
    
    case "$PLATFORM" in
        "Darwin")
            if ! command -v brew &> /dev/null; then
                error "Homebrew is required on macOS. Please install it first."
                exit 1
            fi
            
            log "Installing macOS dependencies..."
            brew update
            brew install portaudio ffmpeg libsndfile
            ;;
        "Linux")
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y portaudio19-dev ffmpeg libsndfile1-dev libasound2-dev
            elif command -v yum &> /dev/null; then
                sudo yum install -y portaudio-devel ffmpeg-devel libsndfile-devel alsa-lib-devel
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y portaudio-devel ffmpeg-devel libsndfile-devel alsa-lib-devel
            else
                warning "Package manager not detected. Please install portaudio, ffmpeg, libsndfile, and ALSA manually."
            fi
            ;;
        *)
            warning "Unsupported platform for automatic dependency installation"
            ;;
    esac
    
    success "System dependencies installed"
}

# Create project structure
create_project_structure() {
    header "Creating Project Structure"
    
    # Create main directories
    mkdir -p ~/.voice_models/{stt,tts,ollama}
    mkdir -p ~/.voice_services/{logs,config}
    mkdir -p ~/.voice_venv
    
    # Create installation scripts directory
    mkdir -p install_scripts
    
    success "Project structure created"
}

# Install STT models
install_stt_models() {
    header "Installing STT Models"
    
    log "Installing Canary Qwen 2.5B and Whisper Large V3 Turbo..."
    
    if [[ -f "install_scripts/install_stt.sh" ]]; then
        chmod +x install_scripts/install_stt.sh
        ./install_scripts/install_stt.sh
    else
        error "STT installation script not found"
        return 1
    fi
    
    success "STT models installation completed"
}

# Install TTS models
install_tts_models() {
    header "Installing TTS Models"
    
    log "Installing Orpheus TTS 3B, XTTS v2, and Piper..."
    
    if [[ -f "install_scripts/install_tts.sh" ]]; then
        chmod +x install_scripts/install_tts.sh
        ./install_scripts/install_tts.sh
    else
        error "TTS installation script not found"
        return 1
    fi
    
    success "TTS models installation completed"
}

# Install Ollama and LLMs
install_ollama() {
    header "Installing Ollama and Local LLMs"
    
    log "Installing Ollama and downloading local LLM models..."
    
    if [[ -f "install_scripts/install_ollama.sh" ]]; then
        chmod +x install_scripts/install_ollama.sh
        ./install_scripts/install_ollama.sh
    else
        error "Ollama installation script not found"
        return 1
    fi
    
    success "Ollama installation completed"
}

# Install Python dependencies
install_python_dependencies() {
    header "Installing Python Dependencies"
    
    log "Setting up Python virtual environment..."
    
    # Create virtual environment
    python3 -m venv ~/.voice_venv
    source ~/.voice_venv/bin/activate
    
    # Upgrade pip
    python -m pip install --upgrade pip setuptools wheel
    
    # Install core dependencies
    pip install numpy soundfile librosa pyaudio requests aiohttp torch torchaudio
    
    # Install model-specific dependencies
    pip install nemo_toolkit[asr] openai-whisper faster-whisper TTS==0.22.0 coqui-tts piper-tts transformers sentencepiece
    
    # Install web framework dependencies
    pip install fastapi uvicorn python-multipart
    
    # Install monitoring and configuration dependencies
    pip install psutil pyyaml
    
    success "Python dependencies installed"
}

# Create main configuration
create_main_configuration() {
    header "Creating Main Configuration"
    
    # Create main voice configuration
    cat > ~/.voice_config.json << 'EOF'
{
    "voice": {
        "llm_mode": "auto",
        "quality_mode": "balanced",
        "stt_model": "canary_qwen_2.5b",
        "tts_model": "orpheus_3b",
        "ollama_model": "llama3.2",
        "fallback_timeout": 5.0,
        "max_concurrent_requests": 3,
        "enable_voice_cloning": false
    },
    "stt": {
        "model": "canary_qwen_2.5b",
        "confidence_threshold": 0.8,
        "max_audio_duration": 30.0,
        "silence_timeout": 2.0,
        "enable_vad": true,
        "vad_aggressiveness": 2,
        "language": "en",
        "fallback_models": ["whisper_large_v3_turbo", "piper"]
    },
    "tts": {
        "model": "orpheus_3b",
        "voice": "default",
        "speed": 1.0,
        "pitch": 1.0,
        "volume": 1.0,
        "emotion": "neutral",
        "enable_voice_cloning": false,
        "max_text_length": 2000,
        "streaming_enabled": true,
        "fallback_models": ["xtts_v2", "piper", "kokoro"]
    },
    "ollama": {
        "host": "localhost",
        "port": 11434,
        "model": "llama3.2",
        "timeout": 120,
        "max_tokens": 2000,
        "temperature": 0.7,
        "top_p": 0.9,
        "stream": true,
        "enable_context": true,
        "context_size": 10,
        "fallback_models": ["llama3.1", "mistral", "gemma2", "phi3"]
    },
    "audio": {
        "sample_rate": 16000,
        "channels": 1,
        "format": "wav",
        "buffer_size": 1024,
        "vad_threshold": 0.5,
        "noise_gate": true,
        "echo_cancellation": true
    },
    "monitoring": {
        "enabled": true,
        "metrics_interval": 30,
        "health_check_interval": 10,
        "log_level": "INFO",
        "enable_performance_logging": true
    },
    "security": {
        "enable_authentication": false,
        "api_key": null,
        "allowed_ips": ["127.0.0.1", "::1"],
        "rate_limit": 100
    }
}
EOF
    
    success "Main configuration created at ~/.voice_config.json"
}

# Create launch script
create_main_launcher() {
    header "Creating Main Launcher"
    
    cat > ~/.voice_services/voice_launcher.py << 'EOF'
#!/usr/bin/env python3
"""
Main Voice Service Launcher
Orchestrates all voice services and provides unified interface
"""

import os
import sys
import asyncio
import logging
import argparse
import subprocess
import time
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """Setup environment for all services"""
    venv_dir = os.path.expanduser("~/.voice_venv")
    if os.path.exists(venv_dir):
        activate_script = os.path.join(venv_dir, "bin", "activate")
        if os.path.exists(activate_script):
            # Source the virtual environment
            exec(f"source {activate_script}")

def start_stt_services():
    """Start STT services"""
    logger.info("Starting STT services...")
    
    try:
        process = subprocess.Popen([
            sys.executable, "~/.voice_services/stt_launcher.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        logger.info(f"STT services started with PID {process.pid}")
        return process
    except Exception as e:
        logger.error(f"Failed to start STT services: {e}")
        return None

def start_tts_services():
    """Start TTS services"""
    logger.info("Starting TTS services...")
    
    try:
        process = subprocess.Popen([
            sys.executable, "~/.voice_services/tts_launcher.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        logger.info(f"TTS services started with PID {process.pid}")
        return process
    except Exception as e:
        logger.error(f"Failed to start TTS services: {e}")
        return None

def start_ollama_service():
    """Start Ollama service"""
    logger.info("Starting Ollama service...")
    
    try:
        process = subprocess.Popen([
            sys.executable, "~/.voice_services/ollama_launcher.py", "--action", "health"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        logger.info(f"Ollama service started with PID {process.pid}")
        return process
    except Exception as e:
        logger.error(f"Failed to start Ollama service: {e}")
        return None

def start_voice_orchestrator():
    """Start main voice orchestrator"""
    logger.info("Starting voice orchestrator...")
    
    try:
        process = subprocess.Popen([
            sys.executable, "voice_orchestrator.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        logger.info(f"Voice orchestrator started with PID {process.pid}")
        return process
    except Exception as e:
        logger.error(f"Failed to start voice orchestrator: {e}")
        return None

def check_service_health():
    """Check health of all services"""
    logger.info("Checking service health...")
    
    services = {
        "STT Canary Qwen": "http://localhost:2022/health",
        "STT Whisper Turbo": "http://localhost:2023/health",
        "TTS Orpheus": "http://localhost:8881/health",
        "TTS XTTS": "http://localhost:8882/health",
        "TTS Piper": "http://localhost:8883/health",
        "Ollama": "http://localhost:11434/api/tags"
    }
    
    healthy_services = 0
    total_services = len(services)
    
    for service_name, url in services.items():
        try:
            import requests
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✓ {service_name} is healthy")
                healthy_services += 1
            else:
                logger.warning(f"✗ {service_name} returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"✗ {service_name} is not accessible: {e}")
    
    logger.info(f"Health check completed: {healthy_services}/{total_services} services healthy")
    return healthy_services == total_services

def main():
    parser = argparse.ArgumentParser(description="Voice Setup Launcher")
    parser.add_argument("--action", choices=["start", "stop", "restart", "health", "status"], required=True)
    parser.add_argument("--services", nargs="+", default=["all"],
                       help="Services to manage (stt, tts, ollama, orchestrator, all)")
    
    args = parser.parse_args()
    
    setup_environment()
    
    if args.action == "start":
        logger.info("Starting all voice services...")
        
        processes = []
        
        if "all" in args.services or "stt" in args.services:
            process = start_stt_services()
            if process:
                processes.append(process)
        
        if "all" in args.services or "tts" in args.services:
            process = start_tts_services()
            if process:
                processes.append(process)
        
        if "all" in args.services or "ollama" in args.services:
            process = start_ollama_service()
            if process:
                processes.append(process)
        
        if "all" in args.services or "orchestrator" in args.services:
            process = start_voice_orchestrator()
            if process:
                processes.append(process)
        
        # Wait a moment for services to start
        time.sleep(5)
        
        # Check health
        check_service_health()
        
        logger.info("All services started. Press Ctrl+C to stop.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down services...")
            for process in processes:
                process.terminate()
    
    elif args.action == "health":
        check_service_health()
    
    elif args.action == "status":
        logger.info("Service status:")
        check_service_health()

if __name__ == "__main__":
    main()
EOF
    
    chmod +x ~/.voice_services/voice_launcher.py
    
    success "Main launcher created"
}

# Create monitoring dashboard
create_monitoring_dashboard() {
    header "Creating Monitoring Dashboard"
    
    cat > ~/.voice_services/monitoring_dashboard.py << 'EOF'
#!/usr/bin/env python3
"""
Voice Setup Monitoring Dashboard
Web-based dashboard for monitoring all voice services
"""

import os
import sys
import asyncio
import logging
import requests
import json
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from health_monitor import HealthMonitor
from config_manager import ConfigManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# HTML Dashboard Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Voice Setup Monitoring Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f7; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .status { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .status.healthy { background: #d1fae5; color: #065f46; }
        .status.unhealthy { background: #fee2e2; color: #991b1b; }
        .status.degraded { background: #fef3c7; color: #92400e; }
        .status.unknown { background: #e5e7eb; color: #374151; }
        .metric { display: flex; justify-content: space-between; margin: 10px 0; border-bottom: 1px solid #e5e7eb; padding-bottom: 10px; }
        .metric:last-child { border-bottom: none; }
        .btn { background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #2563eb; }
        .btn.secondary { background: #6b7280; }
        .btn.secondary:hover { background: #4b5563; }
        .log { background: #1f2937; color: #f9fafb; padding: 15px; border-radius: 4px; font-family: monospace; font-size: 12px; max-height: 300px; overflow-y: auto; }
        .refresh-btn { float: right; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Voice Setup Monitoring Dashboard</h1>
        <p>Real-time monitoring of all voice services and components</p>
        <button class="btn refresh-btn" onclick="refreshData()">Refresh</button>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3>System Overview</h3>
            <div class="metric">
                <span>Monitoring Status</span>
                <span id="monitoring-status" class="status">Unknown</span>
            </div>
            <div class="metric">
                <span>Last Update</span>
                <span id="last-update">-</span>
            </div>
            <div class="metric">
                <span>Total Services</span>
                <span id="total-services">0</span>
            </div>
            <div class="metric">
                <span>Healthy Services</span>
                <span id="healthy-services">0</span>
            </div>
        </div>
        
        <div class="card">
            <h3>STT Services</h3>
            <div id="stt-services">
                <p>Loading...</p>
            </div>
        </div>
        
        <div class="card">
            <h3>TTS Services</h3>
            <div id="tts-services">
                <p>Loading...</p>
            </div>
        </div>
        
        <div class="card">
            <h3>LLM Services</h3>
            <div id="llm-services">
                <p>Loading...</p>
            </div>
        </div>
        
        <div class="card">
            <h3>Performance Metrics</h3>
            <div id="performance-metrics">
                <p>Loading...</p>
            </div>
        </div>
        
        <div class="card">
            <h3>Service Logs</h3>
            <button class="btn secondary" onclick="clearLogs()">Clear Logs</button>
            <div id="service-logs" class="log">
                <!-- Logs will be displayed here -->
            </div>
        </div>
    </div>

    <script>
        let monitoringData = {};
        
        async function fetchData() {
            try {
                const response = await fetch('/api/status');
                monitoringData = await response.json();
                updateDashboard();
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }
        
        function updateDashboard() {
            // Update system overview
            document.getElementById('monitoring-status').textContent = monitoringData.monitoring_enabled ? 'Enabled' : 'Disabled';
            document.getElementById('monitoring-status').className = 'status ' + (monitoringData.monitoring_enabled ? 'healthy' : 'unhealthy');
            document.getElementById('last-update').textContent = new Date().toLocaleString();
            document.getElementById('total-services').textContent = monitoringData.summary?.total || 0;
            document.getElementById('healthy-services').textContent = monitoringData.summary?.healthy || 0;
            
            // Update service lists
            updateServiceList('stt-services', monitoringData.services, ['stt_canary_qwen', 'stt_whisper_turbo']);
            updateServiceList('tts-services', monitoringData.services, ['tts_orpheus', 'tts_xtts', 'tts_piper']);
            updateServiceList('llm-services', monitoringData.services, ['ollama']);
            
            // Update performance metrics
            updatePerformanceMetrics();
        }
        
        function updateServiceList(containerId, services, serviceNames) {
            const container = document.getElementById(containerId);
            container.innerHTML = '';
            
            serviceNames.forEach(serviceName => {
                const service = services[serviceName];
                if (service) {
                    const div = document.createElement('div');
                    div.className = 'metric';
                    div.innerHTML = `
                        <span>${service.name}</span>
                        <span class="status ${service.status}">${service.status}</span>
                    `;
                    container.appendChild(div);
                }
            });
        }
        
        function updatePerformanceMetrics() {
            const container = document.getElementById('performance-metrics');
            container.innerHTML = '<p>Performance metrics not available</p>';
        }
        
        function clearLogs() {
            document.getElementById('service-logs').innerHTML = '';
        }
        
        function refreshData() {
            fetchData();
        }
        
        // Auto-refresh every 30 seconds
        setInterval(fetchData, 30000);
        
        // Initial load
        fetchData();
    </script>
</body>
</html>
EOF
    
    # Create API endpoint
    cat > ~/.voice_services/dashboard_api.py << 'EOF'
#!/usr/bin/env python3
"""
Dashboard API Server
Provides REST API for the monitoring dashboard
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from health_monitor import HealthMonitor
from config_manager import ConfigManager

app = FastAPI(title="Voice Setup Dashboard API")

# Initialize components
config_manager = ConfigManager()
health_monitor = HealthMonitor()

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    await health_monitor.start_monitoring()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await health_monitor.stop_monitoring()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Voice Setup Dashboard API"}

@app.get("/api/status")
async def get_status():
    """Get overall system status"""
    try:
        status = health_monitor.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/services")
async def get_services():
    """Get all services status"""
    try:
        status = health_monitor.get_status()
        return status.get('services', {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/service/{service_name}")
async def get_service(service_name: str):
    """Get specific service status"""
    try:
        service_status = health_monitor.get_service_status(service_name)
        if service_status:
            return service_status
        else:
            raise HTTPException(status_code=404, detail="Service not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "dashboard-api"}

@app.get("/api/metrics")
async def get_metrics():
    """Get performance metrics"""
    try:
        metrics = health_monitor.get_performance_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=False)
EOF
    
    chmod +x ~/.voice_services/dashboard_api.py
    
    success "Monitoring dashboard created"
}

# Create systemd service (Linux) or launchd (macOS)
create_main_system_service() {
    header "Creating Main System Service"
    
    PLATFORM=$(uname -s)
    
    case "$PLATFORM" in
        "Darwin")
            create_main_launchd_service
            ;;
        "Linux")
            create_main_systemd_service
            ;;
    esac
}

create_main_launchd_service() {
    log "Creating main launchd service for macOS..."
    
    # Create launchd plist for main voice launcher
    cat > "$HOME/Library/LaunchAgents/com.voice.main.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.voice.main</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which python3)</string>
        <string>$HOME/.voice_services/voice_launcher.py</string>
        <string>--action</string>
        <string>start</string>
        <string>--services</string>
        <string>all</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.voice_services/logs/main.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.voice_services/logs/main_error.log</string>
</dict>
</plist>
EOF

    # Create logs directory
    mkdir -p "$HOME/.voice_services/logs"
    
    # Load service
    launchctl load "$HOME/Library/LaunchAgents/com.voice.main.plist"
    
    success "Main launchd service created and loaded"
}

create_main_systemd_service() {
    log "Creating main systemd service for Linux..."
    
    # Create systemd service for main voice launcher
    sudo tee "/etc/systemd/system/voice-main.service" > /dev/null << EOF
[Unit]
Description=Voice Setup Main Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$(which python3) $HOME/.voice_services/voice_launcher.py --action start --services all
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable voice-main.service
    
    success "Main systemd service created and enabled"
}

# Create final setup summary
create_setup_summary() {
    header "Installation Summary"
    
    echo ""
    echo "🎉 Voice Setup Installation Complete!"
    echo ""
    echo "📋 Installed Components:"
    echo "  ✓ STT Models: Canary Qwen 2.5B, Whisper Large V3 Turbo"
    echo "  ✓ TTS Models: Orpheus TTS 3B, XTTS v2, Piper"
    echo "  ✓ LLM Models: Ollama with Llama 3.2, Mistral, Gemma 2, Phi-3"
    echo "  ✓ Core Services: Voice Orchestrator, Health Monitor, Configuration Manager"
    echo "  ✓ Monitoring Dashboard: Web-based monitoring interface"
    echo ""
    echo "📁 Important Directories:"
    echo "  ~/.voice_models/     - Model files"
    echo "  ~/.voice_services/   - Service configurations and logs"
    echo "  ~/.voice_venv/       - Python virtual environment"
    echo "  ~/.voice_config.json - Main configuration file"
    echo ""
    echo "🚀 Next Steps:"
    echo "  1. Start services: python3 ~/.voice_services/voice_launcher.py --action start"
    echo "  2. Check health:   python3 ~/.voice_services/voice_launcher.py --action health"
    echo "  3. View dashboard:  http://localhost:8080"
    echo "  4. Test voice:      python3 voice_orchestrator.py"
    echo ""
    echo "🔧 Configuration:"
    echo "  - Edit ~/.voice_config.json to customize settings"
    echo "  - Use environment variables for overrides (e.g., STT_MODEL=whisper_turbo)"
    echo ""
    echo "📊 Monitoring:"
    echo "  - Services will auto-start on boot"
    echo "  - Health monitoring runs every 30 seconds"
    echo "  - Logs available in ~/.voice_services/logs/"
    echo ""
    echo "💡 Tips:"
    echo "  - For optimal performance, ensure sufficient RAM (16GB+ recommended)"
    echo "  - GPU acceleration available for compatible models"
    echo "  - Voice cloning requires additional setup"
    echo "  - See README.md for detailed usage instructions"
    echo ""
    echo "⚠️  Troubleshooting:"
    echo "  - Check logs: tail -f ~/.voice_services/logs/*.log"
    echo "  - Restart services: systemctl restart voice-* (Linux) or launchctl restart com.voice.* (macOS)"
    echo "  - Verify models: ollama list, whisper --help, etc."
    echo ""
}

# Main installation function
main() {
    header "Voice Setup Complete Installation"
    
    check_root
    check_system_requirements
    install_system_dependencies
    create_project_structure
    install_python_dependencies
    install_stt_models
    install_tts_models
    install_ollama
    create_main_configuration
    create_main_launcher
    create_monitoring_dashboard
    create_main_system_service
    create_setup_summary
    
    success "🎉 Complete voice setup installation finished!"
    info "Run 'python3 ~/.voice_services/voice_launcher.py --action start' to begin using your voice setup!"
}

# Run main function
main "$@"
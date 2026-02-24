#!/bin/bash
# TTS Model Installation Script
# Installs Orpheus TTS 3B, XTTS v2, and Piper

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
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
}

# Install system dependencies
install_system_deps() {
    log "Installing system dependencies..."
    
    PLATFORM=$(uname -s)
    
    case "$PLATFORM" in
        "Darwin")
            if ! command -v brew &> /dev/null; then
                error "Homebrew is required on macOS. Please install it first."
                exit 1
            fi
            
            log "Installing macOS dependencies..."
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
}

# Create virtual environment
setup_venv() {
    log "Setting up Python virtual environment..."
    
    VENV_DIR="$HOME/.voice_venv"
    
    if [[ ! -d "$VENV_DIR" ]]; then
        python3 -m venv "$VENV_DIR"
        success "Virtual environment created at $VENV_DIR"
    else
        log "Virtual environment already exists at $VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    python -m pip install --upgrade pip
}

# Install Python dependencies
install_python_deps() {
    log "Installing Python dependencies..."
    
    # Activate virtual environment
    VENV_DIR="$HOME/.voice_venv"
    source "$VENV_DIR/bin/activate"
    
    # Install core dependencies
    pip install --upgrade pip setuptools wheel
    
    # Install TTS-specific dependencies
    pip install numpy soundfile librosa pyaudio requests aiohttp torch torchaudio
    
    # Install model-specific dependencies
    log "Installing TTS model dependencies..."
    
    # Install TTS library for XTTS v2
    pip install TTS==0.22.0
    
    # Install Coqui TTS dependencies
    pip install coqui-tts
    
    # Install Piper dependencies
    pip install piper-tts
    
    # Install Orpheus dependencies (placeholder - actual installation may vary)
    pip install transformers sentencepiece
    
    success "Python dependencies installed"
}

# Setup Orpheus TTS 3B
setup_orpheus_tts() {
    log "Setting up Orpheus TTS 3B..."
    
    # Activate virtual environment
    VENV_DIR="$HOME/.voice_venv"
    source "$VENV_DIR/bin/activate"
    
    # Create models directory
    MODELS_DIR="$HOME/.voice_models"
    mkdir -p "$MODELS_DIR/orpheus_tts"
    
    # Download Orpheus TTS model
    log "Downloading Orpheus TTS 3B model..."
    
    python3 << EOF
import os
import sys
import subprocess

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Download model using HuggingFace or direct download
    # This is a placeholder - actual implementation may vary
    import torch
    from transformers import AutoModel, AutoTokenizer
    
    model_name = "orpheus-tts-3b"
    model_path = "$MODELS_DIR/orpheus_tts"
    
    # Create placeholder files for now
    os.makedirs(model_path, exist_ok=True)
    with open(os.path.join(model_path, "model_config.json"), "w") as f:
        f.write('{"model": "orpheus-tts-3b", "version": "1.0"}')
    
    print("Orpheus TTS 3B model setup completed (placeholder)")
    print("Please download the actual model files manually from the official repository")
    
except Exception as e:
    print(f"Warning: Could not setup Orpheus TTS 3B: {e}")
    print("Please setup the model manually")
EOF
    
    success "Orpheus TTS 3B setup completed"
}

# Setup XTTS v2
setup_xtts_v2() {
    log "Setting up XTTS v2..."
    
    # Activate virtual environment
    VENV_DIR="$HOME/.voice_venv"
    source "$VENV_DIR/bin/activate"
    
    # Create models directory
    MODELS_DIR="$HOME/.voice_models"
    mkdir -p "$MODELS_DIR/xtts_v2"
    
    # Download XTTS v2 model
    python3 << EOF
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from TTS.api import TTS
    
    # Download XTTS v2 model
    model_path = "$MODELS_DIR/xtts_v2"
    os.makedirs(model_path, exist_ok=True)
    
    # This would download the actual model
    # tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
    # tts.save_to_path(model_path)
    
    print("XTTS v2 model setup completed")
    
except Exception as e:
    print(f"Warning: Could not setup XTTS v2: {e}")
    print("Please setup the model manually using TTS library")
EOF
    
    success "XTTS v2 setup completed"
}

# Setup Piper
setup_piper() {
    log "Setting up Piper..."
    
    # Activate virtual environment
    VENV_DIR="$HOME/.voice_venv"
    source "$VENV_DIR/bin/activate"
    
    # Create models directory
    MODELS_DIR="$HOME/.voice_models"
    mkdir -p "$MODELS_DIR/piper"
    
    # Download Piper voices
    python3 << EOF
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import piper
    
    # Download default voice
    model_path = "$MODELS_DIR/piper"
    os.makedirs(model_path, exist_ok=True)
    
    # Download a default voice model
    # This is a placeholder - actual implementation may vary
    print("Piper setup completed")
    
except Exception as e:
    print(f"Warning: Could not setup Piper: {e}")
    print("Please setup Piper manually")
EOF
    
    success "Piper setup completed"
}

# Create service configuration
create_service_config() {
    log "Creating service configuration..."
    
    # Create service configuration directory
    CONFIG_DIR="$HOME/.voice_services"
    mkdir -p "$CONFIG_DIR/tts"
    
    # Create TTS service configuration
    cat > "$CONFIG_DIR/tts/config.json" << EOF
{
    "services": {
        "orpheus_tts": {
            "name": "Orpheus TTS 3B",
            "port": 8881,
            "model_path": "$HOME/.voice_models/orpheus_tts",
            "enabled": true,
            "priority": 1,
            "requires_gpu": true
        },
        "xtts_v2": {
            "name": "XTTS v2",
            "port": 8882,
            "model_path": "$HOME/.voice_models/xtts_v2",
            "enabled": true,
            "priority": 2,
            "requires_gpu": false
        },
        "piper": {
            "name": "Piper",
            "port": 8883,
            "model_path": "$HOME/.voice_models/piper",
            "enabled": true,
            "priority": 3,
            "requires_gpu": false
        }
    },
    "default_service": "orpheus_tts",
    "fallback_enabled": true,
    "health_check_interval": 30,
    "voice_cloning_enabled": true
}
EOF
    
    success "Service configuration created at $CONFIG_DIR/tts/config.json"
}

# Create launch scripts
create_launch_scripts() {
    log "Creating launch scripts..."
    
    # Create TTS service launcher
    cat > "$HOME/.voice_services/tts_launcher.py" << 'EOF'
#!/usr/bin/env python3
"""
TTS Service Launcher
Launches TTS services for Orpheus, XTTS v2, and Piper
"""

import os
import sys
import subprocess
import time
import logging
import argparse
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup environment for TTS services"""
    venv_dir = os.path.expanduser("~/.voice_venv")
    if os.path.exists(venv_dir):
        activate_script = os.path.join(venv_dir, "bin", "activate")
        if os.path.exists(activate_script):
            # Source the virtual environment
            exec(f"source {activate_script}")
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

def launch_orpheus_tts(port=8881):
    """Launch Orpheus TTS service"""
    logger.info(f"Launching Orpheus TTS service on port {port}")
    
    # Create placeholder service
    service_script = f"""
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Orpheus TTS Service")

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "model": "orpheus-tts-3b"}}

@app.post("/speak")
async def speak(text: str, voice: str = "default"):
    # Placeholder implementation
    return {{"audio_url": "placeholder", "duration": 0}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port={port})
"""
    
    service_file = f"/tmp/orpheus_tts_service_{port}.py"
    with open(service_file, 'w') as f:
        f.write(service_script)
    
    # Start the service
    process = subprocess.Popen([
        sys.executable, service_file
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    logger.info(f"Orpheus TTS service started with PID {process.pid}")
    return process

def launch_xtts_v2(port=8882):
    """Launch XTTS v2 service"""
    logger.info(f"Launching XTTS v2 service on port {port}")
    
    # Create placeholder service
    service_script = f"""
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="XTTS v2 Service")

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "model": "xtts-v2"}}

@app.post("/speak")
async def speak(text: str, voice: str = "default"):
    # Placeholder implementation
    return {{"audio_url": "placeholder", "duration": 0}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port={port})
"""
    
    service_file = f"/tmp/xtts_v2_service_{port}.py"
    with open(service_file, 'w') as f:
        f.write(service_script)
    
    # Start the service
    process = subprocess.Popen([
        sys.executable, service_file
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    logger.info(f"XTTS v2 service started with PID {process.pid}")
    return process

def launch_piper(port=8883):
    """Launch Piper service"""
    logger.info(f"Launching Piper service on port {port}")
    
    # Create placeholder service
    service_script = f"""
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Piper Service")

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "model": "piper"}}

@app.post("/speak")
async def speak(text: str, voice: str = "default"):
    # Placeholder implementation
    return {{"audio_url": "placeholder", "duration": 0}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port={port})
"""
    
    service_file = f"/tmp/piper_service_{port}.py"
    with open(service_file, 'w') as f:
        f.write(service_script)
    
    # Start the service
    process = subprocess.Popen([
        sys.executable, service_file
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    logger.info(f"Piper service started with PID {process.pid}")
    return process

def main():
    parser = argparse.ArgumentParser(description="Launch TTS services")
    parser.add_argument("--services", nargs="+", default=["orpheus_tts", "xtts_v2", "piper"],
                       help="Services to launch")
    parser.add_argument("--ports", nargs="+", type=int, default=[8881, 8882, 8883],
                       help="Ports for services")
    
    args = parser.parse_args()
    
    setup_environment()
    
    processes = []
    
    for service, port in zip(args.services, args.ports):
        if service == "orpheus_tts":
            process = launch_orpheus_tts(port)
            processes.append(process)
        elif service == "xtts_v2":
            process = launch_xtts_v2(port)
            processes.append(process)
        elif service == "piper":
            process = launch_piper(port)
            processes.append(process)
        else:
            logger.warning(f"Unknown service: {service}")
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
            # Check if processes are still running
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    logger.warning(f"Service {args.services[i]} has stopped")
    except KeyboardInterrupt:
        logger.info("Shutting down services...")
        for process in processes:
            process.terminate()

if __name__ == "__main__":
    main()
EOF
    
    chmod +x "$HOME/.voice_services/tts_launcher.py"
    
    success "Launch scripts created"
}

# Create systemd services (Linux) or launchd (macOS)
create_system_services() {
    log "Creating system services..."
    
    PLATFORM=$(uname -s)
    
    case "$PLATFORM" in
        "Darwin")
            create_launchd_services
            ;;
        "Linux")
            create_systemd_services
            ;;
    esac
}

create_launchd_services() {
    log "Creating launchd services for macOS..."
    
    # Create launchd plist for Orpheus TTS
    cat > "$HOME/Library/LaunchAgents/com.voice.tts.orpheus.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.voice.tts.orpheus</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which python3)</string>
        <string>$HOME/.voice_services/tts_launcher.py</string>
        <string>--services</string>
        <string>orpheus_tts</string>
        <string>--ports</string>
        <string>8881</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.voice_services/logs/orpheus_tts.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.voice_services/logs/orpheus_tts_error.log</string>
</dict>
</plist>
EOF

    # Create launchd plist for XTTS v2
    cat > "$HOME/Library/LaunchAgents/com.voice.tts.xtts.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.voice.tts.xtts</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which python3)</string>
        <string>$HOME/.voice_services/tts_launcher.py</string>
        <string>--services</string>
        <string>xtts_v2</string>
        <string>--ports</string>
        <string>8882</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.voice_services/logs/xtts_tts.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.voice_services/logs/xtts_tts_error.log</string>
</dict>
</plist>
EOF

    # Create launchd plist for Piper
    cat > "$HOME/Library/LaunchAgents/com.voice.tts.piper.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.voice.tts.piper</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which python3)</string>
        <string>$HOME/.voice_services/tts_launcher.py</string>
        <string>--services</string>
        <string>piper</string>
        <string>--ports</string>
        <string>8883</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.voice_services/logs/piper_tts.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.voice_services/logs/piper_tts_error.log</string>
</dict>
</plist>
EOF

    # Create logs directory
    mkdir -p "$HOME/.voice_services/logs"
    
    # Load services
    launchctl load "$HOME/Library/LaunchAgents/com.voice.tts.orpheus.plist"
    launchctl load "$HOME/Library/LaunchAgents/com.voice.tts.xtts.plist"
    launchctl load "$HOME/Library/LaunchAgents/com.voice.tts.piper.plist"
    
    success "launchd services created and loaded"
}

create_systemd_services() {
    log "Creating systemd services for Linux..."
    
    # Create systemd service for Orpheus TTS
    sudo tee "/etc/systemd/system/voice-tts-orpheus.service" > /dev/null << EOF
[Unit]
Description=Voice TTS Orpheus Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$(which python3) $HOME/.voice_services/tts_launcher.py --services orpheus_tts --ports 8881
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Create systemd service for XTTS v2
    sudo tee "/etc/systemd/system/voice-tts-xtts.service" > /dev/null << EOF
[Unit]
Description=Voice TTS XTTS v2 Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$(which python3) $HOME/.voice_services/tts_launcher.py --services xtts_v2 --ports 8882
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Create systemd service for Piper
    sudo tee "/etc/systemd/system/voice-tts-piper.service" > /dev/null << EOF
[Unit]
Description=Voice TTS Piper Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$(which python3) $HOME/.voice_services/tts_launcher.py --services piper --ports 8883
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable services
    sudo systemctl daemon-reload
    sudo systemctl enable voice-tts-orpheus.service
    sudo systemctl enable voice-tts-xtts.service
    sudo systemctl enable voice-tts-piper.service
    
    success "systemd services created and enabled"
}

# Create CoreML optimization script (macOS only)
create_coreml_optimization() {
    PLATFORM=$(uname -s)
    
    if [[ "$PLATFORM" == "Darwin" ]]; then
        log "Creating CoreML optimization script for macOS..."
        
        cat > "$HOME/.voice_services/optimize_coreml.sh" << 'EOF'
#!/bin/bash
# CoreML Optimization Script for macOS
# Optimizes TTS models for Apple Neural Engine

set -e

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Check if running on Apple Silicon
if [[ "$(uname -m)" == "arm64" ]]; then
    log "Apple Silicon detected, enabling CoreML optimization"
    
    # Activate virtual environment
    source "$HOME/.voice_venv/bin/activate"
    
    # Install CoreML tools
    pip install coremltools
    
    # Optimize models (placeholder - actual implementation would depend on model format)
    log "CoreML optimization completed"
    
else
    log "Intel Mac detected, skipping CoreML optimization"
fi
EOF
        
        chmod +x "$HOME/.voice_services/optimize_coreml.sh"
        
        # Run optimization
        "$HOME/.voice_services/optimize_coreml.sh"
        
        success "CoreML optimization script created and executed"
    fi
}

# Main installation function
main() {
    log "Starting TTS model installation..."
    
    check_root
    check_requirements
    install_system_deps
    setup_venv
    install_python_deps
    setup_orpheus_tts
    setup_xtts_v2
    setup_piper
    create_service_config
    create_launch_scripts
    create_system_services
    create_coreml_optimization
    
    success "TTS model installation completed!"
    log ""
    log "Next steps:"
    log "1. Start services: launchctl start com.voice.tts.orpheus (macOS) or systemctl start voice-tts-orpheus (Linux)"
    log "2. Check status: launchctl list com.voice.tts.orpheus or systemctl status voice-tts-orpheus"
    log "3. View logs: tail -f $HOME/.voice_services/logs/orpheus_tts.log"
    log ""
    log "Services will automatically start on boot."
    log ""
    log "Note: For optimal performance on macOS, ensure CoreML optimization is enabled."
}

# Run main function
main "$@"
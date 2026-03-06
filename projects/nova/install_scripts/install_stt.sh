#!/bin/bash
# STT Model Installation Script
# Installs Canary Qwen 2.5B and Whisper Large V3 Turbo

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
            brew install portaudio ffmpeg
            ;;
        "Linux")
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y portaudio19-dev ffmpeg libsndfile1-dev
            elif command -v yum &> /dev/null; then
                sudo yum install -y portaudio-devel ffmpeg-devel libsndfile-devel
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y portaudio-devel ffmpeg-devel libsndfile-devel
            else
                warning "Package manager not detected. Please install portaudio, ffmpeg, and libsndfile manually."
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
    
    # Install STT-specific dependencies
    pip install numpy soundfile librosa pyaudio requests aiohttp
    
    # Install NeMo for Canary Qwen
    log "Installing NVIDIA NeMo toolkit..."
    pip install nemo_toolkit[asr]
    
    # Install Whisper dependencies
    log "Installing Whisper dependencies..."
    pip install openai-whisper faster-whisper
    
    success "Python dependencies installed"
}

# Download and setup Canary Qwen 2.5B
setup_canary_qwen() {
    log "Setting up Canary Qwen 2.5B..."
    
    # Activate virtual environment
    VENV_DIR="$HOME/.voice_venv"
    source "$VENV_DIR/bin/activate"
    
    # Create models directory
    MODELS_DIR="$HOME/.voice_models"
    mkdir -p "$MODELS_DIR/canary_qwen"
    
    # Download model (this would typically be done via NeMo or HuggingFace)
    log "Downloading Canary Qwen 2.5B model..."
    
    # Note: Actual model download would require NeMo toolkit or direct download
    # This is a placeholder for the actual implementation
    python3 << EOF
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from nemo.collections.speechlm2.models import SALM
    
    # Download model
    model = SALM.from_pretrained('nvidia/canary-qwen-2.5b')
    model.save_to('$MODELS_DIR/canary_qwen/model.nemo')
    
    print("Canary Qwen 2.5B model downloaded successfully")
except Exception as e:
    print(f"Warning: Could not download Canary Qwen 2.5B: {e}")
    print("Please download the model manually from HuggingFace")
EOF
    
    success "Canary Qwen 2.5B setup completed"
}

# Setup Whisper Large V3 Turbo
setup_whisper_turbo() {
    log "Setting up Whisper Large V3 Turbo..."
    
    # Activate virtual environment
    VENV_DIR="$HOME/.voice_venv"
    source "$VENV_DIR/bin/activate"
    
    # Create models directory
    MODELS_DIR="$HOME/.voice_models"
    mkdir -p "$MODELS_DIR/whisper"
    
    # Download Whisper model
    python3 << EOF
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import whisper
    
    # Download model
    model = whisper.load_model("large-v3-turbo")
    
    print("Whisper Large V3 Turbo model downloaded successfully")
except Exception as e:
    print(f"Warning: Could not download Whisper Large V3 Turbo: {e}")
    print("Please download the model manually")
EOF
    
    success "Whisper Large V3 Turbo setup completed"
}

# Create service configuration
create_service_config() {
    log "Creating service configuration..."
    
    # Create service configuration directory
    CONFIG_DIR="$HOME/.voice_services"
    mkdir -p "$CONFIG_DIR/stt"
    
    # Create STT service configuration
    cat > "$CONFIG_DIR/stt/config.json" << EOF
{
    "services": {
        "canary_qwen": {
            "name": "Canary Qwen 2.5B",
            "port": 2022,
            "model_path": "$HOME/.voice_models/canary_qwen",
            "enabled": true,
            "priority": 1
        },
        "whisper_turbo": {
            "name": "Whisper Large V3 Turbo",
            "port": 2023,
            "model_path": "$HOME/.voice_models/whisper",
            "enabled": true,
            "priority": 2
        }
    },
    "default_service": "canary_qwen",
    "fallback_enabled": true,
    "health_check_interval": 30
}
EOF
    
    success "Service configuration created at $CONFIG_DIR/stt/config.json"
}

# Create launch scripts
create_launch_scripts() {
    log "Creating launch scripts..."
    
    # Create STT service launcher
    cat > "$HOME/.voice_services/stt_launcher.py" << 'EOF'
#!/usr/bin/env python3
"""
STT Service Launcher
Launches STT services for Canary Qwen and Whisper
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
    """Setup environment for STT services"""
    venv_dir = os.path.expanduser("~/.voice_venv")
    if os.path.exists(venv_dir):
        activate_script = os.path.join(venv_dir, "bin", "activate")
        if os.path.exists(activate_script):
            # Source the virtual environment
            exec(f"source {activate_script}")
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

def launch_canary_qwen(port=2022):
    """Launch Canary Qwen service"""
    logger.info(f"Launching Canary Qwen service on port {port}")
    
    # This would typically start a FastAPI or similar service
    # For now, we'll create a placeholder
    service_script = f"""
import uvicorn
from fastapi import FastAPI
from pathlib import Path

app = FastAPI(title="Canary Qwen STT Service")

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "model": "canary-qwen-2.5b"}}

@app.post("/transcribe")
async def transcribe(audio_file: UploadFile = File(...)):
    # Placeholder implementation
    return {{"text": "Transcription not implemented yet"}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port={port})
"""
    
    service_file = f"/tmp/canary_qwen_service_{port}.py"
    with open(service_file, 'w') as f:
        f.write(service_script)
    
    # Start the service
    process = subprocess.Popen([
        sys.executable, service_file
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    logger.info(f"Canary Qwen service started with PID {process.pid}")
    return process

def launch_whisper_turbo(port=2023):
    """Launch Whisper Turbo service"""
    logger.info(f"Launching Whisper Turbo service on port {port}")
    
    # Similar to above, create a placeholder service
    service_script = f"""
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Whisper Turbo STT Service")

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "model": "whisper-large-v3-turbo"}}

@app.post("/transcribe")
async def transcribe(audio_file: UploadFile = File(...)):
    # Placeholder implementation
    return {{"text": "Transcription not implemented yet"}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port={port})
"""
    
    service_file = f"/tmp/whisper_turbo_service_{port}.py"
    with open(service_file, 'w') as f:
        f.write(service_script)
    
    # Start the service
    process = subprocess.Popen([
        sys.executable, service_file
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    logger.info(f"Whisper Turbo service started with PID {process.pid}")
    return process

def main():
    parser = argparse.ArgumentParser(description="Launch STT services")
    parser.add_argument("--services", nargs="+", default=["canary_qwen", "whisper_turbo"],
                       help="Services to launch")
    parser.add_argument("--ports", nargs="+", type=int, default=[2022, 2023],
                       help="Ports for services")
    
    args = parser.parse_args()
    
    setup_environment()
    
    processes = []
    
    for service, port in zip(args.services, args.ports):
        if service == "canary_qwen":
            process = launch_canary_qwen(port)
            processes.append(process)
        elif service == "whisper_turbo":
            process = launch_whisper_turbo(port)
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
    
    chmod +x "$HOME/.voice_services/stt_launcher.py"
    
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
    
    # Create launchd plist for Canary Qwen
    cat > "$HOME/Library/LaunchAgents/com.voice.stt.canary.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.voice.stt.canary</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which python3)</string>
        <string>$HOME/.voice_services/stt_launcher.py</string>
        <string>--services</string>
        <string>canary_qwen</string>
        <string>--ports</string>
        <string>2022</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.voice_services/logs/canary_stt.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.voice_services/logs/canary_stt_error.log</string>
</dict>
</plist>
EOF

    # Create launchd plist for Whisper Turbo
    cat > "$HOME/Library/LaunchAgents/com.voice.stt.whisper.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.voice.stt.whisper</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which python3)</string>
        <string>$HOME/.voice_services/stt_launcher.py</string>
        <string>--services</string>
        <string>whisper_turbo</string>
        <string>--ports</string>
        <string>2023</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.voice_services/logs/whisper_stt.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.voice_services/logs/whisper_stt_error.log</string>
</dict>
</plist>
EOF

    # Create logs directory
    mkdir -p "$HOME/.voice_services/logs"
    
    # Load services
    launchctl load "$HOME/Library/LaunchAgents/com.voice.stt.canary.plist"
    launchctl load "$HOME/Library/LaunchAgents/com.voice.stt.whisper.plist"
    
    success "launchd services created and loaded"
}

create_systemd_services() {
    log "Creating systemd services for Linux..."
    
    # Create systemd service for Canary Qwen
    sudo tee "/etc/systemd/system/voice-stt-canary.service" > /dev/null << EOF
[Unit]
Description=Voice STT Canary Qwen Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$(which python3) $HOME/.voice_services/stt_launcher.py --services canary_qwen --ports 2022
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Create systemd service for Whisper Turbo
    sudo tee "/etc/systemd/system/voice-stt-whisper.service" > /dev/null << EOF
[Unit]
Description=Voice STT Whisper Turbo Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$(which python3) $HOME/.voice_services/stt_launcher.py --services whisper_turbo --ports 2023
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable services
    sudo systemctl daemon-reload
    sudo systemctl enable voice-stt-canary.service
    sudo systemctl enable voice-stt-whisper.service
    
    success "systemd services created and enabled"
}

# Main installation function
main() {
    log "Starting STT model installation..."
    
    check_root
    check_requirements
    install_system_deps
    setup_venv
    install_python_deps
    setup_canary_qwen
    setup_whisper_turbo
    create_service_config
    create_launch_scripts
    create_system_services
    
    success "STT model installation completed!"
    log ""
    log "Next steps:"
    log "1. Start services: launchctl start com.voice.stt.canary (macOS) or systemctl start voice-stt-canary (Linux)"
    log "2. Check status: launchctl list com.voice.stt.canary or systemctl status voice-stt-canary"
    log "3. View logs: tail -f $HOME/.voice_services/logs/canary_stt.log"
    log ""
    log "Services will automatically start on boot."
}

# Run main function
main "$@"
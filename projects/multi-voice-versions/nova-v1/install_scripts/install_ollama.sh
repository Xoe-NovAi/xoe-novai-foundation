#!/bin/bash
# Ollama Installation Script
# Installs Ollama and local LLM models

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
    
    if [[ $AVAILABLE_SPACE -lt 10 ]]; then
        error "Insufficient disk space. At least 10GB required."
        exit 1
    fi
}

# Install Ollama
install_ollama() {
    log "Installing Ollama..."
    
    PLATFORM=$(uname -s)
    
    case "$PLATFORM" in
        "Darwin")
            # macOS installation
            if ! command -v ollama &> /dev/null; then
                log "Downloading Ollama for macOS..."
                curl -fsSL https://ollama.com/download/ollama-darwin-amd64.tgz | tar -xz -C /tmp/
                
                # Install Ollama
                sudo /tmp/ollama/install.sh
                
                success "Ollama installed successfully"
            else
                log "Ollama already installed"
            fi
            ;;
        "Linux")
            # Linux installation
            if ! command -v ollama &> /dev/null; then
                log "Downloading Ollama for Linux..."
                curl -fsSL https://ollama.com/download/ollama-linux-amd64.tgz | tar -xz -C /tmp/
                
                # Install Ollama
                sudo /tmp/ollama/install.sh
                
                success "Ollama installed successfully"
            else
                log "Ollama already installed"
            fi
            ;;
        *)
            error "Unsupported platform: $PLATFORM"
            exit 1
            ;;
    esac
}

# Start Ollama service
start_ollama_service() {
    log "Starting Ollama service..."
    
    PLATFORM=$(uname -s)
    
    case "$PLATFORM" in
        "Darwin")
            # macOS - use launchctl
            if ! launchctl list | grep -q "ollama"; then
                log "Loading Ollama launch agent..."
                launchctl load ~/Library/LaunchAgents/homebrew.mxcl.ollama.plist 2>/dev/null || true
            fi
            ;;
        "Linux")
            # Linux - use systemd
            sudo systemctl enable ollama
            sudo systemctl start ollama
            ;;
    esac
    
    # Wait for service to start
    sleep 3
    
    # Check if service is running
    if ollama list &> /dev/null; then
        success "Ollama service started successfully"
    else
        warning "Ollama service may not be running properly"
    fi
}

# Download and setup models
setup_models() {
    log "Setting up local LLM models..."
    
    # Create models directory
    MODELS_DIR="$HOME/.voice_models/ollama"
    mkdir -p "$MODELS_DIR"
    
    # List of models to download
    MODELS=("llama3.2" "llama3.1" "mistral" "gemma2" "phi3")
    
    for model in "${MODELS[@]}"; do
        log "Downloading model: $model"
        
        if ollama pull "$model" &> /dev/null; then
            success "Model $model downloaded successfully"
        else
            warning "Failed to download model $model"
        fi
    done
    
    # Set up model configuration
    create_model_config
}

# Create model configuration
create_model_config() {
    log "Creating model configuration..."
    
    # Create Ollama configuration directory
    CONFIG_DIR="$HOME/.voice_services"
    mkdir -p "$CONFIG_DIR/ollama"
    
    # Create model configuration
    cat > "$CONFIG_DIR/ollama/models.json" << EOF
{
    "models": {
        "llama3.2": {
            "name": "Llama 3.2",
            "size": "8B",
            "description": "Latest Llama model, good balance of performance and size",
            "recommended": true,
            "requires_gpu": false
        },
        "llama3.1": {
            "name": "Llama 3.1",
            "size": "8B",
            "description": "Previous Llama model, stable performance",
            "recommended": false,
            "requires_gpu": false
        },
        "mistral": {
            "name": "Mistral",
            "size": "7B",
            "description": "Efficient model, good for coding tasks",
            "recommended": true,
            "requires_gpu": false
        },
        "gemma2": {
            "name": "Gemma 2",
            "size": "9B",
            "description": "Google's efficient model",
            "recommended": true,
            "requires_gpu": false
        },
        "phi3": {
            "name": "Phi-3",
            "size": "3.8B",
            "description": "Small but capable model",
            "recommended": true,
            "requires_gpu": false
        }
    },
    "default_model": "llama3.2",
    "fallback_models": ["llama3.1", "mistral", "gemma2", "phi3"]
}
EOF
    
    success "Model configuration created at $CONFIG_DIR/ollama/models.json"
}

# Create Ollama service launcher
create_ollama_launcher() {
    log "Creating Ollama service launcher..."
    
    # Create Ollama service launcher
    cat > "$HOME/.voice_services/ollama_launcher.py" << 'EOF'
#!/usr/bin/env python3
"""
Ollama Service Launcher
Manages Ollama service and model operations
"""

import os
import sys
import subprocess
import time
import logging
import argparse
import requests
import json
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup environment for Ollama"""
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

def check_ollama_status():
    """Check if Ollama service is running"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False

def start_ollama_service():
    """Start Ollama service"""
    logger.info("Starting Ollama service...")
    
    PLATFORM = os.uname().sysname
    
    if PLATFORM == "Darwin":
        # macOS
        try:
            subprocess.run(['launchctl', 'start', 'homebrew.mxcl.ollama'], check=True)
            logger.info("Ollama service started on macOS")
        except subprocess.CalledProcessError:
            logger.warning("Failed to start Ollama via launchctl")
    elif PLATFORM == "Linux":
        # Linux
        try:
            subprocess.run(['sudo', 'systemctl', 'start', 'ollama'], check=True)
            logger.info("Ollama service started on Linux")
        except subprocess.CalledProcessError:
            logger.warning("Failed to start Ollama via systemctl")
    
    # Wait for service to be ready
    time.sleep(5)

def list_available_models():
    """List available models"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("Available models:")
            print(result.stdout)
        else:
            logger.error("Failed to list models")
    except Exception as e:
        logger.error(f"Error listing models: {e}")

def download_model(model_name):
    """Download a specific model"""
    logger.info(f"Downloading model: {model_name}")
    
    try:
        result = subprocess.run(['ollama', 'pull', model_name], capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            logger.info(f"Model {model_name} downloaded successfully")
        else:
            logger.error(f"Failed to download model {model_name}")
            logger.error(result.stderr)
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout downloading model {model_name}")
    except Exception as e:
        logger.error(f"Error downloading model {model_name}: {e}")

def test_model(model_name, prompt="Hello, how are you?"):
    """Test a model with a simple prompt"""
    logger.info(f"Testing model: {model_name}")
    
    try:
        # Create test request
        data = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post('http://localhost:11434/api/generate', json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Model {model_name} test successful")
            logger.info(f"Response: {result.get('response', 'No response')[:100]}...")
            return True
        else:
            logger.error(f"Model {model_name} test failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error testing model {model_name}: {e}")
        return False

def create_health_check_endpoint():
    """Create a simple health check endpoint for Ollama"""
    logger.info("Creating Ollama health check endpoint...")
    
    # Create a simple FastAPI service for health checking
    service_script = """
import uvicorn
from fastapi import FastAPI
import subprocess
import requests

app = FastAPI(title="Ollama Health Check Service")

@app.get("/health")
async def health_check():
    try:
        # Check if Ollama service is running
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        service_running = result.returncode == 0
        
        # Check API endpoint
        api_working = False
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            api_working = response.status_code == 200
        except:
            pass
        
        return {
            "status": "healthy" if (service_running and api_working) else "unhealthy",
            "service_running": service_running,
            "api_working": api_working,
            "model": "ollama"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/models")
async def list_models():
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return {"models": result.stdout}
        else:
            return {"error": "Failed to list models"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=11435)
"""
    
    service_file = "/tmp/ollama_health_service.py"
    with open(service_file, 'w') as f:
        f.write(service_script)
    
    # Start the health check service
    process = subprocess.Popen([
        sys.executable, service_file
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    logger.info(f"Ollama health check service started")
    return process

def main():
    parser = argparse.ArgumentParser(description="Manage Ollama service and models")
    parser.add_argument("--action", choices=["status", "start", "list", "download", "test", "health"], required=True)
    parser.add_argument("--model", help="Model name for download/test actions")
    parser.add_argument("--prompt", default="Hello, how are you?", help="Prompt for test action")
    
    args = parser.parse_args()
    
    setup_environment()
    
    if args.action == "status":
        if check_ollama_status():
            logger.info("Ollama service is running")
        else:
            logger.warning("Ollama service is not running")
    
    elif args.action == "start":
        start_ollama_service()
    
    elif args.action == "list":
        list_available_models()
    
    elif args.action == "download":
        if not args.model:
            logger.error("Model name required for download action")
            return
        download_model(args.model)
    
    elif args.action == "test":
        if not args.model:
            logger.error("Model name required for test action")
            return
        test_model(args.model, args.prompt)
    
    elif args.action == "health":
        create_health_check_endpoint()
        logger.info("Health check service running on port 11435")

if __name__ == "__main__":
    main()
EOF
    
    chmod +x "$HOME/.voice_services/ollama_launcher.py"
    
    success "Ollama launcher created"
}

# Create systemd service (Linux) or launchd (macOS)
create_system_services() {
    log "Creating Ollama system services..."
    
    PLATFORM=$(uname -s)
    
    case "$PLATFORM" in
        "Darwin")
            create_launchd_service
            ;;
        "Linux")
            create_systemd_service
            ;;
    esac
}

create_launchd_service() {
    log "Creating launchd service for macOS..."
    
    # Create launchd plist for Ollama health check
    cat > "$HOME/Library/LaunchAgents/com.voice.ollama.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.voice.ollama</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which python3)</string>
        <string>$HOME/.voice_services/ollama_launcher.py</string>
        <string>--action</string>
        <string>health</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.voice_services/logs/ollama.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.voice_services/logs/ollama_error.log</string>
</dict>
</plist>
EOF

    # Create logs directory
    mkdir -p "$HOME/.voice_services/logs"
    
    # Load service
    launchctl load "$HOME/Library/LaunchAgents/com.voice.ollama.plist"
    
    success "launchd service created and loaded"
}

create_systemd_service() {
    log "Creating systemd service for Linux..."
    
    # Create systemd service for Ollama health check
    sudo tee "/etc/systemd/system/voice-ollama.service" > /dev/null << EOF
[Unit]
Description=Voice Ollama Health Check Service
After=network.target ollama.service

[Service]
Type=simple
User=$USER
ExecStart=$(which python3) $HOME/.voice_services/ollama_launcher.py --action health
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable voice-ollama.service
    
    success "systemd service created and enabled"
}

# Create Ollama configuration
create_ollama_config() {
    log "Creating Ollama configuration..."
    
    # Create Ollama configuration directory
    CONFIG_DIR="$HOME/.voice_services"
    mkdir -p "$CONFIG_DIR/ollama"
    
    # Create Ollama service configuration
    cat > "$CONFIG_DIR/ollama/config.json" << EOF
{
    "host": "localhost",
    "port": 11434,
    "models": {
        "llama3.2": {
            "enabled": true,
            "priority": 1
        },
        "llama3.1": {
            "enabled": true,
            "priority": 2
        },
        "mistral": {
            "enabled": true,
            "priority": 3
        },
        "gemma2": {
            "enabled": true,
            "priority": 4
        },
        "phi3": {
            "enabled": true,
            "priority": 5
        }
    },
    "default_model": "llama3.2",
    "fallback_enabled": true,
    "health_check_interval": 60,
    "timeout": 120,
    "max_tokens": 2000,
    "temperature": 0.7,
    "stream": true
}
EOF
    
    success "Ollama configuration created at $CONFIG_DIR/ollama/config.json"
}

# Main installation function
main() {
    log "Starting Ollama installation..."
    
    check_root
    check_requirements
    install_ollama
    start_ollama_service
    setup_models
    create_ollama_launcher
    create_system_services
    create_ollama_config
    
    success "Ollama installation completed!"
    log ""
    log "Next steps:"
    log "1. Test Ollama: ollama list"
    log "2. Test a model: ollama run llama3.2"
    log "3. Check health service: curl http://localhost:11435/health"
    log ""
    log "Ollama service will automatically start on boot."
    log ""
    log "Available models:"
    log "  - llama3.2 (8B, recommended)"
    log "  - llama3.1 (8B)"
    log "  - mistral (7B)"
    log "  - gemma2 (9B)"
    log "  - phi3 (3.8B)"
}

# Run main function
main "$@"
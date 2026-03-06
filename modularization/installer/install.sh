#!/bin/bash

# Xoe-NovAi Omega Stack Beautiful Installer
# ==========================================
# A stunning, user-friendly installation system for the Omega stack

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INSTALLER_VERSION="1.0.0"
FRONTEND_PORT=3000
BACKEND_PORT=8001
INSTALLER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$INSTALLER_DIR/.." && pwd)"

# Logging
LOG_FILE="$PROJECT_ROOT/installer.log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

print_header() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    Xoe-NovAi Omega Stack                     ║"
    echo "║                  Beautiful Installer v$INSTALLER_VERSION                ║"
    echo "║                                                              ║"
    echo "║  Transform your sophisticated Omega stack into an accessible ║"
    echo "║  installation experience with stunning UI/UX and complete    ║"
    echo "║  customization options.                                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check if we're on a supported OS
    if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "Unsupported operating system. Please use Linux or macOS."
        exit 1
    fi
    
    # Check if Python 3.12+ is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 12 ]]; then
        print_error "Python 3.12+ is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Prerequisites check passed (Python $PYTHON_VERSION)"
}

install_frontend_dependencies() {
    print_step "Installing frontend dependencies..."
    
    cd "$INSTALLER_DIR/frontend"
    
    if ! command -v npm &> /dev/null; then
        print_error "Node.js and npm are required but not installed."
        print_info "Please install Node.js from https://nodejs.org/"
        exit 1
    fi
    
    if [ ! -d "node_modules" ]; then
        print_info "Installing npm dependencies..."
        npm install
    else
        print_info "Frontend dependencies already installed"
    fi
    
    print_success "Frontend dependencies ready"
}

install_backend_dependencies() {
    print_step "Installing backend dependencies..."
    
    cd "$INSTALLER_DIR/backend"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        # Install required packages
        pip install fastapi uvicorn[standard] python-socketio aiofiles python-multipart psutil
    fi
    
    print_success "Backend dependencies ready"
}

check_existing_omega_stack() {
    print_step "Checking for existing Omega stack..."
    
    cd "$PROJECT_ROOT"
    
    if [ -f "docker-compose.yml" ] || [ -f "Makefile" ]; then
        print_info "Existing Omega stack detected"
        echo ""
        echo "Found existing Omega stack components:"
        [ -f "docker-compose.yml" ] && echo "  ✓ Docker Compose configuration"
        [ -f "Makefile" ] && echo "  ✓ Makefile with build targets"
        [ -d "config" ] && echo "  ✓ Configuration directory"
        [ -d "app" ] && echo "  ✓ Application directory"
        echo ""
        
        read -p "Do you want to use the existing stack? (Y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            print_info "Proceeding with fresh installation"
        else
            print_success "Using existing Omega stack"
            return 0
        fi
    else
        print_info "No existing Omega stack found"
    fi
}

start_installer() {
    print_step "Starting beautiful installer..."
    
    # Start backend server
    print_info "Starting backend server on port $BACKEND_PORT..."
    cd "$INSTALLER_DIR/backend"
    source venv/bin/activate
    
    # Run backend in background
    uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
    BACKEND_PID=$!
    
    # Wait for backend to start
    sleep 3
    
    # Check if backend started successfully
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_error "Failed to start backend server"
        exit 1
    fi
    
    print_success "Backend server started (PID: $BACKEND_PID)"
    
    # Start frontend development server
    print_info "Starting frontend on port $FRONTEND_PORT..."
    cd "$INSTALLER_DIR/frontend"
    
    # Run frontend in background
    npm run dev &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    sleep 3
    
    # Check if frontend started successfully
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_error "Failed to start frontend server"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    print_success "Frontend server started (PID: $FRONTEND_PID)"
    
    # Open browser
    print_info "Opening installer in your browser..."
    sleep 2
    
    case "$(uname -s)" in
        Linux*)
            if command -v xdg-open &> /dev/null; then
                xdg-open "http://localhost:$FRONTEND_PORT" &
            fi
            ;;
        Darwin*)
            open "http://localhost:$FRONTEND_PORT" &
            ;;
        CYGWIN*|MINGW32*|MSYS*|MINGW*)
            start "http://localhost:$FRONTEND_PORT" &
            ;;
    esac
    
    print_success "Beautiful installer is now running!"
    echo ""
    echo "🌐 Frontend:  http://localhost:$FRONTEND_PORT"
    echo "🔌 Backend:   http://localhost:$BACKEND_PORT"
    echo "📄 Logs:      $LOG_FILE"
    echo ""
    echo "Press Ctrl+C to stop the installer"
    echo ""
    
    # Wait for user to stop the installer
    trap 'cleanup' INT
    wait
}

cleanup() {
    print_step "Cleaning up..."
    
    # Kill frontend and backend processes
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        print_success "Frontend server stopped"
    fi
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        print_success "Backend server stopped"
    fi
    
    print_success "Cleanup complete"
    exit 0
}

show_help() {
    echo "Xoe-NovAi Omega Stack Beautiful Installer"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h     Show this help message"
    echo "  --version, -v  Show version information"
    echo "  --clean        Clean up previous installations"
    echo "  --headless     Run in headless mode (no browser)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start the beautiful installer"
    echo "  $0 --clean            # Clean previous installation"
    echo "  $0 --headless         # Start without opening browser"
}

show_version() {
    echo "Xoe-NovAi Omega Stack Beautiful Installer v$INSTALLER_VERSION"
    echo "Built on: $(date)"
}

clean_installation() {
    print_step "Cleaning previous installation..."
    
    # Stop any running processes
    pkill -f "uvicorn" || true
    pkill -f "npm run dev" || true
    
    # Remove temporary files
    rm -f "$PROJECT_ROOT/docker-compose.installer.yml"
    rm -rf "$INSTALLER_DIR/frontend/node_modules"
    rm -rf "$INSTALLER_DIR/backend/venv"
    
    print_success "Cleanup complete"
}

# Main execution
main() {
    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --version|-v)
            show_version
            exit 0
            ;;
        --clean)
            clean_installation
            exit 0
            ;;
        --headless)
            print_header
            check_prerequisites
            install_frontend_dependencies
            install_backend_dependencies
            check_existing_omega_stack
            print_info "Headless mode: Backend server started on port $BACKEND_PORT"
            print_info "Frontend development server started on port $FRONTEND_PORT"
            print_info "Please open http://localhost:$FRONTEND_PORT in your browser"
            print_info "Press Ctrl+C to stop"
            trap 'cleanup' INT
            wait
            ;;
        "")
            print_header
            check_prerequisites
            install_frontend_dependencies
            install_backend_dependencies
            check_existing_omega_stack
            start_installer
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
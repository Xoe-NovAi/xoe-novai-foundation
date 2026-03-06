# Xoe-NovAi Omega Stack Beautiful Installer

A stunning, user-friendly installation system for the Xoe-NovAi Omega Stack that transforms sophisticated infrastructure into an accessible, beautiful experience.

## 🌟 Features

### 🎨 Beautiful UI/UX
- **Modern Design**: Clean, intuitive interface with smooth animations
- **Real-time Progress**: Live progress tracking with detailed status updates
- **Responsive Layout**: Works perfectly on desktop and tablet devices
- **Dark/Light Theme**: Automatic theme switching with user preferences

### ⚡ Fast & Efficient
- **Optimized Installation**: Parallel processing where possible
- **Smart Dependencies**: Automatic dependency resolution and caching
- **Progressive Loading**: Only load what's needed when it's needed
- **Error Recovery**: Graceful handling of installation failures

### 🔧 Complete Customization
- **Multiple Presets**: Quick Start, Standard, Enterprise, and Development stacks
- **Granular Control**: Choose exactly which services to install
- **Environment Selection**: Development, staging, and production configurations
- **Provider Selection**: Support for multiple AI providers and services

### 🛡️ Enterprise Ready
- **Security First**: No hardcoded secrets, secure credential handling
- **Validation Framework**: Comprehensive testing and validation
- **Logging & Monitoring**: Detailed installation logs and metrics
- **Rollback Support**: Ability to pause, cancel, and resume installations

## 🚀 Quick Start

### Prerequisites
- **Operating System**: Linux or macOS
- **Python**: 3.12 or higher
- **Node.js**: 18 or higher (for frontend development)
- **Container Runtime**: Docker or Podman

### Installation

1. **Clone the installer**:
   ```bash
   cd modularization/installer
   ```

2. **Run the beautiful installer**:
   ```bash
   ./install.sh
   ```

3. **Open your browser**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001

4. **Follow the guided setup**:
   - System requirements check
   - Service selection and configuration
   - Installation progress tracking
   - Validation and completion

### Command Line Options

```bash
./install.sh --help           # Show help
./install.sh --version        # Show version
./install.sh --clean          # Clean previous installation
./install.sh --headless       # Run without opening browser
```

## 🏗️ Architecture

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   ├── pages/              # Main application pages
│   ├── contexts/           # State management
│   ├── hooks/              # Custom React hooks
│   ├── utils/              # Utility functions
│   └── styles/             # Global styles and themes
├── vite.config.ts          # Vite configuration
└── package.json            # Dependencies and scripts
```

### Backend (FastAPI + Python)
```
backend/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── venv/                   # Virtual environment
└── static/                 # Frontend build files
```

### Installation Flow

1. **System Check**: Verify prerequisites and system capabilities
2. **Service Selection**: Choose which components to install
3. **Configuration**: Set up environment and provider settings
4. **Installation**: Execute installation with real-time progress
5. **Validation**: Verify installation success and service health
6. **Completion**: Provide summary and next steps

## 📦 Available Services

### Core Services (Required)
- **RAG Engine**: Main retrieval-augmented generation service
- **Chainlit UI**: Web interface for interaction and monitoring
- **Redis Cache**: High-performance caching layer

### Optional Services
- **PostgreSQL**: Relational database for persistent storage
- **VictoriaMetrics**: Time-series database for metrics and monitoring
- **Qdrant**: Vector database for semantic search
- **MinIO**: Object storage for file management

### AI Providers
- **OpenCode**: Primary AI provider with multiple models
- **Antigravity**: Free frontier models access
- **Cline**: CLI integration and tool calling
- **Gemini**: Google's Gemini API integration

## 🎯 Installation Presets

### Quick Start (5 minutes)
Perfect for getting started quickly with core services only.
- RAG Engine
- Chainlit UI
- Redis Cache

### Standard Stack (10 minutes)
Recommended setup with multiple AI providers and monitoring.
- All Core Services
- Multiple AI Providers
- Enhanced Monitoring

### Enterprise Stack (15 minutes)
Production-ready with all features and advanced security.
- Complete Feature Set
- Advanced Security
- High Availability

### Development Stack (12 minutes)
With debug tools and source code for contributors.
- Debug Tools
- Source Code
- Hot Reloading

## 🔧 Configuration

### Environment Variables
```bash
# Backend configuration
export INSTALLER_PORT=8001
export INSTALLER_HOST=0.0.0.0
export LOG_LEVEL=INFO

# Frontend configuration
export VITE_API_URL=http://localhost:8001
export VITE_THEME=system
```

### Custom Configuration
Create a `config.json` file in the installer directory:
```json
{
  "preset": "standard",
  "environment": "development",
  "services": [
    {"id": "postgres", "selected": true},
    {"id": "victoriametrics", "selected": true}
  ],
  "providers": [
    {"id": "opencode", "selected": true},
    {"id": "antigravity", "selected": true}
  ]
}
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_installation.py
```

### Test Coverage
- ✅ Frontend dependencies validation
- ✅ Backend dependencies validation
- ✅ System requirements checking
- ✅ API endpoint functionality
- ✅ Installation process validation
- ✅ Error handling scenarios
- ✅ Progress tracking functionality
- ✅ Security validation
- ✅ Performance requirements
- ✅ User experience features

## 📊 Monitoring

### Installation Metrics
- **Progress Tracking**: Real-time installation progress
- **Performance Metrics**: Installation speed and efficiency
- **Error Reporting**: Detailed error information and suggestions
- **Resource Usage**: System resource monitoring during installation

### Health Checks
- **Service Status**: Verify all services are running
- **Port Availability**: Check required ports are open
- **Dependency Health**: Validate all dependencies are functional
- **Configuration Validation**: Ensure all configurations are correct

## 🔒 Security

### Best Practices
- **No Hardcoded Secrets**: All credentials are injected at runtime
- **Secure Communication**: HTTPS for all API communications
- **Input Validation**: Comprehensive validation of all user inputs
- **Error Handling**: Secure error messages without sensitive information

### Security Features
- **Credential Management**: Secure storage and retrieval of API keys
- **Access Control**: Role-based access to installation features
- **Audit Logging**: Complete audit trail of all installation activities
- **Vulnerability Scanning**: Automatic scanning for known vulnerabilities

## 🚨 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Check which process is using the port
lsof -i :3000
lsof -i :8001

# Kill the process if needed
kill -9 <PID>
```

**Python Dependencies Missing**
```bash
# Reinstall backend dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend Build Issues**
```bash
# Clean and rebuild frontend
cd frontend
rm -rf node_modules
npm install
npm run build
```

**Docker/Podman Issues**
```bash
# Check container runtime status
docker --version
podman --version

# Start container runtime if needed
sudo systemctl start docker
```

### Getting Help

1. **Check Logs**: Installation logs are saved to `installer.log`
2. **Run Tests**: Execute `python test_installation.py` for diagnostics
3. **Clean Installation**: Use `./install.sh --clean` to start fresh
4. **Community Support**: Join our Discord for community support

## 🤝 Contributing

We welcome contributions to make the installer even more beautiful!

### Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd modularization/installer

# Install development dependencies
./install.sh --headless

# Start development servers
cd frontend && npm run dev
cd backend && uvicorn main:app --reload
```

### Code Style
- **Frontend**: Follow React and TypeScript best practices
- **Backend**: Follow FastAPI and Python conventions
- **Styling**: Use Tailwind CSS with consistent naming
- **Testing**: Write comprehensive tests for all new features

### Pull Request Guidelines
1. Create feature branches from `main`
2. Write clear commit messages
3. Include tests for new functionality
4. Update documentation as needed
5. Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **React Community**: For the amazing ecosystem and tools
- **FastAPI Team**: For the excellent web framework
- **Tailwind CSS**: For beautiful, utility-first styling
- **Our Contributors**: For making this project beautiful

## 📞 Contact

For questions, support, or just to say hello:

- **Email**: support@xoe-novai.com
- **Discord**: [Join our community](https://discord.gg/xoe-novai)
- **GitHub**: [Open an issue](https://github.com/xoe-novai/omega-stack/issues)

---

**Transform your sophisticated Omega stack into an accessible, user-friendly installation experience. 🤖✨**
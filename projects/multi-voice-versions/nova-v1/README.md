# Enhanced Local Voice Setup

A comprehensive, production-ready local voice setup that integrates Claude Code with local LLMs (Ollama) and advanced TTS/STT models for a seamless voice conversation experience.

## ✨ Current Status

**Production Ready** - The voice assistant is fully operational with:
- ✅ **Whisper STT** running locally on port 2022 (with Core ML acceleration)
- ✅ **Kokoro TTS** running locally on port 8880
- ✅ **VoiceMode MCP** integration for Claude Code
- ✅ **Memory Bank** system with semantic search
- ✅ **macOS App Bundle** for easy launching
- ✅ **LaunchAgent** for system boot startup

## 🆕 Latest Updates (2026)

### Memory Bank System
The voice assistant now includes a sophisticated memory system:
- **SQLite-based persistent storage** for conversation history
- **Semantic search** using sentence embeddings (all-MiniLM-L6-v2)
- **Automatic cleanup** of expired memories
- **Context-aware responses** using relevant past conversations

### macOS Integration
- **VoiceAssistant.app** - Native macOS application bundle
- **LaunchAgent** - Automatic startup at login
- **Full Disk Access** support for seamless operation

## 🚀 Quick Start

### One-Command Installation

```bash
# Download and run the complete installation
curl -fsSL https://raw.githubusercontent.com/your-repo/voice-setup/master/install_scripts/install_all.sh | bash
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/voice-setup.git
cd voice-setup

# Run the complete installation
./install_scripts/install_all.sh
```

### Start Using Your Voice Setup

```bash
# Start all services
python3 ~/.voice_services/voice_launcher.py --action start

# Test the setup
python3 voice_orchestrator.py

# View monitoring dashboard
open http://localhost:8080
```

## 📋 System Requirements

### Minimum Requirements
- **OS**: macOS 10.15+ or Linux (Ubuntu 20.04+)
- **CPU**: 4-core processor
- **RAM**: 8GB (16GB recommended)
- **Storage**: 20GB free space
- **Python**: 3.8+

### Recommended Requirements
- **CPU**: 8-core processor or better
- **RAM**: 16GB+
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
- **Storage**: 50GB+ SSD

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Voice Orchestrator                      │
│              (Main service coordinator)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   STT       │ │   TTS       │ │   Ollama    │
│ Manager     │ │ Manager     │ │ Client      │
└─────────────┘ └─────────────┘ └─────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Canary      │ │ Orpheus     │ │ Llama 3.2   │
│ Qwen 2.5B   │ │ TTS 3B      │ │ Mistral     │
│ Whisper     │ │ XTTS v2     │ │ Gemma 2     │
│ Turbo       │ │ Piper       │ │ Phi-3       │
└─────────────┘ └─────────────┘ └─────────────┘
                      │
                      ▼
              ┌─────────────────┐
              │ Health Monitor  │
              │   (Circuit      │
              │   Breaker)      │
              └─────────────────┘
```

## 🎯 Key Features

### ✨ Multi-LLM Orchestration
- **Smart LLM Selection**: Automatically chooses between Claude Code and local Ollama models
- **Fallback Mechanism**: Seamless fallback when primary LLM is unavailable
- **Quality vs Speed Modes**: Choose between high-quality or fast response modes
- **Context Management**: Intelligent conversation history handling

### 🔊 Advanced Audio Processing
- **Multi-Model STT**: Canary Qwen 2.5B, Whisper Large V3 Turbo, and fallback options
- **High-Quality TTS**: Orpheus TTS 3B, XTTS v2, and Piper with voice cloning support
- **Voice Activity Detection**: Smart audio capture with configurable sensitivity
- **Audio Enhancement**: Noise reduction and echo cancellation

### 🏥 Production-Ready Monitoring
- **Real-time Health Monitoring**: Track all services with circuit breaker protection
- **Performance Metrics**: Latency tracking and success rate monitoring
- **Web Dashboard**: Beautiful monitoring interface at `http://localhost:8080`
- **Auto-restart**: Automatic service recovery with exponential backoff

### 🔧 Enterprise Configuration
- **Hierarchical Configuration**: Environment-based overrides and model-specific settings
- **Security Features**: Authentication, rate limiting, and IP filtering
- **Logging & Debugging**: Comprehensive logging with multiple levels
- **Service Discovery**: Automatic service detection and health checking

## 📦 Installed Components

### STT Models
- **Canary Qwen 2.5B**: High-accuracy speech recognition
- **Whisper Large V3 Turbo**: Fast and reliable transcription
- **Piper**: Lightweight fallback option

### TTS Models
- **Orpheus TTS 3B**: High-quality neural text-to-speech
- **XTTS v2**: Multilingual and customizable voices
- **Piper**: Fast and efficient speech synthesis

### LLM Models (via Ollama)
- **Llama 3.2**: Latest Llama model for general-purpose tasks
- **Mistral**: Efficient model optimized for coding
- **Gemma 2**: Google's high-performance model
- **Phi-3**: Small but capable model for quick responses

### Core Services
- **Voice Orchestrator**: Main service coordinator
- **Health Monitor**: Service health and circuit breaker
- **Configuration Manager**: Hierarchical configuration system
- **Monitoring Dashboard**: Web-based monitoring interface

## 🎛️ Configuration

### Main Configuration File
Edit `~/.voice_config.json` to customize your setup:

```json
{
    "voice": {
        "llm_mode": "auto",
        "quality_mode": "balanced",
        "stt_model": "canary_qwen_2.5b",
        "tts_model": "orpheus_3b",
        "ollama_model": "llama3.2"
    },
    "stt": {
        "confidence_threshold": 0.8,
        "language": "en",
        "enable_vad": true
    },
    "tts": {
        "voice": "default",
        "speed": 1.0,
        "emotion": "neutral",
        "enable_voice_cloning": false
    },
    "ollama": {
        "host": "localhost",
        "port": 11434,
        "timeout": 120
    }
}
```

### Environment Variables
Override configuration with environment variables:

```bash
export STT_MODEL=whisper_turbo
export TTS_MODEL=xtts_v2
export OLLAMA_MODEL=mistral
export LLM_MODE=ollama_only
```

### Quality Modes
- **high_quality**: Best audio quality, slower response
- **balanced**: Good balance of quality and speed (default)
- **high_speed**: Faster response, lower quality
- **ultra_fast**: Maximum speed, basic quality

## 🚀 Usage

### Start Services
```bash
# Start all services
python3 ~/.voice_services/voice_launcher.py --action start

# Start specific services
python3 ~/.voice_services/voice_launcher.py --action start --services stt tts

# Check service health
python3 ~/.voice_services/voice_launcher.py --action health
```

### Voice Conversation
```bash
# Start voice conversation
python3 voice_orchestrator.py

# The system will:
# 1. Listen for your voice input
# 2. Transcribe speech to text
# 3. Generate response using selected LLM
# 4. Convert response to speech
# 5. Play the response
```

### Monitoring Dashboard
Access the web-based monitoring dashboard:
- **URL**: http://localhost:8080
- **Features**: Real-time service status, performance metrics, logs
- **Auto-refresh**: Updates every 30 seconds

### API Usage
```python
from voice_orchestrator import VoiceOrchestrator

# Create orchestrator
orchestrator = VoiceOrchestrator()

# Start conversation
await orchestrator.start_conversation()

# Get status
status = orchestrator.get_status()
print(f"Active LLM: {status['active_llm']}")
print(f"STT Status: {status['stt_status']}")
print(f"TTS Status: {status['tts_status']}")
```

## 🔧 Advanced Configuration

### Voice Cloning
Enable voice cloning for personalized TTS:

```json
{
    "tts": {
        "enable_voice_cloning": true,
        "voice_clone_sample_path": "/path/to/voice/sample.wav"
    }
}
```

### Security Settings
Configure authentication and access control:

```json
{
    "security": {
        "enable_authentication": true,
        "api_key": "your-api-key-here",
        "allowed_ips": ["127.0.0.1", "192.168.1.0/24"],
        "rate_limit": 100
    }
}
```

### Performance Tuning
Optimize for your hardware:

```json
{
    "audio": {
        "sample_rate": 16000,
        "buffer_size": 1024,
        "vad_threshold": 0.5
    },
    "monitoring": {
        "metrics_interval": 30,
        "health_check_interval": 10
    }
}
```

## 📊 Monitoring & Troubleshooting

### Service Status
```bash
# Check all services
python3 ~/.voice_services/voice_launcher.py --action status

# Check specific service
curl http://localhost:2022/health  # STT Canary
curl http://localhost:8881/health  # TTS Orpheus
curl http://localhost:11434/api/tags  # Ollama
```

### Logs
```bash
# View service logs
tail -f ~/.voice_services/logs/*.log

# View orchestrator logs
tail -f voice_orchestrator.log
```

### Performance Metrics
```bash
# Get performance metrics
curl http://localhost:8080/api/metrics

# Example output:
{
    "stt_canary_qwen": {
        "average_response_time": 1.2,
        "success_rate": 0.95,
        "total_requests": 100
    }
}
```

### Common Issues

#### Service Won't Start
```bash
# Check dependencies
python3 -c "import torch; print(torch.__version__)"

# Check ports
sudo lsof -i :2022  # STT ports
sudo lsof -i :8881  # TTS ports
sudo lsof -i :11434  # Ollama port
```

#### Poor Audio Quality
```bash
# Check microphone
arecord -d 5 -f cd test.wav && aplay test.wav

# Adjust VAD settings
# Edit ~/.voice_config.json
{
    "stt": {
        "vad_aggressiveness": 1  # 0-3, lower = more sensitive
    }
}
```

#### Slow Response Times
```bash
# Check model loading
ollama list

# Use faster models
export OLLAMA_MODEL=phi3
export TTS_MODEL=piper
```

## 🔄 Updates & Maintenance

### Update Models
```bash
# Update Ollama models
ollama pull llama3.2
ollama pull mistral

# Update Python dependencies
source ~/.voice_venv/bin/activate
pip install --upgrade torch torchaudio
```

### Backup Configuration
```bash
# Backup configuration
cp ~/.voice_config.json ~/.voice_config.json.backup

# Backup models (optional)
tar -czf voice_models_backup.tar.gz ~/.voice_models/
```

### System Updates
```bash
# Update system dependencies
# macOS
brew update && brew upgrade

# Ubuntu/Debian
sudo apt update && sudo apt upgrade

# CentOS/RHEL
sudo yum update
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Claude Code Team**: For the excellent Claude Code platform
- **Ollama**: For making local LLMs accessible
- **OpenAI**: For Whisper and audio processing tools
- **NVIDIA**: For NeMo and speech processing frameworks
- **Community**: For all the amazing open-source contributions

## 📞 Support

For support and questions:
- **Issues**: [GitHub Issues](https://github.com/your-repo/voice-setup/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/voice-setup/discussions)
- **Documentation**: [Wiki](https://github.com/your-repo/voice-setup/wiki)

---

**Note**: This is a production-ready implementation designed for local deployment. Always ensure you have the necessary permissions and comply with local regulations when recording and processing audio.
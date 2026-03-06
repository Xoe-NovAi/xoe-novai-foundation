# OpenCode Multi-Account System Documentation

## 📚 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Plugin Development](#plugin-development)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🚀 Quick Start

### Installation

```bash
# Download the setup script
curl -O https://raw.githubusercontent.com/opencode/multi-account-system/main/modularization/setup.py

# Run interactive setup
python setup.py --interactive

# Or run automatic setup
python setup.py --auto --environment production
```

### Basic Usage

```bash
# Start the system
./bin/opencode-multi-account start

# Check system health
./bin/opencode-multi-account health

# View logs
./bin/opencode-multi-account logs

# Stop the system
./bin/opencode-multi-account stop
```

### Making Requests

```bash
# Using curl
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?", "provider": "opencode"}'

# Using Python
import requests
response = requests.post(
    "http://localhost:8080/api/v1/chat",
    json={"prompt": "Hello, how are you?", "provider": "opencode"}
)
print(response.json())
```

## ⚙️ Installation

### System Requirements

- Python 3.8+
- 2GB RAM minimum
- 100MB disk space
- Linux, macOS, or Windows

### Installation Methods

#### 1. Standalone Installation

```bash
# Download and run setup
python setup.py --install-dir /opt/opencode --environment production
```

#### 2. Docker Installation

```bash
# Pull from Docker Hub
docker pull opencode/multi-account:latest

# Run with configuration
docker run -d \
  --name opencode-multi-account \
  -p 8080:8080 \
  -v /path/to/config:/app/config \
  -v /path/to/data:/app/data \
  opencode/multi-account:latest
```

#### 3. Kubernetes Installation

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

## 🔧 Configuration

### Configuration Files

The system uses YAML configuration files located in the `config/` directory:

- `config.yaml` - Main configuration
- `providers.yaml` - Provider-specific settings
- `secrets.enc` - Encrypted secrets
- `environment.yaml` - Environment-specific overrides

### Environment Variables

```bash
# Basic configuration
export OPENCODE_ENV=production
export OPENCODE_CONFIG_PATH=/path/to/config
export OPENCODE_DEBUG=false

# Provider configuration
export OPENCODE_API_KEY=your-opencode-key
export ANTIGRAVITY_CLIENT_SECRET=your-secret
export GEMINI_API_KEY=your-gemini-key

# Storage configuration
export OPENCODE_STORAGE_PATH=/path/to/data
export OPENCODE_BACKUP_ENABLED=true

# Monitoring configuration
export OPENCODE_METRICS_ENABLED=true
export OPENCODE_HEALTH_CHECK_INTERVAL=300
```

### Provider Configuration

#### OpenCode Provider

```yaml
providers:
  opencode:
    enabled: true
    accounts:
      count: 8
      rotation_strategy: round_robin
      health_check_interval: 300
    credentials:
      template_path: ~/.config/xnai/opencode-credentials.yaml
      injection_enabled: true
```

#### Antigravity Provider

```yaml
providers:
  antigravity:
    enabled: true
    oauth:
      client_id: your-client-id
      client_secret: your-client-secret
    models:
      - opus-4-6-thinking
      - claude-sonnet
    quality_validation: true
```

#### Gemini Provider

```yaml
providers:
  gemini:
    enabled: true
    api_key: your-gemini-api-key
    context_window: 8192
    quality_score: 90
```

## 📡 API Reference

### Health Check

```http
GET /health
```

Returns system health status.

**Response:**
```json
{
  "system_state": "running",
  "timestamp": "2024-01-01T12:00:00Z",
  "components": {
    "account_manager": {"status": "ok"},
    "rotation_manager": {"status": "ok"}
  },
  "providers": {
    "opencode": true,
    "antigravity": true
  },
  "overall_health": "healthy"
}
```

### Chat API

```http
POST /api/v1/chat
Content-Type: application/json

{
  "prompt": "Your question here",
  "provider": "opencode",  // Optional
  "context": {
    "conversation_id": "123",
    "user_id": "user123"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "response": "Answer from AI provider",
  "provider": "opencode",
  "response_time": 2.5,
  "context": {
    "conversation_id": "123",
    "provider_used": "opencode"
  }
}
```

### Metrics API

```http
GET /api/v1/metrics
```

Returns system and provider metrics.

**Response:**
```json
{
  "system": {
    "uptime_seconds": 3600,
    "active_accounts": 8,
    "total_requests": 1000,
    "successful_requests": 950,
    "failed_requests": 50,
    "average_response_time": 2.5,
    "memory_usage_mb": 256,
    "cpu_usage_percent": 15.5
  },
  "providers": {
    "opencode": {
      "status": "healthy",
      "response_time": 2.1,
      "success_rate": 0.95,
      "total_requests": 800
    }
  }
}
```

### Provider Management

```http
GET /api/v1/providers
```

Lists all available providers.

```http
POST /api/v1/providers/{name}/health
```

Triggers health check for specific provider.

## 🔌 Plugin Development

### Creating a Provider Plugin

1. Create a new Python module:

```python
# providers/my_provider.py
from modularization.core.plugin_system import ProviderPlugin
import asyncio

class MyProviderPlugin(ProviderPlugin):
    __plugin_name__ = "my-provider"
    __version__ = "1.0.0"
    __description__ = "My custom AI provider"
    __author__ = "Your Name"
    __dependencies__ = []

    async def initialize(self, config: dict) -> bool:
        # Initialize your provider
        self.api_key = config.get("api_key")
        return True

    async def get_response(self, prompt: str, context: dict = None) -> dict:
        # Implement your provider logic
        return {
            "status": "success",
            "response": "Response from my provider",
            "provider": "my-provider",
            "response_time": 1.5
        }

    async def health_check(self) -> bool:
        # Check if your provider is healthy
        return True

    async def get_metrics(self) -> dict:
        return {
            "status": "healthy",
            "response_time": 1.5,
            "success_rate": 0.95
        }
```

2. Register your plugin:

```python
# In your plugin module
from modularization.core.plugin_system import PluginRegistry

registry = PluginRegistry()
registry.register_plugin("my-provider", MyProviderPlugin, MyProviderPlugin.get_metadata())
```

### Creating an Integration Plugin

```python
# integrations/my_integration.py
from modularization.core.plugin_system import IntegrationPlugin
import asyncio

class MyIntegrationPlugin(IntegrationPlugin):
    __plugin_name__ = "my-integration"
    __version__ = "1.0.0"
    __description__ = "My custom integration"
    __author__ = "Your Name"

    async def initialize(self, config: dict) -> bool:
        self.webhook_url = config.get("webhook_url")
        return True

    async def start(self) -> bool:
        # Start your integration service
        return True

    async def stop(self) -> None:
        # Stop your integration service
        pass

    async def handle_event(self, event_type: str, data: dict) -> None:
        # Handle system events
        if event_type == "health_check":
            print(f"Health check: {data}")
```

## 🚢 Deployment

### Production Deployment

1. **Environment Setup:**
   ```bash
   # Set up production environment
   python setup.py --environment production --install-dir /opt/opencode
   ```

2. **Configuration:**
   ```yaml
   # config/environment.yaml
   environment: production
   debug: false
   log_level: INFO
   
   monitoring:
     enabled: true
     metrics_interval: 300
     health_check_interval: 600
   ```

3. **Service Management:**
   ```bash
   # Start as system service
   sudo systemctl enable opencode-multi-account
   sudo systemctl start opencode-multi-account
   
   # Check status
   sudo systemctl status opencode-multi-account
   ```

### Docker Deployment

```bash
# Build custom image
docker build -t opencode/multi-account:custom .

# Run with custom configuration
docker run -d \
  --name opencode-multi-account \
  -p 8080:8080 \
  -v /host/config:/app/config \
  -v /host/data:/app/data \
  -v /host/logs:/app/logs \
  -e OPENCODE_ENV=production \
  -e OPENCODE_DEBUG=false \
  opencode/multi-account:custom
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opencode-multi-account
spec:
  replicas: 3
  selector:
    matchLabels:
      app: opencode-multi-account
  template:
    metadata:
      labels:
        app: opencode-multi-account
    spec:
      containers:
      - name: opencode-multi-account
        image: opencode/multi-account:latest
        ports:
        - containerPort: 8080
        env:
        - name: OPENCODE_ENV
          value: "production"
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: data-volume
          mountPath: /app/data
      volumes:
      - name: config-volume
        configMap:
          name: opencode-config
      - name: data-volume
        persistentVolumeClaim:
          claimName: opencode-data-pvc
```

## 📊 Monitoring

### Health Monitoring

The system provides comprehensive health monitoring:

```bash
# Check system health
curl http://localhost:8080/health

# Check specific provider health
curl http://localhost:8080/api/v1/providers/opencode/health
```

### Metrics Collection

```bash
# Get system metrics
curl http://localhost:8080/api/v1/metrics

# Get provider metrics
curl http://localhost:8080/api/v1/providers/metrics
```

### Prometheus Integration

```yaml
# Prometheus configuration
- job_name: 'opencode-multi-account'
  static_configs:
  - targets: ['localhost:8080']
  metrics_path: '/metrics'
  scrape_interval: 30s
```

### Alerting

Configure alerts for:

- System health degradation
- Provider failures
- High error rates
- Slow response times
- Resource exhaustion

## 🔧 Troubleshooting

### Common Issues

#### 1. Provider Not Responding

```bash
# Check provider health
./bin/opencode-multi-account health

# Check provider logs
tail -f logs/opencode-multi-account.log | grep "opencode"
```

#### 2. Configuration Errors

```bash
# Validate configuration
python -c "
from modularization.core.config_manager import config_manager
import asyncio
async def test():
    config = await config_manager.load_config()
    print('Configuration loaded successfully')
asyncio.run(test())
"
```

#### 3. Permission Issues

```bash
# Fix permissions
sudo chown -R $(whoami) /path/to/installation
sudo chmod -R 755 /path/to/installation
```

#### 4. Memory Issues

```bash
# Check memory usage
./bin/opencode-multi-account health

# Adjust memory limits in configuration
# config.yaml
monitoring:
  memory_threshold_mb: 1000
```

### Debug Mode

```bash
# Enable debug mode
export OPENCODE_DEBUG=true
export OPENCODE_LOG_LEVEL=DEBUG

# Restart system
./bin/opencode-multi-account restart
```

### Log Analysis

```bash
# View all logs
./bin/opencode-multi-account logs

# Filter by provider
tail -f logs/opencode-multi-account.log | grep "opencode"

# Filter by error
tail -f logs/opencode-multi-account.log | grep "ERROR"
```

## 🤝 Contributing

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/opencode/multi-account-system.git
   cd multi-account-system
   ```

2. **Install development dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Run tests:**
   ```bash
   pytest
   ```

4. **Code quality checks:**
   ```bash
   ruff check .
   black --check .
   mypy .
   ```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for all public functions
- Use async/await for I/O operations
- Handle exceptions properly

### Testing

- Write unit tests for all new features
- Use pytest for testing framework
- Mock external dependencies
- Test error conditions
- Use test fixtures for configuration

### Pull Request Guidelines

1. Create feature branch from `main`
2. Write clear commit messages
3. Update documentation for new features
4. Ensure all tests pass
5. Get code review before merging

## 📞 Support

### Getting Help

- **Documentation:** [docs.opencode.ai](https://docs.opencode.ai)
- **Issues:** [GitHub Issues](https://github.com/opencode/multi-account-system/issues)
- **Discussions:** [GitHub Discussions](https://github.com/opencode/multi-account-system/discussions)
- **Email:** support@opencode.ai

### Reporting Bugs

When reporting bugs, please include:

1. System information (OS, Python version)
2. Steps to reproduce the issue
3. Expected vs actual behavior
4. Error messages and stack traces
5. Configuration files (with sensitive data removed)

### Feature Requests

For feature requests:

1. Describe the feature and use case
2. Explain why it's needed
3. Provide examples if possible
4. Consider submitting a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenCode Team
- Contributors
- Community feedback
- Early adopters
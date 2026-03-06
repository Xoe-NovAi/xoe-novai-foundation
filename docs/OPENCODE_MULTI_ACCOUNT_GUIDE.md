# OpenCode Multi-Account System Implementation Guide

## Overview

This guide documents the complete implementation of the OpenCode multi-account system with MiniMax m2.5 prime working memory and Antigravity Opus 4.6 integration. The system enables free tier usage limit remediation through account rotation while maintaining high-quality AI interactions.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Quick Start](#quick-start)
3. [Configuration Reference](#configuration-reference)
4. [Usage Examples](#usage-examples)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Troubleshooting](#troubleshooting)
7. [Performance Optimization](#performance-optimization)

## System Architecture

### Core Components

1. **OpenCode Multi-Account System**
   - 8 concurrent OpenCode accounts
   - XDG_DATA_HOME isolation pattern
   - Round-robin rotation strategy
   - Health monitoring and fallback

2. **MiniMax m2.5 prime Working Memory**
   - Fast response times for working memory operations
   - Context window optimization
   - Quality validation checkpoints
   - Seamless handoff to premium models

3. **Antigravity Free Frontier Models**
   - Google OAuth authentication
   - Free tier access to frontier models
   - Opus 4.6 thinking model integration
   - Quality validation and monitoring

4. **Working Memory Handoff Protocol**
   - Context preservation during handoff
   - Quality validation checkpoints
   - Seamless model switching
   - Usage optimization

5. **Performance Optimization & Monitoring**
   - Cross-model context window optimization
   - Real-time usage tracking
   - Intelligent alerting system
   - Performance monitoring dashboard

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                           │
│  (OpenCode CLI, Dashboard, API)                            │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                    Load Balancer                            │
│  (Account Selection, Health Monitoring)                     │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                    Working Memory                           │
│  (MiniMax m2.5 prime - 8 instances)                        │
│  - Fast response times                                     │
│  - Context window management                               │
│  - Quality validation                                      │
└─────────────┬───────────────────────────────────────────────┘
              │ (Handoff when needed)
┌─────────────▼───────────────────────────────────────────────┐
│                    Premium Models                           │
│  (Antigravity Opus 4.6, Gemini 20B, Qwen Plus)             │
│  - Complex reasoning                                         │
│  - Long-form generation                                      │
│  - Quality preservation                                      │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                    Monitoring & Logging                     │
│  (Usage tracking, Performance metrics, Alerts)              │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Prerequisites

Ensure you have the following installed:
- OpenCode CLI (v1.2.15+)
- yq (for YAML processing)
- jq (for JSON processing)
- systemd (for service management)

```bash
# Install dependencies
sudo apt update
sudo apt install -y yq jq systemd

# Install OpenCode CLI
# (Follow official installation instructions)
```

### 2. Run the Complete Setup

```bash
# Navigate to the project directory
cd /path/to/omega-stack

# Run the complete setup
./scripts/setup-opencode-multiaccount.sh all
```

### 3. Configure Credentials

Edit the environment file with your actual credentials:

```bash
# Edit environment variables
nano ~/.config/xnai/.env

# Edit OpenCode credentials
nano ~/.config/xnai/opencode-credentials.yaml
```

### 4. Inject Credentials

```bash
# Inject credentials for all accounts
./scripts/xnai-inject-credentials.sh ~/.config/xnai/opencode-credentials.yaml all
```

### 5. Start Monitoring

```bash
# Start the monitoring dashboard
~/.config/xnai/start-dashboard.sh

# Monitor rotation service
journalctl -u xnai-opencode-rotation.service -f
```

## Configuration Reference

### OpenCode Credentials Configuration

Location: `~/.config/xnai/opencode-credentials.yaml`

```yaml
credentials:
  opencode:
    accounts:
      account_1:
        name: "OpenCode Account 1"
        email: "user1@example.com"
        api_key: "${OPENCODE_API_KEY_1}"
        xdg_data_home: "/tmp/xnai-opencode-instance-1"
        port: 10001
        status: "active"
      # ... accounts 2-8
```

**Required Environment Variables:**
- `OPENCODE_API_KEY_1` through `OPENCODE_API_KEY_8`

### Working Memory Configuration

Location: `~/.config/xnai/minimax-working-memory.yaml`

```yaml
working_memory:
  model: "minimax-m2.5-free"
  instances:
    - name: "working_memory_1"
      xdg_data_home: "/tmp/xnai-opencode-instance-1"
      port: 10001
      priority: 1
      status: "active"
  # ... additional instances
```

### Antigravity Configuration

Location: `~/.config/xnai/antigravity-free-frontier.yaml`

```yaml
antigravity:
  authentication:
    type: "google_oauth"
    client_id: "${ANTIGRAVITY_CLIENT_ID}"
    client_secret: "${ANTIGRAVITY_CLIENT_SECRET}"
    redirect_uri: "http://localhost:8080/callback"
```

**Required Environment Variables:**
- `ANTIGRAVITY_CLIENT_ID`
- `ANTIGRAVITY_CLIENT_SECRET`

### Performance Optimization Configuration

Location: `~/.config/xnai/performance-optimization.yaml`

```yaml
performance_optimization:
  context_window_optimization:
    enabled: true
    models:
      minimax_m2_5_free:
        strategy: "aggressive_compression"
        compression_ratio: 0.6
        quality_threshold: 0.8
```

## Usage Examples

### Basic Working Memory Usage

```bash
# Use working memory with account 1
XDG_DATA_HOME=/tmp/xnai-opencode-instance-1 opencode chat \
  --model minimax-m2.5-free \
  --json 'What is the capital of France?'

# Use working memory with context management
XDG_DATA_HOME=/tmp/xnai-opencode-instance-1 opencode chat \
  --model minimax-m2.5-free \
  --context-size 4096 \
  --json 'Summarize the following text...'
```

### Premium Model Usage

```bash
# Use Antigravity Opus 4.6
XDG_DATA_HOME=/tmp/xnai-opencode-instance-1 opencode chat \
  --model "google/antigravity-claude-opus-4-6-thinking" \
  --json 'Perform complex analysis...'

# Use with quality validation
XDG_DATA_HOME=/tmp/xnai-opencode-instance-1 opencode chat \
  --model "google/antigravity-claude-opus-4-6-thinking" \
  --enable-quality-validation \
  --json 'Generate comprehensive report...'
```

### Working Memory with Handoff

```bash
# Automatic handoff with context preservation
XDG_DATA_HOME=/tmp/xnai-opencode-instance-1 opencode chat \
  --model minimax-m2.5-free \
  --auto-handoff \
  --compression-strategy "adaptive" \
  --json 'Generate comprehensive report...'

# Manual handoff trigger
XDG_DATA_HOME=/tmp/xnai-opencode-instance-1 opencode chat \
  --model minimax-m2.5-free \
  --enable-handoff \
  --target-model "google/antigravity-claude-opus-4-6-thinking" \
  --json 'Perform complex analysis...'
```

### Testing All Accounts

```bash
# Test all 8 accounts
for i in {1..8}; do
  echo "Testing account $i:"
  XDG_DATA_HOME="/tmp/xnai-opencode-instance-$i" opencode chat \
    --json 'test' 2>&1 | head -3
  echo "---"
done
```

## Monitoring and Maintenance

### Dashboard Access

```bash
# Start dashboard
~/.config/xnai/start-dashboard.sh

# Access dashboard
# URL: http://localhost:8080
# Username: admin (or your configured username)
# Password: your-secure-password
```

### Monitoring Commands

```bash
# Check rotation service status
systemctl status xnai-opencode-rotation.timer
systemctl --user status xnai-opencode-rotation.timer

# View rotation logs
journalctl -u xnai-opencode-rotation.service -f
journalctl --user -u xnai-opencode-rotation.service -f

# Check account health
./scripts/xnai-inject-credentials.sh ~/.config/xnai/opencode-credentials.yaml all --validate-only

# Monitor usage metrics
curl http://localhost:8080/api/metrics/usage
```

### Maintenance Tasks

```bash
# Update credentials
./scripts/xnai-inject-credentials.sh ~/.config/xnai/opencode-credentials.yaml all

# Restart rotation service
sudo systemctl restart xnai-opencode-rotation.timer
systemctl --user restart xnai-opencode-rotation.timer

# Check system health
./scripts/setup-opencode-multiaccount.sh validate
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failures

**Symptoms:**
- "Invalid token" errors
- Authentication timeouts
- OAuth failures

**Solutions:**
```bash
# Check environment variables
echo $OPENCODE_API_KEY_1
echo $ANTIGRAVITY_CLIENT_ID

# Re-inject credentials
./scripts/xnai-inject-credentials.sh ~/.config/xnai/opencode-credentials.yaml all

# Check token validity
XDG_DATA_HOME=/tmp/xnai-opencode-instance-1 opencode chat --json 'test'
```

#### 2. Context Window Issues

**Symptoms:**
- "Context window full" errors
- Poor response quality
- Slow response times

**Solutions:**
```bash
# Check context utilization
curl http://localhost:8080/api/metrics/context

# Adjust compression settings
# Edit ~/.config/xnai/performance-optimization.yaml

# Force context compression
XDG_DATA_HOME=/tmp/xnai-opencode-instance-1 opencode chat \
  --model minimax-m2.5-free \
  --compression-strategy "aggressive" \
  --json 'Your prompt'
```

#### 3. Performance Issues

**Symptoms:**
- Slow response times
- High memory usage
- Service timeouts

**Solutions:**
```bash
# Check system resources
top
free -h
df -h

# Restart services
sudo systemctl restart xnai-opencode-rotation.timer

# Check performance metrics
curl http://localhost:8080/api/metrics/performance

# Adjust optimization settings
# Edit ~/.config/xnai/performance-optimization.yaml
```

#### 4. Service Issues

**Symptoms:**
- Rotation service not running
- Dashboard not accessible
- Systemd service failures

**Solutions:**
```bash
# Check service status
systemctl status xnai-opencode-rotation.timer
systemctl --user status xnai-opencode-rotation.timer

# View service logs
journalctl -u xnai-opencode-rotation.service -n 50
journalctl --user -u xnai-opencode-rotation.service -n 50

# Restart services
sudo systemctl restart xnai-opencode-rotation.timer
systemctl --user restart xnai-opencode-rotation.timer

# Check dashboard
curl http://localhost:8080/health
```

### Debug Commands

```bash
# Check all configuration files
ls -la ~/.config/xnai/

# Validate YAML configurations
yq eval '.' ~/.config/xnai/opencode-credentials.yaml
yq eval '.' ~/.config/xnai/minimax-working-memory.yaml

# Test individual accounts
for i in {1..8}; do
  echo "Testing account $i:"
  timeout 30 XDG_DATA_HOME="/tmp/xnai-opencode-instance-$i" opencode chat --json 'health check' || echo "Account $i failed"
done

# Check systemd timers
systemctl list-timers --user
sudo systemctl list-timers
```

## Performance Optimization

### Context Window Optimization

The system automatically optimizes context window usage across models:

1. **MiniMax m2.5 free**: Aggressive compression (60% ratio)
2. **Opus 4.6 thinking**: Quality preservation (80% ratio)
3. **Gemini 20B thinking**: Balanced approach (70% ratio)
4. **Qwen Plus thinking**: Adaptive compression (75% ratio)

### Usage Distribution

The rotation system distributes usage across 8 accounts:
- Each account gets approximately 12.5% of total usage
- Health monitoring ensures only healthy accounts are used
- Fallback mechanisms handle account failures

### Quality Validation

The system validates quality at multiple checkpoints:
1. **Pre-handoff**: Context integrity and task completeness
2. **Post-handoff**: Context transfer and response quality
3. **Continuous**: Response coherence and user satisfaction

### Monitoring Metrics

Key metrics tracked by the system:
- **Token usage**: Per model and per account
- **Context utilization**: Real-time window usage
- **Response times**: Model performance metrics
- **Quality scores**: User satisfaction and coherence
- **Error rates**: System reliability metrics

### Optimization Tips

1. **Regular Monitoring**: Check dashboard daily for usage patterns
2. **Credential Management**: Rotate API keys regularly
3. **Resource Allocation**: Monitor system resources and adjust as needed
4. **Quality Tuning**: Adjust compression ratios based on quality feedback
5. **Account Health**: Regularly test all accounts for functionality

## Security Considerations

### Credential Security

- Store API keys in environment variables, not in files
- Use secure file permissions (0600) for credential files
- Regularly rotate API keys and OAuth credentials
- Monitor for unauthorized usage

### Data Protection

- Enable encryption for sensitive data
- Implement proper access controls
- Regular security audits
- Monitor for data breaches

### Network Security

- Use HTTPS for dashboard access
- Implement firewall rules for service ports
- Monitor network traffic for anomalies
- Regular security updates

## Conclusion

The OpenCode multi-account system provides a robust, scalable solution for free tier usage limit remediation while maintaining high-quality AI interactions. The system's modular design allows for easy customization and extension, while comprehensive monitoring ensures reliable operation.

For additional support or questions, refer to the project documentation or contact the development team.
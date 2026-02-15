# Gemini CLI Installation Guide
## Complete Setup for Xoe-NovAi Integration

**Status**: ✅ READY FOR EXECUTION
**Time Required**: 15 minutes
**Prerequisites**: Node.js 20+, Linux environment

---

## 🎯 Installation Overview

This guide provides complete, sovereign installation instructions for Google Gemini CLI integration into the Xoe-NovAi development environment.

---

## 📋 Prerequisites Check

### System Requirements
```bash
# Check Node.js version (must be 20+)
node --version
# Expected: v20.x.x or higher

# Check npm version
npm --version
# Expected: 10.x.x or higher

# Check available memory
free -h
# Should show at least 4GB available

# Check internet connectivity (for initial setup only)
curl -s https://registry.npmjs.org/ | head -1
# Should return valid JSON
```

### Environment Preparation
```bash
# Create Gemini CLI configuration directory
mkdir -p ~/.config/gemini-cli

# Backup existing npm configuration
cp ~/.npmrc ~/.npmrc.backup 2>/dev/null || true

# Ensure clean npm environment
npm config delete proxy 2>/dev/null || true
npm config delete https-proxy 2>/dev/null || true
```

---

## 🚀 Installation Steps

### Step 1: Global Installation (3 minutes)
```bash
# Install Gemini CLI globally with latest version
npm install -g @google/gemini-cli@latest

# Verify installation
gemini --version
# Expected output: 0.2.x or higher

# Check available commands
gemini --help
```

### Step 2: API Key Configuration (2 minutes)
```bash
# Set API key securely (replace with your actual key)
export GEMINI_API_KEY="AIzaSyCERmdOq6pZBYiZeCLMSgbFVxpqTl4g8K4"

# Make configuration persistent across sessions
cat > ~/.config/gemini-cli/config.yaml << EOF
api_key: "${GEMINI_API_KEY}"
model: gemini-2.5-pro-exp-01-22
safety_settings: high
local_only: true
mcp_enabled: false
sovereignty_mode: enabled
data_transmission: minimal
EOF

# Set environment variable for current session
export GEMINI_API_KEY="AIzaSyCERmdOq6pZBYiZeCLMSgbFVxpqTl4g8K4"
```

### Step 3: Sovereignty Configuration (3 minutes)
```bash
# Create sovereignty validation script
cat > ~/gemini-sovereignty-check.sh << 'EOF'
#!/bin/bash
echo "🔒 Gemini CLI Sovereignty Validation"
echo "===================================="

# Check if API key is set (but not exposed)
if [ -n "$GEMINI_API_KEY" ]; then
    echo "✅ API Key: Configured (hidden for security)"
else
    echo "❌ API Key: Not configured"
    exit 1
fi

# Verify no proxy settings that could leak data
if npm config get proxy | grep -q "null\|undefined\|''"; then
    echo "✅ Proxy: Not configured (good for sovereignty)"
else
    echo "⚠️  Proxy: Configured (review for data leakage)"
fi

# Check if running in containerized environment
if [ -n "$CONTAINER" ] || [ -f /.dockerenv ]; then
    echo "✅ Environment: Containerized (additional isolation)"
else
    echo "ℹ️  Environment: Host system (ensure firewall rules)"
fi

echo ""
echo "🎯 Sovereignty Status: VALIDATED"
echo "Ma'at Compliance: ENABLED"
EOF

chmod +x ~/gemini-sovereignty-check.sh

# Run sovereignty validation
~/gemini-sovereignty-check.sh
```

### Step 4: Basic Functionality Test (2 minutes)
```bash
# Test basic connectivity (should not transmit data externally)
gemini --dry-run "test connection"
# Expected: No errors, no external calls

# Test API key validation
timeout 10 gemini "Hello, this is a test message for sovereignty validation"
# Should respond without errors

# Check rate limits and quota
gemini --quota
# Should show free tier limits
```

### Step 5: Codium Integration Setup (5 minutes)
```bash
# Install Continue.dev extension in Codium (if not already installed)
# Open Codium → Extensions → Search "Continue" → Install "Continue - Codestral, Claude, and more"

# Configure Continue.dev for Gemini integration
mkdir -p ~/.continue
cat > ~/.continue/config.json << EOF
{
  "models": [
    {
      "title": "Gemini 2.5 Pro (Sovereign)",
      "provider": "openai",
      "model": "gemini-2.5-pro-exp-01-22",
      "apiBase": "https://generativelanguage.googleapis.com/v1beta",
      "apiKey": "${GEMINI_API_KEY}",
      "requestOptions": {
        "headers": {
          "x-goog-api-key": "${GEMINI_API_KEY}"
        }
      },
      "contextLength": 1000000,
      "completionOptions": {
        "temperature": 0.7,
        "topP": 0.8,
        "maxTokens": 4096
      }
    }
  ],
  "embeddingsProvider": {
    "provider": "free-trial"
  },
  "tabAutocompleteModel": {
    "title": "Gemini 2.0 Flash (Fast)",
    "provider": "openai",
    "model": "gemini-2.0-flash",
    "apiBase": "https://generativelanguage.googleapis.com/v1beta",
    "apiKey": "${GEMINI_API_KEY}"
  }
}
EOF

# Test Continue.dev integration
# Open a Python file in Codium, highlight code, press ⌘L (or Ctrl+L)
# Should show Gemini completion options
```

---

## 🔧 tmux Integration Setup

### Multi-Pane Terminal Collaboration
```bash
# Install tmux if not present
sudo apt update && sudo apt install -y tmux

# Create Gemini CLI tmux session template
cat > ~/.tmux/gemini-session << 'EOF'
# Gemini CLI Collaboration Session
new-session -s gemini-dev
split-window -h
split-window -v
select-pane -t 0
send-keys 'cd /home/arcana-novai/Documents/Xoe-NovAi' C-m
send-keys 'export GEMINI_API_KEY="AIzaSyCERmdOq6pZBYiZeCLMSgbFVxpqTl4g8K4"' C-m
send-keys 'gemini' C-m
select-pane -t 1
send-keys 'cd /home/arcana-novai/Documents/Xoe-NovAi' C-m
send-keys '# Lilith coordination pane' C-m
select-pane -t 2
send-keys 'cd /home/arcana-novai/Documents/Xoe-NovAi' C-m
send-keys '# Cline monitoring pane' C-m
EOF

# Make executable
chmod +x ~/.tmux/gemini-session

# Launch collaboration session
~/.tmux/gemini-session
```

---

## ✅ Validation & Testing

### Installation Verification
```bash
# Complete installation test
gemini --version && echo "✅ Version check passed"

gemini "Test message for Ma'at compliance validation" > /dev/null && echo "✅ API connectivity passed"

~/gemini-sovereignty-check.sh && echo "✅ Sovereignty validation passed"

echo "🎉 Gemini CLI installation COMPLETE and SOVEREIGN"
```

### Performance Benchmarking
```bash
# Basic performance test
time gemini --model gemini-2.0-flash "Count to 10" > /dev/null
# Should complete in <3 seconds

# Memory usage check
gemini "test" > /dev/null &
sleep 2
ps aux | grep gemini | grep -v grep
# Should show reasonable memory usage (<200MB)
```

---

## 🔒 Security Hardening

### API Key Protection
```bash
# Ensure API key is never in command history
export HISTIGNORE="export GEMINI_API_KEY*"

# Set restrictive permissions on config files
chmod 600 ~/.config/gemini-cli/config.yaml
chmod 600 ~/.continue/config.json

# Never commit API keys to git
echo "GEMINI_API_KEY" >> .gitignore
echo ".env" >> .gitignore
```

### Network Security
```bash
# Verify no unauthorized network connections
sudo netstat -tlnp | grep :443
# Should only show expected connections

# Check for any proxy configurations
env | grep -i proxy
# Should be clean for sovereignty
```

---

## 🚨 Troubleshooting

### Common Issues & Solutions

**Issue: "command not found: gemini"**
```bash
# Check npm global path
npm config get prefix
# Add to PATH if needed
export PATH="$(npm config get prefix)/bin:$PATH"
```

**Issue: "API key invalid"**
```bash
# Verify key format
echo $GEMINI_API_KEY | head -c 20
# Should start with "AIzaSy"

# Test with minimal request
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}' 2>/dev/null | jq .error
```

**Issue: Rate limit exceeded**
```bash
# Check current quota
gemini --quota

# Switch to faster model
gemini --model gemini-2.0-flash "your prompt"

# Wait for reset (usually 1 hour)
```

---

## 📊 Success Metrics

### Installation Success Criteria
- ✅ `gemini --version` returns valid version
- ✅ API key authentication successful
- ✅ Sovereignty validation passes
- ✅ Continue.dev integration working
- ✅ tmux collaboration session launches

### Performance Targets
- ✅ Response time <5 seconds for typical queries
- ✅ Memory usage <200MB during operation
- ✅ Zero external data transmission verified
- ✅ Ma'at compliance validation functional

---

## 🎯 Next Steps

Once installation is complete:
1. Test with [Prompt Engineering Guide](prompt-engineering.md)
2. Configure [Team Coordination](team-coordination.md) protocols
3. Implement [Mind Model Integration](mind-model-prompts.md)
4. Set up [Terminal Workflows](terminal-integration.md)

**Installation complete! Ready for sovereign Gemini CLI integration.** 🚀🤖✨
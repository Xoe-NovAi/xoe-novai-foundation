#!/bin/bash
# Wave 4 Phase 3A Setup Script
# Sets up credential storage and daily audit system

set -euo pipefail

echo "🚀 Setting up Wave 4 Phase 3A: Infrastructure"

# Create directories
mkdir -p ~/.config/xnai
mkdir -p ~/.local/share/opencode

# Copy templates
echo "📋 Copying credential templates..."
cp config/templates/opencode-credentials.yaml.template ~/.config/xnai/opencode-credentials.yaml
cp config/templates/opencode-rotation-rules.yaml.template ~/.config/xnai/opencode-rotation-rules.yaml

# Set permissions
echo "🔒 Setting secure permissions..."
chmod 0600 ~/.config/xnai/opencode-credentials.yaml
chmod 0600 ~/.config/xnai/opencode-rotation-rules.yaml

# Make scripts executable
echo "⚙️ Making scripts executable..."
chmod +x scripts/xnai-setup-opencode-providers.sh
chmod +x scripts/xnai-quota-auditor.py

# Install systemd timer
echo "⏰ Installing daily audit timer..."
sudo cp scripts/xnai-quota-audit.{timer,service} /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable xnai-quota-audit.timer
sudo systemctl start xnai-quota-audit.timer

# Verify installation
echo "✅ Verifying installation..."
if [[ -f ~/.config/xnai/opencode-credentials.yaml ]]; then
    echo "✓ Credential template installed"
else
    echo "❌ Credential template missing"
    exit 1
fi

if systemctl is-active --quiet xnai-quota-audit.timer; then
    echo "✓ Daily audit timer active"
else
    echo "❌ Daily audit timer not active"
    exit 1
fi

echo ""
echo "🎉 Phase 3A setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit ~/.config/xnai/opencode-credentials.yaml with actual credentials"
echo "2. Run: ./scripts/xnai-setup-opencode-providers.sh"
echo "3. Test daily audit: ./scripts/xnai-quota-auditor.py"
echo ""
echo "⚠️  SECURITY NOTE: Keep credential files git-ignored and 0600 permissions"
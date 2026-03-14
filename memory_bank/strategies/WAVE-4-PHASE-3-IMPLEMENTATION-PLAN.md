---
title: "Wave 4 Phase 3: Implementation Plan"
subtitle: "From Design to Production-Ready Multi-Account Orchestration"
status: draft
phase: "Wave 4 - Phase 3 Implementation"
created: 2026-02-25
updated: 2026-02-25
owner: "MC-Overseer"
tags: [wave-4, phase-3, implementation, infrastructure, dispatch, raptor]
---

# Wave 4 Phase 3: Implementation Plan

**Coordination Key**: `WAVE-4-PHASE-3-IMPLEMENTATION-2026-02-25`  
**Status**: 🟢 READY FOR IMPLEMENTATION  
**Prerequisites**: Phase 2 designs complete, account audit data needed

---

## Executive Summary

**Phase 3** transforms Phase 2 designs into production-ready implementation across 4 sub-phases:

- **Phase 3A**: Infrastructure (20 hours) - Credential storage, audit system
- **Phase 3B**: Dispatch System (20 hours) - Multi-CLI routing, Agent Bus integration  
- **Phase 3C**: Raptor Integration (8 hours) - Copilot CLI wrapper, quota management
- **Phase 3D**: Testing & Validation (7 hours) - Comprehensive testing suite

**Total Effort**: 55 hours (1 week for 1-person team, 2-3 days for 2-person team)

**Expected Outcome**: Production-ready multi-account provider orchestration with automated quota management, intelligent dispatch, and 400 monthly messages efficiently utilized.

---

## Phase 3A: Infrastructure (20 hours)

### Objective
Build secure credential management and automated account tracking systems.

### Tasks

#### 3A.1: Credential Storage System (8 hours)

**Task 3A.1.1: Create Credential Template**
```bash
# Create template file
mkdir -p config/templates
cat > config/templates/opencode-credentials.yaml.template << 'EOF'
# OpenCode Credentials Template
# Copy to ~/.config/xnai/opencode-credentials.yaml
# Set permissions: chmod 0600 ~/.config/xnai/opencode-credentials.yaml

providers:
  antigravity:
    type: oauth
    accounts:
      - email: "user1@example.com"
        access_token: "ya29.c..." # 1 year validity
        refresh_token: "1//..." # Refresh mechanism
        expires_at: "2027-02-23"
        quota_limit: "unlimited"
        active: true
        
      - email: "user2@example.com"
        access_token: "ya29.d...."
        active: true
        
  openrouter:
    type: api_key
    api_key: "sk-or-v1-..." # Loaded from env var or keyring
    quota_limit: "3.5M tokens/month"
    
  together:
    type: api_key
    api_key_env: "TOGETHER_API_KEY" # Points to env var
    quota_limit: "unlimited"
    
  groq:
    type: api_key
    api_key_env: "GROQ_API_KEY"
    quota_limit: "500K tokens/free"
EOF
```

**Task 3A.1.2: Create Injection Script**
```bash
# Create injection script
cat > scripts/xnai-setup-opencode-providers.sh << 'EOF'
#!/bin/bash
# OpenCode Provider Credential Injection Script
# Usage: ./scripts/xnai-setup-opencode-providers.sh

set -euo pipefail

CREDS_FILE="${HOME}/.config/xnai/opencode-credentials.yaml"
AUTH_FILE="${HOME}/.local/share/opencode/auth.json"
OPENCODE_JSON="$(pwd)/.opencode/opencode.json"

# Function: Load API key from env var or credential file
get_api_key() {
    local provider=$1
    local key_env_var=$2
    
    # Try env var first
    if [[ -n "${!key_env_var}" ]]; then
        echo "${!key_env_var}"
        return 0
    fi
    
    # Fallback to YAML
    yq eval ".providers.$provider.api_key" "$CREDS_FILE"
}

# Function: Inject into auth.json
inject_provider_auth() {
    local provider=$1
    local auth_key=$2
    local auth_value=$3
    
    jq --arg prov "$provider" \
       --arg key "$auth_key" \
       --arg val "$auth_value" \
       '.[$prov][$key] = $val' \
       "$AUTH_FILE" > "$AUTH_FILE.tmp" && mv "$AUTH_FILE.tmp" "$AUTH_FILE"
}

# Function: Rotate accounts
rotate_account() {
    local provider=$1
    local accounts_file=$2
    
    # Get current active account
    current_account=$(yq eval ".providers.$provider.accounts | map(select(.active == true)) | .[0].email" "$accounts_file")
    
    # Find next account
    all_accounts=$(yq eval ".providers.$provider.accounts[].email" "$accounts_file")
    next_account=""
    
    while IFS= read -r account; do
        if [[ "$account" != "$current_account" && -z "$next_account" ]]; then
            next_account="$account"
        fi
    done <<< "$all_accounts"
    
    # If no next account found, use first
    if [[ -z "$next_account" ]]; then
        next_account=$(yq eval ".providers.$provider.accounts[0].email" "$accounts_file")
    fi
    
    echo "$next_account"
}

# Main loop: For each provider in credentials
echo "⚙️  Injecting provider credentials..."

if [[ ! -f "$CREDS_FILE" ]]; then
    echo "❌ Credential file not found: $CREDS_FILE"
    echo "Please copy config/templates/opencode-credentials.yaml.template to $CREDS_FILE"
    exit 1
fi

if [[ ! -f "$AUTH_FILE" ]]; then
    echo "❌ Auth file not found: $AUTH_FILE"
    echo "Please ensure OpenCode is installed and has created auth.json"
    exit 1
fi

yq eval '.providers | keys' "$CREDS_FILE" | while read -r provider; do
    echo "  Processing $provider..."
    
    case "$provider" in
        antigravity)
            # Load first active account
            access_token=$(yq eval '.providers.antigravity.accounts[0].access_token' "$CREDS_FILE")
            inject_provider_auth "google" "accessToken" "$access_token"
            echo "    ✓ Antigravity (${access_token:0:10}...)"
            ;;
        openrouter)
            api_key=$(get_api_key "openrouter" "OPENROUTER_API_KEY")
            inject_provider_auth "openrouter" "apiKey" "$api_key"
            echo "    ✓ OpenRouter"
            ;;
        together)
            api_key=$(get_api_key "together" "TOGETHER_API_KEY")
            inject_provider_auth "together" "apiKey" "$api_key"
            echo "    ✓ Together.ai"
            ;;
        groq)
            api_key=$(get_api_key "groq" "GROQ_API_KEY")
            inject_provider_auth "groq" "apiKey" "$api_key"
            echo "    ✓ Groq"
            ;;
    esac
done

echo "✅ Provider injection complete!"
echo "Run: opencode --model google/antigravity-gemini-3-pro to test"
EOF

chmod +x scripts/xnai-setup-opencode-providers.sh
```

**Task 3A.1.3: Create Rotation Rules Template**
```bash
# Create rotation rules template
cat > config/templates/opencode-rotation-rules.yaml.template << 'EOF'
# OpenCode Account Rotation Rules
# Copy to ~/.config/xnai/opencode-rotation-rules.yaml

rotation:
  enable: true
  strategy: "round-robin" # or "least-used" or "quota-aware"
  
  antigravity:
    accounts:
      - email: "user1@example.com"
        quota_used: 45000
        quota_total: 100000
        last_used: "2026-02-23T14:00:00Z"
        
      - email: "user2@example.com"
        quota_used: 12000
        quota_total: 100000
        last_used: "2026-02-23T12:30:00Z"
        
      - email: "user3@example.com"
        quota_used: 98000 # Nearly full
        quota_total: 100000
        last_used: "2026-02-22T08:00:00Z"
        
    next_to_use: "user2@example.com"
    rotation_interval: "72h" # Rotate accounts every 3 days
    
  openrouter:
    quota_used: 2500000
    quota_total: 3500000
    percentage_used: 71%
EOF
```

#### 3A.2: Daily Audit System (12 hours)

**Task 3A.2.1: Create Audit Data Collector**
```python
# Create audit data collector
cat > scripts/xnai-quota-auditor.py << 'EOF'
#!/usr/bin/env python3
"""
OpenCode Quota Auditor
Automated daily audit of all provider accounts and quota usage.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import yaml

# Add app to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.XNAi_rag_app.core.token_validation import TokenValidator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/xnai-quota-auditor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class QuotaAuditor:
    def __init__(self):
        self.creds_file = Path.home() / ".config" / "xnai" / "opencode-credentials.yaml"
        self.auth_file = Path.home() / ".local" / "share" / "opencode" / "auth.json"
        self.registry_file = Path("memory_bank") / "ACCOUNT-REGISTRY.yaml"
        self.validator = TokenValidator()
        
    async def audit_all_providers(self) -> Dict[str, Any]:
        """Audit all configured providers and return comprehensive report."""
        logger.info("Starting comprehensive quota audit")
        
        audit_report = {
            "audit_date": datetime.now().isoformat(),
            "audit_time": datetime.now().strftime("%H:%M:%S UTC"),
            "providers": {},
            "summary": {
                "total_accounts": 0,
                "healthy_accounts": 0,
                "warning_accounts": 0,
                "critical_accounts": 0,
                "total_quota_used": 0,
                "total_quota_available": 0
            },
            "alerts": [],
            "recommendations": []
        }
        
        # Audit each provider
        providers_to_audit = ["antigravity", "openrouter", "together", "groq"]
        
        for provider in providers_to_audit:
            try:
                provider_data = await self.audit_provider(provider)
                if provider_data:
                    audit_report["providers"][provider] = provider_data
                    logger.info(f"✓ {provider} audit completed")
                else:
                    logger.warning(f"⚠️ {provider} audit returned no data")
            except Exception as e:
                logger.error(f"❌ {provider} audit failed: {e}")
                audit_report["alerts"].append({
                    "severity": "critical",
                    "provider": provider,
                    "message": f"Audit failed: {str(e)}",
                    "action_required": "Manual investigation needed"
                })
        
        # Generate summary and recommendations
        self._generate_summary(audit_report)
        self._generate_recommendations(audit_report)
        
        # Save audit report
        await self._save_audit_report(audit_report)
        
        logger.info("Quota audit completed successfully")
        return audit_report
    
    async def audit_provider(self, provider: str) -> Optional[Dict[str, Any]]:
        """Audit a specific provider."""
        logger.info(f"Auditing {provider}...")
        
        if provider == "antigravity":
            return await self._audit_antigravity()
        elif provider == "openrouter":
            return await self._audit_openrouter()
        elif provider == "together":
            return await self._audit_together()
        elif provider == "groq":
            return await self._audit_groq()
        else:
            logger.warning(f"Unknown provider: {provider}")
            return None
    
    async def _audit_antigravity(self) -> Dict[str, Any]:
        """Audit Antigravity accounts."""
        provider_data = {
            "provider": "antigravity",
            "accounts": {},
            "total_quota_used": 0,
            "total_quota_available": 0,
            "status": "unknown"
        }
        
        # Load credentials
        if not self.creds_file.exists():
            logger.warning("Antigravity credentials file not found")
            return provider_data
        
        with open(self.creds_file, 'r') as f:
            creds = yaml.safe_load(f)
        
        accounts = creds.get("providers", {}).get("antigravity", {}).get("accounts", [])
        
        for i, account in enumerate(accounts):
            account_id = f"antigravity_user_{i+1}"
            account_data = {
                "email": account.get("email", f"unknown_{i+1}@example.com"),
                "status": "unknown",
                "quota_used": account.get("quota_used", 0),
                "quota_total": account.get("quota_total", 100000),  # Default estimate
                "quota_used_percent": 0,
                "last_used": account.get("last_used", None),
                "health_status": "unknown"
            }
            
            # Calculate health status
            used_percent = (account_data["quota_used"] / account_data["quota_total"]) * 100
            account_data["quota_used_percent"] = used_percent
            
            if used_percent < 50:
                account_data["health_status"] = "green"
                provider_data["summary"]["healthy_accounts"] += 1
            elif used_percent < 80:
                account_data["health_status"] = "yellow"
                provider_data["summary"]["warning_accounts"] += 1
            else:
                account_data["health_status"] = "red"
                provider_data["summary"]["critical_accounts"] += 1
            
            provider_data["accounts"][account_id] = account_data
            provider_data["total_quota_used"] += account_data["quota_used"]
            provider_data["total_quota_available"] += account_data["quota_total"]
        
        # Determine overall status
        critical_count = provider_data["summary"]["critical_accounts"]
        warning_count = provider_data["summary"]["warning_accounts"]
        
        if critical_count > 0:
            provider_data["status"] = "critical"
        elif warning_count > 0:
            provider_data["status"] = "warning"
        else:
            provider_data["status"] = "healthy"
        
        return provider_data
    
    async def _audit_openrouter(self) -> Dict[str, Any]:
        """Audit OpenRouter account."""
        # For API key providers, we can't easily get quota without making API calls
        # This would require actual API requests which we want to avoid in audit
        return {
            "provider": "openrouter",
            "status": "healthy",
            "quota_used": 0,  # Would need API call to get actual usage
            "quota_total": 3500000,
            "quota_used_percent": 0,
            "notes": "API key provider - quota tracking requires API calls"
        }
    
    async def _audit_together(self) -> Dict[str, Any]:
        """Audit Together.ai account."""
        return {
            "provider": "together",
            "status": "healthy",
            "quota_used": 0,
            "quota_total": 0,  # Unlimited
            "quota_used_percent": 0,
            "notes": "API key provider - unlimited quota"
        }
    
    async def _audit_groq(self) -> Dict[str, Any]:
        """Audit Groq account."""
        return {
            "provider": "groq",
            "status": "healthy",
            "quota_used": 0,
            "quota_total": 500000,
            "quota_used_percent": 0,
            "notes": "API key provider - free tier quota"
        }
    
    def _generate_summary(self, audit_report: Dict[str, Any]):
        """Generate audit summary."""
        total_accounts = 0
        healthy = 0
        warning = 0
        critical = 0
        total_used = 0
        total_available = 0
        
        for provider_data in audit_report["providers"].values():
            if "accounts" in provider_data:
                for account_data in provider_data["accounts"].values():
                    total_accounts += 1
                    if account_data["health_status"] == "green":
                        healthy += 1
                    elif account_data["health_status"] == "yellow":
                        warning += 1
                    elif account_data["health_status"] == "red":
                        critical += 1
                    total_used += account_data["quota_used"]
                    total_available += account_data["quota_total"]
            else:
                # Single account provider
                total_accounts += 1
                if provider_data["status"] == "healthy":
                    healthy += 1
                elif provider_data["status"] == "warning":
                    warning += 1
                elif provider_data["status"] == "critical":
                    critical += 1
        
        audit_report["summary"] = {
            "total_accounts": total_accounts,
            "healthy_accounts": healthy,
            "warning_accounts": warning,
            "critical_accounts": critical,
            "total_quota_used": total_used,
            "total_quota_available": total_available,
            "overall_health": "healthy" if critical == 0 and warning == 0 else "warning" if critical == 0 else "critical"
        }
    
    def _generate_recommendations(self, audit_report: Dict[str, Any]):
        """Generate actionable recommendations."""
        recommendations = []
        
        # Check for critical accounts
        for provider, provider_data in audit_report["providers"].items():
            if "accounts" in provider_data:
                for account_id, account_data in provider_data["accounts"].items():
                    if account_data["health_status"] == "red":
                        recommendations.append({
                            "priority": "high",
                            "action": f"Rotate {account_id} - quota exhausted",
                            "rationale": f"{account_data['quota_used_percent']:.1f}% quota used",
                            "impact": "Prevent service interruption"
                        })
                    elif account_data["health_status"] == "yellow":
                        recommendations.append({
                            "priority": "medium",
                            "action": f"Monitor {account_id} - approaching quota limit",
                            "rationale": f"{account_data['quota_used_percent']:.1f}% quota used",
                            "impact": "Plan rotation before exhaustion"
                        })
        
        # Check overall capacity
        summary = audit_report["summary"]
        if summary["critical_accounts"] > 0:
            recommendations.append({
                "priority": "high",
                "action": "Implement emergency rotation for critical accounts",
                "rationale": f"{summary['critical_accounts']} accounts at quota limit",
                "impact": "Maintain service availability"
            })
        
        if summary["warning_accounts"] > 3:
            recommendations.append({
                "priority": "medium",
                "action": "Review usage patterns and consider additional accounts",
                "rationale": f"{summary['warning_accounts']} accounts approaching limits",
                "impact": "Improve capacity planning"
            })
        
        audit_report["recommendations"] = recommendations
    
    async def _save_audit_report(self, audit_report: Dict[str, Any]):
        """Save audit report to file."""
        audit_dir = Path("memory_bank")
        audit_dir.mkdir(exist_ok=True)
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        audit_file = audit_dir / f"ACCOUNT-TRACKING-{date_str}.yaml"
        
        # Convert to YAML for better readability
        import yaml
        with open(audit_file, 'w') as f:
            yaml.dump(audit_report, f, default_flow_style=False, indent=2)
        
        logger.info(f"Audit report saved to {audit_file}")
        
        # Also save JSON version for programmatic access
        json_file = audit_dir / f"ACCOUNT-TRACKING-{date_str}.json"
        with open(json_file, 'w') as f:
            json.dump(audit_report, f, indent=2)
        
        logger.info(f"JSON report saved to {json_file}")

async def main():
    """Main audit execution."""
    auditor = QuotaAuditor()
    
    try:
        audit_report = await auditor.audit_all_providers()
        
        # Print summary
        summary = audit_report["summary"]
        print(f"\n=== QUOTA AUDIT SUMMARY ===")
        print(f"Total Accounts: {summary['total_accounts']}")
        print(f"Healthy: {summary['healthy_accounts']}")
        print(f"Warning: {summary['warning_accounts']}")
        print(f"Critical: {summary['critical_accounts']}")
        print(f"Overall Health: {summary['overall_health']}")
        
        if audit_report["alerts"]:
            print(f"\n=== ALERTS ===")
            for alert in audit_report["alerts"]:
                print(f"⚠️ {alert['severity'].upper()}: {alert['message']}")
        
        if audit_report["recommendations"]:
            print(f"\n=== RECOMMENDATIONS ===")
            for rec in audit_report["recommendations"]:
                print(f"🎯 {rec['priority'].upper()}: {rec['action']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Audit failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
EOF

chmod +x scripts/xnai-quota-auditor.py
```

**Task 3A.2.2: Create Systemd Timer**
```bash
# Create systemd timer for daily audit
cat > scripts/xnai-quota-audit.timer << 'EOF'
[Unit]
Description=Daily OpenCode Quota Audit
Requires=xnai-quota-audit.service

[Timer]
OnCalendar=daily
Persistent=true
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
EOF

cat > scripts/xnai-quota-audit.service << 'EOF'
[Unit]
Description=OpenCode Quota Audit Service
After=network.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=/home/$USER/Documents/xnai-foundation
ExecStart=/usr/bin/python3 /home/$USER/Documents/xnai-foundation/scripts/xnai-quota-auditor.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

**Task 3A.2.3: Create Setup Script**
```bash
# Create complete setup script
cat > scripts/setup-wave4-phase3a.sh << 'EOF'
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
EOF

chmod +x scripts/setup-wave4-phase3a.sh
```

### Implementation Status: Phase 3A

- [x] Credential storage system design
- [x] Injection script implementation
- [x] Rotation rules template
- [x] Daily audit system design
- [x] Audit data collector implementation
- [x] Systemd timer setup
- [x] Complete setup script
- [ ] User credential configuration
- [ ] Testing and validation

---

## Phase 3B: Dispatch System (20 hours)

### Objective
Build intelligent task routing system that selects optimal CLI based on task type, context requirements, and account availability.

### Tasks

#### 3B.1: Core Dispatcher Implementation (12 hours)

**Task 3B.1.1: Create MultiProviderDispatcher Class**
```python
# Create multi-provider dispatcher
cat > app/XNAi_rag_app/core/multi_provider_dispatcher.py << 'EOF'
#!/usr/bin/env python3
"""
Multi-Provider Dispatcher
Intelligent task routing across OpenCode, Copilot, Cline, and Local providers.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml
import json

from app.XNAi_rag_app.core.token_validation import TokenValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiProviderDispatcher:
    """Intelligent task dispatcher for multi-provider orchestration."""
    
    def __init__(self, registry_file: str = "memory_bank/ACCOUNT-REGISTRY.yaml"):
        self.registry_file = Path(registry_file)
        self.validator = TokenValidator()
        self.call_history = []
        self.statistics = {
            "total_dispatches": 0,
            "success_rate": 0.0,
            "avg_response_time": 0.0,
            "provider_usage": {},
            "fallback_triggers": 0
        }
        
        # Provider capabilities
        self.provider_capabilities = {
            "opencode": {
                "context_window": 1000000,  # 1M tokens
                "speed": 800,  # ms
                "best_for": ["reasoning", "large_docs", "analysis"],
                "models": ["gemini-3-pro", "claude-opus-4.6-thinking", "gemini-3-flash"]
            },
            "copilot": {
                "context_window": 264000,  # 264K tokens
                "speed": 200,  # ms
                "best_for": ["code_analysis", "refactoring", "agent_mode"],
                "models": ["raptor-mini", "claude-haiku-4.5", "gpt-4-preview"]
            },
            "cline": {
                "context_window": 200000,  # 200K tokens
                "speed": 1000,  # ms
                "best_for": ["file_operations", "refactoring", "ide_integration"],
                "models": ["sonnet-4.5", "opus-4.6", "opus-4.6-thinking"]
            },
            "local": {
                "context_window": 4000,  # 4K tokens
                "speed": 2000,  # ms
                "best_for": ["sovereign", "sensitive", "offline"],
                "models": ["llama-2-7b", "llama-2-13b", "codellama-34b"]
            }
        }
        
        # Load account registry
        self.account_registry = self._load_account_registry()
    
    def _load_account_registry(self) -> Dict[str, Any]:
        """Load account registry from YAML file."""
        if not self.registry_file.exists():
            logger.warning(f"Account registry not found: {self.registry_file}")
            return {}
        
        with open(self.registry_file, 'r') as f:
            return yaml.safe_load(f)
    
    async def dispatch_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch task to optimal provider.
        
        Args:
            task: Task dictionary with 'type', 'context_size', 'priority', 'content'
        
        Returns:
            Dispatch result with selected provider and account
        """
        start_time = time.time()
        self.statistics["total_dispatches"] += 1
        
        try:
            # 1. Classify task
            task_type = self._classify_task(task)
            logger.info(f"Classifying task: {task_type}")
            
            # 2. Get candidate providers
            candidates = self._get_candidates(task_type, task.get("context_size", 0))
            logger.info(f"Candidate providers: {candidates}")
            
            # 3. Score candidates
            scored_candidates = []
            for provider in candidates:
                score = self._calculate_score(provider, task)
                scored_candidates.append((provider, score))
            
            # 4. Select best candidate
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            best_provider = scored_candidates[0][0] if scored_candidates else "local"
            
            # 5. Select account
            selected_account = self._select_account(best_provider)
            
            # 6. Validate selection
            if not await self._validate_provider(best_provider, selected_account):
                logger.warning(f"Provider validation failed: {best_provider}")
                # Fallback to next best
                for provider, _ in scored_candidates[1:]:
                    if await self._validate_provider(provider, self._select_account(provider)):
                        best_provider = provider
                        selected_account = self._select_account(provider)
                        self.statistics["fallback_triggers"] += 1
                        break
                else:
                    # Ultimate fallback to local
                    best_provider = "local"
                    selected_account = 0
                    self.statistics["fallback_triggers"] += 1
            
            # 7. Execute task
            result = await self._execute_task(best_provider, selected_account, task)
            
            # 8. Update statistics
            response_time = time.time() - start_time
            self._update_statistics(best_provider, response_time, True)
            
            # 9. Log dispatch
            dispatch_log = {
                "timestamp": datetime.now().isoformat(),
                "task_type": task_type,
                "selected_provider": best_provider,
                "selected_account": selected_account,
                "response_time": response_time,
                "success": True
            }
            self.call_history.append(dispatch_log)
            
            return {
                "provider": best_provider,
                "account": selected_account,
                "response_time": response_time,
                "success": True,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Dispatch failed: {e}")
            self._update_statistics("error", time.time() - start_time, False)
            return {
                "provider": "error",
                "account": None,
                "response_time": time.time() - start_time,
                "success": False,
                "error": str(e)
            }
    
    def _classify_task(self, task: Dict[str, Any]) -> str:
        """Classify task by type."""
        content = task.get("content", "").lower()
        task_type = task.get("type", "general")
        
        # Content-based classification
        if any(keyword in content for keyword in ["refactor", "code", "function", "class"]):
            return "code_analysis"
        elif any(keyword in content for keyword in ["reasoning", "explain", "why", "how"]):
            return "reasoning"
        elif any(keyword in content for keyword in ["file", "write", "create", "modify"]):
            return "file_operations"
        elif any(keyword in content for keyword in ["sensitive", "private", "confidential"]):
            return "sovereign"
        elif any(keyword in content for keyword in ["agent", "orchestrate", "coordinate"]):
            return "agent_mode"
        else:
            return task_type
    
    def _get_candidates(self, task_type: str, context_size: int) -> List[str]:
        """Get candidate providers for task type."""
        candidates = []
        
        for provider, capabilities in self.provider_capabilities.items():
            # Check context fit
            if context_size <= capabilities["context_window"] * 0.8:  # 80% utilization
                # Check task type fit
                if task_type in capabilities["best_for"]:
                    candidates.append(provider)
        
        # If no candidates found, use all providers
        if not candidates:
            candidates = list(self.provider_capabilities.keys())
        
        return candidates
    
    def _calculate_score(self, provider: str, task: Dict[str, Any]) -> float:
        """Calculate composite score for provider selection."""
        capabilities = self.provider_capabilities[provider]
        
        # 1. Context fit score (0-100)
        context_size = task.get("context_size", 0)
        context_fit = max(0, 100 - (context_size / capabilities["context_window"] * 100))
        
        # 2. Task type fit score (0-100)
        task_type = self._classify_task(task)
        task_fit = 100 if task_type in capabilities["best_for"] else 50
        
        # 3. Latency score (0-100, lower is better)
        latency_score = max(0, 100 - (capabilities["speed"] / 10))  # Normalize to 0-100
        
        # 4. Availability score (0-100)
        availability_score = self._get_availability_score(provider)
        
        # 5. Historical performance score (0-100)
        performance_score = self._get_performance_score(provider)
        
        # Weighted composite score
        weights = {
            "context": 0.30,
            "task": 0.30,
            "latency": 0.20,
            "availability": 0.10,
            "performance": 0.10
        }
        
        composite_score = (
            context_fit * weights["context"] +
            task_fit * weights["task"] +
            latency_score * weights["latency"] +
            availability_score * weights["availability"] +
            performance_score * weights["performance"]
        )
        
        logger.debug(f"Score breakdown for {provider}: "
                    f"context={context_fit:.1f}, task={task_fit:.1f}, "
                    f"latency={latency_score:.1f}, availability={availability_score:.1f}, "
                    f"performance={performance_score:.1f} = {composite_score:.1f}")
        
        return composite_score
    
    def _get_availability_score(self, provider: str) -> float:
        """Get availability score based on account health."""
        if provider not in self.account_registry:
            return 50.0
        
        registry = self.account_registry[provider]
        healthy_accounts = 0
        total_accounts = 0
        
        if "account_list" in registry:
            for account in registry["account_list"]:
                total_accounts += 1
                if account.get("status", "active") == "active":
                    quota_used = account.get("quota", {}).get("used", 0)
                    quota_total = account.get("quota", {}).get("limit", 100)
                    if quota_used / quota_total < 0.8:  # Less than 80% used
                        healthy_accounts += 1
        
        if total_accounts == 0:
            return 50.0
        
        return (healthy_accounts / total_accounts) * 100
    
    def _get_performance_score(self, provider: str) -> float:
        """Get historical performance score."""
        if provider not in self.statistics["provider_usage"]:
            return 80.0  # Default score
        
        usage = self.statistics["provider_usage"][provider]
        success_rate = usage.get("success_rate", 0.8)
        avg_response_time = usage.get("avg_response_time", 1000)
        
        # Convert to 0-100 scale
        success_score = success_rate * 100
        latency_score = max(0, 100 - (avg_response_time / 10))
        
        return (success_score * 0.7) + (latency_score * 0.3)
    
    def _select_account(self, provider: str) -> int:
        """Select account for provider based on rotation strategy."""
        if provider == "local":
            return 0
        
        # For multi-account providers, use round-robin
        if provider in ["opencode", "copilot"]:
            # Get last used account and rotate
            last_used = self._get_last_used_account(provider)
            total_accounts = self._get_total_accounts(provider)
            return (last_used + 1) % total_accounts
        
        return 0
    
    def _get_last_used_account(self, provider: str) -> int:
        """Get last used account index for provider."""
        for log in reversed(self.call_history):
            if log["selected_provider"] == provider:
                return log["selected_account"]
        return 0
    
    def _get_total_accounts(self, provider: str) -> int:
        """Get total accounts for provider."""
        if provider not in self.account_registry:
            return 1
        
        registry = self.account_registry[provider]
        if "account_list" in registry:
            return len(registry["account_list"])
        return 1
    
    async def _validate_provider(self, provider: str, account: int) -> bool:
        """Validate provider and account availability."""
        try:
            if provider == "opencode":
                # Check if OpenCode is available
                result = await self._test_opencode_connection(account)
                return result
            elif provider == "copilot":
                # Check if Copilot is available
                result = await self._test_copilot_connection(account)
                return result
            elif provider == "cline":
                # Check if Cline is available
                result = await self._test_cline_connection()
                return result
            elif provider == "local":
                # Check if local model is available
                result = await self._test_local_connection()
                return result
            return False
        except Exception as e:
            logger.error(f"Provider validation failed: {provider} - {e}")
            return False
    
    async def _test_opencode_connection(self, account: int) -> bool:
        """Test OpenCode connection."""
        # Simple test - check if auth file exists and has valid structure
        auth_file = Path.home() / ".local" / "share" / "opencode" / "auth.json"
        if not auth_file.exists():
            return False
        
        try:
            with open(auth_file, 'r') as f:
                auth_data = json.load(f)
            
            # Check if Google auth is present (Antigravity)
            if "google" in auth_data and "accessToken" in auth_data["google"]:
                return True
        except Exception:
            pass
        
        return False
    
    async def _test_copilot_connection(self, account: int) -> bool:
        """Test Copilot connection."""
        try:
            # Test gh copilot status
            result = await asyncio.create_subprocess_exec(
                "gh", "copilot", "status",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            return result.returncode == 0 and b"enabled" in stdout
        except Exception:
            return False
    
    async def _test_cline_connection(self) -> bool:
        """Test Cline connection."""
        try:
            # Test cline status
            result = await asyncio.create_subprocess_exec(
                "cline", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            return result.returncode == 0
        except Exception:
            return False
    
    async def _test_local_connection(self) -> bool:
        """Test local model connection."""
        try:
            # Test local model endpoint
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8080/health") as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def _execute_task(self, provider: str, account: int, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with selected provider."""
        # This would integrate with actual CLI commands
        # For now, return mock result
        return {
            "provider": provider,
            "account": account,
            "task_type": self._classify_task(task),
            "content": task.get("content", ""),
            "status": "executed",
            "timestamp": datetime.now().isoformat()
        }
    
    def _update_statistics(self, provider: str, response_time: float, success: bool):
        """Update dispatch statistics."""
        if provider not in self.statistics["provider_usage"]:
            self.statistics["provider_usage"][provider] = {
                "calls": 0,
                "successes": 0,
                "total_response_time": 0,
                "success_rate": 0.0,
                "avg_response_time": 0.0
            }
        
        usage = self.statistics["provider_usage"][provider]
        usage["calls"] += 1
        if success:
            usage["successes"] += 1
        
        usage["total_response_time"] += response_time
        usage["success_rate"] = usage["successes"] / usage["calls"]
        usage["avg_response_time"] = usage["total_response_time"] / usage["calls"]
        
        # Update overall statistics
        total_calls = sum(u["calls"] for u in self.statistics["provider_usage"].values())
        total_successes = sum(u["successes"] for u in self.statistics["provider_usage"].values())
        total_response_time = sum(u["total_response_time"] for u in self.statistics["provider_usage"].values())
        
        self.statistics["success_rate"] = total_successes / total_calls if total_calls > 0 else 0.0
        self.statistics["avg_response_time"] = total_response_time / total_calls if total_calls > 0 else 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dispatch statistics."""
        return {
            "total_dispatches": self.statistics["total_dispatches"],
            "success_rate": self.statistics["success_rate"],
            "avg_response_time": self.statistics["avg_response_time"],
            "fallback_triggers": self.statistics["fallback_triggers"],
            "provider_usage": self.statistics["provider_usage"],
            "recent_calls": self.call_history[-10:]  # Last 10 calls
        }
    
    def save_statistics(self, file_path: str):
        """Save statistics to file."""
        stats_file = Path(file_path)
        with open(stats_file, 'w') as f:
            json.dump(self.get_statistics(), f, indent=2)
        logger.info(f"Statistics saved to {stats_file}")

# Singleton instance
dispatcher = MultiProviderDispatcher()
EOF
```

**Task 3B.1.2: Create CLI Interface**
```python
# Create CLI interface for dispatcher
cat > scripts/xnai-dispatch-cli.py << 'EOF'
#!/usr/bin/env python3
"""
OpenCode Multi-Provider Dispatch CLI
Command-line interface for testing and using the multi-provider dispatcher.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.XNAi_rag_app.core.multi_provider_dispatcher import dispatcher

async def main():
    parser = argparse.ArgumentParser(description="OpenCode Multi-Provider Dispatcher CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Dispatch command
    dispatch_parser = subparsers.add_parser("dispatch", help="Dispatch a task")
    dispatch_parser.add_argument("--type", choices=["code_analysis", "reasoning", "file_operations", "sovereign", "agent_mode", "general"], 
                                default="general", help="Task type")
    dispatch_parser.add_argument("--content", required=True, help="Task content")
    dispatch_parser.add_argument("--context-size", type=int, default=0, help="Estimated context size in tokens")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show dispatcher status")
    
    # Statistics command
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.add_argument("--save", help="Save statistics to file")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test provider connections")
    test_parser.add_argument("--provider", choices=["opencode", "copilot", "cline", "local"], 
                           help="Test specific provider")
    
    args = parser.parse_args()
    
    if args.command == "dispatch":
        task = {
            "type": args.type,
            "content": args.content,
            "context_size": args.context_size
        }
        
        print(f"Dispatching task: {args.type}")
        print(f"Content: {args.content[:100]}...")
        
        result = await dispatcher.dispatch_task(task)
        
        print(f"\nDispatch Result:")
        print(f"Provider: {result['provider']}")
        print(f"Account: {result['account']}")
        print(f"Response Time: {result['response_time']:.2f}s")
        print(f"Success: {result['success']}")
        
        if not result['success']:
            print(f"Error: {result['error']}")
    
    elif args.command == "status":
        stats = dispatcher.get_statistics()
        print(f"Dispatcher Status:")
        print(f"Total Dispatches: {stats['total_dispatches']}")
        print(f"Success Rate: {stats['success_rate']:.2%}")
        print(f"Avg Response Time: {stats['avg_response_time']:.2f}s")
        print(f"Fallback Triggers: {stats['fallback_triggers']}")
        
        print(f"\nProvider Usage:")
        for provider, usage in stats['provider_usage'].items():
            print(f"  {provider}: {usage['calls']} calls, {usage['success_rate']:.2%} success, {usage['avg_response_time']:.2f}s avg")
    
    elif args.command == "stats":
        stats = dispatcher.get_statistics()
        print(json.dumps(stats, indent=2))
        
        if args.save:
            dispatcher.save_statistics(args.save)
            print(f"Statistics saved to {args.save}")
    
    elif args.command == "test":
        if args.provider:
            providers = [args.provider]
        else:
            providers = ["opencode", "copilot", "cline", "local"]
        
        for provider in providers:
            print(f"Testing {provider}...")
            
            # Test account selection
            account = dispatcher._select_account(provider)
            print(f"  Selected account: {account}")
            
            # Test validation
            is_valid = await dispatcher._validate_provider(provider, account)
            print(f"  Validation: {'✓' if is_valid else '✗'}")
            
            # Test scoring
            test_task = {"type": "general", "content": "test", "context_size": 1000}
            score = dispatcher._calculate_score(provider, test_task)
            print(f"  Score: {score:.1f}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
EOF

chmod +x scripts/xnai-dispatch-cli.py
```

#### 3B.2: Agent Bus Integration (8 hours)

**Task 3B.2.1: Create MCP Server Integration**
```python
# Create MCP server for dispatcher
cat > app/XNAi_rag_app/mcp/dispatcher_server.py << 'EOF'
#!/usr/bin/env python3
"""
Dispatcher MCP Server
MCP server that exposes the multi-provider dispatcher as an MCP service.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
import aiohttp
from aiohttp import web

from app.XNAi_rag_app.core.multi_provider_dispatcher import dispatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DispatcherMCPServer:
    """MCP server for multi-provider dispatch."""
    
    def __init__(self, host: str = "localhost", port: int = 8081):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup MCP server routes."""
        self.app.router.add_post("/mcp/dispatch", self.handle_dispatch)
        self.app.router.add_get("/mcp/status", self.handle_status)
        self.app.router.add_get("/mcp/stats", self.handle_stats)
        self.app.router.add_post("/mcp/test", self.handle_test)
    
    async def handle_dispatch(self, request):
        """Handle dispatch requests."""
        try:
            data = await request.json()
            
            task = {
                "type": data.get("type", "general"),
                "content": data.get("content", ""),
                "context_size": data.get("context_size", 0)
            }
            
            result = await dispatcher.dispatch_task(task)
            
            return web.json_response({
                "success": True,
                "result": result
            })
            
        except Exception as e:
            logger.error(f"Dispatch failed: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def handle_status(self, request):
        """Handle status requests."""
        stats = dispatcher.get_statistics()
        return web.json_response(stats)
    
    async def handle_stats(self, request):
        """Handle stats requests."""
        stats = dispatcher.get_statistics()
        return web.json_response(stats)
    
    async def handle_test(self, request):
        """Handle test requests."""
        try:
            data = await request.json()
            provider = data.get("provider", "all")
            
            if provider == "all":
                providers = ["opencode", "copilot", "cline", "local"]
            else:
                providers = [provider]
            
            results = {}
            for prov in providers:
                account = dispatcher._select_account(prov)
                is_valid = await dispatcher._validate_provider(prov, account)
                results[prov] = {
                    "account": account,
                    "valid": is_valid,
                    "score": dispatcher._calculate_score(prov, {"type": "general", "content": "test", "context_size": 1000})
                }
            
            return web.json_response({
                "success": True,
                "results": results
            })
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def start(self):
        """Start the MCP server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"Dispatcher MCP server started on {self.host}:{self.port}")
        
        # Keep server running
        while True:
            await asyncio.sleep(1)

async def main():
    """Main server entry point."""
    server = DispatcherMCPServer()
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
EOF
```

**Task 3B.2.2: Create Agent Bus Integration**
```python
# Create Agent Bus integration
cat > app/XNAi_rag_app/core/agent_bus_integration.py << 'EOF'
#!/usr/bin/env python3
"""
Agent Bus Integration
Integration between multi-provider dispatcher and Agent Bus.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
import redis.asyncio as redis

from app.XNAi_rag_app.core.multi_provider_dispatcher import dispatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentBusDispatcher:
    """Integration between dispatcher and Agent Bus."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.task_stream = "xnai:agent_bus"
        self.group_name = "dispatcher_group"
        self.consumer_name = "dispatcher_consumer"
    
    async def connect(self):
        """Connect to Redis and setup stream."""
        self.redis_client = redis.from_url(self.redis_url)
        
        # Create consumer group if it doesn't exist
        try:
            await self.redis_client.xgroup_create(
                self.task_stream, 
                self.group_name, 
                id="0", 
                mkstream=True
            )
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
        
        logger.info("Agent Bus dispatcher connected")
    
    async def start_listening(self):
        """Start listening for tasks from Agent Bus."""
        logger.info("Starting Agent Bus dispatcher listener")
        
        while True:
            try:
                # Read from stream
                messages = await self.redis_client.xreadgroup(
                    self.group_name,
                    self.consumer_name,
                    {self.task_stream: ">"},
                    count=1,
                    block=1000
                )
                
                for stream, msgs in messages:
                    for msg_id, fields in msgs:
                        await self.process_task(msg_id, fields)
                        
            except Exception as e:
                logger.error(f"Error processing task: {e}")
                await asyncio.sleep(1)
    
    async def process_task(self, msg_id: str, fields: Dict[str, Any]):
        """Process a task from Agent Bus."""
        try:
            # Parse task
            task_data = json.loads(fields[b"task"].decode())
            
            logger.info(f"Processing task: {task_data.get('type', 'unknown')}")
            
            # Dispatch task
            result = await dispatcher.dispatch_task(task_data)
            
            # Send result back to Agent Bus
            result_data = {
                "task_id": task_data.get("task_id"),
                "result": result,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await self.redis_client.xadd(
                f"{self.task_stream}:results",
                {"result": json.dumps(result_data)}
            )
            
            # Acknowledge message
            await self.redis_client.xack(self.task_stream, self.group_name, msg_id)
            
            logger.info(f"Task completed: {result.get('success', False)}")
            
        except Exception as e:
            logger.error(f"Task processing failed: {e}")
            
            # Send error result
            error_result = {
                "task_id": fields.get(b"task_id", b"unknown").decode(),
                "result": {"success": False, "error": str(e)},
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await self.redis_client.xadd(
                f"{self.task_stream}:results",
                {"result": json.dumps(error_result)}
            )
    
    async def send_task(self, task: Dict[str, Any]) -> str:
        """Send task to Agent Bus."""
        task_id = f"task_{asyncio.get_event_loop().time()}"
        
        task_data = {
            "task_id": task_id,
            "task": task,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        msg_id = await self.redis_client.xadd(
            self.task_stream,
            {"task": json.dumps(task_data)}
        )
        
        logger.info(f"Task sent to Agent Bus: {task_id}")
        return task_id
    
    async def get_result(self, task_id: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """Get result for a task."""
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            # Check result stream
            messages = await self.redis_client.xread(
                {f"{self.task_stream}:results": "0"},
                count=100,
                block=100
            )
            
            for stream, msgs in messages:
                for msg_id, fields in msgs:
                    result_data = json.loads(fields[b"result"].decode())
                    if result_data.get("task_id") == task_id:
                        return result_data.get("result")
            
            await asyncio.sleep(0.1)
        
        return None

# Global instance
agent_bus_dispatcher = AgentBusDispatcher()

async def main():
    """Main entry point for Agent Bus dispatcher."""
    await agent_bus_dispatcher.connect()
    await agent_bus_dispatcher.start_listening()

if __name__ == "__main__":
    asyncio.run(main())
EOF
```

### Implementation Status: Phase 3B

- [x] MultiProviderDispatcher class design
- [x] Task classification and scoring algorithms
- [x] Account selection and rotation logic
- [x] Provider validation and fallback mechanisms
- [x] CLI interface implementation
- [x] MCP server integration design
- [x] Agent Bus integration design
- [ ] Full integration testing
- [ ] Performance optimization
- [ ] Documentation and guides

---

## Phase 3C: Raptor Integration (8 hours)

### Objective
Integrate Raptor Mini via Copilot CLI for optimal code analysis tasks.

### Tasks

#### 3C.1: Copilot CLI Wrapper (4 hours)

**Task 3C.1.1: Create Copilot CLI Wrapper**
```python
# Create Copilot CLI wrapper
cat > scripts/xnai-copilot-wrapper.py << 'EOF'
#!/usr/bin/env python3
"""
Copilot CLI Wrapper
Wrapper for gh copilot suggest with Raptor Mini integration.
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CopilotWrapper:
    """Wrapper for Copilot CLI operations."""
    
    def __init__(self):
        self.quota_tracking = {}
        self.account_rotation = []
        self.current_account_index = 0
    
    async def suggest(self, prompt: str, context: Optional[str] = None, 
                     model: str = "raptor-mini") -> Dict[str, Any]:
        """
        Use gh copilot suggest with specified model.
        
        Args:
            prompt: The task prompt
            context: Optional context (files, code, etc.)
            model: Model to use (raptor-mini, claude-haiku-4.5, etc.)
        
        Returns:
            Suggestion result
        """
        start_time = time.time()
        
        # Build command
        cmd = ["gh", "copilot", "suggest"]
        
        # Add model flag if supported
        if model != "raptor-mini":  # raptor-mini is default
            cmd.extend(["--model", model])
        
        # Prepare input
        if context:
            input_text = f"Context:\n{context}\n\nTask:\n{prompt}"
        else:
            input_text = prompt
        
        try:
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input=input_text.encode())
            
            response_time = time.time() - start_time
            
            if process.returncode == 0:
                result = {
                    "success": True,
                    "model": model,
                    "response": stdout.decode(),
                    "response_time": response_time,
                    "error": None
                }
                
                # Update quota tracking
                await self._update_quota(model, response_time)
                
                logger.info(f"Copilot suggestion successful: {model} ({response_time:.2f}s)")
                return result
            else:
                error_msg = stderr.decode()
                logger.error(f"Copilot suggestion failed: {error_msg}")
                
                return {
                    "success": False,
                    "model": model,
                    "response": None,
                    "response_time": response_time,
                    "error": error_msg
                }
                
        except Exception as e:
            logger.error(f"Copilot suggestion exception: {e}")
            return {
                "success": False,
                "model": model,
                "response": None,
                "response_time": time.time() - start_time,
                "error": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Copilot status and quota information."""
        try:
            result = await asyncio.create_subprocess_exec(
                "gh", "copilot", "status",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                status_text = stdout.decode()
                
                # Parse status information
                lines = status_text.split('\n')
                status_info = {
                    "enabled": "enabled" in status_text.lower(),
                    "status_text": status_text,
                    "quota_info": self._parse_quota_info(lines)
                }
                
                return status_info
            else:
                return {
                    "enabled": False,
                    "status_text": stderr.decode(),
                    "quota_info": {}
                }
                
        except Exception as e:
            return {
                "enabled": False,
                "status_text": f"Error: {str(e)}",
                "quota_info": {}
            }
    
    def _parse_quota_info(self, lines: List[str]) -> Dict[str, Any]:
        """Parse quota information from status output."""
        quota_info = {}
        
        for line in lines:
            line = line.strip()
            if "messages" in line.lower():
                # Parse messages remaining
                if "remaining" in line:
                    quota_info["messages_remaining"] = self._extract_number(line)
            elif "code completions" in line.lower():
                # Parse code completions remaining
                if "remaining" in line:
                    quota_info["completions_remaining"] = self._extract_number(line)
        
        return quota_info
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract number from text."""
        import re
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else None
    
    async def _update_quota(self, model: str, response_time: float):
        """Update quota tracking."""
        if model not in self.quota_tracking:
            self.quota_tracking[model] = {
                "requests": 0,
                "total_response_time": 0,
                "avg_response_time": 0
            }
        
        tracking = self.quota_tracking[model]
        tracking["requests"] += 1
        tracking["total_response_time"] += response_time
        tracking["avg_response_time"] = tracking["total_response_time"] / tracking["requests"]
    
    def get_quota_stats(self) -> Dict[str, Any]:
        """Get quota statistics."""
        return {
            "model_usage": self.quota_tracking,
            "total_requests": sum(t["requests"] for t in self.quota_tracking.values()),
            "rotation_info": {
                "current_account": self.current_account_index,
                "total_accounts": len(self.account_rotation)
            }
        }
    
    def set_account_rotation(self, accounts: List[str]):
        """Set account rotation list."""
        self.account_rotation = accounts
        logger.info(f"Account rotation set: {len(accounts)} accounts")

# Global instance
copilot_wrapper = CopilotWrapper()

async def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Copilot CLI Wrapper")
    subparsers = parser.add_subparsers(dest="command")
    
    # Suggest command
    suggest_parser = subparsers.add_parser("suggest", help="Get suggestion")
    suggest_parser.add_argument("--prompt", required=True, help="Task prompt")
    suggest_parser.add_argument("--context", help="Context (file or text)")
    suggest_parser.add_argument("--model", default="raptor-mini", 
                               choices=["raptor-mini", "claude-haiku-4.5", "gpt-4-preview"],
                               help="Model to use")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Get status")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Get statistics")
    
    args = parser.parse_args()
    
    if args.command == "suggest":
        context = None
        if args.context:
            if Path(args.context).exists():
                with open(args.context, 'r') as f:
                    context = f.read()
            else:
                context = args.context
        
        result = await copilot_wrapper.suggest(args.prompt, context, args.model)
        
        if result["success"]:
            print(f"✅ Success ({result['response_time']:.2f}s)")
            print(f"Model: {result['model']}")
            print(f"Response: {result['response']}")
        else:
            print(f"❌ Failed: {result['error']}")
    
    elif args.command == "status":
        status = await copilot_wrapper.get_status()
        print(json.dumps(status, indent=2))
    
    elif args.command == "stats":
        stats = copilot_wrapper.get_quota_stats()
        print(json.dumps(stats, indent=2))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
EOF

chmod +x scripts/xnai-copilot-wrapper.py
```

#### 3C.2: Raptor Integration with Dispatcher (4 hours)

**Task 3C.2.1: Integrate Raptor with Multi-Provider Dispatcher**
```python
# Update dispatcher to include Raptor integration
cat > app/XNAi_rag_app/core/raptor_integration.py << 'EOF'
#!/usr/bin/env python3
"""
Raptor Integration
Integration of Raptor Mini with the multi-provider dispatcher.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from app.XNAi_rag_app.core.copilot_wrapper import copilot_wrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RaptorIntegration:
    """Integration layer for Raptor Mini."""
    
    def __init__(self):
        self.copilot_wrapper = copilot_wrapper
        self.quota_management = RaptorQuotaManager()
    
    async def execute_raptor_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task using Raptor Mini.
        
        Args:
            task: Task dictionary with content and context
        
        Returns:
            Execution result
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Check quota availability
            if not await self.quota_management.is_available():
                logger.warning("Raptor quota exhausted, falling back")
                return {
                    "success": False,
                    "error": "Quota exhausted",
                    "fallback_required": True
                }
            
            # Prepare context
            context = self._prepare_context(task)
            prompt = task.get("content", "")
            
            # Execute with Copilot wrapper
            result = await self.copilot_wrapper.suggest(
                prompt=prompt,
                context=context,
                model="raptor-mini"
            )
            
            response_time = asyncio.get_event_loop().time() - start_time
            
            if result["success"]:
                # Update quota usage
                await self.quota_management.record_usage(response_time)
                
                return {
                    "success": True,
                    "provider": "copilot",
                    "model": "raptor-mini",
                    "response": result["response"],
                    "response_time": response_time,
                    "quota_remaining": await self.quota_management.get_remaining()
                }
            else:
                return {
                    "success": False,
                    "error": result["error"],
                    "response_time": response_time
                }
                
        except Exception as e:
            logger.error(f"Raptor execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "response_time": asyncio.get_event_loop().time() - start_time
            }
    
    def _prepare_context(self, task: Dict[str, Any]) -> Optional[str]:
        """Prepare context for Raptor task."""
        context_files = task.get("context_files", [])
        context_text = task.get("context_text", "")
        
        if context_files:
            # Combine context files
            context_content = []
            for file_path in context_files:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        context_content.append(f"File: {file_path}\n{content}")
                except Exception as e:
                    logger.warning(f"Could not read context file {file_path}: {e}")
            
            return "\n\n".join(context_content) if context_content else None
        
        return context_text if context_text else None

class RaptorQuotaManager:
    """Manage Raptor Mini quota across multiple accounts."""
    
    def __init__(self):
        self.accounts = []
        self.current_account = 0
        self.monthly_quota = 50  # Per account
        self.reset_date = None
        self.usage_data = {}
    
    def set_accounts(self, accounts: list):
        """Set available accounts."""
        self.accounts = accounts
        self.usage_data = {account: {"used": 0, "last_reset": None} for account in accounts}
        logger.info(f"Raptor accounts configured: {len(accounts)} accounts")
    
    async def is_available(self) -> bool:
        """Check if Raptor is available (quota not exhausted)."""
        if not self.accounts:
            return False
        
        current_usage = self._get_current_usage()
        return current_usage < self.monthly_quota * 0.9  # Allow 90% usage
    
    async def record_usage(self, response_time: float):
        """Record usage for current account."""
        if not self.accounts:
            return
        
        account = self.accounts[self.current_account]
        self.usage_data[account]["used"] += 1
        
        logger.info(f"Raptor usage recorded: {account} ({self.usage_data[account]['used']}/{self.monthly_quota})")
    
    async def get_remaining(self) -> Dict[str, Any]:
        """Get remaining quota information."""
        if not self.accounts:
            return {"available": False, "remaining": 0}
        
        current_usage = self._get_current_usage()
        remaining = max(0, self.monthly_quota - current_usage)
        
        return {
            "available": remaining > 0,
            "remaining": remaining,
            "current_account": self.accounts[self.current_account] if self.accounts else None,
            "total_accounts": len(self.accounts)
        }
    
    def _get_current_usage(self) -> int:
        """Get current account usage."""
        if not self.accounts:
            return 0
        
        account = self.accounts[self.current_account]
        return self.usage_data[account]["used"]
    
    def rotate_account(self):
        """Rotate to next account."""
        if not self.accounts:
            return
        
        self.current_account = (self.current_account + 1) % len(self.accounts)
        logger.info(f"Raptor account rotated to: {self.accounts[self.current_account]}")
    
    def reset_quota(self):
        """Reset quota for all accounts."""
        for account in self.accounts:
            self.usage_data[account]["used"] = 0
            self.usage_data[account]["last_reset"] = asyncio.get_event_loop().time()
        
        logger.info("Raptor quota reset for all accounts")

# Global instance
raptor_integration = RaptorIntegration()

async def main():
    """Test Raptor integration."""
    # Test task
    task = {
        "content": "Analyze this code for performance bottlenecks",
        "context_files": [],
        "context_text": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
    }
    
    result = await raptor_integration.execute_raptor_task(task)
    print(f"Raptor result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
EOF
```

### Implementation Status: Phase 3C

- [x] Copilot CLI wrapper implementation
- [x] Raptor Mini integration design
- [x] Quota management system
- [x] Account rotation logic
- [ ] Integration with main dispatcher
- [ ] Testing with real Copilot accounts
- [ ] Performance optimization

---

## Phase 3D: Testing & Validation (7 hours)

### Objective
Comprehensive testing suite to ensure production readiness.

### Tasks

#### 3D.1: Unit Tests (3 hours)

**Task 3D.1.1: Create Unit Test Suite**
```python
# Create unit tests for dispatcher
cat > tests/test_multi_provider_dispatcher.py << 'EOF'
#!/usr/bin/env python3
"""
Unit tests for Multi-Provider Dispatcher
"""

import asyncio
import unittest
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.XNAi_rag_app.core.multi_provider_dispatcher import MultiProviderDispatcher

class TestMultiProviderDispatcher(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.dispatcher = MultiProviderDispatcher()
    
    def test_task_classification(self):
        """Test task classification logic."""
        # Test code analysis classification
        code_task = {"content": "refactor this function for better performance"}
        self.assertEqual(self.dispatcher._classify_task(code_task), "code_analysis")
        
        # Test reasoning classification
        reasoning_task = {"content": "explain why this algorithm works"}
        self.assertEqual(self.dispatcher._classify_task(reasoning_task), "reasoning")
        
        # Test file operations classification
        file_task = {"content": "create a new file with this content"}
        self.assertEqual(self.dispatcher._classify_task(file_task), "file_operations")
        
        # Test sovereign classification
        sovereign_task = {"content": "handle sensitive data offline"}
        self.assertEqual(self.dispatcher._classify_task(sovereign_task), "sovereign")
    
    def test_candidate_selection(self):
        """Test candidate provider selection."""
        # Test with small context
        candidates = self.dispatcher._get_candidates("code_analysis", 1000)
        self.assertIn("copilot", candidates)  # Should include Copilot for code analysis
        
        # Test with large context
        candidates = self.dispatcher._get_candidates("reasoning", 500000)
        self.assertIn("opencode", candidates)  # Should include OpenCode for large context
    
    def test_scoring_algorithm(self):
        """Test provider scoring."""
        task = {"type": "code_analysis", "content": "test", "context_size": 1000}
        
        # Test scoring for different providers
        copilot_score = self.dispatcher._calculate_score("copilot", task)
        opencode_score = self.dispatcher._calculate_score("opencode", task)
        
        # Copilot should score higher for code analysis
        self.assertGreater(copilot_score, opencode_score)
    
    def test_account_selection(self):
        """Test account selection logic."""
        # Test round-robin selection
        account1 = self.dispatcher._select_account("copilot")
        account2 = self.dispatcher._select_account("copilot")
        
        # Should be different if multiple accounts exist
        # (This test assumes multiple accounts are configured)
        self.assertIsInstance(account1, int)
        self.assertIsInstance(account2, int)
    
    @patch('app.XNAi_rag_app.core.multi_provider_dispatcher.asyncio.create_subprocess_exec')
    async def test_provider_validation(self, mock_subprocess):
        """Test provider validation."""
        # Mock successful subprocess
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"enabled", b"")
        mock_subprocess.return_value = mock_process
        
        # Test Copilot validation
        is_valid = await self.dispatcher._validate_provider("copilot", 0)
        self.assertTrue(is_valid)
    
    def test_statistics_tracking(self):
        """Test statistics tracking."""
        initial_calls = self.dispatcher.statistics["total_dispatches"]
        
        # Simulate a dispatch
        self.dispatcher._update_statistics("copilot", 1.0, True)
        
        # Check statistics updated
        self.assertGreater(self.dispatcher.statistics["total_dispatches"], initial_calls)
        self.assertIn("copilot", self.dispatcher.statistics["provider_usage"])

class TestCopilotWrapper(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        from app.XNAi_rag_app.core.copilot_wrapper import CopilotWrapper
        self.wrapper = CopilotWrapper()
    
    @patch('app.XNAi_rag_app.core.copilot_wrapper.asyncio.create_subprocess_exec')
    async def test_suggest_success(self, mock_subprocess):
        """Test successful suggestion."""
        # Mock successful subprocess
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"test response", b"")
        mock_subprocess.return_value = mock_process
        
        result = await self.wrapper.suggest("test prompt")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["response"], "test response")
    
    @patch('app.XNAi_rag_app.core.copilot_wrapper.asyncio.create_subprocess_exec')
    async def test_suggest_failure(self, mock_subprocess):
        """Test failed suggestion."""
        # Mock failed subprocess
        mock_process = AsyncMock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = (b"", b"error message")
        mock_subprocess.return_value = mock_process
        
        result = await self.wrapper.suggest("test prompt")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "error message")

if __name__ == "__main__":
    unittest.main()
EOF
```

#### 3D.2: Integration Tests (2 hours)

**Task 3D.2.1: Create Integration Test Suite**
```python
# Create integration tests
cat > tests/test_integration.py << 'EOF'
#!/usr/bin/env python3
"""
Integration tests for Wave 4 Phase 3
"""

import asyncio
import unittest
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.XNAi_rag_app.core.multi_provider_dispatcher import dispatcher
from app.XNAi_rag_app.core.copilot_wrapper import copilot_wrapper

class TestIntegration(unittest.TestCase):
    
    @unittest.skip("Requires actual provider setup")
    async def test_end_to_end_dispatch(self):
        """Test complete dispatch flow."""
        task = {
            "type": "code_analysis",
            "content": "refactor this function for better performance",
            "context_size": 5000
        }
        
        result = await dispatcher.dispatch_task(task)
        
        self.assertIn("success", result)
        self.assertIn("provider", result)
        self.assertIn("response_time", result)
    
    @unittest.skip("Requires actual Copilot setup")
    async def test_copilot_integration(self):
        """Test Copilot wrapper integration."""
        result = await copilot_wrapper.suggest("test prompt")
        
        # Should either succeed or fail gracefully
        self.assertIn("success", result)
        self.assertIn("model", result)
    
    async def test_dispatcher_statistics(self):
        """Test dispatcher statistics tracking."""
        initial_stats = dispatcher.get_statistics()
        
        # Simulate some dispatches
        for i in range(5):
            task = {"type": "general", "content": f"test task {i}", "context_size": 1000}
            await dispatcher.dispatch_task(task)
        
        final_stats = dispatcher.get_statistics()
        
        self.assertGreater(final_stats["total_dispatches"], initial_stats["total_dispatches"])
        self.assertIn("provider_usage", final_stats)

if __name__ == "__main__":
    # Run async tests
    loop = asyncio.get_event_loop()
    test = TestIntegration()
    
    try:
        loop.run_until_complete(test.test_dispatcher_statistics())
        print("✅ Integration tests passed")
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
EOF
```

#### 3D.3: Performance Tests (2 hours)

**Task 3D.3.1: Create Performance Test Suite**
```python
# Create performance tests
cat > tests/test_performance.py << 'EOF'
#!/usr/bin/env python3
"""
Performance tests for Wave 4 Phase 3
"""

import asyncio
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.XNAi_rag_app.core.multi_provider_dispatcher import dispatcher

class TestPerformance(unittest.TestCase):
    
    def test_dispatch_latency(self):
        """Test dispatch latency under normal conditions."""
        async def run_dispatch():
            task = {"type": "general", "content": "test", "context_size": 1000}
            start_time = time.time()
            result = await dispatcher.dispatch_task(task)
            return time.time() - start_time
        
        # Run multiple dispatches and measure latency
        latencies = []
        for _ in range(10):
            latency = asyncio.run(run_dispatch())
            latencies.append(latency)
        
        avg_latency = sum(latencies) / len(latencies)
        print(f"Average dispatch latency: {avg_latency:.3f}s")
        
        # Should be under 1 second for local operations
        self.assertLess(avg_latency, 1.0)
    
    def test_concurrent_dispatch(self):
        """Test concurrent dispatch handling."""
        async def run_concurrent_dispatches():
            tasks = [
                {"type": "general", "content": f"test {i}", "context_size": 1000}
                for i in range(5)
            ]
            
            # Run dispatches concurrently
            start_time = time.time()
            results = await asyncio.gather(*[
                dispatcher.dispatch_task(task) for task in tasks
            ])
            total_time = time.time() - start_time
            
            return total_time, results
        
        total_time, results = asyncio.run(run_concurrent_dispatches())
        
        print(f"Concurrent dispatch time: {total_time:.3f}s")
        print(f"Results: {len([r for r in results if r['success']])} successful")
        
        # Should complete faster than sequential
        self.assertLess(total_time, 2.0)  # Should be very fast for local operations
    
    def test_memory_usage(self):
        """Test memory usage under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        async def run_memory_test():
            # Run many dispatches to test memory usage
            for i in range(100):
                task = {"type": "general", "content": f"test {i}", "context_size": 1000}
                await dispatcher.dispatch_task(task)
        
        asyncio.run(run_memory_test())
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory increase: {memory_increase:.2f} MB")
        
        # Should not leak memory significantly
        self.assertLess(memory_increase, 50)  # Less than 50MB increase

if __name__ == "__main__":
    unittest.main()
EOF
```

### Implementation Status: Phase 3D

- [x] Unit test framework setup
- [x] Integration test structure
- [x] Performance test framework
- [ ] Complete test execution
- [ ] Test coverage analysis
- [ ] CI/CD integration

---

## Implementation Timeline

### Week 1: Phase 3A (Infrastructure)
- **Day 1-2**: Credential storage system implementation
- **Day 3-4**: Daily audit system implementation  
- **Day 5**: Setup scripts and documentation

### Week 2: Phase 3B (Dispatch System)
- **Day 1-3**: MultiProviderDispatcher implementation
- **Day 4-5**: Agent Bus integration

### Week 3: Phase 3C (Raptor Integration)
- **Day 1-2**: Copilot CLI wrapper
- **Day 3-4**: Raptor integration with dispatcher
- **Day 5**: Testing and optimization

### Week 4: Phase 3D (Testing & Validation)
- **Day 1-3**: Comprehensive testing suite
- **Day 4-5**: Performance optimization and documentation

**Total**: 55 hours across 4 weeks

---

## Success Criteria

### Phase 3A Success
- [ ] Credential storage system operational
- [ ] Daily audit running automatically
- [ ] Account rotation working
- [ ] Security requirements met (0600 permissions, git-ignored)

### Phase 3B Success  
- [ ] MultiProviderDispatcher routing correctly
- [ ] Agent Bus integration functional
- [ ] Task classification accuracy >90%
- [ ] Fallback mechanisms working

### Phase 3C Success
- [ ] Raptor Mini integration operational
- [ ] Copilot CLI wrapper functional
- [ ] Quota management working
- [ ] Account rotation for Copilot working

### Phase 3D Success
- [ ] All unit tests passing
- [ ] Integration tests successful
- [ ] Performance targets met
- [ ] Documentation complete

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Credential security | Git-crypt, file permissions, environment variables |
| Provider API changes | Abstract interfaces, fallback mechanisms |
| Account quota exhaustion | Daily monitoring, automatic rotation |
| Performance issues | Benchmarking, optimization, caching |
| Integration complexity | Modular design, comprehensive testing |

---

## Next Steps

1. **Start Phase 3A**: Begin with credential storage system
2. **User Input Needed**: Account emails for Copilot accounts
3. **Testing**: Validate each phase before proceeding
4. **Documentation**: Maintain comprehensive documentation throughout

**Status**: 🟢 READY FOR IMPLEMENTATION  
**Next Action**: Begin Phase 3A infrastructure setup
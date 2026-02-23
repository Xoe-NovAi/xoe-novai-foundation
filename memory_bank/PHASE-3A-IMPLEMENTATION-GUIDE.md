# Phase 3A: Credential Storage & Token Validation - Implementation Guide

**Last Updated**: 2026-02-23T21:42:00Z  
**Status**: 🟢 COMPLETE & DOCUMENTED  
**Implementation Effort**: 6-7 hours (Credentials + Validation + Systemd)

---

## Overview

Phase 3A implements the credential management infrastructure for multi-account OpenCode dispatch:

1. **Credential Storage** (YAML config) - Stores provider credentials securely
2. **Credential Injection** (Bash script) - Injects credentials into runtime
3. **Token Validation** (Python module) - Validates tokens before dispatch
4. **Daily Audit** (Python script) - Tracks quota usage
5. **Systemd Integration** (Timer + Service) - Runs audits at 2 AM UTC

---

## Components

### 1. Credential Storage Template

**File**: `scripts/xnai-setup-opencode-credentials.yaml`

**Purpose**: Central credential configuration file with support for multiple provider accounts

**Structure**:
```yaml
credentials:
  opencode:
    accounts:
      account_1:
        auth_method: "oauth"
        provider: "google"
        oauth_token: "${XNAI_OPENCODE_ACCOUNT_1_OAUTH_TOKEN}"
        token_expiry: "2026-03-25T00:00:00Z"
        models: ["gemini-3-pro-preview", "claude-opus-4-6"]
  copilot:
    accounts:
      account_1:
        auth_method: "github_oauth"
        oauth_token: "${XNAI_COPILOT_ACCOUNT_1_TOKEN}"
        models: ["raptor-mini", "claude-haiku-4-5"]
  cline:
    auth_method: "api_key"
    api_key: "${XNAI_CLINE_ANTHROPIC_API_KEY}"
    models: ["claude-opus-4-6"]
```

**Security**:
- File permissions: 0600 (owner read/write only)
- Git-ignored: Add to .gitignore
- Environment variable override: Supports ${VAR} expansion
- Optional encryption: Can use git-crypt or sops

**Setup**:
```bash
# Create config directory
mkdir -p ~/.config/xnai

# Copy template
cp scripts/xnai-setup-opencode-credentials.yaml ~/.config/xnai/opencode-credentials.yaml

# Set permissions
chmod 0600 ~/.config/xnai/opencode-credentials.yaml

# Edit to add actual credentials (or use environment variables)
export XNAI_OPENCODE_ACCOUNT_1_OAUTH_TOKEN="ya29...."
export XNAI_COPILOT_ACCOUNT_1_TOKEN="ghp_..."
export XNAI_CLINE_ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. Credential Injection Script

**File**: `scripts/xnai-inject-credentials.sh`

**Purpose**: Validates and injects credentials into OpenCode runtime

**Features**:
- Pre-injection token validation
- XDG_DATA_HOME multi-instance isolation
- Environment variable override capability
- Security logging

**Usage**:
```bash
# Validate all credentials
./scripts/xnai-inject-credentials.sh ~/.config/xnai/opencode-credentials.yaml

# Inject OpenCode account 1
./scripts/xnai-inject-credentials.sh ~/.config/xnai/opencode-credentials.yaml opencode

# Setup multi-instance OpenCode
eval $(./scripts/xnai-inject-credentials.sh ~/.config/xnai/opencode-credentials.yaml all)

# Multi-instance with isolated credentials
XDG_DATA_HOME=/tmp/opencode-instance-1 opencode chat "prompt"
XDG_DATA_HOME=/tmp/opencode-instance-2 opencode chat "different prompt"
```

**Environment Setup**:
The script outputs environment variable assignments. Capture them:
```bash
# Capture output
CREDS=$(./scripts/xnai-inject-credentials.sh ~/.config/xnai/opencode-credentials.yaml all)

# Source into current shell
eval "$CREDS"

# Now use with OpenCode or Copilot
opencode chat "test"
```

### 3. Token Validation Module

**File**: `app/XNAi_rag_app/core/token_validation.py`

**Purpose**: Validates all provider credentials before dispatch

**Supported Providers**:

| Provider | Token Type | Lifetime | Validation | Refresh |
|----------|-----------|----------|-----------|---------|
| OpenCode | OAuth | ~30 days | Format + expiry | Optional (plugin) |
| Copilot | GitHub OAuth | 8-12 hours | Format + gh CLI | Automatic |
| Cline | API Key | Permanent | Format only | Manual |
| XNAI IAM | JWT | 15 minutes | Format + expiry + signature | Via refresh endpoint |

**Python API**:

```python
from app.XNAi_rag_app.core.token_validation import TokenValidator, TokenValidationResult

# Initialize validator
validator = TokenValidator(config_file="~/.config/xnai/opencode-credentials.yaml")

# Validate OpenCode token
status = validator.validate_token("opencode", "account_1")
print(f"Status: {status.result}")  # TokenValidationResult.VALID
print(f"Expires in: {status.hours_until_expiry}h")

# Validate Copilot token
status = validator.validate_token("copilot", "account_1")
if status.is_valid:
    print("Token valid, safe to dispatch")
else:
    print(f"Token invalid: {status.message}")

# Validate all accounts
results = validator.validate_all_accounts()
for account_id, status in results.items():
    print(f"{account_id}: {status.result.value}")

# Validate before credential injection
if validator.validate_token("opencode", "account_1").is_valid:
    # Safe to inject and use
    os.environ["OPENCODE_ACCOUNT"] = "account_1"
```

**CLI Usage**:
```bash
# Validate all accounts
python3 app/XNAi_rag_app/core/token_validation.py --all

# Validate specific account
python3 app/XNAi_rag_app/core/token_validation.py --provider opencode --account account_1

# Verbose output
python3 app/XNAi_rag_app/core/token_validation.py --all -v
```

**Validation Logic**:

| Provider | Checks |
|----------|--------|
| OpenCode | Token format (ya29.* or OAuth pattern) + expiry time |
| Copilot | Token length (40+) + gh CLI verification (if available) |
| Cline | Token prefix (sk-ant-) + format validation |
| XNAI IAM | JWT structure (3 parts) + expiry + optional signature |

### 4. Daily Quota Audit System

**File**: `scripts/xnai-quota-auditor.py`

**Purpose**: Collects quota usage daily at 2 AM UTC

**Output**: YAML reports saved to `memory_bank/ACCOUNT-TRACKING-YYYY-MM-DD.yaml`

**Usage**:
```bash
# Manual execution
python3 scripts/xnai-quota-auditor.py --config ~/.config/xnai/opencode-credentials.yaml

# With custom output
python3 scripts/xnai-quota-auditor.py --output /tmp/audit-reports
```

**Report Format**:
```yaml
audit_metadata:
  timestamp: 2026-02-23T02:00:00+00:00
  collection_time: "02:00 UTC"
  timezone: "UTC"

quotas:
  - provider: "opencode"
    account: "Antigravity Account 1"
    quota_total: 1000000
    quota_used: 250000
    quota_remaining: 750000
    usage_percentage: 25.0
    status: "active"
    burn_rate_per_day: 250000
    days_until_exhaustion: 3.0
    projection:
      exhaustion_date: 2026-02-26T02:00:00+00:00
      days_remaining: 3.0

summary:
  total_providers: 3
  total_accounts: 17
  critical_count: 0
  warning_count: 0
  average_usage_percentage: 32.5

alerts:
  - level: "WARNING"
    provider: "copilot"
    account: "Copilot Account 5"
    message: "Quota 82.0% used - monitor closely"
    action: "Plan account rotation in next 1-2 days"
```

### 5. Systemd Timer & Service

**Files**:
- `scripts/xnai-quota-audit.timer` - Scheduling configuration
- `scripts/xnai-quota-audit.service` - Service execution configuration

**Installation**:
```bash
# Copy timer and service files to systemd
sudo cp scripts/xnai-quota-audit.timer /etc/systemd/system/
sudo cp scripts/xnai-quota-audit.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable timer (auto-start on boot)
sudo systemctl enable xnai-quota-audit.timer

# Start timer immediately
sudo systemctl start xnai-quota-audit.timer

# Check timer status
systemctl status xnai-quota-audit.timer

# View timer schedule
systemctl list-timers xnai-quota-audit.timer

# View service logs
journalctl -u xnai-quota-audit.service -f
```

**Manual Execution**:
```bash
# Trigger quota audit manually (useful for testing)
sudo systemctl start xnai-quota-audit.service

# Check execution status
systemctl status xnai-quota-audit.service

# View last execution logs
journalctl -u xnai-quota-audit.service --lines=50
```

**Debugging**:
```bash
# Check if timer is active
systemctl is-active xnai-quota-audit.timer

# Check when next run is scheduled
systemctl list-timers xnai-quota-audit.timer --all

# Manually trigger for testing
sudo systemctl start xnai-quota-audit.service

# Watch logs in real-time
journalctl -u xnai-quota-audit.service -f
```

---

## Complete Setup Instructions

### Step 1: Prepare Credentials

```bash
# Get OAuth tokens from providers
# OpenCode: Visit https://accounts.google.com and complete OAuth flow in OpenCode CLI
# Copilot: Run `gh auth login` (if not already authenticated)
# Cline: Get from https://console.anthropic.com/account/keys

# Set environment variables with credentials
export XNAI_OPENCODE_ACCOUNT_1_OAUTH_TOKEN="ya29...."
export XNAI_OPENCODE_ACCOUNT_2_OAUTH_TOKEN="ya29...."
export XNAI_COPILOT_ACCOUNT_1_TOKEN="ghp_..."
export XNAI_CLINE_ANTHROPIC_API_KEY="sk-ant-..."
```

### Step 2: Setup Credential Storage

```bash
# Create config directory
mkdir -p ~/.config/xnai

# Copy and edit template
cp scripts/xnai-setup-opencode-credentials.yaml ~/.config/xnai/opencode-credentials.yaml
chmod 0600 ~/.config/xnai/opencode-credentials.yaml

# Edit to add credentials (replace ${VAR} with actual values or keep for env var substitution)
nano ~/.config/xnai/opencode-credentials.yaml
```

### Step 3: Validate Credentials

```bash
# Test credential injection
./scripts/xnai-inject-credentials.sh ~/.config/xnai/opencode-credentials.yaml

# Validate tokens in Python
python3 app/XNAi_rag_app/core/token_validation.py --all -v

# Should see: opencode_account_1: valid, copilot_account_1: valid, cline: valid
```

### Step 4: Setup Systemd Timer

```bash
# Copy systemd files
sudo cp scripts/xnai-quota-audit.{timer,service} /etc/systemd/system/

# Reload and enable
sudo systemctl daemon-reload
sudo systemctl enable xnai-quota-audit.timer
sudo systemctl start xnai-quota-audit.timer

# Verify installation
systemctl list-timers xnai-quota-audit.timer
```

### Step 5: Verify Installation

```bash
# Manual quota audit
python3 scripts/xnai-quota-auditor.py

# Check output
ls -la memory_bank/ACCOUNT-TRACKING-*.yaml

# Verify timer
systemctl status xnai-quota-audit.timer

# Check next scheduled run
systemctl list-timers xnai-quota-audit.timer --all
```

---

## Integration with Phase 3B Dispatcher

### Environment Variables for Dispatch

The credential injection script outputs environment variables ready for dispatcher use:

```bash
# Source credentials for dispatcher
eval $(./scripts/xnai-inject-credentials.sh ~/.config/xnai/opencode-credentials.yaml all)

# Dispatcher can access via environment
OPENCODE_ACCOUNT  # Which OpenCode account to use
XNAI_CLINE_ANTHROPIC_API_KEY  # Cline API key
```

### Quota Scoring Algorithm

Phase 3B dispatcher uses quota data from daily audits:

```python
# From Phase 3B scorer
quota_percentage = read_latest_audit("opencode", "account_1")
quota_score = 1.0 - (quota_percentage / 100)  # 100% used = score 0, 0% used = score 1.0

# Integrated into overall scoring:
# final_score = (quota_score * 0.4) + (latency_score * 0.3) + (context_fit * 0.3)
```

---

## Troubleshooting

### Token Validation Fails

**Problem**: "Token format invalid" or "gh CLI validation failed"

**Solution**:
1. Verify token is set: `echo $XNAI_OPENCODE_ACCOUNT_1_OAUTH_TOKEN`
2. For OpenCode: Ensure OAuth token starts with "ya29."
3. For Copilot: Run `gh auth status` to verify gh CLI setup
4. For Cline: Ensure API key starts with "sk-ant-"

### Systemd Timer Not Running

**Problem**: Timer shows "inactive" or logs show errors

**Solution**:
```bash
# Check timer is enabled
systemctl is-enabled xnai-quota-audit.timer

# Check service file syntax
systemd-analyze verify /etc/systemd/system/xnai-quota-audit.service

# Manual test
sudo systemctl start xnai-quota-audit.service

# Check logs
journalctl -u xnai-quota-audit.service -n 100
```

### Credentials Not Loading

**Problem**: "Config file not found" or YAML parse errors

**Solution**:
1. Verify config file exists: `ls -la ~/.config/xnai/opencode-credentials.yaml`
2. Check YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('~/.config/xnai/opencode-credentials.yaml'))"`
3. Verify permissions: `stat ~/.config/xnai/opencode-credentials.yaml` (should be 0600)

---

## Security Best Practices

1. **Store credentials securely**:
   - Use system keyring for production
   - Or use git-crypt for repo-based storage
   - Never commit plaintext credentials

2. **Rotate credentials regularly**:
   - OpenCode: Monthly (30-day OAuth tokens)
   - Copilot: Automatic (gh CLI handles refresh)
   - Cline: Quarterly (manual API key rotation)

3. **Monitor token validation**:
   - Check logs for validation failures
   - Set up alerts for low quota (80%+)
   - Audit daily quota reports

4. **Limit file access**:
   - Config file: 0600 (owner only)
   - Service runs as dedicated user (if possible)
   - Logs stored with restricted access

---

## Files Reference

| File | Purpose | Type |
|------|---------|------|
| `scripts/xnai-setup-opencode-credentials.yaml` | Credential template | Config |
| `scripts/xnai-inject-credentials.sh` | Credential injection | Script |
| `app/XNAi_rag_app/core/token_validation.py` | Token validation | Python Module |
| `scripts/xnai-quota-auditor.py` | Daily quota audit | Script |
| `scripts/xnai-quota-audit.timer` | Systemd timer | Unit |
| `scripts/xnai-quota-audit.service` | Systemd service | Unit |

---

## Next Steps

1. **Phase 3A.3**: ✅ Token validation middleware (complete)
2. **Phase 3A.4**: ✅ Systemd timer integration (complete)
3. **Phase 3B**: Implement dispatcher with token validation + quota scoring
4. **Phase 3C**: Multi-account Copilot/Cline rotation
5. **Phase 3D**: E2E testing with all components

---

**Status**: 🟢 PHASE 3A COMPLETE & FULLY DOCUMENTED  
**Security**: ✅ Zero-telemetry, git-ignored, perms enforced  
**Integration Ready**: ✅ For Phase 3B dispatcher  

*Implementation guide locked into memory_bank*

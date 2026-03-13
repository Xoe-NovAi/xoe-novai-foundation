# Multi-Account Specialist Expert

**Date**: February 26, 2026  
**Status**: Expert System Documentation  
**Purpose**: Dedicated expert for GitHub multi-account management, Copilot quota optimization, and account rotation

---

## Expert Overview

The Multi-Account Specialist Expert is a specialized domain expert responsible for all aspects of managing multiple GitHub accounts, Copilot quota optimization, and intelligent account rotation. This expert provides deep knowledge of the account management infrastructure, rotation strategies, and best practices for maximizing free tier usage across multiple accounts.

---

## Expert Capabilities

### Core Responsibilities

- **Account Management**: Comprehensive management of 7+ GitHub accounts
- **Quota Optimization**: Intelligent allocation and rotation of Copilot quotas
- **Rate Limit Management**: Monitoring and handling of rate limits
- **Automation**: Script-based and systemd-based account auditing
- **Integration**: Coordination with multi-provider dispatcher and Agent Bus

### Specializations

- **GitHub Account Management**
- **Copilot Free Tier Optimization**
- **Multi-Account Rotation Strategies**
- **Quota Monitoring & Alerts**
- **Account Authentication Management**
- **Split Test Coordination**

---

## Knowledge Domains

### 1. GitHub Account Architecture

**Purpose**: Understanding of GitHub multi-account setup and configuration

**Knowledge Areas**:

- **Account Types**: Admin (owner) vs Contributor accounts
- **Authentication**: GitHub CLI (`gh`) authentication and switching
- **SSH Keys**: Per-account SSH key management
- **Git Config**: Per-repository git identity configuration

**Key Components**:

- **GitHub CLI**: `gh auth status`, `gh auth switch`
- **SSH Config**: `~/.ssh/config` with host aliases
- **Git Config**: `git config --local user.email`
- **Account Registry**: `memory_bank/usage/github-accounts.yaml`

### 2. Copilot Quota Management

**Purpose**: Expertise in managing Copilot free tier quotas

**Knowledge Areas**:

- **Quota Structure**: 50 messages/month + 2000 completions per account
- **Reset Cycles**: Monthly reset on 1st of each month at 00:00 UTC
- **Usage Tracking**: Per-account usage monitoring
- **Model Preferences**: Raptor Mini, Claude Haiku 4.5, GPT-4.1

**Account Status**:

| Account | Email | Status | Usage |
|---------|-------|--------|-------|
| admin-01 | xoe.nova.ai@gmail.com | Active | 0/50 |
| contrib-01 | arcananovaai@gmail.com | SPLIT TEST READY | 25/50 (50%) |
| contrib-02-06 | Various | Ready | Reset in 3-5 days |

### 3. Rotation Strategies

**Purpose**: Intelligent account selection and rotation

**Strategies Available**:

| Strategy | Description | Best For |
|----------|-------------|----------|
| `lowest-usage-first` | Select account with lowest used quota | General tasks |
| `round-robin` | Sequential selection | Balanced usage |
| `quota-aware` | Prefer accounts above warning threshold | Sustained operations |
| `task-specific` | Match account to task type | Specialized work |

**Configuration**:

```yaml
rotation_strategy:
  method: "quota-aware"
  warning_threshold: 40  # Switch at 40% remaining
  exhaustion_threshold: 10  # Force switch at 10%
  auto_switch: true
```

### 4. Account Infrastructure

**Purpose**: Technical infrastructure for account management

**Components**:

- **Audit Script**: `scripts/github-account-audit.py`
- **Systemd Timer**: `scripts/xnai-github-audit.timer`
- **Account Registry**: `memory_bank/usage/github-accounts.yaml`
- **Dashboard**: `memory_bank/usage/DASHBOARD.md`

### 5. Split Test Coordination

**Purpose**: Managing model comparison split tests

**Workflow**:

1. Identify account with available quota
2. Switch to account using `gh auth switch`
3. Execute model task
4. Capture metrics and session logs
5. Rotate to next account/model

**Current Split Test Ready**:

- ✅ **arcananovaai@gmail.com**: 25 messages remaining (50%)

---

## Implementation Details

### Account Registry Schema

```yaml
accounts:
  - id: "gh-admin-01"
    email: "xoe.nova.ai@gmail.com"
    role: "admin"
    daily_driver: true
    copilot:
      messages_limit: 50
      messages_used: 0
      messages_remaining: 50
    status: "active"
```

### Audit Script Usage

```bash
# Check all accounts
python3 scripts/github-account-audit.py --verbose

# Save results to JSON
python3 scripts/github-account-audit.py --save

# Specific account check
gh api rate_limit
```

### Account Switching

```bash
# Switch to specific account
gh auth switch --user arcananovaai

# Verify current account
gh auth status

# Check git identity
git config user.email
```

---

## Integration Points

### With Multi-Provider Dispatcher

The Multi-Account Specialist integrates with the existing `multi_provider_dispatcher.py`:

- **Account Selection**: Provides account recommendations based on quota
- **Rotation Updates**: Updates account usage in real-time
- **Fallback Selection**: Provides fallback accounts when primary exhausted

### With Agent Bus

Publishes account events to Redis Streams:

- Account rotation events
- Quota exhaustion alerts
- Split test progress updates

### With Quota Auditor

Works alongside existing `scripts/xnai-quota-audit.py`:

- GitHub-specific quota tracking
- Cross-provider quota correlation
- Usage trend analysis

---

## Quick Expert Creation (JSON/YAML)

### Minimal Expert Definition

For quick expert creation without dedicated memory_bank, use YAML/JSON mappings:

```yaml
# Quick Expert: GitHub Account Quick Reference
expert_id: "github-account-quick"
domain: "github_accounts"
version: "1.0.0"

# Core knowledge (YAML)
knowledge:
  accounts:
    - id: "gh-01"
      email: "arcananovaai@gmail.com"
      status: "active"
      quota_remaining: 25
      
  commands:
    check_status: "gh auth status"
    switch_account: "gh auth switch --user <username>"
    check_rate_limit: "gh api rate_limit"
    
  rotation:
    strategy: "lowest-usage-first"
    current: "arcananovaai"

# File location
config_path: "memory_bank/usage/github-accounts.yaml"

# Dependencies
requires:
  - "scripts/github-account-audit.py"
  - "memory_bank/usage/DASHBOARD.md"
```

### JSON Quick Expert

```json
{
  "expert_id": "github-account-quick",
  "domain": "github_accounts",
  "version": "1.0.0",
  "knowledge": {
    "accounts": [
      {
        "id": "gh-01",
        "email": "arcananovaai@gmail.com",
        "status": "active",
        "quota_remaining": 25
      }
    ]
  },
  "commands": {
    "check_status": "gh auth status",
    "switch_account": "gh auth switch --user <username>"
  }
}
```

---

## Best Practices

### Daily Operations

1. **Morning Check**: Run audit script to check quota status
2. **Before Large Task**: Verify account has sufficient quota
3. **After Exhaustion**: Switch to next available account
4. **Weekly**: Review usage trends, plan rotations

### Split Test Protocol

1. **Pre-Test**: Verify account quota > 50%
2. **During Test**: Monitor for rate limit errors
3. **Post-Test**: Log results, rotate account if needed
4. **Analysis**: Compare outputs using evaluation criteria

### Account Maintenance

1. **Monthly Reset**: Update registry with new quotas
2. **Quarterly**: Review account list, remove stale accounts
3. **As Needed**: Add new contributor accounts

---

## Error Handling

### Rate Limit Exceeded

```bash
# Check current limit
gh api rate_limit

# Switch to account with quota
gh auth switch --user <account_with_quota>

# Wait for reset (if all exhausted)
# GitHub Copilot resets on 1st of month
```

### Authentication Issues

```bash
# Re-authenticate
gh auth login

# Check SSH keys
ls -la ~/.ssh/

# Verify Git config
git config --list --local
```

---

## File Locations

### Key Files

| File | Purpose |
|------|---------|
| `scripts/github-account-audit.py` | Account audit script |
| `scripts/xnai-github-audit.timer` | Daily audit timer |
| `scripts/xnai-github-audit.service` | Audit service |
| `memory_bank/usage/github-accounts.yaml` | Account registry |
| `memory_bank/usage/DASHBOARD.md` | Usage dashboard |
| `scripts/account_management/` | Modular account system |

### Configuration

- **Primary Config**: `memory_bank/usage/github-accounts.yaml`
- **Modular System**: `scripts/account_management/base.py`
- **Rotation Rules**: Within account registry

---

## Related Experts

- **Foundation Stack Expert**: Overall stack coordination
- **Multi-Provider Dispatcher**: Cross-provider task routing
- **Quota Auditor**: General quota monitoring
- **Agent Bus**: Event coordination

---

## Status

**Version**: 1.0.0  
**Status**: Active  
**Last Updated**: 2026-02-26  
**Ready for**: Split tests, account rotation, quota management

---

**Expert ID**: `multi-account-specialist`  
**Domain**: `github_accounts_copilot`  
**Integration**: `memory_bank/usage/` + `scripts/`

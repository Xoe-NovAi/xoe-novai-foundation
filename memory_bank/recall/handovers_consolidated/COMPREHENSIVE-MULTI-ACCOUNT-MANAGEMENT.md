# Comprehensive Multi-Account Management Strategy

**Date**: 2026-02-26  
**Status**: Strategic Implementation Guide  
**Purpose**: Unified management of GitHub accounts, Copilot quotas, and provider rotation  
**Integration**: Works with existing `memory_bank/usage/` infrastructure

---

## Executive Summary

This document establishes a comprehensive multi-account management strategy that:
1. **Integrates with existing quota rotation infrastructure** (scripts, tracking)
2. **Assigns GitHub accounts to specific branches and roles**
3. **Maximizes Copilot free tier utilization** (50 msgs × 8 accounts = 400/month)
4. **Provides clear daily driver strategy** for development
5. **Enables branch-specific account ownership** for attribution

---

## 1. Account Assignment Strategy

### 1.1 GitHub Account Registry

| Account | Role | Daily Driver | Primary Use | Branch Ownership | Quota |
|---------|------|--------------|-------------|------------------|-------|
| `xoe.nova.ai@gmail.com` | **Admin** | ✅ YES | Main development, merges, admin | `main`, `develop` | 50 |
| `lilithasterion@gmail.com` | Contributor | ❌ NO | Feature work, testing | `feature/*`, `lilith/*` | 50 |
| `antipode2727@gmail.com` | Contributor | ❌ NO | Feature work, testing | `feature/*`, `antipode2727/*` | 50 |
| `antipode74@gmail.com` | Contributor | ❌ NO | Feature work, testing | `feature/*`, `antipode74/*` | 50 |
| (additional) | Contributor | ❌ NO | Rotational | `experiment/*` | 50 |

### 1.2 Daily Driver Recommendation

**Use `xoe.nova.ai@gmail.com` (admin) as daily driver because:**

| Factor | Rationale |
|--------|-----------|
| **Ownership** | Owns the repository, can merge PRs |
| **Persistence** | Primary identity, always available |
| **Simplicity** | One primary account for daily work |
| **Permissions** | Can push to protected branches |
| **Copilot** | 50 msgs/month + 2000 completions guaranteed |

**Use contributor accounts for:**
- Additional Copilot quota when admin exhausted
- Specific feature branches (attribution)
- Testing multi-account scenarios
- Parallel development streams

---

## 2. Branch Ownership Model

### 2.1 Recommended Branch Strategy

```
main (protected - admin only)
    │
    ├── develop (integration - admin only)
    │       │
    │       ├── feature/split-test-infra (lilithasterion)
    │       │       └── For split test infrastructure
    │       │
    │       ├── feature/wave5-manual (antipode2727)
    │       │       └── For Wave 5 manual work
    │       │
    │       └── feature/nova-voice (antipode74)
    │               └── For voice app work
    │
    └── experiment/* (rotating accounts)
            └── For testing/trying things
```

### 2.2 Why Branch Ownership Matters

| Benefit | Description |
|---------|-------------|
| **Attribution** | Know who wrote what |
| **Accountability** | Clear ownership for issues |
| **Quota Tracking** | Know which account used quota |
| **History** | Git blame shows contributor |

### 2.3 Setting Up Branch Ownership

```bash
# When creating a feature branch, configure local git identity
git checkout -b feature/split-test-infra

# Set branch-specific identity
git config user.name "Lilith Asterion"
git config user.email "lilithasterion@gmail.com"

# Verify
git config --local user.email
# Output: lilithasterion@gmail.com
```

---

## 3. Integration with Existing Quota Infrastructure

### 3.1 Current Infrastructure

The XNAi Foundation already has robust quota management:

| Component | Location | Purpose |
|-----------|----------|---------|
| **Quota Auditor** | `scripts/xnai-quota-auditor.py` | Daily quota monitoring |
| **Systemd Timer** | `scripts/xnai-quota-audit.timer` | Automated daily runs |
| **Usage Tracking** | `memory_bank/usage/copilot-usage.json` | Per-account quota |
| **Dispatch Log** | `memory_bank/usage/DISPATCH-LOG.json` | Account rotation log |

### 3.2 Extended Schema

Extend `copilot-usage.json` to include GitHub identity:

```json
{
  "account_pool": [
    {
      "id": "copilot-01",
      "email": "xoe.nova.ai@gmail.com",
      "github_account": "xoe-novai",
      "role": "admin",
      "daily_driver": true,
      "branch_pattern": "main,develop",
      "messages_used": 0,
      "messages_limit": 50,
      "status": "active",
      "notes": "Primary account - admin"
    },
    {
      "id": "copilot-02", 
      "email": "lilithasterion@gmail.com",
      "github_account": "lilithasterion",
      "role": "contributor",
      "daily_driver": false,
      "branch_pattern": "feature/*,lilith/*",
      "messages_used": 0,
      "messages_limit": 50,
      "status": "ready",
      "notes": "Feature development"
    }
  ]
}
```

### 3.3 Rotation Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                   QUOTA ROTATION WORKFLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Daily: Quota auditor checks all accounts                 │
│     └── scripts/xnai-quota-auditor.py                       │
│                                                              │
│  2. If account-01 < 10 msgs remaining:                     │
│     └── Mark as "depleted"                                 │
│     └── Log to DISPATCH-LOG.json                           │
│                                                              │
│  3. Next CLI task:                                          │
│     └── Select lowest-usage account                         │
│     └── gh auth switch --user <account>                    │
│     └── Run copilot "task..."                              │
│                                                              │
│  4. After task:                                             │
│     └── Update messages_used in copilot-usage.json         │
│     └── Update DISPATCH-LOG.json                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. SSH Key Configuration

### 4.1 Generate SSH Keys (If Needed)

```bash
# Check if you have SSH keys
ls -la ~/.ssh/

# If not, generate for each account (ED25519 recommended)
ssh-keygen -t ed25519 -C "xoe.nova.ai@gmail.com" -f ~/.ssh/github_xoe
ssh-keygen -t ed25519 -C "lilithasterion@gmail.com" -f ~/.ssh/github_lilith
ssh-keygen -t ed25519 -C "antipode2727@gmail.com" -f ~/.ssh/github_antipode2727
ssh-keygen -t ed25519 -C "antipode74@gmail.com" -f ~/.ssh/github_antipode74
```

### 4.2 Add to GitHub

For each public key (`~/.ssh/*.pub`), add to respective GitHub account:
1. Go to Settings → SSH and GPG keys → New SSH key
2. Paste public key
3. Give descriptive title (e.g., "XNAi Workstation - xoe.nova.ai")

### 4.3 SSH Config

```bash
# ~/.ssh/config

# Main (admin) account - default
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_xoe
    IdentitiesOnly yes

# Contributor accounts (if needed for specific repos)
Host github-lilith
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_lilith
    IdentitiesOnly yes

Host github-antipode2727
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_antipode2727
    IdentitiesOnly yes

Host github-antipode74
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_antipode74
    IdentitiesOnly yes
```

---

## 5. Git Configuration Per Account

### 5.1 Global Default (Admin Account)

```bash
# Set global to main account
git config --global user.name "Xoe NovAi"
git config --global user.email "xoe.nova.ai@gmail.com"
git config --global core.sshCommand "ssh -i ~/.ssh/github_xoe"
```

### 5.2 Repository-Specific Override

For feature branches owned by contributor accounts:

```bash
# In repository
cd /path/to/xoe-novai-foundation

# Override for specific branch or feature
git config user.name "Lilith Asterion"
git config user.email "lilithasterion@gmail.com"

# This creates .git/config entry:
# [user]
#     name = Lilith Asterion
#     email = lilithasterion@gmail.com
```

### 5.3 Verify Configuration

```bash
# Check current repo config
git config --list --local

# Check which identity will be used
git log -1 --format="%ae"

# Check SSH key
ssh -T git@github.com
# Should respond with your GitHub username
```

---

## 6. GitHub CLI (gh) Integration

### 6.1 Check Current Auth

```bash
# See authenticated accounts
gh auth status

# List all accounts
gh api user -q '.login' 2>/dev/null || echo "Not authenticated"
```

### 6.2 Switching Accounts

```bash
# Switch to different account for Copilot
gh auth switch --user lilithasterion

# Verify
gh auth status

# Now Copilot uses this identity
copilot "your task"
```

### 6.3 Automation Script

Create `scripts/gh-account-switch.sh`:

```bash
#!/bin/bash
# Switch GitHub account for development

ACCOUNT=$1

case $ACCOUNT in
  xoe)
    gh auth switch --user xoe-novai
    git config --local user.email "xoe.nova.ai@gmail.com"
    ;;
  lilith)
    gh auth switch --user lilithasterion
    git config --local user.email "lilithasterion@gmail.com"
    ;;
  antipode2727)
    gh auth switch --user antipode2727
    git config --local user.email "antipode2727@gmail.com"
    ;;
  antipode74)
    gh auth switch --user antipode74
    git config --local user.email "antipode74@gmail.com"
    ;;
  *)
    echo "Usage: $0 {xoe|lilith|antipode2727|antipode74}"
    exit 1
    ;;
esac

echo "Switched to: $ACCOUNT"
gh auth status
```

---

## 7. Account Rotation for Split Test

### 7.1 Split Test Account Allocation

| Model | Account | Rationale |
|-------|---------|-----------|
| **Raptor Mini** | `xoe.nova.ai` (admin) | Most quota, primary |
| **Haiku 4.5** | `lilithasterion` | Dedicated account |
| **MiniMax M2.5** | OpenCode (unlimited) | No GitHub needed |

### 7.2 Execution Workflow

```bash
# Step 1: Raptor Mini
./scripts/gh-account-switch.sh xoe
copilot -m raptor-mini-preview "Create Wave 5 Manual..."

# Step 2: Haiku 4.5  
./scripts/gh-account-switch.sh lilith
copilot -m claude-haiku-4-5 "Create Wave 5 Manual..."

# Step 3: MiniMax M2.5 (no GitHub needed)
opencode --model minimax-m2.5-free "Create Wave 5 Manual..."
```

---

## 8. Integration with Existing Infrastructure

### 8.1 Extend Quota Auditor

Update `scripts/xnai-quota-auditor.py` to track GitHub identity:

```python
# Add to account schema
account_schema = {
    "id": "copilot-01",
    "email": "xoe.nova.ai@gmail.com",
    "github_account": "xoe-novai",  # NEW
    "role": "admin",                # NEW
    "daily_driver": True,           # NEW
    "branch_pattern": "main,develop",  # NEW
    "messages_used": 0,
    "messages_limit": 50,
    ...
}
```

### 8.2 Update Dispatcher

Integrate with `multi_provider_dispatcher.py`:

```python
# When selecting GitHub/Copilot provider:
def select_github_account(self, task_type: str) -> str:
    """Select best GitHub account based on quota and branch needs"""
    
    accounts = self.load_accounts()
    
    # Filter by branch requirements if specified
    if task_type == "feature":
        # Use contributor accounts for features
        candidates = [a for a in accounts if a["role"] == "contributor"]
    else:
        # Use admin for main work
        candidates = [a for a in accounts if a["role"] == "admin"]
    
    # Select lowest usage
    return min(candidates, key=lambda a: a["messages_used"])
```

---

## 9. Summary: Turning Complexity to Advantage

### 9.1 Why This Works

| Complexity | Advantage |
|------------|-----------|
| **Multiple accounts** | 400 msgs/month vs 50 |
| **Branch ownership** | Clear attribution, accountability |
| **Role separation** | Admin for merges, contributors for features |
| **Rotation** | Always have quota available |
| **Integration** | Works with existing quota system |

### 9.2 Daily Workflow

```bash
# Morning: Check quota status
python3 scripts/xnai-quota-auditor.py

# Development: Use admin (default)
# ... work on main ...

# Feature branch: Switch identity
./scripts/gh-account-switch.sh lilith
git checkout -b feature/my-feature
# ... work on feature ...

# Copilot task: Use account with most quota
# (Quota auditor automatically selects)
```

### 9.3 When to Use Which Account

| Task | Account | Why |
|------|---------|-----|
| Main development | `xoe.nova.ai` | Permissions, ownership |
| Merging PRs | `xoe.nova.ai` | Admin required |
| Feature work | Any contributor | Attribution, quota preservation |
| Copilot tasks | Rotating | Maximize quota |
| Admin tasks | `xoe.nova.ai` | Only admin can do |

---

## 10. Quick Reference Commands

```bash
# Check current identity
git config user.email
gh auth status

# Switch account
gh auth switch --user lilithasterion

# Create feature branch with identity
git checkout -b feature/my-feature
git config user.name "Feature Author"
git config user.email "contributor@gmail.com"

# Verify quota status
python3 scripts/xnai-quota-auditor.py

# Check rotation recommendations
cat memory_bank/usage/DISPATCH-LOG.json | jq
```

---

## 11. Next Steps

1. **Verify SSH keys** (check `ls ~/.ssh/`)
2. **Configure git identity** for this repository
3. **Update copilot-usage.json** with actual emails
4. **Test account switching** with `gh auth switch`
5. **Run split test** with quota rotation

---

## Appendix: Complete Account Registry

```yaml
# memory_bank/usage/github-accounts.yaml
accounts:
  - email: xoe.nova.ai@gmail.com
    github_username: xoe-novai
    role: admin
    daily_driver: true
    branch_pattern: main,develop
    ssh_key: github_xoe
    copilot_quota: 50/month
    status: active
    
  - email: lilithasterion@gmail.com
    github_username: lilithasterion
    role: contributor
    daily_driver: false
    branch_pattern: feature/*,lilith/*
    ssh_key: github_lilith
    copilot_quota: 50/month
    status: ready
    
  - email: antipode2727@gmail.com
    github_username: antipode2727
    role: contributor
    daily_driver: false
    branch_pattern: feature/*,antipode2727/*
    ssh_key: github_antipode2727
    copilot_quota: 50/month
    status: ready
    
  - email: antipode74@gmail.com
    github_username: antipode74
    role: contributor
    daily_driver: false
    branch_pattern: feature/*,antipode74/*
    ssh_key: github_antipode74
    copilot_quota: 50/month
    status: ready

total_copilot_quota: 200 messages/month
```

---

**Last Updated**: 2026-02-26  
**Status**: Implementation Ready  
**Coordination Key**: `MULTI-ACCOUNT-MANAGEMENT-2026-02-26`

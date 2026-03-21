# Multiple GitHub Account Management Strategy

**Date**: 2026-02-26  
**Status**: Strategy & Recommendations  
**Purpose**: Guide for managing multiple GitHub accounts and leveraging for XNAi Foundation

---

## 1. Current Account Setup Analysis

### 1.1 Your Accounts

| Account | Role | Primary Use |
|---------|------|-------------|
| `xoe.nova.ai@gmail.com` | **Admin/Owner** | Main repo owner, admin tasks |
| `lilithasterion@gmail.com` | Contributor | Additional Copilot free tier |
| `antipode2727@gmail.com` | Contributor | Additional Copilot free tier |
| `antipode74@gmail.com` | Contributor | Additional Copilot free tier |
| `thejedifather@gmail.com` (maybe) | Contributor | Additional Copilot free tier |

### 1.2 Purpose

The complex setup exists because:
- **GitHub Copilot Free Tier**: 50 messages/month per account
- **Multiple accounts** = 50 × N messages per month
- **Strategy**: Maximize free tier usage for development

---

## 2. Recommended Management Approach

### 2.1 SSH Key Strategy (Recommended)

Create separate SSH keys for each account:

```bash
# Generate SSH keys for each account
ssh-keygen -t ed25519 -C "xoe.nova.ai@gmail.com" -f ~/.ssh/github_xoe
ssh-keygen -t ed25519 -C "lilithasterion@gmail.com" -f ~/.ssh/github_lilith
ssh-keygen -t ed25519 -C "antipode2727@gmail.com" -f ~/.ssh/github_antipode2727
ssh-keygen -t ed25519 -C "antipode74@gmail.com" -f ~/.ssh/github_antipode74

# Add each public key to respective GitHub account
# Settings → SSH and GPG keys → New SSH key
```

### 2.2 SSH Config File

Configure `~/.ssh/config` to route to correct keys:

```bash
# ~/.ssh/config

# Default (main account)
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

### 2.3 Repository-Specific Git Config

For each repository, set local git config:

```bash
# For XNAi Foundation (use main account)
cd /path/to/xoe-novai-foundation
git config user.name "Xoe NovAi"
git config user.email "xoe.nova.ai@gmail.com"

# For experimental repos (could use contributor)
cd /path/to/experiment
git config user.name "Lilith"
git config user.email "lilithasterion@gmail.com"
```

---

## 3. GitHub CLI (gh) Multi-Account

### 3.1 Check Current Auth

```bash
# See current authenticated accounts
gh auth status

# List all authenticated accounts
gh api user -q '.login'
```

### 3.2 Switching Accounts

```bash
# Switch to different account (if authenticated)
gh auth switch

# Add another account
gh auth login
```

### 3.3 For Copilot CLI (copilot)

The Copilot CLI uses GitHub OAuth, so it inherits from `gh` auth:

```bash
# Ensure you're authenticated with the right account
gh auth status

# Then run copilot with that identity
copilot "your prompt here"
```

---

## 4. Strategy for XNAi Foundation

### 4.1 Recommended Approach

**Use main account (`xoe.nova.ai@gmail.com`) for:**
- Repository ownership and administration
- All commits to main branch
- Merging pull requests
- Admin tasks

**Use contributor accounts for:**
- Feature branches (to show contribution diversity)
- Testing multi-account workflows
- Additional Copilot quota for development

### 4.2 For Split Test Execution

Each model run can use different accounts for quota management:

```bash
# Account 1: xoe.nova.ai (main)
gh auth switch --user xoe.nova.ai
copilot -m raptor-mini-preview "Create Wave 5 Manual..."

# Account 2: lilithasterion
gh auth switch --user lilithasterion
copilot -m claude-haiku-4-5 "Create Wave 5 Manual..."

# Account 3: antipode2727
gh auth switch --user antipode2727
opencode --model minimax-m2.5-free "Create Wave 5 Manual..."
```

---

## 5. Managing the Complexity

### 5.1 Credential Storage

| Method | Pros | Cons |
|--------|------|------|
| **SSH Keys** | Secure, persistent | Setup complexity |
| **GitHub CLI (gh)** | Easy, integrated | Token expiry |
| **Personal Access Tokens** | Full control | Manual refresh |

### 5.2 Workflow Recommendation

```
┌─────────────────────────────────────────────────────────────┐
│                    RECOMMENDED WORKFLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Set up SSH keys for all accounts                       │
│  2. Configure ~/.ssh/config with aliases                    │
│  3. Use main account for XNAi Foundation repo               │
│  4. Use gh auth switch for Copilot CLI                     │
│  5. Document account usage in memory_bank                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Account Usage Tracking

Track usage in memory bank:

```yaml
# memory_bank/usage/github-accounts.yaml
accounts:
  - email: xoe.nova.ai@gmail.com
    role: admin
    ssh_key: github_xoe
    copilot_quota: 50/month
    
  - email: lilithasterion@gmail.com
    role: contributor
    ssh_key: github_lilith
    copilot_quota: 50/month
    
  - email: antipode2727@gmail.com
    role: contributor
    ssh_key: github_antipode2727
    copilot_quota: 50/month
    
  - email: antipode74@gmail.com
    role: contributor
    ssh_key: github_antipode74
    copilot_quota: 50/month

total_copilot_quota: 200 messages/month
```

---

## 6. Should You Use Admin Account?

### 6.1 Recommendation

**YES — Use admin account (`xoe.nova.ai@gmail.com`) for:**

1. **Repository management** - Settings, branches, collaborators
2. **Main development** - Working on main codebase
3. **Merges** - Pull request merges to main
4. **Admin tasks** - GitHub Copilot settings, organization

**Use contributor accounts for:**

1. **Additional Copilot quota** - When main account exhausted
2. **Testing** - Multi-account scenarios
3. **Experimentation** - Feature branches

### 6.2 Why This Works

| Task | Account | Reason |
|------|---------|--------|
| Push to main | xoe.nova.ai | Owner permissions |
| Create feature branch | Any | Contributor can create |
| Run Copilot | Any with quota | Rate limit management |
| Merge PR | xoe.nova.ai | Admin required |

---

## 7. Quick Setup Commands

### 7.1 Check Current Setup

```bash
# Check git config
git config --list --local

# Check SSH keys
ls -la ~/.ssh/

# Check gh auth
gh auth status

# Check current user
git config user.email
```

### 7.2 Switch Account for Development

```bash
# Switch to different GitHub account for Copilot
gh auth switch --user lilithasterion

# Verify
gh auth status

# Now run Copilot with this identity
copilot "your task"
```

### 7.3 Switch Back to Admin

```bash
# Switch back to main account
gh auth switch --user xoe.nova.ai

# Verify
gh auth status
```

---

## 8. Alternative: Single Account with Tokens

If managing multiple accounts becomes too complex:

### Option A: Use One Account + API Tokens

```bash
# Create Personal Access Token (PAT) for each account
# Settings → Developer settings → Personal access tokens

# Store tokens securely
echo "gh auth login"  # Use token when prompted
```

### Option B: Use GitHub Organization

Create an organization and invite all accounts as members:
- Single main account owns org
- All contributor accounts are members
- Simpler permissions management

---

## 9. Summary & Recommendations

### Decision Matrix

| Factor | Recommendation |
|--------|-----------------|
| **Primary account** | `xoe.nova.ai@gmail.com` (admin) |
| **Development** | Use admin for main work |
| **Copilot quota** | Rotate through contributor accounts |
| **SSH keys** | Set up for all accounts |
| **gh auth** | Use for quick account switching |

### Next Steps

1. **Verify current setup**:
   ```bash
   gh auth status
   git config user.email
   ls ~/.ssh/
   ```

2. **If not set up**: Create SSH keys for each account

3. **Document in memory_bank**: Track account usage

4. **Use admin for XNAi**: Primary development on main account

---

## 10. Questions for You

1. **Are all accounts authenticated** with `gh` currently?
2. **Do you have SSH keys** set up for each account?
3. **Which account are you most comfortable** using for daily work?
4. **Do you want to consolidate** to fewer accounts, or keep the multi-account setup for maximum Copilot quota?

---

**Last Updated**: 2026-02-26  
**Guidance**: Use admin account for main work, contributor accounts for additional Copilot quota

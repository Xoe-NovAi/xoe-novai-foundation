# 🌌 Antigravity Sovereign Operations Guide

**System:** Antigravity OAuth Integration for OpenCode CLI  
**Stack:** Omega Stack (Xoe-NovAi Foundation)  
**Version:** 2.1.0 (Patched for OpenCode 1.2.16)  
**Status:** ✅ OPERATIONAL

---

## 📖 Overview

This guide documents the **Sovereign Operations** for the Antigravity authentication system. Due to fundamental bugs in the OpenCode CLI (v1.2.16) internal `auth` command, we use a custom-built, out-of-band injection and rotation system designed specifically for the Omega Stack.

### Key Capabilities
- **Direct OAuth Injection**: Bypasses the broken `fetch` logic in OpenCode.
- **Multi-Account Rotation**: Supports up to 8 rotating Google accounts for massive free context windows.
- **Thinking Block Preservation**: Advanced Claude Opus 4.6 configuration with signature caching.
- **Omega Instance Sync**: Automatically synchronizes credentials across all 8 isolated Omega instances.

---

## 🚀 Walkthrough: Getting Started

### 1. The Direct Login (One-Time)
Since `opencode auth login` is currently broken, use our custom sovereign tool:

```bash
# Start the login server
node scripts/antigravity-direct-login.js
```

1.  **Copy the URL** generated in the terminal.
2.  **Authorize** in your browser.
3.  **Wait for SUCCESS**: The script will automatically capture the token and update your system.

### 2. Synchronize Instances
After a successful login, sync your tokens to all Omega instances:

```bash
./scripts/antigravity-maintenance.sh sync
```

### 3. Verify Capability
Test the highest-tier model available:

```bash
opencode run "Analyze the Omega Stack architecture." --model=google/antigravity-claude-opus-4-6-thinking --variant=max
```

---

## 🛠️ Maintenance & Health Monitoring

We provide a dedicated maintenance tool for the Antigravity subsystem.

| Command | Purpose |
|---------|---------|
| `./scripts/antigravity-maintenance.sh status` | Check account health, enabled status, and quotas. |
| `./scripts/antigravity-maintenance.sh sync` | Push current `auth.json` to all `/tmp/xnai-opencode-instance-*` folders. |
| `./scripts/antigravity-maintenance.sh cleanup` | Remove debug logs older than 7 days. |
| `./scripts/antigravity-maintenance.sh all` | Perform a full health check, sync, and cleanup. |

---

## ⚙️ Advanced Configuration

The system is pre-configured in `~/.config/opencode/antigravity.json`.

### Recommended "Sovereign" Tuning:
```json
{
  "account_selection_strategy": "hybrid",  // Health-based deterministic rotation
  "keep_thinking": true,                   // DO NOT strip thinking blocks
  "proactive_token_refresh": true,         // Refresh tokens 30m before expiry
  "soft_quota_threshold_percent": 95,      // Prevent hard rate limits
  "scheduling_mode": "cache_first"         // Priority to prompt caching
}
```

---

## ❓ FAQ

**Q: Why can't I just use `opencode auth login`?**  
**A:** OpenCode v1.2.16 has a bug where it attempts to fetch internal URLs that are invalid, causing a `fetch() URL is invalid` crash. Our `antigravity-direct-login.js` tool bypasses this entirely.

**Q: How do I add a second or third account?**  
**A:** Run `node scripts/antigravity-direct-login.js` again. The tool will append the new account to your registry automatically.

**Q: What is `rising-fact-p41fc`?**  
**A:** This is the default internal project ID used for Antigravity access. It is normal to see this in your `auth.json`.

---

## 🆘 Troubleshooting

### Error: `All Antigravity accounts have invalid refresh tokens`
**Cause:** Your Google session has expired or the token was revoked.  
**Fix:** 
1. Run `rm ~/.config/opencode/antigravity-accounts.json`
2. Run `node scripts/antigravity-direct-login.js` to re-authenticate.

### Error: `Google Generative AI API key is missing`
**Cause:** The plugin failed to initialize or the `google/` prefix was not recognized.  
**Fix:** Run `./scripts/xnai-setup-opencode-providers.sh` to fix your `auth.json` format.

### Error: Port `51121` already in use
**Cause:** A previous login attempt is still running in the background.  
**Fix:** `lsof -i :51121` -> `kill -9 <PID>`.

---

## 🔄 Updating the System

If the Antigravity plugin updates, run:
```bash
npm install -g opencode-antigravity-auth@latest
./scripts/setup-opencode-multiaccount.sh config
```
*Note: Our patches are resilient to global plugin updates as they target the configuration and injection layers.*

## 🤖 Agent Handoff Automation

To streamline the handoff from MiniMax (Working Memory) to Opus (Reasoning Core), use the `handoff-prep` tool.

**Usage (from Agent):**
```bash
!python3 scripts/prepare_handoff_context.py "Task description"
```

**Usage (from Makefile):**
```bash
make handoff-prep TASK="Task description"
```

This generates `context_for_opus.md`, containing the current task, active context, and recent logs, formatted for Opus 4.6.

## 🔗 Advanced Provider Setup

For instructions on setting up additional cloud providers (SiliconFlow, SambaNova, etc.), see the [Omega Stack Provider Setup Guide](./PROVIDER_SETUP_GUIDE.md).

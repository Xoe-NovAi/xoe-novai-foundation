# Antigravity Auth — Google OAuth Comprehensive Guide

**Date:** 2026-02-18 (updated after live auth session)
**Status:** ✅ OPERATIONAL — OAuth completed successfully
**Source:** NPM package docs (v1.5.1) + live auth session observation
**Plugin:** `opencode-antigravity-auth@latest`

---

## What You Get (Free, via Google Account)

| Model ID | Context | Thinking | Best For |
|----------|---------|----------|---------|
| `google/antigravity-gemini-3-pro` | 1M | variants: `low`, `high` | Full codebase analysis |
| `google/antigravity-gemini-3-flash` | 1M | variants: `minimal`→`high` | Fast large-context tasks |
| `google/antigravity-claude-sonnet-4-5` | 200K | — | General dev, fast quality |
| `google/antigravity-claude-sonnet-4-5-thinking` | 200K | variants: `low`, `max` | Balanced reasoning |
| `google/antigravity-claude-opus-4-5-thinking` | 200K | variants: `low`, `max` | Deep architecture work |
| `google/antigravity-claude-opus-4-6-thinking` | 200K | variants: `low`, `max` | Latest Opus, deep reasoning |
| `google/gemini-2.5-flash` | 1M | — | Gemini CLI quota fallback |
| `google/gemini-2.5-pro` | 1M | — | Gemini CLI quota fallback |

> **Note on "Cline vs OpenCode models"**: In Cline (this VSCodium extension), you have access to Claude Sonnet 4.6.
> In OpenCode (CLI tool), via Antigravity auth, you get Claude Sonnet 4.5, Opus 4.5, and Opus 4.6 — these are **different access paths** from different providers.

---

## OAuth Technical Details

### What Type of OAuth Is This?

This is **OAuth 2.0 Authorization Code flow + PKCE** (Proof Key for Code Exchange).

From Google's classification, this is the **"Installed Application / Desktop App"** type:
- No client secret needed on user side
- Uses PKCE (`code_challenge` + `code_challenge_method=S256`) for security
- Redirect URI is `http://localhost:51121/oauth-callback` (local callback server)
- The OAuth client belongs to Antigravity, not you — client_id: `1071006060591-tmhssin2h21lcre235vtolojh4g403ep`

### You Do NOT Need Google Cloud Console

**No setup required on your end.** You do not need to:
- Create a Google Cloud project
- Register an OAuth app
- Configure credentials or redirect URIs
- Choose an "OAuth type" in your Google account
- Enable any Google APIs

Antigravity's OAuth client is already registered with Google. You just sign in and click Allow.

### OAuth Scopes Requested

When you authenticate, Antigravity requests these scopes:
```
https://www.googleapis.com/auth/cloud-platform      ← GCP API access
https://www.googleapis.com/auth/userinfo.email      ← Your email
https://www.googleapis.com/auth/userinfo.profile    ← Your name/photo
https://www.googleapis.com/auth/cclog               ← Antigravity companion logging
https://www.googleapis.com/auth/experimentsandconfigs ← Antigravity feature flags
openid                                               ← Standard OpenID Connect
```

These scopes give Antigravity access to Google's internal AI Companion API (which backs the Gemini and Claude models). They do NOT give access to your Gmail, Drive, Calendar, or other personal data.

---

## Step-by-Step Auth Guide

### Prerequisites

```bash
# Ensure plugin is installed globally
npm list -g opencode-antigravity-auth 2>/dev/null || npm install -g opencode-antigravity-auth@latest

# Confirm opencode is installed
opencode --version

# Confirm plugin is in your config
grep -c "antigravity" /home/arcana-novai/Documents/xnai-foundation/.opencode/opencode.json
```

### Step 1 — Run auth

```bash
cd /home/arcana-novai/Documents/xnai-foundation
opencode auth login
```

### Step 2 — Select provider

The interactive menu will show:
```
◆  Add credential
│
◆  Select provider
│  ● OpenCode Zen (recommended)
│  ○ Anthropic
│  ○ Google
│  ...
```
→ Select **Google**

### Step 3 — Select login method

```
◆  Login method
│  ● OAuth with Google (Antigravity)
│  ○ Manually enter API Key
```
→ Select **OAuth with Google (Antigravity)**

### Step 4 — Project ID prompt

```
Project ID (leave blank to use your default project):
```

**⚠️ Important**: Press **Enter (leave blank)** UNLESS you have a Google Cloud project with Gemini API enabled.
- If you enter an arbitrary name like "xnai-foundation" it will be embedded in the auth token
- For Antigravity quota (Claude + Gemini), project ID doesn't matter — leave blank
- For Gemini CLI quota models (`gemini-2.5-pro`, `gemini-3-pro-preview`), you need a real GCP project with Gemini for Cloud API enabled, or you'll get 403 errors

### Step 5 — Open OAuth URL

The terminal will print a URL like:
```
https://accounts.google.com/o/oauth2/v2/auth?client_id=1071006060591-...
```

**Open this URL in your browser.** If the browser doesn't open automatically:
1. Copy the URL from the terminal
2. Paste into Firefox or Chrome (NOT Safari — see troubleshooting)

### Step 6 — Google consent screen

1. Sign in with your Google account if not already signed in
2. Consent screen: *"Antigravity wants to access your Google Account"*
3. Review the permissions (email, profile, cloud-platform access)
4. Click **Allow** / **Continue**

### Step 7 — Handle the callback

**Automatic (best case):**
- Browser redirects to `http://localhost:51121/oauth-callback?code=...`
- Terminal immediately shows success

**Manual (if automatic fails — localhost:51121 not reachable):**
After 30 seconds, the terminal shows:
```
⏳ Automatic callback not received after 30 seconds.
You can paste the redirect URL manually.
```

1. After clicking Allow in Google, the browser tries to load `http://localhost:51121/oauth-callback?code=...&scope=...`
2. The browser will show an error ("This site can't be reached") — **this is normal**
3. Copy the FULL URL from the browser address bar
4. Paste it into the terminal prompt

### Step 8 — Multi-account prompt

```
Add another account? (1 added) (y/n):
```

- **n** — single account (recommended for personal use)
- **y** — add a second Google account for doubled quota (run through the OAuth flow again)

### Step 9 — Verify

```bash
opencode auth status
# Shows: authenticated account(s) and email address(es)
```

---

## Using Antigravity Models

```bash
# Default model (from opencode.json "model" key)
opencode -p "your task here"

# Specific model — standard usage
opencode -m google/antigravity-claude-sonnet-4-5 -p "fix this bug"

# With thinking variant (for thinking models)
opencode run "complex architecture task" --model=google/antigravity-claude-opus-4-5-thinking --variant=max

# Gemini 3 Pro with high thinking (1M context!)
opencode run "review entire codebase" --model=google/antigravity-gemini-3-pro --variant=high

# Latest Opus with extended thinking
opencode run "design sovereign agent architecture" --model=google/antigravity-claude-opus-4-6-thinking --variant=max
```

---

## Using Local llama-cpp-python Model

The `llama-cpp-python` provider is configured in `opencode.json` and requires no auth. Start the server first:

```bash
# Terminal 1 — start llama-cpp-python OpenAI-compatible server
python -m llama_cpp.server \
  --model /path/to/your-model.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --n_ctx 32768 \
  --n_gpu_layers -1   # Use Vulkan/GPU layers if available

# Terminal 2 — use it in opencode
opencode -m llama-cpp/local -p "your task"
```

**Caddy integration:** The existing `Caddyfile` does not proxy `llama-cpp-python` — it's accessed directly at `http://localhost:8080/v1`. This is intentional: Caddy proxies the Docker stack services (RAG API, Chainlit UI, Vikunja) on port 8000, while llama-cpp-python runs as a separate local process. No Caddyfile changes needed.

If you want Caddy to proxy llama-cpp-python (e.g., for a unified port), you could add:
```caddyfile
@llama {
  path /llama/*
}
handle @llama {
  uri strip_prefix /llama
  reverse_proxy localhost:8080
}
```
But since OpenCode connects directly to `http://localhost:8080/v1`, this is unnecessary.

---

## Config Files Reference

| File | Purpose |
|------|---------|
| `.opencode/opencode.json` (project) | Provider + model definitions |
| `~/.config/opencode/opencode.json` | Global OpenCode config |
| `~/.config/opencode/antigravity-accounts.json` | Stored OAuth tokens (refresh tokens) |
| `~/.config/opencode/antigravity.json` | Optional plugin behaviour config |
| `~/.config/opencode/antigravity-logs/` | Debug logs |

> **Security note**: `antigravity-accounts.json` contains your OAuth refresh token. It is stored in your home directory, NOT in the `xnai-foundation` git repo. Never commit it.

### Quick Reset (if auth breaks)

```bash
rm ~/.config/opencode/antigravity-accounts.json
opencode auth login  # re-authenticate from scratch
```

---

## Token Lifetime & Refresh

Per Google's OAuth 2.0 documentation:
- **Access tokens**: short-lived (1 hour)
- **Refresh tokens**: long-lived, used to silently get new access tokens
- **Refresh token expiry**: Tokens expire if unused for **6 months**, or if you revoke the app in your Google account settings
- The plugin handles token refresh automatically — you don't need to re-auth manually

**When you WILL need to re-auth:**
- After 6 months of not using it
- If you revoke Antigravity's access at [myaccount.google.com/permissions](https://myaccount.google.com/permissions)
- If you delete `antigravity-accounts.json`
- Google Workspace accounts with session control policies (session may expire in 1-24 hours)

---

## Multi-Account Strategy

Run `opencode auth login` multiple times to add more Google accounts. The plugin:
- Auto-rotates between accounts when one is rate-limited
- Tracks quota per account
- Supports up to ~15-20 accounts safely (Google limit: 100 refresh tokens per OAuth client)

| Accounts | Recommended strategy |
|----------|---------------------|
| 1 account | `"account_selection_strategy": "sticky"` |
| 2–5 accounts | Default (`"hybrid"`) |
| 5+ accounts | `"account_selection_strategy": "round-robin"` |

Configure in `~/.config/opencode/antigravity.json`:
```json
{
  "$schema": "https://raw.githubusercontent.com/NoeFabris/opencode-antigravity-auth/main/assets/antigravity.schema.json",
  "account_selection_strategy": "sticky"
}
```

---

## ⚠️ Terms of Service Warning

The plugin's NPM page explicitly warns:
> Using this plugin **may violate Google's Terms of Service**. A small number of users have had their accounts **banned or shadow-banned**.
>
> **High-risk scenarios:**
> - 🚨 Fresh Google accounts have very high chance of getting banned
> - 🚨 New accounts with Pro/Ultra subscriptions are frequently flagged

**Recommendation**: Use an established personal Google account you don't rely on for critical services. Do NOT use a work/Workspace account.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Configuration is invalid` | `mcpServers` or `rules` in `opencode.json` | **Fixed** — removed in Sprint 3 |
| Auth hung, no browser opens | No default browser / headless | Copy URL, open manually in Firefox/Chrome |
| Safari "can't open page" after Allow | Safari HTTPS-only blocks `http://localhost` | Use Chrome/Firefox instead |
| Port 51121 already in use | Stale process | `lsof -i :51121` → `kill -9 <PID>` → retry |
| 403 `rising-fact-p41fc` | Used Gemini CLI model without valid GCP project | Use Antigravity models (`antigravity-*`) or add real GCP project ID |
| `Invalid function name` with MCP | MCP tool name starts with number | Rename MCP key to start with letter |
| All accounts rate-limited | Cache bug | Delete `antigravity-accounts.json`, re-auth |
| Model not found | Missing model definition in `opencode.json` | Config updated with all models in Sprint 3 |
| Token expired | Unused >6 months, or revoked | `opencode auth login` |

---

## Privacy & Sovereign Stack Compatibility

| Aspect | Detail |
|--------|--------|
| Google data shared | Email + name only (via OAuth scopes) |
| Code/prompts | Sent to Anthropic/Google via Antigravity proxy — **not air-gap compatible** |
| Token storage | `~/.config/opencode/antigravity-accounts.json` (home dir only, not in git) |
| Telemetry | Standard API call logs on Google/Anthropic servers |
| Disable completely | Remove `"plugin": ["opencode-antigravity-auth@latest"]` from `opencode.json` |
| Air-gap fallback | Use `llama-cpp/local` model — no auth, no internet, fully sovereign |

---

*Guide v2.0 — Updated after live auth session — 2026-02-18 — Claude Sonnet 4.6 (Cline)*

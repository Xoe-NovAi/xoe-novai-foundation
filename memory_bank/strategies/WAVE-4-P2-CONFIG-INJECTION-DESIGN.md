---
title: "Wave 4 Phase 2: Config File Injection System Design"
subtitle: "Provider API Credential Management Without Manual Copy/Paste"
status: draft
phase: "Wave 4 - Phase 2 Design"
created: 2026-02-23
updated: 2026-02-23
owner: "MC-Overseer"
tags: [wave-4, provider-integration, config-management, security]
---

# Wave 4 Phase 2: Config File Injection System Design

**Coordination Key**: `WAVE-4-P2-CONFIG-INJECTION-DESIGN`  
**Related**: `memory_bank/strategies/WAVE-4-PHASE-1-STATUS-REPORT.md`

---

## Problem Statement

OpenCode CLI requires manual entry of API keys via terminal UI, which is problematic because:
- Copy/paste restrictions in terminal TUI
- Manual process creates friction for multi-provider setup
- No centralized credential management
- Difficult to rotate accounts without re-entering keys
- No way to inject credentials programmatically (for automation)

**Goal**: Design a secure, programmatic system to inject provider credentials into OpenCode (and other CLIs) without manual copy/paste.

---

## Discovered Architecture

### Current OpenCode Authentication

From `.opencode/opencode.json` and `~/.local/share/opencode/auth.json`:

```yaml
# Provider Definition (opencode.json - VISIBLE)
providers:
  google:
    npm: "@ai-sdk/google"
    models:
      antigravity-gemini-3-pro:
        context: 1048576
        capabilities: [text, image, pdf]

# Auth Storage (auth.json - LOCAL, PLAINTEXT)
auth:
  google:
    apiKey: "gsk_..." # Antigravity OAuth token
    # OR
    accessToken: "ya29..." # Google OAuth token
```

### Key Findings

1. **Auth Storage**: `~/.local/share/opencode/auth.json` (plaintext JSON)
2. **Provider Definitions**: `.opencode/opencode.json` (version-controlled)
3. **Auth Methods**:
   - **OAuth** (Antigravity, Google): Browser redirect → Copy URL → Paste in CLI
   - **API Key** (OpenRouter, Together.ai, etc.): Direct key entry or env var
   - **mTLS** (enterprise): Certificate-based
4. **Environment Variables**: OpenCode reads `PROVIDER_API_KEY` pattern (needs verification)
5. **No Native Config Import**: OpenCode doesn't have `--load-config` or similar flag

---

## Design Proposal: Three-Tier Architecture

### Tier 1: Credential Storage (Local & Secure)

```yaml
# ~/.config/xnai/opencode-credentials.yaml (git-ignored, 0600 permissions)
providers:
  antigravity:
    type: oauth
    accounts:
      - email: user1@example.com
        access_token: "ya29.c...." # 1 year validity
        refresh_token: "1//..." # Refresh mechanism
        expires_at: 2027-02-23
        quota_limit: "unlimited"
        active: true
        
      - email: user2@example.com
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
```

**Security**:
- File permissions: `0600` (user-only read/write)
- Encryption: git-crypt or SOPS (optional, for repos)
- API keys: Can reference env vars instead of storing directly
- OAuth tokens: Stored locally with refresh mechanism

---

### Tier 2: Injection Script (`setup-opencode-providers.sh`)

Reads credentials config and updates OpenCode auth:

```bash
#!/bin/bash
# setup-opencode-providers.sh

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

# Main loop: For each provider in credentials
yq eval '.providers | keys' "$CREDS_FILE" | while read -r provider; do
    echo "⚙️  Injecting $provider credentials..."
    
    case "$provider" in
        antigravity)
            # Load first active account
            access_token=$(yq eval '.providers.antigravity.accounts[0].access_token' "$CREDS_FILE")
            inject_provider_auth "google" "accessToken" "$access_token"
            echo "✓ Antigravity (${access_token:0:10}...)"
            ;;
        openrouter)
            api_key=$(get_api_key "openrouter" "OPENROUTER_API_KEY")
            inject_provider_auth "openrouter" "apiKey" "$api_key"
            echo "✓ OpenRouter"
            ;;
        together)
            api_key=$(get_api_key "together" "TOGETHER_API_KEY")
            inject_provider_auth "together" "apiKey" "$api_key"
            echo "✓ Together.ai"
            ;;
        groq)
            api_key=$(get_api_key "groq" "GROQ_API_KEY")
            inject_provider_auth "groq" "apiKey" "$api_key"
            echo "✓ Groq"
            ;;
    esac
done

echo "✅ Provider injection complete!"
echo "Run: opencode --model google/antigravity-gemini-3-pro to test"
```

**Workflow**:
1. User creates `~/.config/xnai/opencode-credentials.yaml` (once)
2. User exports environment variables (or not, if using stored keys)
3. Run `setup-opencode-providers.sh`
4. Script updates `~/.local/share/opencode/auth.json`
5. OpenCode is now ready to use all providers

---

### Tier 3: Multi-Account Rotation & Quota Tracking

```yaml
# ~/.config/xnai/opencode-rotation-rules.yaml
rotation:
  enable: true
  strategy: "round-robin" # or "least-used" or "quota-aware"
  
  antigravity:
    accounts:
      - email: user1@example.com
        quota_used: 45000
        quota_total: 100000
        last_used: 2026-02-23T14:00:00Z
        
      - email: user2@example.com
        quota_used: 12000
        quota_total: 100000
        last_used: 2026-02-23T12:30:00Z
        
      - email: user3@example.com
        quota_used: 98000 # Nearly full
        quota_total: 100000
        last_used: 2026-02-22T08:00:00Z
        
    next_to_use: user2@example.com
    rotation_interval: "72h" # Rotate accounts every 3 days
    
  openrouter:
    quota_used: 2500000
    quota_total: 3500000
    percentage_used: 71%
```

**Rotation Algorithm**:
```
if next_account.quota_used >= 0.9 * quota_total:
    use_next_account = true
else if time_since_last_use >= rotation_interval:
    use_next_account = true
    
select account from candidates where quota_used <= 0.8 * quota_total
```

---

## Implementation Phases

### Phase 2A: Design & Specification (THIS PHASE)

- [x] Analyze current OpenCode auth structure
- [x] Design credential storage format
- [ ] Design injection script
- [ ] Design rotation algorithm
- [ ] Create security specifications
- [ ] Get user feedback on design

**Deliverables**:
- This document (WAVE-4-P2-CONFIG-INJECTION-DESIGN.md)
- Security requirements spec
- Script pseudo-code and templates

---

### Phase 3A: Implementation (NEXT PHASE)

- [ ] Create credential file template
- [ ] Write injection script (Bash)
- [ ] Write rotation script (Python)
- [ ] Create setup documentation
- [ ] Add environment variable defaults

**Deliverables**:
- `scripts/xnai-setup-opencode-providers.sh`
- `scripts/xnai-rotate-opencode-accounts.py`
- `config/templates/opencode-credentials.yaml.template`
- `config/templates/opencode-rotation-rules.yaml.template`

---

### Phase 4A: Testing & Validation (FINAL PHASE)

- [ ] Test credential injection with real providers
- [ ] Test multi-account rotation
- [ ] Test quota tracking
- [ ] Verify no plaintext leaks
- [ ] Performance test (injection time < 1s)

**Success Criteria**:
- User can add new provider without CLI copy/paste
- Credentials are stored securely (git-ignored)
- Rotation happens automatically
- All auth methods work (OAuth, API key, env var)

---

## Security Considerations

### Threat Model

| Threat | Risk | Mitigation |
|--------|------|-----------|
| Credentials in git history | HIGH | git-crypt, .gitignore, pre-commit hooks |
| Plaintext in memory | MEDIUM | Overwrite sensitive strings after use |
| OAuth tokens expiry | MEDIUM | Auto-refresh mechanism, fallback to email/pwd login |
| Multiple people on same machine | LOW | File permissions (0600), separate config dirs |
| Compromised keyring | HIGH | Use system keyring (libsecret, Keychain) instead of plaintext |

### Best Practices

1. **File Permissions**: `chmod 0600 ~/.config/xnai/opencode-credentials.yaml`
2. **Git Ignore**: Add to `.gitignore`:
   ```
   ~/.config/xnai/opencode-credentials.yaml
   ~/.local/share/opencode/auth.json
   OPENCODE_* env vars
   ```
3. **Keyring Integration**: Prefer system keyring over plaintext:
   ```bash
   pass insert xnai/opencode/antigravity
   # Retrieve: $(pass show xnai/opencode/antigravity)
   ```
4. **Audit Trail**: Log all credential injections (without storing keys):
   ```json
   {
     "timestamp": "2026-02-23T14:00:00Z",
     "action": "inject_provider_auth",
     "provider": "antigravity",
     "account": "user1@example.com",
     "status": "success"
   }
   ```

---

## Alternative Approaches Considered

### Option A: Environment Variables Only
- **Pros**: Simplest, most portable
- **Cons**: Doesn't scale to 8+ accounts (env var pollution)
- **Decision**: Use as fallback for single providers

### Option B: OpenCode Plugin
- **Pros**: Native integration, official support
- **Cons**: Requires OpenCode maintainer cooperation
- **Decision**: Future enhancement (if OpenCode adopts)

### Option C: Headless Mode + API Injection
- **Pros**: No CLI UI, pure programmatic
- **Cons**: OpenCode doesn't officially support headless mode
- **Decision**: Research for Phase 3 if needed

### Option D: Custom Wrapper CLI
- **Pros**: Full control, portable across tools
- **Cons**: Maintenance burden
- **Decision**: Use if config injection doesn't work (fallback)

---

## Integration with Wave 4 Strategy

### How This Enables Multi-Account Orchestration

```
Wave 4 Multi-CLI Dispatcher
    ├─ OpenCode (Tier 1: Fastest)
    │   ├─ Account Pool: 8 Antigravity accounts
    │   ├─ Models: Gemini 3 Pro (1M), Sonnet 4.5 (200K)
    │   └─ Injection: setup-opencode-providers.sh + rotation
    │
    ├─ Copilot CLI (Tier 2: Code optimization)
    │   ├─ Account Pool: 8 accounts × 50 msgs/month
    │   ├─ Models: Raptor Mini (264K context)
    │   └─ Injection: gh config + env vars
    │
    ├─ Cline (Tier 3: File operations)
    │   ├─ Account Pool: Single (multi-account TBD)
    │   └─ Injection: cline.config.json
    │
    └─ Local Fallback (Tier 4: Sovereign)
        ├─ llama-cpp (port 8080)
        └─ GGUF models (unlimited)
```

**Credential Routing**:
1. Dispatcher receives task
2. Checks task requirements (model, context, speed)
3. Selects appropriate CLI
4. Injects credentials from config
5. Executes task
6. Updates quota tracking

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Setup time (new provider) | < 2 minutes | TBD (Phase 4) |
| Credential injection time | < 1 second | TBD (Phase 4) |
| Account rotation accuracy | 100% | TBD (Phase 4) |
| Credential security audit | 0 plaintext leaks | TBD (Phase 4) |
| User documentation completeness | 100% | TBD (Phase 3) |

---

## Related Documents

- `memory_bank/ACCOUNT-REGISTRY.yaml` (provider metadata)
- `memory_bank/strategies/WAVE-4-PHASE-1-STATUS-REPORT.md` (Phase 1 findings)
- `.opencode/opencode.json` (current config structure)
- `expert-knowledge/OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md` (setup guide)

---

## Next Steps

1. **User Review**: Get feedback on this design
2. **Phase 2B**: Design multi-instance dispatch (Cline/Copilot/OpenCode)
3. **Phase 2C**: Design Raptor Mini integration strategy
4. **Phase 3**: Implement scripts and templates
5. **Phase 4**: Test and validate

---

**Status**: 🔵 DRAFT - Awaiting User Feedback  
**Last Updated**: 2026-02-23  
**Next Checkpoint**: Phase 2B Design Review

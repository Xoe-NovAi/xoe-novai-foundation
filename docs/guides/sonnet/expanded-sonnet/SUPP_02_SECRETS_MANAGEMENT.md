---
title: "Omega-Stack Supplemental Manual SUPP-02: Secrets Management & Credential Hardening"
section: "SUPP-02"
scope: "Plaintext .env rotation, SOPS+age encryption, pre-commit hooks, git-filter-repo, Podman secrets, AppArmor, API key rotation procedures"
status: "Actionable — Critical Security Remediation"
owner: "arcana-novai (UID 1000)"
last_updated: "2026-03-13"
confidence_overall: "95% (verified procedures + upstream tool docs)"
haiku_review: "Integrated — confidence matrix, git-filter-repo for history cleanup, pre-commit hooks, fallback strategies"
priority: "P1 — 5 Plaintext Secrets Identified; Rotation Required Before Any External Sharing"
---

# SUPP-02 — Secrets Management & Credential Hardening
## Omega-Stack Supplemental Implementation Manual

> **🤖 CONTEXT PRIME — READ FIRST:**
> - Five plaintext secrets in `.env` including default credentials (`changeme123`)
> - Default credentials are in every exploit dictionary — assume already compromised if exposed publicly
> - `oauth_creds.json` in `~/.gemini/` is plaintext JSON with OAuth tokens — must be mode 0600, NO ACL for UID 100999
> - Google API key was previously exposed in a GitHub commit — rotate immediately and clean git history
> - Primary tool: **SOPS + age** (no daemon required, single binary, air-gap compatible, ideal for this stack)
> - Alternative: Podman native secrets (for container-internal use, not file-based)
> - Pre-commit hooks prevent future leaks at the git layer — install these FIRST

---

## Confidence Matrix

| Claim | Confidence | Basis | Fragile If... |
|-------|-----------|-------|--------------|
| Default `changeme123` passwords are in exploit dicts | 99% | Security research consensus | Always true |
| SOPS+age works offline/air-gapped | 98% | age design principle, SOPS docs | age binary itself unavailable |
| git-filter-repo is safer than git filter-branch | 97% | git docs explicitly recommend filter-repo | BFG Repo Cleaner is alternative |
| Rotating credentials invalidates sessions | 95% | Standard auth behavior | Some services have grace periods |
| Podman secrets stored at mode 600 (not encrypted) | 90% | Podman upstream docs | Different Linux DAC configuration |
| Pre-commit hooks run before every commit | 97% | git hook mechanism | Developer bypasses with --no-verify |
| detect-secrets catches common API key patterns | 80% | detect-secrets coverage docs | Novel or custom secret formats |

---

## Table of Contents

1. [Threat Assessment & Scope](#1-threat-assessment--scope)
2. [Immediate Credential Rotation](#2-immediate-credential-rotation)
3. [Git History Cleanup — Removing Exposed Secrets](#3-git-history-cleanup--removing-exposed-secrets)
4. [Pre-commit Hooks — Prevent Future Leaks](#4-pre-commit-hooks--prevent-future-leaks)
5. [SOPS + age — Encrypted Secrets at Rest](#5-sops--age--encrypted-secrets-at-rest)
6. [Podman Native Secrets](#6-podman-native-secrets)
7. [oauth_creds.json — OAuth Token Hardening](#7-oauth_credsjson--oauth-token-hardening)
8. [API Key Rotation Procedures](#8-api-key-rotation-procedures)
9. [AppArmor Enforcement for Containers](#9-apparmor-enforcement-for-containers)
10. [Decision Tree — What to Do When Credentials Are Exposed](#10-decision-tree--what-to-do-when-credentials-are-exposed)
11. [Fallback Strategies](#11-fallback-strategies)
12. [Verification Checklist](#12-verification-checklist)

---

## 1. Threat Assessment & Scope

### 1.1 Known Exposure Inventory

| Secret | Location | Current State | Risk | Action |
|--------|---------|---------------|------|--------|
| PostgreSQL password | `.env` | `changeme123` (default!) | 🔴 CRITICAL | Rotate immediately |
| Redis auth token | `.env` | `changeme123` (default!) | 🔴 CRITICAL | Rotate immediately |
| API keys (×3) | `.env` | Hardcoded strings | 🔴 HIGH | Rotate + encrypt |
| OAuth tokens | `~/.gemini/oauth_creds.json` | Plaintext JSON | 🟠 HIGH | Secure permissions |
| Google API key | git history | Previously committed | 🔴 CRITICAL | Rotate + clean history |
| Database URLs | docker-compose env | Connection strings | 🟡 MEDIUM | Reference encrypted .env |

### 1.2 Blast Radius Assessment

```
If .env is exposed:
  → All database services accessible (postgres, redis, mariadb)
  → All API integrations compromised (GitHub, search, SambaNova)
  → Complete data exfiltration possible

If oauth_creds.json is exposed:
  → Gemini CLI sessions compromised
  → All facet sessions can be hijacked
  → .gemini/credentials/ may be accessible if attacker gets the token

If git history contains secrets (Google API key incident):
  → Anyone who cloned the repo has the secret
  → Key must be revoked AND history cleaned (cleaning alone is insufficient)
```

---

## 2. Immediate Credential Rotation

> **🔴 DO THIS FIRST.** Encryption is useless if the credentials being encrypted are already compromised. Rotate before encrypting.

### 2.1 Generate Secure Passwords

```bash
#!/usr/bin/env bash
# Generate cryptographically secure passwords
gen_pass() { openssl rand -base64 40 | tr -d '/+=' | head -c 32; echo; }

echo "=== NEW OMEGA-STACK CREDENTIALS ==="
echo "(COPY THESE BEFORE RUNNING ROTATION SCRIPTS)"
echo ""
printf "POSTGRES_PASSWORD=%s\n" "$(gen_pass)"
printf "REDIS_PASSWORD=%s\n" "$(gen_pass)"
printf "MARIADB_ROOT_PASSWORD=%s\n" "$(gen_pass)"
printf "MARIADB_PASSWORD=%s\n" "$(gen_pass)"
printf "VIKUNJA_SECRET=%s\n" "$(gen_pass)"
printf "GRAFANA_ADMIN_PASSWORD=%s\n" "$(gen_pass)"
echo ""
echo "Save these in a password manager before proceeding."
echo "You will need them for the rotation steps below."
```

### 2.2 Rotate PostgreSQL Password

```bash
#!/usr/bin/env bash
# Interactive rotation — paste new password when prompted
read -r -p "New PostgreSQL password: " -s NEW_PG_PASS
echo ""

# Step 1: Apply in PostgreSQL
podman exec postgres psql -U postgres -c "ALTER USER postgres WITH PASSWORD '${NEW_PG_PASS}';" && \
  echo "✅ PostgreSQL password changed in database"

# Step 2: Update .env
sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${NEW_PG_PASS}/" \
  ~/Documents/Xoe-NovAi/omega-stack/.env && \
  echo "✅ .env updated"

# Step 3: Restart dependent services (they read .env on startup)
for SVC in rag_api librarian memory-bank-mcp oikos xnai-gnosis; do
  podman restart "$SVC" 2>/dev/null && echo "  Restarted: $SVC"
done

# Step 4: Verify
podman exec postgres psql -U postgres -c "SELECT version();" &>/dev/null && \
  echo "✅ PostgreSQL connection verified with new password" || \
  echo "❌ Connection failed — check password update"
```

### 2.3 Rotate Redis Password

```bash
#!/usr/bin/env bash
read -r -p "New Redis password: " -s NEW_REDIS_PASS
echo ""

# Hot reload in Redis (no restart needed)
podman exec redis redis-cli -a "$(grep REDIS_PASSWORD ~/Documents/Xoe-NovAi/omega-stack/.env | cut -d= -f2)" \
  CONFIG SET requirepass "$NEW_REDIS_PASS" 2>/dev/null || \
  podman exec redis redis-cli CONFIG SET requirepass "$NEW_REDIS_PASS"

# Verify new password works
podman exec redis redis-cli -a "$NEW_REDIS_PASS" PING && echo "✅ Redis auth with new password"

# Update .env
sed -i "s/^REDIS_PASSWORD=.*/REDIS_PASSWORD=${NEW_REDIS_PASS}/" \
  ~/Documents/Xoe-NovAi/omega-stack/.env

# Restart Redis clients (they cache the old password)
for SVC in rag_api xnai-memory xnai-rag xnai-agentbus memory-bank-mcp; do
  podman restart "$SVC" 2>/dev/null && echo "  Restarted: $SVC"
done
```

### 2.4 Verify No Default Passwords Remain

```bash
# Scan for any remaining default credentials
echo "=== DEFAULT PASSWORD SCAN ==="
grep -i "changeme\|password123\|admin123\|secret123\|default\|test123" \
  ~/Documents/Xoe-NovAi/omega-stack/.env 2>/dev/null && \
  echo "❌ Default passwords still present — rotate above" || \
  echo "✅ No default passwords detected"
```

---

## 3. Git History Cleanup — Removing Exposed Secrets

> **⚠️ CRITICAL WARNING:**
> Cleaning git history is DESTRUCTIVE and affects all collaborators. Everyone who has cloned the repo must re-clone after this operation. The exposed secret MUST be revoked regardless — history cleaning only removes the evidence, not the exposure risk.

### 3.1 Audit What Was Committed

```bash
#!/usr/bin/env bash
OMEGA=~/Documents/Xoe-NovAi/omega-stack
echo "=== GIT SECRET AUDIT ==="

echo ".env in history:"
git -C "$OMEGA" log --all --full-history --oneline -- ".env" 2>/dev/null | head -10

echo ""
echo "*.pem or *.key files in history:"
git -C "$OMEGA" log --all --full-history --oneline -- "*.pem" "*.key" 2>/dev/null | head -10

echo ""
echo "oauth_creds.json in history:"
git -C "$OMEGA" log --all --full-history --oneline -- "*.json" 2>/dev/null | \
  grep -i cred | head -5

echo ""
echo ".env.* files:"
git -C "$OMEGA" log --all --full-history --oneline -- ".env.*" 2>/dev/null | head -5

echo ""
echo "Searching for API key patterns in all commits (slow):"
git -C "$OMEGA" log --all --format='%H' 2>/dev/null | head -50 | while read HASH; do
  git -C "$OMEGA" show "$HASH" 2>/dev/null | grep -iE "(api_key|apikey|secret|password)\s*[=:]\s*['\"][a-zA-Z0-9]{20,}" | head -2 | \
    while read LINE; do echo "  Found in $HASH: ${LINE:0:60}..."; done
done
```

### 3.2 Clean History with git-filter-repo (Recommended)

```bash
#!/usr/bin/env bash
OMEGA=~/Documents/Xoe-NovAi/omega-stack
echo "=== GIT HISTORY CLEANUP WITH git-filter-repo ==="
echo ""
echo "⚠️  This will rewrite git history and force-push."
echo "⚠️  ALL collaborators must re-clone after this."
echo "⚠️  The exposed credential MUST be revoked even after cleaning."
echo ""
echo "Type 'CLEAN_HISTORY' to proceed:"
read -r CONFIRM
[ "$CONFIRM" = "CLEAN_HISTORY" ] || { echo "Aborted"; exit 0; }

# Install git-filter-repo
pip install git-filter-repo --break-system-packages 2>/dev/null || \
  pip install git-filter-repo 2>/dev/null || \
  { echo "Install manually: https://github.com/newren/git-filter-repo/releases"; exit 1; }

cd "$OMEGA"

# Create fresh backup before cleaning
BACKUP_DIR="/media/arcana-novai/omega_vault/git_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
git bundle create "${BACKUP_DIR}/omega-stack-before-clean.bundle" --all
echo "✅ Backup created: ${BACKUP_DIR}/omega-stack-before-clean.bundle"

# Remove .env from all history
echo "Removing .env from history..."
git filter-repo --path .env --invert-paths --force
echo "✅ .env removed from history"

# Remove private key files
echo "Removing *.pem and *.key files..."
git filter-repo --path-glob '*.pem' --path-glob '*.key' --invert-paths --force
echo "✅ Key files removed from history"

# Remove oauth_creds.json if it was committed
echo "Removing oauth_creds.json if present..."
git filter-repo --path-glob '*oauth_creds*' --invert-paths --force 2>/dev/null || true

# Update .gitignore to prevent re-commit
cat >> .gitignore << 'GITIGNORE'

# Secrets — must never be committed
.env
.env.*
!.env.example
!.env.encrypted
*.pem
*.key
id_rsa
id_ed25519
oauth_creds.json
credentials/
keys/
.secrets.baseline
GITIGNORE

git add .gitignore && git commit -m "security: enforce .gitignore for secrets"

echo ""
echo "=== NEXT STEPS ==="
echo "1. Force push: git push origin --force --all"
echo "2. Notify all collaborators to re-clone (their copies have the old history)"
echo "3. Revoke the exposed credential (if not done already):"
echo "   - Google API key: https://console.cloud.google.com/apis/credentials"
echo "   - GitHub tokens: https://github.com/settings/tokens"
echo "4. Rotate all other credentials in .env (see §2)"
```

### 3.3 Alternative: BFG Repo Cleaner (Faster for Large Repos)

```bash
# BFG is faster than git-filter-repo for simple deletion cases
# Use if git-filter-repo is unavailable or repo is very large (>1GB history)

# Install BFG
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar -O /tmp/bfg.jar
# Requires Java: sudo apt install default-jre

# Create bare clone backup
git clone --bare ~/Documents/Xoe-NovAi/omega-stack /tmp/omega-stack-mirror.git

# Remove files
java -jar /tmp/bfg.jar --delete-files .env /tmp/omega-stack-mirror.git
java -jar /tmp/bfg.jar --delete-files '*.pem' /tmp/omega-stack-mirror.git

# Apply changes
cd /tmp/omega-stack-mirror.git
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

---

## 4. Pre-commit Hooks — Prevent Future Leaks

Install these BEFORE making any more commits. They block secrets at the git layer, even before they enter history.

### 4.1 Installation

```bash
cd ~/Documents/Xoe-NovAi/omega-stack/

# Install pre-commit framework
pip install pre-commit detect-secrets --break-system-packages 2>/dev/null || \
  pip install pre-commit detect-secrets

# Create configuration
cat > .pre-commit-config.yaml << 'EOF'
repos:
  # detect-secrets: catches common API key patterns, high-entropy strings
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: '\.enc$|\.encrypted$'

  # Standard file checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=2000']
      - id: check-merge-conflict
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-yaml
      - id: check-json

  # Local custom hooks
  - repo: local
    hooks:
      - id: block-dotenv
        name: Block .env files from commits
        entry: bash -c 'FILES=$(git diff --cached --name-only); echo "$FILES" | grep -qE "^\.env$|^\.env\.[^e]" && { echo "ERROR: Refusing to commit .env file. Use .env.encrypted instead."; exit 1; } || exit 0'
        language: system
        always_run: true
        pass_filenames: false

      - id: block-private-keys
        name: Block private key files
        entry: bash -c 'FILES=$(git diff --cached --name-only); echo "$FILES" | grep -qE "private\.pem|\.key$|id_rsa|id_ed25519" && { echo "ERROR: Private key file detected. Never commit private keys."; exit 1; } || exit 0'
        language: system
        always_run: true
        pass_filenames: false

      - id: block-default-passwords
        name: Block default passwords
        entry: bash -c 'git diff --cached | grep -qiE "(changeme|password123|admin123|secret123)" && { echo "ERROR: Default password pattern detected in staged changes."; exit 1; } || exit 0'
        language: system
        always_run: true
        pass_filenames: false

      - id: block-oauth-creds
        name: Block OAuth credentials files
        entry: bash -c 'FILES=$(git diff --cached --name-only); echo "$FILES" | grep -q "oauth_creds" && { echo "ERROR: Never commit OAuth credentials. This file contains live tokens."; exit 1; } || exit 0'
        language: system
        always_run: true
        pass_filenames: false
EOF

# Create baseline for detect-secrets (marks known acceptable items)
detect-secrets scan \
  --exclude-files '\.enc$' \
  --exclude-files '\.encrypted$' \
  --exclude-files 'node_modules' \
  > .secrets.baseline 2>/dev/null || \
  echo '{"plugins_used": [], "results": {}, "generated_at": "", "version": "1.4.0"}' > .secrets.baseline

# Install hooks into .git/hooks/
pre-commit install
pre-commit install --hook-type commit-msg

echo "✅ Pre-commit hooks installed"
echo "Test: echo 'POSTGRES_PASSWORD=changeme123' > test.env && git add test.env && git commit -m 'test' && rm test.env"
```

### 4.2 Testing the Hooks

```bash
# Test that the hooks actually block secrets
cd ~/Documents/Xoe-NovAi/omega-stack/

echo "Testing default password detection..."
echo "SECRET_KEY=changeme123" > /tmp/test_secret
cp /tmp/test_secret test_file.txt
git add test_file.txt
git commit -m "test" 2>&1 | grep -q "ERROR\|Blocked\|default password" && \
  echo "✅ Default password hook works" || echo "⚠️  Hook may not be working"
git restore --staged test_file.txt && rm -f test_file.txt

echo ""
echo "Testing .env block..."
echo "DB_PASS=supersecret" > .env.test_hook
git add .env.test_hook
git commit -m "test env" 2>&1 | grep -q "ERROR\|Refused" && \
  echo "✅ .env block hook works" || echo "⚠️  .env hook may not be blocking"
git restore --staged .env.test_hook && rm -f .env.test_hook
```

---

## 5. SOPS + age — Encrypted Secrets at Rest

SOPS (Secrets OPerationS) encrypts specific fields in YAML/JSON/dotenv files using age public-key cryptography. The encrypted file is safe to commit. Decryption requires your private age key.

### 5.1 Installation

```bash
# Install age
sudo apt install age 2>/dev/null || {
  # Manual install
  AGE_VERSION=$(curl -s https://api.github.com/repos/FiloSottile/age/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
  curl -LO "https://github.com/FiloSottile/age/releases/download/${AGE_VERSION}/age-${AGE_VERSION}-linux-amd64.tar.gz"
  tar xf age-${AGE_VERSION}-linux-amd64.tar.gz
  sudo mv age/age age/age-keygen /usr/local/bin/
  rm -rf age age-${AGE_VERSION}-linux-amd64.tar.gz
}

# Install SOPS
SOPS_VERSION=$(curl -s https://api.github.com/repos/getsops/sops/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
curl -LO "https://github.com/getsops/sops/releases/download/${SOPS_VERSION}/sops-${SOPS_VERSION}.linux.amd64"
sudo install -m 755 "sops-${SOPS_VERSION}.linux.amd64" /usr/local/bin/sops
rm "sops-${SOPS_VERSION}.linux.amd64"

# Verify
age --version && sops --version && echo "✅ SOPS + age installed"
```

### 5.2 Generate age Encryption Key

```bash
# Generate your encryption keypair
AGE_KEY_DIR=~/.config/sops/age
mkdir -p "$AGE_KEY_DIR"
age-keygen -o "${AGE_KEY_DIR}/keys.txt"

# Restrict private key access
chmod 600 "${AGE_KEY_DIR}/keys.txt"

# Display public key (needed for .sops.yaml)
AGE_PUBLIC_KEY=$(grep 'public key' "${AGE_KEY_DIR}/keys.txt" | awk '{print $NF}')
echo "Your age public key: $AGE_PUBLIC_KEY"
echo ""
echo "CRITICAL: Back up ${AGE_KEY_DIR}/keys.txt to omega_vault NOW"
echo "  cp ${AGE_KEY_DIR}/keys.txt /media/arcana-novai/omega_vault/secrets/age_key_backup_$(date +%Y%m%d).txt"
mkdir -p /media/arcana-novai/omega_vault/secrets/ 2>/dev/null || true
cp "${AGE_KEY_DIR}/keys.txt" "/media/arcana-novai/omega_vault/secrets/age_key_backup_$(date +%Y%m%d).txt" 2>/dev/null && \
  echo "✅ Key backed up to vault" || echo "⚠️  Vault not mounted — back up key manually"
```

### 5.3 Configure SOPS

```bash
# Create .sops.yaml in the repo root
AGE_PUBLIC_KEY=$(grep 'public key' ~/.config/sops/age/keys.txt | awk '{print $NF}')

cat > ~/Documents/Xoe-NovAi/omega-stack/.sops.yaml << SOPSEOF
creation_rules:
  - path_regex: \.env\.encrypted$
    age: ${AGE_PUBLIC_KEY}
  - path_regex: secrets/.*\.yaml$
    age: ${AGE_PUBLIC_KEY}
  - path_regex: \.env\.secrets$
    age: ${AGE_PUBLIC_KEY}
SOPSEOF

echo "✅ .sops.yaml created with your age public key"
```

### 5.4 Encrypt the .env File

```bash
cd ~/Documents/Xoe-NovAi/omega-stack/

# Create .env.example (safe to commit — no real values)
python3 -c "
with open('.env') as f:
    lines = f.readlines()
with open('.env.example', 'w') as f:
    for line in lines:
        if '=' in line and not line.startswith('#'):
            key = line.split('=')[0]
            f.write(f'{key}=CHANGE_ME\n')
        else:
            f.write(line)
print('✅ .env.example created (no real values)')
"

# Encrypt .env with SOPS
SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt \
  sops --encrypt .env > .env.encrypted

# Verify encryption worked
head -5 .env.encrypted  # Should show encrypted gibberish, not real values

# Test decryption
SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt \
  sops --decrypt .env.encrypted | head -3

# Commit encrypted version, NOT plaintext
git add .env.encrypted .env.example .sops.yaml
git commit -m "security: add SOPS-encrypted credentials"
echo "✅ Encrypted .env.encrypted committed"
echo "✅ .env (plaintext) remains local only — excluded by .gitignore"
```

### 5.5 Runtime Decryption

```bash
#!/usr/bin/env bash
# Decrypt for use with podman-compose
# ~/omega-stack/scripts/start_with_encrypted_env.sh

decrypt_env() {
  local ENCRYPTED="${1:-$(pwd)/.env.encrypted}"
  local TMPFILE
  TMPFILE=$(mktemp /tmp/omega_env_XXXXXX)
  chmod 600 "$TMPFILE"

  SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt \
    sops --decrypt "$ENCRYPTED" > "$TMPFILE" || {
    echo "❌ Decryption failed — check: SOPS_AGE_KEY_FILE is correct"
    rm -f "$TMPFILE"
    return 1
  }

  echo "$TMPFILE"
}

# Usage:
ENV_FILE=$(decrypt_env)
trap "rm -f $ENV_FILE" EXIT  # Auto-cleanup on script exit
podman-compose --env-file "$ENV_FILE" up -d
```

---

## 6. Podman Native Secrets

For container-internal secret access without file mounts:

```bash
# Create secrets from current .env values
create_podman_secret() {
  local NAME="$1" VALUE="$2"
  echo -n "$VALUE" | podman secret create "$NAME" - 2>/dev/null && \
    echo "✅ Secret created: $NAME" || \
    echo "⚠️  Secret $NAME may already exist (rm first: podman secret rm $NAME)"
}

# Extract from .env and create Podman secrets
PG_PASS=$(grep POSTGRES_PASSWORD ~/Documents/Xoe-NovAi/omega-stack/.env | cut -d= -f2)
REDIS_PASS=$(grep REDIS_PASSWORD ~/Documents/Xoe-NovAi/omega-stack/.env | cut -d= -f2)

create_podman_secret "postgres_password" "$PG_PASS"
create_podman_secret "redis_password" "$REDIS_PASS"

# List all secrets (values are never shown)
podman secret ls

# Use in docker-compose.yml:
# services:
#   postgres:
#     secrets:
#       - postgres_password
#     environment:
#       POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
#
# secrets:
#   postgres_password:
#     external: true
#     name: postgres_password
```

> **📝 NOTE — Podman Secrets Storage:**
> Podman secrets are stored in `~/.local/share/containers/storage/secrets/`. They are protected by the user's file permissions (mode 600) but are NOT encrypted at rest. For encryption at rest, use SOPS (§5) or a hardware key. For this single-node home lab, Podman secrets + SOPS is the recommended combination.

---

## 7. oauth_creds.json — OAuth Token Hardening

```bash
#!/usr/bin/env bash
echo "=== OAUTH CREDENTIALS HARDENING ==="

CREDS_FILES=(
  ~/.gemini/oauth_creds.json
  ~/Documents/Xoe-NovAi/omega-stack/.gemini/oauth_creds.json
)

for CREDS in "${CREDS_FILES[@]}"; do
  if [ -f "$CREDS" ]; then
    # Set restrictive permissions
    chmod 600 "$CREDS"

    # Remove ALL ACLs (containers must NOT access OAuth tokens)
    setfacl -b "$CREDS" 2>/dev/null && echo "✅ ACLs removed from $CREDS" || true

    # Verify permissions
    MODE=$(stat -c '%a' "$CREDS")
    ACLS=$(getfacl -p "$CREDS" 2>/dev/null | grep -v '^#\|^user::\|^group::\|^other::\|^$' | wc -l)
    echo "  Mode: $MODE (expected: 600)"
    echo "  Extra ACLs: $ACLS (expected: 0)"
    [ "$MODE" = "600" ] && [ "$ACLS" -eq 0 ] && echo "  ✅ oauth_creds.json properly secured" || \
      echo "  ❌ Security issue — fix above"

    # Check token expiry without exposing values
    python3 -c "
import json, time, os
with open('$CREDS') as f:
    creds = json.load(f)

# Check for expiry fields
for key in ['expiry', 'expires_at', 'expiry_date', 'exp']:
    if key in creds:
        val = creds[key]
        if isinstance(val, (int, float)):
            remaining = val - time.time()
            if remaining > 0:
                print(f'  Token valid for: {remaining/3600:.1f} hours')
            else:
                print(f'  ⚠️  Token EXPIRED {abs(remaining)/3600:.1f} hours ago — re-authenticate')
        else:
            print(f'  Expiry: {val}')
        break
else:
    print('  No expiry field (long-lived token)')

# Confirm token field present without exposing value
for key in ['access_token', 'token', 'id_token', 'refresh_token']:
    if key in creds:
        print(f'  Token type present: {key}')
        break
" 2>/dev/null
  fi
done

# Ensure oauth_creds.json is in .gitignore
grep -q "oauth_creds" ~/Documents/Xoe-NovAi/omega-stack/.gitignore 2>/dev/null && \
  echo "✅ oauth_creds.json in .gitignore" || {
  echo "oauth_creds.json" >> ~/Documents/Xoe-NovAi/omega-stack/.gitignore
  echo "✅ Added oauth_creds.json to .gitignore"
}
```

---

## 8. API Key Rotation Procedures

### 8.1 Rotation Audit

```bash
#!/usr/bin/env bash
echo "=== API KEY AUDIT ==="
# Find all API keys in .env without exposing values
grep -iE '^(api_key|apikey|secret|token|key|auth).*=' \
  ~/Documents/Xoe-NovAi/omega-stack/.env 2>/dev/null | \
  sed 's/=.*/=<REDACTED>/' | sort

echo ""
echo "For each key above: check if it appears in git history"
git -C ~/Documents/Xoe-NovAi/omega-stack log --all --format="%H" 2>/dev/null | head -100 | \
  xargs -I{} git show {} 2>/dev/null | \
  grep -iE "(api_key|apikey)\s*[=:]\s*['\"][a-zA-Z0-9_-]{20,}" | \
  sed 's/[a-zA-Z0-9_-]\{8\}[a-zA-Z0-9_-]*/[REDACTED]/g' | head -10
```

### 8.2 Google API Key Rotation (Addressing Haiku-Reported Incident)

```bash
echo "=== GOOGLE API KEY ROTATION PROCEDURE ==="
echo ""
echo "1. Revoke the exposed key:"
echo "   → https://console.cloud.google.com/apis/credentials"
echo "   → Find the exposed key → Delete or Revoke"
echo ""
echo "2. Generate a new key:"
echo "   → Create credentials → API key"
echo "   → Restrict to specific APIs (do NOT use unrestricted keys)"
echo "   → Set application restrictions (HTTP referrers or IP)"
echo ""
echo "3. Update .env:"
echo "   sed -i 's/^GEMINI_API_KEY=.*/GEMINI_API_KEY=new_key_here/' .env"
echo "   OR: Use SOPS encryption (§5) for all future changes"
echo ""
echo "4. Clean git history (§3) to remove the old key"
echo ""
echo "5. Verify new key works:"
curl -sf "https://generativelanguage.googleapis.com/v1/models?key=$(grep GEMINI_API_KEY .env | cut -d= -f2)" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print('✅ API key valid' if 'models' in d else '❌ Invalid key')" 2>/dev/null
```

### 8.3 GitHub Token Rotation

```bash
echo "Rotate GitHub token:"
echo "  → https://github.com/settings/tokens"
echo "  → Revoke old token → Generate new → Fine-grained (preferred over classic)"
echo "  → Required scopes: repo (for code), issues, pull_requests"
echo ""
echo "Update in .env:"
read -r -p "New GitHub token: " -s NEW_GH_TOKEN
echo ""
sed -i "s/^GITHUB_TOKEN=.*/GITHUB_TOKEN=${NEW_GH_TOKEN}/" \
  ~/Documents/Xoe-NovAi/omega-stack/.env
podman restart xnai-github 2>/dev/null && echo "✅ xnai-github restarted with new token"
```

---

## 9. AppArmor Enforcement for Containers

> **📝 NOTE:** Ubuntu 25.10 uses AppArmor (NOT SELinux). The `:Z` volume flag in Podman is for SELinux only — it has no effect on AppArmor systems.

```bash
# Check current AppArmor state
sudo aa-status 2>/dev/null | grep -E 'enforce|complain|unconfined' | head -5

# Podman automatically creates AppArmor profiles for containers
# Check what profiles are generated
sudo aa-status 2>/dev/null | grep podman | head -10

# Gradual enforcement strategy (recommended over immediate)
# Phase 1: 30 days in complain mode (logs but doesn't block)
sudo aa-complain /usr/bin/podman 2>/dev/null || true

# Monitor for denials
sudo journalctl -k --since "today" | grep DENIED | tail -10
# If no denials after 30 days → safe to enforce

# Phase 2: Enable enforcement
# sudo aa-enforce /usr/bin/podman

# Container-specific hardening
# Prevent specific capabilities in docker-compose.yml:
# security_opt:
#   - no-new-privileges:true
# cap_drop:
#   - ALL
# cap_add:
#   - NET_BIND_SERVICE  # Only if needed for port binding
```

---

## 10. Decision Tree — What to Do When Credentials Are Exposed

```
INCIDENT: Credentials have been or may have been exposed
══════════════════════════════════════════════════════════════════

STEP 1: Determine scope of exposure
  Was the credential committed to git?
  ├─ YES → It's PUBLIC regardless of repo visibility
  │         Action: REVOKE immediately (§8), then clean history (§3)
  └─ NO  →
      Was the .env file readable to other users?
      ├─ YES → Check who accessed: last -x | grep arcana-novai
      └─ NO  → May be contained to local system

STEP 2: Revoke FIRST, rotate second
  Always revoke the credential at the provider (GitHub, Google, etc.)
  BEFORE rotating — revocation closes the breach immediately
  Rotation without revocation: old key still works during migration

STEP 3: Rotate affected credentials
  → §2 for database passwords
  → §8 for API keys
  → §7 for OAuth tokens

STEP 4: Clean git history if committed
  → §3 git-filter-repo procedure
  → Notify all collaborators to re-clone

STEP 5: Prevent recurrence
  → §4 pre-commit hooks
  → §5 SOPS encryption
  → Update .gitignore

STEP 6: Audit access logs
  → sudo journalctl | grep "auth\|fail" | tail -50
  → Check if any containers accessed files they shouldn't have
  → Review AppArmor denials: sudo journalctl -k | grep DENIED

Recovery confidence: 95% for pure local exposure
Recovery confidence: 80% for git-committed (key may have been scraped)
Recovery confidence: 60% for public repo exposure (assume key is used)
```

---

## 11. Fallback Strategies

### 11.1 SOPS Decryption Fails (Key Not Found)

**Trigger:** `Error: no master key found in this encrypted file` or `Error: could not decrypt`

```bash
# Check key file exists
ls -la ~/.config/sops/age/keys.txt
# If missing: restore from vault backup
ls /media/arcana-novai/omega_vault/secrets/age_key_backup_*.txt
cp /media/arcana-novai/omega_vault/secrets/age_key_backup_YYYYMMDD.txt ~/.config/sops/age/keys.txt
chmod 600 ~/.config/sops/age/keys.txt

# Try decryption with explicit key file
SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt sops --decrypt .env.encrypted

# If key is lost permanently:
# Fallback to plaintext .env (in emergency) and re-encrypt with new key
echo "⚠️  If key is permanently lost: re-rotate all credentials and start fresh"
```

### 11.2 detect-secrets Triggers on Valid Content

**Trigger:** Pre-commit blocks a commit that doesn't actually contain secrets.

```bash
# Update the baseline to mark known-safe items as acceptable
cd ~/Documents/Xoe-NovAi/omega-stack/
detect-secrets scan --baseline .secrets.baseline  # Update baseline

# Or for a specific file, mark as false positive in baseline
# (edit .secrets.baseline JSON manually and add to the "results" array)

# Emergency bypass (use sparingly — creates audit trail)
git commit --no-verify -m "chore: bypass hooks for [REASON]"
# Document the reason in the commit message always
```

### 11.3 git-filter-repo Fails Mid-Process

```bash
# If filter-repo fails partway through:
# Restore from the bundle backup created in §3.2
cd ~/Documents/Xoe-NovAi/
git clone /media/arcana-novai/omega_vault/git_backup_*/omega-stack-before-clean.bundle omega-stack-restored
cd omega-stack-restored
# Re-attempt filter-repo from clean state
```

---

## 12. Verification Checklist

```bash
#!/usr/bin/env bash
echo "=== SUPP-02 SECRETS MANAGEMENT VERIFICATION ==="
PASS=0; FAIL=0; WARN=0
ok()   { echo "  ✅ $1"; PASS=$((PASS+1)); }
fail() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }
warn() { echo "  ⚠️  $1"; WARN=$((WARN+1)); }

OMEGA=~/Documents/Xoe-NovAi/omega-stack

# Default passwords
grep -q 'changeme' "${OMEGA}/.env" 2>/dev/null && fail "Default passwords still in .env" || ok "No default passwords in .env"

# .env in .gitignore
grep -q '^\\.env$\|^\.env$' "${OMEGA}/.gitignore" 2>/dev/null && ok ".env excluded from git" || fail ".env NOT in .gitignore"

# .env not in git history
GIT_ENV=$(git -C "$OMEGA" log --all --full-history -- ".env" 2>/dev/null | wc -l)
[ "$GIT_ENV" -eq 0 ] && ok ".env not in git history" || fail ".env in git history ($GIT_ENV commits) — run §3"

# Private keys not in git history
GIT_KEYS=$(git -C "$OMEGA" log --all --full-history -- "*.pem" "*.key" 2>/dev/null | wc -l)
[ "$GIT_KEYS" -eq 0 ] && ok "No private keys in git history" || fail "Keys in git history — run §3"

# SOPS encryption
[ -f "${OMEGA}/.env.encrypted" ] && ok ".env.encrypted exists (SOPS encrypted)" || warn ".env.encrypted missing — run §5"
[ -f "${OMEGA}/.sops.yaml" ] && ok ".sops.yaml configured" || warn ".sops.yaml missing — run §5.3"
[ -f ~/.config/sops/age/keys.txt ] && ok "age encryption key present" || warn "age key not found — run §5.2"

# oauth_creds.json
OAUTH_MODE=$(stat -c '%a' ~/.gemini/oauth_creds.json 2>/dev/null || echo "missing")
[ "$OAUTH_MODE" = "600" ] && ok "oauth_creds.json: mode 600" || fail "oauth_creds.json mode: ${OAUTH_MODE} (need 600)"
OAUTH_ACLS=$(getfacl ~/.gemini/oauth_creds.json 2>/dev/null | grep -v '^#\|^user::\|^group::\|^other::\|^$' | wc -l)
[ "$OAUTH_ACLS" -eq 0 ] && ok "oauth_creds.json: no extra ACLs" || fail "oauth_creds.json has ACLs (containers can read tokens)"

# credentials/ directory
CRED_MODE=$(stat -c '%a' ~/.gemini/credentials/ 2>/dev/null || echo "missing")
[ "$CRED_MODE" = "700" ] && ok "credentials/: mode 700" || fail "credentials/ mode: ${CRED_MODE}"

# Pre-commit hooks
[ -f "${OMEGA}/.pre-commit-config.yaml" ] && ok "pre-commit config exists" || warn ".pre-commit-config.yaml missing — run §4"
[ -f "${OMEGA}/.git/hooks/pre-commit" ] && ok "pre-commit hooks installed" || warn "pre-commit hooks not installed: cd $OMEGA && pre-commit install"

# age key backup
ls /media/arcana-novai/omega_vault/secrets/age_key_backup_*.txt &>/dev/null && \
  ok "age key backed up to vault" || warn "age key NOT backed up to vault — CRITICAL if key is lost"

# Podman secrets
SECRET_COUNT=$(podman secret ls 2>/dev/null | wc -l)
[ "$SECRET_COUNT" -gt 1 ] && ok "Podman secrets configured ($SECRET_COUNT)" || warn "No Podman secrets configured — run §6"

echo ""
printf "Results: ✅ %d pass  ❌ %d fail  ⚠️  %d warn\n" "$PASS" "$FAIL" "$WARN"
[ "$FAIL" -gt 0 ] && echo "❌ Critical security issues require immediate attention"
[ "$FAIL" -eq 0 ] && [ "$WARN" -eq 0 ] && echo "✅ Secrets management hardened"
```

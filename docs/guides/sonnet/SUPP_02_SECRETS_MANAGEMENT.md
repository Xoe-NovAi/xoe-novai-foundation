---
title: "Omega-Stack Supplemental Manual SUPP-02: Secrets Management & Credential Hardening"
section: "SUPP-02"
scope: "Plaintext .env, Vault integration, Credential rotation, AppArmor"
status: "Actionable — Critical Security Remediation"
owner: "arcana-novai (UID 1000)"
last_updated: "2026-03-13"
gemini_review: "Integrated"
confidence: "97%"
priority: "P1 — 5 Plaintext Secrets Identified; Immediate Rotation Required"
---

# SUPP-02 — Secrets Management & Credential Hardening
## Omega-Stack Supplemental Implementation Manual

> **🤖 AGENT DIRECTIVE:** Five plaintext secrets have been identified in the `.env` file including default credentials (`changeme123`). If the repository is ever compromised, all services are immediately accessible. This manual provides a zero-downtime migration from plaintext `.env` to encrypted secrets management using **SOPS + age** (lightweight, no daemon required, ideal for a single-node stack).

---

## Table of Contents

1. [Threat Assessment](#1-threat-assessment)
2. [Immediate Credential Rotation](#2-immediate-credential-rotation)
3. [SOPS + age Encrypted Secrets](#3-sops--age-encrypted-secrets)
4. [Podman Secrets Integration](#4-podman-secrets-integration)
5. [oauth_creds.json Protection](#5-oauth_credsjson-protection)
6. [API Key Rotation Procedures](#6-api-key-rotation-procedures)
7. [git-secrets — Prevent Future Leaks](#7-git-secrets--prevent-future-leaks)
8. [AppArmor Enforcement for Containers](#8-apparmor-enforcement-for-containers)
9. [Edge Cases & Failure Modes](#9-edge-cases--failure-modes)
10. [Verification Checklist](#10-verification-checklist)

---

## 1. Threat Assessment

| Secret | Location | Current State | Risk Level |
|--------|---------|---------------|------------|
| PostgreSQL password | `.env` | `changeme123` (default!) | 🔴 CRITICAL |
| Redis auth token | `.env` | `changeme123` (default!) | 🔴 CRITICAL |
| API keys (×3) | `.env` | Hardcoded strings | 🔴 HIGH |
| OAuth tokens | `.gemini/oauth_creds.json` | Plaintext JSON | 🟠 HIGH |
| Database URLs | `docker-compose.yml` env | Connection strings | 🟡 MEDIUM |

> **🔴 CRITICAL CALLOUT:**  
> Default credentials like `changeme123` are in every exploit dictionary and automated scan toolkit. If any container in the stack has a vulnerability and is exploited, an attacker has the database password **without needing to crack anything**. Rotate ALL default passwords before any other work except the P0 storage crisis.

---

## 2. Immediate Credential Rotation

### 2.1 Generate Strong Passwords

```bash
#!/usr/bin/env bash
# Generate cryptographically random passwords for all services
gen_pass() { openssl rand -base64 32 | tr -d '/+=' | head -c 32; }

echo "=== NEW OMEGA-STACK CREDENTIALS ==="
echo "POSTGRES_PASSWORD=$(gen_pass)"
echo "POSTGRES_REPL_PASSWORD=$(gen_pass)"
echo "REDIS_PASSWORD=$(gen_pass)"
echo "MARIADB_ROOT_PASSWORD=$(gen_pass)"
echo "MARIADB_PASSWORD=$(gen_pass)"
echo "VIKUNJA_SECRET=$(gen_pass)"
echo "GRAFANA_ADMIN_PASSWORD=$(gen_pass)"
echo ""
echo "SAVE THESE SECURELY BEFORE PROCEEDING."
echo "You will need them for each service rotation below."
```

### 2.2 Rotate PostgreSQL Password

```bash
# Step 1: Generate new password
NEW_PG_PASS=$(openssl rand -base64 32 | tr -d '/+=')
echo "New PG password (save this): $NEW_PG_PASS"

# Step 2: Update PostgreSQL
podman exec postgres psql -U postgres -c "ALTER USER postgres PASSWORD '${NEW_PG_PASS}';"

# Step 3: Update .env
sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${NEW_PG_PASS}/" \
  ~/Documents/Xoe-NovAi/omega-stack/.env

# Step 4: Restart dependent services
podman restart rag_api librarian memory-bank-mcp

# Step 5: Verify
podman exec postgres psql -U postgres -c "SELECT 1;" && echo "✅ PG connection OK"
```

### 2.3 Rotate Redis Password

```bash
NEW_REDIS_PASS=$(openssl rand -base64 32 | tr -d '/+=')

# Update Redis config (hot reload)
podman exec redis redis-cli CONFIG SET requirepass "$NEW_REDIS_PASS"
podman exec redis redis-cli -a "$NEW_REDIS_PASS" PING

# Update .env
sed -i "s/^REDIS_PASSWORD=.*/REDIS_PASSWORD=${NEW_REDIS_PASS}/" \
  ~/Documents/Xoe-NovAi/omega-stack/.env

# Restart dependent services (Redis clients need re-auth)
podman restart rag_api xnai-memory xnai-rag
```

---

## 3. SOPS + age Encrypted Secrets

SOPS (Secrets OPerationS) encrypts specific fields in YAML/JSON/dotenv files using age keys. The encrypted file can be safely committed to git. Decryption only works with your private age key.

### 3.1 Installation

```bash
# Install age
sudo apt install age

# Install sops
SOPS_VERSION=$(curl -s https://api.github.com/repos/mozilla/sops/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
curl -LO "https://github.com/getsops/sops/releases/download/${SOPS_VERSION}/sops-${SOPS_VERSION}.linux.amd64"
chmod +x "sops-${SOPS_VERSION}.linux.amd64"
sudo mv "sops-${SOPS_VERSION}.linux.amd64" /usr/local/bin/sops

# Verify
sops --version
age --version
```

### 3.2 Generate age Key

```bash
# Generate your encryption key
age-keygen -o ~/.config/sops/age/keys.txt

# Display the public key — you'll need this for .sops.yaml
AGE_PUBLIC_KEY=$(grep 'public key' ~/.config/sops/age/keys.txt | awk '{print $NF}')
echo "Your age public key: $AGE_PUBLIC_KEY"

# Restrict private key access
chmod 600 ~/.config/sops/age/keys.txt
```

### 3.3 Configure SOPS

```bash
cat > ~/Documents/Xoe-NovAi/omega-stack/.sops.yaml << EOF
creation_rules:
  - path_regex: \.env\.encrypted$
    age: ${AGE_PUBLIC_KEY}
  - path_regex: secrets/.*\.yaml$
    age: ${AGE_PUBLIC_KEY}
EOF
```

### 3.4 Encrypt the .env File

```bash
cd ~/Documents/Xoe-NovAi/omega-stack/

# Create clean .env.example (no real values — safe to commit)
cp .env .env.example
sed -i 's/=.*/=CHANGE_ME/' .env.example

# Encrypt .env with SOPS
SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt \
  sops --encrypt .env > .env.encrypted

# Verify encryption
cat .env.encrypted  # Should show encrypted values

# Remove plaintext .env from git tracking
echo ".env" >> .gitignore
git rm --cached .env 2>/dev/null || true
git add .env.encrypted .env.example .gitignore
```

### 3.5 Decrypt at Runtime

```bash
# Decrypt to temporary file for podman-compose
decrypt_env() {
  SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt \
    sops --decrypt ~/Documents/Xoe-NovAi/omega-stack/.env.encrypted > /tmp/omega_env_$$
  chmod 600 /tmp/omega_env_$$
  echo "/tmp/omega_env_$$"
}

# Use in startup:
ENV_FILE=$(decrypt_env)
podman-compose --env-file "$ENV_FILE" up -d
rm -f "$ENV_FILE"  # Clean up decrypted file immediately
```

---

## 4. Podman Secrets Integration

Podman has a native secrets manager that stores secrets in the user's data directory with proper permissions.

```bash
# Create Podman secrets from your .env values
podman secret create postgres_password - <<< "$(grep POSTGRES_PASSWORD .env | cut -d= -f2)"
podman secret create redis_password - <<< "$(grep REDIS_PASSWORD .env | cut -d= -f2)"

# List secrets (values are never shown)
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

> **📝 AGENT NOTE — Podman Secret Storage:**  
> Podman secrets are stored in `~/.local/share/containers/storage/secrets/`. These are protected by the user's file permissions (600) but are NOT encrypted at rest. For encryption at rest, use SOPS (Section 3) or a hardware key. For most single-node home lab deployments, Podman secrets + SOPS is sufficient.

---

## 5. oauth_creds.json Protection

```bash
# The OAuth credentials file is plaintext JSON in .gemini
# It should NEVER be readable by non-owner processes

# Set restrictive permissions
chmod 600 ~/.gemini/oauth_creds.json 2>/dev/null || true
chmod 600 ~/Documents/Xoe-NovAi/omega-stack/.gemini/oauth_creds.json 2>/dev/null || true

# Verify
ls -la ~/.gemini/oauth_creds.json
# Expected: -rw------- 1 arcana-novai arcana-novai

# Add to .gitignore
echo ".gemini/oauth_creds.json" >> ~/Documents/Xoe-NovAi/omega-stack/.gitignore
echo ".gemini/credentials/" >> ~/Documents/Xoe-NovAi/omega-stack/.gitignore

# Check if already committed (this would be a breach)
git -C ~/Documents/Xoe-NovAi/omega-stack/ log --all --full-history -- .gemini/oauth_creds.json
# If output shows commits: the file was committed. Rotate ALL OAuth tokens immediately.
```

---

## 6. API Key Rotation Procedures

### 6.1 Rotation Checklist

For each API key found in `.env`:

```bash
# Find all API keys in .env
grep -iE '(api_key|secret|token|password|auth)' ~/Documents/Xoe-NovAi/omega-stack/.env | \
  sed 's/=.*/=REDACTED/'

# For each key:
# 1. Generate new key in the provider's dashboard
# 2. Update .env FIRST
# 3. Restart affected service
# 4. Revoke old key in provider dashboard
# 5. Verify service still works
```

### 6.2 Automated Key Audit

```bash
#!/usr/bin/env bash
# Scan for exposed credentials across the repository
REPO=~/Documents/Xoe-NovAi/omega-stack/

echo "=== CREDENTIAL AUDIT ==="
echo ""
echo "Files with potential secrets (excluding .gitignore patterns):"
grep -rn --include="*.yml" --include="*.yaml" --include="*.json" --include="*.env" \
  -iE '(password|api_key|secret|token|credential).*[=:]\s*[^$\{<"][^$\{<"]{8,}' \
  "$REPO" \
  --exclude-dir=".git" \
  --exclude="*.example" \
  --exclude="*.encrypted" 2>/dev/null | head -30

echo ""
echo "Git history credential scan (last 50 commits):"
git -C "$REPO" log --all --pretty=format:"%H" -50 | while read HASH; do
  git -C "$REPO" show "$HASH" --stat 2>/dev/null | grep -iE '(\.env|secret|cred)' && echo "  In commit: $HASH"
done
```

---

## 7. git-secrets — Prevent Future Leaks

```bash
# Install git-secrets
sudo apt install git-secrets 2>/dev/null || \
  (cd /tmp && git clone https://github.com/awslabs/git-secrets && cd git-secrets && sudo make install)

# Configure for the omega-stack repository
cd ~/Documents/Xoe-NovAi/omega-stack/
git secrets --install
git secrets --register-aws  # Catches AWS patterns

# Add custom patterns for common defaults
git secrets --add 'changeme123'
git secrets --add 'password.*=.*[a-z0-9]{8,}'

# Test that it blocks commits with secrets
echo "TEST_SECRET=changeme123" > /tmp/test_secret.env
git secrets --scan /tmp/test_secret.env && echo "❌ Did not detect secret" || echo "✅ Secret detected correctly"
rm /tmp/test_secret.env
```

---

## 8. AppArmor Enforcement for Containers

> **📝 AGENT NOTE:**  
> The current AppArmor configuration is in **permissive mode** — it logs violations but does not block them. Enabling enforcement provides Mandatory Access Control (MAC) for containers, preventing container escapes even if the seccomp profile is bypassed.

### 8.1 Check Current AppArmor State

```bash
sudo aa-status | head -20
# Look for: "0 profiles are in enforce mode" (currently permissive)

# Check Podman's auto-generated profiles
sudo aa-status | grep podman
```

### 8.2 Enable AppArmor for Podman (Gradual Approach)

```bash
# Step 1: Review the auto-generated profile in complain mode first (30 days)
sudo aa-complain /usr/bin/podman 2>/dev/null || true

# Step 2: Generate profile from logs
sudo aa-logprof  # Interactive — review each denied operation

# Step 3: After 30 days of complain mode without issues, enforce
sudo aa-enforce /usr/bin/podman

# Monitor AppArmor denials
sudo journalctl -k | grep DENIED | tail -20
```

### 8.3 Container-Specific AppArmor Profile

```bash
# Create a custom profile for high-risk containers (qdrant, rag_api)
sudo tee /etc/apparmor.d/omega-container-restricted << 'EOF'
#include <tunables/global>

profile omega-container-restricted flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  # Allow read access to mounted volumes
  /home/arcana-novai/Documents/Xoe-NovAi/omega-stack/.gemini/** r,

  # Deny write to sensitive paths
  deny /etc/passwd w,
  deny /etc/shadow w,
  deny /proc/sysrq-trigger w,
  deny @{PROC}/** w,

  # Network
  network inet stream,
  network inet6 stream,
}
EOF
sudo apparmor_parser -r /etc/apparmor.d/omega-container-restricted
```

---

## 9. Edge Cases & Failure Modes

| Scenario | Resolution |
|----------|-----------|
| SOPS decryption fails (key not found) | `export SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt` and retry |
| Podman secret unavailable in container | Verify `--secret` flag used; check `podman secret ls` |
| OAuth token expires after rotation | Re-authenticate each tool individually; tokens are per-tool |
| git history contains credentials | Use `git filter-repo` to purge; rotate ALL exposed credentials |
| AppArmor enforcement blocks container | Check `journalctl -k | grep DENIED`; add rule to profile; reload |

---

## 10. Verification Checklist

```bash
#!/usr/bin/env bash
echo "=== SUPP-02 SECRETS MANAGEMENT VERIFICATION ==="

# No default passwords
! grep -q 'changeme' ~/Documents/Xoe-NovAi/omega-stack/.env 2>/dev/null && \
  echo "✅ No default passwords in .env" || echo "❌ Default passwords still present"

# .env in .gitignore
grep -q '^\.env$' ~/Documents/Xoe-NovAi/omega-stack/.gitignore 2>/dev/null && \
  echo "✅ .env in .gitignore" || echo "❌ .env NOT in .gitignore"

# oauth_creds.json permissions
[ "$(stat -c '%a' ~/.gemini/oauth_creds.json 2>/dev/null)" = "600" ] && \
  echo "✅ oauth_creds.json is mode 600" || echo "⚠️ oauth_creds.json permissions incorrect"

# SOPS encryption exists
[ -f ~/Documents/Xoe-NovAi/omega-stack/.env.encrypted ] && \
  echo "✅ Encrypted .env exists" || echo "❌ No encrypted .env — plaintext only"

# git-secrets installed
command -v git-secrets &>/dev/null && \
  echo "✅ git-secrets installed" || echo "❌ git-secrets not installed"

echo "=== END VERIFICATION ==="
```

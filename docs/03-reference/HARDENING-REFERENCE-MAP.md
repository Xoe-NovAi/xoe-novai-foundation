---
document_type: reference
title: "Hardening Implementation Reference Map"
created_by: "Copilot (223556219+Copilot@users.noreply.github.com)"
created_date: 2026-03-15
version: 1.0
status: active
category: security
priority: P0
tags: [hardening, reference, files, config, validation]
---

# Hardening Reference Map: Files, Config Sections, Health Checks

**Purpose**: Quick lookup for hardening implementation locations, configuration sections, and health check commands.

---

## Layer 1: Permission System - File Locations

### Critical Paths (Must Have Correct Ownership & ACLs)

| Path | Purpose | Criticality | Owner Should Be | Layer 1 Tier |
|------|---------|------------|-----------------|-------------|
| `~/.gemini/` | Gemini CLI home | P0 | 1000:1000 | 1, 2 |
| `~/.gemini/memory_bank/` | Persistent memory | P0 | 1000:1000 | 1, 2 |
| `~/Documents/Xoe-NovAi/omega-stack/.gemini/` | Stack config | P0 | 1000:1000 | 1, 2 |
| `~/Documents/Xoe-NovAi/omega-stack/.logs/` | App logs | P1 | 1000:1000 | 1, 2 |
| `~/Documents/Xoe-NovAi/omega-stack/.venv_mcp/` | Python venv | P1 | 1000:1000 | 1, 2 |
| `~/Documents/Xoe-NovAi/omega-stack/mcp-servers/` | MCP configs | P1 | 1000:1000 | 1, 2 |
| `~/Documents/Xoe-NovAi/omega-stack/storage/instances/*/gemini-cli/.gemini/` | Instance config | P2 | 1000:1000 | 1, 2 |
| `~/Documents/Xoe-NovAi/omega-stack/storage/instances-active/*/gemini-cli/.gemini/` | Active instance | P2 | 1000:1000 | 1, 2 |

### Systemd Timer Files (Tier 4: Auto-Healing)

| File | Location | Purpose | Status |
|------|----------|---------|--------|
| `omega-permissions-heal.service` | `/etc/systemd/system/` | Service unit for healing script | ⚠️ Deploy |
| `omega-permissions-heal.timer` | `/etc/systemd/system/` | Timer unit (runs daily) | ⚠️ Deploy |
| `omega-permissions-heal.sh` | `/usr/local/bin/` | Healing script | ⚠️ Deploy |

### Setup Commands (Tier 1-4)

```bash
# Tier 1: Ownership Restoration
sudo chown -R 1000:1000 ~/.gemini
sudo chown -R 1000:1000 ~/Documents/Xoe-NovAi/omega-stack/.gemini
sudo chown -R 1000:1000 ~/Documents/Xoe-NovAi/omega-stack/.logs

# Tier 2: Default ACLs
sudo setfacl -R -d -m u:1000:rwx ~/.gemini
sudo setfacl -R -d -m g:1000:rwx ~/.gemini

# Tier 3: Container Config (in docker-compose.yml)
userns_mode: 'keep-id'

# Tier 4: Deploy systemd timer
sudo systemctl enable omega-permissions-heal.timer
sudo systemctl start omega-permissions-heal.timer
```

---

## Layer 2: Boundary Isolation - Configuration

### Docker Compose Security Settings

**File**: `/infra/docker/docker-compose.yml`

```yaml
# RAG Service Hardening
rag:
  image: localhost/xnai-rag:latest
  init: true  # Reap zombies, handle signals
  user: "100999:100999"  # Non-root (SHOULD BE: 1000:1000 with userns_mode)
  userns_mode: 'keep-id'  # MISSING - ADD THIS
  deploy:
    resources:
      limits:
        memory: 1.5G  # Hard limit
        cpus: '2.0'   # CPU throttling
  security_opt:
    - no-new-privileges:true  # Prevent capability escalation via SUID
  cap_drop:
    - ALL  # Drop all capabilities
  cap_add:
    - NET_BIND_SERVICE  # Only if service needs to bind ports <1024

# Redis Hardening
redis:
  image: redis:7.4.1
  user: "1000:1000"
  userns_mode: 'keep-id'
  deploy:
    resources:
      limits:
        memory: 512M
        cpus: '0.5'
  cap_drop:
    - ALL

# PostgreSQL Hardening
postgres:
  image: postgres:15
  user: "1000:1000"
  userns_mode: 'keep-id'
  deploy:
    resources:
      limits:
        memory: 1.0G
        cpus: '1.0'
  cap_drop:
    - ALL
```

### Config Section Reference

**File**: `/config/config.toml`

| Section | Lines | Purpose | Hardening Relevant |
|---------|-------|---------|------------------|
| `[metadata]` | 15-20 | Stack identity | - |
| `[project]` | 25-31 | Core settings | ✅ `telemetry_enabled = false`, `privacy_mode = "local-only"` |
| `[models]` | 36-46 | LLM specs | - |
| `[performance]` | 49-79 | Resource limits | ✅ `memory_limit_bytes`, `memory_warning_threshold_bytes` |
| `[security]` | 80-100 (estimated) | Security settings | ✅ Should define MFA, token expiry, rate limits |
| `[iam]` | 101-120 (estimated) | IAM config | ✅ JWT settings, MFA issuer, password policy |
| `[redis]` | 121-135 (estimated) | Redis config | ✅ TLS settings, password, maxmemory |
| ... | ... | ... | ... |

**Key Hardening Settings in config.toml**:
```toml
[project]
telemetry_enabled = false           # No external data leakage
privacy_mode = "local-only"         # Data sovereignty
data_sovereignty = true             # Local-only storage

[performance]
memory_limit_bytes = 6442450944     # 6.0 GB (Layer 2)
memory_warning_threshold_bytes = 5905580032  # 5.5 GB
memory_critical_threshold_bytes = 6227702579  # 5.8 GB
```

### Memory Management (zRAM & Compression)

**Status**: Not explicitly configured in current codebase

**Recommendation for 6.6GB hardware**:
```bash
# Enable zRAM (compressed RAM) to extend available memory
# Add to /etc/rc.local or systemd service

# Create 2GB zram device
modprobe zram
echo 2G > /sys/block/zram0/disksize
mkswap /dev/zram0
swapon /dev/zram0 -p 32767  # Priority: higher = use before disk swap

# Verify
zramctl
free -h  # Should show additional swap
```

---

## Layer 3: Network Security - Configuration

### TLS/SSL Certificates

**File**: `/infra/docker/tls/`

```
tls/
├── ca.crt           # Root CA (distributed to clients)
├── ca.key           # Root CA private key (KEEP SECURE)
├── redis.crt        # Redis server certificate
├── redis.key        # Redis private key
└── server.crt       # Optional client certificate
```

### Redis TLS Configuration

**File**: `/infra/docker/docker-compose.yml` (lines 38-74)

```yaml
redis:
  command: >
    redis-server
    --tls-port 6379
    --tls-cert-file /tls/redis.crt
    --tls-key-file /tls/redis.key
    --tls-ca-cert-file /tls/ca.crt
    --tls-auth-clients no
  volumes:
    - ./tls:/tls:ro,Z
```

**Health Check**:
```bash
redis-cli --tls --cacert /infra/docker/tls/ca.crt -a "$REDIS_PASSWORD" ping
# Expected: PONG
```

### Caddy HTTP Security Headers

**File**: `/config/Caddyfile` (or `/infra/docker/Caddyfile`)

```caddyfile
:8000 {
  header {
    Strict-Transport-Security "max-age=31536000; includeSubDomains"
    X-Content-Type-Options "nosniff"
    X-Frame-Options "DENY"
    X-XSS-Protection "1; mode=block"
    Referrer-Policy "strict-origin-when-cross-origin"
  }

  # Route definitions with X-Real-IP header for audit logging
  handle /xnai/api/v1/* {
    reverse_proxy xnai_rag_api:8002 {
      header_up X-Real-IP {remote_host}
    }
  }
}
```

### IAM Service Configuration

**File**: `/app/XNAi_rag_app/core/iam_service.py` (lines 44-80)

```python
class IAMConfig:
    # JWT settings
    JWT_ALGORITHM = "RS256"  # Asymmetric signature
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    # MFA settings
    MFA_ENABLED = os.getenv("MFA_ENABLED", "true").lower() == "true"
    MFA_ISSUER = "Xoe-NovAi"

    # Database
    DB_PATH = os.getenv("IAM_DB_PATH", "storage/data/iam.db")
    WAL_CHECKPOINT_INTERVAL_MINUTES = 5

    # Password policy
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_SPECIAL_CHARS = True
    REQUIRE_NUMBERS = True
```

---

## Layer 4: Data Protection - Configuration

### Content Sanitization

**File**: `/app/XNAi_rag_app/core/security/sanitization.py`

| Pattern | Regex | Purpose | Example |
|---------|-------|---------|---------|
| `api_key` | Matches API key patterns | Remove API keys | `api_key="sk_1234..."` |
| `aws_key` | `AKIA[0-9A-Z]{16}` | AWS credentials | `AKIAJ7K3V2L4Q5R6S7T8` |
| `github_token` | `gh[pousr]_[a-zA-Z0-9_]{36,}` | GitHub tokens | `ghp_1234567890...` |
| `db_password` | `password.*[:=].*` | Database passwords | `password="secret123"` |
| `email` | Standard email regex | PII removal | `user@example.com` |
| `ssn` | `\d{3}-\d{2}-\d{4}` | SSN removal | `123-45-6789` |
| `credit_card` | 16-digit with separators | Payment card detection | `4111-1111-1111-1111` |
| `phone` | US phone format | Phone number removal | `(555) 123-4567` |

**Sanitization Levels**:
- `strict`: All PII removed
- `standard`: Credentials removed, PII flagged (default)
- `permissive`: Credentials only

**Audit Log**: `logs/sanitization_audit.jsonl`

### Knowledge Access Control

**File**: `/app/XNAi_rag_app/core/security/knowledge_access.py`

**Operation Types**:
```python
KnowledgeOperation.READ        # knowledge:read
KnowledgeOperation.QUERY       # knowledge:query
KnowledgeOperation.SEARCH      # knowledge:search
KnowledgeOperation.WRITE       # knowledge:write
KnowledgeOperation.INGEST      # knowledge:ingest
KnowledgeOperation.UPDATE      # knowledge:update
KnowledgeOperation.DELETE      # knowledge:delete
KnowledgeOperation.ADMIN       # knowledge:admin
```

**Permission Levels**:
```python
KnowledgePermission.NONE       # No access
KnowledgePermission.READ_ONLY  # Query only
KnowledgePermission.READ_WRITE # Query + ingest
KnowledgePermission.ADMIN      # Full control
```

**Audit Log**: `logs/knowledge_access_audit.jsonl`

**Usage Pattern**:
```python
@app.post("/xnai/api/v1/knowledge/query")
@require_knowledge_access(KnowledgeOperation.QUERY, "xnai_knowledge", "rag")
async def query_knowledge(query: QueryRequest, agent_context: AgentContext):
    # Access verified before this point
    return await rag_service.query(query)
```

### Phylax Knowledge Guardian

**File**: `/app/XNAi_rag_app/core/security/phylax.py`

**Sensitivity Classification**:
```python
SENSITIVITY_LEVELS = {
    'PUBLIC': 0,      # Searchable by all
    'INTERNAL': 1,    # Organization members
    'SENSITIVE': 2,   # Specific teams
    'RESTRICTED': 3   # Admin + owner only
}
```

**Classification Triggers**:
- Contains API key → RESTRICTED
- Contains credential → RESTRICTED
- Contains PII (email, SSN, phone) → SENSITIVE
- Default → INTERNAL

---

## Health Check Commands (Validation)

### Layer 1: Permission System

```bash
# Check ownership
stat -c '%U:%G (UID:%u:%g)' ~/.gemini
# Expected: arcana-novai arcana-novai (UID:1000:1000)

# Check ACLs
getfacl ~/.gemini | grep "default:user:1000"
# Expected: Shows default:user:1000:rwx

# Test new file ownership
touch ~/.gemini/test.txt
stat -c '%U:%G' ~/.gemini/test.txt
# Expected: arcana-novai arcana-novai (inherited via ACL)

# Check systemd timer status
sudo systemctl list-timers omega-permissions-heal.timer
# Expected: Timer active, next run scheduled

# View timer logs
sudo journalctl -u omega-permissions-heal.service -n 20
```

### Layer 2: Boundary Isolation

```bash
# Check container memory limits
podman inspect xnai_rag_api | grep -A2 '"Memory"'
# Expected: Memory: 1610612736 (1.5GB in bytes)

# Check no-new-privileges
podman inspect xnai_rag_api | grep -i 'no-new-privileges'
# Expected: Should show true

# Check capabilities
podman inspect xnai_rag_api | grep -A10 '"CapAdd"'
podman inspect xnai_rag_api | grep -A10 '"CapDrop"'
# Expected: CapDrop has ["ALL"] or most capabilities

# Test resource limits (cause memory exhaustion)
podman exec xnai_rag_api python -c "x = [0]*10**8; print(len(x))"
# Expected: Should hit memory limit gracefully, not crash host

# Check container userns mode
podman inspect xnai_rag_api | grep -i 'UsernsMode'
# Expected: "keep-id" or "host" (currently shows default)
```

### Layer 3: Network Security

```bash
# Test Redis TLS connection
redis-cli --tls --cacert /infra/docker/tls/ca.crt \
  -h redis.internal -p 6379 \
  -a "$REDIS_PASSWORD" ping
# Expected: PONG

# Verify Redis rejects unencrypted connections
redis-cli -h redis.internal -p 6379 ping
# Expected: Connection timeout or "Error: Protocol error" (6379 is TLS only)

# Check Caddy security headers
curl -I http://localhost:8000/chat
# Expected: 
# Strict-Transport-Security: max-age=31536000; includeSubDomains
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY

# Verify IAM token
curl -X POST http://localhost:8000/xnai/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
# Expected: JSON response with access_token (RS256 JWT)

# Decode JWT (check claims)
echo "eyJhbGciOiJSUzI1NiI..." | jq -R 'split(".") | .[1] | @base64d | fromjson'
# Expected: Shows exp, sub, roles, mfa_verified claims

# Test rate limiting (future)
for i in {1..20}; do curl -s http://localhost:8000/xnai/api/v1/query & done; wait
# Expected: Some requests return 429 (Too Many Requests)
```

### Layer 4: Data Protection

```bash
# Test sanitization
curl -X POST http://localhost:8000/xnai/api/v1/knowledge/ingest \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"content":"API Key: sk_1234567890abcdef","level":"standard"}'
# Expected: Response shows "API Key: [REDACTED_API_KEY]"

# Check sanitization audit log
tail logs/sanitization_audit.jsonl
# Expected: JSON entries with timestamp, agent_did, patterns_found

# Test knowledge access denial
curl -X POST http://localhost:8000/xnai/api/v1/knowledge/query \
  -H "Authorization: Bearer $UNAUTHORIZED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"..."}'
# Expected: 403 Forbidden with "AccessDeniedError" message

# Check knowledge access audit
tail logs/knowledge_access_audit.jsonl
# Expected: Entries with operation, result (ALLOWED/DENIED), decision_reason

# Verify Phylax classification
curl -X GET http://localhost:8000/xnai/api/v1/knowledge/meta/sensitive_count \
  -H "Authorization: Bearer $ADMIN_TOKEN"
# Expected: JSON with count of RESTRICTED and SENSITIVE knowledge

# View Phylax logs
ls -la logs/phylax_classification.jsonl 2>/dev/null || echo "Not yet generated"
```

---

## Metrics & Monitoring

### Key Metrics to Track

| Metric | Source | Frequency | Alert Threshold |
|--------|--------|-----------|-----------------|
| **Permission Regressions** | `/var/log/omega-permissions-heal.log` | Daily | Any CORRECTING lines |
| **Failed Knowledge Access** | `logs/knowledge_access_audit.jsonl` | Real-time | >5% DENIED rate |
| **PII Detected** | `logs/sanitization_audit.jsonl` | Real-time | Any high-risk patterns |
| **Unencrypted Connections** | Caddy logs | Real-time | Any non-HTTPS requests |
| **JWT Token Failures** | IAM logs | Real-time | >1% signature failures |
| **Container Memory Usage** | `podman stats` | Every 60s | >80% of limit |
| **Container Restart Count** | `podman inspect` | Every 5min | >2 restarts/hour |

### Grafana Dashboards (Future)

**Potential Dashboard Panels**:
1. Permission System Health (ownership %, ACL compliance)
2. Container Resource Usage (memory, CPU by service)
3. Network Security (TLS connections, failed auth attempts)
4. Data Protection Metrics (sanitization hits, access denials)

---

## Troubleshooting Quick Reference

### Problem: "Permission denied" on .gemini files

**Check**:
```bash
stat -c '%U:%G' ~/.gemini  # Should be 1000:1000
getfacl ~/.gemini | grep default:user  # Should have ACL entries
```

**Fix**:
```bash
sudo chown -R 1000:1000 ~/.gemini
sudo setfacl -R -d -m u:1000:rwx ~/.gemini
```

### Problem: Container crashes with OOMKilled

**Check**:
```bash
podman inspect xnai_rag_api | grep Memory  # Check limit
journalctl -u docker.service | grep OOM  # Check system logs
```

**Fix**: Increase memory limit in docker-compose.yml, or add zRAM.

### Problem: Redis TLS connection fails

**Check**:
```bash
redis-cli --tls --cacert /infra/docker/tls/ca.crt ping  # Test connection
openssl x509 -in /infra/docker/tls/redis.crt -noout -dates  # Check cert validity
```

**Fix**: Regenerate certificates if expired, verify CA is distributed to clients.

### Problem: Knowledge access audit log not recording

**Check**:
```bash
ls -la logs/knowledge_access_audit.jsonl  # File exists?
grep DENIED logs/knowledge_access_audit.jsonl | wc -l  # Has entries?
```

**Fix**: Ensure `@require_knowledge_access` decorator is applied to endpoints, audit logging is enabled.

---

## Configuration Quick Links

| Component | File | Section | Key Settings |
|-----------|------|---------|---------------|
| Docker Security | `/infra/docker/docker-compose.yml` | services.*.deploy | memory, cpus, no-new-privileges, cap_drop |
| Redis TLS | `/infra/docker/docker-compose.yml` | services.redis.command | tls-cert, tls-key, tls-ca-cert |
| Caddy Headers | `/config/Caddyfile` | :8000 {} | HSTS, X-Frame-Options, X-Content-Type-Options |
| IAM Config | `/app/XNAi_rag_app/core/iam_service.py` | class IAMConfig | JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE |
| Sanitization | `/app/XNAi_rag_app/core/security/sanitization.py` | PATTERNS dict | API key, AWS, GitHub, password patterns |
| Knowledge Access | `/app/XNAi_rag_app/core/security/knowledge_access.py` | class KnowledgeAccessController | verify_access, audit_log |
| Resource Limits | `/config/config.toml` | [performance] | memory_limit_bytes, memory_warning_threshold |

---

## Deployment Checklist

- [ ] Layer 1 Tier 1-3 applied: `stat ~/.gemini`, `getfacl ~/.gemini`, `podman inspect`
- [ ] Layer 1 Tier 4 deployed: `sudo systemctl status omega-permissions-heal.timer`
- [ ] Layer 2 settings verified: Memory limits, no-new-privileges, cap_drop
- [ ] Layer 3 certificates generated: `ls /infra/docker/tls/`
- [ ] Layer 3 headers verified: `curl -I http://localhost:8000`
- [ ] Layer 4 audit logs exist: `tail logs/knowledge_access_audit.jsonl`
- [ ] All health checks pass: Run validation commands above
- [ ] Monthly monitoring scheduled: Set calendar reminder for health check script

---

**Last Updated**: 2026-03-15 | **Next Review**: 2026-06-15

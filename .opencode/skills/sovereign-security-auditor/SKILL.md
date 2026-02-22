# Sovereign Security Auditor Skill

## Purpose
Ensure all changes meet security standards before commit/deployment.

## Trigger
- Before git commit
- Pre-deployment
- Security-sensitive file changes

## Security Checklist

### Container Security
- [ ] Rootless containers (`USER 1001`)
- [ ] Volume mounts use `:z` or `:Z,U`
- [ ] No hardcoded secrets
- [ ] Non-root user in Dockerfiles

### Code Security
- [ ] No secrets in code
- [ ] Input validation present
- [ ] No SQL injection vectors
- [ ] Proper error handling (no stack traces exposed)

### Network Security
- [ ] No external API calls (sovereign)
- [ ] TLS where applicable
- [ ] Proper CORS configuration
- [ ] Rate limiting implemented

### Data Security
- [ ] No PII in logs
- [ ] Encrypted sensitive data
- [ ] Proper access controls
- [ ] Audit trail maintained

## Audit Workflow

### Step 1: File Scan
Identify security-sensitive files:
- `*.env*` - Blocked
- `*secret*` - Blocked
- `*.key` - Blocked
- `*.pem` - Blocked
- `Dockerfile*` - Check user
- `podman-compose*.yaml` - Check volumes

### Step 2: Code Analysis
Scan for:
- Hardcoded credentials
- Insecure dependencies
- Unsafe deserialization
- Command injection

### Step 3: Permission Check
```bash
ls -la sensitive_files/
# Verify 600 for secrets, 644 for configs
```

### Step 4: Container Audit
```bash
podman inspect container_name --format '{{.Config.User}}'
# Should be non-root (1001)
```

### Step 5: Generate Report
```
## Security Audit Report
Date: [timestamp]
Status: [PASS/FAIL/WARN]

### Passed Checks
- [x] Rootless containers
- [x] No hardcoded secrets

### Warnings
- [!] File permissions on X

### Failures
- [ ] Missing input validation in Y

### Recommendation
[BLOCK/PROCEED/FIX_REQUIRED]
```

## Ma'at Ideals Integration
Verify changes align with:
- **Truth**: No deceptive code
- **Justice**: Fair access controls
- **Compassion**: Privacy protection
- **Sovereignty**: No external telemetry
- **Wisdom**: Secure defaults

## Automated Checks
Run via pre-commit hooks:
```bash
# .git/hooks/pre-commit
#!/bin/bash
opencode run sovereign-security-auditor
```

## Integration
- Works with `phase-validator` for phase transitions
- Notifies `agent-bus-coordinator` of security alerts
- Updates `memory_bank/activeContext.md` with security status

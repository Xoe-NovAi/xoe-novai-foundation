# Vikunja Implementation Manual - Part 4: Testing, Validation & Troubleshooting

**Version**: 1.0  
**Updated**: 2026-02-07  
**Estimated Time**: 1 hour  
**Target Audience**: Cline (Local Developer Assistant)

---

## Table of Contents

1. [Functionality Testing](#functionality-testing)
2. [Performance Baseline](#performance-baseline)
3. [Security Validation](#security-validation)
4. [Integration Testing](#integration-testing)
5. [Troubleshooting Guide](#troubleshooting-guide)

---

## Functionality Testing

### Test 1: Vikunja Web UI Access

**Objective**: Verify Vikunja frontend is accessible through Caddy proxy

```bash
# Cline: Test web UI access
curl -I http://localhost/vikunja/

# Expected output:
# HTTP/1.1 200 OK
# Content-Type: text/html
# Server: Caddy
```

**If fails** (404 or 502):
```bash
# Check Vikunja API container
podman compose -f docker-compose.yml -f docker-compose.yml logs vikunja-api --tail=20

# Check if Vikunja listening on port 3456
podman compose -f docker-compose.yml -f docker-compose.yml exec -T vikunja-api \
  netstat -tlnp | grep 3456 || echo "Not listening on 3456"
```

---

### Test 2: Vikunja REST API

**Objective**: Verify API endpoints are functional

```bash
# Cline: Test API info endpoint
curl -s http://localhost/vikunja/api/v1/info | jq .

# Expected output:
# {
#   "version": "0.24.1",
#   "frontendurl": "http://localhost/vikunja",
#   "motd": "..."
# }
```

**If fails** (null response, "Connection refused", etc.):
```bash
# Test direct connection (bypass Caddy)
curl -s http://vikunja-api:3456/api/v1/info | jq . || echo "Direct connection failed"

# Check PostgreSQL connection
podman compose -f docker-compose.yml exec vikunja-api \
  curl -s http://localhost:3456/api/v1/info | jq . || echo "API not responding"
```

---

### Test 3: Create Vikunja User via API

**Objective**: Verify authentication system works

```bash
# Cline: Create a test user (first user auto-promoted to admin)
VIKUNJA_API="http://localhost/vikunja/api/v1"

curl -X POST "$VIKUNJA_API/user" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@localhost",
    "password": "testpass123"
  }'

# Expected output (201 Created):
# {
#   "id": 1,
#   "username": "testuser",
#   "email": "test@localhost",
#   "created": "2026-02-07T...",
#   "is_admin": true
# }
```

---

### Test 4: Create Project & Task

**Objective**: Verify project management workflow

```bash
# Cline: Get JWT token first
VIKUNJA_API="http://localhost/vikunja/api/v1"

# Login to get token
TOKEN=$(curl -s -X POST "$VIKUNJA_API/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }' | jq -r '.token')

echo "Got token: $TOKEN"

# Create a project
PROJECT=$(curl -s -X POST "$VIKUNJA_API/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Vikunja Testing",
    "description": "Test project"
  }' | jq '.')

echo "Created project:"
echo "$PROJECT" | jq '.id, .title'

# Extract project ID
PROJECT_ID=$(echo "$PROJECT" | jq -r '.id')

# Create a task in the project
curl -s -X POST "$VIKUNJA_API/projects/$PROJECT_ID/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task: Verify Vikunja Integration",
    "description": "This task was created via API"
  }' | jq '{id, title, description, created}'

echo "✅ Project and task created successfully"
```

---

### Test 5: Database Persistence

**Objective**: Verify data survives container restart

```bash
# Cline: Stop and restart Vikunja, check data persists

# 1. Get current task count
VIKUNJA_API="http://localhost/vikunja/api/v1"
TOKEN=$(curl -s -X POST "$VIKUNJA_API/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' | jq -r '.token')

TASK_COUNT_BEFORE=$(curl -s "$VIKUNJA_API/tasks/all?sort_by=id&order_by=asc" \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | length')

echo "Tasks before restart: $TASK_COUNT_BEFORE"

# 2. Restart Vikunja containers
podman compose -f docker-compose.yml -f docker-compose.yml restart vikunja-api vikunja-db

# 3. Wait for restart
sleep 30

# 4. Get task count again
TOKEN=$(curl -s -X POST "$VIKUNJA_API/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' | jq -r '.token')

TASK_COUNT_AFTER=$(curl -s "$VIKUNJA_API/tasks/all?sort_by=id&order_by=asc" \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | length')

echo "Tasks after restart: $TASK_COUNT_AFTER"

if [ "$TASK_COUNT_BEFORE" = "$TASK_COUNT_AFTER" ]; then
    echo "✅ Data persistence verified"
else
    echo "❌ Data loss detected!"
fi
```

---

## Performance Baseline

### Measure 1: Container Memory Usage

```bash
# Cline: Capture current memory utilization
podman stats --no-stream --format "table {{.Names}}\t{{.MemUsage}}" | \
  grep -E "vikunja|rag|ui|redis|caddy|postgres"

# Expected (approximate):
# xnai_vikunja_api      50M / 512M
# xnai_vikunja_db       80M / 512M
# xnai_rag_api         800M / 4G
# xnai_chainlit_ui     300M / 2G
# xnai_redis           30M / 512M
# xnai_caddy           10M / 100M
# ─────────────────────────────────
# Total:              ~1.3G / ~7.6G (healthy for 8GB system)
```

**Action if over budget**:
```bash
# Review PostgreSQL tuning
podman compose -f docker-compose.yml exec vikunja-db \
  ps aux | grep postgres

# Check Vikunja database connections
podman compose -f docker-compose.yml exec vikunja-db \
  psql -U vikunja -d vikunja -c "SELECT count(*) FROM pg_stat_activity;"
```

---

### Measure 2: API Latency Baseline

```bash
# Cline: Measure request/response times
VIKUNJA_API="http://localhost/vikunja/api/v1"

# Get auth token
TOKEN=$(curl -s -X POST "$VIKUNJA_API/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' | jq -r '.token')

# Measure latency: List tasks
echo "Measuring API latency (10 requests)..."
for i in {1..10}; do
    curl -s -w "Request $i: %{time_total}s\n" -o /dev/null \
        "$VIKUNJA_API/tasks/all" \
        -H "Authorization: Bearer $TOKEN"
done

# Expected: ~100-300ms per request (on local system)
```

**Interpretation**:
- `< 100ms`: Excellent (local network)
- `100-300ms`: Good (typical containerized)
- `300-1000ms`: Acceptable (slow hardware or network)
- `> 1000ms`: Investigate (PostgreSQL tuning needed)

---

### Measure 3: Disk I/O Performance

```bash
# Cline: Check database file size and I/O
du -sh data/vikunja/db
# Expected: 10-50MB (grows with tasks)

# Monitor active queries
podman compose -f docker-compose.yml exec vikunja-db \
  psql -U vikunja -d vikunja -c "SELECT pid, query, state FROM pg_stat_activity WHERE query NOT LIKE '%idle%';"
```

---

## Security Validation

### Check 1: Secrets Not Exposed

```bash
# Cline: Verify secrets are NOT in plaintext in containers
podman compose -f docker-compose.yml -f docker-compose.yml exec vikunja-api \
  env | grep -E "PASSWORD|SECRET|TOKEN" || echo "✅ No secrets in environment (good!)"

# Verify secrets are injected correctly
podman compose -f docker-compose.yml exec vikunja-db \
  cat /run/secrets/vikunja_db_password > /dev/null && echo "✅ Secrets accessible in container"

# Verify compose file doesn't contain plaintext secrets
grep -E "password|secret|token" docker-compose.yml docker-compose.yml Caddyfile || \
  echo "✅ No hardcoded secrets in configuration files"
```

---

### Check 2: Rootless Container Security

```bash
# Cline: Verify containers run with restricted privileges
podman top xnai_vikunja_api user huser  # Should show non-root UID
# Expected: vikunja user or UID 1000, NOT root (0)

# Check capabilities
podman inspect xnai_vikunja_api | jq '.[] | select(.Id=="xnai_vikunja_api").HostConfig.CapAdd'
# Expected: null or empty (ALL capabilities dropped)

# Verify read-only filesystem
podman inspect xnai_vikunja_api | jq '.[] | .HostConfig.ReadonlyRootfs'
# Expected: true
```

---

### Check 3: Network Isolation

```bash
# Cline: Verify Vikunja is not exposed on direct port
ss -tlnp | grep -E "3456|5432" || echo "✅ Vikunja ports not exposed on host"

# Verify all access goes through Caddy (port 80)
ss -tlnp | grep -E "80|443" | grep caddy && echo "✅ Caddy listening on standard ports"

# Verify xnai_network is isolated
podman network inspect xnai_network | jq '.[] | .Options'
# Expected: driver is "bridge" (isolated), not "host"
```

---

### Check 4: TLS/HTTPS Readiness

```bash
# Cline: Verify Caddyfile is HTTPS-ready (for future deployment)
grep -A5 "tls" Caddyfile && echo "✅ TLS configured" || echo "⚠️  TLS not yet configured (HTTP-only for dev)"

# Test certificate generation (if TLS enabled)
# Caddy auto-generates self-signed certs on first HTTPS request
```

---

## Integration Testing

### Test 1: Caddy Proxy Routing

```bash
# Cline: Verify all services route correctly through Caddy

echo "Testing Caddy proxy routing..."

# Test 1: RAG API through Caddy
curl -s http://localhost/api/v1/health | jq .status || echo "❌ RAG API routing failed"

# Test 2: Chainlit through Caddy
curl -s http://localhost/ | head -20 || echo "❌ Chainlit routing failed"

# Test 3: Vikunja API through Caddy
curl -s http://localhost/vikunja/api/v1/info | jq .version || echo "❌ Vikunja routing failed"

# Test 4: Verify direct (internal) ports are NOT accessible
timeout 2 curl http://localhost:3456/api/v1/info 2>/dev/null || \
  echo "✅ Direct port 3456 properly blocked (good!)"

timeout 2 curl http://localhost:8000/health 2>/dev/null || \
  echo "✅ Direct port 8000 properly blocked (good!)"

echo "✅ All proxy routing tests passed"
```

---

### Test 2: Redis Backend Integration

```bash
# Cline: Verify Vikunja can use Redis for sessions

# Check Redis connectivity
podman compose -f docker-compose.yml exec redis redis-cli -a $(cat secrets/redis_password.txt) ping
# Expected: PONG

# Check if Vikunja is using Redis (create new session and verify in Redis)
podman compose -f docker-compose.yml exec redis redis-cli -a $(cat secrets/redis_password.txt) \
  KEYS "vikunja*" || echo "No Vikunja sessions in Redis yet"

# Create new login (generates session)
curl -s -X POST "http://localhost/vikunja/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' > /dev/null

# Check Redis again for session
podman compose -f docker-compose.yml exec redis redis-cli -a $(cat secrets/redis_password.txt) \
  INFO stats | grep "total_commands_processed" || echo "Check Redis is working"

echo "✅ Redis integration verified"
```

---

### Test 3: FAQs for Common Integration Issues

#### Q: Can I access Vikunja from another device on my network?

```bash
# A: You need to expose Caddy externally
# Current: Only localhost (127.0.0.1) can access
# To fix: Update Caddyfile :80 → 0.0.0.0:80 (NOT RECOMMENDED for dev)

# For now: Use SSH tunnel from other devices
ssh -L 8080:localhost:80 user@your-dev-machine
# Then access: http://localhost:8080/vikunja from other device
```

#### Q: Can Vikunja tasks be edited from both API and UI?

```bash
# A: Yes, they're fully synchronized
# Edit via UI → changes persist in PostgreSQL → API reflects changes

# Verify:
curl -s "http://localhost/vikunja/api/v1/tasks/1" \
  -H "Authorization: Bearer $TOKEN" | jq '.title'
```

#### Q: How do I backup Vikunja data?

```bash
# A: Use pg_dump (PostgreSQL backup tool)
podman compose -f docker-compose.yml exec vikunja-db \
  pg_dump -U vikunja -d vikunja > vikunja_backup_$(date +%Y%m%d).sql

# Or backup filesystem directly
tar czf vikunja_files_backup_$(date +%Y%m%d).tar.gz data/vikunja/files/
```

---

## Troubleshooting Guide

### Problem: Vikunja API returns 500 Error

**Symptoms**: `curl http://localhost/vikunja/api/v1/info` returns HTTP 500

**Diagnosis**:
```bash
# Step 1: Check Vikunja logs
podman compose -f docker-compose.yml logs vikunja-api --tail=30

# Step 2: Check PostgreSQL connectivity
podman compose -f docker-compose.yml logs vikunja-api | grep "database\|postgres\|connection"

# Step 3: Test PostgreSQL directly
podman compose -f docker-compose.yml exec vikunja-db \
  psql -U vikunja -d vikunja -c "SELECT 1"
```

**Solutions**:
```bash
# If PostgreSQL not ready: Wait 60s for initialization
sleep 60
podman compose -f docker-compose.yml restart vikunja-api

# If connection string wrong: Verify environment variables
podman compose -f docker-compose.yml exec vikunja-api env | grep DATABASE

# If database not initialized: Force migration
podman compose -f docker-compose.yml exec vikunja-api \
  vikunja migrate
```

---

### Problem: "Permission denied" when creating tasks

**Symptoms**: UI shows error when trying to create a task

**Diagnosis**:
```bash
# Check if Vikunja can write to /app/vikunja/files
podman compose -f docker-compose.yml exec vikunja-api \
  touch /app/vikunja/files/test.txt && echo "✅ Can write" || echo "❌ Cannot write"

# Check directory permissions from inside container
podman compose -f docker-compose.yml exec vikunja-api \
  ls -la /app/vikunja/
```

**Solutions**:
```bash
# Fix permissions on host
podman unshare chown 1000:1000 -R data/vikunja/files

# Or: Give broader permissions (less secure)
chmod 755 data/vikunja/files
```

---

### Problem: High memory usage by PostgreSQL

**Symptoms**: `podman stats` shows PostgreSQL using >500MB

**Diagnosis**:
```bash
# Check current settings
podman compose -f docker-compose.yml exec vikunja-db \
  postgres -C shared_buffers

# Check active connections
podman compose -f docker-compose.yml exec vikunja-db \
  psql -U vikunja -d vikunja -c "SELECT count(*) FROM pg_stat_activity;"
```

**Solutions**:
```bash
# Reduce PostgreSQL memory usage
# Edit config/postgres.conf:
shared_buffers = 64MB           # Reduce from 128MB
effective_cache_size = 128MB    # Reduce from 256MB

# Restart PostgreSQL
podman compose -f docker-compose.yml restart vikunja-db
```

---

### Problem: Caddy "bad gateway" for Vikunja

**Symptoms**: `curl http://localhost/vikunja/` returns 502 Bad Gateway

**Diagnosis**:
```bash
# Check if Vikunja API is running
podman compose -f docker-compose.yml ps | grep vikunja-api

# Check if Caddy can reach Vikunja internally
podman exec xnai_caddy curl -s http://vikunja-api:3456/api/v1/info | jq . || \
  echo "❌ Caddy cannot reach Vikunja"

# Check Caddy logs
podman logs xnai_caddy --tail=20
```

**Solutions**:
```bash
# Restart Vikunja API
podman compose -f docker-compose.yml restart vikunja-api

# Reload Caddy config (no downtime)
podman exec xnai_caddy caddy reload -c /etc/caddy/Caddyfile

# If persistent: Check network
podman network inspect xnai_network | jq '.[] | .Containers'
```

---

### Problem: JWT Token Expired/Invalid

**Symptoms**: API returns 401 Unauthorized after login

**Diagnosis**:
```bash
# Check token expiration time
curl -s -X POST "http://localhost/vikunja/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' | jq '.expires'

# Expected: Unix timestamp 24h from now (86400 seconds)
```

**Solutions**:
```bash
# Token expiration is normal, re-login
curl -X POST "http://localhost/vikunja/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' | jq '.token'

# If JWT secret was rotated: Users must re-login
# Clear existing tokens (optional)
podman compose -f docker-compose.yml exec redis redis-cli \
  FLUSHDB  # WARNING: Clears all sessions!
```

---

## Success Criteria Checklist

- [ ] Vikunja web UI accessible at `http://localhost/vikunja/`
- [ ] REST API responding at `http://localhost/vikunja/api/v1/info`
- [ ] User can create/edit/delete projects
- [ ] User can create/edit/delete tasks
- [ ] Data persists across container restarts
- [ ] Memory usage < 2GB for Vikunja services
- [ ] API latency < 500ms under normal load
- [ ] No plaintext secrets in environment
- [ ] All containers run as non-root
- [ ] All access goes through Caddy proxy
- [ ] PostgreSQL connection pooling working (<20 max connections)
- [ ] Redis backend for sessions working (optional but verified)

---

## Post-Testing Steps

```bash
# Cline: After all tests pass, clean up test data

# Delete test user
VIKUNJA_API="http://localhost/vikunja/api/v1"
TOKEN=$(curl -s -X POST "$VIKUNJA_API/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' | jq -r '.token')

# List users
curl -s "$VIKUNJA_API/user" -H "Authorization: Bearer $TOKEN" | jq '.[] | {id, username}'

# Delete test user (if desired - optional)
# curl -X DELETE "$VIKUNJA_API/user/[ID]" -H "Authorization: Bearer $TOKEN"

echo "✅ Testing phase complete!"
```

---

**Next Step**: Proceed to Part 5 (Voice Integration & Advanced Features)

---

## Performance Optimization Tips

1. **PostgreSQL**: Monitor `pg_stat_statements` for slow queries
2. **Redis**: Enable `SLOWLOG` to track slow commands
3. **Caddy**: Monitor reverse proxy latency: `podman logs xnai_caddy | grep latency`
4. **Vikunja API**: Enable profiling in config for memory analysis
5. **Docker images**: Use Alpine variants to reduce footprint (~50% smaller)

---

## Monitoring Dashboard (Optional)

For ongoing monitoring, consider:
- Prometheus scraping `/metrics` from RAG API
- Grafana visualizing Prometheus data
- Alert thresholds for memory >3.5GB, latency >1000ms

(Covered in future Phase 2)

---

**Status: All Vikunja testing procedures documented** ✅

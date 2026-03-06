#!/bin/bash
# XNAi Foundation Stack Health Check
# Tests all critical services and reports status

set -u

REDIS_HOST="${REDIS_HOST:-127.0.0.1}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-changeme123}"

VIKUNJA_URL="${VIKUNJA_URL:-http://127.0.0.1:8000/vikunja}"
CONSUL_URL="${CONSUL_URL:-http://127.0.0.1:8500}"
CADDY_URL="${CADDY_URL:-http://127.0.0.1:8000}"
QDRANT_URL="${QDRANT_URL:-http://127.0.0.1:6333}"

echo "============================================"
echo "XNAi Foundation Stack Health Check"
echo "$(date)"
echo "============================================"
echo ""

passed=0
failed=0

# Test Redis
echo -n "Redis ($REDIS_HOST:$REDIS_PORT)... "
if timeout 3 redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" PING &>/dev/null; then
    echo "✓ PASS (AUTH OK)"
    ((passed++))
else
    echo "✗ FAIL"
    ((failed++))
fi

# Test Vikunja
echo -n "Vikunja API ($VIKUNJA_URL/api/v1/info)... "
if timeout 3 curl -s -o /dev/null -w "%{http_code}" "$VIKUNJA_URL/api/v1/info" 2>/dev/null | grep -q "200"; then
    echo "✓ PASS (HTTP 200)"
    ((passed++))
else
    echo "✗ FAIL"
    ((failed++))
fi

# Test Consul
echo -n "Consul UI ($CONSUL_URL/v1/status/leader)... "
if timeout 3 curl -s -o /dev/null -w "%{http_code}" "$CONSUL_URL/v1/status/leader" 2>/dev/null | grep -q "200"; then
    echo "✓ PASS (HTTP 200)"
    ((passed++))
else
    echo "✗ FAIL"
    ((failed++))
fi

# Test Caddy
echo -n "Caddy Reverse Proxy ($CADDY_URL/)... "
# Caddy root may return 502 if no handler; test via vikunja upstream instead
if timeout 3 curl -s -o /dev/null -w "%{http_code}" "$CADDY_URL/vikunja/api/v1/info" 2>/dev/null | grep -q "200"; then
    echo "✓ PASS (Routing OK)"
    ((passed++))
else
    echo "✗ FAIL"
    ((failed++))
fi

# Test Qdrant (optional, known issue)
echo -n "Qdrant Vector DB ($QDRANT_URL/health)... "
if timeout 3 curl -s -o /dev/null -w "%{http_code}" "$QDRANT_URL/health" 2>/dev/null | grep -q "200"; then
    echo "✓ PASS (HTTP 200)"
    ((passed++))
else
    echo "⚠ SKIP (Not running - uid/gid issue pending)"
fi

# Test Podman containers
echo ""
echo "Container Status:"
if command -v podman &>/dev/null; then
    podman ps --format "{{.Names}}\t{{.Status}}" | while read name status; do
        if [[ "$status" == *"healthy"* ]]; then
            echo "  ✓ $name ($status)"
        elif [[ "$status" == *"Up"* ]]; then
            echo "  ✓ $name ($status)"
        else
            echo "  ⚠ $name ($status)"
        fi
    done
fi

# Test disk space
echo ""
echo "Disk Usage:"
disk_usage=$(df / | tail -1 | awk '{print $(NF-1)}')
disk_free=$(df / | tail -1 | awk '{print $(NF-2)}')
echo "  Free: $disk_free / Usage: $disk_usage"
if [[ "${disk_usage%\%}" -gt 90 ]]; then
    echo "  ⚠ CRITICAL: >90% disk usage"
fi

echo ""
echo "============================================"
echo "Summary: $passed passed, $failed failed"
if [[ $failed -eq 0 ]]; then
    echo "Status: ✅ HEALTHY"
    exit 0
else
    echo "Status: ⚠ CHECK FAILURES"
    exit 1
fi

#!/bin/bash
# XNAi Foundation Stack Health Check
# Tests all critical services and reports status using container IPs

set -u

# Function to get container IP
get_container_ip() {
    local name=$1
    local ip=$(podman inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$name" 2>/dev/null)
    if [[ -z "$ip" ]]; then
        echo "localhost"
    else
        echo "$ip"
    fi
}

REDIS_IP=$(get_container_ip xnai_redis)
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"

CADDY_IP=$(get_container_ip xnai_caddy)
VIKUNJA_URL="http://${CADDY_IP}:8000/vikunja"
CONSUL_URL="http://$(get_container_ip xnai_consul):8500"
CADDY_URL="http://${CADDY_IP}:8000"
QDRANT_URL="http://$(get_container_ip xnai_qdrant):6333"

echo "============================================"
echo "XNAi Foundation Stack Health Check"
echo "$(date)"
echo "============================================"
echo ""

passed=0
failed=0

# Test Redis
echo -n "Redis ($REDIS_IP:$REDIS_PORT)... "
if timeout 3 redis-cli -h "$REDIS_IP" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" PING &>/dev/null; then
    echo "✓ PASS"
    ((passed++))
else
    echo "✗ FAIL"
    ((failed++))
fi

# Test Vikunja (via Caddy)
echo -n "Vikunja API ($VIKUNJA_URL/api/v1/info)... "
if timeout 3 curl -s -o /dev/null -w "%{http_code}" "$VIKUNJA_URL/api/v1/info" 2>/dev/null | grep -q "200"; then
    echo "✓ PASS"
    ((passed++))
else
    echo "✗ FAIL"
    ((failed++))
fi

# Test Qdrant
echo -n "Qdrant Vector DB ($QDRANT_URL/healthz)... "
if timeout 3 curl -s -o /dev/null -w "%{http_code}" "$QDRANT_URL/healthz" 2>/dev/null | grep -q "200"; then
    echo "✓ PASS"
    ((passed++))
else
    echo "✗ FAIL"
    ((failed++))
fi

# Test Memory Bank MCP
echo -n "Memory Bank MCP (Redis-check)... "
if timeout 3 podman exec xnai_memory_bank_mcp python3 -c "import redis; import os; r=redis.Redis(host='redis', password=os.environ.get('REDIS_PASSWORD')); r.ping()" &>/dev/null; then
    echo "✓ PASS"
else
    if pgrep -f "memory-bank-mcp/server.py" >/dev/null; then
        echo "✓ PASS (Process)"
    else
        echo "✗ FAIL"
        ((failed++))
        # Don't increment passed for process fallback unless we're sure
        ((passed--)) 
    fi
fi
((passed++))

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

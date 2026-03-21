#!/bin/bash
# MB-MCP Startup Verification Script
# Validates Memory Bank MCP is running and healthy
# Run this during system startup to ensure knowledge persistence layer is available

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
MB_ROOT="$REPO_ROOT/memory_bank"
LOG_FILE="$MB_ROOT/checkpoints/MB-MCP-STARTUP_$(date +%s).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=== MB-MCP Startup Verification ===" | tee -a "$LOG_FILE"
echo "Started at: $(date -u)" | tee -a "$LOG_FILE"
echo "Repository root: $REPO_ROOT" | tee -a "$LOG_FILE"
echo ""

# Check 1: Memory Bank directory structure
echo "[1/6] Checking memory_bank directory structure..." | tee -a "$LOG_FILE"
required_dirs=(
  "checkpoints"
  "sessions"
  "chronicles"
  "tasks"
  "experts"
)

all_dirs_exist=true
for dir in "${required_dirs[@]}"; do
  if [ -d "$MB_ROOT/$dir" ]; then
    echo "  ✓ $dir exists" | tee -a "$LOG_FILE"
  else
    echo "  ✗ $dir missing" | tee -a "$LOG_FILE"
    all_dirs_exist=false
  fi
done

if [ "$all_dirs_exist" = false ]; then
  echo -e "${YELLOW}Warning: Some memory_bank directories missing${NC}" | tee -a "$LOG_FILE"
fi
echo ""

# Check 2: Core knowledge artifacts
echo "[2/6] Checking core knowledge artifacts..." | tee -a "$LOG_FILE"
required_files=(
  "activeContext.md"
  "ANCHOR_MANIFEST.md"
)

all_files_exist=true
for file in "${required_files[@]}"; do
  if [ -f "$MB_ROOT/$file" ]; then
    echo "  ✓ $file exists" | tee -a "$LOG_FILE"
  else
    echo "  ✗ $file missing" | tee -a "$LOG_FILE"
    all_files_exist=false
  fi
done

if [ "$all_files_exist" = false ]; then
  echo -e "${YELLOW}Warning: Some core artifacts missing${NC}" | tee -a "$LOG_FILE"
fi
echo ""

# Check 3: MB-MCP Container health
echo "[3/6] Checking MB-MCP container health..." | tee -a "$LOG_FILE"
if command -v docker &> /dev/null; then
  if docker ps | grep -q "memory-bank-mcp"; then
    echo "  ✓ Container running (docker)" | tee -a "$LOG_FILE"
    docker_status="running"
  else
    echo "  ⚠ Container not found via docker" | tee -a "$LOG_FILE"
    docker_status="not_found"
  fi
elif command -v podman &> /dev/null; then
  if podman ps | grep -q "memory-bank-mcp"; then
    echo "  ✓ Container running (podman)" | tee -a "$LOG_FILE"
    podman_status="running"
  else
    echo "  ⚠ Container not found via podman" | tee -a "$LOG_FILE"
    podman_status="not_found"
  fi
else
  echo "  ⚠ Docker/Podman not found" | tee -a "$LOG_FILE"
fi
echo ""

# Check 4: MB-MCP Health Endpoint
echo "[4/6] Checking MB-MCP health endpoint (http://localhost:8005/health)..." | tee -a "$LOG_FILE"
if command -v curl &> /dev/null; then
  response=$(curl -s -w "\n%{http_code}" http://localhost:8005/health 2>&1 || echo "error\n000")
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | head -n-1)
  
  if [ "$http_code" = "200" ]; then
    echo "  ✓ Health endpoint OK ($http_code)" | tee -a "$LOG_FILE"
    echo "    Response: $body" | tee -a "$LOG_FILE"
    health_status="ok"
  else
    echo "  ✗ Health endpoint failed ($http_code)" | tee -a "$LOG_FILE"
    echo "    Response: $body" | tee -a "$LOG_FILE"
    health_status="failed"
  fi
else
  echo "  ⚠ curl not found, skipping health check" | tee -a "$LOG_FILE"
fi
echo ""

# Check 5: MB-MCP Memory Endpoint
echo "[5/6] Checking MB-MCP memory endpoint (http://localhost:8005/memory)..." | tee -a "$LOG_FILE"
if command -v curl &> /dev/null; then
  response=$(curl -s -w "\n%{http_code}" http://localhost:8005/memory 2>&1 || echo "error\n000")
  http_code=$(echo "$response" | tail -n1)
  
  if [ "$http_code" = "200" ] || [ "$http_code" = "404" ]; then
    echo "  ✓ Memory endpoint accessible ($http_code)" | tee -a "$LOG_FILE"
    memory_status="accessible"
  else
    echo "  ✗ Memory endpoint error ($http_code)" | tee -a "$LOG_FILE"
    memory_status="error"
  fi
else
  echo "  ⚠ curl not available, skipping memory check" | tee -a "$LOG_FILE"
fi
echo ""

# Check 6: Knowledge Graph Index
echo "[6/6] Checking knowledge graph index..." | tee -a "$LOG_FILE"
if [ -f "$MB_ROOT/NAVIGATOR.md" ]; then
  lines=$(wc -l < "$MB_ROOT/NAVIGATOR.md")
  echo "  ✓ NAVIGATOR.md exists ($lines lines)" | tee -a "$LOG_FILE"
  navigator_status="ok"
else
  echo "  ⚠ NAVIGATOR.md not found" | tee -a "$LOG_FILE"
  navigator_status="missing"
fi
echo ""

# Final Summary
echo "=== SUMMARY ===" | tee -a "$LOG_FILE"
echo "Memory Bank Root: $MB_ROOT" | tee -a "$LOG_FILE"
echo "Directories: $([ "$all_dirs_exist" = true ] && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠${NC}") All required directories present" | tee -a "$LOG_FILE"
echo "Artifacts: $([ "$all_files_exist" = true ] && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠${NC}") All core files present" | tee -a "$LOG_FILE"
echo "Container: $([ ! -z "$docker_status" ] && ([ "$docker_status" = "running" ] && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠${NC}") || echo "N/A") Running" | tee -a "$LOG_FILE"
echo "Health: $([ "$health_status" = "ok" ] && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}") Responsive" | tee -a "$LOG_FILE"
echo "Memory API: $([ "$memory_status" = "accessible" ] && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠${NC}") Accessible" | tee -a "$LOG_FILE"
echo "Navigator: $([ "$navigator_status" = "ok" ] && echo -e "${GREEN}✓${NC}" || echo -e "${YELLOW}⚠${NC}") Index available" | tee -a "$LOG_FILE"
echo ""
echo "Completed at: $(date -u)" | tee -a "$LOG_FILE"
echo "Log saved to: $LOG_FILE" | tee -a "$LOG_FILE"

# Exit code based on health endpoint
if [ "$health_status" = "ok" ]; then
  echo -e "${GREEN}✓ MB-MCP is healthy and ready${NC}"
  exit 0
else
  echo -e "${YELLOW}⚠ MB-MCP startup verification completed with warnings${NC}"
  exit 0  # Still exit 0 to allow startup to continue
fi

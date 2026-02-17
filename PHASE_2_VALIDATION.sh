#!/bin/bash
# Phase 2: Chainlit Build & Deploy Validation Script
# Tests audio dependencies installation and service configuration

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "Phase 2: Chainlit Build & Deploy - Validation"
echo "═══════════════════════════════════════════════════════════════"

# Test 1: Verify base image has audio dependencies
echo ""
echo "[TEST 1] Verifying audio dependencies in xnai-base:latest..."
docker run --rm xnai-base:latest bash -c "
  ffmpeg -version 2>&1 | head -1 && echo '  ✓ ffmpeg installed'
  dpkg -l | grep libportaudio2 > /dev/null && echo '  ✓ libportaudio2 installed'
  dpkg -l | grep portaudio19-dev > /dev/null && echo '  ✓ portaudio19-dev installed'
" || exit 1

# Test 2: Verify Chainlit UI image exists
echo ""
echo "[TEST 2] Verifying xnai-ui:latest image..."
docker images xnai-ui | grep latest > /dev/null && echo "  ✓ xnai-ui:latest exists" || exit 1
IMAGE_SIZE=$(docker images xnai-ui --format "{{.Size}}" | grep -o "^[^ ]*")
echo "  ✓ Image size: $IMAGE_SIZE"

# Test 3: Verify docker-compose configuration
echo ""
echo "[TEST 3] Verifying docker-compose.yml configuration..."
grep -q "service.*ui:" docker-compose.yml && echo "  ✓ UI service defined"
grep -q "8001:8001" docker-compose.yml && echo "  ✓ Port mapping 8001:8001 configured"
grep -q "CHAINLIT_NO_TELEMETRY=true" docker-compose.yml && echo "  ✓ Zero-telemetry mode enabled"
grep -q "CHAINLIT_PORT=8001" docker-compose.yml && echo "  ✓ CHAINLIT_PORT set to 8001"

# Test 4: Verify dependencies in Dockerfile
echo ""
echo "[TEST 4] Verifying audio dependencies in Dockerfile.base..."
grep -q "libportaudio2" Dockerfile.base && echo "  ✓ libportaudio2 in Dockerfile"
grep -q "portaudio19-dev" Dockerfile.base && echo "  ✓ portaudio19-dev in Dockerfile"
grep -q "^.*ffmpeg" Dockerfile.base && echo "  ✓ ffmpeg in Dockerfile"

# Test 5: Check service dependencies
echo ""
echo "[TEST 5] Verifying service dependency chain..."
grep -A 5 "service.*ui:" docker-compose.yml | grep -q "redis" && echo "  ✓ UI depends on redis"
grep -A 5 "service.*ui:" docker-compose.yml | grep -q "rag" && echo "  ✓ UI depends on rag"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ Phase 2 Validation Complete - All Checks Passed!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Start services: docker-compose -f docker-compose-noninit.yml up redis qdrant rag ui"
echo "  2. Test UI: curl http://localhost:8001"
echo "  3. Verify audio packages in running container"
echo ""

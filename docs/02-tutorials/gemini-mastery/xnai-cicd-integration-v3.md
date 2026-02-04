# CI/CD Caching Integration Guide (2026 Offline Edition)
**Version**: 3.0 | **Date**: January 27, 2026

---

## Part 1: GitHub Actions with Podman apt-cacher-ng (Offline Runner Support)

Create: `.github/workflows/build-with-cache.yml`

```yaml
name: Build with APT Cache (Offline Runner Support)

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  APT_CACHE_HOST: "127.0.0.1"
  APT_CACHE_PORT: "3142"

jobs:
  build:
    runs-on: self-hosted  # REQUIRED: Use self-hosted runner with persistent cache
    # Alternative: runs-on: ubuntu-latest (ephemeral, no cache persistence)
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install dependencies (if not on self-hosted)
        if: runner.os == 'Linux' && !contains(runner.name, 'self-hosted')
        run: |
          sudo apt-get update
          sudo apt-get install -y podman
      
      - name: Start apt-cacher-ng (if not running)
        run: |
          # Check if cache container is running
          if ! podman ps | grep -q xnai-apt-cacher-ng; then
            echo "Starting apt-cacher-ng..."
            
            # Create cache volume if needed
            podman volume inspect apt-cache >/dev/null 2>&1 || \
              podman volume create apt-cache
            
            # Start container with hardened config
            podman run -d \
              --name xnai-apt-cacher-ng \
              -p ${APT_CACHE_HOST}:${APT_CACHE_PORT}:3142 \
              -v apt-cache:/var/cache/apt-cacher-ng:Z \
              --security-opt no-new-privileges:true \
              --cap-drop=ALL \
              --cap-add=NET_BIND_SERVICE \
              --read-only \
              --tmpfs /tmp:rw,noexec,nosuid,size=64m \
              docker.io/sameersbn/apt-cacher-ng:latest
            
            # Wait for health check
            echo "Waiting for apt-cacher-ng to become healthy..."
            for i in {1..30}; do
              if curl -sf http://${APT_CACHE_HOST}:${APT_CACHE_PORT}/acng-report.html >/dev/null 2>&1; then
                echo "✓ apt-cacher-ng is healthy"
                break
              fi
              echo -n "."
              sleep 1
            done
          else
            echo "✓ apt-cacher-ng already running"
          fi
      
      - name: Verify apt-cacher-ng accessibility
        run: |
          curl -f http://${APT_CACHE_HOST}:${APT_CACHE_PORT}/acng-report.html || {
            echo "✗ apt-cacher-ng not accessible"
            exit 1
          }
      
      - name: Restore Podman image cache (Actions cache)
        uses: actions/cache@v4
        with:
          path: |
            ~/.local/share/containers/storage
          key: podman-${{ runner.os }}-${{ hashFiles('**/Dockerfile*') }}
          restore-keys: |
            podman-${{ runner.os }}-
      
      - name: Build image with apt cache
        run: |
          podman build \
            --build-arg HTTP_PROXY=http://host.containers.internal:${APT_CACHE_PORT} \
            --build-arg HTTPS_PROXY=http://host.containers.internal:${APT_CACHE_PORT} \
            -t xnai-app:${{ github.sha }} \
            -f Dockerfile.api \
            .
      
      - name: Save image to cache (for artifact caching)
        if: github.ref == 'refs/heads/main'
        run: |
          mkdir -p /tmp/podman-images
          podman save xnai-app:${{ github.sha }} -o /tmp/podman-images/xnai-app.tar
      
      - name: Upload image artifact
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v4
        with:
          name: xnai-app-${{ github.sha }}
          path: /tmp/podman-images/xnai-app.tar
          retention-days: 7
      
      - name: Run tests
        run: |
          podman run --rm xnai-app:${{ github.sha }} \
            python -m pytest tests/ -v
      
      - name: Push to registry (on main)
        if: github.ref == 'refs/heads/main'
        env:
          REGISTRY_URL: ${{ secrets.REGISTRY_URL }}
          REGISTRY_USER: ${{ secrets.REGISTRY_USER }}
          REGISTRY_PASS: ${{ secrets.REGISTRY_PASS }}
        run: |
          podman login -u "$REGISTRY_USER" -p "$REGISTRY_PASS" "$REGISTRY_URL"
          podman tag xnai-app:${{ github.sha }} \
            "$REGISTRY_URL/xnai-app:latest"
          podman push "$REGISTRY_URL/xnai-app:latest"
      
      - name: Cache statistics and performance metrics
        if: always()
        run: |
          echo "=== Cache Statistics ==="
          curl -s http://${APT_CACHE_HOST}:${APT_CACHE_PORT}/acng-report.html | \
            grep -i "stored\|fetched\|total\|hit" || echo "Cache unavailable"
          
          # Export metrics to job summary
          echo "## Build Performance" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "- Cache Host: ${APT_CACHE_HOST}:${APT_CACHE_PORT}" >> $GITHUB_STEP_SUMMARY
          echo "- Image: xnai-app:${{ github.sha }}" >> $GITHUB_STEP_SUMMARY
```

---

## Part 2: Self-Hosted Runner Setup (Offline Mode with Persistent Cache)

Create: `~/.local/bin/setup-gh-runner-with-cache.sh`

```bash
#!/bin/bash
set -euo pipefail

# ============================================================================
# XOE-NOVAI GITHUB ACTIONS SELF-HOSTED RUNNER SETUP
# Supports: Offline mode, persistent apt cache, Podman rootless
# Ma'at Principle: Order (systematic setup) + Justice (fair resource access)
# ============================================================================

RUNNER_DIR="${HOME}/github-actions-runner"
CACHE_VOLUME="gh-apt-cache"
RUNNER_TOKEN="${RUNNER_TOKEN:-}"
RUNNER_NAME="${RUNNER_NAME:-apt-cache-runner-$(hostname)}"
REPO_URL="${REPO_URL:-https://github.com/<org>/<repo>}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[✓]${NC} [$(date '+%H:%M:%S')] $*"
}

warn() {
    echo -e "${YELLOW}[⚠]${NC} [$(date '+%H:%M:%S')] $*"
}

error() {
    echo -e "${RED}[✗]${NC} [$(date '+%H:%M:%S')] $*"
    exit 1
}

log "=== GitHub Actions Self-Hosted Runner Setup ==="

# ============================================================================
# STEP 1: Verify Prerequisites
# ============================================================================

log "Verifying prerequisites..."

# Check Podman version
if ! command -v podman &>/dev/null; then
    error "Podman not installed"
fi

podman_version=$(podman --version | awk '{print $3}')
if [[ "$(printf '%s\n' "5.5.0" "$podman_version" | sort -V | head -1)" != "5.5.0" ]]; then
    error "Podman <5.5.0 detected (CVE-2025-22869 vulnerable)"
fi

log "Podman $podman_version OK"

# ============================================================================
# STEP 2: Create Persistent Cache Volume
# ============================================================================

log "Creating persistent cache volume..."
if podman volume inspect "$CACHE_VOLUME" >/dev/null 2>&1; then
    warn "Cache volume $CACHE_VOLUME already exists, reusing"
else
    podman volume create "$CACHE_VOLUME"
    log "Cache volume created"
fi

# ============================================================================
# STEP 3: Start apt-cacher-ng (persistent across runner restarts)
# ============================================================================

log "Starting apt-cacher-ng service..."
if podman ps | grep -q xnai-apt-cacher-ng; then
    warn "apt-cacher-ng already running"
else
    podman run -d \
        --name xnai-apt-cacher-ng \
        -p 127.0.0.1:3142:3142 \
        -v "$CACHE_VOLUME:/var/cache/apt-cacher-ng:Z" \
        --restart=always \
        --security-opt no-new-privileges:true \
        --cap-drop=ALL \
        --cap-add=NET_BIND_SERVICE \
        --read-only \
        --tmpfs /tmp:rw,noexec,nosuid,size=64m \
        --tmpfs /var/run:rw,noexec,nosuid,size=16m \
        docker.io/sameersbn/apt-cacher-ng:latest
    
    sleep 10
    
    if curl -sf http://127.0.0.1:3142/acng-report.html >/dev/null 2>&1; then
        log "apt-cacher-ng started successfully"
    else
        error "apt-cacher-ng failed to start"
    fi
fi

# ============================================================================
# STEP 4: Download GitHub Actions Runner
# ============================================================================

log "Setting up GitHub Actions runner..."
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

if [[ ! -f ./config.sh ]]; then
    log "Downloading GitHub Actions runner..."
    
    # Get latest runner version
    RUNNER_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | \
                     grep -oP '"tag_name": "v\K[0-9.]+' | head -1)
    
    if [[ -z "$RUNNER_VERSION" ]]; then
        # Fallback to known version if GitHub API unavailable (offline mode)
        RUNNER_VERSION="2.313.0"
        warn "Using fallback runner version: $RUNNER_VERSION"
    fi
    
    RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
    
    curl -o actions-runner.tar.gz -L "$RUNNER_URL"
    tar xzf actions-runner.tar.gz
    rm actions-runner.tar.gz
    
    log "Runner downloaded: v${RUNNER_VERSION}"
else
    log "Runner already downloaded"
fi

# ============================================================================
# STEP 5: Configure Runner with Proxy Environment
# ============================================================================

log "Configuring runner environment..."

# Create .env file with proxy settings
cat > "$RUNNER_DIR/.env" <<EOF
# APT cache proxy for builds
http_proxy=http://127.0.0.1:3142
https_proxy=http://127.0.0.1:3142
HTTP_PROXY=http://127.0.0.1:3142
HTTPS_PROXY=http://127.0.0.1:3142

# Podman configuration
STORAGE_DRIVER=overlay
STORAGE_OPTS=overlay.mount_program=/usr/bin/fuse-overlayfs

# Ma'at alignment
RUNNER_NAME=$RUNNER_NAME
RUNNER_WORKDIR=${RUNNER_DIR}/_work
EOF

log "Environment configured"

# ============================================================================
# STEP 6: Register Runner (requires token)
# ============================================================================

if [[ -z "$RUNNER_TOKEN" ]]; then
    warn "RUNNER_TOKEN not set, skipping registration"
    warn "Get token from: $REPO_URL/settings/actions/runners"
    warn ""
    warn "To register manually, run:"
    warn "  export RUNNER_TOKEN=<token>"
    warn "  export REPO_URL=$REPO_URL"
    warn "  $0"
    exit 0
fi

log "Registering runner with repository..."

if [[ -f "$RUNNER_DIR/.runner" ]]; then
    warn "Runner already registered, removing old registration"
    "$RUNNER_DIR/config.sh" remove --token "$RUNNER_TOKEN" || warn "Failed to remove old registration"
fi

"$RUNNER_DIR/config.sh" \
    --url "$REPO_URL" \
    --token "$RUNNER_TOKEN" \
    --unattended \
    --replace \
    --name "$RUNNER_NAME" \
    --work "${RUNNER_DIR}/_work" \
    --labels "self-hosted,Linux,X64,apt-cache,offline-capable"

log "Runner registered: $RUNNER_NAME"

# ============================================================================
# STEP 7: Install as Systemd Service (User Mode)
# ============================================================================

log "Installing as systemd user service..."

# Create systemd user service
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/github-runner.service <<EOF
[Unit]
Description=GitHub Actions Runner ($RUNNER_NAME)
After=network.target apt-cacher-ng.container.service

[Service]
Type=simple
WorkingDirectory=$RUNNER_DIR
ExecStart=$RUNNER_DIR/run.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment (load from .env)
EnvironmentFile=$RUNNER_DIR/.env

[Install]
WantedBy=default.target
EOF

# Reload and enable service
systemctl --user daemon-reload
systemctl --user enable github-runner.service
systemctl --user start github-runner.service

log "Systemd service installed and started"

# ============================================================================
# STEP 8: Verify Installation
# ============================================================================

log "Verifying installation..."
sleep 5

if systemctl --user is-active --quiet github-runner.service; then
    log "✓ Runner service is active"
else
    error "Runner service failed to start"
fi

if curl -sf http://127.0.0.1:3142/acng-report.html >/dev/null 2>&1; then
    log "✓ apt-cacher-ng is healthy"
else
    warn "apt-cacher-ng health check failed"
fi

# ============================================================================
# STEP 9: Display Status
# ============================================================================

log ""
log "=== Setup Complete ==="
log "Runner Name:       $RUNNER_NAME"
log "Runner Directory:  $RUNNER_DIR"
log "Cache Volume:      $CACHE_VOLUME"
log "apt-cacher-ng:     http://127.0.0.1:3142"
log ""
log "Commands:"
log "  Status:    systemctl --user status github-runner.service"
log "  Logs:      journalctl --user-unit github-runner.service -f"
log "  Stop:      systemctl --user stop github-runner.service"
log "  Restart:   systemctl --user restart github-runner.service"
log ""
log "Cache Statistics:"
curl -s http://127.0.0.1:3142/acng-report.html | grep -i "stored\|fetched" | head -5 || echo "Not available"
```

Make executable:
```bash
chmod +x ~/.local/bin/setup-gh-runner-with-cache.sh
```

Run setup:
```bash
export RUNNER_TOKEN="<your-token>"
export REPO_URL="https://github.com/<org>/<repo>"
~/.local/bin/setup-gh-runner-with-cache.sh
```

---

## Part 3: GitLab CI with apt-cacher-ng (Enhanced)

Create: `.gitlab-ci.yml`

```yaml
image: ubuntu:22.04

variables:
  http_proxy: "http://apt-cache:3142"
  https_proxy: "http://apt-cache:3142"
  APT_PROXY: "http://apt-cache:3142"
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""

services:
  - name: docker.io/sameersbn/apt-cacher-ng:latest
    alias: apt-cache
    variables:
      PORT: 3142
      BIND_ADDRESS: "0.0.0.0"

# Cache apt-cacher-ng data across pipeline runs
cache:
  key: apt-cache-global
  paths:
    - /var/cache/apt-cacher-ng/
  policy: pull-push

stages:
  - build
  - test
  - security
  - deploy

# ============================================================================
# BUILD STAGE
# ============================================================================

build:
  stage: build
  services:
    - docker:dind
    - name: docker.io/sameersbn/apt-cacher-ng:latest
      alias: apt-cache
  script:
    # Verify apt-cache is accessible
    - curl -f http://apt-cache:3142/acng-report.html || exit 1
    
    # Build with proxy
    - docker build \
        --build-arg HTTP_PROXY=$APT_PROXY \
        --build-arg HTTPS_PROXY=$APT_PROXY \
        -t xnai-app:$CI_COMMIT_SHA \
        -f Dockerfile.api .
    
    - docker tag xnai-app:$CI_COMMIT_SHA xnai-app:latest
    
    # Save image for subsequent stages
    - docker save xnai-app:latest -o xnai-app.tar
  artifacts:
    paths:
      - xnai-app.tar
    expire_in: 1 day
  cache:
    key: apt-cache-build
    paths:
      - /var/cache/apt-cacher-ng/
    policy: pull-push

# ============================================================================
# TEST STAGE
# ============================================================================

test:
  stage: test
  script:
    - docker load -i xnai-app.tar
    - docker run --rm xnai-app:latest python -m pytest tests/ -v
  dependencies:
    - build
  cache:
    key: apt-cache-global
    paths:
      - /var/cache/apt-cacher-ng/
    policy: pull

# ============================================================================
# SECURITY STAGE (Trivy Scan)
# ============================================================================

security:
  stage: security
  image: aquasec/trivy:latest
  script:
    - docker load -i xnai-app.tar
    - trivy image --severity CRITICAL,HIGH xnai-app:latest
  dependencies:
    - build
  allow_failure: true

# ============================================================================
# DEPLOY STAGE
# ============================================================================

deploy:
  stage: deploy
  script:
    - docker load -i xnai-app.tar
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker tag xnai-app:latest $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:latest
  dependencies:
    - build
  only:
    - main
  environment:
    name: production
    url: https://app.example.com

# ============================================================================
# CACHE STATISTICS (Always Run)
# ============================================================================

cache-stats:
  stage: .post
  script:
    - curl http://apt-cache:3142/acng-report.html | grep -i "hit\|stored" || echo "Cache stats unavailable"
  when: always
```

---

## Part 4: Offline Runner Fallback Strategy (Disaster Recovery)

Create: `~/.local/bin/offline-runner-fallback.sh`

```bash
#!/bin/bash
set -euo pipefail

# ============================================================================
# OFFLINE RUNNER FALLBACK STRATEGY
# Handles builds when internet is unavailable but cache is seeded
# ============================================================================

log() {
    echo "[$(date '+%H:%M:%S')] $*"
}

log "=== Offline Runner Fallback Mode ==="

# 1. Check if internet is available
if ping -c 1 -W 2 google.com >/dev/null 2>&1; then
    log "Internet available, proceeding with normal build"
    exit 0
fi

log "Internet unavailable, switching to offline mode"

# 2. Verify cache is available and seeded
if ! curl -sf http://127.0.0.1:3142/acng-report.html >/dev/null 2>&1; then
    log "ERROR: apt-cacher-ng not available"
    exit 1
fi

cache_size=$(curl -s http://127.0.0.1:3142/acng-report.html | grep -oP 'Total.*?(\d+)' | grep -oP '\d+' | head -1)
if [[ $cache_size -lt 1000 ]]; then
    log "WARNING: Cache appears empty ($cache_size entries)"
    log "Builds may fail due to missing packages"
fi

log "Cache available with $cache_size entries"

# 3. Configure offline mode for apt-cacher-ng
podman exec xnai-apt-cacher-ng sed -i 's/Offline: 0/Offline: 1/' /etc/apt-cacher-ng/acng.conf || true
podman exec xnai-apt-cacher-ng kill -HUP 1 || true

log "apt-cacher-ng configured for offline mode"

# 4. Proceed with build using cached packages only
log "Proceeding with offline build..."
```

---

## Part 5: Artifact Caching Strategy (Podman save/load)

Create: `.github/workflows/build-with-artifact-cache.yml`

```yaml
name: Build with Artifact Caching

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: self-hosted
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Restore cached Podman images
        id: cache-restore
        uses: actions/cache/restore@v4
        with:
          path: /tmp/podman-images
          key: podman-images-${{ hashFiles('**/Dockerfile*', '**/requirements.txt') }}
          restore-keys: |
            podman-images-
      
      - name: Load cached images (if available)
        if: steps.cache-restore.outputs.cache-hit == 'true'
        run: |
          if [[ -f /tmp/podman-images/xnai-app.tar ]]; then
            podman load -i /tmp/podman-images/xnai-app.tar
            echo "✓ Loaded cached image"
          fi
      
      - name: Build image
        run: |
          podman build \
            --build-arg HTTP_PROXY=http://host.containers.internal:3142 \
            -t xnai-app:latest \
            -f Dockerfile.api \
            .
      
      - name: Save image to cache
        run: |
          mkdir -p /tmp/podman-images
          podman save xnai-app:latest -o /tmp/podman-images/xnai-app.tar
      
      - name: Save cached images
        uses: actions/cache/save@v4
        if: always()
        with:
          path: /tmp/podman-images
          key: podman-images-${{ hashFiles('**/Dockerfile*', '**/requirements.txt') }}
```

---

## Part 6: Success Criteria Checklist

### GitHub Actions Integration
- [ ] Self-hosted runner configured with persistent cache
- [ ] apt-cacher-ng service starts automatically on runner boot
- [ ] Workflows use proxy for builds
- [ ] Cold builds <5 min, warm <45 sec in CI
- [ ] Cache hit ratio >70% across builds
- [ ] Artifact caching reduces redundant image builds
- [ ] Offline fallback mode works with seeded cache

### GitLab CI Integration
- [ ] apt-cache service runs alongside builds
- [ ] Pipeline uses cache effectively
- [ ] Security scanning (Trivy) integrated
- [ ] Cache statistics reported in pipeline logs

### Disaster Recovery
- [ ] Offline runner fallback script tested
- [ ] Cache backup/restore procedure documented
- [ ] Runner can operate without internet for >7 days

---

**CI/CD Integration by**: Xoe-NovAi Platform Team  
**Last Updated**: January 27, 2026  
**Prepared by**: Xoe-NovAi Architecture Team
#!/usr/bin/env bash
set -euo pipefail

log() { echo "$@"; }

log "Starting Vikunja fresh spin-up (rootless Podman) v1.0.0..."

# Prune any existing resources to ensure a clean start
log "Pruning existing Vikunja resources..."
podman pod ls -q | xargs -r podman pod rm -f || true
podman ps -a -q --filter "name=vikunja" | xargs -r podman rm -f || true
podman network ls -q --filter "name=vikunja" | xargs -r podman network rm -f || true
podman volume prune -f || true
podman system prune -a -f || true

# Ensure secrets exist
log "Ensuring Podman secrets (db-pass, jwt-secret)"
if ! podman secret inspect db-pass >/dev/null 2>&1; then
  openssl rand -base64 32 | podman secret create db-pass -
fi
if ! podman secret inspect jwt-secret >/dev/null 2>&1; then
  openssl rand -base64 64 | podman secret create jwt-secret -
fi

# Spin up Vikunja
log "Starting Vikunja stack (docker-compose.yml)" 
podman-compose -f docker-compose.yml up -d

# Basic health check loop
log "Waiting for Vikunja API to become healthy..."
for i in {1..60}; do
  if curl -fsS http://localhost:3456/api/v1/info >/dev/null; then
    log "Vikunja is up and healthy."
    exit 0
  fi
  sleep 5
done
log "Vikunja health check timed out."
exit 1

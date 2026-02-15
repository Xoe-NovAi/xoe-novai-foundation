#!/usr/bin/env bash
set -euo pipefail

# Root of the repo (two levels up from this script)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../" && pwd)"
LOG_DIR="$ROOT_DIR/docs/06-development-log/vikunja-integration"
RECOVERY_LOG="$LOG_DIR/recovery-log-$(date +%Y-%m-%d).md"

mkdir -p "$LOG_DIR"

log() {
  local msg="$1"
  echo "$msg" | tee -a "$RECOVERY_LOG"
}

log_step() {
  local title="$1"; local content="$2"
  echo "### $title" >> "$RECOVERY_LOG"
  echo "$content" >> "$RECOVERY_LOG"
  echo "" >> "$RECOVERY_LOG"
}

prune_resources() {
  log "Step 0: Pruning Podman resources for a fresh start..."
  if [ -n "$(podman pod ls -q)" ]; then
    podman pod ls -q | xargs -r podman pod rm -f || true
  fi
  if [ -n "$(podman ps -a -q)" ]; then
    podman ps -a -q | xargs -r podman rm -f || true
  fi
  if [ -n "$(podman network ls -q)" ]; then
    for n in $(podman network ls -q); do
      case "$n" in
        bridge|host|none) continue;;
      esac
      podman network rm "$n" || true
    done
  fi
  podman image prune -a -f || true
  podman volume prune -f || true
  podman system prune -a -f || true
  log "Step 0 complete."
}

fresh_db_dir() {
  log "Step 1: Fresh DB directory"
  rm -rf "$ROOT_DIR/db"
  mkdir -p "$ROOT_DIR/db"
  chmod 0777 "$ROOT_DIR/db"
  log "DB directory prepared at $ROOT_DIR/db"
}

ensure_secrets() {
  log "Step 2: Ensure Podman secrets (db-pass, jwt-secret)"
  if ! podman secret inspect db-pass >/dev/null 2>&1; then
    log "  Creating db-pass secret..."
    openssl rand -base64 32 | podman secret create db-pass -
  else
    log "  db-pass secret already exists."
  fi
  if ! podman secret inspect jwt-secret >/dev/null 2>&1; then
    log "  Creating jwt-secret secret..."
    openssl rand -base64 64 | tr -d '\n' | head -c 64 | podman secret create jwt-secret -
  else
    log "  jwt-secret secret already exists."
  fi
  log "Secrets in place."
}

wait_for_info() {
  local url="$1"; local max_wait=${2:-180}; local delay=${3:-5};
  local i=0
  while [ "$i" -lt "$max_wait" ]; do
    if curl -sSf "$url" >/dev/null; then
      log " Vikunja API reachable at $url"
      return 0
    fi
    sleep "$delay"
    i=$((i + delay))
  done
  log "Timed out waiting for Vikunja at $url"
  return 1
}

start_vikunja() {
  log "Step 3: Start Vikunja (rootless)"
  podman-compose -f docker-compose.vikunja.yml up -d
  log "Waiting for Vikunja to come up..."
  wait_for_info "http://localhost:3456/api/v1/info" 600 5 || true
}

export_vikunja_export() {
  log "Step 4: Export memory_bank to Vikunja import JSON..."
  python3 "$ROOT_DIR/scripts/memory_bank_export.py" memory_bank "$ROOT_DIR/vikunja-import.json"
}

import_flow() {
  local token="$1"
  if [ -z "$token" ]; then
    log "No API token provided; skipping live import. Provide a token to proceed."
    return 0
  fi
  log "Step 5: Importing tasks into Vikunja (live) with provided token..."
  python3 "$ROOT_DIR/scripts/vikunja_importer.py" "$ROOT_DIR/vikunja-import.json" "http://localhost:3456/api/v1" "$token" || true
}

main() {
  prune_resources
  fresh_db_dir
  ensure_secrets
  start_vikunja

  export_vikunja_export

  # Allow token via environment variable to enable non-interactive runs
  VIKUNJA_TOKEN="${VIKUNJA_TOKEN:-}"
  if [ -z "$VIKUNJA_TOKEN" ]; then
    read -r -p "Enter Vikunja API token (or leave blank for dry-run): " VIKUNJA_TOKEN < /dev/tty || true
  fi
  if [ -n "$VIKUNJA_TOKEN" ]; then
    import_flow "$VIKUNJA_TOKEN"
  else
    log "No token provided; memory_bank export ready for import via dry-run."
  fi

  log "Recovery flow completed. Check Vikunja UI at http://localhost:3456 and API at http://localhost:3456/api/v1/"
}

main "$@"

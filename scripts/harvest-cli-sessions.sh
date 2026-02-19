#!/bin/bash
# ---
# tool: cline
# model: claude-sonnet-4-6
# account: arcana-novai
# git_branch: main
# session_id: sprint6-2026-02-18
# version: v1.1.0
# created: 2026-02-18
# updated: 2026-02-18
# changelog: Fixed duplicate main(), corrected model sig, removed 'archived' label from OpenCode
# ---
# harvest-cli-sessions.sh — Harvest CLI session data into XNAi project
#
# Usage:
#   ./scripts/harvest-cli-sessions.sh [--dry-run] [--cli <copilot|gemini|opencode|cline|all>] [--ingest]
#
# Collects session data from all AI CLI tools and copies to xoe-novai-sync/mc-imports/
# for ingestion into the Qdrant xnai_conversations collection.

set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
IMPORT_BASE="$REPO_ROOT/xoe-novai-sync/mc-imports"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
LOG_FILE="$REPO_ROOT/logs/harvest-cli-sessions-${TIMESTAMP}.log"
DRY_RUN=false
TARGET_CLI="all"
DO_INGEST=false
HARVEST_COUNT=0
SKIP_COUNT=0
ERROR_COUNT=0

# ─── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─── Logging ──────────────────────────────────────────────────────────────────
mkdir -p "$(dirname "$LOG_FILE")"
log()  { echo -e "$1" | tee -a "$LOG_FILE"; }
info() { log "${BLUE}[INFO]${NC} $1"; }
ok()   { log "${GREEN}[OK]${NC} $1"; }
warn() { log "${YELLOW}[WARN]${NC} $1"; }
err()  { log "${RED}[ERROR]${NC} $1"; }

# ─── Args ─────────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true; shift ;;
    --ingest)  DO_INGEST=true; shift ;;
    --cli)     TARGET_CLI="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--dry-run] [--ingest] [--cli copilot|gemini|opencode|cline|all]"
      exit 0 ;;
    *) err "Unknown option: $1"; exit 1 ;;
  esac
done

# ─── Helper: safe copy ────────────────────────────────────────────────────────
# Copies src → dst, skipping if dst is newer than src.
safe_copy() {
  local src="$1"
  local dst="$2"

  if [[ ! -f "$src" ]]; then
    SKIP_COUNT=$((SKIP_COUNT + 1))
    return
  fi

  mkdir -p "$(dirname "$dst")"

  # Skip if destination is already up-to-date
  if [[ -f "$dst" && "$dst" -nt "$src" ]]; then
    SKIP_COUNT=$((SKIP_COUNT + 1))
    return
  fi

  if [[ "$DRY_RUN" == "true" ]]; then
    info "[DRY-RUN] Would copy: $src → $dst"
  else
    if cp -p "$src" "$dst" 2>>"$LOG_FILE"; then
      HARVEST_COUNT=$((HARVEST_COUNT + 1))
      ok "Copied: $(basename "$src") → $(dirname "$dst")/"
    else
      err "Failed to copy: $src"
      ERROR_COUNT=$((ERROR_COUNT + 1))
    fi
  fi
}

# ─── 1. GitHub Copilot CLI ────────────────────────────────────────────────────
harvest_copilot() {
  local src_base="$HOME/.copilot/session-state"
  local dst_base="$IMPORT_BASE/copilot"

  if [[ ! -d "$src_base" ]]; then
    warn "Copilot session-state not found: $src_base"
    return
  fi

  info "Harvesting GitHub Copilot CLI sessions from $src_base"
  local session_count=0

  for session_dir in "$src_base"/*/; do
    [[ -d "$session_dir" ]] || continue
    local uuid
    uuid="$(basename "$session_dir")"
    local dst_dir="$dst_base/$uuid"

    # events.jsonl — PRIMARY conversation record
    safe_copy "$session_dir/events.jsonl"    "$dst_dir/events.jsonl"
    # plan.md — valuable task context
    safe_copy "$session_dir/plan.md"         "$dst_dir/plan.md"
    # workspace.yaml — session metadata
    safe_copy "$session_dir/workspace.yaml"  "$dst_dir/workspace.yaml"

    [[ -f "$session_dir/events.jsonl" ]] && session_count=$((session_count + 1))
  done

  ok "Copilot: scanned $session_count sessions"
}

# ─── 2. Gemini CLI ────────────────────────────────────────────────────────────
harvest_gemini() {
  local src_base="$HOME/.gemini"
  local dst_base="$IMPORT_BASE/gemini"

  if [[ ! -d "$src_base" ]]; then
    warn "Gemini CLI data not found: $src_base"
    return
  fi

  info "Harvesting Gemini CLI sessions from $src_base"
  local session_count=0

  # Sessions directory
  if [[ -d "$src_base/sessions" ]]; then
    for session_dir in "$src_base/sessions"/*/; do
      [[ -d "$session_dir" ]] || continue
      local sid
      sid="$(basename "$session_dir")"
      local dst_dir="$dst_base/sessions/$sid"

      safe_copy "$session_dir/conversation.json"  "$dst_dir/conversation.json"
      safe_copy "$session_dir/metadata.json"      "$dst_dir/metadata.json"

      [[ -f "$session_dir/conversation.json" ]] && session_count=$((session_count + 1))
    done
  fi

  # Debug logs (optional — useful for model/routing analysis)
  if [[ -d "$src_base/tmp" ]]; then
    for log_f in "$src_base/tmp"/gemini-debug-*.log; do
      [[ -f "$log_f" ]] && safe_copy "$log_f" "$dst_base/logs/$(basename "$log_f")"
    done
  fi

  ok "Gemini: scanned $session_count sessions"
}

# ─── 3. OpenCode CLI ──────────────────────────────────────────────────────────
# OpenCode is the primary TUI for XNAi terminal work. ACTIVE — fork planned.
# Antigravity Auth plugin (opencode-antigravity-auth@latest) runs inside OpenCode
# to unlock GitHub OAuth premium models — it is NOT a separate CLI.
harvest_opencode() {
  local src_base="$HOME/.opencode"
  local dst_base="$IMPORT_BASE/opencode"

  if [[ ! -d "$src_base" ]]; then
    warn "OpenCode data not found: $src_base"
    return
  fi

  info "Harvesting OpenCode CLI sessions from $src_base"
  local session_count=0

  if [[ -d "$src_base/sessions" ]]; then
    for session_file in "$src_base/sessions"/*.json; do
      [[ -f "$session_file" ]] || continue
      safe_copy "$session_file" "$dst_base/sessions/$(basename "$session_file")"
      session_count=$((session_count + 1))
    done
  fi

  # Grab logs for model/routing analysis
  if [[ -d "$src_base/logs" ]]; then
    for log_f in "$src_base/logs"/*.log; do
      [[ -f "$log_f" ]] && safe_copy "$log_f" "$dst_base/logs/$(basename "$log_f")"
    done
  fi

  ok "OpenCode: scanned $session_count sessions"
}

# ─── 4. Cline (VSCodium extension) ───────────────────────────────────────────
harvest_cline() {
  local src_base="$HOME/.config/VSCodium/User/globalStorage/saoudrizwan.claude-dev/tasks"
  local dst_base="$IMPORT_BASE/cline"

  # Fallback for VS Code
  if [[ ! -d "$src_base" ]]; then
    src_base="$HOME/.config/Code/User/globalStorage/saoudrizwan.claude-dev/tasks"
  fi

  if [[ ! -d "$src_base" ]]; then
    warn "Cline tasks not found at expected locations"
    return
  fi

  info "Harvesting Cline tasks from $src_base"
  local task_count=0

  for task_dir in "$src_base"/*/; do
    [[ -d "$task_dir" ]] || continue
    local tid
    tid="$(basename "$task_dir")"
    local dst_dir="$dst_base/$tid"

    # api_conversation_history.json — PRIMARY (full API message history)
    safe_copy "$task_dir/api_conversation_history.json"  "$dst_dir/api_conversation_history.json"
    # ui_messages.json — UI layer (supplementary)
    safe_copy "$task_dir/ui_messages.json"               "$dst_dir/ui_messages.json"

    [[ -f "$task_dir/api_conversation_history.json" ]] && task_count=$((task_count + 1))
  done

  ok "Cline: scanned $task_count task histories"
}

# ─── 5. Write harvest manifest ────────────────────────────────────────────────
write_manifest() {
  local manifest="$IMPORT_BASE/harvest-manifest-${TIMESTAMP}.json"
  cat > "$manifest" << EOF
{
  "harvest_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "dry_run": $DRY_RUN,
  "target_cli": "$TARGET_CLI",
  "stats": {
    "total_copied": $HARVEST_COUNT,
    "total_skipped": $SKIP_COUNT,
    "total_errors": $ERROR_COUNT
  },
  "destinations": {
    "copilot":  "$IMPORT_BASE/copilot",
    "gemini":   "$IMPORT_BASE/gemini",
    "opencode": "$IMPORT_BASE/opencode",
    "cline":    "$IMPORT_BASE/cline"
  },
  "next_step": "Run app/XNAi_rag_app/conversation_ingestion.py to ingest into Qdrant xnai_conversations"
}
EOF
  ok "Manifest written: $manifest"
}

# ─── 6. Optional Qdrant Ingestion ─────────────────────────────────────────────
run_ingestion() {
  if [[ "$DO_INGEST" != "true" ]]; then
    return
  fi

  info "── Triggering Qdrant Ingestion ──"
  local ingestion_script="$REPO_ROOT/app/XNAi_rag_app/conversation_ingestion.py"

  if [[ ! -f "$ingestion_script" ]]; then
    err "Ingestion script not found: $ingestion_script"
    return 1
  fi

  python3 "$ingestion_script" \
    --import-dir "$IMPORT_BASE" \
    --collection xnai_conversations

  ok "Qdrant ingestion complete"
}

# ─── Main ─────────────────────────────────────────────────────────────────────
main() {
  info "=== XNAi CLI Session Harvest v1.1.0 ==="
  info "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  info "Dry run:   $DRY_RUN"
  info "Target:    $TARGET_CLI"
  info "Ingest:    $DO_INGEST"
  info "Base dir:  $IMPORT_BASE"
  echo ""

  mkdir -p "$IMPORT_BASE"/{copilot,gemini,opencode,cline}

  case "$TARGET_CLI" in
    copilot)  harvest_copilot ;;
    gemini)   harvest_gemini ;;
    opencode) harvest_opencode ;;
    cline)    harvest_cline ;;
    all)
      harvest_copilot
      harvest_gemini
      harvest_opencode
      harvest_cline
      ;;
    *) err "Unknown CLI: $TARGET_CLI"; exit 1 ;;
  esac

  echo ""
  info "=== Harvest Complete ==="
  ok   "Copied:  $HARVEST_COUNT files"
  [[ $SKIP_COUNT  -gt 0 ]] && warn "Skipped: $SKIP_COUNT files (up-to-date)"
  [[ $ERROR_COUNT -gt 0 ]] && err  "Errors:  $ERROR_COUNT"
  info "Log:     $LOG_FILE"

  if [[ "$DRY_RUN" == "false" && $HARVEST_COUNT -gt 0 ]]; then
    write_manifest
  fi

  run_ingestion

  if [[ "$DRY_RUN" == "false" && $HARVEST_COUNT -gt 0 && "$DO_INGEST" == "false" ]]; then
    echo ""
    info "Next: ingest into Qdrant with:"
    info "  python app/XNAi_rag_app/conversation_ingestion.py --import-dir $IMPORT_BASE --collection xnai_conversations"
    info "Or re-run with --ingest flag."
  fi
}

main "$@"

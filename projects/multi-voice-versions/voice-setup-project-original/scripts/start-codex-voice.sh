#!/usr/bin/env bash
set -euo pipefail

DEFAULT_WORKSPACE="/Users/buck/Documents/voice-setup-project"
workspace="${1:-$DEFAULT_WORKSPACE}"

if [[ ! -d "$workspace" ]]; then
  echo "Workspace does not exist: $workspace" >&2
  exit 1
fi

if command -v codex >/dev/null 2>&1; then
  exec codex app "$workspace"
fi

open -a "/Applications/Codex.app" "$workspace"


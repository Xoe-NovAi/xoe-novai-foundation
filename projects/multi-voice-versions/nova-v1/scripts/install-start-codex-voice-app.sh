#!/usr/bin/env bash
set -euo pipefail

DEFAULT_WORKSPACE="/Users/buck/Documents/voice-setup-project"
DEFAULT_APP_PATH="/Applications/Start Codex Voice.app"

workspace="${1:-$DEFAULT_WORKSPACE}"
app_path="${2:-$DEFAULT_APP_PATH}"

if [[ ! -d "$workspace" ]]; then
  echo "Workspace does not exist: $workspace" >&2
  exit 1
fi

if ! command -v osacompile >/dev/null 2>&1; then
  echo "osacompile is required (macOS)." >&2
  exit 1
fi

workspace_js="${workspace//\\/\\\\}"
workspace_js="${workspace_js//\"/\\\"}"

tmp_script="$(mktemp -t start_codex_voice.XXXXXX.js)"
trap 'rm -f "$tmp_script"' EXIT

cat > "$tmp_script" <<EOF
function run(argv) {
  var app = Application.currentApplication();
  app.includeStandardAdditions = true;
  var workspacePath = "$workspace_js";
  var commandLine = "codex app " + JSON.stringify(workspacePath);
  app.doShellScript("/bin/zsh -lc " + JSON.stringify(commandLine));
}
EOF

osacompile -l JavaScript -o "$app_path" "$tmp_script"

echo "Created: $app_path"
echo "You can now assign a macOS keyboard shortcut for 'Start Codex Voice'."

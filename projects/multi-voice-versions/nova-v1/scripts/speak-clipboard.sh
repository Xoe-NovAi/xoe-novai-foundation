#!/usr/bin/env bash
set -euo pipefail

voice="${VOICE_NAME:-Samantha}"
rate="${VOICE_RATE:-190}"

if [[ "$#" -gt 0 ]]; then
  text="$*"
else
  text="$(pbpaste)"
fi

if [[ -z "${text//[[:space:]]/}" ]]; then
  echo "No text provided and clipboard is empty." >&2
  exit 1
fi

say -v "$voice" -r "$rate" "$text"


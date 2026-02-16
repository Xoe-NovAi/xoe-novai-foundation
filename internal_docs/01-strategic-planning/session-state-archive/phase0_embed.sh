#!/usr/bin/env bash
# Wrapper to run phase0_embed.py in a virtualenv
set -euo pipefail
REPO_ROOT="/home/arcana-novai/Documents/xnai-foundation"
INPUT_DIR="$REPO_ROOT/internal_docs/01-strategic-planning/sessions/02_16_2026_phase5_operationalization"
OUT_DIR="$HOME/.copilot/session-state/phase0_embed_output"
BATCH_SIZE=6

python3 /home/arcana-novai/.copilot/session-state/600a4354-1bd2-4f7c-aacd-366110f48273/phase0_embed.py --input-dir "$INPUT_DIR" --outdir "$OUT_DIR" --batch-size "$BATCH_SIZE"

echo "Embedding script staged. Review $OUT_DIR for manifests and outputs (if run)."

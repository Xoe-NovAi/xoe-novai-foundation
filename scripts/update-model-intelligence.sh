#!/usr/bin/env bash
# update-model-intelligence.sh
# Fetches live model data from OpenRouter and writes a JSON snapshot
# to expert-knowledge/model-snapshots/ for RAG ingestion and CI diffing.
#
# Usage:
#   ./scripts/update-model-intelligence.sh
#   ./scripts/update-model-intelligence.sh --output /tmp/models.json
#
# Dependencies: curl, jq, python3 (all available on this system)
# Runs: manually OR via .github/workflows/model-intelligence-update.yml (weekly)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SNAPSHOT_DIR="${REPO_ROOT}/expert-knowledge/model-snapshots"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DATE_SLUG="$(date -u +%Y-%m-%d)"
OUTPUT_FILE="${SNAPSHOT_DIR}/openrouter-models-${DATE_SLUG}.json"
LATEST_FILE="${SNAPSHOT_DIR}/openrouter-models-latest.json"
PREV_FILE="${SNAPSHOT_DIR}/openrouter-models-previous.json"

# Allow override via --output flag
if [[ "${1:-}" == "--output" && -n "${2:-}" ]]; then
  OUTPUT_FILE="$2"
fi

echo "🔍 XNAi Model Intelligence Updater"
echo "   Timestamp: ${TIMESTAMP}"
echo "   Output:    ${OUTPUT_FILE}"
echo ""

# Create snapshot directory if it doesn't exist
mkdir -p "${SNAPSHOT_DIR}"

# ─── STEP 1: Fetch OpenRouter model list ─────────────────────────────────────
echo "📡 Fetching OpenRouter model list..."
RAW_RESPONSE=$(curl -sf \
  -H "Content-Type: application/json" \
  "https://openrouter.ai/api/v1/models" \
  --max-time 30 \
  --retry 3 \
  --retry-delay 5 \
  2>&1) || {
  echo "❌ Failed to fetch from OpenRouter API"
  exit 1
}

MODEL_COUNT=$(echo "$RAW_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('data',[])))" 2>/dev/null || echo "0")
echo "   Found ${MODEL_COUNT} models on OpenRouter"

# ─── STEP 2: Write dated snapshot ────────────────────────────────────────────
echo "$RAW_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
output = {
    'fetched_at': '${TIMESTAMP}',
    'source': 'https://openrouter.ai/api/v1/models',
    'model_count': len(data.get('data', [])),
    'models': [
        {
            'id': m.get('id', ''),
            'name': m.get('name', ''),
            'context_length': m.get('context_length', 0),
            'pricing': m.get('pricing', {}),
            'architecture': m.get('architecture', {}),
            'top_provider': m.get('top_provider', {}),
        }
        for m in data.get('data', [])
    ]
}
print(json.dumps(output, indent=2))
" > "${OUTPUT_FILE}"

echo "✅ Snapshot written: ${OUTPUT_FILE}"

# ─── STEP 3: Detect new models vs previous snapshot ──────────────────────────
if [[ -f "${LATEST_FILE}" ]]; then
  echo ""
  echo "🔄 Comparing with previous snapshot..."

  PREV_IDS=$(python3 -c "
import json
with open('${LATEST_FILE}') as f:
    d = json.load(f)
print('\n'.join(m['id'] for m in d.get('models', [])))
" 2>/dev/null | sort || echo "")

  NEW_IDS=$(python3 -c "
import json
with open('${OUTPUT_FILE}') as f:
    d = json.load(f)
print('\n'.join(m['id'] for m in d.get('models', [])))
" 2>/dev/null | sort || echo "")

  NEW_MODELS=$(comm -23 <(echo "$NEW_IDS") <(echo "$PREV_IDS") 2>/dev/null || echo "")
  REMOVED_MODELS=$(comm -13 <(echo "$NEW_IDS") <(echo "$PREV_IDS") 2>/dev/null || echo "")

  if [[ -n "$NEW_MODELS" ]]; then
    echo ""
    echo "🆕 NEW MODELS DETECTED:"
    echo "$NEW_MODELS" | while read -r model; do
      echo "   + ${model}"
    done
    # Write new models list for GitHub Actions to pick up
    echo "$NEW_MODELS" > "${SNAPSHOT_DIR}/new-models-${DATE_SLUG}.txt"
    echo "   Saved to: ${SNAPSHOT_DIR}/new-models-${DATE_SLUG}.txt"
  else
    echo "   No new models detected"
  fi

  if [[ -n "$REMOVED_MODELS" ]]; then
    echo ""
    echo "🗑️  REMOVED MODELS:"
    echo "$REMOVED_MODELS" | while read -r model; do
      echo "   - ${model}"
    done
  fi

  # Archive previous
  cp "${LATEST_FILE}" "${PREV_FILE}" 2>/dev/null || true
fi

# ─── STEP 4: Update latest symlink/file ──────────────────────────────────────
cp "${OUTPUT_FILE}" "${LATEST_FILE}"
echo ""
echo "📌 Updated latest: ${LATEST_FILE}"

# ─── STEP 5: Free tier models quick report ───────────────────────────────────
echo ""
echo "🆓 Free models on OpenRouter:"
python3 -c "
import json
with open('${OUTPUT_FILE}') as f:
    d = json.load(f)
free_models = [
    m for m in d.get('models', [])
    if str(m.get('pricing', {}).get('prompt', '1')) == '0'
       or float(m.get('pricing', {}).get('prompt', '1') or '1') == 0.0
]
for m in sorted(free_models, key=lambda x: x['id'])[:30]:
    ctx = m.get('context_length', 0)
    ctx_str = f'{ctx//1000}K' if ctx else 'N/A'
    print(f'  {m[\"id\"]:<55} {ctx_str}')
print(f'  Total free models: {len(free_models)}')
" 2>/dev/null || echo "  (could not parse free models)"

echo ""
echo "✨ Model intelligence update complete!"
echo "   Next steps:"
echo "   1. Review ${OUTPUT_FILE}"
echo "   2. Run: python3 app/XNAi_rag_app/model_intelligence_ingestion.py --ingest ${OUTPUT_FILE}"
echo "   3. Check ${SNAPSHOT_DIR}/new-models-${DATE_SLUG}.txt for alerts"

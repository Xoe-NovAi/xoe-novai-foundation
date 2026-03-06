#!/bin/bash
# Simple check to enforce image size budget
# Usage: scripts/check_image_sizes.sh [size_limit_mb]

set -e
LIMIT_MB=${1:-500}

images=(
  "xnai-base:latest"
  "xnai-base-build:latest"
  "localhost/xnai-rag:latest"
  "localhost/xnai-ui:latest"
  "localhost/xnai-crawl:latest"
  "localhost/xnai-curation-worker:latest"
)

fail=0
for img in "${images[@]}"; do
    size=$(docker image inspect "$img" --format='{{.Size}}' 2>/dev/null || echo 0)
    if [[ "$size" -eq 0 ]]; then
        echo "⚠️  Image $img not present";
        continue
    fi
    mb=$((size/1024/1024))
    if [[ $mb -gt $LIMIT_MB ]]; then
        echo "❌ $img is ${mb}MB which exceeds ${LIMIT_MB}MB";
        fail=1
    else
        echo "✅ $img is ${mb}MB";
    fi
done

if [[ $fail -ne 0 ]]; then
    exit 1
fi

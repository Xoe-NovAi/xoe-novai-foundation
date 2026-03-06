#!/usr/bin/env bash
# Bootstrap a new research project directory and Vikunja project

set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <slug> [title] [description]"
    exit 1
fi

SLUG="$1"
TITLE="${2:-$SLUG}"
DESCRIPTION="${3:-}"
DATE=$(date +%Y%m%d)
BASE="research/${DATE}-${SLUG}"

mkdir -p "$BASE"/{code,data,outputs}
cat <<EOF > "$BASE/notes.md"
# Research: $TITLE

*Slug*: $SLUG
*Created*: $(date --iso-8601=minutes)

## Overview

$DESCRIPTION

## Progress

- [ ] Project initialization
- [ ] Research planning
- [ ] Data collection
- [ ] Analysis and synthesis
- [ ] Documentation

## Results

(To be filled during research execution)

EOF

cat <<EOF > "$BASE/meta.yaml"
slug: $SLUG
title: "$TITLE"
description: "$DESCRIPTION"
status: open
domain_tags: []
created_at: $(date --iso-8601=seconds)
updated_at: $(date --iso-8601=seconds)
vikunja_project_id: null
EOF

# record in index
INDEX="research/index.json"
mkdir -p research
if ! grep -q "$SLUG" "$INDEX" 2>/dev/null; then
    jq --arg slug "$SLUG" --arg path "$BASE" '. + [{slug:$slug,path:$path}]' "$INDEX" 2>/dev/null || echo "[{\"slug\":\"$SLUG\",\"path\":\"$BASE\"}]" > "$INDEX"
fi

echo "✅ Created new research project at $BASE"

# Create Vikunja project if API token is available
if [ -n "${VIKUNJA_API_TOKEN:-}" ] && [ -n "${VIKUNJA_URL:-}" ]; then
    echo "🔗 Creating Vikunja project..."
    
    # Use Python script for Vikunja integration
    if command -v python3 >/dev/null 2>&1; then
        VIKUNJA_PROJECT_ID=$(python3 -c "
import sys
sys.path.append('scripts')
from vikunja_integration import create_vikunja_project_for_research
result = create_vikunja_project_for_research('$SLUG', '$TITLE', '$DESCRIPTION')
print(result if result else '')
" 2>/dev/null)
        
        if [ -n "$VIKUNJA_PROJECT_ID" ]; then
            echo "✅ Vikunja project created with ID: $VIKUNJA_PROJECT_ID"
            
            # Update meta.yaml with Vikunja project ID
            python3 -c "
import yaml
with open('$BASE/meta.yaml', 'r') as f:
    data = yaml.safe_load(f)
data['vikunja_project_id'] = $VIKUNJA_PROJECT_ID
with open('$BASE/meta.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False)
"
        else
            echo "⚠️  Failed to create Vikunja project (check API token and URL)"
        fi
    else
        echo "⚠️  Python3 not available, skipping Vikunja integration"
    fi
else
    echo "⚠️  Vikunja integration skipped (set VIKUNJA_API_TOKEN and VIKUNJA_URL environment variables)"
fi

echo ""
echo "📋 Next steps:"
echo "1. Update $BASE/notes.md with research details"
echo "2. Add domain tags to $BASE/meta.yaml"
echo "3. Use 'omega agent list-jobs' to see available jobs"
echo "4. Use 'omega agent claim <agent_id> <job_id>' to claim this job"
echo ""
echo "📚 Research project ready at: $BASE"

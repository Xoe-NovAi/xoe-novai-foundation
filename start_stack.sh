#!/bin/bash
set -a
source "/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/.env"
set +a

# --- Check for Deprecated Architectural Documents ---
DEPRECATION_SCHEDULE_FILE="/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/memory_bank/DEPRECATION_SCHEDULE.md"
if [ -f "$DEPRECATION_SCHEDULE_FILE" ]; then
    CURRENT_DATE=$(date +%Y-%m-%d)
    # Read the file, skip header and lines that are not PENDING, then check dates
    grep "PENDING" "$DEPRECATION_SCHEDULE_FILE" | while IFS='|' read -r deprecated_file transmuted_to review_date status; do
        # Clean up whitespace and extract just the date
        CLEAN_REVIEW_DATE=$(echo "$review_date" | xargs)
        if [[ "$CLEAN_REVIEW_DATE" < "$CURRENT_DATE" ]]; then
            echo "--- ARCHITECTURAL DOCUMENTATION WARNING ---"
            echo "The following document is marked for review and archival:"
            echo "  Deprecated: $(echo "$deprecated_file" | xargs)"
            echo "  Transmuted To: $(echo "$transmuted_to" | xargs)"
            echo "  Review Date: $CLEAN_REVIEW_DATE (PAST DUE)"
            echo "Please review 'memory_bank/DEPRECATION_SCHEDULE.md' and update accordingly."
            echo "------------------------------------------"
        fi
    done
fi
# --- End Deprecation Check ---

podman-compose -f "/home/arcana-novai/Documents/Xoe-NovAi/omega-stack/infra/docker/docker-compose.yml" up -d

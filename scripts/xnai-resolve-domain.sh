#!/bin/bash
# xnai-resolve-domain.sh - Canonical domain resolver for Omega Stack
# Sources: config/metropolis-domains.yaml or config/domain-routing.yaml

resolve_domain() {
    local flag="$1"
    INSTANCE_ID=1
    DOMAIN_NAME="General"

    # 1. Resolve OMEGA_ROOT
    if [ -z "$OMEGA_ROOT" ]; then
        OMEGA_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    fi

    # 2. Check for direct instance flag: --instance-N
    if [[ "$flag" =~ ^--instance-([1-8])$ ]]; then
        INSTANCE_ID="${BASH_REMATCH[1]}"
        DOMAIN_NAME="Direct (Instance $INSTANCE_ID)"
        return 0
    fi

    # 3. Check for domain flags (e.g., --architect, --api)
    if [[ "$flag" =~ ^--([a-zA-Z0-9_-]+)$ ]]; then
        local domain="${BASH_REMATCH[1]}"
        
        # Try metropolis-domains.yaml (Legacy/Metropolis compatibility)
        local METROPOLIS_CONFIG="${OMEGA_ROOT}/config/metropolis-domains.yaml"
        if [[ -f "$METROPOLIS_CONFIG" ]]; then
            INSTANCE_ID=$(python3 -c "
import yaml, sys
try:
    data = yaml.safe_load(open('$METROPOLIS_CONFIG'))
    print(data.get('domains', {}).get('$domain', {}).get('id', ''))
except: pass
" 2>/dev/null)
            if [[ -n "$INSTANCE_ID" ]]; then
                DOMAIN_NAME="$domain"
                return 0
            fi
        fi

        # Fallback to hardcoded safe defaults
        declare -A _FALLBACK
        _FALLBACK[architect]=1; _FALLBACK[api]=2; _FALLBACK[ui]=3; _FALLBACK[voice]=4
        _FALLBACK[data]=5; _FALLBACK[ops]=6; _FALLBACK[research]=7; _FALLBACK[test]=8
        
        if [[ -n "${_FALLBACK[$domain]:-}" ]]; then
            INSTANCE_ID="${_FALLBACK[$domain]}"
            DOMAIN_NAME="$domain"
            return 0
        fi
    fi

    return 1
}

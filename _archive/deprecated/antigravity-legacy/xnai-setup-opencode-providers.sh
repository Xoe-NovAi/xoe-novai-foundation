#!/bin/bash
# OpenCode Provider Credential Injection Script (XNAi Optimized)
# Usage: ./scripts/xnai-setup-opencode-providers.sh

set -euo pipefail

CREDS_FILE="${HOME}/.config/xnai/opencode-credentials.yaml"
AUTH_FILE="${HOME}/.local/share/opencode/auth.json"
OPENCODE_JSON="$(pwd)/.opencode/opencode.json"

# Helper function to convert YAML to JSON for jq
# Using Python as a workaround for missing yq
yaml2json() {
    python3 -c "import yaml, json, sys; print(json.dumps(yaml.safe_load(sys.stdin)))"
}

# Function: Load API key from env var or credential file
get_api_key() {
    local provider=$1
    local key_env_var=$2
    
    # Try env var first
    if [[ -n "${!key_env_var:-}" ]]; then
        echo "${!key_env_var}"
        return 0
    fi
    
    # Fallback to YAML (using Python + jq workaround)
    cat "$CREDS_FILE" | yaml2json | jq -r ".providers.$provider.api_key // empty"
}

# Function: Inject into auth.json
inject_provider_auth() {
    local provider=$1
    local auth_key=$2
    local auth_value=$3
    
    jq --arg prov "$provider" \
       --arg key "$auth_key" \
       --arg val "$auth_value" \
       '.[$prov][$key] = $val' \
       "$AUTH_FILE" > "$AUTH_FILE.tmp" && mv "$AUTH_FILE.tmp" "$AUTH_FILE"
}

# Function: Inject complete provider object into auth.json
inject_provider_obj() {
    local provider=$1
    local obj_json=$2
    
    jq --arg prov "$provider" \
       --argjson obj "$obj_json" \
       '.[$prov] = $obj' \
       "$AUTH_FILE" > "$AUTH_FILE.tmp" && mv "$AUTH_FILE.tmp" "$AUTH_FILE"
}

# Main loop: For each provider in credentials
echo "⚙️  Injecting provider credentials..."

if [[ ! -f "$CREDS_FILE" ]]; then
    echo "❌ Credential file not found: $CREDS_FILE"
    echo "Please copy config/templates/opencode-credentials.yaml.template to $CREDS_FILE"
    exit 1
fi

if [[ ! -f "$AUTH_FILE" ]]; then
    echo "❌ Auth file not found: $AUTH_FILE"
    echo "Please ensure OpenCode is installed and has created auth.json"
    exit 1
fi

# Get JSON representation of credentials
creds_json=$(cat "$CREDS_FILE" | yaml2json)

# Check for root key (providers or credentials)
if echo "$creds_json" | jq -e '.providers' >/dev/null; then
    providers_json=$(echo "$creds_json" | jq -c '.providers')
elif echo "$creds_json" | jq -e '.credentials' >/dev/null; then
    providers_json=$(echo "$creds_json" | jq -c '.credentials')
else
    # Try using the root object if no known keys found
    providers_json="$creds_json"
fi

# Get all providers from JSON
providers=$(echo "$providers_json" | jq -r 'keys | .[]')

for provider in $providers; do
    echo "  Processing $provider..."
    
    case "$provider" in
        antigravity)
            # Load first active account
            provider_creds=$(echo "$providers_json" | jq -c '.antigravity')
            if echo "$provider_creds" | jq -e '.accounts' >/dev/null; then
                creds_item=$(echo "$provider_creds" | jq -c '.accounts[0]')
            else
                creds_item="$provider_creds"
            fi
            
            access_token=$(echo "$creds_item" | jq -r '.access_token // .api_key // empty')
            refresh_token=$(echo "$creds_item" | jq -r '.refresh_token // empty')
            
            if [[ -n "$access_token" && "$access_token" != "null" ]]; then
                # Antigravity requires OAuth authentication with access tokens
                auth_obj="{\"type\": \"oauth\", \"access\": \"$access_token\""
                if [[ -n "$refresh_token" && "$refresh_token" != "null" ]]; then
                    auth_obj="$auth_obj, \"refresh\": \"$refresh_token\""
                fi
                auth_obj="$auth_obj, \"expires\": 0}"
                
                inject_provider_obj "google" "$auth_obj"
                echo "    ✓ Antigravity (${access_token:0:10}...)"
            else
                echo "    ⚠ No access token found for Antigravity"
            fi
            ;;
        openrouter|together|groq|opencode)
            provider_creds=$(echo "$providers_json" | jq -c ".\"$provider\"")
            
            # Handle different key names (api_key, apiKey, key)
            api_key=$(echo "$provider_creds" | jq -r '.api_key // .apiKey // .key // empty')
            
            # Check env var fallback if empty
            if [[ -z "$api_key" || "$api_key" == "null" ]]; then
                key_env_var=$(echo "$provider_creds" | jq -r '.api_key_env // empty')
                if [[ -n "$key_env_var" ]]; then
                    api_key="${!key_env_var:-}"
                fi
            fi
            
            if [[ -n "$api_key" && "$api_key" != "null" ]]; then
                # Special case for opencode (internal name in auth.json)
                auth_name="$provider"
                [[ "$provider" == "opencode" ]] && auth_name="opencode"
                
                inject_provider_auth "$auth_name" "key" "$api_key"
                echo "    ✓ $provider"
            fi
            ;;
    esac
done

echo "✅ Provider injection complete!"
echo "Run: opencode --model google/antigravity-claude-opus-4-6-thinking to test"

#!/bin/bash
# ---
# tool: cline
# model: claude-sonnet-4-6
# account: arcana-novai
# git_branch: main
# session_id: sprint6-2026-02-18
# version: v1.1.0
# created: 2026-02-18
# updated: 2026-02-18
# changelog: Added agent-identity.yaml lookup + interactive prompt fallback
# ---
#
# sign-document.sh — Inject YAML frontmatter into .md files
# Part of the XNAi Document Signing Protocol
# See: expert-knowledge/protocols/DOCUMENT-SIGNING-PROTOCOL.md
#
# Usage:
#   ./scripts/sign-document.sh <file.md> [OPTIONS]
#   ./scripts/sign-document.sh --batch <directory> [OPTIONS]
#
# Options:
#   --tool      Tool name (cline|opencode|gemini-cli|copilot|human|script)
#   --model     Model name (auto-looked-up from configs/agent-identity.yaml if omitted)
#   --account   Account (default: arcana-novai)
#   --branch    Git branch (default: current branch)
#   --session   Session ID (default: manual-YYYY-MM-DD)
#   --version   Document version (default: v1.0.0)
#   --tags      Comma-separated tags (default: "document")
#   --force     Overwrite existing frontmatter
#   --dry-run   Show what would be done without writing

set -euo pipefail

# ─── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

log()     { echo -e "${CYAN}[sign]${NC} $*"; }
success() { echo -e "${GREEN}[sign]${NC} ✅ $*"; }
warn()    { echo -e "${YELLOW}[sign]${NC} ⚠️  $*"; }
error()   { echo -e "${RED}[sign]${NC} ❌ $*" >&2; }

# ─── Defaults ─────────────────────────────────────────────────────────────────
TOOL="human"
MODEL=""        # empty = auto-lookup from configs/agent-identity.yaml
ACCOUNT="arcana-novai"
BRANCH=""
SESSION_ID=""
VERSION="v1.0.0"
TAGS="document"
FORCE=false
DRY_RUN=false
BATCH=false
BATCH_DIR=""
TARGET_FILE=""

# ─── Agent Identity Lookup ────────────────────────────────────────────────────
# Reads configs/agent-identity.yaml to get model/account for a given tool.
# Falls back to interactive prompt if tool not found or yaml unavailable.
SCRIPT_DIR_SIGN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT_SIGN="$(cd "$SCRIPT_DIR_SIGN/.." && pwd)"
AGENT_IDENTITY_FILE="$REPO_ROOT_SIGN/configs/agent-identity.yaml"

lookup_agent_identity() {
    local tool="$1"

    if [[ ! -f "$AGENT_IDENTITY_FILE" ]]; then
        warn "configs/agent-identity.yaml not found — using interactive prompt"
        prompt_for_model "$tool"
        return
    fi

    # Use python3 to parse YAML (available on all XNAi systems)
    local result
    result=$(python3 - "$tool" "$AGENT_IDENTITY_FILE" << 'PYEOF'
import sys, re

tool = sys.argv[1]
yaml_file = sys.argv[2]

with open(yaml_file) as f:
    content = f.read()

# Find the agents section for the given tool (simple regex-based parse)
# Pattern: match "  <tool>:" then find "model: <value>" within ~20 lines
lines = content.split('\n')
in_agent = False
agent_indent = 0
found_model = None
found_account = None

for i, line in enumerate(lines):
    # Look for the tool entry under agents:
    stripped = line.lstrip()
    indent = len(line) - len(stripped)

    if stripped.startswith(f'{tool}:') and indent == 2:
        in_agent = True
        agent_indent = indent
        continue

    if in_agent:
        # Stop if we hit another top-level agent entry (indent == 2)
        if indent == 2 and stripped and not stripped.startswith('#'):
            break
        m = re.match(r'\s+model:\s+(.+)', line)
        if m:
            found_model = m.group(1).strip().strip('"\'')
        a = re.match(r'\s+account:\s+(.+)', line)
        if a:
            found_account = a.group(1).strip().strip('"\'')

if found_model:
    print(f"model={found_model}")
if found_account:
    print(f"account={found_account}")
PYEOF
    2>/dev/null)

    if [[ -n "$result" ]]; then
        local looked_up_model
        local looked_up_account
        looked_up_model=$(echo "$result" | grep '^model=' | cut -d= -f2)
        looked_up_account=$(echo "$result" | grep '^account=' | cut -d= -f2)

        if [[ -n "$looked_up_model" ]]; then
            MODEL="$looked_up_model"
            log "Auto-resolved model for '$tool': $MODEL (from configs/agent-identity.yaml)"
        fi
        if [[ -n "$looked_up_account" && "$ACCOUNT" == "arcana-novai" ]]; then
            ACCOUNT="$looked_up_account"
        fi
    else
        warn "Tool '$tool' not found in configs/agent-identity.yaml"
        prompt_for_model "$tool"
    fi
}

prompt_for_model() {
    local tool="$1"

    if [[ ! -t 0 ]]; then
        # Non-interactive (piped/scripted) — use unknown
        warn "Non-interactive mode and model unknown — using 'unknown'. Pass --model to fix."
        MODEL="unknown"
        return
    fi

    echo ""
    warn "Cannot auto-detect model for tool: $tool"
    echo -e "${CYAN}  Tool '$tool' not found in configs/agent-identity.yaml.${NC}"
    echo -e "${CYAN}  Common models:${NC}"
    echo -e "    claude-sonnet-4-6    (Cline VSCodium)"
    echo -e "    big-pickle           (OpenCode built-in)"
    echo -e "    gemini-2.5-pro       (Gemini CLI)"
    echo -e "    gpt-4o               (Copilot CLI)"
    echo -e "    unknown              (human/manual)"
    echo ""
    read -r -p "  Enter model name [unknown]: " user_model
    MODEL="${user_model:-unknown}"
    log "Model set to: $MODEL"
    echo ""
}

# ─── Detect Git Branch ────────────────────────────────────────────────────────
detect_branch() {
    if git rev-parse --is-inside-work-tree &>/dev/null; then
        git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main"
    else
        echo "main"
    fi
}

# ─── Detect Git Commit ────────────────────────────────────────────────────────
detect_commit() {
    if git rev-parse --is-inside-work-tree &>/dev/null; then
        git rev-parse --short HEAD 2>/dev/null || echo ""
    else
        echo ""
    fi
}

# ─── Parse Arguments ──────────────────────────────────────────────────────────
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --tool)      TOOL="$2"; shift 2 ;;
            --model)     MODEL="$2"; shift 2 ;;
            --account)   ACCOUNT="$2"; shift 2 ;;
            --branch)    BRANCH="$2"; shift 2 ;;
            --session)   SESSION_ID="$2"; shift 2 ;;
            --version)   VERSION="$2"; shift 2 ;;
            --tags)      TAGS="$2"; shift 2 ;;
            --force)     FORCE=true; shift ;;
            --dry-run)   DRY_RUN=true; shift ;;
            --batch)     BATCH=true; BATCH_DIR="$2"; shift 2 ;;
            --help|-h)   show_help; exit 0 ;;
            -*)          error "Unknown option: $1"; exit 1 ;;
            *)
                if [[ -z "$TARGET_FILE" ]]; then
                    TARGET_FILE="$1"
                fi
                shift
                ;;
        esac
    done

    # Set defaults
    [[ -z "$BRANCH" ]] && BRANCH=$(detect_branch)
    [[ -z "$SESSION_ID" ]] && SESSION_ID="manual-$(date +%Y-%m-%d)"

    # Auto-resolve model from agent-identity.yaml if not explicitly set
    if [[ -z "$MODEL" ]]; then
        lookup_agent_identity "$TOOL"
    fi
    # Final fallback
    [[ -z "$MODEL" ]] && MODEL="unknown"
}

# ─── Show Help ────────────────────────────────────────────────────────────────
show_help() {
    cat << 'EOF'
sign-document.sh — Inject YAML frontmatter into markdown files

USAGE:
  ./scripts/sign-document.sh <file.md> [OPTIONS]
  ./scripts/sign-document.sh --batch <directory> [OPTIONS]

OPTIONS:
  --tool      Tool (cline|opencode|gemini-cli|copilot|human|script)
  --model     Model (claude-opus-4-5|gemini-2.0-flash|gpt-4o|...)
  --account   Account identifier (default: arcana-novai)
  --branch    Git branch (default: auto-detected)
  --session   Session ID (default: manual-YYYY-MM-DD)
  --version   Document version (default: v1.0.0)
  --tags      Comma-separated tags (default: "document")
  --force     Overwrite existing frontmatter
  --dry-run   Show what would be done without writing
  --help      Show this help

EXAMPLES:
  # Sign a single file
  ./scripts/sign-document.sh docs/README.md --tool human --model unknown

  # Sign with Cline session info (model auto-resolved from configs/agent-identity.yaml)
  ./scripts/sign-document.sh expert-knowledge/research/new-doc.md \
    --tool cline \
    --session sprint5-2026-02-18 \
    --tags "research,ai,protocol"

  # Batch sign all unsigned .md files in a directory
  ./scripts/sign-document.sh --batch expert-knowledge/ \
    --tool human --model unknown --force

  # Dry run to preview
  ./scripts/sign-document.sh docs/guide.md --tool cline --dry-run
EOF
}

# ─── Check if File Has Frontmatter ────────────────────────────────────────────
has_frontmatter() {
    local file="$1"
    head -1 "$file" | grep -q "^---$"
}

# ─── Convert comma tags to YAML list ─────────────────────────────────────────
tags_to_yaml() {
    local tags="$1"
    # Convert "tag1,tag2,tag3" → "[tag1, tag2, tag3]"
    local formatted
    formatted=$(echo "$tags" | sed 's/,/, /g' | sed 's/^/[/' | sed 's/$/]/')
    echo "$formatted"
}

# ─── Build Frontmatter ────────────────────────────────────────────────────────
build_frontmatter() {
    local file="$1"
    local today
    today=$(date +%Y-%m-%d)
    local commit
    commit=$(detect_commit)
    local yaml_tags
    yaml_tags=$(tags_to_yaml "$TAGS")

    cat << EOF
---
tool: ${TOOL}
model: ${MODEL}
account: ${ACCOUNT}
git_branch: ${BRANCH}$([ -n "$commit" ] && echo "
git_commit: ${commit}" || echo "")
session_id: ${SESSION_ID}
version: ${VERSION}
created: ${today}
tags: ${yaml_tags}
---
EOF
}

# ─── Sign Single File ─────────────────────────────────────────────────────────
sign_file() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        error "File not found: $file"
        return 1
    fi

    if [[ "${file##*.}" != "md" ]]; then
        warn "Skipping non-.md file: $file"
        return 0
    fi

    if has_frontmatter "$file" && [[ "$FORCE" == "false" ]]; then
        warn "Already has frontmatter (use --force to overwrite): $file"
        return 0
    fi

    local frontmatter
    frontmatter=$(build_frontmatter "$file")

    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN — would sign: $file"
        echo "$frontmatter"
        return 0
    fi

    # Create temp file with frontmatter prepended
    local tmp
    tmp=$(mktemp)

    if has_frontmatter "$file" && [[ "$FORCE" == "true" ]]; then
        # Remove existing frontmatter (everything between first --- and second ---)
        local in_frontmatter=true
        local skip_first=true
        local body=""
        while IFS= read -r line; do
            if [[ "$skip_first" == "true" && "$line" == "---" ]]; then
                skip_first=false
                continue
            fi
            if [[ "$in_frontmatter" == "true" && "$skip_first" == "false" ]]; then
                if [[ "$line" == "---" ]]; then
                    in_frontmatter=false
                    continue
                fi
                continue
            fi
            body="${body}${line}"$'\n'
        done < "$file"
        echo "$frontmatter" > "$tmp"
        echo "$body" >> "$tmp"
    else
        echo "$frontmatter" > "$tmp"
        cat "$file" >> "$tmp"
    fi

    mv "$tmp" "$file"
    success "Signed: $file"
}

# ─── Batch Sign Directory ────────────────────────────────────────────────────
sign_batch() {
    local dir="$1"
    local count=0
    local signed=0

    if [[ ! -d "$dir" ]]; then
        error "Directory not found: $dir"
        exit 1
    fi

    log "Batch signing .md files in: $dir"

    while IFS= read -r -d '' file; do
        count=$((count + 1))
        if sign_file "$file"; then
            signed=$((signed + 1))
        fi
    done < <(find "$dir" -name "*.md" -type f -print0)

    log "Processed: $count files, signed/updated: $signed"
}

# ─── Main ────────────────────────────────────────────────────────────────────
main() {
    parse_args "$@"

    if [[ "$BATCH" == "true" ]]; then
        if [[ -z "$BATCH_DIR" ]]; then
            error "No directory specified for --batch"
            exit 1
        fi
        sign_batch "$BATCH_DIR"
    elif [[ -n "$TARGET_FILE" ]]; then
        sign_file "$TARGET_FILE"
    else
        error "No file or --batch directory specified"
        show_help
        exit 1
    fi
}

main "$@"

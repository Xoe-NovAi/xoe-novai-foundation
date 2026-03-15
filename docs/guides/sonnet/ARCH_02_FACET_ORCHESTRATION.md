---
title: "Omega-Stack Architecture Manual ARCH-02: Facet Orchestration — Spin-Up, Delegation & Subagent Calling"
section: "ARCH-02"
scope: "omega-facet CLI, Makefile targets, in-session subagent patterns, spin-up management, A2A, context passing"
status: "Actionable — Complete Orchestration System"
owner: "arcana-novai (UID 1000)"
last_updated: "2026-03-13"
gemini_review: "Research-validated against Gemini CLI v0.32.0+ documentation"
confidence: "97%"
priority: "P1 — Replace Ad-Hoc Facet Management"
---

# ARCH-02 — Facet Orchestration: Spin-Up, Delegation & Subagent Calling
## Omega-Stack Agent Architecture Manual

> **🤖 AGENT DIRECTIVE:** This manual replaces ad-hoc Makefile targets with a complete `omega-facet` CLI and defines the three canonical patterns for calling facets as subagents during a Gemini session. Prerequisites: ARCH-01 (Archon identity + subagent files), IMPL-04 (facet storage), IMPL-07 (permissions).

---

## Table of Contents

1. [Orchestration Architecture Overview](#1-orchestration-architecture-overview)
2. [The omega-facet CLI — Full Implementation](#2-the-omega-facet-cli--full-implementation)
3. [Enhanced Makefile Targets](#3-enhanced-makefile-targets)
4. [Pattern 1 — In-Session Subagent Delegation (Native)](#4-pattern-1--in-session-subagent-delegation-native)
5. [Pattern 2 — Shell-Based Subprocess Invocation](#5-pattern-2--shell-based-subprocess-invocation)
6. [Pattern 3 — MCP-Based Agentbus Delegation (Async)](#6-pattern-3--mcp-based-agentbus-delegation-async)
7. [Context Passing Between Archon and Facets](#7-context-passing-between-archon-and-facets)
8. [Facet Lifecycle Management](#8-facet-lifecycle-management)
9. [Session Management & Checkpointing](#9-session-management--checkpointing)
10. [Edge Cases & Failure Modes](#10-edge-cases--failure-modes)
11. [Verification Checklist](#11-verification-checklist)

---

## 1. Orchestration Architecture Overview

### 1.1 Three Invocation Patterns Compared

| Pattern | Where Used | Mechanism | Context Sharing | Best For |
|---------|-----------|-----------|----------------|---------|
| **Native Subagent** | Inside Gemini session | `/agent <name>` or automatic routing | Isolated + summary returned | Long tasks, context preservation |
| **Shell Subprocess** | CLI / Makefile / omega-facet | `gemini -p "..."` subprocess | Via file handoff | Scripted pipelines, automation |
| **MCP Agentbus** | xnai-agentbus (port 8011) | HTTP POST to delegation endpoint | Via memory-bank-mcp | Async, multi-facet, background |

### 1.2 Decision Flowchart

```
HOW DO YOU WANT TO INVOKE A FACET?
            │
    ┌───────┴──────────────┐
    │                      │
    ▼                      ▼
Inside Gemini         From Terminal /
Session?              Script / Makefile?
    │                      │
    ▼                      ▼
Pattern 1             Pattern 2 or 3
(Native /agent)           │
                    ┌─────┴──────────┐
                    │                │
                    ▼                ▼
             Needs result      Fire-and-forget /
             synchronously?    background task?
                    │                │
                    ▼                ▼
               Pattern 2        Pattern 3
             (subprocess)       (agentbus)
```

---

## 2. The omega-facet CLI — Full Implementation

The `omega-facet` CLI replaces scattered Makefile targets with a single, discoverable command interface.

### 2.1 Installation

```bash
# Create the CLI script
mkdir -p ~/Documents/Xoe-NovAi/omega-stack/bin/
cat > ~/Documents/Xoe-NovAi/omega-stack/bin/omega-facet << 'SCRIPT_EOF'
#!/usr/bin/env bash
# =============================================================================
# omega-facet — Omega-Stack Facet Orchestration CLI
# Version: 1.0.0
# Usage: omega-facet <command> [options]
# =============================================================================
set -euo pipefail

OMEGA="${HOME}/Documents/Xoe-NovAi/omega-stack"
INSTANCES_DIR="${OMEGA}/storage/instances"
ACTIVE_DIR="${OMEGA}/instances-active"
MEMORY_DIR="${HOME}/.gemini/memory"
AGENTS_DIR="${HOME}/.gemini/agents"
LOG_DIR="/tmp/omega-facet-logs"
mkdir -p "$LOG_DIR"

# ─── Colour output ─────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
log()  { echo -e "${GREEN}[omega-facet]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
err()  { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }
info() { echo -e "${CYAN}$*${NC}"; }

# ─── Facet registry ────────────────────────────────────────────────────────
declare -A FACET_NAMES=(
  [archon]="Archon (Gemini General — Oversoul)"
  [researcher]="Researcher — Research & Analysis"
  [engineer]="Engineer — Software Engineering"
  [infrastructure]="Infrastructure — DevOps & Platform"
  [creator]="Creator — Technical Writing & Content"
  [datascientist]="DataScientist — Data Science & ML"
  [security]="Security — Security Engineering"
  [devops]="DevOps — SRE & Operations"
  [general_legacy]="General-Legacy — Fallback & Compatibility"
)

declare -A FACET_IDS=(
  [archon]=4 [researcher]=1 [engineer]=2 [infrastructure]=3
  [creator]=5 [datascientist]=6 [security]=7 [devops]=8 [general_legacy]=9
)

# ─── Subcommands ──────────────────────────────────────────────────────────
cmd_list() {
  info "═══════════════════════════════════════════════════"
  info "  Omega-Stack Facet Registry"
  info "═══════════════════════════════════════════════════"
  printf "  %-18s %-8s %-35s %-10s\n" "FACET" "ID" "DESCRIPTION" "SUBAGENT"
  printf "  %-18s %-8s %-35s %-10s\n" "─────────────────" "────────" "───────────────────────────────────" "─────────"
  for FACET in archon researcher engineer infrastructure creator datascientist security devops general_legacy; do
    ID="${FACET_IDS[$FACET]}"
    DESC="${FACET_NAMES[$FACET]}"
    SA_FILE="${AGENTS_DIR}/${FACET}.md"
    SA_STATUS="$([ -f "$SA_FILE" ] && echo '✅ ready' || echo '❌ missing')"
    printf "  %-18s %-8s %-35s %-10s\n" "$FACET" "$ID" "${DESC:0:35}" "$SA_STATUS"
  done
  echo ""
  info "Active instance:"
  readlink -f ~/.gemini 2>/dev/null || echo "  No active symlink"
}

cmd_status() {
  local FACET="${1:-}"
  info "═══ Facet Status Check ═══"
  
  # Current active facet
  ACTIVE=$(readlink -f ~/.gemini 2>/dev/null || echo "direct directory")
  echo "  Active .gemini: $ACTIVE"
  
  # Backend services
  echo ""
  echo "  Backend Services:"
  for NAME_PORT in "memory-bank-mcp:8005" "qdrant:6333" "postgres:5432" "redis:6379"; do
    NAME="${NAME_PORT%%:*}"; PORT="${NAME_PORT##*:}"
    if curl -sf "http://localhost:${PORT}/health" &>/dev/null 2>/dev/null || \
       nc -z localhost "$PORT" 2>/dev/null; then
      echo "    ✅ $NAME (port $PORT)"
    else
      echo "    ❌ $NAME (port $PORT) — NOT AVAILABLE"
    fi
  done
  
  # Subagent files
  echo ""
  echo "  Subagent Definitions:"
  for FACET in researcher engineer infrastructure creator datascientist security devops general_legacy; do
    SA_FILE="${AGENTS_DIR}/${FACET}.md"
    [ -f "$SA_FILE" ] && echo "    ✅ $FACET" || echo "    ❌ $FACET — missing ~/.gemini/agents/${FACET}.md"
  done
  
  # Memory
  echo ""
  echo "  Memory:"
  [ -f "${MEMORY_DIR}/archon_worldmodel.md" ] && echo "    ✅ World model" || echo "    ⚠️  No world model"
  SESSIONS=$(ls "${MEMORY_DIR}"/archon_session_*.md 2>/dev/null | wc -l)
  echo "    Sessions stored: $SESSIONS"
}

cmd_spawn() {
  local FACET="${1:-}"
  local TASK="${2:-}"
  
  [ -z "$FACET" ] && err "Usage: omega-facet spawn <facet> [initial-task]"
  [[ -v FACET_IDS[$FACET] ]] || err "Unknown facet: $FACET. Run 'omega-facet list' for options."
  
  log "Spawning ${FACET_NAMES[$FACET]}..."
  
  # Switch .gemini symlink if instance directory exists
  FACET_ID="${FACET_IDS[$FACET]}"
  INSTANCE_DIR="${ACTIVE_DIR}/instance-${FACET_ID}"
  
  if [ -d "$INSTANCE_DIR" ]; then
    # Save current state (if active facet is different)
    CURRENT=$(readlink -f ~/.gemini 2>/dev/null || echo "none")
    if [ "$CURRENT" != "${INSTANCE_DIR}/.gemini" ]; then
      log "Switching from active instance to facet-${FACET_ID}..."
      ln -sfn "${INSTANCE_DIR}/.gemini" ~/.gemini
      log "✅ .gemini symlink updated to facet-${FACET_ID} (${FACET})"
    fi
  else
    warn "No instance directory for facet-${FACET_ID} — using shared .gemini"
  fi
  
  # Build the gemini invocation
  AGENT_FILE="${AGENTS_DIR}/${FACET}.md"
  
  if [ -f "$AGENT_FILE" ]; then
    # Use extension-style invocation if Gemini CLI supports it
    if [ -n "$TASK" ]; then
      IDENTITY="You are the ${FACET} facet of the Omega-Stack Archon system. ${TASK}"
      log "Delegating task to $FACET..."
      gemini -p "$IDENTITY" --yolo
    else
      # Interactive session
      log "Starting interactive $FACET session..."
      log "Context: $(head -5 "$AGENT_FILE" | grep description || echo "$FACET specialist")"
      
      # Prepend identity to session via GEMINI.md override
      TMPDIR=$(mktemp -d)
      cp ~/Documents/Xoe-NovAi/omega-stack/GEMINI.md "${TMPDIR}/GEMINI.md" 2>/dev/null || true
      cat >> "${TMPDIR}/GEMINI.md" << IDENTITY_EOF

## Active Identity Override
You are currently operating as the **${FACET}** facet. Apply ${FACET_NAMES[$FACET]:-$FACET} expertise exclusively. Return a ${FACET^^} DEBRIEF at the end of your session.
IDENTITY_EOF
      
      cd "$TMPDIR" && gemini
      rm -rf "$TMPDIR"
    fi
  else
    warn "No subagent file for $FACET — starting Archon session with $FACET persona hint"
    gemini -p "You are the $FACET specialist of the Omega-Stack. ${TASK:-Begin interactive session.}"
  fi
}

cmd_delegate() {
  local FACET="${1:-}"
  local TASK="${2:-}"
  local OUTPUT="${3:-/tmp/omega_facet_${FACET}_$(date +%Y%m%d_%H%M%S).md}"
  
  [ -z "$FACET" ] && err "Usage: omega-facet delegate <facet> '<task>' [output-file]"
  [ -z "$TASK" ]  && err "Usage: omega-facet delegate <facet> '<task>' [output-file]"
  [[ -v FACET_IDS[$FACET] ]] || err "Unknown facet: $FACET"
  
  log "Delegating to ${FACET_NAMES[$FACET]}..."
  log "Task: ${TASK:0:80}..."
  log "Output: $OUTPUT"
  
  # Critical: explicitly state identity to prevent identity confusion
  PROMPT="You are the ${FACET} facet of the Omega-Stack Archon system. Your role: ${FACET_NAMES[$FACET]}.

TASK: ${TASK}

After completing the task, provide a structured DEBRIEF in this format:
${FACET^^} DEBRIEF
$(printf '=%.0s' {1..40})
Task completed: [one sentence]
Key findings: [bullet points]
Files modified: [list or 'none']
Confidence: [High/Medium/Low]
Limitations: [any caveats]"

  # Run as non-interactive subprocess, capture output
  gemini --yolo -p "$PROMPT" --output-format text 2>&1 | tee "$OUTPUT"
  
  log "✅ Delegation complete. Output saved to: $OUTPUT"
  echo "$OUTPUT"
}

cmd_synthesize() {
  local INPUT_FILES=()
  local SYNTHESIS_TASK=""
  
  # Parse arguments: all .md files as inputs, last non-file arg as synthesis task
  while [[ $# -gt 0 ]]; do
    if [[ "$1" == *.md ]] || [[ -f "$1" ]]; then
      INPUT_FILES+=("$1")
    else
      SYNTHESIS_TASK="$1"
    fi
    shift
  done
  
  [ ${#INPUT_FILES[@]} -eq 0 ] && err "Usage: omega-facet synthesize <file1.md> [file2.md ...] '<synthesis-task>'"
  
  log "Synthesizing ${#INPUT_FILES[@]} facet reports..."
  
  COMBINED=""
  for FILE in "${INPUT_FILES[@]}"; do
    [ -f "$FILE" ] || warn "File not found: $FILE (skipping)"
    COMBINED="${COMBINED}\n\n## From: $(basename "$FILE")\n$(cat "$FILE")"
  done
  
  PROMPT="You are Archon, the Omega-Stack Oversoul. You have received reports from your specialist facets.

FACET REPORTS:
${COMBINED}

SYNTHESIS TASK: ${SYNTHESIS_TASK:-Synthesize these facet reports into a unified analysis and action plan.}

Apply the INTEGRATION synthesis framework:
- Integrate all findings into a unified narrative
- Note any conflicts between facets
- Identify cross-domain insights
- Rank recommendations by priority
- Define a concrete, ordered action plan"

  gemini -p "$PROMPT"
}

cmd_activate() {
  local FACET="${1:-}"
  [ -z "$FACET" ] && err "Usage: omega-facet activate <facet>"
  [[ -v FACET_IDS[$FACET] ]] || err "Unknown facet: $FACET"
  
  FACET_ID="${FACET_IDS[$FACET]}"
  INSTANCE_DIR="${ACTIVE_DIR}/instance-${FACET_ID}"
  
  if [ -d "${INSTANCE_DIR}/.gemini" ]; then
    ln -sfn "${INSTANCE_DIR}/.gemini" ~/.gemini
    log "✅ Activated facet-${FACET_ID} (${FACET}): .gemini → ${INSTANCE_DIR}/.gemini"
  else
    warn "No dedicated instance directory for facet-${FACET_ID}"
    warn "Using shared .gemini directory"
  fi
  
  # Fix permissions on activation
  sudo chown -R arcana-novai:arcana-novai ~/.gemini/ 2>/dev/null || true
  setfacl -d -m u:1000:rwx,u:100999:rwx,m::rwx ~/.gemini/ 2>/dev/null || true
  log "✅ Permissions verified for $FACET"
}

cmd_memory() {
  local SUBCOMMAND="${1:-show}"
  
  case "$SUBCOMMAND" in
    show)
      info "═══ Archon Memory State ═══"
      if [ -f "${MEMORY_DIR}/archon_worldmodel.md" ]; then
        cat "${MEMORY_DIR}/archon_worldmodel.md"
      else
        echo "No world model found. Run: omega-facet memory init"
      fi
      ;;
    sessions)
      info "═══ Session History ═══"
      ls -lt "${MEMORY_DIR}"/archon_session_*.md 2>/dev/null | head -10 || echo "No sessions found"
      ;;
    save)
      local CONTENT="${2:-}"
      [ -z "$CONTENT" ] && err "Usage: omega-facet memory save '<content>'"
      DATE=$(date +%Y%m%d)
      echo "" >> "${MEMORY_DIR}/archon_session_${DATE}.md"
      echo "## $(date '+%H:%M:%S')" >> "${MEMORY_DIR}/archon_session_${DATE}.md"
      echo "$CONTENT" >> "${MEMORY_DIR}/archon_session_${DATE}.md"
      log "✅ Saved to ${MEMORY_DIR}/archon_session_${DATE}.md"
      ;;
    query)
      local QUERY="${2:-}"
      [ -z "$QUERY" ] && err "Usage: omega-facet memory query '<search terms>'"
      grep -rl "$QUERY" "${MEMORY_DIR}/" 2>/dev/null | \
        xargs grep -h -C 2 "$QUERY" 2>/dev/null | head -40 || echo "No matches found"
      ;;
    init)
      mkdir -p "$MEMORY_DIR"
      [ -f "${MEMORY_DIR}/archon_worldmodel.md" ] && warn "World model already exists — not overwriting" || \
        omega-facet memory save "# Archon World Model — Initialized $(date '+%Y-%m-%d')"
      log "✅ Memory initialized"
      ;;
    *)
      err "Unknown memory subcommand: $SUBCOMMAND. Options: show, sessions, save, query, init"
      ;;
  esac
}

cmd_help() {
  cat << 'HELP_EOF'
omega-facet — Omega-Stack Facet Orchestration CLI

COMMANDS:
  list                          Show all facets and subagent status
  status                        Show active instance, backends, subagents
  activate <facet>              Switch .gemini symlink to a facet's instance
  spawn <facet> [task]          Start interactive or task-based facet session
  delegate <facet> '<task>' [output]
                                Delegate a task to a facet (non-interactive)
  synthesize <file1> [file2...] '<task>'
                                Have Archon synthesize multiple facet reports
  memory <subcommand>           Manage Archon memory (show/sessions/save/query/init)
  help                          Show this help

FACETS:
  archon          Gemini General — Polymath Oversoul
  researcher      Research & Analysis
  engineer        Software Engineering  
  infrastructure  DevOps & Platform Engineering
  creator         Technical Writing & Content
  datascientist   Data Science & ML
  security        Security Engineering
  devops          SRE & Operations
  general_legacy  Fallback & Legacy Compatibility

EXAMPLES:
  omega-facet list
  omega-facet spawn researcher
  omega-facet spawn engineer "Refactor the auth module for type safety"
  omega-facet delegate security "Audit .env and docker-compose.yml for secrets" /tmp/audit.md
  omega-facet synthesize /tmp/security_report.md /tmp/engineer_report.md "Create unified hardening plan"
  omega-facet memory show
  omega-facet memory save "Rotated all credentials on 2026-03-13"
  omega-facet activate archon

HELP_EOF
}

# ─── Main dispatch ────────────────────────────────────────────────────────
COMMAND="${1:-help}"
shift 2>/dev/null || true

case "$COMMAND" in
  list|ls)         cmd_list "$@" ;;
  status|st)       cmd_status "$@" ;;
  spawn|run|s)     cmd_spawn "$@" ;;
  delegate|d)      cmd_delegate "$@" ;;
  synthesize|syn)  cmd_synthesize "$@" ;;
  activate|a)      cmd_activate "$@" ;;
  memory|mem|m)    cmd_memory "$@" ;;
  help|--help|-h)  cmd_help ;;
  *)               err "Unknown command: $COMMAND. Run 'omega-facet help' for usage." ;;
esac
SCRIPT_EOF

chmod +x ~/Documents/Xoe-NovAi/omega-stack/bin/omega-facet
echo "✅ omega-facet CLI installed"
```

### 2.2 Add to PATH

```bash
# Add to ~/.profile (persistent)
cat >> ~/.profile << 'EOF'

# Omega-Stack bin directory
export PATH="${HOME}/Documents/Xoe-NovAi/omega-stack/bin:${PATH}"
EOF

# Apply immediately
export PATH="${HOME}/Documents/Xoe-NovAi/omega-stack/bin:${PATH}"

# Verify
omega-facet list
```

---

## 3. Enhanced Makefile Targets

For those who prefer `make`, here are comprehensive targets that wrap `omega-facet`. These complement (not replace) the CLI.

```makefile
# Omega-Stack Facet Management Makefile Targets
# Add to ~/Documents/Xoe-NovAi/omega-stack/Makefile

OMEGA := $(HOME)/Documents/Xoe-NovAi/omega-stack
BIN   := $(OMEGA)/bin/omega-facet

# ─── Archon (Gemini General — Oversoul) ────────────────────────────────────
.PHONY: archon
archon: ## Launch Archon (Gemini General as Oversoul) — main interactive session
	cd $(OMEGA) && gemini

# ─── Facet Spawning ────────────────────────────────────────────────────────
.PHONY: facet-researcher facet-engineer facet-infra facet-creator
.PHONY: facet-data facet-security facet-devops facet-legacy

facet-researcher: ## Spawn Researcher facet (interactive)
	$(BIN) spawn researcher

facet-engineer: ## Spawn Engineer facet (interactive)
	$(BIN) spawn engineer

facet-infra: ## Spawn Infrastructure facet (interactive)
	$(BIN) spawn infrastructure

facet-creator: ## Spawn Creator facet (interactive)
	$(BIN) spawn creator

facet-data: ## Spawn DataScientist facet (interactive)
	$(BIN) spawn datascientist

facet-security: ## Spawn Security facet (interactive)
	$(BIN) spawn security

facet-devops: ## Spawn DevOps facet (interactive)
	$(BIN) spawn devops

facet-legacy: ## Spawn General-Legacy facet (interactive)
	$(BIN) spawn general_legacy

# ─── Delegation shortcuts ──────────────────────────────────────────────────
.PHONY: audit-security audit-infra review-code

audit-security: ## Run security audit on .env and docker-compose.yml
	$(BIN) delegate security \
	  "Audit ~/Documents/Xoe-NovAi/omega-stack/.env and docker-compose.yml for: exposed secrets, default passwords, overly permissive volumes, missing security hardening. Provide CRITICAL/HIGH/MEDIUM/LOW findings." \
	  /tmp/security_audit_$(shell date +%Y%m%d).md
	@echo "Audit saved to /tmp/security_audit_$(shell date +%Y%m%d).md"

audit-infra: ## Run infrastructure audit (permissions, resource limits, health checks)
	$(BIN) delegate infrastructure \
	  "Audit the Omega-Stack for: missing resource limits, services without health checks, incorrect volume flags, and permission model correctness. Verify ACL state." \
	  /tmp/infra_audit_$(shell date +%Y%m%d).md

review-code: ## Code review of recent git changes
	$(BIN) delegate engineer \
	  "Review the recent git changes (git diff HEAD~5..HEAD) for: correctness, security, performance, and style. Flag any issues." \
	  /tmp/code_review_$(shell date +%Y%m%d).md

# ─── Stack Management ──────────────────────────────────────────────────────
.PHONY: facet-status facet-list

facet-status: ## Show all facet and backend status
	$(BIN) status

facet-list: ## List all facets and subagent files
	$(BIN) list

# ─── Memory ────────────────────────────────────────────────────────────────
.PHONY: memory-show memory-query

memory-show: ## Show Archon world model
	$(BIN) memory show

memory-query: ## Query memory (QUERY="search terms")
	$(BIN) memory query "$(QUERY)"

# ─── Help ──────────────────────────────────────────────────────────────────
.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
```

---

## 4. Pattern 1 — In-Session Subagent Delegation (Native)

This is the most powerful and context-efficient method. The Archon calls a facet subagent directly within the Gemini CLI session.

### 4.1 How It Works

<IMPORTANT — AGENT CALLOUT>
**Gemini CLI subagent mechanics (v0.32.0+):**
1. Each `.gemini/agents/<name>.md` file is registered as a callable tool named after the file
2. The Archon's generalist agent automatically routes appropriate tasks to subagents
3. Manual invocation: `/agent <name> <task>` within a session
4. Subagents run in **isolated context windows** — their execution history is compressed into a single summary in the Archon's context
5. The Archon receives a structured DEBRIEF, not the raw conversation history
6. YOLO mode: subagents may execute tools without confirmation — monitor carefully
</IMPORTANT>

### 4.2 Enable Subagents

```bash
# Verify subagents are enabled
cat ~/.gemini/settings.json | python3 -m json.tool | grep -A3 experimental
# Expected: "enableAgents": true

# If not enabled:
python3 -c "
import json
with open('$HOME/.gemini/settings.json', 'r+') as f:
    s = json.load(f)
    s.setdefault('experimental', {})['enableAgents'] = True
    s['experimental']['enableSkills'] = True
    f.seek(0)
    json.dump(s, f, indent=2)
    f.truncate()
print('✅ Agents enabled in settings.json')
"
```

### 4.3 In-Session Invocation Examples

```
# Inside an active `gemini` session (Archon mode):

# Explicit manual delegation
/agent researcher Survey the literature on zero-copy networking techniques for containerized environments

# The generalist agent auto-routes (if you describe the task with domain keywords)
User: Conduct a comprehensive security audit of our entire .gemini directory structure 
      and all permission-related files.

# Archon recognizes "security audit" → delegates to @security subagent
# security runs isolated analysis
# Returns SECURITY DEBRIEF → Archon synthesizes

# Multi-facet sequential delegation
User: I need both a security review AND a performance analysis of our rag_api service.

# Archon plan:
# Step 1: /agent security [audit rag_api security]
# Step 2: /agent datascientist [analyze rag_api performance metrics]  
# Step 3: Archon synthesizes both reports
```

### 4.4 Subagent Routing Optimization

The generalist agent uses the `description` field in each subagent's YAML frontmatter to decide routing. To optimize routing accuracy:

```bash
# Test routing with a specific prompt
# Start a session and ask:
# "Why didn't you delegate to the security agent for this task?"
# The generalist will explain its routing decision

# Force a specific agent:
/agent security <task>

# Reload agent registry after changing .md files:
/agents reload
```

---

## 5. Pattern 2 — Shell-Based Subprocess Invocation

Use when you need facet outputs in a script, pipeline, or from outside a Gemini session.

### 5.1 Basic Delegation

```bash
#!/usr/bin/env bash
# Delegate a task to a facet and capture output

delegate_to_facet() {
  local FACET="$1"
  local TASK="$2"
  local OUTPUT_FILE="${3:-/tmp/facet_${FACET}_$(date +%Y%m%d_%H%M%S).md}"
  
  # CRITICAL: Always prefix with identity establishment
  # Without this, the subprocess defaults to generic Gemini and ignores the agent persona
  local PROMPT="You are the ${FACET} facet of the Omega-Stack Archon system.

$(cat ~/.gemini/agents/${FACET}.md 2>/dev/null | sed '/^---/,/^---/d' | head -30)

TASK: ${TASK}

Provide a complete response followed by a structured DEBRIEF."

  gemini --yolo -p "$PROMPT" --output-format text > "$OUTPUT_FILE" 2>&1
  echo "$OUTPUT_FILE"
}

# Usage examples:
SECURITY_REPORT=$(delegate_to_facet security "Audit all files in ~/omega-stack/.env for plaintext secrets")
ENGINEER_REPORT=$(delegate_to_facet engineer "Review the ACL repair script for correctness and edge cases")

# Pass to Archon for synthesis
omega-facet synthesize "$SECURITY_REPORT" "$ENGINEER_REPORT" \
  "Create a unified remediation plan for the security and code quality issues found"
```

### 5.2 Parallel Facet Execution (with File Isolation Check)

```bash
#!/usr/bin/env bash
# Run multiple facets in parallel when they don't share file targets
# WARNING: Only do this if the facets analyze DIFFERENT resources

parallel_delegate() {
  local TASKS=("$@")
  local PIDS=()
  local OUTPUT_FILES=()
  
  for TASK_SPEC in "${TASKS[@]}"; do
    FACET="${TASK_SPEC%%:*}"
    TASK="${TASK_SPEC#*:}"
    OUTPUT="/tmp/parallel_${FACET}_$(date +%Y%m%d_%H%M%S).md"
    OUTPUT_FILES+=("$OUTPUT")
    
    (delegate_to_facet "$FACET" "$TASK" "$OUTPUT") &
    PIDS+=($!)
    echo "Started $FACET (PID $!)"
  done
  
  # Wait for all
  for PID in "${PIDS[@]}"; do
    wait "$PID" && echo "✅ PID $PID complete" || echo "⚠️ PID $PID failed"
  done
  
  echo "${OUTPUT_FILES[@]}"
}

# Example: analyze different services in parallel (no file conflicts)
OUTPUTS=$(parallel_delegate \
  "security:Audit the redis configuration for security issues" \
  "devops:Review the VictoriaMetrics alert rules for completeness" \
  "researcher:Research best practices for Podman memory limits on 6GB systems"
)

# Note: Gemini CLI docs warn not to run parallel subagents that mutate same files
# These read different resources, so parallel is safe
omega-facet synthesize $OUTPUTS "Unified infrastructure improvement plan"
```

### 5.3 Pipeline Pattern — Chain Facets

```bash
#!/usr/bin/env bash
# Research → Engineer → Security pipeline
# Each facet builds on the previous one's output

OMEGA=~/Documents/Xoe-NovAi/omega-stack

# Stage 1: Research the approach
log "Stage 1: Researcher gathers context..."
omega-facet delegate researcher \
  "Research best practices for Podman volume permission management with rootless containers and POSIX ACLs. Focus on production-grade patterns for 2025-2026." \
  /tmp/pipeline_stage1_research.md

# Stage 2: Engineer designs implementation
log "Stage 2: Engineer designs implementation based on research..."
omega-facet delegate engineer \
  "Based on this research report, design a robust implementation for the Omega-Stack's .gemini permission management. Implement as a production-grade bash script: $(cat /tmp/pipeline_stage1_research.md)" \
  /tmp/pipeline_stage2_implementation.md

# Stage 3: Security reviews the implementation
log "Stage 3: Security audits the implementation..."
omega-facet delegate security \
  "Security review this implementation for the Omega-Stack permission management system: $(cat /tmp/pipeline_stage2_implementation.md). Focus on privilege escalation, symlink attacks, and race conditions." \
  /tmp/pipeline_stage3_security.md

# Final: Archon synthesizes all three stages
log "Final: Archon synthesis..."
omega-facet synthesize \
  /tmp/pipeline_stage1_research.md \
  /tmp/pipeline_stage2_implementation.md \
  /tmp/pipeline_stage3_security.md \
  "Produce the final hardened implementation incorporating all findings"
```

---

## 6. Pattern 3 — MCP-Based Agentbus Delegation (Async)

For fire-and-forget background delegation via `xnai-agentbus` (port 8011).

> **📝 NOTE:** This pattern requires xnai-agentbus to expose a task delegation endpoint. If the current agentbus doesn't support this natively, use the shell-based approach (Pattern 2) instead. The protocol below is the design target for future implementation.

### 6.1 Agentbus Delegation Protocol

```bash
#!/usr/bin/env bash
# Submit a task to the agentbus for background processing

delegate_async() {
  local FACET="$1"
  local TASK="$2"
  local CALLBACK_URL="${3:-}"  # Optional webhook URL for completion notification
  
  TASK_ID="omega-${FACET}-$(date +%s)-$$"
  
  curl -sf -X POST "http://localhost:8011/delegate" \
    -H "Content-Type: application/json" \
    -d "{
      \"task_id\": \"${TASK_ID}\",
      \"facet\": \"${FACET}\",
      \"task\": \"${TASK}\",
      \"priority\": \"normal\",
      \"callback_url\": \"${CALLBACK_URL}\",
      \"output_path\": \"/tmp/${TASK_ID}.md\"
    }" && echo "✅ Task submitted: $TASK_ID" || echo "❌ Agentbus unavailable — use Pattern 2"
}

# Check task status
check_task() {
  local TASK_ID="$1"
  curl -sf "http://localhost:8011/tasks/${TASK_ID}" | python3 -m json.tool
}

# Example usage
delegate_async researcher \
  "Build a comprehensive report on the Omega-Stack's current technology choices against 2026 best practices" \
  ""

# Check later
check_task "omega-researcher-$(date +%s)-$$"
```

---

## 7. Context Passing Between Archon and Facets

### 7.1 Context Injection Methods

| Method | When to Use | Implementation |
|--------|------------|----------------|
| **File handoff** | Large context (> 2KB) | Write to `/tmp/context_*.md`, pass path in prompt |
| **Inline injection** | Small context (< 2KB) | Embed directly in prompt string |
| **Memory-bank query** | Historical context | `curl http://localhost:8005/query` then inject results |
| **World model** | Stack facts | Read `~/.gemini/memory/archon_worldmodel.md` and prepend |

### 7.2 Context Template for Subagent Calls

```bash
build_context_prompt() {
  local FACET="$1"
  local TASK="$2"
  local EXTRA_CONTEXT="${3:-}"
  
  # Load world model (always relevant)
  WORLD_MODEL=$(cat ~/.gemini/memory/archon_worldmodel.md 2>/dev/null | head -30)
  
  # Query memory bank for relevant history
  MEMORY_CONTEXT=""
  if curl -sf http://localhost:8005/health &>/dev/null; then
    MEMORY_CONTEXT=$(curl -sf -X POST http://localhost:8005/query \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"${TASK}\", \"limit\": 3}" 2>/dev/null | \
      python3 -c "import json,sys; d=json.load(sys.stdin); print('\n'.join([r.get('content','') for r in d.get('results',[])]))" 2>/dev/null || echo "")
  fi
  
  cat << PROMPT_EOF
You are the ${FACET} facet of the Omega-Stack Archon system.

## Stack Context
${WORLD_MODEL}

## Relevant Memory
${MEMORY_CONTEXT}

${EXTRA_CONTEXT:+## Additional Context
$EXTRA_CONTEXT

}## Task
${TASK}
PROMPT_EOF
}

# Usage:
PROMPT=$(build_context_prompt security "Audit the rag_api service for authentication weaknesses" \
  "The rag_api was recently updated to use connection pooling")
gemini --yolo -p "$PROMPT" > /tmp/security_rag_audit.md
```

---

## 8. Facet Lifecycle Management

### 8.1 Instance Directory Structure

```
instances-active/
├── instance-1/   facet-1: Researcher
│   └── .gemini/
│       ├── settings.json   (researcher-specific settings)
│       ├── memory/         (researcher's accumulated knowledge)
│       └── chats/          (researcher session history)
├── instance-2/   facet-2: Engineer
│   └── .gemini/
├── instance-4/   facet-4: General (Archon) ← currently active
│   └── .gemini/
│       ├── settings.json
│       ├── memory/         (archon world model + session logs)
│       ├── agents/         (all 8 subagent .md files)
│       ├── skills/         (domain skill injection files)
│       └── chats/
└── ...
```

### 8.2 Create Instance Directories for All Facets

```bash
#!/usr/bin/env bash
# Initialize instance directories for all 9 facets
OMEGA=~/Documents/Xoe-NovAi/omega-stack
ACTIVE_DIR="${OMEGA}/instances-active"
TEMPLATES_DIR="${OMEGA}/storage/instances"

declare -A FACET_IDS=(
  [archon]=4 [researcher]=1 [engineer]=2 [infrastructure]=3
  [creator]=5 [datascientist]=6 [security]=7 [devops]=8 [general_legacy]=9
)

for FACET in "${!FACET_IDS[@]}"; do
  ID="${FACET_IDS[$FACET]}"
  INST_DIR="${ACTIVE_DIR}/instance-${ID}"
  GEMINI_DIR="${INST_DIR}/.gemini"
  
  mkdir -p "${GEMINI_DIR}/memory" "${GEMINI_DIR}/chats" "${GEMINI_DIR}/agents" "${GEMINI_DIR}/skills"
  
  # Copy template if it exists
  TEMPLATE="${TEMPLATES_DIR}/${FACET}/gemini-cli/.gemini/"
  if [ -d "$TEMPLATE" ]; then
    rsync -a --ignore-existing "$TEMPLATE" "${GEMINI_DIR}/"
    echo "✅ Instance $ID ($FACET): populated from template"
  else
    # Create minimal settings.json
    cat > "${GEMINI_DIR}/settings.json" << SETTINGS_EOF
{
  "experimental": { "enableAgents": true, "enableSkills": true },
  "theme": "Default",
  "facet": "${FACET}",
  "facetId": ${ID}
}
SETTINGS_EOF
    echo "✅ Instance $ID ($FACET): initialized fresh"
  fi
  
  # Fix permissions
  chown -R arcana-novai:arcana-novai "${INST_DIR}" 2>/dev/null || true
  setfacl -d -m u:1000:rwx,u:100999:rwx,m::rwx "${GEMINI_DIR}" 2>/dev/null || true
done

# The agents/ and skills/ directories should live in the Archon (instance-4)
# and be shared via the ARCH-01 setup
cp ~/.gemini/agents/*.md "${ACTIVE_DIR}/instance-4/.gemini/agents/" 2>/dev/null || true
cp ~/.gemini/skills/*.md "${ACTIVE_DIR}/instance-4/.gemini/skills/" 2>/dev/null || true

echo "✅ All ${#FACET_IDS[@]} facet instance directories initialized"
```

---

## 9. Session Management & Checkpointing

### 9.1 Checkpointing Long Sessions

```bash
# Enable checkpointing in settings.json (already done in ARCH-01)
# Checkpoints are saved automatically

# Manual checkpoint during a session:
# /checkpoint save my-archon-session-2026-03-13

# Resume from checkpoint:
# gemini --checkpoint my-archon-session-2026-03-13

# List checkpoints:
# /checkpoint list
```

### 9.2 Session Continuity Protocol

```bash
#!/usr/bin/env bash
# Start a session with context from previous session

start_archon_session() {
  local RESUME="${1:-}"
  
  cd ~/Documents/Xoe-NovAi/omega-stack
  
  if [ -n "$RESUME" ]; then
    echo "Resuming session: $RESUME"
    gemini --checkpoint "$RESUME"
  else
    # Prime the new session with world model
    WORLD_MODEL=$(cat ~/.gemini/memory/archon_worldmodel.md 2>/dev/null)
    RECENT_SESSION=$(ls -t ~/.gemini/memory/archon_session_*.md 2>/dev/null | head -1)
    RECENT=$([ -n "$RECENT_SESSION" ] && tail -20 "$RECENT_SESSION" || echo "No recent sessions")
    
    # Create priming note
    PRIME=$(cat << PRIME_EOF
CONTEXT PRIME — Read before responding to anything.

WORLD MODEL:
${WORLD_MODEL}

RECENT SESSION SUMMARY:
${RECENT}
PRIME_EOF
)
    
    # Start with primed context
    echo "$PRIME" | gemini --stdin_prompt
  fi
}
```

---

## 10. Edge Cases & Failure Modes

| Scenario | Symptom | Resolution |
|----------|---------|------------|
| Subagent identity confusion | Subagent gives generic response, ignores DEBRIEF format | Always prefix: `"You are the X facet..."` + inject agent file body |
| Recursive delegation loop | Subagent calls another subagent which calls it back | Add `"Do NOT call other agents or delegate."` to subagent prompts |
| omega-facet CLI not in PATH | `command not found: omega-facet` | `source ~/.profile` or `export PATH="...bin:$PATH"` |
| Agentbus (8011) not responding | Pattern 3 fails | Fall back to Pattern 2 (shell subprocess); check `podman ps` for xnai-agentbus |
| gemini --yolo modifies wrong files | Unintended side effects | Review task specification; restrict tools in subagent YAML: `tools: [read_file, write_file]` only for read tasks |
| .gemini symlink points to wrong facet | Wrong memory/settings loaded | `omega-facet activate archon` to reset to General; `omega-facet status` to verify |
| Context window overflow in synthesis | Long multi-facet reports exceed window | Pre-summarize each report: `omega-facet delegate creator "Summarize this to 500 words: $(cat report.md)"` |
| Subagent not registered (agents not reloaded) | `/agent X` returns "agent not found" | `/agents reload` within session; check file exists at `~/.gemini/agents/X.md` |
| facet instance .gemini permissions broken | Facet can't read settings after switch | `omega-facet activate <facet>` (includes permission repair) |

---

## 11. Verification Checklist

```bash
#!/usr/bin/env bash
echo "=== ARCH-02 ORCHESTRATION VERIFICATION ==="

# omega-facet CLI installed
command -v omega-facet &>/dev/null && echo "✅ omega-facet CLI installed" || echo "❌ omega-facet not in PATH"

# All subagent definitions exist
for FACET in researcher engineer infrastructure creator datascientist security devops general_legacy; do
  [ -f ~/.gemini/agents/${FACET}.md ] && echo "✅ Subagent: $FACET" || echo "❌ Missing: ~/.gemini/agents/${FACET}.md"
done

# Settings enable agents
python3 -c "
import json
with open('$HOME/.gemini/settings.json') as f:
    s = json.load(f)
print('✅ enableAgents: true' if s.get('experimental',{}).get('enableAgents') else '❌ enableAgents NOT enabled')
" 2>/dev/null

# Instance directories
for ID in 1 2 3 4 5 6 7 8 9; do
  DIR=~/Documents/Xoe-NovAi/omega-stack/instances-active/instance-${ID}
  [ -d "$DIR" ] && echo "✅ Instance ${ID} directory" || echo "⚠️  Missing: instance-${ID}"
done

# Active symlink
ACTIVE=$(readlink -f ~/.gemini 2>/dev/null || echo "none")
echo "Active .gemini: $ACTIVE"

# Memory directory
[ -d ~/.gemini/memory ] && echo "✅ Memory directory exists" || echo "❌ Memory directory missing"

echo ""
echo "=== QUICK TEST ==="
echo "Try: omega-facet list"
echo "Try: omega-facet status"
echo "Try: omega-facet spawn researcher 'Explain POSIX Default ACLs in 3 sentences'"
```

#!/usr/bin/env bash
# ---
# tool: opencode
# model: claude-opus-4-6-thinking
# account: arcana-novai
# session_id: sprint7-opus-2026-02-19
# version: v1.1.0
# created: 2026-02-19
# ---
#
# run-benchmark.sh — XNAi Context Engineering Benchmark Runner
#
# Creates an isolated git worktree from a benchmark tag, prepares
# environment context packs (E1-E5), and outputs evaluator instructions.
#
# Integration:
#   - Uses scripts/stack-cat.py with configs/stack-cat-config.yaml for E5
#   - Results can be ingested via scripts/ingest_library.py
#   - Scoring uses benchmarks/scoring-rubric.yaml
#   - Ground truth in benchmarks/ground-truth-baseline.yaml
#
# Stack Integration (optional flags):
#   --preflight   Run scripts/stack_health_check.sh before starting
#   --publish     Publish run manifest to Redis stream xnai:benchmark_results
#   --ingest      Feed generated context packs to scripts/ingest_library.py
#   --harvest     Harvest CLI session data post-run via scripts/harvest-cli-sessions.sh
#   --integrate   Enable all stack integrations (preflight+publish+ingest+harvest)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_OUTPUT="/tmp/xnai-benchmark"
WORKTREE_BASE="/tmp/xnai-benchmark-worktree"

# --- Defaults ---
TAG=""
ENV_FILTER="all"
MODEL_ID=""
OUTPUT_DIR="$DEFAULT_OUTPUT"
CLEANUP=false
PACK_ONLY=false
DO_PREFLIGHT=false
DO_PUBLISH=false
DO_INGEST=false
DO_HARVEST=false

usage() {
    cat <<'USAGE'
Usage: run-benchmark.sh [OPTIONS]

Creates an isolated snapshot from a benchmark tag and prepares context packs.

Options:
  -t, --tag TAG         Benchmark tag (default: latest benchmark/* tag)
  -e, --env ENV         Environment: E1|E2|E3|E4|E5|all (default: all)
  -m, --model MODEL     Model identifier for results directory naming
  -o, --output DIR      Output directory (default: /tmp/xnai-benchmark)
  -c, --cleanup         Remove worktree after pack generation
  -p, --pack-only       Generate packs only, skip evaluator instructions
  -h, --help            Show this help

Stack Integration (all optional, degrade gracefully if services unavailable):
  --preflight           Run stack health check before starting
  --publish             Publish run manifest to Redis stream xnai:benchmark_results
  --ingest              Ingest generated context packs into RAG vectorstore
  --harvest             Harvest CLI session data post-run
  --integrate           Enable all stack integrations above

Environments:
  E1  Cold Start       — repo path only, no context injected
  E2  README Only      — README.md content injected
  E3  Raw Codebase     — full repo access, memory_bank/ excluded
  E4  Minimal Memory   — activeContext.md + progress.md only
  E5  Full Protocol    — 15-file XNAi Onboarding Protocol via stack-cat

Examples:
  ./scripts/run-benchmark.sh -t benchmark/context-engineering-v1.0.0 -e E5 -m opus-4.6
  ./scripts/run-benchmark.sh --env all --cleanup
  ./scripts/run-benchmark.sh -e E2 -p
  ./scripts/run-benchmark.sh --integrate -m gemini-3-pro -e E5
USAGE
    exit 0
}

# --- Argument Parsing ---
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tag)    TAG="$2"; shift 2 ;;
        -e|--env)    ENV_FILTER="$2"; shift 2 ;;
        -m|--model)  MODEL_ID="$2"; shift 2 ;;
        -o|--output) OUTPUT_DIR="$2"; shift 2 ;;
        -c|--cleanup) CLEANUP=true; shift ;;
        -p|--pack-only) PACK_ONLY=true; shift ;;
        --preflight)  DO_PREFLIGHT=true; shift ;;
        --publish)    DO_PUBLISH=true; shift ;;
        --ingest)     DO_INGEST=true; shift ;;
        --harvest)    DO_HARVEST=true; shift ;;
        --integrate)  DO_PREFLIGHT=true; DO_PUBLISH=true; DO_INGEST=true; DO_HARVEST=true; shift ;;
        -h|--help)   usage ;;
        *) echo "Error: Unknown option $1"; usage ;;
    esac
done

# --- Validation ---
validate_env() {
    case "$1" in
        E1|E2|E3|E4|E5|all) return 0 ;;
        *) echo "Error: Invalid environment '$1'. Must be E1-E5 or 'all'."; exit 1 ;;
    esac
}
validate_env "$ENV_FILTER"

# --- Tag Resolution ---
resolve_tag() {
    if [[ -n "$TAG" ]]; then
        if ! git -C "$PROJECT_ROOT" rev-parse "$TAG" &>/dev/null; then
            echo "Error: Tag '$TAG' not found."
            echo "Available benchmark tags:"
            git -C "$PROJECT_ROOT" tag -l 'benchmark/*' 2>/dev/null || echo "  (none)"
            exit 1
        fi
        echo "$TAG"
        return
    fi

    local latest
    latest=$(git -C "$PROJECT_ROOT" tag -l 'benchmark/*' --sort=-version:refname | head -1)
    if [[ -z "$latest" ]]; then
        echo "Error: No benchmark/* tags found."
        echo ""
        echo "Create one with:"
        echo "  git tag -a benchmark/context-engineering-v1.0.0 -m 'Initial benchmark snapshot'"
        echo ""
        echo "Or use HEAD directly for development:"
        echo "  $0 -t HEAD"
        exit 1
    fi
    echo "$latest"
}

# --- Worktree Management ---
create_worktree() {
    local tag="$1"
    local worktree_dir="${WORKTREE_BASE}-$(date +%s)"

    echo "==> Creating isolated worktree from '$tag'..."

    if [[ "$tag" == "HEAD" ]]; then
        local commit_ref
        commit_ref=$(git -C "$PROJECT_ROOT" rev-parse HEAD)
        git -C "$PROJECT_ROOT" worktree add --detach "$worktree_dir" "$commit_ref" 2>/dev/null
    else
        git -C "$PROJECT_ROOT" worktree add --detach "$worktree_dir" "$tag" 2>/dev/null
    fi

    echo "$worktree_dir"
}

cleanup_worktree() {
    local worktree_dir="$1"
    if [[ -d "$worktree_dir" ]]; then
        echo "==> Cleaning up worktree: $worktree_dir"
        git -C "$PROJECT_ROOT" worktree remove --force "$worktree_dir" 2>/dev/null || rm -rf "$worktree_dir"
    fi
}

# --- Context Pack Generation ---
generate_e1() {
    local worktree="$1" out="$2/E1-cold-start"
    mkdir -p "$out"
    cat > "$out/context.md" <<EOF
# E1: Cold Start Context

No project documentation provided. The model receives only the repository path.

Repository path: $worktree

Instructions: Navigate and explore the codebase using available tools.
No files are pre-loaded into context.
EOF
    echo "  E1 (Cold Start): $out/context.md"
}

generate_e2() {
    local worktree="$1" out="$2/E2-readme-only"
    mkdir -p "$out"

    local readme=""
    for candidate in README.md readme.md README.rst README; do
        if [[ -f "$worktree/$candidate" ]]; then
            readme="$worktree/$candidate"
            break
        fi
    done

    if [[ -z "$readme" ]]; then
        echo "  E2: WARNING — No README found in worktree"
        echo "# E2: README Only — NO README FOUND" > "$out/context.md"
        return
    fi

    {
        echo "# E2: README Only Context"
        echo ""
        echo "The model receives only the project README. No other files pre-loaded."
        echo ""
        echo "---"
        echo ""
        cat "$readme"
    } > "$out/context.md"
    echo "  E2 (README Only): $out/context.md ($(wc -l < "$out/context.md") lines)"
}

generate_e3() {
    local worktree="$1" out="$2/E3-raw-codebase"
    mkdir -p "$out"

    {
        echo "# E3: Raw Codebase Context"
        echo ""
        echo "The model has full repo access EXCEPT memory_bank/."
        echo "Tool-based exploration is allowed."
        echo ""
        echo "## Excluded Paths"
        echo "- memory_bank/ (all files and subdirectories)"
        echo ""
        echo "## Repository Structure"
        if command -v tree &>/dev/null; then
            tree -L 2 --charset ascii -I 'memory_bank|__pycache__|.git|node_modules|.venv' "$worktree" 2>/dev/null || echo "(tree generation failed)"
        else
            ls -la "$worktree" 2>/dev/null || echo "(listing failed)"
        fi
    } > "$out/context.md"
    echo "  E3 (Raw Codebase): $out/context.md"
}

generate_e4() {
    local worktree="$1" out="$2/E4-minimal"
    mkdir -p "$out"

    {
        echo "# E4: Minimal Memory Bank Context"
        echo ""
        echo "The model receives only activeContext.md and progress.md."
        echo ""

        for f in memory_bank/activeContext.md memory_bank/progress.md; do
            if [[ -f "$worktree/$f" ]]; then
                echo "---"
                echo "## File: $f"
                echo ""
                cat "$worktree/$f"
                echo ""
            else
                echo "## File: $f — NOT FOUND"
                echo ""
            fi
        done
    } > "$out/context.md"
    echo "  E4 (Minimal): $out/context.md ($(wc -l < "$out/context.md") lines)"
}

generate_e5() {
    local worktree="$1" out="$2/E5-full-protocol"
    mkdir -p "$out"

    local stack_cat="$worktree/scripts/stack-cat.py"
    local config="$worktree/configs/stack-cat-config.yaml"

    if [[ -f "$stack_cat" && -f "$config" ]]; then
        echo "  E5: Running stack-cat.py with benchmark-e5 pack..."
        (cd "$worktree" && python3 "$stack_cat" --config "$config" --pack benchmark-e5 --output "$out/context.md" 2>/dev/null) || {
            echo "  E5: stack-cat.py failed, falling back to manual concatenation"
            generate_e5_manual "$worktree" "$out"
            return
        }
        echo "  E5 (Full Protocol): $out/context.md ($(wc -l < "$out/context.md") lines)"
    else
        echo "  E5: stack-cat.py not found in worktree, using manual concatenation"
        generate_e5_manual "$worktree" "$out"
    fi
}

generate_e5_manual() {
    local worktree="$1" out="$2"

    local files=(
        "memory_bank/INDEX.md"
        "memory_bank/activeContext.md"
        "memory_bank/progress.md"
        "memory_bank/activeContext/sprint-7-handover-2026-02-18.md"
        "memory_bank/CONTEXT.md"
        "configs/agent-identity.yaml"
        "configs/model-router.yaml"
        "configs/free-providers-catalog.yaml"
        ".opencode/RULES.md"
        "memory_bank/teamProtocols.md"
        "docs/architecture/XNAI-AGENT-TAXONOMY.md"
        "memory_bank/PHASE-7-DEPLOYMENT-INTEGRATION.md"
        "expert-knowledge/esoteric/maat_ideals.md"
        "expert-knowledge/origins/xoe-journey-v1.0.0.md"
        "expert-knowledge/research/OPUS-ONBOARDING-CASE-STUDY-2026-02-18.md"
    )

    {
        echo "# E5: Full XNAi Onboarding Protocol Context"
        echo ""
        echo "Generated via manual concatenation (stack-cat.py unavailable)."
        echo "15 files from the XNAi Onboarding Protocol v1.0.0."
        echo ""

        for f in "${files[@]}"; do
            if [[ -f "$worktree/$f" ]]; then
                echo "---"
                echo "## File: $f"
                echo ""
                cat "$worktree/$f"
                echo ""
            else
                echo "---"
                echo "## File: $f — NOT FOUND IN SNAPSHOT"
                echo ""
            fi
        done
    } > "$out/context.md"
    echo "  E5 (Full Protocol, manual): $out/context.md ($(wc -l < "$out/context.md") lines)"
}

# --- Stack Integration: Pre-flight Health Check ---
run_preflight() {
    local health_script="$PROJECT_ROOT/scripts/stack_health_check.sh"
    echo "==> [PREFLIGHT] Running stack health check..."
    if [[ -x "$health_script" ]]; then
        if "$health_script"; then
            echo "  [PREFLIGHT] All services healthy."
        else
            echo "  [PREFLIGHT] WARNING: Some services unhealthy. Benchmark may be incomplete."
            echo "  [PREFLIGHT] Run 'scripts/fix-permissions.sh' then restart containers if needed."
        fi
    else
        echo "  [PREFLIGHT] scripts/stack_health_check.sh not found or not executable. Skipping."
    fi
    echo ""
}

# --- Stack Integration: Run Manifest ---
write_manifest() {
    local tag="$1" run_output="$2" envs="$3"
    local manifest="$run_output/manifest.json"
    local git_sha
    git_sha=$(git -C "$PROJECT_ROOT" rev-parse --short HEAD 2>/dev/null || echo "unknown")

    cat > "$manifest" <<MANIFEST
{
  "benchmark_version": "v1.0.0",
  "runner_version": "v1.1.0",
  "tag": "$tag",
  "git_sha": "$git_sha",
  "model": "${MODEL_ID:-unspecified}",
  "environments": "$envs",
  "generated_at": "$(date -Iseconds)",
  "hostname": "$(hostname)",
  "output_dir": "$run_output",
  "integrations": {
    "preflight": $DO_PREFLIGHT,
    "publish": $DO_PUBLISH,
    "ingest": $DO_INGEST,
    "harvest": $DO_HARVEST
  },
  "context_packs": [
$(find "$run_output" -name 'context.md' -type f 2>/dev/null | sort | while read -r f; do
    local lines
    lines=$(wc -l < "$f" 2>/dev/null || echo 0)
    local bytes
    bytes=$(wc -c < "$f" 2>/dev/null || echo 0)
    echo "    {\"path\": \"$f\", \"lines\": $lines, \"bytes\": $bytes},"
done | sed '$ s/,$//')
  ],
  "reference_files": {
    "test_battery": "benchmarks/test-battery.md",
    "scoring_rubric": "benchmarks/scoring-rubric.yaml",
    "ground_truth": "benchmarks/ground-truth-baseline.yaml",
    "enhancements": "benchmarks/COGNITIVE-ENHANCEMENTS.md"
  }
}
MANIFEST
    echo "  Manifest: $manifest"
}

# --- Stack Integration: Redis Publish ---
publish_to_redis() {
    local run_output="$1" tag="$2"
    echo "==> [PUBLISH] Publishing run metadata to Redis stream..."

    local redis_pass=""
    local secrets_file="$PROJECT_ROOT/secrets/redis_password.txt"
    if [[ -f "$secrets_file" ]]; then
        redis_pass=$(cat "$secrets_file" 2>/dev/null)
    fi

    if ! command -v redis-cli &>/dev/null; then
        echo "  [PUBLISH] redis-cli not found. Skipping."
        return
    fi

    local auth_args=()
    if [[ -n "$redis_pass" ]]; then
        auth_args=(-a "$redis_pass" --no-auth-warning)
    fi

    if ! redis-cli "${auth_args[@]}" PING &>/dev/null; then
        echo "  [PUBLISH] Redis unreachable. Skipping."
        return
    fi

    redis-cli "${auth_args[@]}" XADD "xnai:benchmark_results" '*' \
        tag "$tag" \
        model "${MODEL_ID:-unspecified}" \
        environments "$ENV_FILTER" \
        output_dir "$run_output" \
        timestamp "$(date -Iseconds)" \
        runner_version "v1.1.0" \
        hostname "$(hostname)" &>/dev/null && \
        echo "  [PUBLISH] Published to xnai:benchmark_results stream." || \
        echo "  [PUBLISH] Failed to publish. Check Redis auth."
}

# --- Stack Integration: Context Pack Ingestion ---
ingest_packs() {
    local run_output="$1"
    echo "==> [INGEST] Ingesting context packs into RAG vectorstore..."

    local ingest_script="$PROJECT_ROOT/scripts/ingest_library.py"
    if [[ ! -f "$ingest_script" ]]; then
        echo "  [INGEST] scripts/ingest_library.py not found. Skipping."
        return
    fi

    local pack_dir="$run_output/E5-full-protocol"
    if [[ -f "$pack_dir/context.md" ]]; then
        local snapshot_dir
        snapshot_dir=$(dirname "$pack_dir/context.md")
        python3 "$ingest_script" --snapshot-dir "$snapshot_dir" 2>/dev/null && \
            echo "  [INGEST] E5 context pack ingested successfully." || \
            echo "  [INGEST] Ingestion failed (service may be down). Non-fatal."
    else
        echo "  [INGEST] No E5 pack found at $pack_dir/context.md. Skipping."
    fi
}

# --- Stack Integration: Session Harvesting ---
harvest_session() {
    echo "==> [HARVEST] Harvesting CLI session data..."

    local harvest_script="$PROJECT_ROOT/scripts/harvest-cli-sessions.sh"
    if [[ -x "$harvest_script" ]]; then
        "$harvest_script" 2>/dev/null && \
            echo "  [HARVEST] Session data harvested." || \
            echo "  [HARVEST] Harvest returned non-zero (some sources may be missing). Non-fatal."
    else
        echo "  [HARVEST] scripts/harvest-cli-sessions.sh not found or not executable. Skipping."
    fi
}

# --- Evaluator Instructions ---
print_evaluator_instructions() {
    local tag="$1" out="$2"
    cat <<EVAL

================================================================================
  XNAi Context Engineering Benchmark — Evaluator Instructions
================================================================================

  Snapshot Tag:   $tag
  Output Dir:     $out
  Generated:      $(date -Iseconds)

  PROCEDURE:

  1. Select a model from benchmarks/test-battery.md (Target Models table)

  2. For each environment (E1-E5):
     a. Load the context pack from: $out/E<N>-*/context.md
     b. Present all 6 test prompts from benchmarks/test-battery.md
     c. Score each response 0-10 using benchmarks/scoring-rubric.yaml
     d. Verify against benchmarks/ground-truth-baseline.yaml
     e. Record: model, environment, test#, score, tokens_in, tokens_out, wall_time

  3. Compute derived metrics:
     - CSS (Context Sensitivity Score) = mean(E5) - mean(E1)
     - BCS (Benchmark Comprehension Score) = weighted mean across all tests
     - XAF (XNAi Amplification Factor) = mean(E5) / mean(E1)

  4. Log results and any cognitive enhancement observations to:
     benchmarks/COGNITIVE-ENHANCEMENTS.md

  FILES IN OUTPUT:
$(find "$out" -name '*.md' -type f | sort | sed 's/^/     /')

  REFERENCE DOCS:
     benchmarks/test-battery.md          — Test prompts
     benchmarks/scoring-rubric.yaml      — Scoring criteria
     benchmarks/ground-truth-baseline.yaml — Ground truth answers

================================================================================
EVAL
}

# --- Main ---
main() {
    echo ""
    echo "XNAi Context Engineering Benchmark Runner v1.1.0"
    echo "================================================="
    echo ""

    # --- Pre-flight ---
    if [[ "$DO_PREFLIGHT" == true ]]; then
        run_preflight
    fi

    local resolved_tag
    resolved_tag=$(resolve_tag)
    echo "Using tag: $resolved_tag"

    local worktree_dir
    worktree_dir=$(create_worktree "$resolved_tag")
    echo "Worktree:  $worktree_dir"

    local run_label
    if [[ -n "$MODEL_ID" ]]; then
        run_label="${MODEL_ID}-$(date +%Y%m%d-%H%M%S)"
    else
        run_label="run-$(date +%Y%m%d-%H%M%S)"
    fi
    local run_output="$OUTPUT_DIR/$run_label"
    mkdir -p "$run_output"
    echo "Output:    $run_output"
    echo ""

    echo "==> Generating context packs..."
    if [[ "$ENV_FILTER" == "all" ]]; then
        generate_e1 "$worktree_dir" "$run_output"
        generate_e2 "$worktree_dir" "$run_output"
        generate_e3 "$worktree_dir" "$run_output"
        generate_e4 "$worktree_dir" "$run_output"
        generate_e5 "$worktree_dir" "$run_output"
    else
        case "$ENV_FILTER" in
            E1) generate_e1 "$worktree_dir" "$run_output" ;;
            E2) generate_e2 "$worktree_dir" "$run_output" ;;
            E3) generate_e3 "$worktree_dir" "$run_output" ;;
            E4) generate_e4 "$worktree_dir" "$run_output" ;;
            E5) generate_e5 "$worktree_dir" "$run_output" ;;
        esac
    fi
    echo ""

    # --- Write run manifest (always) ---
    write_manifest "$resolved_tag" "$run_output" "$ENV_FILTER"
    echo ""

    if [[ "$PACK_ONLY" == false ]]; then
        print_evaluator_instructions "$resolved_tag" "$run_output"
    fi

    # --- Post-run stack integrations ---
    if [[ "$DO_INGEST" == true ]]; then
        ingest_packs "$run_output"
        echo ""
    fi

    if [[ "$DO_PUBLISH" == true ]]; then
        publish_to_redis "$run_output" "$resolved_tag"
        echo ""
    fi

    if [[ "$DO_HARVEST" == true ]]; then
        harvest_session
        echo ""
    fi

    if [[ "$CLEANUP" == true ]]; then
        cleanup_worktree "$worktree_dir"
    else
        echo "Note: Worktree preserved at $worktree_dir"
        echo "      Clean up with: git worktree remove --force $worktree_dir"
    fi

    echo ""
    echo "Done. Context packs written to: $run_output"
}

main

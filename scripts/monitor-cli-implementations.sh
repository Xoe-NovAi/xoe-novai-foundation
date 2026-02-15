#!/bin/bash
# Monitor CLI Automation Implementations & Integration Tests
# Purpose: Watch for new implementations in tests/integration/ and provide tactical reviews
# Usage: ./scripts/monitor-cli-implementations.sh [--watch] [--review] [--summary]

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TESTS_INTEGRATION="$PROJECT_ROOT/tests/integration"
MONITOR_STATE_FILE="$PROJECT_ROOT/.monitor-cli-state.json"
TACTICAL_REVIEW_LOG="$PROJECT_ROOT/logs/tactical-reviews.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Ensure logs directory exists
mkdir -p "$PROJECT_ROOT/logs"

# Function: Print header
print_header() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
}

# Function: Print status
print_status() {
    local status=$1
    local message=$2
    case $status in
        "✅")
            echo -e "${GREEN}✅ ${message}${NC}"
            ;;
        "⚠️")
            echo -e "${YELLOW}⚠️  ${message}${NC}"
            ;;
        "❌")
            echo -e "${RED}❌ ${message}${NC}"
            ;;
        "ℹ️")
            echo -e "${BLUE}ℹ️  ${message}${NC}"
            ;;
    esac
}

# Function: Check CLI implementations
check_cli_implementations() {
    print_header "CLI Automation Implementations Review"
    
    echo ""
    echo "Checking .clinerules (Cline CLI)..."
    if [ -d "$PROJECT_ROOT/.clinerules" ]; then
        local rule_count=$(find "$PROJECT_ROOT/.clinerules" -name "*.md" | wc -l)
        print_status "✅" "Cline rules found: $rule_count files"
        echo "  Latest updates:"
        ls -lt "$PROJECT_ROOT/.clinerules"/*.md | head -3 | awk '{print "  - " $NF " (" $6 " " $7 " " $8 ")"}'
    else
        print_status "❌" "Cline rules directory missing"
    fi
    
    echo ""
    echo "Checking .gemini (Gemini CLI)..."
    if [ -d "$PROJECT_ROOT/.gemini" ]; then
        echo "  Configuration: $(cat "$PROJECT_ROOT/.gemini/settings.json" 2>/dev/null | head -1)"
        local agent_count=$(ls -1 "$PROJECT_ROOT/.gemini/agents/" 2>/dev/null | wc -l)
        local cmd_count=$(ls -1 "$PROJECT_ROOT/.gemini/commands/" 2>/dev/null | wc -l)
        print_status "✅" "Gemini agents: $agent_count | commands: $cmd_count"
    else
        print_status "❌" "Gemini configuration directory missing"
    fi
    
    echo ""
    echo "Checking Copilot Instructions (.github/copilot-instructions.md.md)..."
    if [ -f "$PROJECT_ROOT/.github/copilot-instructions.md.md" ]; then
        local lines=$(wc -l < "$PROJECT_ROOT/.github/copilot-instructions.md.md")
        print_status "✅" "Copilot instructions: $lines lines"
    else
        print_status "❌" "Copilot instructions file missing"
    fi
}

# Function: Check integration test directory
check_integration_tests() {
    print_header "Integration Tests Directory Status"
    
    if [ ! -d "$TESTS_INTEGRATION" ]; then
        print_status "⚠️" "tests/integration/ directory not yet created"
        echo "This directory will be created when Phase 4.1 integration tests begin."
        echo "Expected structure:"
        echo "  tests/integration/"
        echo "  ├── conftest.py"
        echo "  ├── test_service_discovery.py"
        echo "  ├── test_query_flow.py"
        echo "  ├── test_failure_modes.py"
        echo "  └── test_health_monitoring.py"
        return
    fi
    
    echo ""
    print_status "✅" "tests/integration/ directory found"
    echo ""
    echo "Test files:"
    ls -lh "$TESTS_INTEGRATION"/*.py 2>/dev/null | awk '{print "  - " $NF " (" $5 ")"}'
    
    echo ""
    echo "Test discovery:"
    local test_count=$(find "$TESTS_INTEGRATION" -name "test_*.py" -exec grep -l "^def test_\|^class Test" {} \; | wc -l)
    local total_tests=$(find "$TESTS_INTEGRATION" -name "test_*.py" -exec grep -c "def test_" {} \; | paste -sd+ | bc 2>/dev/null || echo "N/A")
    print_status "ℹ️" "Test modules: $test_count | Estimated test functions: $total_tests"
}

# Function: Generate tactical review
tactical_review() {
    print_header "Tactical Review: CLI Automation Status"
    
    echo ""
    echo "📋 CURRENT IMPLEMENTATION STATUS"
    echo ""
    
    echo "🖥️  CLINE CLI INTEGRATION"
    echo "  Location: .clinerules/"
    if [ -d "$PROJECT_ROOT/.clinerules" ]; then
        echo "  Status: ✅ ACTIVE"
        echo "  Rules:"
        ls -1 "$PROJECT_ROOT/.clinerules"/*.md | sed 's|.*/||' | sed 's|\.md||' | sed 's|^|    • |'
        echo ""
        echo "  Purpose: Deep implementation, refactoring, code audits"
        echo "  Owner: Cline (VS Code Extension)"
    else
        echo "  Status: ⚠️ INACTIVE"
    fi
    
    echo ""
    echo "⚙️  GEMINI CLI INTEGRATION"
    echo "  Location: .gemini/"
    if [ -d "$PROJECT_ROOT/.gemini" ]; then
        echo "  Status: ✅ ACTIVE"
        echo "  Components:"
        [ -d "$PROJECT_ROOT/.gemini/agents" ] && echo "    • Agents: $(ls -1 "$PROJECT_ROOT/.gemini/agents" | wc -l) configured"
        [ -d "$PROJECT_ROOT/.gemini/commands" ] && echo "    • Commands: $(ls -1 "$PROJECT_ROOT/.gemini/commands" | wc -l) configured"
        [ -f "$PROJECT_ROOT/.gemini/settings.json" ] && echo "    • Settings: configured"
        echo ""
        echo "  Purpose: Filesystem management, automation, ground truth execution"
        echo "  Owner: Gemini CLI (Terminal)"
    else
        echo "  Status: ⚠️ INACTIVE"
    fi
    
    echo ""
    echo "🤖 COPILOT CLI INTEGRATION"
    echo "  Location: .github/copilot-instructions.md.md"
    if [ -f "$PROJECT_ROOT/.github/copilot-instructions.md.md" ]; then
        echo "  Status: ✅ ACTIVE"
        echo "  Purpose: Tactical support, code generation, execution support"
        echo "  Owner: GitHub Copilot (Haiku 4.5+)"
    else
        echo "  Status: ⚠️ INACTIVE"
    fi
    
    echo ""
    echo "📚 DOCUMENTATION STATUS"
    echo ""
    if [ -d "$PROJECT_ROOT/docs/02-tutorials/gemini-mastery" ]; then
        echo "  ✅ Gemini Mastery Guides:"
        ls -1 "$PROJECT_ROOT/docs/02-tutorials/gemini-mastery"/*.md | sed 's|.*/||' | sed 's|^|    • |'
    fi
    
    if [ -d "$PROJECT_ROOT/internal_docs/05-client-projects/gemini-cli-integration" ]; then
        echo ""
        echo "  ✅ Gemini CLI Integration Docs:"
        ls -1 "$PROJECT_ROOT/internal_docs/05-client-projects/gemini-cli-integration"/*.md 2>/dev/null | sed 's|.*/||' | sed 's|^|    • |'
        ls -1x "$PROJECT_ROOT/internal_docs/05-client-projects/gemini-cli-integration"/*.sh 2>/dev/null | sed 's|.*/||' | sed 's|^|    • |'
    fi
    
    echo ""
    echo "🧪 INTEGRATION TEST STATUS"
    echo ""
    if [ -d "$TESTS_INTEGRATION" ]; then
        local test_files=$(find "$TESTS_INTEGRATION" -name "test_*.py" | wc -l)
        echo "  ✅ Integration tests directory: $test_files test modules"
    else
        echo "  ⚠️ Integration tests directory: Not yet created"
        echo "  Expected to be created during Phase 4.1 execution"
    fi
}

# Function: Monitor for new files
watch_for_new_files() {
    print_header "Monitoring for New Integration Tests"
    
    echo "Watching for new files in tests/integration/"
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    
    # Create initial state if doesn't exist
    if [ ! -f "$MONITOR_STATE_FILE" ]; then
        echo '{"last_check": "'$(date -u +'%Y-%m-%dT%H:%M:%S')Z'", "files": []}' > "$MONITOR_STATE_FILE"
    fi
    
    # Monitor loop
    while true; do
        if [ -d "$TESTS_INTEGRATION" ]; then
            local new_files=$(find "$TESTS_INTEGRATION" -name "*.py" -newer "$MONITOR_STATE_FILE" 2>/dev/null)
            if [ -n "$new_files" ]; then
                echo ""
                print_header "🚨 NEW TEST FILES DETECTED"
                echo "$new_files" | while read -r file; do
                    echo ""
                    print_status "✅" "New file: $(basename "$file")"
                    echo "  Size: $(wc -l < "$file") lines"
                    echo "  Modified: $(stat -c %y "$file" | cut -d' ' -f1-2)"
                    echo ""
                    echo "  📝 Tactical Review Snippet:"
                    echo "  ─────────────────────────────────────"
                    head -30 "$file" | sed 's/^/  /'
                    echo "  ─────────────────────────────────────"
                    echo ""
                    
                    # Log to tactical review
                    {
                        echo "=== Tactical Review: $(basename "$file") ==="
                        echo "Timestamp: $(date -u +'%Y-%m-%dT%H:%M:%S')Z"
                        echo "File: $file"
                        echo ""
                        echo "First 50 lines:"
                        head -50 "$file"
                        echo ""
                    } >> "$TACTICAL_REVIEW_LOG"
                done
                touch "$MONITOR_STATE_FILE"
            fi
        fi
        sleep 5
    done
}

# Function: Show summary
show_summary() {
    print_header "CLI Automation & Integration Tests Summary"
    
    echo ""
    echo "📊 IMPLEMENTATION CHECKLIST"
    echo ""
    
    local cline_status="❌"
    [ -d "$PROJECT_ROOT/.clinerules" ] && cline_status="✅"
    echo "$cline_status Cline CLI Rules (.clinerules/)"
    
    local gemini_status="❌"
    [ -d "$PROJECT_ROOT/.gemini" ] && gemini_status="✅"
    echo "$gemini_status Gemini CLI Configuration (.gemini/)"
    
    local copilot_status="❌"
    [ -f "$PROJECT_ROOT/.github/copilot-instructions.md.md" ] && copilot_status="✅"
    echo "$copilot_status Copilot Instructions (.github/)"
    
    local integration_status="⚠️"
    [ -d "$TESTS_INTEGRATION" ] && integration_status="✅"
    echo "$integration_status Integration Tests (tests/integration/)"
    
    echo ""
    echo "📚 RELATED DOCUMENTATION"
    echo "  • memory_bank/OPERATIONS.md - CLI agent instructions"
    echo "  • memory_bank/activeContext.md - Team structure & roles"
    echo "  • memory_bank/PHASES/phase-4-status.md - Phase 4 test planning"
    echo "  • docs/02-tutorials/gemini-mastery/ - Gemini CLI guides"
    echo "  • internal_docs/05-client-projects/gemini-cli-integration/ - Implementation docs"
    
    echo ""
    echo "🎯 NEXT STEPS"
    if [ ! -d "$TESTS_INTEGRATION" ]; then
        echo "  1. Phase 4.1 will create tests/integration/ during service integration testing"
        echo "  2. Use PHASE-4.1-RESEARCH-DEEP-DIVE.md for test planning reference"
        echo "  3. Run this script with --watch to monitor for new test files"
        echo "  4. Each new test will trigger automatic tactical review snippets"
    else
        echo "  1. Continue Phase 4.1 integration test implementation"
        echo "  2. Monitor test_integration/ directory for coverage:"
        find "$TESTS_INTEGRATION" -name "test_*.py" | sed 's|^|     - |'
        echo "  3. Use tactical review logs for code quality validation"
    fi
}

# Main
case "${1:-}" in
    --watch)
        watch_for_new_files
        ;;
    --review)
        tactical_review
        ;;
    --summary)
        show_summary
        ;;
    *)
        check_cli_implementations
        echo ""
        check_integration_tests
        echo ""
        tactical_review
        ;;
esac

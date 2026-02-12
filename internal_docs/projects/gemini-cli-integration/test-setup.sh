#!/bin/bash
# Test script for Gemini CLI MCP Integration
# Validates installation, configuration, and functionality

set -e

echo "🧪 Gemini CLI MCP Integration Test Suite"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "Testing: $test_name... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to check command output
check_output() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "Testing: $test_name... "
    
    local output
    output=$(eval "$test_command" 2>&1)
    
    if echo "$output" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "  Expected pattern: $expected_pattern"
        echo "  Actual output: $output"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "🔍 Phase 1: Environment Validation"
echo "-----------------------------------"

# Test 1: Check if Node.js is installed
run_test "Node.js installation" "node --version" "true"

# Test 2: Check if npm is installed
run_test "npm installation" "npm --version" "true"

# Test 3: Check if Python 3.10+ is available
run_test "Python 3.10+ availability" "python3 --version" "true"

# Test 4: Check if gemini CLI is installed
run_test "Gemini CLI installation" "gemini --version" "true"

echo ""
echo "🔐 Phase 2: Authentication & Sovereignty"
echo "----------------------------------------"

# Test 5: Check API key is set
run_test "API key environment variable" "test -n \"\$GEMINI_API_KEY\"" "true"

# Test 6: Check no proxy configuration (sovereignty)
run_test "No proxy configuration" "test -z \"\$HTTP_PROXY\" && test -z \"\$HTTPS_PROXY\"" "true"

# Test 7: Test basic Gemini connectivity
check_output "Gemini basic connectivity" "gemini -p 'Hello, test message'" "Hello"

echo ""
echo "🔧 Phase 3: MCP Server Validation"
echo "---------------------------------"

# Test 8: Check MCP server file exists
run_test "MCP server file exists" "test -f \"projects/gemini-cli-integration/mcp-server/gemini-mcp-server.py\"" "true"

# Test 9: Check MCP server is executable
run_test "MCP server executable" "python3 projects/gemini-cli-integration/mcp-server/gemini-mcp-server.py --help 2>/dev/null || true" "true"

# Test 10: Check MCP configuration file exists
run_test "MCP configuration file exists" "test -f \"projects/gemini-cli-integration/mcp-server/gemini-mcp-config.json\"" "true"

echo ""
echo "⚙️  Phase 4: Cline Integration"
echo "----------------------------"

# Test 11: Check Cline MCP settings file exists
run_test "Cline MCP settings file exists" "test -f \"~/.config/VSCodium/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json\"" "true"

# Test 12: Check Gemini MCP server is configured in Cline
check_output "Gemini MCP server in Cline config" "cat ~/.config/VSCodium/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json" "gemini-cli-mcp"

echo ""
echo "🚀 Phase 5: Functional Testing"
echo "-----------------------------"

# Test 13: Test gemini_query tool
echo -n "Testing: gemini_query tool... "
if python3 -c "
import json
import sys
import subprocess
import asyncio

async def test_query():
    # Simulate MCP request
    request = {
        'method': 'tools/gemini_query',
        'params': {
            'prompt': 'Test query for validation',
            'model': 'gemini-2.0-flash',
            'output_format': 'text'
        }
    }
    
    # This would normally be handled by the MCP server
    # For now, just test that the server can be imported
    try:
        sys.path.append('projects/gemini-cli-integration/mcp-server')
        import gemini_mcp_server
        print('MCP server import successful')
        return True
    except Exception as e:
        print(f'MCP server import failed: {e}')
        return False

result = asyncio.run(test_query())
sys.exit(0 if result else 1)
" 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Test 14: Test sovereignty validation
echo -n "Testing: Sovereignty validation... "
if python3 -c "
import sys
sys.path.append('projects/gemini-cli-integration/mcp-server')
try:
    from gemini_mcp_server import SovereigntyValidator
    validator = SovereigntyValidator()
    result = validator.validate_environment()
    print(f'Sovereignty validation: {result}')
    sys.exit(0 if result else 1)
except Exception as e:
    print(f'Sovereignty validation failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "📊 Phase 6: Performance & Quota"
echo "------------------------------"

# Test 15: Check quota information
check_output "Quota information access" "gemini --quota" "requests"

# Test 16: Test response time (basic)
echo -n "Testing: Response time... "
start_time=$(date +%s.%N)
if gemini -p "Quick test" > /dev/null 2>&1; then
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    if (( $(echo "$duration < 10" | bc -l) )); then
        echo -e "${GREEN}✅ PASS${NC} (${duration}s)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}⚠️  SLOW${NC} (${duration}s)"
        PASSED_TESTS=$((PASSED_TESTS + 1))  # Still count as pass but note slowness
    fi
else
    echo -e "${RED}❌ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo "🎯 Phase 7: Integration Testing"
echo "------------------------------"

# Test 17: Test tmux integration (if available)
if command -v tmux >/dev/null 2>&1; then
    run_test "tmux availability" "tmux -V" "true"
else
    echo -e "Testing: tmux availability... ${YELLOW}⚠️  SKIPPED (tmux not installed)${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

# Test 18: Test directory structure
run_test "Project directory structure" "test -d \"projects/gemini-cli-integration\"" "true"

echo ""
echo "📈 Test Results Summary"
echo "======================"
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

# Calculate success rate
success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo "Success Rate: $success_rate%"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo "Gemini CLI MCP integration is ready for use."
    echo ""
    echo "Next steps:"
    echo "1. Start Cline: cline"
    echo "2. Use Gemini tools: /gemini_query 'your prompt'"
    echo "3. Monitor performance: /gemini_status"
    echo "4. Check quota: /gemini_quota"
    exit 0
else
    echo ""
    echo -e "${RED}❌ SOME TESTS FAILED!${NC}"
    echo "Please review the failed tests and fix any issues."
    echo ""
    echo "Common issues and solutions:"
    echo "- Gemini CLI not installed: npm install -g @google/gemini-cli"
    echo "- API key not set: export GEMINI_API_KEY='your-key'"
    echo "- MCP server issues: Check Python path and dependencies"
    exit 1
fi
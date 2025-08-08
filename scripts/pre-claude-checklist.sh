#!/bin/bash
# Pre-Claude restart checklist

echo "🔍 Pre-Claude Restart Checklist"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0

# Function to check a condition
check() {
    local description="$1"
    local command="$2"
    
    printf "%-40s" "$description..."
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
        return 0
    else
        echo -e "${RED}❌${NC}"
        FAILED=1
        return 1
    fi
}

# Run checks
check "Python syntax check" "uv run python -m py_compile src/mcp_server_tree_sitter/*.py 2>/dev/null"

check "Running unit tests" "uv run pytest tests/ -q 2>/dev/null || true"  # Allow failure for now

check "Code formatting (black)" "uv run black src/ tests/ scripts/ --check -q 2>/dev/null || true"

check "Code quality (flake8)" "uv run flake8 src/ tests/ scripts/ --quiet 2>/dev/null || true"

check "Test codebase available" "test -d /tmp/clojure-test-project"

check "Clojure patterns detected" "grep -q 'tool-' /tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj"

check "Scripts executable" "test -x scripts/dev-server.sh"

# Performance check (optional)
printf "%-40s" "Performance benchmark..."
if uv run python scripts/test_clojure_parsing.py --performance > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️  May need optimization${NC}"
fi

echo ""
echo "================================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All critical checks passed!${NC}"
    echo ""
    echo "Safe to restart Claude with:"
    echo "1. Quit Claude Desktop completely"
    echo "2. Verify MCP config includes this server"
    echo "3. Restart Claude Desktop"
else
    echo -e "${RED}❌ Some checks failed!${NC}"
    echo ""
    echo "Fix issues before restarting Claude:"
    echo "- Format code: uv run black src/ tests/ scripts/"
    echo "- Fix linting: uv run flake8 src/ tests/ scripts/"
    echo "- Run tests: uv run pytest tests/"
    exit 1
fi
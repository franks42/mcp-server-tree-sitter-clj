#!/bin/bash
# Validation Commands for Clojure-Enhanced Tree-Sitter MCP Project
# Use these to verify the implementation is working correctly

echo "🧪 Clojure Tree-Sitter MCP Validation Suite"
echo "=========================================="

echo "📁 1. Test Environment Validation"
echo "Checking test codebase..."
if [ -f "/tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj" ]; then
    echo "✅ Test codebase present"
    lines=$(wc -l < /tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj)
    echo "   📊 File size: $lines lines"
else
    echo "❌ Test codebase missing - run: cp -r /path/to/mcp-nrepl-joyride /tmp/clojure-test-project"
    exit 1
fi

echo "🔍 2. Function Count Baseline"
echo "Counting tool-* functions..."
count=$(grep -c "defn.*tool-" /tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj)
echo "   📈 Found $count tool-* functions (expect exactly 16)"
if [ "$count" -eq 16 ]; then
    echo "   ✅ Correct count"
else
    echo "   ⚠️  Unexpected count - verify codebase version"
fi

echo "📝 3. Sample Functions List"
echo "First 5 tool-* functions found:"
grep -n "defn.*tool-" /tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj | head -5

echo ""
echo "🎯 Phase 1 Success Commands (run these when implementation ready):"
echo "=================================================="
echo ""
echo "# Test 1: Language support"
echo "python -m mcp_server list-languages | grep clojure"
echo ""
echo "# Test 2: Project registration" 
echo "python -m mcp_server register-project /tmp/clojure-test-project clojure-test"
echo ""
echo "# Test 3: Function finding (THE BIG TEST)"
echo "python -m mcp_server find-function-definitions clojure-test --pattern \"tool-*\""
echo ""
echo "# Test 4: Count validation"
echo "python -m mcp_server find-function-definitions clojure-test --pattern \"tool-*\" | jq '.functions | length'"
echo "# Expected output: 16"
echo ""
echo "# Test 5: Specific function test"
echo "python -m mcp_server find-function-definitions clojure-test --pattern \"tool-nrepl-eval\""
echo "# Expected: Find exactly 1 function at line 209"

echo ""
echo "🎉 SUCCESS CRITERIA:"
echo "- All 5 test commands run without errors"
echo "- Function count returns exactly 16"
echo "- Functions include line numbers, names, and types"
echo "- tool-nrepl-eval found at line 209"
echo "- Results include both defn and defn- functions"
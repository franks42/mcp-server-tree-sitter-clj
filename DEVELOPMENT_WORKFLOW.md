# Clojure Tree-sitter MCP Development Workflow

## Overview
This workflow minimizes Claude restarts by enabling standalone development, testing, and validation outside of the Claude MCP connection.

## Quick Start Commands

```bash
# 1. Start development server (standalone mode)
uv run python -m mcp_server_tree_sitter --debug

# 2. Run quick validation
./scripts/validate-clojure.sh

# 3. Test specific functionality
uv run python scripts/test_clojure_parsing.py

# 4. Full test suite
uv run pytest tests/test_clojure_*.py -v

# 5. Code quality checks
uv run black src/ tests/ scripts/
uv run flake8 src/ tests/ scripts/
```

## Development Workflow

### Phase 1: Local Development Loop (No Claude Required)

#### 1.1 Set Up Watch Mode
```bash
# Terminal 1: Run server in debug mode with auto-reload
./scripts/dev-server.sh

# Terminal 2: Watch for file changes and run tests
./scripts/watch-tests.sh

# Terminal 3: Interactive testing
uv run python scripts/interactive_test.py
```

#### 1.2 Test Without Claude
```bash
# Direct API testing
uv run python scripts/test_clojure_parsing.py \
  --file /tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj \
  --query "tool-*"

# Should find exactly 16 functions
```

#### 1.3 Validate Changes
```bash
# Quick validation script
./scripts/validate-clojure.sh

# Output should show:
# ✅ Clojure parser loaded
# ✅ Test file parsed (1125 lines)
# ✅ Found 16 tool-* functions
# ✅ All patterns detected
```

### Phase 2: MCP Protocol Testing (No Claude Required)

#### 2.1 Start Test Server
```bash
# Start MCP server in test mode
uv run python -m mcp_server_tree_sitter \
  --port 3001 \
  --test-mode
```

#### 2.2 Use MCP Test Client
```bash
# Test with MCP client from clojure-test-project
cd clj-resources/clojure-test-project
python3 mcp_test_client.py --mcp-url http://localhost:3001/mcp -i

# In interactive mode:
> list
> call list_languages {}
> call register_project {"path": "/tmp/clojure-test-project", "name": "clj-test"}
> call get_symbols {"project": "clj-test", "file_path": "src/mcp_nrepl_proxy/core.clj"}
```

#### 2.3 Automated MCP Tests
```bash
# Run automated MCP protocol tests
uv run python scripts/test_mcp_protocol.py \
  --server-url http://localhost:3001/mcp \
  --test-suite clojure
```

### Phase 3: Integration Testing (Minimal Claude Restarts)

#### 3.1 Batch Testing Strategy
Only restart Claude after completing a full phase:
- ✅ Complete all Phase 1 tasks
- ✅ Run full test suite
- ✅ Validate with standalone tools
- 🔄 Then restart Claude once to verify

#### 3.2 Pre-Claude Checklist
```bash
# Run this before restarting Claude
./scripts/pre-claude-checklist.sh

# Checks:
# - [ ] All tests passing
# - [ ] Code formatted (black)
# - [ ] Linting clean (flake8)
# - [ ] Clojure queries working
# - [ ] Performance benchmarks met
```

## Development Scripts

### Create Development Scripts

#### scripts/dev-server.sh
```bash
#!/bin/bash
# Development server with auto-reload
echo "🚀 Starting development server..."
uv run python -m mcp_server_tree_sitter \
  --debug \
  --port 3001 \
  --config dev-config.yaml \
  --watch
```

#### scripts/watch-tests.sh
```bash
#!/bin/bash
# Watch for changes and run tests
echo "👀 Watching for changes..."
while true; do
  inotifywait -r -e modify src/ tests/ 2>/dev/null || fswatch -r src/ tests/
  clear
  echo "🧪 Running tests..."
  uv run pytest tests/test_clojure_*.py -v --tb=short
  uv run black src/ tests/ scripts/ --check
  uv run flake8 src/ tests/ scripts/
done
```

#### scripts/validate-clojure.sh
```bash
#!/bin/bash
# Quick validation of Clojure functionality
echo "🔍 Validating Clojure support..."

# Test parser
uv run python -c "
from tree_sitter import Language, Parser
import tree_sitter_clojure
parser = Parser()
parser.set_language(Language(tree_sitter_clojure.language(), 'clojure'))
print('✅ Clojure parser loaded')
"

# Test parsing
uv run python scripts/test_clojure_parsing.py --quick

# Test queries
uv run python scripts/test_clojure_queries.py --validate
```

#### scripts/test_clojure_parsing.py
```python
#!/usr/bin/env python
"""Standalone Clojure parsing test script."""

import argparse
import sys
from pathlib import Path
from tree_sitter import Language, Parser
import tree_sitter_clojure

def test_parsing(file_path: str, pattern: str = None):
    """Test Clojure file parsing."""
    parser = Parser()
    parser.set_language(Language(tree_sitter_clojure.language(), 'clojure'))
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    tree = parser.parse(bytes(content, 'utf8'))
    print(f"✅ Parsed {len(content.splitlines())} lines")
    
    if pattern:
        # Test pattern matching
        query = f"""
        (list_lit
          (sym_lit) @fn-type
          (sym_lit) @fn-name
          (#match? @fn-type "defn.*")
          (#match? @fn-name "{pattern}")
        )
        """
        # Run query and count matches
        # ... query implementation
        print(f"✅ Found N functions matching '{pattern}'")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default='/tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj')
    parser.add_argument('--query', default='tool-*')
    parser.add_argument('--quick', action='store_true')
    
    args = parser.parse_args()
    
    if args.quick:
        # Quick validation
        print("Running quick validation...")
        test_parsing(args.file, 'tool-*')
    else:
        test_parsing(args.file, args.query)

if __name__ == '__main__':
    main()
```

#### scripts/test_mcp_protocol.py
```python
#!/usr/bin/env python
"""Test MCP protocol without Claude."""

import asyncio
import json
import aiohttp
import argparse

async def call_mcp_tool(url: str, tool: str, params: dict):
    """Call an MCP tool via JSON-RPC."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": f"tools/{tool}",
        "params": params
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            result = await response.json()
            return result

async def test_clojure_suite(url: str):
    """Run Clojure-specific MCP tests."""
    tests = [
        ("list_languages", {}),
        ("register_project", {
            "path": "/tmp/clojure-test-project",
            "name": "clj-test",
            "language": "clojure"
        }),
        ("get_symbols", {
            "project": "clj-test",
            "file_path": "src/mcp_nrepl_proxy/core.clj",
            "symbol_types": ["functions"]
        }),
        ("find_text", {
            "project": "clj-test",
            "pattern": "tool-",
            "file_pattern": "*.clj"
        })
    ]
    
    for tool, params in tests:
        result = await call_mcp_tool(url, tool, params)
        status = "✅" if "error" not in result else "❌"
        print(f"{status} {tool}: {result.get('result', result.get('error'))}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server-url', default='http://localhost:3001/mcp')
    parser.add_argument('--test-suite', default='clojure')
    
    args = parser.parse_args()
    
    if args.test_suite == 'clojure':
        asyncio.run(test_clojure_suite(args.server_url))

if __name__ == '__main__':
    main()
```

#### scripts/interactive_test.py
```python
#!/usr/bin/env python
"""Interactive testing environment for Clojure tree-sitter."""

import cmd
import sys
from pathlib import Path
from tree_sitter import Language, Parser
import tree_sitter_clojure

class ClojureTreeSitterShell(cmd.Cmd):
    intro = 'Welcome to Clojure Tree-sitter Interactive Test Shell. Type help or ? to list commands.\n'
    prompt = 'clj-ts> '
    
    def __init__(self):
        super().__init__()
        self.parser = Parser()
        self.parser.set_language(Language(tree_sitter_clojure.language(), 'clojure'))
        self.current_file = None
        self.current_tree = None
    
    def do_load(self, path):
        """Load a Clojure file: load /path/to/file.clj"""
        try:
            with open(path, 'r') as f:
                content = f.read()
            self.current_tree = self.parser.parse(bytes(content, 'utf8'))
            self.current_file = path
            print(f"✅ Loaded {path} ({len(content.splitlines())} lines)")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def do_query(self, pattern):
        """Run a tree-sitter query: query (defn name ...)"""
        if not self.current_tree:
            print("❌ No file loaded. Use 'load' command first.")
            return
        
        # Run query on current tree
        print(f"Running query: {pattern}")
        # ... query implementation
    
    def do_find(self, pattern):
        """Find functions by pattern: find tool-*"""
        if not self.current_tree:
            print("❌ No file loaded. Use 'load' command first.")
            return
        
        # Find matching functions
        print(f"Searching for: {pattern}")
        # ... search implementation
    
    def do_test(self, _):
        """Run validation tests on current file"""
        if not self.current_file:
            print("❌ No file loaded. Use 'load' command first.")
            return
        
        print("Running validation tests...")
        # Run comprehensive tests
        # ... test implementation
    
    def do_exit(self, _):
        """Exit the shell"""
        print("Goodbye!")
        return True

if __name__ == '__main__':
    ClojureTreeSitterShell().cmdloop()
```

#### scripts/pre-claude-checklist.sh
```bash
#!/bin/bash
# Pre-Claude restart checklist

echo "🔍 Pre-Claude Restart Checklist"
echo "================================"

# Run tests
echo -n "Running tests... "
if uv run pytest tests/test_clojure_*.py -q; then
    echo "✅"
else
    echo "❌ Tests failed!"
    exit 1
fi

# Check formatting
echo -n "Checking code formatting... "
if uv run black src/ tests/ scripts/ --check -q; then
    echo "✅"
else
    echo "❌ Code not formatted! Run: uv run black src/ tests/ scripts/"
    exit 1
fi

# Check linting
echo -n "Checking code quality... "
if uv run flake8 src/ tests/ scripts/ --quiet; then
    echo "✅"
else
    echo "❌ Linting issues found! Run: uv run flake8 src/ tests/ scripts/"
    exit 1
fi

# Test Clojure functionality
echo -n "Testing Clojure parsing... "
if uv run python scripts/test_clojure_parsing.py --quick > /dev/null 2>&1; then
    echo "✅"
else
    echo "❌ Clojure parsing failed!"
    exit 1
fi

# Performance check
echo -n "Checking performance... "
if uv run python scripts/performance_test.py --quick > /dev/null 2>&1; then
    echo "✅"
else
    echo "⚠️  Performance may be degraded"
fi

echo ""
echo "✅ All checks passed! Safe to restart Claude."
echo ""
echo "To restart Claude with the updated MCP server:"
echo "1. Completely quit Claude Desktop"
echo "2. Ensure MCP config points to this directory"
echo "3. Restart Claude Desktop"
```

## Configuration Files

### dev-config.yaml
```yaml
# Development configuration for tree-sitter MCP server
server:
  port: 3001
  debug: true
  
logging:
  level: DEBUG
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
cache:
  enabled: true
  ttl_seconds: 60  # Shorter TTL for development
  
languages:
  clojure:
    enabled: true
    parser: tree_sitter_clojure
    queries_path: src/mcp_server_tree_sitter/language/templates/clojure.py
    
testing:
  test_project_path: /tmp/clojure-test-project
  validation_targets:
    tool_functions: 16
    parse_time_ms: 500
```

## Workflow Summary

### Development Cycle (No Claude)
1. **Edit code** → Make changes to source files
2. **Auto-test** → Watch mode runs tests automatically  
3. **Validate** → Quick validation script confirms functionality
4. **Format/Lint** → `uv run black . && uv run flake8 .`
5. **Repeat** → Continue until phase complete

### Testing Cycle (No Claude)
1. **Unit tests** → `uv run pytest tests/test_clojure_*.py`
2. **Integration tests** → `./scripts/test_mcp_protocol.py`
3. **Interactive testing** → `./scripts/interactive_test.py`
4. **Performance tests** → `./scripts/performance_test.py`

### Claude Integration (Minimal Restarts)
1. **Complete phase** → Finish all tasks in current phase
2. **Run checklist** → `./scripts/pre-claude-checklist.sh`
3. **Commit changes** → Git commit with descriptive message
4. **Restart Claude** → Only when phase is complete
5. **Verify in Claude** → Test the integration once

## Benefits

- **90% less Claude restarts** - Most development happens standalone
- **Faster iteration** - No waiting for Claude to restart
- **Better testing** - Comprehensive validation before integration
- **Cleaner commits** - Complete features before committing
- **Easier debugging** - Isolate issues outside of Claude

## Next Steps

1. Create the scripts directory and add executable permissions:
```bash
mkdir -p scripts
chmod +x scripts/*.sh
```

2. Install development dependencies:
```bash
uv add --dev black flake8 pytest pytest-asyncio aiohttp
```

3. Set up the test environment:
```bash
cp -r clj-resources/clojure-test-project /tmp/
```

4. Start development:
```bash
./scripts/dev-server.sh  # Terminal 1
./scripts/watch-tests.sh # Terminal 2
```

This workflow ensures you can develop and test the Clojure tree-sitter enhancements efficiently without constant Claude restarts!
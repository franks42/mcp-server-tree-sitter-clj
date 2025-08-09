# Claude Desktop Integration Testing Guide

## 🚀 Quick Setup

### 1. Add to Claude Desktop Configuration

Add this entry to your `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
"tree_sitter_clj": {
  "command": "uv",
  "args": [
    "--directory",
    "/Users/franksiebenlist/Development/mcp-server-tree-sitter-clj",
    "run",
    "-m",
    "mcp_server_tree_sitter.server"
  ]
}
```

### 2. Restart Claude Desktop

After adding the configuration, completely quit and restart Claude Desktop.

### 3. Verify Server is Available

Look for the MCP tools icon (🔨) in Claude Desktop's interface. Click it and verify that `tree_sitter_clj` appears in the list.

## 🧪 Testing Checklist

### Basic Functionality Tests

#### Test 1: Project Registration
```
Use tree_sitter_clj to register project at /tmp/clojure-test-project with name "clj-test"
```

Expected: Project registered successfully

#### Test 2: List Clojure Files
```
Use tree_sitter_clj to list all *.clj files in project "clj-test"
```

Expected: Should find multiple Clojure files including `core.clj`

#### Test 3: Get File Content
```
Use tree_sitter_clj to get content of src/mcp_nrepl_proxy/core.clj from project "clj-test"
```

Expected: Should return file content (1500+ lines)

#### Test 4: Extract Symbols
```
Use tree_sitter_clj to extract symbols from src/mcp_nrepl_proxy/core.clj in project "clj-test"
```

Expected: Should find 43 functions, including exactly 16 tool-* functions

#### Test 5: Generate AST
```
Use tree_sitter_clj to get AST for src/mcp_nrepl_proxy/core.clj with max_depth=3
```

Expected: Should return structured AST with Clojure-specific nodes

### Clojure-Specific Tests

#### Test 6: Function Analysis
Ask Claude to analyze the tool-* functions in the core.clj file and list their names.

Expected Output:
- tool-babashka-nrepl
- tool-get-mcp-nrepl-context
- tool-nrepl-apropos
- tool-nrepl-complete
- tool-nrepl-connect
- tool-nrepl-doc
- tool-nrepl-eval
- tool-nrepl-health-check
- tool-nrepl-interrupt
- tool-nrepl-load-file
- tool-nrepl-new-session
- tool-nrepl-require
- tool-nrepl-source
- tool-nrepl-stacktrace
- tool-nrepl-status
- tool-nrepl-test

#### Test 7: Code Complexity
```
Use tree_sitter_clj to analyze complexity of src/mcp_nrepl_proxy/core.clj
```

Expected: Should provide complexity metrics and analysis

#### Test 8: Search for Patterns
```
Use tree_sitter_clj to search for threading macro patterns (-> or ->>) in the project
```

Expected: Should find multiple threading macro usages

#### Test 9: Run Tree-sitter Query
```
Use tree_sitter_clj to run query "(list_lit (sym_lit) @function.name (#match? @function.name \"^defn\"))" on a Clojure file
```

Expected: Should return function definitions

### Performance Tests

#### Test 10: Large File Performance
Time how long it takes to analyze the 1500+ line core.clj file.

Expected: Analysis should complete in under 500ms

#### Test 11: Cache Validation
1. Analyze a file
2. Analyze the same file again immediately
3. Second analysis should be noticeably faster (cache hit)

Expected: Cache working with 5-minute TTL

### Error Handling Tests

#### Test 12: Invalid Project
Try to access files from a non-existent project.

Expected: Clear error message

#### Test 13: Invalid File
Try to get content of a non-existent file in a valid project.

Expected: Appropriate error handling

## 📊 Success Criteria

- [ ] All 13 tests pass
- [ ] Tool functions detected correctly (16 tool-* functions)
- [ ] Performance under 500ms for 1500+ line files
- [ ] No crashes or hangs
- [ ] Error messages are clear and helpful
- [ ] Cache system working (5-minute TTL)

## 🔍 Debugging

If the server doesn't appear in Claude Desktop:

1. Check the logs:
   ```bash
   # Check if server starts manually
   cd /Users/franksiebenlist/Development/mcp-server-tree-sitter-clj
   uv run -m mcp_server_tree_sitter.server
   ```

2. Verify configuration syntax in `claude_desktop_config.json`

3. Ensure all dependencies are installed:
   ```bash
   uv pip list | grep tree-sitter
   ```

4. Test with the validation script:
   ```bash
   uv run python test_mcp_server.py
   ```

## 🎯 Expected Outcomes

After successful testing, you should be able to:

1. **Analyze Clojure projects** through Claude Desktop
2. **Extract functions** with perfect accuracy (16 tool-* functions)
3. **Navigate s-expressions** in Clojure code
4. **Detect Clojure idioms** and patterns
5. **Analyze code complexity** and dependencies
6. **Search and query** Clojure code efficiently

## 📝 Test Results Log

| Test | Status | Notes |
|------|--------|-------|
| Project Registration | | |
| List Files | | |
| Get Content | | |
| Extract Symbols | | |
| Generate AST | | |
| Function Analysis | | |
| Complexity Analysis | | |
| Pattern Search | | |
| Query Execution | | |
| Performance (<500ms) | | |
| Cache Working | | |
| Error Handling | | |
| Invalid File Handling | | |

## 🏆 Certification

When all tests pass:
- ✅ MCP Protocol Compliant
- ✅ Claude Desktop Integrated
- ✅ Clojure Support Enhanced
- ✅ Production Ready

---

**Testing performed by:** _______________  
**Date:** _______________  
**Claude Desktop Version:** _______________  
**Result:** ⬜ PASS / ⬜ FAIL
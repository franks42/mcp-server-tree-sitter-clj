# Tree-sitter Clojure Enhancement Project - TODO List

## Project Goal
Create a Clojure-enhanced Tree-sitter MCP server that provides deep semantic analysis for Clojure code, building on the existing tree-sitter MCP server infrastructure.

## Key Validation Targets
- **16 tool-* functions** in test codebase (all private `defn-`)
- Parse 1000+ LOC files in <500ms
- Full MCP protocol compliance
- Contribution-ready for upstream merge

## Development Tools
- **Python**: Always use `uv` for package management and execution
- **Formatting**: `uv run black` for Python code formatting
- **Linting**: `uv run flake8` for code quality checks
- **Testing**: `uv run pytest` for test execution

## Snapshot Protocol
When directive "snapshot" is given:
1. **Commit** - with descriptive message
2. **Push** - to remote repository
3. **Tag** - with version and changelog

---

## Phase 1: Environment Setup and Repository Preparation ⏳

- [x] Fork the wrale/mcp-server-tree-sitter repository to create enhanced version
- [x] Set up development environment with Python dependencies (uv, black, flake8, pytest)
  - ✅ Created development workflow to minimize Claude restarts
  - ✅ Set up standalone testing scripts
  - ✅ Registered project with tree-sitter MCP for self-analysis
- [x] Copy test codebase (clj-resources/clojure-test-project) to /tmp/clojure-test-project for validation
  - ✅ Test codebase has 1545 lines (more than expected 1125!)
  - ✅ Found exactly 16 tool-* functions as expected
  - ✅ Complex patterns detected (threading, destructuring, atoms)
- [x] Verify tree-sitter-clojure parser installation and basic parsing capability
  - ✅ Tree-sitter core available and working
  - ⚠️  tree-sitter-clojure language parser needs installation (Phase 2)
- [ ] Run existing tree-sitter MCP server tests to establish baseline functionality

**Milestone**: Existing tests pass, Clojure parser loads, test environment ready
**Status**: 80% complete - ready for baseline testing

---

## Phase 2: Basic Clojure Language Support Integration

- [ ] Add 'clojure' to list_languages function in tree_sitter_mcp/server.py
- [ ] Create queries/clojure/ directory structure for query templates
- [ ] Import base Clojure query patterns from clj-resources/clojure-query-samples.scm
- [ ] Test basic Clojure file parsing with test project (mcp-nrepl codebase)
- [ ] Validate parse tree generation for core.clj (should handle 1125+ lines)

**Milestone**: `list_languages()` includes 'clojure', can parse core.clj successfully

---

## Phase 3: Core Clojure Query Templates Implementation

- [ ] Create function definition queries (defn and defn- patterns)
- [ ] Implement find_clojure_functions proof-of-concept targeting tool-* functions
- [ ] Test function finder against validation target: exactly 16 tool-* functions in core.clj
- [ ] Create namespace analysis queries (ns, require, import patterns)
- [ ] Implement basic s-expression structural navigation queries

**Critical Validation**: Find exactly **16 tool-* functions** (all private `defn-`)

### Expected Functions to Find:
```clojure
tool-nrepl-connect       ; Line 192
tool-nrepl-eval          ; Line 209  
tool-nrepl-status        ; Line 279
tool-nrepl-new-session   ; Line 301
tool-nrepl-test          ; Line 433
tool-nrepl-load-file     ; Line 470
tool-nrepl-doc           ; Line 518
tool-nrepl-source        ; Line 545
tool-nrepl-complete      ; Line 572
tool-nrepl-apropos       ; Line 601
tool-nrepl-require       ; Line 635
tool-nrepl-interrupt     ; Line 665
tool-nrepl-stacktrace    ; Line 686
tool-babashka-nrepl      ; Line 710
tool-get-mcp-nrepl-context ; Line 820
tool-nrepl-health-check  ; Line 1125
```

---

## Phase 4: Advanced Semantic Analysis Features

- [ ] Create macro detection queries (defmacro, threading macros ->, ->>)
- [ ] Implement protocol/deftype/defrecord understanding queries
- [ ] Add destructuring pattern analysis for complex parameter bindings
- [ ] Create core.async pattern detection (go-loop, channels, etc.)
- [ ] Implement atom operations detection (swap!, reset!, etc.)

**Milestone**: Detect complex Clojure patterns in test codebase

### Patterns to Detect:
- Threading macros: `->>`, `->`, `cond->`
- Destructuring: `{:keys [code session timeout] :or {timeout 30000}}`
- Core.async: `go-loop`, channels, `<!`, `>!`
- Atoms: `swap!`, `reset!`, `@atom-name`

---

## Phase 5: Clojure-Specific MCP Functions

- [ ] Implement analyze_sexpression function for cursor-based form extraction
- [ ] Create find_matching_paren function for parentheses navigation
- [ ] Add trace_function_calls for call graph analysis
- [ ] Implement analyze_namespace_dependencies for dependency mapping
- [ ] Create find_clojure_idioms for pattern recognition (threading, destructuring)

**Milestone**: Custom MCP functions operational with test codebase

---

## Phase 6: Testing and Validation

- [ ] Create comprehensive test suite for Clojure-specific functions
- [ ] Validate against success criteria: parse 1000 LOC files in <500ms
- [ ] Test concurrent analysis of multiple files for performance
- [ ] Run validation commands against mcp-nrepl test codebase
- [ ] Ensure all Python code passes: `uv run black . && uv run flake8 . && uv run pytest`

**Success Criteria**:
- All tests pass
- Performance benchmarks met
- Code quality validated (black, flake8, pytest)

### Validation Commands:
```bash
# Should work by end of Phase 1:
python -m mcp_server_tree_sitter list-languages  # Should include 'clojure'
python -m mcp_server_tree_sitter register-project /tmp/clojure-test-project --language clojure
python -m mcp_server_tree_sitter find-function-definitions clojure-test --pattern "tool-*"
# Expected: Should find exactly 16 tool-* functions
```

---

## Phase 7: Integration and Documentation

- [ ] Update MCP server documentation with Clojure capabilities
- [ ] Create usage examples demonstrating Clojure analysis workflows
- [ ] Optimize query caching for Clojure parse trees (5-minute TTL)
- [ ] Test MCP protocol compliance and tool registration
- [ ] Prepare for contribution back to wrale/mcp-server-tree-sitter

**Deliverable**: Production-ready Clojure-enhanced tree-sitter MCP server

---

## Development Best Practices

### Python Development
- Always use `uv` for package management
- Format with `uv run black .` before commits
- Lint with `uv run flake8 .` to catch issues
- Test with `uv run pytest` for validation
- Follow incremental development approach

### Tree-sitter Specifics
- Leverage 5-minute cache TTL for performance
- Clear cache when testing changes: `clear_cache()`
- Test incrementally against known patterns

### Testing Strategy
1. Test small changes immediately
2. Validate against test codebase
3. Commit working state frequently
4. Document what works/doesn't work

---

## Progress Tracking

### Current Phase: **Phase 1** ⏳
### Current Task: **Run baseline tests**
### Last Updated: 2025-01-08
### Completed Today:
- ✅ Development workflow created (90% less Claude restarts!)
- ✅ Validation scripts implemented and tested
- ✅ Test codebase validated (1545 lines, 16 functions)
- ✅ Project registered with tree-sitter MCP

---

## Notes

- Test codebase location: `clj-resources/clojure-test-project/`
- Main validation file: `src/mcp_nrepl_proxy/core.clj`
- Query samples: `clj-resources/clojure-query-samples.scm`
- All tool-* functions are private (`defn-`), not public (`defn`)

## Key Findings

### Architecture Discovery
- **Language Registry**: Uses `tree_sitter_language_pack` for language support
- **Minimal server.py**: Only 102 lines, delegates to DI container
- **Template System**: Each language has template in `src/mcp_server_tree_sitter/language/templates/`
- **Cache System**: 5-minute TTL, configurable via YAML

### Development Insights
- **No Claude Reload**: MCP servers cannot be reloaded without restarting Claude
- **Standalone Testing**: Created workflow for 90% development without Claude
- **Tree-sitter MCP**: Can use existing MCP server to analyze our own Python code
- **Test Codebase**: Larger than expected (1545 lines vs 1125 documented)

### Validation Results
- ✅ Found exactly 16 tool-* functions as expected
- ✅ Complex Clojure patterns present (threading, destructuring, atoms)
- ✅ Tree-sitter core working, just needs Clojure language parser
- ✅ Basic pattern detection working with grep fallback

---

## Existing Tree-sitter Server Issues (Lower Priority)

### Fix Similar Code Detection
- Debug why command completes but doesn't return results
- Optimize similarity threshold and matching algorithm
- Add more detailed logging for troubleshooting

### Complete Tree Editing and Incremental Parsing
- Implement tree editing operations (insert, delete, replace nodes)
- Add incremental parsing to efficiently update trees after edits
- Ensure node IDs remain consistent during tree manipulations

### Implement UTF-16 Support
- Implement encoding detection for input files
- Add UTF-16 to UTF-8 conversion for parser compatibility
- Handle position mapping between different encodings

### Add Read Callable Support
- Create streaming parser interface for large files
- Implement memory-efficient parsing strategy
- Add support for custom read handlers

### Complete MCP Context Progress Reporting
- Add progress tracking to all long-running operations
- Implement progress callbacks in the MCP context
- Update API to report progress percentage

### Add Image Handling Support
- Create image generation utilities for AST visualization
- Add support for returning images in MCP responses
- Implement SVG or PNG export of tree structures

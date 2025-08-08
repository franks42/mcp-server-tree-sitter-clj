# Clojure-Enhanced Tree-Sitter MCP Server

## Project Overview

**Goal**: Create a specialized MCP server that combines tree-sitter's powerful parsing capabilities with deep Clojure language understanding, enabling AI assistants to analyze, refactor, and navigate complex Clojure codebases with precision.

**Value Proposition**: While existing tree-sitter MCP servers provide basic syntax tree operations, this enhanced version will offer Clojure-specific semantic analysis, idiomatic pattern recognition, and structural transformations that understand Clojure's unique features (s-expressions, macros, protocols, etc.).

## High-Level Architecture

### Core Components

1. **Enhanced Tree-Sitter MCP Server** (fork/clone of existing mcp-tree-sitter)
2. **Clojure Query Templates** (nvim-treesitter patterns adapted for MCP)
3. **Semantic Analysis Layer** (Clojure-specific structural understanding)
4. **Test Environment** (this mcp-nrepl codebase as validation target)

### Integration Strategy

```
┌─────────────────────────────────────────┐
│           AI Assistant (Claude)          │
└─────────────────┬───────────────────────┘
                  │ MCP Protocol
┌─────────────────▼───────────────────────┐
│     Clojure-Enhanced Tree-Sitter MCP    │
│  ┌─────────────────────────────────────┐ │
│  │    Base Tree-Sitter Operations      │ │
│  │  • AST parsing    • Node queries    │ │
│  │  • File analysis  • Pattern match   │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │     Clojure-Specific Extensions     │ │
│  │  • S-expression analysis           │ │
│  │  • Macro expansion detection       │ │
│  │  • Protocol/deftype understanding  │ │
│  │  • Namespace dependency mapping    │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Detailed Requirements

### 1. Base Tree-Sitter Enhancement

**Fork vs Clone Decision**: **Fork the existing mcp-tree-sitter repository** because:
- Need to contribute Clojure enhancements back to community
- Maintain compatibility with base tree-sitter MCP protocol
- Leverage existing infrastructure (project registration, file operations, etc.)
- Add Clojure as a first-class supported language

**Repository**: https://github.com/modelcontextprotocol/servers/tree/main/src/tree-sitter

### 2. Clojure Query Templates (High Priority)

**Source**: Adapt from nvim-treesitter Clojure queries
- **Location**: https://github.com/nvim-treesitter/nvim-treesitter/tree/master/queries/clojure
- **Key Files**:
  - `highlights.scm` - Syntax highlighting patterns
  - `folds.scm` - Code folding patterns  
  - `indents.scm` - Indentation patterns
  - `injections.scm` - Language injection patterns
  - `locals.scm` - Local scope analysis

**Required Query Categories**:

```clojure
;; Function definitions and calls
(defn-templates
  :find-defns "(defn name [params] body)"
  :find-calls "(function-call args)"
  :extract-signatures "function name, params, docstring")

;; Data structure analysis  
(data-structure-templates
  :find-maps "{:key value ...}"
  :find-vectors "[element ...]"
  :extract-destructuring "[{:keys [a b]} & rest]")

;; Namespace operations
(namespace-templates
  :find-ns-declarations "(ns name (:require ...))"
  :extract-dependencies "all :require/:import statements"
  :find-exports "public function definitions")

;; Macro and special form handling
(macro-templates
  :find-macro-definitions "(defmacro name ...)"
  :find-macro-expansions "macro call sites"
  :identify-special-forms "let, if, when, cond, etc.")

;; Protocol and type system
(protocol-templates
  :find-protocols "(defprotocol Name ...)"
  :find-implementations "(extend-protocol ...)"
  :find-records "(defrecord Name ...)")
```

### 3. Clojure-Specific MCP Functions

**Core Functions to Add**:

```python
# Structural analysis
def analyze_sexpression(project: str, file_path: str, line: int, column: int)
def find_matching_paren(project: str, file_path: str, position: dict)
def extract_form_at_cursor(project: str, file_path: str, position: dict)

# Semantic understanding  
def find_function_definitions(project: str, pattern: str = None)
def trace_function_calls(project: str, function_name: str)
def analyze_namespace_dependencies(project: str, namespace: str = None)

# Refactoring support
def suggest_destructuring_patterns(project: str, file_path: str, binding_node: dict)
def find_refactoring_opportunities(project: str, refactor_type: str)
def extract_common_patterns(project: str, similarity_threshold: float = 0.8)

# Advanced queries
def find_clojure_idioms(project: str, idiom_type: str)
def analyze_threading_macros(project: str, file_path: str = None)
def detect_performance_patterns(project: str)
```

### 4. Test Environment Setup

**Use This MCP-nREPL Codebase as Test Target**:

**Rationale**:
- **Rich Clojure Code**: Contains diverse Clojure patterns (core.async, atoms, protocols, etc.)
- **Real-World Complexity**: Non-trivial namespace structure and dependencies
- **Active Development**: Code patterns we're actively working with
- **Validation Ready**: We understand the expected results of queries

**Test Scenarios**:
```bash
# Copy mcp-nrepl-joyride codebase to test directory
cp -r /Users/franksiebenlist/Development/mcp-nrepl-joyride /tmp/clojure-test-project

# Register with enhanced tree-sitter server
mcp-treesitter register-project /tmp/clojure-test-project --language clojure

# Test Clojure-specific queries
mcp-treesitter find-function-definitions clojure-test-project --pattern "tool-*"
mcp-treesitter analyze-namespace-dependencies clojure-test-project --namespace mcp-nrepl-proxy.core
mcp-treesitter find-clojure-idioms clojure-test-project --idiom-type threading-macros
```

## Implementation Plan

### Phase 1: Fork and Basic Clojure Support (Week 1)
1. **Fork mcp-tree-sitter repository**
2. **Add Clojure language support** to base server
3. **Import nvim-treesitter Clojure queries** as templates
4. **Test basic parsing** with mcp-nrepl codebase

**Deliverable**: Enhanced MCP server that can parse Clojure files and run basic tree-sitter queries

### Phase 2: Clojure Query Templates (Week 2)  
1. **Convert nvim-treesitter queries** to MCP query templates
2. **Implement core Clojure-specific functions** (defn finder, namespace analysis)
3. **Add s-expression structural operations**
4. **Test with mcp-nrepl codebase patterns**

**Deliverable**: Rich set of Clojure query templates covering common analysis needs

### Phase 3: Advanced Semantic Analysis (Week 3)
1. **Add macro detection and analysis**
2. **Implement protocol/deftype understanding**  
3. **Build namespace dependency mapping**
4. **Add refactoring pattern detection**

**Deliverable**: Deep semantic analysis capabilities beyond basic syntax parsing

### Phase 4: AI Assistant Integration (Week 4)
1. **Optimize for AI assistant workflows**
2. **Add batch operation support**
3. **Create comprehensive documentation**
4. **Performance optimization and caching**

**Deliverable**: Production-ready Clojure-enhanced tree-sitter MCP server

## Success Criteria

### Functional Requirements
- ✅ Parse and analyze any valid Clojure file
- ✅ Extract function definitions, calls, and signatures
- ✅ Map namespace dependencies accurately  
- ✅ Identify common Clojure idioms (threading, destructuring, etc.)
- ✅ Support complex s-expression navigation
- ✅ Handle macro calls and special forms correctly

### Performance Requirements
- ⚡ Parse large Clojure files (<500ms for 1000 LOC)
- 🔄 Cache parse trees for repeated queries
- 📊 Support concurrent analysis of multiple files
- 💾 Memory efficient for large codebases

### Integration Requirements  
- 🔌 Compatible with existing MCP protocol
- 🤖 Optimized for AI assistant workflows
- 📚 Comprehensive query template library
- 🧪 Validated against real-world Clojure code

## Technical Considerations

### Tree-Sitter Clojure Grammar
- **Repository**: https://github.com/sogaiu/tree-sitter-clojure
- **Completeness**: Mature grammar with good s-expression support
- **Special Forms**: Handles Clojure's unique syntax (reader macros, etc.)

### MCP Protocol Extensions
- **Custom Tool Names**: `clojure_*` prefix for Clojure-specific operations
- **Result Formats**: JSON structures optimized for AI consumption
- **Error Handling**: Clojure-aware error messages and recovery

### Performance Optimizations
- **Incremental Parsing**: Update only changed parts of syntax tree
- **Query Caching**: Cache compiled tree-sitter queries
- **Lazy Loading**: Load query templates on demand

## Getting Started Instructions

### For the Implementation Claude Session

**Context Setup**:
```bash
# 1. Fork the tree-sitter MCP repository
git clone https://github.com/modelcontextprotocol/servers.git mcp-servers-clojure-fork
cd mcp-servers-clojure-fork/src/tree-sitter

# 2. Copy test codebase
cp -r /Users/franksiebenlist/Development/mcp-nrepl-joyride /tmp/clojure-test-project

# 3. Research nvim-treesitter Clojure patterns
curl -L https://raw.githubusercontent.com/nvim-treesitter/nvim-treesitter/master/queries/clojure/highlights.scm > clojure-queries.scm
```

**Key Files to Examine**:
1. `mcp_server.py` - Main MCP server implementation
2. `tree_sitter_mcp/server.py` - Core tree-sitter operations  
3. `/tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj` - Primary test target

**First Implementation Steps**:
1. Add Clojure to `list_languages` function
2. Create `queries/clojure/` directory with query templates  
3. Implement `find_clojure_functions` as proof-of-concept
4. Test against mcp-nrepl codebase

**Success Validation**:
```bash
# Should successfully identify all tool-* functions in mcp-nrepl codebase
python -m mcp_server find-function-definitions clojure-test --pattern "tool-*"

# Should map namespace dependencies correctly
python -m mcp_server analyze-namespace-dependencies clojure-test --namespace mcp-nrepl-proxy.core
```

## 🎯 Key Design Decisions

### Fork vs Clone Decision: **FORK** ✅
**Decision**: Fork wrale/mcp-server-tree-sitter repository
**Repository**: https://github.com/wrale/mcp-server-tree-sitter
**Rationale**:
- **Community Contribution**: Clojure enhancements can be contributed back to wrale/mcp-server-tree-sitter
- **Infrastructure Reuse**: Leverage existing project registration, file operations, caching
- **Protocol Compatibility**: Maintain full MCP protocol compatibility  
- **Maintenance**: Stay synchronized with upstream improvements
- **First-Class Support**: Make Clojure a fully supported language, not an add-on

### Test Environment Decision: **mcp-nrepl Codebase** ✅
**Decision**: Use this mcp-nrepl-joyride codebase as primary test target  
**Rationale**:
- **Rich Clojure Patterns**: Contains diverse real-world Clojure code (core.async, atoms, protocols, macros)
- **Complex Dependencies**: Non-trivial namespace structure we can validate against
- **Known Expected Results**: We understand what queries should return
- **Active Development**: Patterns we're actively working with
- **Validation Ready**: Can immediately test if function finding works correctly

### Architecture Decision: **Enhanced Extension** ✅  
**Decision**: Extend base tree-sitter MCP with Clojure-specific semantic layer
**Rationale**:
- **Base Compatibility**: All existing tree-sitter operations continue working
- **Semantic Enhancement**: Add Clojure-specific understanding (s-expressions, macros, protocols)
- **Performance**: Tree-sitter parsing with semantic post-processing
- **Modularity**: Clojure enhancements can be enabled/disabled

## 🚀 Next Steps for Implementation Session

### Immediate Actions (Session Start)
1. **Fork Repository**:
   ```bash
   # Step 1: Fork on GitHub (via browser)
   # Go to https://github.com/wrale/mcp-server-tree-sitter
   # Click "Fork" button to create YOUR-USERNAME/mcp-server-tree-sitter
   
   # Step 2: Clone your fork locally
   git clone https://github.com/YOUR-USERNAME/mcp-server-tree-sitter.git mcp-clojure-enhanced
   cd mcp-clojure-enhanced
   
   # Step 3: Add upstream remote for future updates
   git remote add upstream https://github.com/wrale/mcp-server-tree-sitter.git
   ```

2. **Validate Test Environment**:
   ```bash
   # Verify test codebase is ready
   ls /tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj
   
   # Count target functions for validation
   grep -n "defn tool-" /tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj
   ```

3. **Import Query Patterns**:
   ```bash
   mkdir -p queries/clojure
   cp /tmp/clojure-query-samples.scm queries/clojure/base-patterns.scm
   ```

### First Week Milestones
- [ ] **Day 1**: Fork setup + basic Clojure language support
- [ ] **Day 2**: Import nvim-treesitter query patterns  
- [ ] **Day 3**: Implement `find_clojure_functions` proof-of-concept
- [ ] **Day 4**: Test against mcp-nrepl codebase validation
- [ ] **Day 5**: Document results and plan Phase 2

### Success Validation Commands  
```bash
# These should work by end of Phase 1:
python -m mcp_server list-languages  # Should include 'clojure'
python -m mcp_server register-project /tmp/clojure-test-project --language clojure
python -m mcp_server find-function-definitions clojure-test --pattern "tool-*"

# Expected: Should find ~15 tool-* functions in mcp-nrepl codebase
```

### Critical Success Factors
- **Immediate Feedback**: Test every change against known codebase
- **Incremental Development**: Each commit should add working functionality
- **Documentation**: Keep detailed notes on what works/doesn't work
- **Community Focus**: Code should be contribution-ready from start

### Handoff Checklist
✅ Requirements document complete (`/tmp/clojure-treesitter-mcp-requirements.md`)  
✅ Test environment prepared (`/tmp/clojure-test-project/`)  
✅ Query samples available (`/tmp/clojure-query-samples.scm`)  
✅ Design decisions documented and justified  
✅ Implementation roadmap with clear milestones  
✅ Success validation criteria defined  

## 🧠 Essential Context for Implementation

### Understanding the Test Codebase (mcp-nrepl-joyride)
**What it does**: This is an MCP (Model Context Protocol) server that provides AI assistants access to Clojure nREPL (networked REPL) connections. It enables Claude and other AI assistants to:
- Execute Clojure code in live environments
- Interact with running Clojure applications 
- Perform code analysis and debugging
- Load files and manage namespaces

**Why it's perfect for testing**:
- **Real Production Code**: Currently used in production by AI assistants
- **Rich Clojure Patterns**: Uses atoms, core.async channels, protocols, macros
- **Complex Dependencies**: Multiple namespaces with interdependencies
- **Diverse Function Types**: Tool functions, utility functions, protocol implementations

### Expected Test Results - Concrete Examples

**Functions to find** (should return **exactly 16** matches for "tool-*" pattern):
```clojure
;; In /tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj
;; NOTE: These are PRIVATE functions (defn-), not public (defn)

(defn- tool-nrepl-connect       ; Line 192
(defn- tool-nrepl-eval          ; Line 209  
(defn- tool-nrepl-status        ; Line 279
(defn- tool-nrepl-new-session   ; Line 301
(defn- tool-nrepl-test          ; Line 433
(defn- tool-nrepl-load-file     ; Line 470
(defn- tool-nrepl-doc           ; Line 518
(defn- tool-nrepl-source        ; Line 545
(defn- tool-nrepl-complete      ; Line 572
(defn- tool-nrepl-apropos       ; Line 601
(defn- tool-nrepl-require       ; Line 635
(defn- tool-nrepl-interrupt     ; Line 665
(defn- tool-nrepl-stacktrace    ; Line 686
(defn- tool-babashka-nrepl      ; Line 710
(defn- tool-get-mcp-nrepl-context ; Line 820
(defn- tool-nrepl-health-check  ; Line 1125
```

**⚠️ Important**: These are **private functions** (`defn-`), so your tree-sitter query must account for both `defn` and `defn-` patterns!

**Namespace structure to analyze**:
```
mcp-nrepl-proxy.core          ; Main MCP tools
  ├── Requires: clojure.core.async, bencode.core, etc.
  ├── Uses: atoms for connection state
  └── Contains: 15+ tool- functions

mcp-nrepl-proxy.server        ; HTTP server (if exists)
mcp-nrepl-proxy.utils         ; Utility functions (if exists)
```

**Complex patterns to detect**:
```clojure
;; Threading macros
(->> responses
     (filter #(= (:id %) message-id))
     (map :value)
     first)

;; Core.async channels
(let [responses-ch (async/chan)]
  (async/go-loop []))

;; Atom state management  
(swap! connection-state assoc :status :connected)

;; Protocol implementations (if any)
(defprotocol NREPLConnection ...)
```

## 🛠️ Development Workflow & Tips

### Recommended Iteration Cycle
```bash
# 1. Make small change
vim tree_sitter_mcp/server.py

# 2. Test immediately against known target
python -m mcp_server register-project /tmp/clojure-test-project
python -m mcp_server find-function-definitions clojure-test --pattern "tool-eval"

# 3. Validate result 
# Should find: tool-nrepl-eval at line ~X in core.clj

# 4. Commit working state
git add . && git commit -m "Add basic Clojure function finding"
```

### Common Tree-Sitter Gotchas
- **S-expression Parsing**: Clojure's nested structure can be tricky
- **Symbol vs Keyword**: `:keyword` vs `symbol` distinction  
- **Reader Macros**: `#{}` sets, `^{}` metadata, `#()` anonymous functions
- **Whitespace Handling**: Significant in some contexts, ignored in others
- **Docstrings**: Optional, can appear in different positions

### Testing Strategy
```python
# Test progression - build confidence incrementally
def test_basic_parsing():
    # Can we parse any Clojure file?
    ast = parse_clojure_file("/tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj")
    assert ast is not None

def test_find_simple_function():
    # Can we find one specific function?
    result = find_function("tool-nrepl-eval")
    assert len(result) == 1
    assert result[0]["name"] == "tool-nrepl-eval"

def test_find_pattern_functions():
    # Can we find all tool-* functions?
    results = find_functions_matching("tool-*") 
    assert len(results) == 16  # Exactly 16 tool-* functions in test codebase
    assert all("tool-" in r["name"] for r in results)
    assert all(r["type"] in ["defn-", "defn"] for r in results)  # Most are private
```

## 📚 Essential Resources & References

### Tree-Sitter Resources
- **Main Documentation**: https://tree-sitter.github.io/tree-sitter/
- **Clojure Grammar**: https://github.com/sogaiu/tree-sitter-clojure
- **Query Syntax**: https://tree-sitter.github.io/tree-sitter/using-parsers#query-syntax
- **Python Bindings**: https://github.com/tree-sitter/py-tree-sitter

### MCP Protocol  
- **Specification**: https://spec.modelcontextprotocol.io/
- **Existing Tree-Sitter Server**: https://github.com/modelcontextprotocol/servers/tree/main/src/tree-sitter
- **Tool Schema**: JSON-RPC format for tool definitions

### Clojure Language References
- **S-expression Structure**: Understanding nested lists, vectors, maps
- **Special Forms**: `let`, `if`, `defn`, `defmacro`, etc.
- **Reader Macros**: `#{}`, `^{}`, `#()`, etc.

## 🔧 Development Environment Setup

### Prerequisites Check
```bash
# Required tools
python --version          # Should be 3.8+
pip install tree-sitter   # Tree-sitter Python bindings  
git --version            # For repository management

# Validate test environment
ls /tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj
# Should exist with ~500 lines of Clojure code

# Count target functions for baseline
grep -c "defn.*tool-" /tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj  
# Should return exactly 16
```

### Initial Repository Structure
```
mcp-clojure-enhanced/
├── src/tree-sitter/
│   ├── mcp_server.py              # Main entry point
│   ├── tree_sitter_mcp/
│   │   ├── server.py              # Core tree-sitter logic
│   │   └── __init__.py
│   ├── queries/
│   │   ├── python/                # Existing language support
│   │   ├── javascript/
│   │   └── clojure/               # ← Add this directory
│   │       ├── base-patterns.scm  # From /tmp/clojure-query-samples.scm
│   │       ├── functions.scm      # Function-specific patterns
│   │       └── namespaces.scm     # Namespace analysis patterns
│   └── README.md
```

## 🎯 Sample Expected Outputs

### Function Finding Result Format
```json
{
  "functions": [
    {
      "name": "tool-nrepl-eval",
      "line": 45,
      "column": 0,
      "file": "/tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj",
      "docstring": "Evaluates Clojure code in nREPL session",
      "parameters": ["request"],
      "namespace": "mcp-nrepl-proxy.core",
      "type": "defn"
    }
  ],
  "total_found": 16,
  "query_time_ms": 23
}
```

### Namespace Analysis Result Format
```json
{
  "namespace": "mcp-nrepl-proxy.core",
  "dependencies": {
    "requires": [
      "clojure.core.async",
      "bencode.core", 
      "clojure.tools.nrepl"
    ],
    "imports": ["java.util.UUID"]
  },
  "exports": [
    "tool-nrepl-eval",
    "tool-nrepl-load-file",
    "create-connection"
  ],
  "line_count": 487
}
```

## 🚨 Common Pitfalls & Solutions

### Tree-Sitter Parsing Issues
```python
# WRONG: Assuming simple string matching
def find_functions_wrong(code):
    return re.findall(r'defn\s+(\w+)', code)  # Misses edge cases

# RIGHT: Use tree-sitter AST
def find_functions_right(tree):
    query = language.query("(list_lit (sym_lit) @fn-name)")
    return query.captures(tree.root_node)
```

### Clojure-Specific Edge Cases
```clojure
;; Multi-arity functions - single function, multiple patterns
(defn tool-example
  ([arg1] ...)
  ([arg1 arg2] ...))

;; Private functions - should be distinguished  
(defn- private-helper [])

;; Functions with metadata
(defn ^:private ^{:doc "Helper"} utility-fn [])

;; ACTUAL patterns you'll encounter in test codebase:
(defn- tool-nrepl-eval
  "Evaluates Clojure code in the connected nREPL session"
  [{:keys [code session timeout] :or {timeout 30000} :as request}]
  ;; Function body with complex logic
  )

;; Complex parameter destructuring (common in MCP functions)
[{:keys [file-path session] :as request}]

;; Error handling patterns you'll see
(try
  (some-nrepl-operation)
  (catch Exception e
    {:error (str "Operation failed: " (.getMessage e))}))
```

### Real Codebase Patterns to Handle
Based on analysis of the test codebase, expect these patterns:
- **All tool-* functions are private (`defn-`)**
- **Complex parameter destructuring**: `{:keys [code session timeout] :or {timeout 30000}}`
- **Docstrings present**: Most functions have descriptive docstrings
- **Error handling**: Try-catch blocks with structured error responses
- **Core.async usage**: `go-loop`, channels, `<!`, `>!`
- **Atom operations**: `swap!`, `reset!`, `@atom-name`
- **Threading macros**: `->>`, `->`, `cond->` commonly used

### Performance Considerations
- **Parse Once**: Cache parsed ASTs for repeated queries
- **Incremental Updates**: Re-parse only changed files
- **Query Compilation**: Pre-compile tree-sitter queries
- **Memory Management**: Clean up unused ASTs

## 🎉 Success Celebration Criteria

### Phase 1 Complete When:
```bash
# All these commands work without errors:
python -m mcp_server list-languages | grep clojure
python -m mcp_server register-project /tmp/clojure-test-project clojure-test
python -m mcp_server find-function-definitions clojure-test --pattern "tool-*" | jq '.functions | length'
# Output: 16 (exactly - all are private defn- functions)
```

### Beyond Phase 1:
- **Namespace mapping** finds all requires/imports correctly
- **Macro detection** identifies threading macros, let bindings
- **Protocol analysis** finds defprotocol/deftype/defrecord
- **Performance** parses 1000-line Clojure files in <100ms

## 📖 Sources & References Used

### Primary Documentation Sources
- **MCP Tree-Sitter Server**: https://github.com/wrale/mcp-server-tree-sitter
  - *Used for*: Understanding existing MCP tree-sitter architecture, tool patterns, project structure
- **MCP Protocol Specification**: https://spec.modelcontextprotocol.io/
  - *Used for*: JSON-RPC tool definitions, protocol compliance requirements
- **Tree-Sitter Documentation**: https://tree-sitter.github.io/tree-sitter/
  - *Used for*: Query syntax, parsing concepts, performance considerations

### Clojure Language Resources
- **Tree-Sitter Clojure Grammar**: https://github.com/sogaiu/tree-sitter-clojure
  - *Used for*: Understanding AST node types, parsing capabilities, grammar completeness
- **nvim-treesitter Clojure Queries**: https://github.com/nvim-treesitter/nvim-treesitter/tree/master/queries/clojure
  - *Used for*: Base query patterns, highlighting rules, structural patterns
  - *Specific file*: `highlights.scm` - extracted function definitions, namespace patterns, macro detection

### Test Codebase Analysis
- **mcp-nrepl-joyride Codebase**: `/Users/franksiebenlist/Development/mcp-nrepl-joyride/`
  - *Used for*: Real-world Clojure patterns, function analysis, complexity assessment
  - *Analysis results*: 16 tool-* functions identified, private function patterns, complex parameter destructuring
  - *Command used*: `grep -n "defn.*tool-" /tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj`

### Implementation Research
- **Python Tree-Sitter Bindings**: https://github.com/tree-sitter/py-tree-sitter
  - *Used for*: Python integration patterns, performance considerations
- **Tree-Sitter Query Documentation**: https://tree-sitter.github.io/tree-sitter/using-parsers#query-syntax
  - *Used for*: Query pattern syntax, capture groups, pattern matching

### Design Decision Sources
- **MCP Server Development Best Practices**: Based on analysis of wrale/mcp-server-tree-sitter repository
- **Clojure Development Patterns**: Based on analysis of real-world Clojure codebases and community conventions
- **AI Assistant Workflow Optimization**: Based on practical experience with Claude Desktop integration and AI code analysis patterns

### Files Created During Analysis
- `/tmp/clojure-test-project/` - Complete copy of mcp-nrepl-joyride codebase for testing
- `/tmp/clojure-query-samples.scm` - Extracted tree-sitter query patterns from nvim-treesitter
- `/tmp/controllable_test_server_guide.md` - Custom test server implementation guide
- `/tmp/validation-commands.sh` - Validation script for implementation verification

### Validation Data
- **Function Count**: 16 tool-* functions confirmed in test codebase
- **Function Types**: All private functions (`defn-`) with complex parameter destructuring
- **Line Numbers**: Specific locations provided for validation (tool-nrepl-eval at line 209)
- **Codebase Size**: ~1125 lines in main core.clj file

---

**🚀 Ready for separate implementation session!**

This project will create a powerful tool for AI-assisted Clojure development, enabling sophisticated code analysis and refactoring capabilities that understand Clojure's unique characteristics.
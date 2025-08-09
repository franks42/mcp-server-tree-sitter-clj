# AI Assistant Tree-sitter MCP Cookbook

## Overview

This cookbook is designed specifically for **AI assistants** (Claude, GPT, etc.) to effectively leverage the enhanced tree-sitter MCP server for semantic code analysis, navigation, and intelligent refactoring. Unlike traditional text-based code analysis, tree-sitter provides **AST-level understanding** that enables sophisticated codebase manipulation and insight.

## 🎯 Key AI Advantages with Tree-sitter

**❌ What Traditional Text Analysis Misses:**
- Function boundaries in complex nested code
- Semantic relationships between symbols
- Structural patterns and code organization
- Cross-file dependency relationships
- Language-specific idioms and best practices

**✅ What Tree-sitter MCP Provides:**
- **AST-level parsing** - True syntactic understanding
- **Symbol extraction** - Functions, classes, variables with precise locations
- **Semantic queries** - Custom pattern matching across codebases
- **Dependency analysis** - Import/require relationship mapping
- **Complexity metrics** - Objective code quality assessment
- **Cross-language consistency** - Same patterns work across 31+ languages

## 🚀 Enhanced Clojure Capabilities

This server provides **advanced Clojure analysis** beyond standard tree-sitter:

- **S-expression Navigation** - Navigate nested forms with cursor awareness
- **Idiomatic Pattern Recognition** - Threading macros, destructuring, functional patterns
- **Call Graph Analysis** - Function dependency mapping with complexity metrics
- **Namespace Analysis** - Transitive dependency analysis with coupling metrics
- **Performance Optimized** - Handle 1000+ LOC files in <500ms with caching

---

## 🔄 Essential First Step

### Context Function - Start Here!
- `mcp__tree_sitter__get_treesitter_context` - **CALL THIS FIRST!** Get complete server overview, capabilities, and documentation links

## 📚 Available MCP Tools

### Core Analysis Tools
- `mcp__tree_sitter__get_symbols` - Extract functions, classes, imports
- `mcp__tree_sitter__get_ast` - Parse and navigate syntax trees
- `mcp__tree_sitter__find_usage` - Find symbol references across files
- `mcp__tree_sitter__analyze_complexity` - Code quality and complexity metrics
- `mcp__tree_sitter__get_dependencies` - Import/require analysis

### Advanced Analysis Tools
- `mcp__tree_sitter__run_query` - Custom AST pattern matching
- `mcp__tree_sitter__find_similar_code` - Code pattern detection
- `mcp__tree_sitter__analyze_project` - Comprehensive codebase analysis
- `mcp__tree_sitter__get_node_at_position` - Precise cursor-based analysis

### Project Management Tools
- `mcp__tree_sitter__register_project_tool` - Register codebases for analysis
- `mcp__tree_sitter__list_projects_tool` - View registered projects
- `mcp__tree_sitter__list_files` - File discovery with pattern matching

---

## 🔄 Progressive AI Workflows

### Phase 0: Essential Context (MANDATORY FIRST STEP)

**Goal:** Get comprehensive server context and guidance

```python
# ALWAYS START HERE - Get complete context and roadmap
context = mcp__tree_sitter__get_treesitter_context()
# Returns: server overview, capabilities, documentation links, quick start workflow
```

### Phase 1: Codebase Discovery and Mapping

**Goal:** Understand the structure and organization of an unfamiliar codebase

```python
# 1. Register the project for analysis
mcp__tree_sitter__register_project_tool(
    path="/path/to/project",
    name="target-project", 
    description="Project under analysis"
)

# 2. Get project overview and structure
project_analysis = mcp__tree_sitter__analyze_project(
    project="target-project",
    scan_depth=3  # Balance detail vs performance
)

# 3. Identify main code files by language
python_files = mcp__tree_sitter__list_files(
    project="target-project",
    pattern="**/*.py",
    max_depth=5
)

clojure_files = mcp__tree_sitter__list_files(
    project="target-project", 
    pattern="**/*.clj",
    max_depth=5
)

# 4. Extract high-level symbols to understand architecture
for file in python_files[:10]:  # Limit initial exploration
    symbols = mcp__tree_sitter__get_symbols(
        project="target-project",
        file_path=file,
        symbol_types=["functions", "classes", "imports"]
    )
    # Analyze symbols to understand module purpose and API
```

**AI Analysis Questions to Answer:**
- What are the main modules and their purposes?
- What's the overall architecture pattern (MVC, microservices, etc.)?
- Which files are central to the application's functionality?
- What are the key external dependencies?

### Phase 2: Focused Module Analysis

**Goal:** Deep-dive into specific modules or components

```python
# 1. Analyze a specific high-value module
core_symbols = mcp__tree_sitter__get_symbols(
    project="target-project",
    file_path="src/core.py",  # or main identified file
    symbol_types=["functions", "classes"]
)

# 2. Understand dependencies and relationships
dependencies = mcp__tree_sitter__get_dependencies(
    project="target-project", 
    file_path="src/core.py"
)

# 3. Analyze code complexity and quality
complexity = mcp__tree_sitter__analyze_complexity(
    project="target-project",
    file_path="src/core.py"
)

# 4. Find how core functions are used throughout codebase
for func in core_symbols['functions'][:5]:  # Focus on top functions
    usage = mcp__tree_sitter__find_usage(
        project="target-project",
        symbol=func['name'],
        language="python"
    )
    # Map usage patterns and coupling
```

**Clojure-Specific Deep Analysis:**
```python
# Enhanced Clojure analysis for idiomatic patterns
idioms = mcp__tree_sitter__find_clojure_idioms(
    project="target-project",
    file_path="src/core.clj"
)

# Analyze s-expression at specific locations
sexp_analysis = mcp__tree_sitter__analyze_sexpression(
    project="target-project",
    file_path="src/core.clj", 
    line=42,
    column=15
)

# Get comprehensive idiomatic scoring
idiom_summary = mcp__tree_sitter__get_idiom_summary(
    project="target-project",
    file_path="src/core.clj"
)
```

### Phase 3: Pattern Recognition and Code Quality Assessment

**Goal:** Identify code patterns, potential issues, and improvement opportunities

```python
# 1. Find similar code patterns for consistency analysis
similar_patterns = mcp__tree_sitter__find_similar_code(
    project="target-project",
    snippet="def process_data(data):\n    return transform(data)",
    language="python",
    threshold=0.7
)

# 2. Custom query for specific patterns
error_handling_query = """
(try_statement
  body: (block) @try.body
  handlers: (except_handler) @except.handler) @try.statement
"""

error_patterns = mcp__tree_sitter__run_query(
    project="target-project",
    query=error_handling_query,
    language="python"
)

# 3. Analyze complexity across multiple files
complexity_report = {}
for file in python_files[:20]:  # Batch analysis
    complexity_report[file] = mcp__tree_sitter__analyze_complexity(
        project="target-project",
        file_path=file
    )

# 4. Dependency analysis for architecture insights
dependency_graph = {}
for file in python_files:
    deps = mcp__tree_sitter__get_dependencies(
        project="target-project",
        file_path=file
    )
    dependency_graph[file] = deps
```

### Phase 4: Intelligent Refactoring Preparation

**Goal:** Prepare for safe, informed code modifications

```python
# 1. Before refactoring a function, understand its complete impact
target_function = "process_user_data"

# Find all usages
usages = mcp__tree_sitter__find_usage(
    project="target-project", 
    symbol=target_function,
    language="python"
)

# Understand the function's context
func_node = mcp__tree_sitter__get_node_at_position(
    project="target-project",
    path="src/users.py",
    row=function_line,  # From symbol extraction
    column=0
)

# Get AST context for precise modification
ast_context = mcp__tree_sitter__get_ast(
    project="target-project",
    path="src/users.py", 
    max_depth=3,
    include_text=True
)

# 2. For Clojure refactoring - analyze function call chains
call_graph = mcp__tree_sitter__trace_function_calls(
    project="target-project",
    file_path="src/core.clj",
    target_function="process-data"
)

# 3. Identify potential breaking changes
for usage in usages:
    # Analyze each usage context to understand modification impact
    usage_context = mcp__tree_sitter__get_node_at_position(
        project="target-project",
        path=usage['file'],
        row=usage['line'],
        column=usage['column']
    )
```

---

## 💼 Practical AI Use Cases

### Use Case 1: Understanding Legacy Codebase

**Scenario:** AI needs to understand and document an undocumented Python project

```python
# Step 1: Quick architecture overview
project_structure = mcp__tree_sitter__analyze_project(
    project="legacy-app",
    scan_depth=2
)

# Step 2: Identify entry points and main flows  
main_files = mcp__tree_sitter__list_files(
    project="legacy-app",
    pattern="**/main.py"  # or app.py, server.py, etc.
)

for main_file in main_files:
    entry_points = mcp__tree_sitter__get_symbols(
        project="legacy-app",
        file_path=main_file,
        symbol_types=["functions"]
    )
    
    # Analyze each entry point
    for func in entry_points['functions']:
        if func['name'] in ['main', 'run', 'start', 'app']:
            # This is likely an entry point
            func_usage = mcp__tree_sitter__find_usage(
                project="legacy-app",
                symbol=func['name'],
                language="python"
            )

# Step 3: Map the data flow
data_models = mcp__tree_sitter__list_files(
    project="legacy-app",
    pattern="**/models.py"
)

for model_file in data_models:
    models = mcp__tree_sitter__get_symbols(
        project="legacy-app",
        file_path=model_file,
        symbol_types=["classes"]
    )
    
    # Understand model relationships
    for model in models['classes']:
        model_usage = mcp__tree_sitter__find_usage(
            project="legacy-app", 
            symbol=model['name'],
            language="python"
        )

# Step 4: Generate comprehensive documentation
# AI can now create accurate architectural diagrams, API documentation,
# and data flow descriptions based on actual code structure
```

### Use Case 2: Safe Refactoring Planning

**Scenario:** AI needs to refactor a complex function without breaking dependencies

```python
# Step 1: Complete impact analysis
target_function = "calculate_user_metrics"
target_file = "src/analytics.py"

# Find all direct usages
direct_usage = mcp__tree_sitter__find_usage(
    project="analytics-app",
    symbol=target_function,
    language="python"
)

# Get function's full context and dependencies
function_deps = mcp__tree_sitter__get_dependencies(
    project="analytics-app",
    file_path=target_file
)

# Analyze function complexity to understand refactoring scope
complexity = mcp__tree_sitter__analyze_complexity(
    project="analytics-app", 
    file_path=target_file
)

# Step 2: Find similar functions for consistency
similar_functions = mcp__tree_sitter__find_similar_code(
    project="analytics-app",
    snippet="def calculate_",  # Pattern for similar calculation functions
    language="python",
    threshold=0.6
)

# Step 3: Custom query to find specific patterns that might be affected
metrics_query = """
(call
  function: (attribute 
    object: (identifier) @obj
    attribute: (identifier) @method)
  arguments: (argument_list) @args
  (#match? @method "calculate.*"))
"""

calculation_patterns = mcp__tree_sitter__run_query(
    project="analytics-app",
    query=metrics_query,
    language="python"
)

# Step 4: AI can now plan the refactoring with full knowledge of:
# - All places the function is called
# - Similar functions that should maintain consistency  
# - Complexity metrics to guide the refactoring approach
# - Dependencies that must be preserved
```

### Use Case 3: Code Quality and Architecture Analysis

**Scenario:** AI provides comprehensive code review and architectural recommendations

```python
# Step 1: Project-wide complexity analysis
files = mcp__tree_sitter__list_files(
    project="review-target",
    pattern="**/*.py"
)

complexity_report = {}
high_complexity_files = []

for file in files:
    complexity = mcp__tree_sitter__analyze_complexity(
        project="review-target",
        file_path=file
    )
    
    complexity_report[file] = complexity
    
    # Identify files that need attention
    if complexity.get('cyclomatic_complexity', 0) > 10:
        high_complexity_files.append({
            'file': file,
            'complexity': complexity
        })

# Step 2: Dependency analysis for architecture insights
dependency_graph = {}
circular_deps = []

for file in files:
    deps = mcp__tree_sitter__get_dependencies(
        project="review-target", 
        file_path=file
    )
    dependency_graph[file] = deps
    
    # Check for potential circular dependencies
    for dep in deps.get('imports', []):
        reverse_deps = mcp__tree_sitter__get_dependencies(
            project="review-target",
            file_path=dep
        )
        if file in [r.get('module') for r in reverse_deps.get('imports', [])]:
            circular_deps.append((file, dep))

# Step 3: Pattern consistency analysis
common_patterns = [
    "def __init__(self",
    "def process_",
    "def validate_", 
    "def serialize_"
]

pattern_analysis = {}
for pattern in common_patterns:
    similar_code = mcp__tree_sitter__find_similar_code(
        project="review-target",
        snippet=pattern,
        language="python",
        threshold=0.8
    )
    pattern_analysis[pattern] = similar_code

# Step 4: Generate comprehensive recommendations
# AI can now provide detailed analysis including:
# - Specific files that need refactoring (high complexity)
# - Architecture issues (circular dependencies)
# - Code consistency opportunities (pattern analysis)
# - Concrete suggestions with file and line references
```

### Use Case 4: Clojure-Specific Analysis and Optimization

**Scenario:** AI analyzes and optimizes a Clojure codebase for idiomatic patterns

```python
# Step 1: Comprehensive Clojure idiom analysis
clj_files = mcp__tree_sitter__list_files(
    project="clj-project",
    pattern="**/*.clj"
)

idiomatic_analysis = {}
for file in clj_files:
    # Get overall idiomatic scoring
    idiom_summary = mcp__tree_sitter__get_idiom_summary(
        project="clj-project",
        file_path=file
    )
    
    # Find specific patterns
    idioms = mcp__tree_sitter__find_clojure_idioms(
        project="clj-project", 
        file_path=file
    )
    
    idiomatic_analysis[file] = {
        'summary': idiom_summary,
        'patterns': idioms
    }

# Step 2: Namespace dependency analysis
ns_dependencies = {}
for file in clj_files:
    ns_deps = mcp__tree_sitter__analyze_namespace_dependencies(
        project="clj-project",
        file_path=file
    )
    ns_dependencies[file] = ns_deps

# Step 3: Function call graph analysis for optimization
core_functions = mcp__tree_sitter__get_symbols(
    project="clj-project",
    file_path="src/core.clj",
    symbol_types=["functions"]  
)

call_graphs = {}
for func in core_functions['functions'][:10]:  # Focus on key functions
    call_graph = mcp__tree_sitter__trace_function_calls(
        project="clj-project",
        file_path="src/core.clj",
        target_function=func['name']
    )
    call_graphs[func['name']] = call_graph

# Step 4: Advanced s-expression analysis for refactoring
# For specific complex expressions, analyze structure
complex_forms = mcp__tree_sitter__run_query(
    project="clj-project",
    query="(list (symbol) @fn (list) @nested) @complex_form",
    language="clojure"
)

for form in complex_forms:
    sexp_analysis = mcp__tree_sitter__analyze_sexpression(
        project="clj-project",
        file_path=form['file'],
        line=form['line'],
        column=form['column']
    )

# AI can now provide Clojure-specific recommendations:
# - Idiomatic improvements (threading macro opportunities)
# - Namespace organization suggestions
# - Performance optimization opportunities (function call patterns)
# - Code clarity improvements (complex s-expression simplification)
```

---

## 🎯 Best Practices for AI Assistants

### 1. Progressive Analysis Strategy

**Always start broad, then narrow focus:**
```python
# ✅ Good: Progressive approach
project_overview = mcp__tree_sitter__analyze_project(...)
key_files = identify_important_files(project_overview)
detailed_analysis = analyze_specific_files(key_files)

# ❌ Avoid: Analyzing every file immediately
for file in all_files:  # Don't do this first
    detailed_analysis = mcp__tree_sitter__get_symbols(...)
```

### 2. Context-Aware Analysis

**Use cursor position and AST context for precise understanding:**
```python
# ✅ Good: Get specific node context
node_info = mcp__tree_sitter__get_node_at_position(
    project="proj", path="file.py", row=42, column=15
)

ast_context = mcp__tree_sitter__get_ast(
    project="proj", path="file.py", 
    max_depth=2,  # Limit depth for performance
    include_text=True
)

# ❌ Avoid: Analyzing entire files for specific questions
entire_file_ast = mcp__tree_sitter__get_ast(
    project="proj", path="file.py", 
    max_depth=10  # Too deep, too slow
)
```

### 3. Batch Operations for Efficiency

**Group similar operations to minimize tool calls:**
```python
# ✅ Good: Batch similar analysis
files_to_analyze = ["core.py", "utils.py", "models.py"]
complexity_results = {}

for file in files_to_analyze:
    complexity_results[file] = mcp__tree_sitter__analyze_complexity(
        project="proj", file_path=file
    )

# ✅ Better: Design analysis workflow to minimize redundant calls
analysis_plan = design_efficient_analysis(target_questions)
execute_batch_analysis(analysis_plan)
```

### 4. Language-Specific Optimization

**Leverage enhanced capabilities for supported languages:**
```python
# For Clojure - use enhanced analysis
if language == "clojure":
    idiom_analysis = mcp__tree_sitter__find_clojure_idioms(...)
    sexp_analysis = mcp__tree_sitter__analyze_sexpression(...)
    call_graph = mcp__tree_sitter__trace_function_calls(...)

# For other languages - use standard analysis
else:
    symbols = mcp__tree_sitter__get_symbols(...)
    complexity = mcp__tree_sitter__analyze_complexity(...)
    usage = mcp__tree_sitter__find_usage(...)
```

### 5. Error Handling and Graceful Degradation

**Handle tool failures gracefully:**
```python
try:
    detailed_analysis = mcp__tree_sitter__analyze_complexity(
        project="proj", file_path="complex_file.py"
    )
except Exception as e:
    # Fallback to simpler analysis
    basic_symbols = mcp__tree_sitter__get_symbols(
        project="proj", file_path="complex_file.py",
        symbol_types=["functions"]
    )
    # Work with what you have
```

---

## 🔍 Query Patterns and Custom Analysis

### Common AST Query Patterns

**Python Function Analysis:**
```python
# Find all async functions
async_query = """
(async_function_definition 
  name: (identifier) @function.name
  parameters: (parameters) @function.params
  body: (block) @function.body) @async_function
"""

# Find error handling patterns
error_query = """
(try_statement
  body: (block) @try.body
  handlers: (except_handler
    type: (identifier) @exception.type
    name: (identifier)? @exception.name
    body: (block) @exception.handler)) @error_handling
"""

# Find class inheritance patterns
class_query = """
(class_definition
  name: (identifier) @class.name
  superclasses: (argument_list
    (identifier) @superclass)*
  body: (block) @class.body) @class_definition
"""
```

**Clojure S-expression Patterns:**
```python
# Find threading macro usage
threading_query = """
(list
  (symbol) @macro (#match? @macro "->|->>");
  (_) @first_arg
  (_)* @rest_args) @threading_macro
"""

# Find function definitions with docstrings
fn_with_doc_query = """
(list
  (symbol) @fn_type (#match? @fn_type "defn|defn-")
  (symbol) @fn_name
  (string)? @docstring
  (vector) @params
  (_)* @body) @function_def
"""

# Find destructuring patterns
destructuring_query = """
(vector
  (map
    (keyword) @destructure_key
    (symbol) @destructure_symbol)) @destructuring_pattern
"""
```

### Advanced Analysis Workflows

**Cross-File Dependency Mapping:**
```python
def build_dependency_graph(project_name, file_list):
    graph = {}
    
    for file in file_list:
        # Get direct dependencies
        deps = mcp__tree_sitter__get_dependencies(
            project=project_name,
            file_path=file
        )
        
        # Find usage of this file's exports in other files
        symbols = mcp__tree_sitter__get_symbols(
            project=project_name,
            file_path=file, 
            symbol_types=["functions", "classes"]
        )
        
        dependents = []
        for symbol in symbols.get('functions', []) + symbols.get('classes', []):
            usage = mcp__tree_sitter__find_usage(
                project=project_name,
                symbol=symbol['name'],
                language="python"
            )
            dependents.extend([u['file'] for u in usage if u['file'] != file])
        
        graph[file] = {
            'dependencies': deps,
            'dependents': list(set(dependents))
        }
    
    return graph
```

**Code Quality Scoring:**
```python
def calculate_code_quality_score(project_name, file_path):
    # Get complexity metrics
    complexity = mcp__tree_sitter__analyze_complexity(
        project=project_name,
        file_path=file_path
    )
    
    # Get symbol information for structure analysis
    symbols = mcp__tree_sitter__get_symbols(
        project=project_name,
        file_path=file_path,
        symbol_types=["functions", "classes"]
    )
    
    # Calculate scoring factors
    complexity_score = min(100, 100 - (complexity.get('cyclomatic_complexity', 0) * 5))
    
    # Function size analysis
    avg_function_length = complexity.get('lines_of_code', 0) / max(len(symbols.get('functions', [])), 1)
    size_score = max(0, 100 - (avg_function_length - 20) * 2)
    
    # Dependency coupling score
    deps = mcp__tree_sitter__get_dependencies(project=project_name, file_path=file_path)
    coupling_score = max(0, 100 - len(deps.get('imports', [])) * 3)
    
    # Combined score
    overall_score = (complexity_score + size_score + coupling_score) / 3
    
    return {
        'overall_score': round(overall_score, 1),
        'complexity_score': complexity_score,
        'size_score': size_score,
        'coupling_score': coupling_score,
        'metrics': complexity
    }
```

---

## 🚀 Advanced AI Capabilities

### Intelligent Code Refactoring Assistant

AI can use tree-sitter analysis to become a sophisticated refactoring assistant:

```python
def suggest_refactoring_opportunities(project_name):
    opportunities = []
    
    # Find files with high complexity
    files = mcp__tree_sitter__list_files(project=project_name, pattern="**/*.py")
    
    for file in files:
        complexity = mcp__tree_sitter__analyze_complexity(
            project=project_name, file_path=file
        )
        
        if complexity.get('cyclomatic_complexity', 0) > 10:
            # Find specific complex functions
            symbols = mcp__tree_sitter__get_symbols(
                project=project_name, file_path=file,
                symbol_types=["functions"]
            )
            
            # Analyze each function for refactoring potential
            for func in symbols['functions']:
                # Find similar code that could be extracted
                similar = mcp__tree_sitter__find_similar_code(
                    project=project_name,
                    snippet=f"def {func['name']}",
                    language="python"
                )
                
                opportunities.append({
                    'type': 'complexity_reduction',
                    'file': file,
                    'function': func['name'],
                    'complexity': complexity,
                    'similar_patterns': similar,
                    'suggestion': f"Consider breaking down {func['name']} - complexity: {complexity.get('cyclomatic_complexity', 0)}"
                })
    
    return opportunities
```

### Architectural Pattern Detection

```python
def detect_architectural_patterns(project_name):
    patterns = {
        'mvc': {'models': [], 'views': [], 'controllers': []},
        'repository': [],
        'factory': [],
        'observer': [],
        'singleton': []
    }
    
    files = mcp__tree_sitter__list_files(project=project_name, pattern="**/*.py")
    
    for file in files:
        symbols = mcp__tree_sitter__get_symbols(
            project=project_name, file_path=file,
            symbol_types=["classes", "functions"]
        )
        
        # Detect MVC pattern
        if 'model' in file.lower():
            patterns['mvc']['models'].extend(symbols.get('classes', []))
        elif 'view' in file.lower():
            patterns['mvc']['views'].extend(symbols.get('classes', []))
        elif 'controller' in file.lower():
            patterns['mvc']['controllers'].extend(symbols.get('classes', []))
        
        # Detect other patterns through naming and structure
        for cls in symbols.get('classes', []):
            if cls['name'].endswith('Repository'):
                patterns['repository'].append({'file': file, 'class': cls})
            elif cls['name'].endswith('Factory'):
                patterns['factory'].append({'file': file, 'class': cls})
            elif 'Singleton' in cls['name'] or '_instance' in str(cls):
                patterns['singleton'].append({'file': file, 'class': cls})
    
    return patterns
```

---

## 🎯 Integration with Development Workflows

### Pre-commit Analysis

AI can perform pre-commit quality checks:

```python
def pre_commit_analysis(project_name, changed_files):
    issues = []
    
    for file in changed_files:
        if file.endswith(('.py', '.clj')):
            # Quality check
            complexity = mcp__tree_sitter__analyze_complexity(
                project=project_name, file_path=file
            )
            
            if complexity.get('cyclomatic_complexity', 0) > 15:
                issues.append({
                    'file': file,
                    'type': 'high_complexity', 
                    'severity': 'warning',
                    'message': f"High complexity: {complexity.get('cyclomatic_complexity')}"
                })
            
            # Find potential issues
            symbols = mcp__tree_sitter__get_symbols(
                project=project_name, file_path=file,
                symbol_types=["functions"]
            )
            
            for func in symbols.get('functions', []):
                if len(func['name']) < 3:
                    issues.append({
                        'file': file,
                        'type': 'naming',
                        'severity': 'info',
                        'line': func.get('line'),
                        'message': f"Function name '{func['name']}' is very short"
                    })
    
    return issues
```

### Documentation Generation

AI can generate comprehensive documentation based on code structure:

```python
def generate_api_documentation(project_name, module_path):
    symbols = mcp__tree_sitter__get_symbols(
        project=project_name,
        file_path=module_path,
        symbol_types=["functions", "classes"]
    )
    
    dependencies = mcp__tree_sitter__get_dependencies(
        project=project_name,
        file_path=module_path
    )
    
    documentation = {
        'module': module_path,
        'dependencies': dependencies,
        'functions': [],
        'classes': []
    }
    
    # Document each function with usage analysis
    for func in symbols.get('functions', []):
        usage = mcp__tree_sitter__find_usage(
            project=project_name,
            symbol=func['name'],
            language="python"
        )
        
        documentation['functions'].append({
            'name': func['name'],
            'location': f"{module_path}:{func.get('line', 0)}",
            'usage_count': len(usage),
            'used_by': [u['file'] for u in usage],
            'complexity': 'needs_analysis'  # Could add complexity per function
        })
    
    return documentation
```

---

This cookbook empowers AI assistants to perform sophisticated code analysis and provide intelligent development assistance using the enhanced tree-sitter MCP server. The key is to combine multiple analysis tools strategically to build comprehensive understanding of codebases.
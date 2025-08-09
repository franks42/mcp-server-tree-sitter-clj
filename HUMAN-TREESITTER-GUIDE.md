# Human Developer Tree-sitter MCP Guide

## Overview

This guide shows **human developers** how to effectively leverage AI assistants that have access to the enhanced tree-sitter MCP server. Instead of manually analyzing code or struggling with complex refactoring, you can ask AI assistants to perform sophisticated semantic analysis and provide detailed insights about your codebase.

## 🎯 Why Tree-sitter MCP is Game-Changing

**❌ Traditional Manual Code Analysis:**
- Grep/find for basic text search (misses context)
- Manual code reading for understanding structure
- Guesswork about dependencies and relationships
- Time-consuming complexity assessment
- Error-prone refactoring planning

**✅ AI with Tree-sitter MCP:**
- **AST-level understanding** - True semantic analysis
- **Automated code mapping** - Complete codebase structure analysis
- **Intelligent refactoring** - Safe modification planning with impact analysis
- **Pattern recognition** - Consistent code style and architecture insights
- **Cross-language analysis** - Same powerful analysis across 31+ languages

## 🚀 Enhanced Capabilities

This tree-sitter server provides **advanced analysis** especially for:
- **Python** - Full symbol extraction, complexity analysis, dependency mapping
- **JavaScript/TypeScript** - React patterns, module analysis, call graphs  
- **Go, Rust, Java** - Interface analysis, package dependencies, performance insights
- **Clojure** - S-expression navigation, idiomatic patterns, namespace analysis

---

## 📋 What to Ask AI Assistants

### 🗺️ Codebase Discovery and Architecture

**When you need to understand a new or complex codebase:**

**Ask AI:** *"Analyze the structure and architecture of this project using tree-sitter. What are the main components and how do they relate?"*

**What AI will do:**
```python
# AI first gets server context (new essential step!)
context = mcp__tree_sitter__get_treesitter_context()

# AI registers your project and analyzes structure
project_analysis = mcp__tree_sitter__analyze_project(
    project="your-project", scan_depth=3
)

# Maps file organization and identifies key modules
key_files = mcp__tree_sitter__list_files(
    project="your-project", pattern="**/*.py"
)

# Analyzes symbols in important files
symbols = mcp__tree_sitter__get_symbols(
    project="your-project", file_path="src/main.py",
    symbol_types=["functions", "classes", "imports"]
)
```

**You'll get:**
- High-level architecture overview
- Key modules and their purposes  
- Main entry points and data flows
- External dependencies and their usage
- Suggestions for where to start reading code

### 🔍 Deep Code Analysis

**When you need to understand specific modules or complex functions:**

**Ask AI:** *"Give me a detailed analysis of the `user_service.py` module. What does it do, how complex is it, and what depends on it?"*

**What AI will do:**
```python
# Analyzes specific module in detail
symbols = mcp__tree_sitter__get_symbols(
    project="your-project", file_path="src/user_service.py"
)

complexity = mcp__tree_sitter__analyze_complexity(
    project="your-project", file_path="src/user_service.py"  
)

dependencies = mcp__tree_sitter__get_dependencies(
    project="your-project", file_path="src/user_service.py"
)

# Finds usage across codebase
usage = mcp__tree_sitter__find_usage(
    project="your-project", symbol="UserService", language="python"
)
```

**You'll get:**
- Function-by-function breakdown
- Complexity metrics and quality assessment
- Dependencies (what it imports/uses)
- Dependents (what uses this module)
- Potential improvement opportunities

### 🛠️ Refactoring Planning

**When you want to modify code safely:**

**Ask AI:** *"I want to refactor the `process_data` function. Show me everywhere it's used and help me plan the changes safely."*

**What AI will do:**
```python
# Comprehensive impact analysis
usage_analysis = mcp__tree_sitter__find_usage(
    project="your-project", symbol="process_data", language="python"
)

# Gets function context
function_context = mcp__tree_sitter__get_node_at_position(
    project="your-project", path="src/data.py", row=42, column=0
)

# Finds similar functions for consistency
similar_functions = mcp__tree_sitter__find_similar_code(
    project="your-project", snippet="def process_", language="python"
)

# Analyzes complexity
complexity = mcp__tree_sitter__analyze_complexity(
    project="your-project", file_path="src/data.py"
)
```

**You'll get:**
- Complete list of where function is called
- Context of each usage (how it's being called)
- Similar functions that should remain consistent
- Complexity analysis to guide refactoring approach
- Step-by-step refactoring plan with risk assessment

### 🕵️ Code Quality Assessment

**When you want to improve code quality:**

**Ask AI:** *"Analyze the code quality of this project. What files need attention and what are the main issues?"*

**What AI will do:**
```python
# Project-wide complexity analysis
files = mcp__tree_sitter__list_files(project="your-project", pattern="**/*.py")

complexity_report = {}
for file in files:
    complexity_report[file] = mcp__tree_sitter__analyze_complexity(
        project="your-project", file_path=file
    )

# Dependency analysis for architecture issues
dependency_graph = {}
for file in files:
    dependency_graph[file] = mcp__tree_sitter__get_dependencies(
        project="your-project", file_path=file
    )

# Pattern consistency analysis
similar_patterns = mcp__tree_sitter__find_similar_code(
    project="your-project", snippet="common_pattern", language="python"
)
```

**You'll get:**
- Files ranked by complexity (highest attention needed first)
- Architecture issues (circular dependencies, high coupling)
- Code consistency opportunities
- Specific improvement recommendations with file/line references
- Prioritized action plan

### 🔗 Dependency Analysis

**When you need to understand system dependencies:**

**Ask AI:** *"Map out the dependencies in this project. What imports what and are there any circular dependencies or architecture issues?"*

**What AI will do:**
```python
# Builds complete dependency graph
dependency_graph = {}
for file in all_files:
    deps = mcp__tree_sitter__get_dependencies(
        project="your-project", file_path=file
    )
    dependency_graph[file] = deps

# Analyzes for circular dependencies and coupling
circular_deps = detect_circular_dependencies(dependency_graph)
high_coupling = detect_high_coupling(dependency_graph)
```

**You'll get:**
- Visual dependency map
- Circular dependency detection
- High coupling warnings
- Suggestions for decoupling
- Architecture improvement recommendations

---

## 🎯 Language-Specific Requests

### 🐍 Python Projects

**Django Application Analysis:**
*"Analyze this Django project. Show me the models, views, and their relationships. What's the data flow?"*

**FastAPI/Flask Analysis:** 
*"Map out the API endpoints in this project. What routes exist and what functions handle them?"*

**Data Science Project:**
*"Analyze this ML project. What are the main processing pipelines and where is the model training logic?"*

### ☕ Java/Kotlin Projects

**Spring Boot Analysis:**
*"Analyze this Spring Boot project. What are the main controllers, services, and repositories? How are they connected?"*

**Architecture Review:**
*"Review the package structure of this Java project. Are we following good architectural patterns?"*

### 🦀 Rust Projects

**Crate Analysis:**
*"Analyze the module structure of this Rust project. What are the main public APIs and internal dependencies?"*

**Performance Review:**
*"Look for potential performance issues in this Rust code. Are there any obvious bottlenecks or inefficiencies?"*

### 🌐 JavaScript/TypeScript Projects

**React Application:**
*"Analyze this React project. What are the main components and how do they share state?"*

**Node.js API:**
*"Map out the routes and middleware in this Express.js application."*

### 🔧 Clojure Projects (Enhanced Analysis)

**Namespace Analysis:**
*"Analyze the namespace structure of this Clojure project. What are the dependencies and coupling between namespaces?"*

**Idiomatic Review:**
*"Review this Clojure code for idiomatic patterns. Are we using threading macros, destructuring, and functional patterns effectively?"*

**Performance Analysis:**
*"Analyze the function call patterns in this Clojure code. Are there any performance bottlenecks or optimization opportunities?"*

---

## 💬 Sample Conversations with AI

### Conversation 1: Understanding Legacy Code

**You:** "I inherited this Python project and I'm completely lost. Can you help me understand what it does?"

**AI Response:** "I'll analyze the project structure for you. Let me start with a high-level overview..."

*[AI performs project analysis using tree-sitter tools]*

**AI:** "This appears to be a data processing pipeline with 3 main components:

1. **Data Ingestion** (`src/ingestion/`) - 5 modules handling different data sources
2. **Processing Core** (`src/processors/`) - Main business logic in 12 modules
3. **Output Handlers** (`src/outputs/`) - 4 different output formats

The main entry point is `main.py` which orchestrates the pipeline. The most complex module is `processors/data_transformer.py` (complexity score: 15.2 - needs attention).

Key dependencies: pandas, sqlalchemy, redis
Main data flow: Raw data → Validation → Transformation → Enrichment → Output

Would you like me to dive deeper into any specific component?"

### Conversation 2: Refactoring Planning

**You:** "The `calculate_metrics` function in analytics.py is getting too complex. I want to break it down but I'm worried about breaking things."

**AI Response:** "Let me analyze the impact of refactoring `calculate_metrics`..."

*[AI performs comprehensive impact analysis]*

**AI:** "I found `calculate_metrics` is used in 8 locations across 5 files. Here's the breakdown:

**High Risk Changes:**
- `reports/monthly.py:45` - Passes complex parameters, signature change would break this
- `api/endpoints.py:123` - Called from external API, needs backward compatibility

**Low Risk Changes:**
- `tests/test_analytics.py` - 4 test cases, easy to update

**Refactoring Strategy:**
1. **Phase 1**: Extract helper functions (no breaking changes)
   - `_calculate_averages()` - lines 15-30
   - `_apply_filters()` - lines 35-50
   
2. **Phase 2**: Create new interface, deprecate old
   - Keep original function for backward compatibility
   - Add warning about deprecation
   
3. **Phase 3**: Update all callers and remove old function

**Complexity Reduction**: Current complexity 18.5 → Expected 6.2 after refactoring

Would you like me to show you the specific code patterns to extract?"

### Conversation 3: Architecture Review

**You:** "Can you review the architecture of this microservice? I'm concerned about the dependencies and coupling."

**AI Response:** "I'll analyze the architecture and dependency patterns..."

*[AI performs comprehensive architecture analysis]*

**AI:** "**Architecture Analysis Results:**

**🟢 Good Patterns:**
- Clear separation between handlers, services, and repositories
- Proper dependency injection in most modules
- Consistent error handling patterns

**🟡 Concerns:**
- **Circular Dependencies**: Found 3 circular import chains:
  - `models.py` ↔ `validators.py` ↔ `utils.py`
  - `auth/service.py` ↔ `user/service.py`
  
- **High Coupling**: `core/business_logic.py` imports from 12 different modules

**🔴 Issues:**
- Database models imported directly in API handlers (should go through services)
- Configuration scattered across 8 different files

**Recommended Actions:**
1. **Break circular dependencies** by extracting interfaces
2. **Reduce coupling** in business_logic.py - split into 3 focused modules
3. **Centralize configuration** - create single config module

**Priority**: Address circular dependencies first (deployment risk), then tackle coupling.

Would you like me to show specific refactoring steps for any of these issues?"

---

## 🎯 Specific Task Examples

### Task 1: Code Review Preparation

**Request:** *"I'm doing a code review for a pull request that changes the authentication system. Help me understand what's being changed and what I should look for."*

**AI Actions:**
- Analyze changed files with complexity metrics
- Find all usages of authentication functions
- Identify potential security implications
- Check for consistent error handling patterns
- Map dependency changes

**Your Benefit:** Thorough review checklist with specific concerns highlighted

### Task 2: Performance Investigation

**Request:** *"The application is running slowly. Can you analyze the codebase and identify potential performance bottlenecks?"*

**AI Actions:**
- Find complex functions (high cyclomatic complexity)
- Identify nested loops and recursive patterns  
- Analyze database query patterns
- Look for synchronous operations that could be async
- Map hot code paths through call graph analysis

**Your Benefit:** Prioritized list of performance improvement opportunities

### Task 3: Documentation Generation

**Request:** *"Generate documentation for the public API of this module."*

**AI Actions:**
- Extract all public functions and classes
- Analyze function signatures and parameters
- Find usage examples from test files
- Map dependencies and return types
- Generate comprehensive API documentation

**Your Benefit:** Complete, accurate API documentation based on actual code

### Task 4: Migration Planning

**Request:** *"We want to upgrade from Python 3.8 to 3.11. What code might be affected and what should we test?"*

**AI Actions:**
- Find deprecated function usage patterns
- Identify syntax that might need updating
- Analyze library dependencies for compatibility
- Find areas using version-specific features
- Generate testing checklist

**Your Benefit:** Detailed migration plan with risk assessment

---

## 💡 Pro Tips for Working with AI

### 1. Be Specific About Your Goals

**❌ Vague:** "Analyze this code"
**✅ Better:** "Analyze this user authentication module to understand its security patterns and find potential vulnerabilities"
**✅ Best:** "I'm reviewing the authentication module for a security audit. Show me all places where user input is processed, how passwords are handled, and any potential injection points."

### 2. Ask for Prioritized Results

**❌ Generic:** "What needs to be fixed?"
**✅ Better:** "What are the top 5 issues that need immediate attention, ranked by risk and impact?"

### 3. Request Actionable Recommendations

**❌ Abstract:** "This code is complex"
**✅ Better:** "This code is complex - show me specific refactoring steps to reduce complexity while maintaining functionality"

### 4. Leverage Cross-File Analysis

**❌ Limited:** "Review this function"
**✅ Better:** "Review this function and show me how it's used throughout the codebase. Are there any inconsistent usage patterns?"

### 5. Ask for Learning Opportunities

**❌ Just fixing:** "Fix these issues"
**✅ Better:** "Fix these issues and explain the underlying patterns so I can avoid similar problems in the future"

---

## 🚀 Advanced Requests

### Multi-Language Project Analysis

**Request:** *"This project has Python backend and TypeScript frontend. Analyze both and show me how they interact."*

**AI Benefit:** Cross-language analysis showing API contracts, data flow, and integration points

### Architectural Evolution Planning  

**Request:** *"We want to break this monolith into microservices. Analyze the current coupling and suggest natural service boundaries."*

**AI Benefit:** Data-driven microservice boundaries based on actual code dependencies and complexity

### Code Style Consistency

**Request:** *"Ensure our codebase follows consistent patterns. Find places where we deviate from our established patterns."*

**AI Benefit:** Automated style consistency analysis with specific examples and fixes

### Technical Debt Assessment

**Request:** *"Give me a technical debt report. What are our biggest maintenance burdens and how should we prioritize fixing them?"*

**AI Benefit:** Quantified technical debt with ROI analysis for fixes

---

## 🎯 Getting Started Checklist

### Before Your First AI Analysis Session:

1. **✅ Ensure AI has tree-sitter MCP access**
   - Verify AI can call `mcp__tree_sitter__get_treesitter_context()`
   - This function provides complete server overview and guidance

2. **✅ Prepare your project**
   - Clean up any obvious junk files
   - Ensure code is in a consistent state
   - Have specific questions ready

3. **✅ Define your goals**
   - What specific insights do you need?
   - What decisions are you trying to make?
   - What are your main concerns or pain points?

### During Analysis Sessions:

1. **🎯 Start broad, then narrow**
   - Begin with project overview
   - Drill down into specific areas of concern
   - Ask follow-up questions for clarification

2. **📋 Take notes**
   - AI insights are valuable - document key findings
   - Create action items from recommendations
   - Track progress on suggested improvements

3. **🔄 Iterate**
   - Ask for clarification on complex points
   - Request alternative approaches
   - Challenge assumptions with "what if" scenarios

---

This guide transforms how you work with code by leveraging AI assistants that have deep semantic understanding through tree-sitter analysis. Instead of manual code archaeology, you get intelligent insights that help you make better development decisions faster.

The key is asking the right questions and being specific about your goals - the AI will handle the complex analysis and provide actionable recommendations tailored to your needs.
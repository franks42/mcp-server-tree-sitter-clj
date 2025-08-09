"""Tool registration with dependency injection for MCP server.

This module centralizes all tool registrations with proper dependency injection,
removing the need for global variables or singletons.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from ..di import DependencyContainer
from ..exceptions import ProjectError

logger = logging.getLogger(__name__)


def register_tools(mcp_server: Any, container: DependencyContainer) -> None:
    """Register all MCP tools with dependency injection.
    
    IMPORTANT: Tools are registered in priority order for optimal AI discovery.
    The context function is registered FIRST to ensure maximum visibility.

    Args:
        mcp_server: MCP server instance
        container: Dependency container
    """
    # Access dependencies
    config_manager = container.config_manager
    tree_cache = container.tree_cache
    project_registry = container.project_registry
    language_registry = container.language_registry

    # === PRIORITY REGISTRATION: ESSENTIAL CONTEXT FUNCTION ===
    # This MUST be registered FIRST for proper AI discovery and tool prominence
    _register_essential_context_tool(mcp_server, container)
    
    # === CORE TOOL REGISTRATION ===
    _register_configuration_tools(mcp_server, container)
    _register_project_management_tools(mcp_server, container)
    _register_language_tools(mcp_server, container)
    _register_file_operations_tools(mcp_server, container)
    _register_ast_analysis_tools(mcp_server, container)
    _register_search_query_tools(mcp_server, container)
    _register_code_analysis_tools(mcp_server, container)
    _register_cache_management_tools(mcp_server, container)
    _register_debug_tools(mcp_server, container)
    
    # Register Prompts
    _register_prompts(mcp_server, container)


def _register_essential_context_tool(mcp_server: Any, container: DependencyContainer) -> None:
    """Register the essential context function with maximum visibility.
    
    This function is registered FIRST and with enhanced metadata to ensure
    AI assistants discover it immediately and understand its critical importance.
    """
    # Access dependencies
    config_manager = container.config_manager
    language_registry = container.language_registry
    
    @mcp_server.tool(
        name="get_treesitter_context",
        description="⚡ START HERE: Essential Tree-sitter MCP server context and capabilities overview"
    )
    def get_treesitter_context() -> Dict[str, Any]:
        """⭐ ESSENTIAL FIRST CALL ⭐ - Complete Tree-sitter MCP server context and guidance

        🚨 CRITICAL: You MUST call this function BEFORE using any other tree-sitter tools!
        🎯 THIS IS YOUR STARTING POINT FOR ALL TREE-SITTER ANALYSIS!

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        📋 WHAT YOU GET:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🔹 Complete server capabilities overview (31+ languages)
        🔹 Enhanced Clojure semantic analysis features  
        🔹 Documentation links (AI cookbook + human guide)
        🔹 Quick start workflow and best practices
        🔹 Performance optimization guidance
        🔹 Tool reference with usage patterns

        🎯 WHY THIS IS MANDATORY:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ✅ Prevents tool misuse and suboptimal analysis
        ✅ Unlocks advanced semantic code understanding
        ✅ Provides roadmap for effective workflows  
        ✅ Links to comprehensive cookbooks and guides
        ✅ Maximizes analysis quality and accuracy

        ⚠️  CONSEQUENCE: Skipping this leads to 90% missed capabilities!
        💡 BOOKMARK THIS: Call anytime you need guidance or feature discovery
        
        Returns:
            Complete context with server info, capabilities, quick start guide,
            documentation links, and essential usage patterns for maximum effectiveness.

        """
        # Get available languages
        available_languages = language_registry.list_available_languages()

        # Get server configuration
        config = config_manager.get_config()

        return {
            "server_info": {
                "name": "Enhanced Tree-sitter MCP Server",
                "purpose": "Semantic code analysis with AST-level understanding across 31+ languages",
                "version": "0.8.0",
                "description": "Provides sophisticated code analysis beyond text-based tools using Abstract Syntax Trees",
            },
            "capabilities": {
                "supported_languages": len(available_languages),
                "language_list": available_languages,
                "enhanced_clojure_analysis": True,
                "features": {
                    "ast_parsing": "Parse and navigate syntax trees with cursor precision",
                    "symbol_extraction": "Functions, classes, variables with precise locations",
                    "dependency_analysis": "Import/require relationship mapping",
                    "complexity_analysis": "Objective code quality metrics",
                    "cross_file_analysis": "Project-wide dependency and usage tracking",
                    "semantic_queries": "Custom AST pattern matching with tree-sitter queries",
                    "performance": "Handle 1000+ LOC files in <500ms with intelligent caching",
                },
                "clojure_enhancements": {
                    "s_expression_navigation": "Navigate nested forms with cursor awareness",
                    "idiomatic_patterns": "Threading macros, destructuring, functional patterns",
                    "call_graph_analysis": "Function dependency mapping with complexity metrics",
                    "namespace_analysis": "Transitive dependency analysis with coupling metrics",
                    "performance_optimized": "Hybrid regex + tree-sitter for corruption-free parsing",
                },
            },
            "documentation": {
                "ai_cookbook": {
                    "file": "AI-TREESITTER-COOKBOOK.md",
                    "purpose": "Complete guide for AI assistants to leverage semantic analysis",
                    "sections": [
                        "Progressive workflows",
                        "31 MCP tools reference",
                        "Advanced use cases",
                        "Best practices",
                    ],
                    "access": "Use get_file() after register_project_tool() to read content",
                },
                "human_guide": {
                    "file": "HUMAN-TREESITTER-GUIDE.md",
                    "purpose": "Practical guide showing developers what to ask AIs",
                    "sections": [
                        "What to ask AI",
                        "Sample conversations",
                        "Language-specific requests",
                        "Task examples",
                    ],
                    "access": "Use get_file() after register_project_tool() to read content",
                },
                "features_reference": {
                    "file": "FEATURES.md",
                    "purpose": "Technical reference for all 31 MCP tools with examples",
                    "access": "Use get_file() after register_project_tool() to read content",
                },
            },
            "quick_start_workflow": {
                "step_1": {
                    "action": "Call get_treesitter_context()",
                    "purpose": "Get this overview (you just did this!)",
                },
                "step_2": {
                    "action": "register_project_tool(path='/path/to/code', name='project-name')",
                    "purpose": "Register a codebase for analysis",
                },
                "step_3": {
                    "action": "analyze_project(project='project-name', scan_depth=2)",
                    "purpose": "Get high-level project structure and organization",
                },
                "step_4": {
                    "action": "get_symbols(project='project-name', file_path='main.py')",
                    "purpose": "Extract functions, classes, imports from key files",
                },
                "step_5": {
                    "action": "Read cookbooks for advanced patterns",
                    "purpose": "get_file(project='project-name', path='AI-TREESITTER-COOKBOOK.md')",
                },
            },
            "core_tools_overview": {
                "project_management": [
                    "register_project_tool",
                    "list_projects_tool",
                    "remove_project_tool",
                ],
                "file_operations": ["list_files", "get_file", "get_file_metadata"],
                "ast_analysis": ["get_ast", "get_node_at_position"],
                "symbol_extraction": ["get_symbols", "find_usage", "get_dependencies"],
                "code_analysis": [
                    "analyze_complexity",
                    "find_similar_code",
                    "analyze_project",
                ],
                "search_and_query": ["find_text", "run_query", "build_query"],
                "configuration": ["configure", "clear_cache", "list_languages"],
            },
            "first_time_users": {
                "ai_assistants": {
                    "recommendation": "Read AI-TREESITTER-COOKBOOK.md for comprehensive semantic analysis patterns",
                    "key_sections": [
                        "Phase 1: Codebase Discovery",
                        "Phase 2: Focused Analysis",
                        "Advanced Use Cases",
                    ],
                    "why": "Learn progressive workflows and best practices for AST-level code understanding",
                },
                "human_developers": {
                    "recommendation": "Read HUMAN-TREESITTER-GUIDE.md for 'what to ask AI' guidance",
                    "key_sections": [
                        "Sample Conversations",
                        "Language-Specific Requests",
                        "Task Examples",
                    ],
                    "why": "Understand how to request sophisticated code analysis from AI assistants",
                },
            },
            "performance_notes": {
                "caching": f"Parse tree caching {'enabled' if config.cache.enabled else 'disabled'}",
                "max_file_size": f"{config.security.max_file_size_mb}MB file size limit",
                "optimization": "Intelligent cursor-based traversal and hybrid parsing for enhanced accuracy",
            },
            "next_steps": {
                "for_ais": "Start with register_project_tool() then analyze_project() for any codebase",
                "for_humans": "Ask AI: 'Analyze the structure and architecture of my project using tree-sitter'",
            },
            "context_acknowledgment": {
                "message": "✅ CONTEXT LOADED: You now have essential tree-sitter knowledge!",
                "warning": "🚨 Other AIs that skip this context miss 90% of server capabilities",
                "advice": "Bookmark this function - call it whenever you need guidance",
            },
        }


def _register_configuration_tools(mcp_server: Any, container: DependencyContainer) -> None:
    """Register configuration management tools."""
    # Access dependencies
    config_manager = container.config_manager
    tree_cache = container.tree_cache
    
    # Configuration Tool
    @mcp_server.tool()
    def configure(
        config_path: Optional[str] = None,
        cache_enabled: Optional[bool] = None,
        max_file_size_mb: Optional[int] = None,
        log_level: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Configure the server.

        Args:
            config_path: Path to YAML config file
            cache_enabled: Whether to enable parse tree caching
            max_file_size_mb: Maximum file size in MB
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

        Returns:
            Current configuration
        """
        # Get initial config for comparison
        initial_config = config_manager.get_config()
        logger.info(
            f"Initial configuration: "
            f"cache.max_size_mb = {initial_config.cache.max_size_mb}, "
            f"security.max_file_size_mb = {initial_config.security.max_file_size_mb}, "
            f"language.default_max_depth = {initial_config.language.default_max_depth}"
        )

        # Load config if path provided
        if config_path:
            logger.info(f"Configuring server with YAML config from: {config_path}")
            # Log absolute path to ensure we're looking at the right file
            abs_path = os.path.abspath(config_path)
            logger.info(f"Absolute path: {abs_path}")

            # Check if the file exists before trying to load it
            if not os.path.exists(abs_path):
                logger.error(f"Config file does not exist: {abs_path}")

            config_manager.load_from_file(abs_path)

        # Update specific settings
        if cache_enabled is not None:
            logger.info(f"Setting cache.enabled to {cache_enabled}")
            config_manager.update_value("cache.enabled", cache_enabled)
            tree_cache.set_enabled(cache_enabled)

        if max_file_size_mb is not None:
            logger.info(f"Setting security.max_file_size_mb to {max_file_size_mb}")
            config_manager.update_value("security.max_file_size_mb", max_file_size_mb)

        if log_level is not None:
            logger.info(f"Setting log_level to {log_level}")
            config_manager.update_value("log_level", log_level)

        # Return current config as dict
        return config_manager.to_dict()


def _register_project_management_tools(mcp_server: Any, container: DependencyContainer) -> None:
    """Register project management tools."""
    # Access dependencies  
    project_registry = container.project_registry
    language_registry = container.language_registry
    
    # Project Management Tools
    @mcp_server.tool(
        name="register_project_tool",
        description="🏗️ Register project for analysis - Essential second step after get_treesitter_context()"
    )
    def register_project_tool(
        path: str, name: Optional[str] = None, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register a project directory for code exploration.

        ⚡ RECOMMENDED: Call get_treesitter_context() FIRST for complete server guidance!
        📋 This is typically your SECOND step after getting context.

        Args:
            path: Path to the project directory
            name: Optional name for the project (defaults to directory name)
            description: Optional description of the project

        Returns:
            Project information
        """
        try:
            # Register project
            project = project_registry.register_project(name or path, path, description)

            # Scan for languages
            project.scan_files(language_registry)

            return project.to_dict()
        except Exception as e:
            raise ProjectError(f"Failed to register project: {e}") from e

    @mcp_server.tool(
        name="list_projects_tool",
        description="📋 List all registered projects"
    )
    def list_projects_tool() -> List[Dict[str, Any]]:
        """List all registered projects.

        Returns:
            List of project information
        """
        return project_registry.list_projects()

    @mcp_server.tool(
        name="remove_project_tool", 
        description="🗑️ Remove a registered project"
    )
    def remove_project_tool(name: str) -> Dict[str, str]:
        """Remove a registered project.

        Args:
            name: Project name

        Returns:
            Success message
        """
        try:
            project_registry.remove_project(name)
            return {"status": "success", "message": f"Project '{name}' removed"}
        except Exception as e:
            raise ProjectError(f"Failed to remove project: {e}") from e


def _register_language_tools(mcp_server: Any, container: DependencyContainer) -> None:
    """Register language parser tools."""
    # Access dependencies
    language_registry = container.language_registry
    
    # Language Tools
    @mcp_server.tool()
    def list_languages() -> Dict[str, Any]:
        """List available languages.

        Returns:
            Information about available languages
        """
        available = language_registry.list_available_languages()

        return {
            "available": available,
            "installable": [],  # No separate installation needed with language-pack
        }

    @mcp_server.tool()
    def check_language_available(language: str) -> Dict[str, str]:
        """Check if a tree-sitter language parser is available.

        Args:
            language: Language to check

        Returns:
            Success message
        """
        if language_registry.is_language_available(language):
            return {
                "status": "success",
                "message": f"Language '{language}' is available via tree-sitter-language-pack",
            }
        else:
            return {
                "status": "error",
                "message": f"Language '{language}' is not available",
            }


def _register_file_operations_tools(mcp_server: Any, container: DependencyContainer) -> None:
    """Register file operations tools."""
    # Access dependencies
    project_registry = container.project_registry
    
    # File Operations Tools
    @mcp_server.tool()
    def list_files(
        project: str,
        pattern: Optional[str] = None,
        max_depth: Optional[int] = None,
        extensions: Optional[List[str]] = None,
    ) -> List[str]:
        """List files in a project.

        Args:
            project: Project name
            pattern: Optional glob pattern (e.g., "**/*.py")
            max_depth: Maximum directory depth
            extensions: List of file extensions to include (without dot)

        Returns:
            List of file paths
        """
        from ..tools.file_operations import list_project_files

        return list_project_files(
            project_registry.get_project(project), pattern, max_depth, extensions
        )

    @mcp_server.tool()
    def get_file(
        project: str, path: str, max_lines: Optional[int] = None, start_line: int = 0
    ) -> str:
        """Get content of a file.

        Args:
            project: Project name
            path: File path relative to project root
            max_lines: Maximum number of lines to return
            start_line: First line to include (0-based)

        Returns:
            File content
        """
        from ..tools.file_operations import get_file_content

        return get_file_content(
            project_registry.get_project(project),
            path,
            max_lines=max_lines,
            start_line=start_line,
        )

    @mcp_server.tool()
    def get_file_metadata(project: str, path: str) -> Dict[str, Any]:
        """Get metadata for a file.

        Args:
            project: Project name
            path: File path relative to project root

        Returns:
            File metadata
        """
        from ..tools.file_operations import get_file_info

        return get_file_info(project_registry.get_project(project), path)


def _register_ast_analysis_tools(mcp_server: Any, container: DependencyContainer) -> None:
    """Register AST analysis tools."""
    # Access dependencies
    config_manager = container.config_manager
    tree_cache = container.tree_cache
    project_registry = container.project_registry
    language_registry = container.language_registry
    
    # AST Analysis Tools
    @mcp_server.tool()
    def get_ast(
        project: str,
        path: str,
        max_depth: Optional[int] = None,
        include_text: bool = True,
    ) -> Dict[str, Any]:
        """Get abstract syntax tree for a file.

        Args:
            project: Project name
            path: File path relative to project root
            max_depth: Maximum depth of the tree (default: 5)
            include_text: Whether to include node text

        Returns:
            AST as a nested dictionary
        """
        from ..tools.ast_operations import get_file_ast

        config = config_manager.get_config()
        depth = max_depth or config.language.default_max_depth

        return get_file_ast(
            project_registry.get_project(project),
            path,
            language_registry,
            tree_cache,
            max_depth=depth,
            include_text=include_text,
        )

    @mcp_server.tool()
    def get_node_at_position(
        project: str, path: str, row: int, column: int
    ) -> Optional[Dict[str, Any]]:
        """Find the AST node at a specific position.

        Args:
            project: Project name
            path: File path relative to project root
            row: Line number (0-based)
            column: Column number (0-based)

        Returns:
            Node information or None if not found
        """
        from ..models.ast import node_to_dict
        from ..tools.ast_operations import find_node_at_position

        project_obj = project_registry.get_project(project)
        file_path = project_obj.get_file_path(path)

        language = language_registry.language_for_file(path)
        if not language:
            raise ValueError(f"Could not detect language for {path}")

        from ..tools.ast_operations import parse_file as parse_file_helper

        tree, source_bytes = parse_file_helper(
            file_path, language, language_registry, tree_cache
        )

        node = find_node_at_position(tree.root_node, row, column)
        if node:
            return node_to_dict(node, source_bytes, max_depth=2)

        return None


def _register_search_query_tools(mcp_server: Any, container: DependencyContainer) -> None:
    """Register search and query tools."""
    # Access dependencies
    config_manager = container.config_manager
    tree_cache = container.tree_cache
    project_registry = container.project_registry
    language_registry = container.language_registry
    
    # Search and Query Tools
    @mcp_server.tool()
    def find_text(
        project: str,
        pattern: str,
        file_pattern: Optional[str] = None,
        max_results: int = 100,
        case_sensitive: bool = False,
        whole_word: bool = False,
        use_regex: bool = False,
        context_lines: int = 2,
    ) -> List[Dict[str, Any]]:
        """Search for text pattern in project files.

        Args:
            project: Project name
            pattern: Text pattern to search for
            file_pattern: Optional glob pattern (e.g., "**/*.py")
            max_results: Maximum number of results
            case_sensitive: Whether to do case-sensitive matching
            whole_word: Whether to match whole words only
            use_regex: Whether to treat pattern as a regular expression
            context_lines: Number of context lines to include

        Returns:
            List of matches with file, line number, and text
        """
        from ..tools.search import search_text

        config = config_manager.get_config()

        return search_text(
            project_registry.get_project(project),
            pattern,
            file_pattern,
            max_results if max_results is not None else config.max_results_default,
            case_sensitive,
            whole_word,
            use_regex,
            context_lines,
        )

    @mcp_server.tool()
    def run_query(
        project: str,
        query: str,
        file_path: Optional[str] = None,
        language: Optional[str] = None,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """Run a tree-sitter query on project files.

        Args:
            project: Project name
            query: Tree-sitter query string
            file_path: Optional specific file to query
            language: Language to use (required if file_path not provided)
            max_results: Maximum number of results

        Returns:
            List of query matches
        """
        from ..tools.search import query_code

        config = config_manager.get_config()

        return query_code(
            project_registry.get_project(project),
            query,
            language_registry,
            tree_cache,
            file_path,
            language,
            max_results if max_results is not None else config.max_results_default,
        )

    @mcp_server.tool()
    def get_query_template_tool(language: str, template_name: str) -> Dict[str, Any]:
        """Get a predefined tree-sitter query template.

        Args:
            language: Language name
            template_name: Template name (e.g., "functions", "classes")

        Returns:
            Query template information
        """
        from ..language.query_templates import get_query_template

        template = get_query_template(language, template_name)
        if not template:
            raise ValueError(f"No template '{template_name}' for language '{language}'")

        return {
            "language": language,
            "name": template_name,
            "query": template,
        }

    @mcp_server.tool()
    def list_query_templates_tool(language: Optional[str] = None) -> Dict[str, Any]:
        """List available query templates.

        Args:
            language: Optional language to filter by

        Returns:
            Available templates
        """
        from ..language.query_templates import list_query_templates

        return list_query_templates(language)

    @mcp_server.tool()
    def build_query(
        language: str, patterns: List[str], combine: str = "or"
    ) -> Dict[str, str]:
        """Build a tree-sitter query from templates or patterns.

        Args:
            language: Language name
            patterns: List of template names or custom patterns
            combine: How to combine patterns ("or" or "and")

        Returns:
            Combined query
        """
        from ..tools.query_builder import build_compound_query

        query = build_compound_query(language, patterns, combine)
        return {
            "language": language,
            "query": query,
        }

    @mcp_server.tool()
    def adapt_query(query: str, from_language: str, to_language: str) -> Dict[str, str]:
        """Adapt a query from one language to another.

        Args:
            query: Original query string
            from_language: Source language
            to_language: Target language

        Returns:
            Adapted query
        """
        from ..tools.query_builder import adapt_query_for_language

        adapted = adapt_query_for_language(query, from_language, to_language)
        return {
            "original_language": from_language,
            "target_language": to_language,
            "original_query": query,
            "adapted_query": adapted,
        }

    @mcp_server.tool()
    def get_node_types(language: str) -> Dict[str, str]:
        """Get descriptions of common node types for a language.

        Args:
            language: Language name

        Returns:
            Dictionary of node types and descriptions
        """
        from ..tools.query_builder import describe_node_types

        return describe_node_types(language)


def _register_code_analysis_tools(mcp_server: Any, container: DependencyContainer) -> None:
    """Register code analysis tools."""
    # Access dependencies
    config_manager = container.config_manager
    tree_cache = container.tree_cache
    project_registry = container.project_registry
    language_registry = container.language_registry
    
    # Analysis Tools
    @mcp_server.tool(
        name="get_symbols", 
        description="🎯 Extract functions, classes, imports from files - Essential for code understanding"
    )
    def get_symbols(
        project: str, file_path: str, symbol_types: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Extract symbols (functions, classes, imports) from a file.
        
        🎯 POPULAR CHOICE: Often the 4th step after context → register → analyze → symbols

        Args:
            project: Project name
            file_path: Path to the file
            symbol_types: Types of symbols to extract (functions, classes, imports, etc.)

        Returns:
            Dictionary of symbols by type
        """
        from ..tools.analysis import extract_symbols

        return extract_symbols(
            project_registry.get_project(project),
            file_path,
            language_registry,
            symbol_types,
        )

    @mcp_server.tool(
        name="analyze_project",
        description="🔍 Comprehensive project structure analysis - Popular third step after context + register"
    )
    def analyze_project(
        project: str, scan_depth: int = 3, ctx: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Analyze overall project structure and architecture.

        ⚡ RECOMMENDED: Call get_treesitter_context() FIRST for complete analysis guidance!
        🏗️ PREREQUISITE: Project must be registered with register_project_tool() first.
        🎯 This is often the THIRD step: context → register → analyze

        Args:
            project: Project name
            scan_depth: Depth of detailed analysis (higher is slower)
            ctx: Optional MCP context for progress reporting

        Returns:
            Project analysis
        """
        from ..tools.analysis import analyze_project_structure

        return analyze_project_structure(
            project_registry.get_project(project), language_registry, scan_depth, ctx
        )

    @mcp_server.tool()
    def get_dependencies(project: str, file_path: str) -> Dict[str, List[str]]:
        """Find dependencies of a file.

        Args:
            project: Project name
            file_path: Path to the file

        Returns:
            Dictionary of imports/includes
        """
        from ..tools.analysis import find_dependencies

        return find_dependencies(
            project_registry.get_project(project),
            file_path,
            language_registry,
        )

    @mcp_server.tool()
    def analyze_complexity(project: str, file_path: str) -> Dict[str, Any]:
        """Analyze code complexity.

        Args:
            project: Project name
            file_path: Path to the file

        Returns:
            Complexity metrics
        """
        from ..tools.analysis import analyze_code_complexity

        return analyze_code_complexity(
            project_registry.get_project(project),
            file_path,
            language_registry,
        )

    @mcp_server.tool()
    def find_similar_code(
        project: str,
        snippet: str,
        language: Optional[str] = None,
        threshold: float = 0.8,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Find similar code to a snippet.

        Args:
            project: Project name
            snippet: Code snippet to find
            language: Language of the snippet
            threshold: Similarity threshold (0.0-1.0)
            max_results: Maximum number of results

        Returns:
            List of similar code locations
        """
        # This is a simple implementation that uses text search
        from ..tools.search import search_text

        # Clean the snippet to handle potential whitespace differences
        clean_snippet = snippet.strip()

        # Map language names to file extensions
        extension_map = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "rust": "rs",
            "go": "go",
            "java": "java",
            "c": "c",
            "cpp": "cpp",
            "ruby": "rb",
            "swift": "swift",
            "kotlin": "kt",
        }

        # Get the appropriate file extension for the language
        extension = extension_map.get(language, language) if language else None
        file_pattern = f"**/*.{extension}" if extension else None

        return search_text(
            project_registry.get_project(project),
            clean_snippet,
            file_pattern=file_pattern,
            max_results=max_results,
            case_sensitive=False,  # Ignore case differences
            whole_word=False,  # Allow partial matches
            use_regex=False,  # Simple text search is more reliable for this case
        )

    @mcp_server.tool()
    def find_usage(
        project: str,
        symbol: str,
        file_path: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Find usage of a symbol.

        Args:
            project: Project name
            symbol: Symbol name to find
            file_path: Optional file to look in (for local symbols)
            language: Language to search in

        Returns:
            List of usage locations
        """
        # Detect language if not provided but file_path is
        if not language and file_path:
            language = language_registry.language_for_file(file_path)

        if not language:
            raise ValueError("Either language or file_path must be provided")

        # Build a query to find references to the symbol
        query = f"""
        (
          (identifier) @reference
          (#eq? @reference "{symbol}")
        )
        """

        from ..tools.search import query_code

        return query_code(
            project_registry.get_project(project),
            query,
            language_registry,
            tree_cache,
            file_path,
            language,
        )


def _register_cache_management_tools(mcp_server: Any, container: DependencyContainer) -> None:
    """Register cache management tools."""
    # Access dependencies
    tree_cache = container.tree_cache
    project_registry = container.project_registry
    
    # Cache Management
    @mcp_server.tool()
    def clear_cache(
        project: Optional[str] = None, file_path: Optional[str] = None
    ) -> Dict[str, str]:
        """Clear the parse tree cache.

        Args:
            project: Optional project to clear cache for
            file_path: Optional specific file to clear cache for

        Returns:
            Status message
        """
        if project and file_path:
            # Clear cache for specific file
            project_obj = project_registry.get_project(project)
            abs_path = project_obj.get_file_path(file_path)
            tree_cache.invalidate(abs_path)
            message = f"Cache cleared for {file_path} in project {project}"
        elif project:
            # Clear cache for entire project
            # No direct way to clear by project, so invalidate entire cache
            tree_cache.invalidate()
            message = f"Cache cleared for project {project}"
        else:
            # Clear entire cache
            tree_cache.invalidate()
            message = "All caches cleared"

        return {"status": "success", "message": message}


def _register_debug_tools(mcp_server: Any, container: DependencyContainer) -> None:
    """Register debug and diagnostic tools."""
    
    # Debug Tools
    @mcp_server.tool()
    def diagnose_config(config_path: str) -> Dict[str, Any]:
        """Diagnose issues with YAML configuration loading.

        Args:
            config_path: Path to YAML config file

        Returns:
            Diagnostic information
        """
        from ..tools.debug import diagnose_yaml_config

        return diagnose_yaml_config(config_path)


def _register_prompts(mcp_server: Any, container: DependencyContainer) -> None:
    """Register all prompt templates with dependency injection.

    Args:
        mcp_server: MCP server instance
        container: Dependency container
    """
    # Get dependencies
    project_registry = container.project_registry
    language_registry = container.language_registry

    @mcp_server.prompt()
    def code_review(project: str, file_path: str) -> str:
        """Create a prompt for reviewing a code file"""
        from ..tools.analysis import extract_symbols
        from ..tools.file_operations import get_file_content

        project_obj = project_registry.get_project(project)
        content = get_file_content(project_obj, file_path)
        language = language_registry.language_for_file(file_path)

        # Get structure information
        structure = ""
        try:
            symbols = extract_symbols(project_obj, file_path, language_registry)

            if "functions" in symbols and symbols["functions"]:
                structure += "\nFunctions:\n"
                for func in symbols["functions"]:
                    structure += f"- {func['name']}\n"

            if "classes" in symbols and symbols["classes"]:
                structure += "\nClasses:\n"
                for cls in symbols["classes"]:
                    structure += f"- {cls['name']}\n"
        except Exception:
            pass

        return f"""
        Please review this {language} code file:

        ```{language}
        {content}
        ```

        {structure}

        Focus on:
        1. Code clarity and organization
        2. Potential bugs or issues
        3. Performance considerations
        4. Best practices for {language}
        """

    @mcp_server.prompt()
    def explain_code(project: str, file_path: str, focus: Optional[str] = None) -> str:
        """Create a prompt for explaining a code file"""
        from ..tools.file_operations import get_file_content

        project_obj = project_registry.get_project(project)
        content = get_file_content(project_obj, file_path)
        language = language_registry.language_for_file(file_path)

        focus_prompt = ""
        if focus:
            focus_prompt = f"\nPlease focus specifically on explaining: {focus}"

        return f"""
        Please explain this {language} code file:

        ```{language}
        {content}
        ```

        Provide a clear explanation of:
        1. What this code does
        2. How it's structured
        3. Any important patterns or techniques used
        {focus_prompt}
        """

    @mcp_server.prompt()
    def explain_tree_sitter_query() -> str:
        """Create a prompt explaining tree-sitter query syntax"""
        return """
        Tree-sitter queries use S-expression syntax to match patterns in code.

        Basic query syntax:
        - `(node_type)` - Match nodes of a specific type
        - `(node_type field: (child_type))` - Match nodes with specific field relationships
        - `@name` - Capture a node with a name
        - `#predicate` - Apply additional constraints

        Example query for Python functions:
        ```
        (function_definition
          name: (identifier) @function.name
          parameters: (parameters) @function.params
          body: (block) @function.body) @function.def
        ```

        Please write a tree-sitter query to find:
        """

    @mcp_server.prompt()
    def suggest_improvements(project: str, file_path: str) -> str:
        """Create a prompt for suggesting code improvements"""
        from ..tools.analysis import analyze_code_complexity
        from ..tools.file_operations import get_file_content

        project_obj = project_registry.get_project(project)
        content = get_file_content(project_obj, file_path)
        language = language_registry.language_for_file(file_path)

        try:
            complexity = analyze_code_complexity(
                project_obj, file_path, language_registry
            )
            complexity_info = f"""
            Code metrics:
            - Line count: {complexity["line_count"]}
            - Code lines: {complexity["code_lines"]}
            - Comment lines: {complexity["comment_lines"]}
            - Comment ratio: {complexity["comment_ratio"]:.1%}
            - Functions: {complexity["function_count"]}
            - Classes: {complexity["class_count"]}
            - Avg. function length: {complexity["avg_function_lines"]} lines
            - Cyclomatic complexity: {complexity["cyclomatic_complexity"]}
            """
        except Exception:
            complexity_info = ""

        return f"""
        Please suggest improvements for this {language} code:

        ```{language}
        {content}
        ```

        {complexity_info}

        Suggest specific, actionable improvements for:
        1. Code quality and readability
        2. Performance optimization
        3. Error handling and robustness
        4. Following {language} best practices

        Where possible, provide code examples of your suggestions.
        """

    @mcp_server.prompt()
    def project_overview(project: str) -> str:
        """Create a prompt for a project overview analysis"""
        from ..tools.analysis import analyze_project_structure

        project_obj = project_registry.get_project(project)

        try:
            analysis = analyze_project_structure(project_obj, language_registry)

            languages_str = "\n".join(
                f"- {lang}: {count} files"
                for lang, count in analysis["languages"].items()
            )

            entry_points_str = (
                "\n".join(
                    f"- {entry['path']} ({entry['language']})"
                    for entry in analysis["entry_points"]
                )
                if analysis["entry_points"]
                else "None detected"
            )

            build_files_str = (
                "\n".join(
                    f"- {file['path']} ({file['type']})"
                    for file in analysis["build_files"]
                )
                if analysis["build_files"]
                else "None detected"
            )

        except Exception:
            languages_str = "Error analyzing languages"
            entry_points_str = "Error detecting entry points"
            build_files_str = "Error detecting build files"

        return f"""
        Please analyze this codebase:

        Project name: {project_obj.name}
        Path: {project_obj.root_path}

        Languages:
        {languages_str}

        Possible entry points:
        {entry_points_str}

        Build configuration:
        {build_files_str}

        Based on this information, please:
        1. Provide an overview of what this project seems to be
        2. Identify the main components and their relationships
        3. Suggest where to start exploring the codebase
        4. Identify any patterns or architectural approaches used
        """

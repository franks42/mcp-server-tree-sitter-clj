"""Clojure-specific analysis functions for tree-sitter MCP server."""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from tree_sitter_language_pack import get_language, get_parser

logger = logging.getLogger(__name__)


class ClojureAnalyzer:
    """Analyzer for Clojure code using tree-sitter."""

    def __init__(self):
        """Initialize the Clojure analyzer."""
        self.parser = get_parser("clojure")
        self.language = get_language("clojure")

    def find_functions(
        self, code: str, pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find function definitions in Clojure code using hybrid regex + tree-sitter approach.

        This approach first finds function boundaries using regex to avoid tree-sitter
        parsing issues with adjacent functions, then uses tree-sitter for detailed analysis.

        Args:
            code: Clojure source code
            pattern: Optional regex pattern to filter function names

        Returns:
            List of function information dictionaries
        """
        import re

        # First, find all potential function definitions using regex
        # This handles the case where tree-sitter has issues with adjacent functions
        func_pattern = r"\(\s*(defn-?)\s+([\w-]+)"
        matches = []

        for match in re.finditer(func_pattern, code):
            defn_type = match.group(1)  # defn or defn-
            func_name = match.group(2)  # function name
            start_pos = match.start()

            # If pattern is specified, check if this function matches
            if pattern and not re.match(pattern, func_name):
                continue

            matches.append(
                {
                    "name": func_name,
                    "type": defn_type,
                    "start_pos": start_pos,
                    "match_obj": match,
                }
            )

        if not matches:
            return []

        # Now extract complete function boundaries by finding matching parentheses
        functions = []

        for i, match_info in enumerate(matches):
            start_pos = match_info["start_pos"]

            # Find the end of this function by counting parentheses
            paren_count = 0
            end_pos = start_pos

            for j in range(start_pos, len(code)):
                char = code[j]
                if char == "(":
                    paren_count += 1
                elif char == ")":
                    paren_count -= 1
                    if paren_count == 0:  # Found matching closing paren
                        end_pos = j + 1
                        break

            # Extract the complete function text
            func_text = code[start_pos:end_pos]

            # Use tree-sitter to analyze this individual function for detailed info
            detailed_info = self._analyze_single_function(func_text, start_pos, code)

            if detailed_info:
                # Override with our reliable regex-extracted basic info
                detailed_info["name"] = match_info["name"]
                detailed_info["type"] = match_info["type"]
                detailed_info["private"] = match_info["type"] == "defn-"
                detailed_info["start_byte"] = start_pos
                detailed_info["end_byte"] = end_pos
                detailed_info["definition"] = func_text

                # Calculate line numbers
                lines_before = code[:start_pos].count("\n")
                detailed_info["start_line"] = lines_before + 1
                lines_in_func = func_text.count("\n")
                detailed_info["end_line"] = detailed_info["start_line"] + lines_in_func

                functions.append(detailed_info)

        return functions

    def _analyze_single_function(
        self, func_text: str, offset: int, full_code: str
    ) -> Dict[str, Any]:
        """
        Analyze a single function using tree-sitter for detailed extraction.

        Args:
            func_text: The isolated function text
            offset: Byte offset in the full code
            full_code: The complete source code for context

        Returns:
            Dictionary with detailed function information
        """
        try:
            tree = self.parser.parse(bytes(func_text, "utf8"))

            # Simple query for a single function
            single_func_query = """
            (list_lit
              (sym_lit) @defn_type
              (sym_lit) @function_name
              (str_lit)? @docstring
              (vec_lit)? @params) @function_definition
            """

            query = self.language.query(single_func_query)
            matches = query.matches(tree.root_node)

            if matches:
                match = matches[0]  # Should only be one function
                _, captures = match

                func_info = {}

                # Extract docstring
                docstring = self._extract_node_text(func_text, captures, "docstring")
                if docstring:
                    func_info["docstring"] = docstring

                # Extract parameters
                params = self._extract_node_text(func_text, captures, "params")
                if params:
                    func_info["params"] = params

                return func_info

        except Exception as e:
            logger.debug(f"Tree-sitter analysis failed for single function: {e}")

        return {}

    def find_namespaces(self, code: str) -> List[Dict[str, Any]]:
        """
        Find namespace declarations in Clojure code using hybrid regex + tree-sitter approach.

        Args:
            code: Clojure source code

        Returns:
            List of namespace information dictionaries
        """
        import re

        # Use regex to find namespace declarations more reliably
        # Pattern: (ns namespace-name [optional docstring] [optional metadata])
        ns_pattern = r"\(\s*ns\s+([\w.-]+)"

        namespaces = []

        for match in re.finditer(ns_pattern, code):
            ns_name = match.group(1)
            start_pos = match.start()

            # Find the end of this namespace declaration by finding matching parentheses
            paren_count = 0
            end_pos = start_pos

            for j in range(start_pos, len(code)):
                char = code[j]
                if char == "(":
                    paren_count += 1
                elif char == ")":
                    paren_count -= 1
                    if paren_count == 0:  # Found matching closing paren
                        end_pos = j + 1
                        break

            # Extract the complete namespace declaration
            ns_text = code[start_pos:end_pos]

            # Use tree-sitter to analyze this namespace for detailed info
            detailed_info = self._analyze_single_namespace(ns_text, start_pos, code)

            # Build namespace info
            ns_info = {
                "name": ns_name,
                "start_byte": start_pos,
                "end_byte": end_pos,
                "declaration": ns_text,
            }

            # Calculate line numbers
            lines_before = code[:start_pos].count("\n")
            ns_info["start_line"] = lines_before + 1
            lines_in_ns = ns_text.count("\n")
            ns_info["end_line"] = ns_info["start_line"] + lines_in_ns

            # Add detailed info if available
            if detailed_info:
                ns_info.update(detailed_info)

            namespaces.append(ns_info)

        return namespaces

    def _analyze_single_namespace(
        self, ns_text: str, offset: int, full_code: str
    ) -> Dict[str, Any]:
        """
        Analyze a single namespace declaration using tree-sitter for detailed extraction.

        Args:
            ns_text: The isolated namespace declaration text
            offset: Byte offset in the full code
            full_code: The complete source code for context

        Returns:
            Dictionary with detailed namespace information
        """
        try:
            tree = self.parser.parse(bytes(ns_text, "utf8"))

            ns_info = {}

            # Extract docstring if present (usually the second string literal)
            # Look for string literals in the namespace declaration
            def find_strings(node):
                if node.type == "str_lit":
                    text = ns_text[node.start_byte : node.end_byte]
                    return [text]

                strings = []
                for child in node.children:
                    strings.extend(find_strings(child))
                return strings

            strings = find_strings(tree.root_node)
            if strings:
                # Usually the first string after ns name is the docstring
                ns_info["docstring"] = strings[0]

            # Extract require/import statements
            requires = []
            imports = []

            def find_dependencies(node):
                if node.type == "list_lit" and node.children:
                    # Filter out parentheses to get actual content
                    content_children = [
                        c for c in node.children if c.type not in ["(", ")"]
                    ]

                    if content_children:
                        first_content = content_children[0]
                        if first_content.type == "kwd_lit":
                            keyword = ns_text[
                                first_content.start_byte : first_content.end_byte
                            ]
                            if keyword == ":require":
                                # Extract require statements from remaining content children
                                for child in content_children[1:]:
                                    if child.type == "vec_lit":
                                        req_text = ns_text[
                                            child.start_byte : child.end_byte
                                        ]
                                        requires.append(req_text.strip())
                            elif keyword == ":import":
                                # Extract import statements from remaining content children
                                for child in content_children[1:]:
                                    if child.type == "vec_lit":
                                        import_text = ns_text[
                                            child.start_byte : child.end_byte
                                        ]
                                        imports.append(import_text.strip())

                for child in node.children:
                    find_dependencies(child)

            find_dependencies(tree.root_node)

            if requires:
                ns_info["requires"] = requires
            if imports:
                ns_info["imports"] = imports

            return ns_info

        except Exception as e:
            logger.debug(f"Tree-sitter namespace analysis failed: {e}")
            return {}

    def find_imports(self, code: str) -> List[Dict[str, Any]]:
        """
        Find import/require statements in Clojure code.

        Args:
            code: Clojure source code

        Returns:
            List of import/require information dictionaries
        """
        import re

        # First get namespace info which includes imports/requires
        namespaces = self.find_namespaces(code)

        all_dependencies = []

        for ns in namespaces:
            ns_name = ns.get("name", "unknown")

            # Add requires
            for req in ns.get("requires", []):
                all_dependencies.append(
                    {
                        "type": "require",
                        "statement": req,
                        "namespace": ns_name,
                        "source_line": ns.get("start_line", 0),
                    }
                )

            # Add imports
            for imp in ns.get("imports", []):
                all_dependencies.append(
                    {
                        "type": "import",
                        "statement": imp,
                        "namespace": ns_name,
                        "source_line": ns.get("start_line", 0),
                    }
                )

        return all_dependencies

    def find_sexp_at_position(
        self, code: str, line: int, column: int
    ) -> Optional[Dict[str, Any]]:
        """
        Find the s-expression at a given position.

        Args:
            code: Clojure source code
            line: Line number (1-based)
            column: Column number (0-based)

        Returns:
            Dictionary with s-expression information, or None if not found
        """
        try:
            tree = self.parser.parse(bytes(code, "utf8"))

            # Convert line/column to byte position
            lines = code.split("\n")
            if line < 1 or line > len(lines):
                return None

            # Calculate byte position
            byte_pos = sum(len(lines[i]) + 1 for i in range(line - 1))  # +1 for newline
            byte_pos += column

            if byte_pos >= len(code):
                return None

            # Find the node at this position
            node = tree.root_node.descendant_for_byte_range(byte_pos, byte_pos)

            if not node:
                return None

            # Walk up to find the containing s-expression (list_lit)
            sexp_node = node
            while sexp_node and sexp_node.type != "list_lit":
                sexp_node = sexp_node.parent

            if not sexp_node:
                # If no list found, use the current node
                sexp_node = node

            # Extract s-expression info
            sexp_text = code[sexp_node.start_byte : sexp_node.end_byte]
            start_line = code[: sexp_node.start_byte].count("\n") + 1
            start_col = (
                sexp_node.start_byte - code.rfind("\n", 0, sexp_node.start_byte) - 1
            )
            end_line = code[: sexp_node.end_byte].count("\n") + 1
            end_col = sexp_node.end_byte - code.rfind("\n", 0, sexp_node.end_byte) - 1

            return {
                "type": sexp_node.type,
                "text": sexp_text,
                "start_line": start_line,
                "start_column": start_col,
                "end_line": end_line,
                "end_column": end_col,
                "start_byte": sexp_node.start_byte,
                "end_byte": sexp_node.end_byte,
                "depth": self._calculate_depth(sexp_node),
            }

        except Exception as e:
            logger.error(f"Error finding s-expression at position: {e}")
            return None

    def find_matching_paren(
        self, code: str, line: int, column: int
    ) -> Optional[Dict[str, Any]]:
        """
        Find the matching parenthesis for the parenthesis at given position.

        Args:
            code: Clojure source code
            line: Line number (1-based)
            column: Column number (0-based)

        Returns:
            Dictionary with matching parenthesis information, or None if not found
        """
        try:
            # Convert line/column to byte position
            lines = code.split("\n")
            if line < 1 or line > len(lines):
                return None

            byte_pos = sum(len(lines[i]) + 1 for i in range(line - 1))
            byte_pos += column

            if byte_pos >= len(code):
                return None

            char = code[byte_pos]
            if char not in "()[]{}":
                return None

            tree = self.parser.parse(bytes(code, "utf8"))
            node = tree.root_node.descendant_for_byte_range(byte_pos, byte_pos + 1)

            if not node:
                return None

            # Find the parent container
            parent = node.parent
            if not parent:
                return None

            # Find matching bracket based on the parent container
            if char in "([{":
                # Opening bracket - find closing
                if parent.type == "list_lit" and parent.children:
                    closing_node = parent.children[
                        -1
                    ]  # Last child should be closing paren
                elif parent.type == "vec_lit" and parent.children:
                    closing_node = parent.children[
                        -1
                    ]  # Last child should be closing bracket
                elif parent.type == "map_lit" and parent.children:
                    closing_node = parent.children[
                        -1
                    ]  # Last child should be closing brace
                else:
                    return None
            else:
                # Closing bracket - find opening
                if parent.type == "list_lit" and parent.children:
                    closing_node = parent.children[
                        0
                    ]  # First child should be opening paren
                elif parent.type == "vec_lit" and parent.children:
                    closing_node = parent.children[
                        0
                    ]  # First child should be opening bracket
                elif parent.type == "map_lit" and parent.children:
                    closing_node = parent.children[
                        0
                    ]  # First child should be opening brace
                else:
                    return None

            # Calculate line/column for matching bracket
            match_line = code[: closing_node.start_byte].count("\n") + 1
            match_col = (
                closing_node.start_byte
                - code.rfind("\n", 0, closing_node.start_byte)
                - 1
            )

            return {
                "line": match_line,
                "column": match_col,
                "byte_position": closing_node.start_byte,
                "character": code[closing_node.start_byte],
                "container_type": parent.type,
            }

        except Exception as e:
            logger.error(f"Error finding matching parenthesis: {e}")
            return None

    def navigate_sexp(
        self, code: str, line: int, column: int, direction: str
    ) -> Optional[Dict[str, Any]]:
        """
        Navigate to adjacent s-expressions.

        Args:
            code: Clojure source code
            line: Line number (1-based)
            column: Column number (0-based)
            direction: 'next', 'prev', 'up', 'down', 'top'

        Returns:
            Dictionary with target s-expression information, or None if not found
        """
        try:
            current_sexp = self.find_sexp_at_position(code, line, column)
            if not current_sexp:
                return None

            tree = self.parser.parse(bytes(code, "utf8"))
            current_node = tree.root_node.descendant_for_byte_range(
                current_sexp["start_byte"], current_sexp["start_byte"]
            )

            # Find the containing list node
            while current_node and current_node.type != "list_lit":
                current_node = current_node.parent

            if not current_node:
                return None

            target_node = None

            if direction == "next":
                # Find next sibling s-expression
                if current_node.next_sibling:
                    target_node = current_node.next_sibling
                    # Skip non-expression siblings
                    while target_node and target_node.type in ["(", ")", " ", "\n"]:
                        target_node = target_node.next_sibling

            elif direction == "prev":
                # Find previous sibling s-expression
                if current_node.prev_sibling:
                    target_node = current_node.prev_sibling
                    # Skip non-expression siblings
                    while target_node and target_node.type in ["(", ")", " ", "\n"]:
                        target_node = target_node.prev_sibling

            elif direction == "up":
                # Find parent s-expression
                target_node = current_node.parent
                while target_node and target_node.type not in [
                    "list_lit",
                    "vec_lit",
                    "map_lit",
                ]:
                    target_node = target_node.parent

            elif direction == "down":
                # Find first child s-expression
                if current_node.children:
                    for child in current_node.children:
                        if child.type in ["list_lit", "vec_lit", "map_lit"]:
                            target_node = child
                            break

            elif direction == "top":
                # Find top-level s-expression
                target_node = current_node
                while target_node.parent and target_node.parent.type != "source":
                    target_node = target_node.parent

            if not target_node:
                return None

            # Convert target node to s-expression info
            sexp_text = code[target_node.start_byte : target_node.end_byte]
            start_line = code[: target_node.start_byte].count("\n") + 1
            start_col = (
                target_node.start_byte - code.rfind("\n", 0, target_node.start_byte) - 1
            )
            end_line = code[: target_node.end_byte].count("\n") + 1
            end_col = (
                target_node.end_byte - code.rfind("\n", 0, target_node.end_byte) - 1
            )

            return {
                "type": target_node.type,
                "text": sexp_text,
                "start_line": start_line,
                "start_column": start_col,
                "end_line": end_line,
                "end_column": end_col,
                "start_byte": target_node.start_byte,
                "end_byte": target_node.end_byte,
                "depth": self._calculate_depth(target_node),
            }

        except Exception as e:
            logger.error(f"Error navigating s-expression: {e}")
            return None

    def find_macros(
        self, code: str, pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find macro definitions and macro usage in Clojure code.

        Args:
            code: Clojure source code
            pattern: Optional regex pattern to filter macro names

        Returns:
            List of macro information dictionaries
        """
        import re

        macros = []

        # Find defmacro definitions using hybrid approach
        defmacro_pattern = r"\(\s*(defmacro)\s+([\w-]+)"

        for match in re.finditer(defmacro_pattern, code):
            macro_type = match.group(1)  # defmacro
            macro_name = match.group(2)  # macro name
            start_pos = match.start()

            # If pattern is specified, check if this macro matches
            if pattern and not re.match(pattern, macro_name):
                continue

            # Find the end of this macro by counting parentheses
            paren_count = 0
            end_pos = start_pos

            for j in range(start_pos, len(code)):
                char = code[j]
                if char == "(":
                    paren_count += 1
                elif char == ")":
                    paren_count -= 1
                    if paren_count == 0:  # Found matching closing paren
                        end_pos = j + 1
                        break

            # Extract the complete macro text
            macro_text = code[start_pos:end_pos]

            # Use tree-sitter to analyze this individual macro for detailed info
            detailed_info = self._analyze_single_function(macro_text, start_pos, code)

            # Build macro info
            macro_info = {
                "name": macro_name,
                "type": "defmacro",
                "definition": macro_text,
                "start_byte": start_pos,
                "end_byte": end_pos,
                "start_line": code[:start_pos].count("\n") + 1,
                "end_line": code[:start_pos].count("\n") + 1 + macro_text.count("\n"),
                "macro_category": "definition",
            }

            # Add detailed info if available
            if detailed_info:
                macro_info.update(detailed_info)

            macros.append(macro_info)

        # Find threading macro usage (-> ->> some-> some->> cond-> cond->>)
        threading_patterns = [
            (r"\(\s*(->>?)\s+", "threading"),
            (r"\(\s*(some->>?)\s+", "conditional_threading"),
            (r"\(\s*(cond->>?)\s+", "conditional_threading"),
            (r"\(\s*(as->>?)\s+", "binding_threading"),
        ]

        for pattern_regex, category in threading_patterns:
            for match in re.finditer(pattern_regex, code):
                threading_macro = match.group(1)
                start_pos = match.start()

                # Find the end of this threading macro by counting parentheses
                paren_count = 0
                end_pos = start_pos

                for j in range(start_pos, len(code)):
                    char = code[j]
                    if char == "(":
                        paren_count += 1
                    elif char == ")":
                        paren_count -= 1
                        if paren_count == 0:  # Found matching closing paren
                            end_pos = j + 1
                            break

                # Extract the complete threading expression
                threading_text = code[start_pos:end_pos]

                macros.append(
                    {
                        "name": threading_macro,
                        "type": "threading_macro",
                        "definition": threading_text,
                        "start_byte": start_pos,
                        "end_byte": end_pos,
                        "start_line": code[:start_pos].count("\n") + 1,
                        "end_line": code[:start_pos].count("\n")
                        + 1
                        + threading_text.count("\n"),
                        "macro_category": category,
                    }
                )

        return macros

    def find_threading_macros(self, code: str) -> List[Dict[str, Any]]:
        """
        Find threading macro usage specifically (-> ->> some-> some->> etc.).

        Args:
            code: Clojure source code

        Returns:
            List of threading macro usage dictionaries
        """
        # Use find_macros but filter for only threading macros
        all_macros = self.find_macros(code)
        return [m for m in all_macros if m["type"] == "threading_macro"]

    def find_protocols_and_types(
        self, code: str, pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find protocol definitions, deftype, and defrecord in Clojure code.

        Args:
            code: Clojure source code
            pattern: Optional regex pattern to filter names

        Returns:
            List of protocol/type information dictionaries
        """
        import re

        constructs = []

        # Define patterns for different Clojure type constructs
        patterns = [
            (r"\(\s*(defprotocol)\s+([\w-]+)", "defprotocol"),
            (r"\(\s*(deftype)\s+([\w-]+)", "deftype"),
            (r"\(\s*(defrecord)\s+([\w-]+)", "defrecord"),
            (r"\(\s*(reify)\s+", "reify"),
            (r"\(\s*(extend-type)\s+([\w.-]+)", "extend-type"),
            (r"\(\s*(extend-protocol)\s+([\w-]+)", "extend-protocol"),
        ]

        for pattern_regex, construct_type in patterns:
            for match in re.finditer(pattern_regex, code):
                if construct_type in ["reify"]:
                    # reify doesn't have a name, handle specially
                    construct_name = "anonymous"
                    start_pos = match.start()
                else:
                    construct_name = (
                        match.group(2) if len(match.groups()) >= 2 else match.group(1)
                    )
                    start_pos = match.start()

                # If pattern is specified, check if this construct matches
                if (
                    pattern
                    and construct_name != "anonymous"
                    and not re.match(pattern, construct_name)
                ):
                    continue

                # Find the end of this construct by counting parentheses
                paren_count = 0
                end_pos = start_pos

                for j in range(start_pos, len(code)):
                    char = code[j]
                    if char == "(":
                        paren_count += 1
                    elif char == ")":
                        paren_count -= 1
                        if paren_count == 0:  # Found matching closing paren
                            end_pos = j + 1
                            break

                # Extract the complete construct text
                construct_text = code[start_pos:end_pos]

                # Analyze methods/fields if applicable
                methods = []
                fields = []

                if construct_type in ["defprotocol"]:
                    methods = self._extract_protocol_methods(construct_text)
                elif construct_type in ["deftype", "defrecord"]:
                    fields, methods = self._extract_type_fields_and_methods(
                        construct_text
                    )

                construct_info = {
                    "name": construct_name,
                    "type": construct_type,
                    "definition": construct_text,
                    "start_byte": start_pos,
                    "end_byte": end_pos,
                    "start_line": code[:start_pos].count("\n") + 1,
                    "end_line": code[:start_pos].count("\n")
                    + 1
                    + construct_text.count("\n"),
                    "methods": methods,
                    "fields": fields,
                }

                constructs.append(construct_info)

        return constructs

    def _extract_protocol_methods(self, protocol_text: str) -> List[Dict[str, Any]]:
        """Extract method signatures from a protocol definition."""
        import re

        methods = []

        # Look for method signatures like (method-name [args] "docstring"?)
        method_pattern = r'\(\s*([a-z-]+)\s+\[([^\]]*)\](?:\s+"([^"]*)")?'

        for match in re.finditer(method_pattern, protocol_text):
            method_name = match.group(1)
            params = match.group(2).strip() if match.group(2) else ""
            docstring = match.group(3) if match.group(3) else None

            methods.append(
                {"name": method_name, "params": params, "docstring": docstring}
            )

        return methods

    def _extract_type_fields_and_methods(self, type_text: str) -> tuple:
        """Extract fields and methods from deftype/defrecord definition."""
        import re

        fields = []
        methods = []

        # Extract field names from the constructor - first vector after type name
        # Pattern: (deftype TypeName [field1 field2 ...] ...)
        field_pattern = r"\(\s*def(?:type|record)\s+[\w-]+\s+\[([^\]]*)\]"
        field_match = re.search(field_pattern, type_text)

        if field_match:
            field_text = field_match.group(1).strip()
            if field_text:
                # Split on whitespace and filter out empty strings
                fields = [f.strip() for f in re.split(r"\s+", field_text) if f.strip()]

        # Extract method implementations - look for forms like (method-name [args] body...)
        # This is simplified - proper parsing would need more sophisticated tree analysis
        method_pattern = r"\(\s*([a-z-]+)\s+\[([^\]]*)\]"

        for match in re.finditer(method_pattern, type_text):
            method_name = match.group(1)
            params = match.group(2).strip() if match.group(2) else ""

            # Skip if this looks like the constructor (same name as field pattern)
            if not field_match or method_name not in field_text:
                methods.append({"name": method_name, "params": params})

        return fields, methods

    def find_protocols(
        self, code: str, pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find protocol definitions specifically.

        Args:
            code: Clojure source code
            pattern: Optional regex pattern to filter protocol names

        Returns:
            List of protocol information dictionaries
        """
        all_constructs = self.find_protocols_and_types(code, pattern)
        return [c for c in all_constructs if c["type"] == "defprotocol"]

    def find_types(
        self, code: str, pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find deftype and defrecord definitions.

        Args:
            code: Clojure source code
            pattern: Optional regex pattern to filter type names

        Returns:
            List of type information dictionaries
        """
        all_constructs = self.find_protocols_and_types(code, pattern)
        return [c for c in all_constructs if c["type"] in ["deftype", "defrecord"]]

    def analyze_destructuring_patterns(self, code: str) -> List[Dict[str, Any]]:
        """
        Analyze destructuring patterns in function parameters, let bindings, etc.

        Args:
            code: Clojure source code

        Returns:
            List of destructuring pattern information dictionaries
        """
        import re

        patterns = []

        # Find destructuring in various contexts
        # Note: We need to match balanced brackets, so we'll find the full context first
        destructuring_contexts = [
            # Function parameters: (defn func-name [...] ...)
            (r"\(\s*defn-?\s+[\w-]+\s+", "function_params"),
            # Let bindings: (let [...] ...)
            (r"\(\s*let\s+", "let_bindings"),
            # For loops: (for [...] ...)
            (r"\(\s*for\s+", "for_bindings"),
            # Doseq: (doseq [...] ...)
            (r"\(\s*doseq\s+", "doseq_bindings"),
        ]

        for pattern_regex, context_type in destructuring_contexts:
            for match in re.finditer(pattern_regex, code):
                start_pos = match.end()  # Start after the matched pattern

                # Skip whitespace to find the opening bracket
                while start_pos < len(code) and code[start_pos].isspace():
                    start_pos += 1

                if start_pos >= len(code) or code[start_pos] != "[":
                    continue  # No binding vector found

                # Extract the balanced bracket content
                binding_text = self._extract_balanced_brackets(code, start_pos)

                if not binding_text:
                    continue

                # Remove the outer brackets to get just the content
                binding_content = binding_text[1:-1]  # Remove [ and ]

                # Analyze the binding patterns
                destructuring_info = self._analyze_binding_patterns(
                    binding_content, context_type
                )

                if destructuring_info:
                    # Calculate line numbers
                    start_line = code[:start_pos].count("\n") + 1

                    for pattern_info in destructuring_info:
                        pattern_info.update(
                            {
                                "context": context_type,
                                "start_line": start_line,
                                "full_binding": binding_content,
                            }
                        )
                        patterns.append(pattern_info)

        return patterns

    def _extract_balanced_brackets(self, code: str, start_pos: int) -> Optional[str]:
        """Extract balanced bracket content starting from the given position."""
        if start_pos >= len(code) or code[start_pos] != "[":
            return None

        bracket_count = 0
        end_pos = start_pos

        for i in range(start_pos, len(code)):
            char = code[i]
            if char == "[":
                bracket_count += 1
            elif char == "]":
                bracket_count -= 1
                if bracket_count == 0:
                    end_pos = i + 1
                    break

        if bracket_count == 0:
            return code[start_pos:end_pos]
        else:
            return None  # Unbalanced brackets

    def _analyze_binding_patterns(
        self, binding_text: str, context_type: str
    ) -> List[Dict[str, Any]]:
        """
        Analyze individual binding patterns for destructuring.

        Args:
            binding_text: The binding vector content
            context_type: The context where this binding occurs

        Returns:
            List of pattern analysis dictionaries
        """
        import re

        patterns = []

        # Map destructuring: {:keys [a b c] :or {a 1} :as all}
        map_destructuring = re.findall(
            r"\{[^}]*:keys\s+\[([^\]]+)\][^}]*\}", binding_text
        )
        for keys_match in map_destructuring:
            keys = [key.strip() for key in re.split(r"\s+", keys_match) if key.strip()]
            patterns.append(
                {
                    "type": "map_destructuring",
                    "pattern": "keys",
                    "extracted_vars": keys,
                    "complexity": len(keys),
                }
            )

        # Map destructuring with :strs or :syms
        strs_destructuring = re.findall(
            r"\{[^}]*:strs\s+\[([^\]]+)\][^}]*\}", binding_text
        )
        for strs_match in strs_destructuring:
            strs = [s.strip() for s in re.split(r"\s+", strs_match) if s.strip()]
            patterns.append(
                {
                    "type": "map_destructuring",
                    "pattern": "strs",
                    "extracted_vars": strs,
                    "complexity": len(strs),
                }
            )

        syms_destructuring = re.findall(
            r"\{[^}]*:syms\s+\[([^\]]+)\][^}]*\}", binding_text
        )
        for syms_match in syms_destructuring:
            syms = [s.strip() for s in re.split(r"\s+", syms_match) if s.strip()]
            patterns.append(
                {
                    "type": "map_destructuring",
                    "pattern": "syms",
                    "extracted_vars": syms,
                    "complexity": len(syms),
                }
            )

        # Vector destructuring: [a b & rest] or [a b :as all]
        vector_destructuring = re.findall(r"\[([^\]]+)\]", binding_text)
        for vec_match in vector_destructuring:
            # Skip if this looks like a map keys vector (already handled above)
            if ":keys" in vec_match or ":strs" in vec_match or ":syms" in vec_match:
                continue

            elements = [
                elem.strip() for elem in re.split(r"\s+", vec_match) if elem.strip()
            ]

            # Analyze vector pattern
            has_rest = "&" in elements
            has_as = ":as" in elements

            # Count actual variable bindings (excluding & and :as keywords)
            vars_count = len([e for e in elements if e not in ["&", ":as"]])

            patterns.append(
                {
                    "type": "vector_destructuring",
                    "pattern": "sequential",
                    "extracted_vars": [e for e in elements if e not in ["&", ":as"]],
                    "has_rest": has_rest,
                    "has_as": has_as,
                    "complexity": vars_count,
                }
            )

        # Nested destructuring detection
        for pattern in patterns:
            # Check for nested patterns by looking for additional {} or [] within the binding
            if "{" in binding_text and "[" in binding_text:
                pattern["nested"] = True
                pattern["complexity"] += 1

        return patterns

    def find_destructuring_patterns(
        self, code: str, pattern_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find specific types of destructuring patterns.

        Args:
            code: Clojure source code
            pattern_type: Optional filter for pattern type ('map_destructuring', 'vector_destructuring')

        Returns:
            List of filtered destructuring pattern dictionaries
        """
        all_patterns = self.analyze_destructuring_patterns(code)

        if pattern_type:
            return [p for p in all_patterns if p["type"] == pattern_type]

        return all_patterns

    def get_destructuring_complexity(self, code: str) -> Dict[str, Any]:
        """
        Analyze the overall destructuring complexity in code.

        Args:
            code: Clojure source code

        Returns:
            Dictionary with complexity metrics
        """
        patterns = self.analyze_destructuring_patterns(code)

        total_patterns = len(patterns)
        map_patterns = len([p for p in patterns if p["type"] == "map_destructuring"])
        vector_patterns = len(
            [p for p in patterns if p["type"] == "vector_destructuring"]
        )
        nested_patterns = len([p for p in patterns if p.get("nested", False)])

        avg_complexity = (
            sum(p["complexity"] for p in patterns) / total_patterns
            if total_patterns > 0
            else 0
        )
        max_complexity = max(p["complexity"] for p in patterns) if patterns else 0

        return {
            "total_patterns": total_patterns,
            "map_destructuring": map_patterns,
            "vector_destructuring": vector_patterns,
            "nested_patterns": nested_patterns,
            "average_complexity": round(avg_complexity, 2),
            "max_complexity": max_complexity,
            "contexts": list(set(p["context"] for p in patterns)),
        }

    def find_async_patterns(
        self, code: str, pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find core.async patterns in Clojure code.

        Args:
            code: Clojure source code
            pattern: Optional regex pattern to filter patterns

        Returns:
            List of core.async pattern information dictionaries
        """
        import re

        patterns = []

        # Define core.async patterns
        async_patterns = [
            # Go blocks and loops
            (r"\(\s*(go)\s+", "go_block"),
            (r"\(\s*(go-loop)\s+", "go_loop"),
            # Channel operations
            (r"\(\s*(chan)\s*", "channel_creation"),
            (r"\(\s*(buffer)\s+", "buffer_creation"),
            (r"\(\s*(dropping-buffer)\s+", "dropping_buffer"),
            (r"\(\s*(sliding-buffer)\s+", "sliding_buffer"),
            (r"\(\s*(>!)\s+", "channel_put_blocking"),
            (r"\(\s*(>!!)\s+", "channel_put_blocking_sync"),
            (r"\(\s*(<!)\s+", "channel_take_blocking"),
            (r"\(\s*(<!!)\s+", "channel_take_blocking_sync"),
            (r"\(\s*(alt!)\s+", "alt_blocking"),
            (r"\(\s*(alts!)\s+", "alts_blocking"),
            (r"\(\s*(alt!!)\s+", "alt_blocking_sync"),
            (r"\(\s*(alts!!)\s+", "alts_blocking_sync"),
            # Channel utilities
            (r"\(\s*(close!)\s+", "channel_close"),
            (r"\(\s*(pipe)\s+", "channel_pipe"),
            (r"\(\s*(split)\s+", "channel_split"),
            (r"\(\s*(mult)\s+", "channel_mult"),
            (r"\(\s*(tap)\s+", "channel_tap"),
            (r"\(\s*(untap)\s+", "channel_untap"),
            (r"\(\s*(pub)\s+", "channel_pub"),
            (r"\(\s*(sub)\s+", "channel_sub"),
            (r"\(\s*(unsub)\s+", "channel_unsub"),
            # Threading and coordination
            (r"\(\s*(thread)\s+", "thread_block"),
            (r"\(\s*(timeout)\s+", "timeout_channel"),
            (r"\(\s*(onto-chan)\s+", "onto_chan"),
            (r"\(\s*(to-chan)\s+", "to_chan"),
            (r"\(\s*(reduce)\s+", "channel_reduce"),
            (r"\(\s*(transduce)\s+", "channel_transduce"),
        ]

        for pattern_regex, pattern_type in async_patterns:
            for match in re.finditer(pattern_regex, code):
                start_pos = match.start()

                # If pattern filter is specified, check if this matches
                if pattern and not re.match(pattern, pattern_type):
                    continue

                # Find the end of this async construct by counting parentheses
                paren_count = 0
                end_pos = start_pos

                for j in range(start_pos, len(code)):
                    char = code[j]
                    if char == "(":
                        paren_count += 1
                    elif char == ")":
                        paren_count -= 1
                        if paren_count == 0:  # Found matching closing paren
                            end_pos = j + 1
                            break

                # Extract the complete async construct
                construct_text = code[start_pos:end_pos]

                # Categorize the pattern
                category = self._categorize_async_pattern(pattern_type)

                pattern_info = {
                    "pattern_type": pattern_type,
                    "category": category,
                    "definition": construct_text,
                    "start_byte": start_pos,
                    "end_byte": end_pos,
                    "start_line": code[:start_pos].count("\n") + 1,
                    "end_line": code[:start_pos].count("\n")
                    + 1
                    + construct_text.count("\n"),
                }

                patterns.append(pattern_info)

        return patterns

    def _categorize_async_pattern(self, pattern_type: str) -> str:
        """Categorize core.async patterns into logical groups."""

        if pattern_type in ["go_block", "go_loop"]:
            return "async_blocks"
        elif pattern_type in [
            "channel_creation",
            "buffer_creation",
            "dropping_buffer",
            "sliding_buffer",
        ]:
            return "channel_creation"
        elif pattern_type in [
            "channel_put_blocking",
            "channel_put_blocking_sync",
            "channel_take_blocking",
            "channel_take_blocking_sync",
        ]:
            return "channel_io"
        elif pattern_type in [
            "alt_blocking",
            "alts_blocking",
            "alt_blocking_sync",
            "alts_blocking_sync",
        ]:
            return "channel_selection"
        elif pattern_type in [
            "channel_close",
            "channel_pipe",
            "channel_split",
            "channel_mult",
            "channel_tap",
            "channel_untap",
            "channel_pub",
            "channel_sub",
            "channel_unsub",
        ]:
            return "channel_utilities"
        elif pattern_type in [
            "thread_block",
            "timeout_channel",
            "onto_chan",
            "to_chan",
            "channel_reduce",
            "channel_transduce",
        ]:
            return "coordination_utilities"
        else:
            return "other"

    def find_go_blocks(self, code: str) -> List[Dict[str, Any]]:
        """
        Find go blocks and go-loops specifically.

        Args:
            code: Clojure source code

        Returns:
            List of go block information dictionaries
        """
        all_patterns = self.find_async_patterns(code)
        return [p for p in all_patterns if p["category"] == "async_blocks"]

    def find_channel_operations(self, code: str) -> List[Dict[str, Any]]:
        """
        Find channel operations (creation, I/O, utilities).

        Args:
            code: Clojure source code

        Returns:
            List of channel operation information dictionaries
        """
        all_patterns = self.find_async_patterns(code)
        return [
            p
            for p in all_patterns
            if p["category"]
            in [
                "channel_creation",
                "channel_io",
                "channel_selection",
                "channel_utilities",
            ]
        ]

    def get_async_complexity(self, code: str) -> Dict[str, Any]:
        """
        Analyze the overall core.async complexity in code.

        Args:
            code: Clojure source code

        Returns:
            Dictionary with async complexity metrics
        """
        patterns = self.find_async_patterns(code)

        total_patterns = len(patterns)
        if total_patterns == 0:
            return {
                "total_patterns": 0,
                "categories": {},
                "has_async": False,
                "complexity_score": 0,
            }

        # Count by category
        categories = {}
        for pattern in patterns:
            category = pattern["category"]
            if category not in categories:
                categories[category] = 0
            categories[category] += 1

        # Calculate complexity score based on async constructs
        complexity_weights = {
            "async_blocks": 3,  # go blocks are complex
            "channel_creation": 2,  # channel creation is moderate
            "channel_io": 2,  # I/O operations are moderate
            "channel_selection": 4,  # alt/alts are complex
            "channel_utilities": 1,  # utilities are simple
            "coordination_utilities": 2,  # coordination is moderate
        }

        complexity_score = sum(
            categories.get(cat, 0) * weight
            for cat, weight in complexity_weights.items()
        )

        return {
            "total_patterns": total_patterns,
            "categories": categories,
            "has_async": True,
            "complexity_score": complexity_score,
            "async_intensity": round(complexity_score / max(1, total_patterns), 2),
            "pattern_types": list(set(p["pattern_type"] for p in patterns)),
        }

    def find_atom_operations(
        self, code: str, pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find atom and state management operations in Clojure code.

        Args:
            code: Clojure source code
            pattern: Optional regex pattern to filter operations

        Returns:
            List of atom operation information dictionaries
        """
        import re

        operations = []

        # Define atom and state management patterns
        state_patterns = [
            # Atom operations
            (r"\(\s*(atom)\s+", "atom_creation"),
            (r"\(\s*(swap!)\s+", "atom_swap"),
            (r"\(\s*(reset!)\s+", "atom_reset"),
            (r"\(\s*(compare-and-set!)\s+", "atom_cas"),
            # Ref operations (STM)
            (r"\(\s*(ref)\s+", "ref_creation"),
            (r"\(\s*(alter)\s+", "ref_alter"),
            (r"\(\s*(ref-set)\s+", "ref_set"),
            (r"\(\s*(commute)\s+", "ref_commute"),
            (r"\(\s*(ensure)\s+", "ref_ensure"),
            (r"\(\s*(dosync)\s+", "stm_transaction"),
            # Agent operations
            (r"\(\s*(agent)\s+", "agent_creation"),
            (r"\(\s*(send)\s+", "agent_send"),
            (r"\(\s*(send-off)\s+", "agent_send_off"),
            (r"\(\s*(await)\s+", "agent_await"),
            (r"\(\s*(await-for)\s+", "agent_await_for"),
            (r"\(\s*(agent-error)\s+", "agent_error"),
            (r"\(\s*(restart-agent)\s+", "agent_restart"),
            (r"\(\s*(set-error-handler!)\s+", "agent_error_handler"),
            (r"\(\s*(set-error-mode!)\s+", "agent_error_mode"),
            # Var operations
            (r"\(\s*(def)\s+", "var_definition"),
            (r"\(\s*(defonce)\s+", "var_defonce"),
            (r"\(\s*(declare)\s+", "var_declare"),
            (r"\(\s*(alter-var-root)\s+", "var_alter"),
            (r"\(\s*(with-redefs)\s+", "var_rebind_temp"),
            (r"\(\s*(binding)\s+", "var_binding"),
            # Volatile operations (for performance-critical cases)
            (r"\(\s*(volatile!)\s+", "volatile_creation"),
            (r"\(\s*(vreset!)\s+", "volatile_reset"),
            (r"\(\s*(vswap!)\s+", "volatile_swap"),
            # Delay and promise operations
            (r"\(\s*(delay)\s+", "delay_creation"),
            (r"\(\s*(force)\s+", "delay_force"),
            (r"\(\s*(promise)\s+", "promise_creation"),
            (r"\(\s*(deliver)\s+", "promise_deliver"),
            # Transient operations (for performance)
            (r"\(\s*(transient)\s+", "transient_creation"),
            (r"\(\s*(persistent!)\s+", "transient_persist"),
            (r"\(\s*(conj!)\s+", "transient_conj"),
            (r"\(\s*(assoc!)\s+", "transient_assoc"),
            (r"\(\s*(dissoc!)\s+", "transient_dissoc"),
        ]

        for pattern_regex, operation_type in state_patterns:
            for match in re.finditer(pattern_regex, code):
                start_pos = match.start()

                # If pattern filter is specified, check if this matches
                if pattern and not re.match(pattern, operation_type):
                    continue

                # Find the end of this operation by counting parentheses
                paren_count = 0
                end_pos = start_pos

                for j in range(start_pos, len(code)):
                    char = code[j]
                    if char == "(":
                        paren_count += 1
                    elif char == ")":
                        paren_count -= 1
                        if paren_count == 0:  # Found matching closing paren
                            end_pos = j + 1
                            break

                # Extract the complete operation
                operation_text = code[start_pos:end_pos]

                # Categorize the operation
                category = self._categorize_state_operation(operation_type)

                operation_info = {
                    "operation_type": operation_type,
                    "category": category,
                    "definition": operation_text,
                    "start_byte": start_pos,
                    "end_byte": end_pos,
                    "start_line": code[:start_pos].count("\n") + 1,
                    "end_line": code[:start_pos].count("\n")
                    + 1
                    + operation_text.count("\n"),
                    "is_mutation": self._is_mutating_operation(operation_type),
                }

                operations.append(operation_info)

        return operations

    def _categorize_state_operation(self, operation_type: str) -> str:
        """Categorize state operations into logical groups."""

        if operation_type in ["atom_creation", "atom_swap", "atom_reset", "atom_cas"]:
            return "atoms"
        elif operation_type in [
            "ref_creation",
            "ref_alter",
            "ref_set",
            "ref_commute",
            "ref_ensure",
            "stm_transaction",
        ]:
            return "refs_stm"
        elif operation_type in [
            "agent_creation",
            "agent_send",
            "agent_send_off",
            "agent_await",
            "agent_await_for",
            "agent_error",
            "agent_restart",
            "agent_error_handler",
            "agent_error_mode",
        ]:
            return "agents"
        elif operation_type in [
            "var_definition",
            "var_defonce",
            "var_declare",
            "var_alter",
            "var_rebind_temp",
            "var_binding",
        ]:
            return "vars"
        elif operation_type in ["volatile_creation", "volatile_reset", "volatile_swap"]:
            return "volatiles"
        elif operation_type in [
            "delay_creation",
            "delay_force",
            "promise_creation",
            "promise_deliver",
        ]:
            return "delays_promises"
        elif operation_type in [
            "transient_creation",
            "transient_persist",
            "transient_conj",
            "transient_assoc",
            "transient_dissoc",
        ]:
            return "transients"
        else:
            return "other"

    def _is_mutating_operation(self, operation_type: str) -> bool:
        """Check if an operation mutates state."""
        mutating_ops = {
            "atom_swap",
            "atom_reset",
            "atom_cas",
            "ref_alter",
            "ref_set",
            "ref_commute",
            "agent_send",
            "agent_send_off",
            "agent_restart",
            "var_alter",
            "volatile_reset",
            "volatile_swap",
            "promise_deliver",
            "transient_conj",
            "transient_assoc",
            "transient_dissoc",
        }
        return operation_type in mutating_ops

    def find_atoms(self, code: str) -> List[Dict[str, Any]]:
        """
        Find atom operations specifically.

        Args:
            code: Clojure source code

        Returns:
            List of atom operation information dictionaries
        """
        all_operations = self.find_atom_operations(code)
        return [op for op in all_operations if op["category"] == "atoms"]

    def find_state_mutations(self, code: str) -> List[Dict[str, Any]]:
        """
        Find all state-mutating operations.

        Args:
            code: Clojure source code

        Returns:
            List of mutating operation information dictionaries
        """
        all_operations = self.find_atom_operations(code)
        return [op for op in all_operations if op["is_mutation"]]

    def get_state_complexity(self, code: str) -> Dict[str, Any]:
        """
        Analyze the overall state management complexity in code.

        Args:
            code: Clojure source code

        Returns:
            Dictionary with state complexity metrics
        """
        operations = self.find_atom_operations(code)

        total_operations = len(operations)
        if total_operations == 0:
            return {
                "total_operations": 0,
                "categories": {},
                "has_state_management": False,
                "mutation_ratio": 0,
                "complexity_score": 0,
            }

        # Count by category
        categories = {}
        mutations = 0

        for op in operations:
            category = op["category"]
            if category not in categories:
                categories[category] = 0
            categories[category] += 1

            if op["is_mutation"]:
                mutations += 1

        # Calculate complexity score based on state management constructs
        complexity_weights = {
            "atoms": 2,  # atoms are moderate complexity
            "refs_stm": 4,  # STM is complex
            "agents": 3,  # agents are moderately complex
            "vars": 1,  # vars are simple
            "volatiles": 2,  # volatiles are moderate
            "delays_promises": 2,  # delays/promises are moderate
            "transients": 1,  # transients are simple performance optimizations
        }

        complexity_score = sum(
            categories.get(cat, 0) * weight
            for cat, weight in complexity_weights.items()
        )

        mutation_ratio = mutations / total_operations if total_operations > 0 else 0

        return {
            "total_operations": total_operations,
            "categories": categories,
            "has_state_management": True,
            "mutations": mutations,
            "mutation_ratio": round(mutation_ratio, 2),
            "complexity_score": complexity_score,
            "state_intensity": round(complexity_score / max(1, total_operations), 2),
            "operation_types": list(set(op["operation_type"] for op in operations)),
        }

    def analyze_sexpression(self, code: str, line: int, column: int) -> Dict[str, Any]:
        """
        Comprehensive analysis of the s-expression at cursor position.

        This is a high-level MCP function that combines multiple analysis capabilities
        to provide rich contextual information about the code at a specific location.

        Args:
            code: Clojure source code
            line: Line number (1-based)
            column: Column number (0-based)

        Returns:
            Dictionary with comprehensive s-expression analysis
        """
        analysis = {
            "position": {"line": line, "column": column},
            "sexpression": None,
            "context": None,
            "semantic_info": {},
            "navigation": {},
            "patterns": [],
            "suggestions": [],
        }

        try:
            # 1. Find the s-expression at the position
            sexp = self.find_sexp_at_position(code, line, column)
            if not sexp:
                analysis["error"] = "No s-expression found at position"
                return analysis

            analysis["sexpression"] = {
                "type": sexp["type"],
                "text": sexp["text"],
                "start_line": sexp["start_line"],
                "end_line": sexp["end_line"],
                "depth": sexp["depth"],
            }

            # 2. Determine context type
            context = self._determine_sexp_context(code, sexp, line, column)
            analysis["context"] = context

            # 3. Gather semantic information based on context
            semantic_info = self._gather_semantic_info(code, sexp, context)
            analysis["semantic_info"] = semantic_info

            # 4. Provide navigation options
            navigation = self._get_navigation_options(code, line, column)
            analysis["navigation"] = navigation

            # 5. Detect patterns in the current s-expression
            patterns = self._detect_patterns_in_sexp(sexp["text"])
            analysis["patterns"] = patterns

            # 6. Generate contextual suggestions
            suggestions = self._generate_suggestions(context, semantic_info, patterns)
            analysis["suggestions"] = suggestions

        except Exception as e:
            logger.error(f"Error in analyze_sexpression: {e}")
            analysis["error"] = str(e)

        return analysis

    def _determine_sexp_context(
        self, code: str, sexp: Dict[str, Any], line: int, column: int
    ) -> Dict[str, Any]:
        """Determine the context of the s-expression (function call, definition, etc.)."""

        sexp_text = sexp["text"].strip()
        context = {"type": "unknown", "details": {}}

        # Check if it's a function definition
        if sexp_text.startswith("(defn") or sexp_text.startswith("(defn-"):
            context["type"] = "function_definition"
            # Extract function name
            import re

            match = re.search(r"\(defn-?\s+([\w-]+)", sexp_text)
            if match:
                context["details"]["function_name"] = match.group(1)

        # Check if it's a namespace definition
        elif sexp_text.startswith("(ns "):
            context["type"] = "namespace_definition"
            import re

            match = re.search(r"\(ns\s+([\w.-]+)", sexp_text)
            if match:
                context["details"]["namespace_name"] = match.group(1)

        # Check if it's a macro definition
        elif sexp_text.startswith("(defmacro"):
            context["type"] = "macro_definition"
            import re

            match = re.search(r"\(defmacro\s+([\w-]+)", sexp_text)
            if match:
                context["details"]["macro_name"] = match.group(1)

        # Check if it's a protocol/type definition
        elif any(
            sexp_text.startswith(f"({construct}")
            for construct in ["defprotocol", "deftype", "defrecord"]
        ):
            context["type"] = "type_definition"
            import re

            for construct in ["defprotocol", "deftype", "defrecord"]:
                if sexp_text.startswith(f"({construct}"):
                    context["details"]["construct_type"] = construct
                    match = re.search(rf"\({construct}\s+([\w-]+)", sexp_text)
                    if match:
                        context["details"]["type_name"] = match.group(1)
                    break

        # Check if it's a let binding
        elif sexp_text.startswith("(let "):
            context["type"] = "let_binding"

        # Check if it's a function call
        elif sexp_text.startswith("(") and not any(
            sexp_text.startswith(f"({kw}")
            for kw in [
                "defn",
                "defn-",
                "ns",
                "defmacro",
                "defprotocol",
                "deftype",
                "defrecord",
                "let",
            ]
        ):
            context["type"] = "function_call"
            # Extract function name
            import re

            match = re.search(r"\(([^\s\(]+)", sexp_text)
            if match:
                context["details"]["function_name"] = match.group(1)

        # Check if it's a literal (vector, map, etc.)
        elif sexp_text.startswith("["):
            context["type"] = "vector_literal"
        elif sexp_text.startswith("{"):
            context["type"] = "map_literal"

        return context

    def _gather_semantic_info(
        self, code: str, sexp: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather semantic information based on the context."""

        semantic_info = {}
        sexp_text = sexp["text"]

        # For function definitions, get detailed info
        if context["type"] == "function_definition":
            functions = self.find_functions(sexp_text)
            if functions:
                func = functions[0]
                semantic_info["function"] = {
                    "name": func.get("name"),
                    "private": func.get("private", False),
                    "params": func.get("params"),
                    "docstring": func.get("docstring"),
                }

        # For namespace definitions, get imports/requires
        elif context["type"] == "namespace_definition":
            namespaces = self.find_namespaces(sexp_text)
            if namespaces:
                ns = namespaces[0]
                semantic_info["namespace"] = {
                    "name": ns.get("name"),
                    "docstring": ns.get("docstring"),
                    "requires": ns.get("requires", []),
                    "imports": ns.get("imports", []),
                }

        # Check for destructuring patterns
        destructuring = self.analyze_destructuring_patterns(sexp_text)
        if destructuring:
            semantic_info["destructuring"] = {
                "patterns": len(destructuring),
                "complexity": sum(p.get("complexity", 0) for p in destructuring),
                "types": list(set(p["type"] for p in destructuring)),
            }

        # Check for async patterns
        async_patterns = self.find_async_patterns(sexp_text)
        if async_patterns:
            semantic_info["async"] = {
                "patterns": len(async_patterns),
                "types": list(set(p["pattern_type"] for p in async_patterns)),
                "complexity_score": self.get_async_complexity(sexp_text)[
                    "complexity_score"
                ],
            }

        # Check for state management
        state_ops = self.find_atom_operations(sexp_text)
        if state_ops:
            semantic_info["state_management"] = {
                "operations": len(state_ops),
                "categories": list(set(op["category"] for op in state_ops)),
                "mutations": len([op for op in state_ops if op["is_mutation"]]),
            }

        # Check for macros
        macros = self.find_macros(sexp_text)
        if macros:
            semantic_info["macros"] = {
                "count": len(macros),
                "types": list(set(m["type"] for m in macros)),
            }

        return semantic_info

    def _get_navigation_options(
        self, code: str, line: int, column: int
    ) -> Dict[str, Any]:
        """Get available navigation options from current position."""

        navigation = {}

        # Get all possible navigation directions
        directions = ["next", "prev", "up", "down", "top"]

        for direction in directions:
            target = self.navigate_sexp(code, line, column, direction)
            if target:
                navigation[direction] = {
                    "available": True,
                    "target_line": target["start_line"],
                    "target_type": target["type"],
                    "preview": (
                        target["text"][:50] + "..."
                        if len(target["text"]) > 50
                        else target["text"]
                    ),
                }
            else:
                navigation[direction] = {"available": False}

        # Check for matching parentheses
        matching_paren = self.find_matching_paren(code, line, column)
        if matching_paren:
            navigation["matching_paren"] = {
                "available": True,
                "line": matching_paren["line"],
                "column": matching_paren["column"],
                "character": matching_paren["character"],
            }
        else:
            navigation["matching_paren"] = {"available": False}

        return navigation

    def _detect_patterns_in_sexp(self, sexp_text: str) -> List[Dict[str, Any]]:
        """Detect common Clojure patterns in the s-expression."""

        patterns = []

        # Threading macro usage
        if any(pattern in sexp_text for pattern in ["->", "->>", "some->", "cond->"]):
            patterns.append(
                {
                    "type": "threading_macro",
                    "description": "Uses threading macros for data transformation",
                }
            )

        # Destructuring usage
        if (
            "{:keys [" in sexp_text
            or "{:strs [" in sexp_text
            or "{:syms [" in sexp_text
        ):
            patterns.append(
                {
                    "type": "map_destructuring",
                    "description": "Uses map destructuring for parameter binding",
                }
            )

        # Core.async usage
        if any(
            pattern in sexp_text for pattern in ["go ", "go-loop", "<!", ">!", "chan"]
        ):
            patterns.append(
                {
                    "type": "core_async",
                    "description": "Uses core.async for concurrent programming",
                }
            )

        # State management
        if any(
            pattern in sexp_text
            for pattern in ["atom", "swap!", "reset!", "ref", "dosync"]
        ):
            patterns.append(
                {
                    "type": "state_management",
                    "description": "Manages mutable state using Clojure reference types",
                }
            )

        # Spec usage
        if any(pattern in sexp_text for pattern in ["s/def", "s/valid?", "s/conform"]):
            patterns.append(
                {
                    "type": "clojure_spec",
                    "description": "Uses clojure.spec for data validation and specification",
                }
            )

        return patterns

    def _generate_suggestions(
        self,
        context: Dict[str, Any],
        semantic_info: Dict[str, Any],
        patterns: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Generate contextual suggestions based on analysis."""

        suggestions = []

        # Suggestions based on context
        if context["type"] == "function_definition":
            if not semantic_info.get("function", {}).get("docstring"):
                suggestions.append(
                    {
                        "type": "documentation",
                        "priority": "medium",
                        "description": "Consider adding a docstring to document this function",
                    }
                )

        # Suggestions based on semantic info
        if semantic_info.get("destructuring", {}).get("complexity", 0) > 5:
            suggestions.append(
                {
                    "type": "complexity",
                    "priority": "low",
                    "description": "Complex destructuring pattern - consider breaking into smaller parts",
                }
            )

        if semantic_info.get("state_management", {}).get("mutations", 0) > 3:
            suggestions.append(
                {
                    "type": "state_management",
                    "priority": "medium",
                    "description": "Multiple state mutations - consider transaction boundaries",
                }
            )

        # Suggestions based on patterns
        for pattern in patterns:
            if pattern["type"] == "threading_macro":
                suggestions.append(
                    {
                        "type": "refactoring",
                        "priority": "low",
                        "description": "Consider if threading macro improves readability here",
                    }
                )

        return suggestions

    def trace_function_calls(
        self, code: str, target_function: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze function call relationships to build a call graph.

        Args:
            code: Clojure source code
            target_function: Optional specific function to trace (if None, trace all)

        Returns:
            Dictionary with call graph information
        """
        import re

        call_graph = {"functions": {}, "calls": [], "metrics": {}}

        try:
            # First, find all function definitions
            functions = self.find_functions(code)

            # Build function registry
            function_registry = {}
            for func in functions:
                func_name = func["name"]
                function_registry[func_name] = {
                    "definition": func,
                    "calls_made": [],
                    "called_by": [],
                    "call_count": 0,
                    "complexity_score": 0,
                }

            # If target_function specified, filter to that function
            if target_function:
                if target_function not in function_registry:
                    return {
                        "error": f'Function "{target_function}" not found',
                        "available_functions": list(function_registry.keys()),
                    }
                # Focus on the target function and its immediate relationships
                target_functions = {target_function: function_registry[target_function]}
            else:
                target_functions = function_registry

            # Analyze function calls within each function
            for func_name, func_info in target_functions.items():
                func_def = func_info["definition"]
                func_body = func_def.get("definition", "")

                # Find function calls within this function's body
                calls_found = self._extract_function_calls(func_body, function_registry)

                func_info["calls_made"] = calls_found
                func_info["call_count"] = len(calls_found)

                # Calculate complexity based on calls
                func_info["complexity_score"] = self._calculate_call_complexity(
                    calls_found, func_body
                )

                # Record the reverse relationships
                for called_func in calls_found:
                    if called_func in function_registry:
                        function_registry[called_func]["called_by"].append(func_name)

                        # Record the call edge
                        call_graph["calls"].append(
                            {
                                "caller": func_name,
                                "callee": called_func,
                                "call_type": "direct",
                                "location": {
                                    "line": func_def.get("start_line"),
                                    "function": func_name,
                                },
                            }
                        )

            # Build final call graph structure
            call_graph["functions"] = function_registry

            # Calculate metrics
            call_graph["metrics"] = self._calculate_call_graph_metrics(
                function_registry, call_graph["calls"]
            )

            # If target function specified, add specific analysis
            if target_function:
                call_graph["target_analysis"] = self._analyze_target_function(
                    target_function, function_registry, call_graph["calls"]
                )

        except Exception as e:
            logger.error(f"Error in trace_function_calls: {e}")
            call_graph["error"] = str(e)

        return call_graph

    def _extract_function_calls(
        self, func_body: str, function_registry: Dict[str, Any]
    ) -> List[str]:
        """Extract function calls from a function body."""
        import re

        calls_found = []

        # Look for function calls - pattern: (function-name ...)
        # This is a simplified approach - real implementation might use tree-sitter for better accuracy
        call_pattern = r"\(([a-zA-Z][a-zA-Z0-9_-]*)"

        for match in re.finditer(call_pattern, func_body):
            potential_func = match.group(1)

            # Skip common special forms and macros
            special_forms = {
                "let",
                "if",
                "when",
                "cond",
                "case",
                "try",
                "catch",
                "finally",
                "do",
                "loop",
                "recur",
                "fn",
                "defn",
                "defn-",
                "def",
                "defmacro",
                "quote",
                "syntax-quote",
                "unquote",
                "unquote-splicing",
                "and",
                "or",
                "not",
            }

            if potential_func in special_forms:
                continue

            # Check if it's one of our defined functions
            if potential_func in function_registry:
                calls_found.append(potential_func)
            else:
                # It might be a library function or built-in - record it anyway
                calls_found.append(potential_func)

        # Remove duplicates while preserving order
        seen = set()
        unique_calls = []
        for call in calls_found:
            if call not in seen:
                seen.add(call)
                unique_calls.append(call)

        return unique_calls

    def _calculate_call_complexity(self, calls: List[str], func_body: str) -> int:
        """Calculate complexity score based on function calls and structure."""

        complexity = len(calls)  # Base complexity from number of calls

        # Add complexity for nesting (rough approximation)
        complexity += func_body.count("(let ")  # Let bindings add complexity
        complexity += func_body.count("(if ")  # Conditionals add complexity
        complexity += func_body.count("(when ")  # Conditionals add complexity
        complexity += func_body.count("(cond ")  # Multi-branch conditionals
        complexity += func_body.count("(loop ")  # Loops add complexity

        return complexity

    def _calculate_call_graph_metrics(
        self, functions: Dict[str, Any], calls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate overall call graph metrics."""

        total_functions = len(functions)
        total_calls = len(calls)

        # Calculate degree distributions
        in_degrees = {}  # How many functions call this function
        out_degrees = {}  # How many functions this function calls

        for func_name, func_info in functions.items():
            out_degrees[func_name] = len(func_info["calls_made"])
            in_degrees[func_name] = len(func_info["called_by"])

        # Find highly connected functions
        max_in_degree = max(in_degrees.values()) if in_degrees else 0
        max_out_degree = max(out_degrees.values()) if out_degrees else 0

        highly_called = [
            func
            for func, degree in in_degrees.items()
            if degree == max_in_degree and degree > 0
        ]
        highly_calling = [
            func
            for func, degree in out_degrees.items()
            if degree == max_out_degree and degree > 0
        ]

        # Calculate complexity metrics
        total_complexity = sum(
            func_info["complexity_score"] for func_info in functions.values()
        )
        avg_complexity = (
            total_complexity / total_functions if total_functions > 0 else 0
        )

        return {
            "total_functions": total_functions,
            "total_calls": total_calls,
            "avg_calls_per_function": (
                total_calls / total_functions if total_functions > 0 else 0
            ),
            "max_in_degree": max_in_degree,
            "max_out_degree": max_out_degree,
            "highly_called_functions": highly_called,
            "highly_calling_functions": highly_calling,
            "total_complexity": total_complexity,
            "average_complexity": round(avg_complexity, 2),
            "call_density": (
                total_calls / (total_functions * total_functions)
                if total_functions > 0
                else 0
            ),
        }

    def _analyze_target_function(
        self,
        target_function: str,
        functions: Dict[str, Any],
        calls: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Provide detailed analysis for a specific target function."""

        func_info = functions[target_function]

        analysis = {
            "function_name": target_function,
            "definition_info": {
                "line": func_info["definition"].get("start_line"),
                "private": func_info["definition"].get("private", False),
                "params": func_info["definition"].get("params"),
                "docstring": func_info["definition"].get("docstring"),
            },
            "call_analysis": {
                "calls_made": len(func_info["calls_made"]),
                "called_by_count": len(func_info["called_by"]),
                "complexity_score": func_info["complexity_score"],
            },
            "relationships": {
                "calls": func_info["calls_made"],
                "called_by": func_info["called_by"],
            },
        }

        # Add call chain analysis (functions that call this function's callees)
        indirect_callers = set()
        for called_func in func_info["calls_made"]:
            if called_func in functions:
                indirect_callers.update(functions[called_func]["called_by"])

        indirect_callers.discard(target_function)  # Remove self
        analysis["relationships"]["indirect_relationships"] = list(indirect_callers)

        return analysis

    def find_function_dependencies(
        self, code: str, function_name: str
    ) -> Dict[str, Any]:
        """
        Find all dependencies of a specific function (what it calls and what calls it).

        Args:
            code: Clojure source code
            function_name: Name of function to analyze

        Returns:
            Dictionary with dependency information
        """
        call_graph = self.trace_function_calls(code, function_name)

        if "error" in call_graph:
            return call_graph

        if "target_analysis" in call_graph:
            return {
                "function": function_name,
                "dependencies": call_graph["target_analysis"],
            }

        return {"error": f'Function "{function_name}" not found in call graph'}

    def analyze_namespace_dependencies(
        self, code: str, target_namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze namespace dependencies to create a dependency map.

        Args:
            code: Clojure source code
            target_namespace: Optional specific namespace to analyze

        Returns:
            Dictionary with namespace dependency information
        """
        dependency_graph = {"namespaces": {}, "dependencies": [], "metrics": {}}

        try:
            # Find all namespaces in the code
            namespaces = self.find_namespaces(code)

            # Build namespace registry
            namespace_registry = {}

            for ns in namespaces:
                ns_name = ns["name"]

                # Parse require and import dependencies
                dependencies = self._parse_namespace_dependencies(ns)

                namespace_registry[ns_name] = {
                    "definition": ns,
                    "requires": dependencies["requires"],
                    "imports": dependencies["imports"],
                    "all_dependencies": dependencies["requires"]
                    + dependencies["imports"],
                    "dependency_count": len(dependencies["requires"])
                    + len(dependencies["imports"]),
                    "dependents": [],  # Will be filled in reverse pass
                }

            # If target namespace specified, filter analysis
            if target_namespace:
                if target_namespace not in namespace_registry:
                    return {
                        "error": f'Namespace "{target_namespace}" not found',
                        "available_namespaces": list(namespace_registry.keys()),
                    }
                target_namespaces = {
                    target_namespace: namespace_registry[target_namespace]
                }
            else:
                target_namespaces = namespace_registry

            # Build dependency edges and reverse relationships
            for ns_name, ns_info in target_namespaces.items():
                for dep in ns_info["all_dependencies"]:
                    dependency_graph["dependencies"].append(
                        {
                            "from": ns_name,
                            "to": dep,
                            "type": (
                                "require" if dep in ns_info["requires"] else "import"
                            ),
                            "namespace_line": ns_info["definition"].get("start_line"),
                        }
                    )

                    # Record reverse dependency (if the dependency is also in our registry)
                    if dep in namespace_registry:
                        namespace_registry[dep]["dependents"].append(ns_name)

            # Store the processed namespaces
            dependency_graph["namespaces"] = namespace_registry

            # Calculate metrics
            dependency_graph["metrics"] = self._calculate_namespace_metrics(
                namespace_registry, dependency_graph["dependencies"]
            )

            # If target namespace specified, add detailed analysis
            if target_namespace:
                dependency_graph["target_analysis"] = self._analyze_target_namespace(
                    target_namespace,
                    namespace_registry,
                    dependency_graph["dependencies"],
                )

        except Exception as e:
            logger.error(f"Error in analyze_namespace_dependencies: {e}")
            dependency_graph["error"] = str(e)

        return dependency_graph

    def _parse_namespace_dependencies(
        self, namespace: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Parse require and import statements from namespace definition."""

        dependencies = {"requires": [], "imports": []}

        # Parse requires
        for require_stmt in namespace.get("requires", []):
            # Extract namespace name from require statement like "[clojure.string :as str]"
            import re

            # Remove brackets and extract the namespace name (first symbol)
            cleaned = require_stmt.strip("[]")
            parts = cleaned.split()
            if parts:
                # First part is the namespace name
                ns_name = parts[0]
                dependencies["requires"].append(ns_name)

        # Parse imports
        for import_stmt in namespace.get("imports", []):
            # Extract Java class/package from import statement like "[java.util Date Calendar]"
            import re

            # Remove brackets and extract package/class info
            cleaned = import_stmt.strip("[]")
            parts = cleaned.split()
            if parts:
                # First part is typically the package
                package_name = parts[0]
                dependencies["imports"].append(package_name)

        return dependencies

    def _calculate_namespace_metrics(
        self, namespaces: Dict[str, Any], dependencies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate namespace dependency metrics."""

        total_namespaces = len(namespaces)
        total_dependencies = len(dependencies)

        if total_namespaces == 0:
            return {
                "total_namespaces": 0,
                "total_dependencies": 0,
                "avg_dependencies_per_namespace": 0,
                "dependency_density": 0,
            }

        # Calculate dependency statistics
        dependency_counts = [
            ns_info["dependency_count"] for ns_info in namespaces.values()
        ]
        dependent_counts = [
            len(ns_info["dependents"]) for ns_info in namespaces.values()
        ]

        max_dependencies = max(dependency_counts) if dependency_counts else 0
        max_dependents = max(dependent_counts) if dependent_counts else 0

        avg_dependencies = sum(dependency_counts) / total_namespaces
        avg_dependents = sum(dependent_counts) / total_namespaces

        # Find highly connected namespaces
        most_dependencies = [
            ns
            for ns, info in namespaces.items()
            if info["dependency_count"] == max_dependencies and max_dependencies > 0
        ]
        most_dependents = [
            ns
            for ns, info in namespaces.items()
            if len(info["dependents"]) == max_dependents and max_dependents > 0
        ]

        # Calculate dependency types
        requires_count = len([d for d in dependencies if d["type"] == "require"])
        imports_count = len([d for d in dependencies if d["type"] == "import"])

        return {
            "total_namespaces": total_namespaces,
            "total_dependencies": total_dependencies,
            "requires": requires_count,
            "imports": imports_count,
            "avg_dependencies_per_namespace": round(avg_dependencies, 2),
            "avg_dependents_per_namespace": round(avg_dependents, 2),
            "max_dependencies": max_dependencies,
            "max_dependents": max_dependents,
            "namespaces_with_most_dependencies": most_dependencies,
            "most_depended_upon_namespaces": most_dependents,
            "dependency_density": (
                round(total_dependencies / (total_namespaces * total_namespaces), 4)
                if total_namespaces > 0
                else 0
            ),
        }

    def _analyze_target_namespace(
        self,
        target_namespace: str,
        namespaces: Dict[str, Any],
        dependencies: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Provide detailed analysis for a specific namespace."""

        ns_info = namespaces[target_namespace]

        analysis = {
            "namespace_name": target_namespace,
            "definition_info": {
                "line": ns_info["definition"].get("start_line"),
                "docstring": ns_info["definition"].get("docstring"),
                "declaration": ns_info["definition"].get("declaration", "")[:200]
                + "...",  # Truncated
            },
            "dependency_analysis": {
                "requires_count": len(ns_info["requires"]),
                "imports_count": len(ns_info["imports"]),
                "total_dependencies": ns_info["dependency_count"],
                "dependents_count": len(ns_info["dependents"]),
            },
            "relationships": {
                "requires": ns_info["requires"],
                "imports": ns_info["imports"],
                "dependents": ns_info["dependents"],
            },
        }

        # Add dependency chain analysis (transitive dependencies)
        transitive_deps = self._find_transitive_dependencies(
            target_namespace, namespaces, max_depth=3
        )
        analysis["transitive_analysis"] = {
            "depth_1": len(ns_info["all_dependencies"]),
            "depth_2": len(transitive_deps.get("depth_2", [])),
            "depth_3": len(transitive_deps.get("depth_3", [])),
            "total_transitive": sum(len(deps) for deps in transitive_deps.values()),
        }

        return analysis

    def _find_transitive_dependencies(
        self, namespace: str, namespaces: Dict[str, Any], max_depth: int = 3
    ) -> Dict[str, List[str]]:
        """Find transitive dependencies up to a maximum depth."""

        transitive = {}
        visited = set()

        def find_deps_at_depth(ns_name: str, current_depth: int):
            if current_depth > max_depth or ns_name in visited:
                return

            visited.add(ns_name)

            if ns_name in namespaces:
                deps = namespaces[ns_name]["all_dependencies"]
                depth_key = f"depth_{current_depth}"

                if depth_key not in transitive:
                    transitive[depth_key] = []

                for dep in deps:
                    if dep not in transitive[depth_key]:
                        transitive[depth_key].append(dep)

                    # Recurse for transitive dependencies
                    find_deps_at_depth(dep, current_depth + 1)

        # Start from the target namespace
        if namespace in namespaces:
            deps = namespaces[namespace]["all_dependencies"]
            transitive["depth_1"] = deps.copy()

            for dep in deps:
                find_deps_at_depth(dep, 2)

        return transitive

    def get_namespace_dependency_tree(
        self, code: str, root_namespace: str
    ) -> Dict[str, Any]:
        """
        Get a tree representation of namespace dependencies starting from a root.

        Args:
            code: Clojure source code
            root_namespace: Starting namespace for dependency tree

        Returns:
            Dictionary with dependency tree structure
        """
        analysis = self.analyze_namespace_dependencies(code, root_namespace)

        if "error" in analysis:
            return analysis

        if "target_analysis" in analysis:
            target = analysis["target_analysis"]

            return {
                "root_namespace": root_namespace,
                "tree": {
                    "name": root_namespace,
                    "dependencies": target["relationships"]["requires"]
                    + target["relationships"]["imports"],
                    "transitive_analysis": target["transitive_analysis"],
                },
                "metadata": {
                    "total_dependencies": target["dependency_analysis"][
                        "total_dependencies"
                    ],
                    "transitive_count": target["transitive_analysis"][
                        "total_transitive"
                    ],
                },
            }

        return {"error": f"No analysis available for namespace: {root_namespace}"}

    def find_clojure_idioms(
        self, code: str, pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find common Clojure idioms and patterns in code.

        Args:
            code: Clojure source code
            pattern: Optional pattern to filter idioms

        Returns:
            List of detected idioms with their locations and descriptions
        """
        idioms = []

        try:
            # Threading macro idioms (-> and ->>)
            idioms.extend(self._find_threading_idioms(code))

            # Destructuring idioms
            idioms.extend(self._find_destructuring_idioms(code))

            # Functional programming idioms
            idioms.extend(self._find_functional_idioms(code))

            # Collection processing idioms
            idioms.extend(self._find_collection_idioms(code))

            # State management idioms
            idioms.extend(self._find_state_idioms(code))

            # Control flow idioms
            idioms.extend(self._find_control_flow_idioms(code))

            # Nil handling idioms
            idioms.extend(self._find_nil_handling_idioms(code))

            # Filter by pattern if specified
            if pattern:
                pattern_lower = pattern.lower()
                idioms = [
                    idiom
                    for idiom in idioms
                    if pattern_lower in idiom["idiom_type"].lower()
                    or pattern_lower in idiom["description"].lower()
                ]

            # Sort by line number
            idioms.sort(key=lambda x: x["start_line"])

        except Exception as e:
            logger.error(f"Error finding Clojure idioms: {e}")
            return [{"error": str(e)}]

        return idioms

    def _find_threading_idioms(self, code: str) -> List[Dict[str, Any]]:
        """Find threading macro idioms (-> ->> as-> some-> etc.)"""
        idioms = []

        # Threading first (->)
        threading_first_pattern = r"\(\s*->\s+"
        for match in re.finditer(threading_first_pattern, code, re.MULTILINE):
            start_line = code[: match.start()].count("\n") + 1

            # Extract the threading chain
            try:
                # Find the matching closing paren
                paren_count = 1
                pos = match.end()
                while pos < len(code) and paren_count > 0:
                    if code[pos] == "(":
                        paren_count += 1
                    elif code[pos] == ")":
                        paren_count -= 1
                    pos += 1

                if paren_count == 0:
                    threading_code = code[match.start() : pos]

                    # Count the steps in the threading chain
                    steps = threading_code.count("(") - 1  # Approximate step count

                    idioms.append(
                        {
                            "idiom_type": "threading_first",
                            "category": "functional",
                            "description": f"Thread-first macro with ~{steps} transformation steps",
                            "code_snippet": (
                                threading_code[:100] + "..."
                                if len(threading_code) > 100
                                else threading_code
                            ),
                            "start_line": start_line,
                            "complexity_score": min(steps * 0.5, 5.0),
                            "benefits": [
                                "Improved readability",
                                "Left-to-right data flow",
                                "Avoids nested calls",
                            ],
                            "pattern_strength": "high" if steps >= 3 else "medium",
                        }
                    )
            except:
                pass

        # Threading last (->>)
        threading_last_pattern = r"\(\s*->>\s+"
        for match in re.finditer(threading_last_pattern, code, re.MULTILINE):
            start_line = code[: match.start()].count("\n") + 1

            try:
                # Find the matching closing paren
                paren_count = 1
                pos = match.end()
                while pos < len(code) and paren_count > 0:
                    if code[pos] == "(":
                        paren_count += 1
                    elif code[pos] == ")":
                        paren_count -= 1
                    pos += 1

                if paren_count == 0:
                    threading_code = code[match.start() : pos]
                    steps = threading_code.count("(") - 1

                    idioms.append(
                        {
                            "idiom_type": "threading_last",
                            "category": "functional",
                            "description": f"Thread-last macro with ~{steps} transformation steps",
                            "code_snippet": (
                                threading_code[:100] + "..."
                                if len(threading_code) > 100
                                else threading_code
                            ),
                            "start_line": start_line,
                            "complexity_score": min(steps * 0.5, 5.0),
                            "benefits": [
                                "Collection processing",
                                "Sequence transformations",
                                "Functional composition",
                            ],
                            "pattern_strength": "high" if steps >= 3 else "medium",
                        }
                    )
            except:
                pass

        # Other threading macros
        other_threading = [
            ("some->", "threading_some", "Nil-safe threading"),
            ("some->>", "threading_some_last", "Nil-safe thread-last"),
            ("as->", "threading_as", "Named threading with binding"),
        ]

        for macro, idiom_type, description in other_threading:
            pattern = rf"\(\s*{re.escape(macro)}\s+"
            for match in re.finditer(pattern, code, re.MULTILINE):
                start_line = code[: match.start()].count("\n") + 1
                idioms.append(
                    {
                        "idiom_type": idiom_type,
                        "category": "functional",
                        "description": description,
                        "code_snippet": match.group()[:50] + "...",
                        "start_line": start_line,
                        "complexity_score": 2.0,
                        "benefits": [
                            "Nil safety",
                            "Clean error handling",
                            "Functional style",
                        ],
                        "pattern_strength": "medium",
                    }
                )

        return idioms

    def _find_destructuring_idioms(self, code: str) -> List[Dict[str, Any]]:
        """Find destructuring pattern idioms"""
        idioms = []

        # Map destructuring in let/function parameters
        map_destructuring_pattern = r"\{\s*:keys\s*\[[^\]]+\]"
        for match in re.finditer(map_destructuring_pattern, code, re.MULTILINE):
            start_line = code[: match.start()].count("\n") + 1
            keys_match = re.search(r":keys\s*\[([^\]]+)\]", match.group())

            if keys_match:
                keys = [k.strip() for k in keys_match.group(1).split() if k.strip()]

                idioms.append(
                    {
                        "idiom_type": "map_destructuring",
                        "category": "syntax",
                        "description": f'Map destructuring extracting {len(keys)} keys: {keys[:3]}{"..." if len(keys) > 3 else ""}',
                        "code_snippet": match.group(),
                        "start_line": start_line,
                        "complexity_score": min(len(keys) * 0.3, 3.0),
                        "benefits": [
                            "Clean parameter extraction",
                            "Readable function signatures",
                            "Less boilerplate",
                        ],
                        "pattern_strength": "high" if len(keys) >= 3 else "medium",
                    }
                )

        # Vector destructuring
        vector_destructuring_pattern = r"\[([^&\]]*&[^&\]]*|\[[^\]]*\][^&\]]*)\]"
        for match in re.finditer(vector_destructuring_pattern, code, re.MULTILINE):
            if "&" in match.group():  # Rest parameters
                start_line = code[: match.start()].count("\n") + 1

                idioms.append(
                    {
                        "idiom_type": "vector_destructuring_rest",
                        "category": "syntax",
                        "description": "Vector destructuring with rest parameters (&)",
                        "code_snippet": match.group(),
                        "start_line": start_line,
                        "complexity_score": 2.0,
                        "benefits": [
                            "Flexible parameter handling",
                            "Variadic functions",
                            "Clean syntax",
                        ],
                        "pattern_strength": "medium",
                    }
                )

        return idioms

    def _find_functional_idioms(self, code: str) -> List[Dict[str, Any]]:
        """Find functional programming idioms"""
        idioms = []

        # Higher-order function chains
        hof_chains = [
            ("map", "filter", "reduce"),
            ("filter", "map"),
            ("remove", "map"),
            ("map", "mapcat"),
            ("group-by", "map"),
        ]

        for chain in hof_chains:
            # Look for these functions used together
            chain_pattern = r"\(\s*" + r"\s+.*?\)\s*\(\s*".join(chain) + r"\s+"
            for match in re.finditer(chain_pattern, code, re.MULTILINE | re.DOTALL):
                start_line = code[: match.start()].count("\n") + 1

                idioms.append(
                    {
                        "idiom_type": "hof_chain",
                        "category": "functional",
                        "description": f'Higher-order function chain: {" -> ".join(chain)}',
                        "code_snippet": match.group()[:100] + "...",
                        "start_line": start_line,
                        "complexity_score": len(chain) * 0.8,
                        "benefits": [
                            "Functional composition",
                            "Data transformation",
                            "Immutable processing",
                        ],
                        "pattern_strength": "high",
                    }
                )

        # Function composition patterns
        comp_pattern = r"\(\s*comp\s+"
        for match in re.finditer(comp_pattern, code, re.MULTILINE):
            start_line = code[: match.start()].count("\n") + 1

            idioms.append(
                {
                    "idiom_type": "function_composition",
                    "category": "functional",
                    "description": "Function composition using comp",
                    "code_snippet": match.group()[:50] + "...",
                    "start_line": start_line,
                    "complexity_score": 3.0,
                    "benefits": [
                        "Reusable transformations",
                        "Mathematical composition",
                        "Clean abstractions",
                    ],
                    "pattern_strength": "high",
                }
            )

        # Partial application
        partial_pattern = r"\(\s*partial\s+"
        for match in re.finditer(partial_pattern, code, re.MULTILINE):
            start_line = code[: match.start()].count("\n") + 1

            idioms.append(
                {
                    "idiom_type": "partial_application",
                    "category": "functional",
                    "description": "Partial function application",
                    "code_snippet": match.group()[:50] + "...",
                    "start_line": start_line,
                    "complexity_score": 2.0,
                    "benefits": [
                        "Currying",
                        "Function specialization",
                        "Higher-order abstractions",
                    ],
                    "pattern_strength": "medium",
                }
            )

        return idioms

    def _find_collection_idioms(self, code: str) -> List[Dict[str, Any]]:
        """Find collection processing idioms"""
        idioms = []

        # Sequence processing patterns
        seq_patterns = [
            ("take-while", "drop-while", "conditional_sequence_processing"),
            ("partition-by", "group-by", "data_grouping"),
            ("map-indexed", "keep-indexed", "indexed_processing"),
            ("frequencies", "group-by", "data_analysis"),
        ]

        for pattern1, pattern2, idiom_name in seq_patterns:
            combined_pattern = rf"\(\s*({re.escape(pattern1)}|{re.escape(pattern2)})\s+"
            for match in re.finditer(combined_pattern, code, re.MULTILINE):
                start_line = code[: match.start()].count("\n") + 1
                func_name = match.group(1)

                idioms.append(
                    {
                        "idiom_type": idiom_name,
                        "category": "collection",
                        "description": f"Collection processing using {func_name}",
                        "code_snippet": match.group()[:50] + "...",
                        "start_line": start_line,
                        "complexity_score": 2.5,
                        "benefits": [
                            "Efficient processing",
                            "Lazy evaluation",
                            "Memory efficient",
                        ],
                        "pattern_strength": "medium",
                    }
                )

        # Transducer patterns
        transducer_pattern = r"\(\s*(map|filter|take|drop|partition)\s+[^)]*\)\s*\("
        for match in re.finditer(transducer_pattern, code, re.MULTILINE):
            start_line = code[: match.start()].count("\n") + 1

            idioms.append(
                {
                    "idiom_type": "transducer_usage",
                    "category": "collection",
                    "description": "Potential transducer usage pattern",
                    "code_snippet": match.group()[:50] + "...",
                    "start_line": start_line,
                    "complexity_score": 4.0,
                    "benefits": [
                        "Composable transformations",
                        "Performance optimization",
                        "Reusable logic",
                    ],
                    "pattern_strength": "high",
                }
            )

        return idioms

    def _find_state_idioms(self, code: str) -> List[Dict[str, Any]]:
        """Find state management idioms"""
        idioms = []

        # Update-in patterns
        update_in_pattern = r"\(\s*update-in\s+"
        for match in re.finditer(update_in_pattern, code, re.MULTILINE):
            start_line = code[: match.start()].count("\n") + 1

            idioms.append(
                {
                    "idiom_type": "nested_update",
                    "category": "state",
                    "description": "Nested data structure update with update-in",
                    "code_snippet": match.group()[:50] + "...",
                    "start_line": start_line,
                    "complexity_score": 3.0,
                    "benefits": [
                        "Immutable updates",
                        "Clean nested access",
                        "Functional state management",
                    ],
                    "pattern_strength": "high",
                }
            )

        # Assoc-in patterns
        assoc_in_pattern = r"\(\s*assoc-in\s+"
        for match in re.finditer(assoc_in_pattern, code, re.MULTILINE):
            start_line = code[: match.start()].count("\n") + 1

            idioms.append(
                {
                    "idiom_type": "nested_association",
                    "category": "state",
                    "description": "Nested data structure association with assoc-in",
                    "code_snippet": match.group()[:50] + "...",
                    "start_line": start_line,
                    "complexity_score": 2.5,
                    "benefits": [
                        "Immutable updates",
                        "Deep data access",
                        "Clean syntax",
                    ],
                    "pattern_strength": "medium",
                }
            )

        return idioms

    def _find_control_flow_idioms(self, code: str) -> List[Dict[str, Any]]:
        """Find control flow idioms"""
        idioms = []

        # When-let pattern
        when_let_pattern = r"\(\s*when-let\s+"
        for match in re.finditer(when_let_pattern, code, re.MULTILINE):
            start_line = code[: match.start()].count("\n") + 1

            idioms.append(
                {
                    "idiom_type": "conditional_binding",
                    "category": "control_flow",
                    "description": "Conditional binding with when-let",
                    "code_snippet": match.group()[:50] + "...",
                    "start_line": start_line,
                    "complexity_score": 2.0,
                    "benefits": [
                        "Nil safety",
                        "Clean conditionals",
                        "Avoid nested ifs",
                    ],
                    "pattern_strength": "high",
                }
            )

        # If-let pattern
        if_let_pattern = r"\(\s*if-let\s+"
        for match in re.finditer(if_let_pattern, code, re.MULTILINE):
            start_line = code[: match.start()].count("\n") + 1

            idioms.append(
                {
                    "idiom_type": "conditional_binding_with_else",
                    "category": "control_flow",
                    "description": "Conditional binding with if-let",
                    "code_snippet": match.group()[:50] + "...",
                    "start_line": start_line,
                    "complexity_score": 2.5,
                    "benefits": [
                        "Nil safety",
                        "Complete conditionals",
                        "Elegant error handling",
                    ],
                    "pattern_strength": "high",
                }
            )

        # Cond pattern
        cond_pattern = r"\(\s*cond\s+"
        for match in re.finditer(cond_pattern, code, re.MULTILINE):
            start_line = code[: match.start()].count("\n") + 1

            # Count the number of condition pairs
            try:
                # Rough estimate of cond branches
                cond_text = code[match.start() : match.start() + 200]  # Sample
                branch_count = cond_text.count("\n") + 1  # Approximate

                idioms.append(
                    {
                        "idiom_type": "multi_conditional",
                        "category": "control_flow",
                        "description": f"Multi-branch conditional with ~{branch_count} conditions",
                        "code_snippet": cond_text[:100] + "...",
                        "start_line": start_line,
                        "complexity_score": min(branch_count * 0.5, 5.0),
                        "benefits": [
                            "Clean multi-way branching",
                            "Avoid nested ifs",
                            "Pattern matching style",
                        ],
                        "pattern_strength": "high" if branch_count >= 4 else "medium",
                    }
                )
            except:
                pass

        return idioms

    def _find_nil_handling_idioms(self, code: str) -> List[Dict[str, Any]]:
        """Find nil handling idioms"""
        idioms = []

        # Or patterns for default values
        or_default_pattern = r"\(\s*or\s+[^)]+\s+[^)]+\)"
        for match in re.finditer(or_default_pattern, code, re.MULTILINE):
            start_line = code[: match.start()].count("\n") + 1

            idioms.append(
                {
                    "idiom_type": "default_value",
                    "category": "nil_handling",
                    "description": "Default value using or",
                    "code_snippet": match.group(),
                    "start_line": start_line,
                    "complexity_score": 1.0,
                    "benefits": ["Nil safety", "Default fallbacks", "Clean syntax"],
                    "pattern_strength": "medium",
                }
            )

        # Fnil patterns
        fnil_pattern = r"\(\s*fnil\s+"
        for match in re.finditer(fnil_pattern, code, re.MULTILINE):
            start_line = code[: match.start()].count("\n") + 1

            idioms.append(
                {
                    "idiom_type": "nil_safe_function",
                    "category": "nil_handling",
                    "description": "Nil-safe function with fnil",
                    "code_snippet": match.group()[:50] + "...",
                    "start_line": start_line,
                    "complexity_score": 2.0,
                    "benefits": [
                        "Nil safety",
                        "Function adaptation",
                        "Defensive programming",
                    ],
                    "pattern_strength": "medium",
                }
            )

        return idioms

    def get_idiom_summary(self, code: str) -> Dict[str, Any]:
        """Get a summary of all idioms found in the code."""
        idioms = self.find_clojure_idioms(code)

        if not idioms or (len(idioms) == 1 and "error" in idioms[0]):
            return {
                "total_idioms": 0,
                "categories": {},
                "complexity_score": 0,
                "idiomatic_score": 0,
                "top_patterns": [],
            }

        # Categorize idioms
        categories = {}
        complexity_scores = []

        for idiom in idioms:
            cat = idiom["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(idiom)

            if "complexity_score" in idiom:
                complexity_scores.append(idiom["complexity_score"])

        # Calculate metrics
        avg_complexity = (
            sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
        )

        # Calculate idiomatic score (higher is more idiomatic)
        high_strength_count = sum(
            1 for idiom in idioms if idiom.get("pattern_strength") == "high"
        )
        idiomatic_score = min(
            (high_strength_count * 2 + len(idioms))
            / max(len(code.split("\n")), 1)
            * 100,
            100,
        )

        # Find most common patterns
        pattern_counts = {}
        for idiom in idioms:
            pattern = idiom["idiom_type"]
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        top_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]

        return {
            "total_idioms": len(idioms),
            "categories": {
                cat: len(idioms_list) for cat, idioms_list in categories.items()
            },
            "complexity_score": round(avg_complexity, 2),
            "idiomatic_score": round(idiomatic_score, 2),
            "top_patterns": top_patterns,
            "pattern_distribution": categories,
        }

    def _calculate_depth(self, node) -> int:
        """Calculate the nesting depth of a node."""
        depth = 0
        current = node.parent
        while current and current.type != "source":
            if current.type in ["list_lit", "vec_lit", "map_lit"]:
                depth += 1
            current = current.parent
        return depth

    def _get_first_node(self, nodes):
        """Get the first node from a list or single node."""
        if isinstance(nodes, list):
            return nodes[0] if nodes else None
        return nodes

    def _extract_node_text(
        self, code: str, captures: dict, capture_name: str
    ) -> Optional[str]:
        """Safely extract text from a captured node."""
        if capture_name not in captures:
            return None

        node = self._get_first_node(captures[capture_name])
        if node is None:
            return None

        try:
            return code[node.start_byte : node.end_byte]
        except (AttributeError, IndexError):
            logger.warning(f"Failed to extract text for capture '{capture_name}'")
            return None


def find_clojure_functions(code: str, pattern: str = "tool-.*") -> List[Dict[str, Any]]:
    """
    Find Clojure functions matching a pattern.

    This is the main entry point for Phase 3 function finding.

    Args:
        code: Clojure source code
        pattern: Regex pattern to match function names (default: "tool-.*")

    Returns:
        List of function information dictionaries
    """
    analyzer = ClojureAnalyzer()
    return analyzer.find_functions(code, pattern)


if __name__ == "__main__":
    # Test with the validation codebase
    try:
        with open("/tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj", "r") as f:
            code = f.read()

        print("🔍 Testing ClojureAnalyzer")
        functions = find_clojure_functions(code)

        print(f"✅ Found {len(functions)} tool-* functions:")
        for i, func in enumerate(functions, 1):
            print(
                f"  {i:2d}. {func['name']} ({func['type']}) - line {func['start_line']}"
            )

        if len(functions) == 16:
            print("\n🎯 SUCCESS: Found exactly 16 tool-* functions!")

    except FileNotFoundError:
        print(
            "⚠️  Test file not found. Run: cp -r clj-resources/clojure-test-project /tmp/"
        )
    except Exception as e:
        print(f"❌ Error: {e}")

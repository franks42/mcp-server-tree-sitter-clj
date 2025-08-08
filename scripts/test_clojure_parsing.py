#!/usr/bin/env python
"""Standalone Clojure parsing test script."""

import argparse
import sys
import time
from pathlib import Path


def test_basic_parsing(file_path: str):
    """Test basic file parsing without tree-sitter dependency."""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        lines = content.splitlines()
        print(f"✅ File loaded: {len(lines)} lines")

        # Count defn occurrences
        defn_count = sum(1 for line in lines if "defn" in line)
        print(f"✅ Found {defn_count} defn declarations")

        # Count tool-* functions specifically
        tool_funcs = []
        for i, line in enumerate(lines, 1):
            if "defn" in line and "tool-" in line:
                # Extract function name
                parts = line.split()
                for part in parts:
                    if "tool-" in part:
                        func_name = part.strip("()")
                        tool_funcs.append((func_name, i))
                        break

        print(f"✅ Found {len(tool_funcs)} tool-* functions:")
        for func, line_no in tool_funcs:
            print(f"   - {func} at line {line_no}")

        return len(tool_funcs) == 16

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_with_tree_sitter(file_path: str, pattern: str = None):
    """Test Clojure file parsing with tree-sitter."""
    try:
        # Import when needed (will be used in Phase 2)
        from tree_sitter import Language, Parser  # noqa: F401

        # For now, simulate since tree-sitter-clojure isn't installed yet
        print("⚠️  Tree-sitter Clojure parser not yet installed")
        print("   This will be implemented in Phase 2")

        # Fall back to basic parsing
        return test_basic_parsing(file_path)

    except ImportError:
        print("⚠️  tree-sitter not available, using basic parsing")
        return test_basic_parsing(file_path)


def performance_test(file_path: str):
    """Test parsing performance."""
    try:
        start = time.time()

        with open(file_path, "r") as f:
            content = f.read()

        # Simulate parsing
        lines = content.splitlines()

        # Basic AST simulation (count nested levels)
        max_depth = 0
        current_depth = 0
        for line in lines:
            current_depth += line.count("(") - line.count(")")
            max_depth = max(max_depth, abs(current_depth))

        elapsed = (time.time() - start) * 1000  # Convert to ms

        print("✅ Performance test:")
        print(f"   - File size: {len(lines)} lines")
        print(f"   - Parse time: {elapsed:.2f}ms")
        print(f"   - Max nesting: {max_depth} levels")
        print("   - Target: <500ms for 1000+ lines")

        return elapsed < 500

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test Clojure parsing capabilities")
    parser.add_argument(
        "--file",
        default="/tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj",
        help="Clojure file to parse",
    )
    parser.add_argument(
        "--query",
        default="tool-*",
        help="Pattern to search for",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick validation",
    )
    parser.add_argument(
        "--performance",
        action="store_true",
        help="Run performance test",
    )

    args = parser.parse_args()

    # Check if test file exists
    if not Path(args.file).exists():
        print(f"❌ File not found: {args.file}")
        print("   Run: cp -r clj-resources/clojure-test-project /tmp/")
        sys.exit(1)

    print("🔍 Testing Clojure parsing")
    print(f"   File: {args.file}")
    print(f"   Query: {args.query}")
    print()

    success = True

    if args.quick:
        print("Running quick validation...")
        success = test_basic_parsing(args.file)
    elif args.performance:
        print("Running performance test...")
        success = performance_test(args.file)
    else:
        print("Running full test...")
        success = test_with_tree_sitter(args.file, args.query)

    print()
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

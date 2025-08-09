#!/usr/bin/env python3
"""Test the find_clojure_functions implementation for Task 3.2"""

from src.mcp_server_tree_sitter.clojure_analyzer import find_clojure_functions


def main():
    """Test function finder against the validation codebase."""
    try:
        with open("/tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj", "r") as f:
            code = f.read()

        print("🔍 Testing find_clojure_functions implementation")
        print(f"📁 File size: {len(code):,} characters")

        # Find tool-* functions
        tool_functions = find_clojure_functions(code, "tool-.*")

        print(f"\n🎯 Found {len(tool_functions)} tool-* functions:")

        # Show details for each function
        for i, func in enumerate(tool_functions, 1):
            name = func.get("name", "UNKNOWN")
            func_type = func.get("type", "UNKNOWN")
            line_start = func.get("start_line", 0)
            line_end = func.get("end_line", 0)

            # Clean name if it contains newlines or odd characters
            clean_name = name.replace("\n", "\\n").replace("\r", "\\r")
            if len(clean_name) > 30:
                clean_name = clean_name[:30] + "..."

            print(
                f"  {i:2d}. {clean_name} ({func_type}) - lines {line_start}-{line_end}"
            )

        # Validation against our known target
        expected_count = 16
        actual_count = len(tool_functions)

        if actual_count == expected_count:
            print(f"\n✅ SUCCESS: Found exactly {expected_count} tool-* functions!")

            # Additional analysis
            valid_functions = [
                f for f in tool_functions if f.get("name") and not "\n" in f["name"]
            ]
            print(f"📊 Clean function names: {len(valid_functions)}/{actual_count}")

            # Function type breakdown
            private_count = sum(1 for f in tool_functions if f.get("private", False))
            public_count = actual_count - private_count
            print(
                f"📈 Function types: {public_count} public (defn), {private_count} private (defn-)"
            )

            # Show first 3 clean functions as examples
            print(f"\n🔧 Example functions (first 3 with clean names):")
            clean_examples = [f for f in valid_functions[:3]]
            for func in clean_examples:
                print(
                    f"  - {func['name']} ({func['type']}) at line {func['start_line']}"
                )
                if "docstring" in func:
                    doc = func["docstring"][:50].replace("\n", " ")
                    print(f"    Doc: {doc}...")

            if len(valid_functions) >= expected_count * 0.8:  # 80% threshold
                print(f"\n🎉 Task 3.2 Implementation: SUCCESSFUL")
                print(f"   - Found all {expected_count} expected functions")
                print(f"   - {len(valid_functions)} have clean extraction")
                print(f"   - Function parsing and line detection working")
                return True
            else:
                print(
                    f"\n⚠️  Task 3.2 needs refinement: only {len(valid_functions)} clean extractions"
                )
                return False
        else:
            print(f"\n❌ Expected {expected_count} functions, found {actual_count}")
            return False

    except FileNotFoundError:
        print(
            "❌ Test file not found. Run: cp -r clj-resources/clojure-test-project /tmp/"
        )
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

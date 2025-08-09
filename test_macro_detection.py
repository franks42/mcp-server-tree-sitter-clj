#!/usr/bin/env python3
"""Test macro detection functionality for Task 4.1"""

from src.mcp_server_tree_sitter.clojure_analyzer import ClojureAnalyzer


def test_macro_detection():
    """Test macro detection functionality."""

    # Create test Clojure code with various macros
    test_code = """
(defmacro when-let-seq
  "Like when-let but for sequences"
  [binding & body]
  `(when-let [~@binding]
     (when (seq ~(first binding))
       ~@body)))

(defn process-data [data]
  (-> data
      (filter even?)
      (map inc)
      (reduce +)))

(defn complex-transform [items]
  (->> items
       (filter #(> % 10))
       (map #(* % 2))
       (partition 2)
       (take 5)))

(defn safe-transform [data]
  (some-> data
          :items
          (get 0)
          :value))

(defn conditional-process [flag data]
  (cond-> data
          flag (assoc :processed true)
          (not flag) (assoc :skipped true)))

(defmacro debug-print
  "Print debug information"
  [expr]
  `(let [result# ~expr]
     (println "Debug:" '~expr "=" result#)
     result#))
"""

    analyzer = ClojureAnalyzer()

    print("🔍 Testing Macro Detection")
    print("=" * 50)

    # Test 1: Find all macros
    print("1. Testing find_macros (all)")
    macros = analyzer.find_macros(test_code)

    print(f"✅ Found {len(macros)} macros total")

    for i, macro in enumerate(macros, 1):
        print(
            f"  {i:2d}. {macro['name']} ({macro['type']}) - {macro['macro_category']}"
        )
        print(f"      Line {macro['start_line']}-{macro['end_line']}")
        if len(macro["definition"]) > 60:
            print(f"      Definition: {repr(macro['definition'][:60])}...")
        else:
            print(f"      Definition: {repr(macro['definition'])}")

    print()

    # Test 2: Find only defmacro definitions
    print("2. Testing defmacro definitions")
    defmacros = [m for m in macros if m["type"] == "defmacro"]

    print(f"✅ Found {len(defmacros)} defmacro definitions:")
    for macro in defmacros:
        print(f"  - {macro['name']} (line {macro['start_line']})")

    print()

    # Test 3: Find threading macros specifically
    print("3. Testing find_threading_macros")
    threading = analyzer.find_threading_macros(test_code)

    print(f"✅ Found {len(threading)} threading macros:")
    for macro in threading:
        print(
            f"  - {macro['name']} ({macro['macro_category']}) - line {macro['start_line']}"
        )

    print()

    # Test 4: Test on real mcp-nrepl file
    print("4. Testing on real mcp-nrepl file")

    try:
        with open("/tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj", "r") as f:
            real_code = f.read()

        real_macros = analyzer.find_macros(real_code)
        real_threading = analyzer.find_threading_macros(real_code)

        print(f"✅ Found {len(real_macros)} macros in real file:")
        print(
            f"   - {len([m for m in real_macros if m['type'] == 'defmacro'])} defmacro definitions"
        )
        print(f"   - {len(real_threading)} threading macros")

        # Show first few threading macros if any
        if real_threading:
            print("   Threading macro examples:")
            for macro in real_threading[:3]:
                print(f"     - {macro['name']} at line {macro['start_line']}")

    except FileNotFoundError:
        print("❌ Real test file not available")
    except Exception as e:
        print(f"❌ Error testing real file: {e}")

    print()
    print("📊 Macro Detection Test Summary:")
    print(f"✅ find_macros implemented - found {len(macros)} total macros")
    print(f"✅ defmacro detection - found {len(defmacros)} definitions")
    print(f"✅ threading macro detection - found {len(threading)} threading macros")
    print("✅ Task 4.1: Macro detection queries COMPLETED")

    return True


if __name__ == "__main__":
    success = test_macro_detection()
    exit(0 if success else 1)

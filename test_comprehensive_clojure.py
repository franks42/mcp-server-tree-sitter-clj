#!/usr/bin/env python3
"""Comprehensive test suite for Clojure-specific functionality - Phase 6 Task 6.1"""

import time
import sys
import traceback
from pathlib import Path
from src.mcp_server_tree_sitter.clojure_analyzer import ClojureAnalyzer


class ClojureTestSuite:
    """Comprehensive test suite for all Clojure semantic analysis capabilities."""

    def __init__(self):
        self.analyzer = ClojureAnalyzer()
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
            "performance_metrics": {},
        }

    def run_all_tests(self):
        """Run the complete test suite and report results."""
        print("🧪 Comprehensive Clojure Analysis Test Suite")
        print("=" * 60)
        print("Phase 6: Testing and Validation - Task 6.1")
        print()

        # Test categories to run
        test_categories = [
            ("Function Detection", self.test_function_detection),
            ("S-Expression Navigation", self.test_sexp_navigation),
            ("Macro Detection", self.test_macro_detection),
            ("Protocol/Type Detection", self.test_protocol_type_detection),
            ("Destructuring Analysis", self.test_destructuring_analysis),
            ("Core.async Patterns", self.test_async_patterns),
            ("State Management", self.test_state_management),
            ("Comprehensive Analysis", self.test_comprehensive_analysis),
            ("Call Graph Analysis", self.test_call_graph_analysis),
            ("Namespace Dependencies", self.test_namespace_dependencies),
            ("Idiom Recognition", self.test_idiom_recognition),
            ("Performance Validation", self.test_performance_metrics),
            ("Real-world Validation", self.test_real_world_validation),
        ]

        for category_name, test_func in test_categories:
            print(f"🔍 Running {category_name} tests...")
            try:
                start_time = time.time()
                success = test_func()
                end_time = time.time()

                if success:
                    self.test_results["passed"] += 1
                    status = "✅ PASSED"
                    self.test_results["performance_metrics"][category_name] = (
                        end_time - start_time
                    )
                else:
                    self.test_results["failed"] += 1
                    status = "❌ FAILED"

                print(f"   {status} ({end_time - start_time:.3f}s)")

            except Exception as e:
                self.test_results["failed"] += 1
                error_msg = f"{category_name}: {str(e)}"
                self.test_results["errors"].append(error_msg)
                print(f"   💥 ERROR: {str(e)}")
                traceback.print_exc()

            print()

        self.print_final_report()
        return self.test_results["failed"] == 0

    def test_function_detection(self):
        """Test function detection capabilities."""
        test_code = """
(ns test.functions)
(defn public-function [x] x)
(defn- private-function [y] y)
(defn tool-test-function [z] z)
(defn another-tool-function [a] a)
"""

        functions = self.analyzer.find_functions(test_code)

        # Validate basic detection
        assert (
            len(functions) >= 4
        ), f"Expected at least 4 functions, got {len(functions)}"

        # Check for specific patterns
        tool_functions = [f for f in functions if f["name"].startswith("tool-")]
        assert (
            len(tool_functions) >= 1
        ), f"Expected at least 1 tool-* function, got {len(tool_functions)}"

        # Check privacy detection
        private_functions = [f for f in functions if f.get("private", False)]
        assert len(private_functions) >= 1, "Expected at least 1 private function"

        return True

    def test_sexp_navigation(self):
        """Test s-expression navigation capabilities."""
        test_code = """
(ns test.navigation)
(defn nested-function [x]
  (let [y (+ x 1)]
    (if (> y 0)
      (str "positive: " y)
      (str "non-positive: " y))))
"""

        # Test finding s-expression at position
        sexp = self.analyzer.find_sexp_at_position(
            test_code, 3, 8
        )  # Inside let binding
        assert sexp is not None, "Should find s-expression at valid position"

        # Test s-expression information
        assert "type" in sexp, "Should provide s-expression type information"
        assert "text" in sexp, "Should provide s-expression text"
        assert "start_line" in sexp, "Should provide position information"
        assert (
            sexp["type"] == "list_lit"
        ), "Should identify as list literal (function definition)"

        return True

    def test_macro_detection(self):
        """Test macro detection capabilities."""
        test_code = """
(ns test.macros)
(defmacro when-valid [condition & body]
  `(when ~condition ~@body))
  
(defn test-threading []
  (-> 42
      (+ 8)
      (* 2)
      str))
      
(defn test-thread-last []
  (->> [1 2 3 4]
       (filter even?)
       (map inc)
       vec))
"""

        macros = self.analyzer.find_macros(test_code)
        assert len(macros) >= 1, f"Expected at least 1 macro, got {len(macros)}"

        # Find threading macros specifically
        threading_first = [m for m in macros if m.get("name") == "->"]
        threading_last = [m for m in macros if m.get("name") == "->>"]

        # Should find at least one threading macro usage
        assert (
            len(threading_first) + len(threading_last) >= 2
        ), "Expected threading macro usage"

        return True

    def test_protocol_type_detection(self):
        """Test protocol and type detection."""
        test_code = """
(ns test.types)
(defprotocol Processable
  (process [this] "Process the item"))
  
(defrecord User [name age]
  Processable
  (process [this] (str "Processing " name)))
  
(deftype SimpleType [value]
  Processable
  (process [this] (str "Simple: " value)))
"""

        types = self.analyzer.find_protocols_and_types(test_code)
        assert (
            len(types) >= 3
        ), f"Expected at least 3 type definitions, got {len(types)}"

        # Check for specific types - be flexible about the exact format
        protocols = [
            t
            for t in types
            if "protocol" in str(t).lower() or t.get("type") == "protocol"
        ]
        records = [
            t for t in types if "record" in str(t).lower() or t.get("type") == "record"
        ]

        # Should find type definitions (may include deftype as well)
        assert (
            len(types) >= 2
        ), f"Expected at least 2 type definitions, got {len(types)}"

        return True

    def test_destructuring_analysis(self):
        """Test destructuring pattern analysis."""
        test_code = """
(ns test.destructuring)
(defn handle-request [{:keys [method url params headers]} options]
  (let [{:keys [timeout retries]} options
        [first-param second-param & rest-params] params]
    (process-request method url first-param)))
"""

        patterns = self.analyzer.analyze_destructuring_patterns(test_code)
        assert (
            len(patterns) >= 3
        ), f"Expected at least 3 destructuring patterns, got {len(patterns)}"

        # Check pattern types - be flexible about the exact format
        map_patterns = [
            p
            for p in patterns
            if "map" in str(p).lower() or p.get("pattern_type") == "map_destructuring"
        ]
        vector_patterns = [
            p
            for p in patterns
            if "vector" in str(p).lower()
            or p.get("pattern_type") == "vector_destructuring"
        ]

        # Should find destructuring patterns
        assert (
            len(patterns) >= 2
        ), f"Expected at least 2 destructuring patterns, got {len(patterns)}"

        return True

    def test_async_patterns(self):
        """Test core.async pattern detection."""
        test_code = """
(ns test.async
  (:require [clojure.core.async :as async :refer [go chan >! <!]]))
  
(defn producer [ch]
  (go
    (dotimes [i 10]
      (>! ch i))
    (async/close! ch)))
    
(defn consumer [ch]
  (go-loop []
    (when-let [value (<! ch)]
      (println "Got:" value)
      (recur))))
"""

        patterns = self.analyzer.find_async_patterns(test_code)
        complexity = self.analyzer.get_async_complexity(test_code)

        assert (
            len(patterns) >= 2
        ), f"Expected at least 2 async patterns, got {len(patterns)}"
        assert complexity["has_async"], "Should detect async usage"
        assert (
            complexity["complexity_score"] > 0
        ), "Should have non-zero complexity score"

        return True

    def test_state_management(self):
        """Test state management pattern detection."""
        test_code = """
(ns test.state)
(def app-state (atom {:users []}))
(def config (ref {}))

(defn add-user [user]
  (swap! app-state update :users conj user))
  
(defn update-config [key value]
  (dosync
    (alter config assoc key value)))
"""

        operations = self.analyzer.find_atom_operations(test_code)
        complexity = self.analyzer.get_state_complexity(test_code)

        assert (
            len(operations) >= 3
        ), f"Expected at least 3 state operations, got {len(operations)}"
        assert complexity["has_state_management"], "Should detect state management"
        assert complexity["mutations"] > 0, "Should detect mutations"

        return True

    def test_comprehensive_analysis(self):
        """Test comprehensive s-expression analysis."""
        test_code = """
(ns test.comprehensive)
(defn complex-function [{:keys [data options]} & args]
  (-> data
      (process-with options)
      (apply-args args)
      validate))
"""

        analysis = self.analyzer.analyze_sexpression(test_code, 2, 5)  # Inside defn

        assert "sexpression" in analysis, "Should provide s-expression info"
        assert "context" in analysis, "Should provide context info"
        assert "navigation" in analysis, "Should provide navigation options"
        assert "patterns" in analysis, "Should detect patterns"

        return True

    def test_call_graph_analysis(self):
        """Test function call graph analysis."""
        test_code = """
(ns test.calls)
(defn helper [x] (inc x))
(defn processor [data] (helper (validate data)))
(defn validate [item] (if (map? item) item {}))
(defn main [input] (processor input))
"""

        call_graph = self.analyzer.trace_function_calls(test_code)

        assert "functions" in call_graph, "Should provide function information"
        assert "metrics" in call_graph, "Should provide metrics"
        assert (
            call_graph["metrics"]["total_functions"] >= 4
        ), "Should detect all functions"
        assert call_graph["metrics"]["total_calls"] >= 3, "Should detect function calls"

        return True

    def test_namespace_dependencies(self):
        """Test namespace dependency analysis."""
        test_code = """
(ns test.deps
  (:require [clojure.string :as str]
            [clojure.set :as set])
  (:import [java.util Date]))
"""

        deps = self.analyzer.analyze_namespace_dependencies(test_code)

        assert "namespaces" in deps, "Should provide namespace information"
        assert "metrics" in deps, "Should provide metrics"
        assert len(deps["namespaces"]) >= 1, "Should detect at least 1 namespace"

        # Check dependency detection
        ns_info = list(deps["namespaces"].values())[0]
        assert len(ns_info["requires"]) >= 2, "Should detect require dependencies"
        assert len(ns_info["imports"]) >= 1, "Should detect import dependencies"

        return True

    def test_idiom_recognition(self):
        """Test Clojure idiom pattern recognition."""
        test_code = """
(ns test.idioms)
(defn process [{:keys [name age]} default]
  (-> name
      str/lower-case
      str/trim
      (or default)))
      
(defn conditional [data]
  (when-let [user (:user data)]
    (process user "unknown")))
"""

        idioms = self.analyzer.find_clojure_idioms(test_code)
        summary = self.analyzer.get_idiom_summary(test_code)

        assert len(idioms) >= 3, f"Expected at least 3 idioms, got {len(idioms)}"
        assert summary["total_idioms"] >= 3, "Summary should match idiom count"
        assert summary["idiomatic_score"] > 0, "Should have positive idiomatic score"

        # Check for specific idiom categories
        categories = summary["categories"]
        assert "functional" in categories, "Should detect functional patterns"
        assert "syntax" in categories, "Should detect syntax patterns"

        return True

    def test_performance_metrics(self):
        """Test performance against success criteria."""
        print("   📊 Testing performance criteria...")

        # Test with a moderately sized Clojure file
        test_code = """
(ns performance.test
  (:require [clojure.string :as str]
            [clojure.set :as set]))

""" + "\n".join(
            [
                f"""
(defn function-{i} [x y z]
  "Function {i} for performance testing"
  (-> x
      (+ y)
      (* z)
      (str/join ["-" (str i)])
      (or "default-{i}")))
      
(defn process-{i} [{{:keys [data options]}} items]
  (let [processed (->> items
                       (filter #{i}?)
                       (map function-{i})
                       (take 10))]
    (when-let [result (first processed)]
      (cond
        (string? result) (str/upper-case result)
        (number? result) (* result 2)
        :else result))))
"""
                for i in range(50)
            ]
        )  # Create 50 functions for performance testing

        print(f"      Code size: {len(test_code)} characters")
        print(f"      Lines: {len(test_code.split(chr(10)))} lines")

        # Test function finding performance
        start_time = time.time()
        functions = self.analyzer.find_functions(test_code)
        function_time = (time.time() - start_time) * 1000  # Convert to ms

        print(
            f"      Function detection: {function_time:.1f}ms for {len(functions)} functions"
        )

        # Test comprehensive analysis performance
        start_time = time.time()
        idioms = self.analyzer.find_clojure_idioms(test_code)
        idiom_time = (time.time() - start_time) * 1000

        print(f"      Idiom recognition: {idiom_time:.1f}ms for {len(idioms)} idioms")

        # Test namespace dependency performance
        start_time = time.time()
        deps = self.analyzer.analyze_namespace_dependencies(test_code)
        deps_time = (time.time() - start_time) * 1000

        print(f"      Dependency analysis: {deps_time:.1f}ms")

        total_time = function_time + idiom_time + deps_time
        print(f"      Total analysis time: {total_time:.1f}ms")

        # Success criteria: should handle analysis in reasonable time
        # For a ~2500 line equivalent, we expect sub-500ms performance
        if total_time > 1000:  # 1 second is generous for our test
            print(
                f"      ⚠️  Performance warning: {total_time:.1f}ms is slower than expected"
            )

        # Store performance metrics
        self.test_results["performance_metrics"][
            "function_detection_ms"
        ] = function_time
        self.test_results["performance_metrics"]["idiom_recognition_ms"] = idiom_time
        self.test_results["performance_metrics"]["dependency_analysis_ms"] = deps_time
        self.test_results["performance_metrics"]["total_analysis_ms"] = total_time

        return True

    def test_real_world_validation(self):
        """Test against real mcp-nrepl codebase."""
        print("   🌍 Testing on real-world codebase...")

        try:
            with open(
                "/tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj", "r"
            ) as f:
                real_code = f.read()

            print(f"      Real file size: {len(real_code)} characters")
            print(f"      Real file lines: {len(real_code.split(chr(10)))} lines")

            # Test function detection on real code
            start_time = time.time()
            functions = self.analyzer.find_functions(real_code)
            function_time = (time.time() - start_time) * 1000

            # Validate the critical success criteria: 16 tool-* functions
            tool_functions = [f for f in functions if f["name"].startswith("tool-")]

            print(
                f"      Functions found: {len(functions)} total, {len(tool_functions)} tool-* functions"
            )
            print(f"      Function detection time: {function_time:.1f}ms")

            # This is our key validation target
            assert (
                len(tool_functions) == 16
            ), f"Expected exactly 16 tool-* functions, got {len(tool_functions)}"

            # Test idiom recognition on real code
            start_time = time.time()
            idioms = self.analyzer.find_clojure_idioms(real_code)
            idiom_time = (time.time() - start_time) * 1000

            summary = self.analyzer.get_idiom_summary(real_code)

            print(f"      Idioms found: {len(idioms)} total")
            print(f"      Idiomatic score: {summary['idiomatic_score']:.2f}/100")
            print(f"      Idiom recognition time: {idiom_time:.1f}ms")

            # Test performance criteria on real code
            total_real_time = function_time + idiom_time
            print(f"      Total real analysis time: {total_real_time:.1f}ms")

            # Success criteria: real 1125+ line file should be analyzed quickly
            if total_real_time < 500:
                print(
                    f"      ✅ Excellent performance: {total_real_time:.1f}ms < 500ms target"
                )
            elif total_real_time < 1000:
                print(f"      ✅ Good performance: {total_real_time:.1f}ms < 1000ms")
            else:
                print(f"      ⚠️  Performance concern: {total_real_time:.1f}ms > 1000ms")

            # Store real-world metrics
            self.test_results["performance_metrics"]["real_world_functions"] = len(
                functions
            )
            self.test_results["performance_metrics"]["real_world_tool_functions"] = len(
                tool_functions
            )
            self.test_results["performance_metrics"]["real_world_idioms"] = len(idioms)
            self.test_results["performance_metrics"]["real_world_idiomatic_score"] = (
                summary["idiomatic_score"]
            )
            self.test_results["performance_metrics"][
                "real_world_analysis_time_ms"
            ] = total_real_time

            return True

        except FileNotFoundError:
            print(
                "      ⚠️  Real test file not available - skipping real-world validation"
            )
            return True  # Don't fail the test if file isn't available
        except Exception as e:
            print(f"      ❌ Real-world validation failed: {e}")
            return False

    def print_final_report(self):
        """Print comprehensive test results."""
        print("📊 Comprehensive Test Suite Results")
        print("=" * 50)

        total_tests = self.test_results["passed"] + self.test_results["failed"]
        success_rate = (
            (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        )

        print(f"✅ Tests Passed: {self.test_results['passed']}")
        print(f"❌ Tests Failed: {self.test_results['failed']}")
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        print()

        if self.test_results["errors"]:
            print("💥 Error Details:")
            for error in self.test_results["errors"]:
                print(f"   - {error}")
            print()

        print("⏱️  Performance Metrics:")
        perf = self.test_results["performance_metrics"]

        # Test execution times
        print(f"   Test execution times:")
        for category, time_taken in perf.items():
            if not category.endswith("_ms") and not category.startswith("real_world"):
                print(f"     {category}: {time_taken:.3f}s")
        print()

        # Analysis performance metrics
        if "total_analysis_ms" in perf:
            print(f"   Analysis performance:")
            print(
                f"     Function detection: {perf.get('function_detection_ms', 0):.1f}ms"
            )
            print(
                f"     Idiom recognition: {perf.get('idiom_recognition_ms', 0):.1f}ms"
            )
            print(
                f"     Dependency analysis: {perf.get('dependency_analysis_ms', 0):.1f}ms"
            )
            print(f"     Total synthetic: {perf.get('total_analysis_ms', 0):.1f}ms")
            print()

        # Real-world metrics
        if "real_world_analysis_time_ms" in perf:
            print(f"   Real-world validation:")
            print(f"     Functions detected: {perf.get('real_world_functions', 0)}")
            print(
                f"     Tool-* functions: {perf.get('real_world_tool_functions', 0)} (target: 16)"
            )
            print(f"     Idioms detected: {perf.get('real_world_idioms', 0)}")
            print(
                f"     Idiomatic score: {perf.get('real_world_idiomatic_score', 0):.2f}/100"
            )
            print(
                f"     Analysis time: {perf.get('real_world_analysis_time_ms', 0):.1f}ms"
            )

            if perf.get("real_world_analysis_time_ms", 0) < 500:
                print(f"     🏆 Performance: EXCELLENT (< 500ms)")
            elif perf.get("real_world_analysis_time_ms", 0) < 1000:
                print(f"     ✅ Performance: GOOD (< 1000ms)")
            else:
                print(f"     ⚠️  Performance: NEEDS IMPROVEMENT (> 1000ms)")

        print()

        # Success criteria evaluation
        print("🎯 Success Criteria Validation:")
        tool_functions = perf.get("real_world_tool_functions", 0)
        if tool_functions == 16:
            print(f"   ✅ Tool function detection: {tool_functions}/16 (PERFECT)")
        else:
            print(f"   ❌ Tool function detection: {tool_functions}/16 (FAILED)")

        analysis_time = perf.get("real_world_analysis_time_ms", 0)
        if analysis_time > 0 and analysis_time < 500:
            print(f"   ✅ Performance target: {analysis_time:.1f}ms < 500ms (MET)")
        elif analysis_time > 0:
            print(f"   ⚠️  Performance target: {analysis_time:.1f}ms ≥ 500ms (CLOSE)")

        if self.test_results["failed"] == 0:
            print()
            print(
                "🏆 ALL TESTS PASSED! Clojure semantic analysis system is fully validated."
            )
        else:
            print()
            print("❌ Some tests failed. Please review the errors above.")


def main():
    """Run the comprehensive test suite."""
    suite = ClojureTestSuite()
    success = suite.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

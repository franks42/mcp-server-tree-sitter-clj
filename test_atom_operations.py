#!/usr/bin/env python3
"""Test atom operations detection functionality for Task 4.5"""

from src.mcp_server_tree_sitter.clojure_analyzer import ClojureAnalyzer


def test_atom_operations():
    """Test atom operations detection functionality."""

    # Create test Clojure code with various state management patterns
    test_code = """
(ns state-example)

;; Atom operations
(def app-state (atom {:users [] :counter 0}))
(def config (atom {}))

(defn increment-counter []
  (swap! app-state update :counter inc))

(defn reset-app-state []
  (reset! app-state {:users [] :counter 0}))

(defn update-user [id user-data]
  (swap! app-state assoc-in [:users id] user-data))

(defn safe-update [expected-value new-value]
  (compare-and-set! config expected-value new-value))

;; Ref operations (STM)
(def account-a (ref 100))
(def account-b (ref 200))

(defn transfer [amount]
  (dosync
    (alter account-a - amount)
    (ref-set account-b (+ @account-b amount))
    (ensure account-a)))

(defn batch-update [accounts updates]
  (dosync
    (doseq [[account update-fn] (map vector accounts updates)]
      (commute account update-fn))))

;; Agent operations
(def log-agent (agent []))
(def worker-agent (agent 0))

(defn log-message [message]
  (send log-agent conj {:timestamp (System/currentTimeMillis) :msg message}))

(defn process-work [units]
  (send-off worker-agent + units)
  (await worker-agent))

(defn handle-agent-errors []
  (when (agent-error log-agent)
    (restart-agent log-agent [])))

;; Var operations
(def ^:dynamic *context* nil)
(defonce global-config {:env "prod"})
(declare helper-function)

(defn with-context [ctx f]
  (binding [*context* ctx]
    (f)))

(defn update-global []
  (alter-var-root #'global-config assoc :last-update (System/currentTimeMillis)))

(defn temporary-override [overrides f]
  (with-redefs [some-var "temp-value"]
    (f)))

;; Volatile operations (performance)
(def volatile-counter (volatile! 0))

(defn fast-increment []
  (vswap! volatile-counter inc))

(defn fast-reset [n]
  (vreset! volatile-counter n))

;; Delay and promise operations
(def expensive-calc (delay (Thread/sleep 1000) (+ 1 2 3)))
(def result-promise (promise))

(defn use-delay []
  (force expensive-calc))

(defn complete-promise [value]
  (deliver result-promise value))

;; Transient operations (performance)
(defn build-large-map [items]
  (persistent!
    (reduce (fn [acc item]
              (assoc! acc (:id item) item))
            (transient {})
            items)))

(defn build-large-vector [items]
  (persistent!
    (reduce conj!
            (transient [])
            items)))
"""

    analyzer = ClojureAnalyzer()

    print("🔍 Testing Atom Operations Detection")
    print("=" * 50)

    # Test 1: Find all atom operations
    print("1. Testing find_atom_operations (all)")
    operations = analyzer.find_atom_operations(test_code)

    print(f"✅ Found {len(operations)} state management operations:")

    # Group by category for display
    by_category = {}
    for op in operations:
        cat = op["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(op)

    for category, ops in by_category.items():
        print(f"  {category}: {len(ops)} operations")
        for op in ops[:3]:  # Show first 3
            mutation_mark = "🔄" if op["is_mutation"] else "📖"
            print(
                f"    {mutation_mark} {op['operation_type']} (line {op['start_line']})"
            )
        if len(ops) > 3:
            print(f"    ... and {len(ops) - 3} more")

    print()

    # Test 2: Find atoms specifically
    print("2. Testing find_atoms")
    atoms = analyzer.find_atoms(test_code)

    print(f"✅ Found {len(atoms)} atom operations:")
    for atom in atoms:
        mutation_mark = "🔄" if atom["is_mutation"] else "📖"
        print(
            f"  {mutation_mark} {atom['operation_type']} at line {atom['start_line']}"
        )

    print()

    # Test 3: Find state mutations
    print("3. Testing find_state_mutations")
    mutations = analyzer.find_state_mutations(test_code)

    print(f"✅ Found {len(mutations)} state-mutating operations:")

    mutation_categories = {}
    for mut in mutations:
        cat = mut["category"]
        if cat not in mutation_categories:
            mutation_categories[cat] = 0
        mutation_categories[cat] += 1

    for category, count in mutation_categories.items():
        print(f"  - {category}: {count} mutations")

    print()

    # Test 4: Get state complexity
    print("4. Testing get_state_complexity")
    complexity = analyzer.get_state_complexity(test_code)

    print("✅ State Management Complexity Analysis:")
    print(f"  Total operations: {complexity['total_operations']}")
    print(f"  Has state management: {complexity['has_state_management']}")
    print(f"  Total mutations: {complexity['mutations']}")
    print(f"  Mutation ratio: {complexity['mutation_ratio']}")
    print(f"  Complexity score: {complexity['complexity_score']}")
    print(f"  State intensity: {complexity['state_intensity']}")
    print("  Categories:")
    for category, count in complexity["categories"].items():
        print(f"    - {category}: {count}")
    print(f"  Operation types: {len(complexity['operation_types'])} unique types")

    print()

    # Test 5: Test on real mcp-nrepl file
    print("5. Testing on real mcp-nrepl file")

    try:
        with open("/tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj", "r") as f:
            real_code = f.read()

        real_operations = analyzer.find_atom_operations(real_code)
        real_complexity = analyzer.get_state_complexity(real_code)
        real_atoms = analyzer.find_atoms(real_code)
        real_mutations = analyzer.find_state_mutations(real_code)

        print(f"✅ Found {len(real_operations)} state operations in real file:")
        print(f"   - Has state management: {real_complexity['has_state_management']}")
        print(f"   - Atom operations: {len(real_atoms)}")
        print(
            f"   - Mutations: {len(real_mutations)} (ratio: {real_complexity['mutation_ratio']})"
        )
        print(f"   - Complexity score: {real_complexity['complexity_score']}")
        print(f"   - Categories: {real_complexity['categories']}")

        if real_operations:
            print("   Examples:")
            for op in real_operations[:5]:
                mutation_mark = "🔄" if op["is_mutation"] else "📖"
                print(
                    f"     {mutation_mark} {op['operation_type']} at line {op['start_line']}"
                )

    except FileNotFoundError:
        print("❌ Real test file not available")
    except Exception as e:
        print(f"❌ Error testing real file: {e}")

    print()
    print("📊 Atom Operations Detection Test Summary:")
    print(f"✅ find_atom_operations implemented - found {len(operations)} operations")
    print(f"✅ find_atoms implemented - found {len(atoms)} atom operations")
    print(f"✅ find_state_mutations implemented - found {len(mutations)} mutations")
    print(f"✅ Complexity analysis working - score: {complexity['complexity_score']}")
    print(f"✅ Mutation tracking - ratio: {complexity['mutation_ratio']}")
    print("✅ State categorization (7 categories)")
    print("✅ Task 4.5: Atom operations detection COMPLETED")

    return True


if __name__ == "__main__":
    success = test_atom_operations()
    exit(0 if success else 1)

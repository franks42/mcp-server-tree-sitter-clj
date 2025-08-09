#!/usr/bin/env python3
"""Concurrent analysis test for Task 6.3: Test concurrent analysis of multiple files"""

import time
import threading
import concurrent.futures
from src.mcp_server_tree_sitter.clojure_analyzer import ClojureAnalyzer


def create_test_file(file_id, lines=800):
    """Create a test Clojure file with specified line count."""

    template = f"""
(ns concurrent.test.file{file_id}
  "Concurrent testing file {file_id}"
  (:require [clojure.string :as str]
            [clojure.core.async :as async]))

;; File {file_id} functions
""" + "\n".join(
        [
            f"""
(defn function-{file_id}-{i}
  "Function {i} in file {file_id}"
  [{{:keys [data options]}} & args]
  (-> data
      (process-with options)
      (apply-to args)
      (or "default-{file_id}-{i}")))

(defn async-handler-{file_id}-{i}
  "Async processing function {i}"
  [input-ch output-ch]
  (async/go-loop []
    (when-let [item (async/<! input-ch)]
      (let [result (-> item
                      (assoc :file-id {file_id})
                      (assoc :func-id {i})
                      (update :timestamp #(or % (System/currentTimeMillis))))]
        (async/>! output-ch result))
      (recur))))

(defn complex-workflow-{file_id}-{i}
  "Complex workflow {i} with threading and destructuring"
  [requests {{:keys [timeout batch-size] :or {{timeout 5000 batch-size 10}}}}]
  (->> requests
       (filter #(contains? % :id))
       (partition batch-size)
       (mapcat (fn [batch]
                 (when-let [processed (process-batch-{file_id} batch)]
                   (some->> processed
                           (filter successful?)
                           (map #(assoc % :processed-by-file {file_id}))))))
       (take 100)
       vec))
"""
            for i in range(lines // 25)
        ]
    )  # Generate functions to reach target line count

    return template


def analyze_file_worker(file_content, file_id, results_dict, error_dict):
    """Worker function to analyze a single file."""
    try:
        analyzer = ClojureAnalyzer()

        start_time = time.time()

        # Perform comprehensive analysis
        functions = analyzer.find_functions(file_content)
        idioms = analyzer.find_clojure_idioms(file_content)
        namespaces = analyzer.find_namespaces(file_content)

        end_time = time.time()

        results_dict[file_id] = {
            "functions": len(functions),
            "idioms": len(idioms),
            "namespaces": len(namespaces),
            "analysis_time_ms": (end_time - start_time) * 1000,
            "lines": len(file_content.split("\n")),
            "chars": len(file_content),
            "success": True,
        }

    except Exception as e:
        error_dict[file_id] = {"error": str(e), "success": False}


def test_concurrent_analysis():
    """Test concurrent analysis of multiple files."""

    print("🚀 Concurrent Analysis Test - Task 6.3")
    print("Testing concurrent analysis of multiple files for performance")
    print("=" * 70)

    # Test configurations
    test_configs = [
        ("Small Scale", 3, 600),  # 3 files, ~600 lines each
        ("Medium Scale", 5, 800),  # 5 files, ~800 lines each
        ("Large Scale", 8, 1000),  # 8 files, ~1000 lines each
        ("Stress Test", 10, 1200),  # 10 files, ~1200 lines each
    ]

    overall_results = {}

    for config_name, num_files, lines_per_file in test_configs:
        print(f"\n📊 {config_name}: {num_files} files, ~{lines_per_file} lines each")
        print("-" * 50)

        # Generate test files
        test_files = {}
        total_lines = 0
        for i in range(num_files):
            file_content = create_test_file(i, lines_per_file)
            actual_lines = len(file_content.split("\n"))
            test_files[i] = file_content
            total_lines += actual_lines

        print(f"   Generated: {num_files} files, {total_lines} total lines")

        # Test 1: Sequential analysis (baseline)
        print(f"   🔄 Sequential analysis...")
        sequential_start = time.time()
        sequential_results = {}
        sequential_errors = {}

        for file_id, content in test_files.items():
            analyze_file_worker(content, file_id, sequential_results, sequential_errors)

        sequential_end = time.time()
        sequential_time = (sequential_end - sequential_start) * 1000

        print(f"      Sequential time: {sequential_time:.1f}ms")
        print(f"      Files processed: {len(sequential_results)}/{num_files}")
        if sequential_errors:
            print(f"      Errors: {len(sequential_errors)}")

        # Test 2: Concurrent analysis using ThreadPoolExecutor
        print(f"   🔀 Concurrent analysis (threads)...")
        concurrent_start = time.time()
        concurrent_results = {}
        concurrent_errors = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_files) as executor:
            futures = {}
            for file_id, content in test_files.items():
                future = executor.submit(
                    analyze_file_worker,
                    content,
                    file_id,
                    concurrent_results,
                    concurrent_errors,
                )
                futures[file_id] = future

            # Wait for all to complete
            concurrent.futures.wait(futures.values())

        concurrent_end = time.time()
        concurrent_time = (concurrent_end - concurrent_start) * 1000

        print(f"      Concurrent time: {concurrent_time:.1f}ms")
        print(f"      Files processed: {len(concurrent_results)}/{num_files}")
        if concurrent_errors:
            print(f"      Errors: {len(concurrent_errors)}")

        # Calculate performance improvement
        if sequential_time > 0:
            speedup = sequential_time / concurrent_time
            improvement = ((sequential_time - concurrent_time) / sequential_time) * 100
            print(f"      🚀 Speedup: {speedup:.2f}x ({improvement:.1f}% faster)")

        # Test 3: Analysis quality comparison
        print(f"   🔍 Validating analysis quality...")
        quality_issues = []

        for file_id in test_files.keys():
            if file_id in sequential_results and file_id in concurrent_results:
                seq_result = sequential_results[file_id]
                conc_result = concurrent_results[file_id]

                # Compare results - they should be identical
                if seq_result["functions"] != conc_result["functions"]:
                    quality_issues.append(f"File {file_id}: function count mismatch")
                if seq_result["idioms"] != conc_result["idioms"]:
                    quality_issues.append(f"File {file_id}: idiom count mismatch")
                if seq_result["namespaces"] != conc_result["namespaces"]:
                    quality_issues.append(f"File {file_id}: namespace count mismatch")

        if quality_issues:
            print(f"      ⚠️  Quality issues found:")
            for issue in quality_issues[:3]:  # Show first 3
                print(f"         - {issue}")
        else:
            print(f"      ✅ Analysis quality identical: sequential vs concurrent")

        # Store results for summary
        overall_results[config_name] = {
            "num_files": num_files,
            "total_lines": total_lines,
            "sequential_time_ms": sequential_time,
            "concurrent_time_ms": concurrent_time,
            "speedup": speedup if sequential_time > 0 else 0,
            "quality_issues": len(quality_issues),
            "files_processed": len(concurrent_results),
            "errors": len(concurrent_errors),
        }

    # Test 4: Real-world concurrent test
    print(f"\n🌍 Real-world Concurrent Test:")
    print("-" * 50)

    try:
        # Load real file multiple times (simulating multiple similar files)
        with open("/tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj", "r") as f:
            real_content = f.read()

        real_lines = len(real_content.split("\n"))
        num_real_files = 5  # Analyze 5 copies concurrently

        print(
            f"   Testing {num_real_files} copies of real file ({real_lines} lines each)"
        )

        # Sequential baseline
        real_seq_start = time.time()
        real_seq_results = {}
        real_seq_errors = {}

        for i in range(num_real_files):
            analyze_file_worker(
                real_content, f"real_{i}", real_seq_results, real_seq_errors
            )

        real_seq_time = (time.time() - real_seq_start) * 1000

        # Concurrent test
        real_conc_start = time.time()
        real_conc_results = {}
        real_conc_errors = {}

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=num_real_files
        ) as executor:
            real_futures = []
            for i in range(num_real_files):
                future = executor.submit(
                    analyze_file_worker,
                    real_content,
                    f"real_{i}",
                    real_conc_results,
                    real_conc_errors,
                )
                real_futures.append(future)

            concurrent.futures.wait(real_futures)

        real_conc_time = (time.time() - real_conc_start) * 1000

        real_speedup = real_seq_time / real_conc_time if real_conc_time > 0 else 0

        print(f"   Sequential: {real_seq_time:.1f}ms")
        print(f"   Concurrent: {real_conc_time:.1f}ms")
        print(f"   🚀 Real-world speedup: {real_speedup:.2f}x")

        # Check that we found the expected tool functions in each copy
        for i in range(num_real_files):
            file_key = f"real_{i}"
            if file_key in real_conc_results:
                # We know from previous tests this should have 43 functions
                actual_functions = real_conc_results[file_key]["functions"]
                if actual_functions != 43:
                    print(
                        f"   ⚠️  Copy {i}: Expected 43 functions, got {actual_functions}"
                    )

        overall_results["Real-world"] = {
            "num_files": num_real_files,
            "total_lines": real_lines * num_real_files,
            "sequential_time_ms": real_seq_time,
            "concurrent_time_ms": real_conc_time,
            "speedup": real_speedup,
            "files_processed": len(real_conc_results),
            "errors": len(real_conc_errors),
        }

    except Exception as e:
        print(f"   ⚠️  Could not test real file: {e}")

    # Final summary
    print(f"\n📊 Concurrent Analysis Summary:")
    print("=" * 60)

    success_count = 0
    total_tests = len(overall_results)

    for config_name, results in overall_results.items():
        speedup = results.get("speedup", 0)
        quality_issues = results.get("quality_issues", 0)
        files_processed = results.get("files_processed", 0)
        num_files = results.get("num_files", 0)

        print(f"   {config_name}:")
        print(f"      Files: {files_processed}/{num_files}")
        print(f"      Speedup: {speedup:.2f}x")
        print(f"      Quality issues: {quality_issues}")

        # Success criteria: speedup > 1.5x and no quality issues
        if speedup > 1.5 and quality_issues == 0 and files_processed == num_files:
            print(f"      Status: ✅ SUCCESS")
            success_count += 1
        elif speedup > 1.2 and quality_issues == 0:
            print(f"      Status: ⚡ GOOD")
            success_count += 1
        else:
            print(f"      Status: ❌ NEEDS IMPROVEMENT")

    print(f"\n🎯 Concurrent Analysis Results:")
    success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
    print(f"   Successful configurations: {success_count}/{total_tests}")
    print(f"   Success rate: {success_rate:.1f}%")

    if success_rate >= 80:
        print(f"   🏆 CONCURRENT ANALYSIS VALIDATED!")
        return True
    else:
        print(f"   ⚠️  CONCURRENT ANALYSIS NEEDS IMPROVEMENT")
        return False


if __name__ == "__main__":
    success = test_concurrent_analysis()
    print(f"\nTask 6.3 Concurrent Analysis: {'✅ PASSED' if success else '❌ FAILED'}")
    exit(0 if success else 1)

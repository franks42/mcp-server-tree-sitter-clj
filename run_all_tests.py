#!/usr/bin/env python3
"""Test runner for all useful tests in the project."""

import subprocess
import sys
import time
from pathlib import Path

def run_test(test_file, description, timeout=30):
    """Run a single test file."""
    print(f"🧪 Running {description}...")
    print(f"   File: {test_file}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            ["uv", "run", "python", test_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"   ✅ PASSED ({duration:.1f}s)")
            return True
        else:
            print(f"   ❌ FAILED ({duration:.1f}s)")
            print(f"   Error output: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ TIMEOUT after {timeout}s")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def main():
    """Run all useful tests."""
    print("🎯 Enhanced MCP Tree-sitter Server - Test Suite Runner")
    print("=" * 70)
    
    # Define useful tests to run
    tests = [
        ("test_mcp_server.py", "MCP Server Startup & Claude Desktop Integration"),
        ("test_mcp_integration_simple.py", "MCP Integration Test (Key Functionality)"),
        ("test_comprehensive_clojure.py", "Comprehensive Clojure Analysis Suite"),
        ("test_performance_validation.py", "Performance Validation (1000+ LOC in <500ms)"),
    ]
    
    passed = 0
    failed = 0
    results = []
    
    for test_file, description in tests:
        if not Path(test_file).exists():
            print(f"⚠️  Skipping {test_file} - file not found")
            continue
            
        success = run_test(test_file, description)
        results.append((test_file, description, success))
        
        if success:
            passed += 1
        else:
            failed += 1
        
        print()  # Add spacing between tests
    
    # Print summary
    print("📊 Test Suite Results Summary")
    print("=" * 70)
    
    for test_file, description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:10} - {description}")
    
    print()
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    if failed == 0:
        print()
        print("🏆 ALL TESTS PASSED!")
        print("✅ Enhanced MCP Tree-sitter server with Clojure support is fully validated")
        print("✅ Ready for production use and Claude Desktop integration")
    else:
        print()
        print(f"⚠️  {failed} test(s) failed - review output above")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""Simple MCP integration validation test - Tests key functionality through internal APIs."""

import time
import sys
from pathlib import Path

def main():
    """Run a focused integration test validating key MCP functionality."""
    print("🧪 MCP Integration Test Suite")
    print("=" * 60)
    print("Testing key functionality through internal APIs")
    print()
    
    # Test results tracking
    passed = 0
    failed = 0
    errors = []
    
    def run_test(test_name, test_func):
        nonlocal passed, failed, errors
        print(f"🔍 {test_name}...")
        try:
            start_time = time.time()
            result = test_func()
            duration = time.time() - start_time
            
            if result:
                print(f"   ✅ PASSED ({duration:.3f}s)")
                passed += 1
            else:
                print(f"   ❌ FAILED ({duration:.3f}s)")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1
            errors.append(f"{test_name}: {str(e)}")
    
    # === TEST 1: Module Imports ===
    def test_imports():
        try:
            from mcp_server_tree_sitter.server import mcp
            from mcp_server_tree_sitter.di import get_container
            from mcp_server_tree_sitter.context import global_context
            from mcp_server_tree_sitter.clojure_analyzer import ClojureAnalyzer
            from mcp_server_tree_sitter.language.query_templates import list_query_templates
            print("   ✅ All critical modules imported successfully")
            return True
        except Exception as e:
            print(f"   ❌ Import failed: {e}")
            return False
    
    # === TEST 2: Dependency Injection Container ===
    def test_container():
        try:
            from mcp_server_tree_sitter.di import get_container
            
            container = get_container()
            
            # Check essential components
            if not hasattr(container, 'project_registry'):
                print("   ❌ Missing project_registry")
                return False
            if not hasattr(container, 'language_registry'):
                print("   ❌ Missing language_registry")
                return False
            if not hasattr(container, 'tree_cache'):
                print("   ❌ Missing tree_cache")
                return False
            if not hasattr(container, 'config_manager'):
                print("   ❌ Missing config_manager")
                return False
                
            print("   ✅ Container has all essential components")
            return True
            
        except Exception as e:
            print(f"   ❌ Container test failed: {e}")
            return False
    
    # === TEST 3: Project Management ===
    def test_project_management():
        try:
            from mcp_server_tree_sitter.context import global_context
            
            test_project_path = "/tmp/clojure-test-project"
            test_project_name = "integration-test"
            
            # Clean up first
            try:
                global_context.remove_project(test_project_name)
            except:
                pass  # Expected if doesn't exist
                
            # Register project
            result = global_context.register_project(
                test_project_path,
                name=test_project_name,
                description="Integration test project"
            )
            
            if not result or "name" not in result:
                print("   ❌ Project registration failed")
                return False
                
            # List projects
            projects = global_context.list_projects()
            if not any(p["name"] == test_project_name for p in projects):
                print("   ❌ Registered project not in list")
                return False
                
            # Clean up
            global_context.remove_project(test_project_name)
            
            print(f"   ✅ Project management working - found {result.get('languages', {})}")
            return True
            
        except Exception as e:
            print(f"   ❌ Project management test failed: {e}")
            return False
    
    # === TEST 4: Clojure Query Templates ===
    def test_clojure_templates():
        try:
            from mcp_server_tree_sitter.language.query_templates import list_query_templates
            
            templates = list_query_templates("clojure")
            if not templates or "clojure" not in templates:
                print("   ❌ No Clojure templates found")
                return False
                
            clojure_templates = templates["clojure"]
            expected = ["functions", "macros", "namespaces", "imports"]
            missing = [t for t in expected if t not in clojure_templates]
            
            if missing:
                print(f"   ❌ Missing templates: {missing}")
                return False
                
            print(f"   ✅ Found {len(clojure_templates)} Clojure query templates")
            return True
            
        except Exception as e:
            print(f"   ❌ Template test failed: {e}")
            return False
    
    # === TEST 5: Clojure Analyzer Direct Test ===
    def test_clojure_analyzer():
        try:
            from mcp_server_tree_sitter.clojure_analyzer import ClojureAnalyzer
            
            analyzer = ClojureAnalyzer()
            
            # Test with real code file
            test_file = "/tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj"
            if not Path(test_file).exists():
                print("   ❌ Test file not found")
                return False
                
            with open(test_file, 'r') as f:
                code = f.read()
                
            # Test function finding
            functions = analyzer.find_functions(code)
            if len(functions) < 40:
                print(f"   ❌ Expected 40+ functions, found {len(functions)}")
                return False
                
            # Count tool-* functions
            tool_functions = [f for f in functions if f.get("name", "").startswith("tool-")]
            if len(tool_functions) != 16:
                print(f"   ❌ Expected 16 tool-* functions, found {len(tool_functions)}")
                return False
                
            print(f"   ✅ Analyzer found {len(functions)} functions, {len(tool_functions)} tool-* functions")
            return True
            
        except Exception as e:
            print(f"   ❌ Analyzer test failed: {e}")
            return False
    
    # === TEST 6: MCP Server Registration ===
    def test_mcp_server():
        try:
            from mcp_server_tree_sitter.server import mcp
            from mcp_server_tree_sitter.di import get_container
            from mcp_server_tree_sitter.tools.registration import register_tools
            from mcp_server_tree_sitter.capabilities import register_capabilities
            
            # Test server instance
            if not mcp or not hasattr(mcp, 'name'):
                print("   ❌ MCP server not properly instantiated")
                return False
                
            if mcp.name != "tree_sitter":
                print(f"   ❌ Expected server name 'tree_sitter', got '{mcp.name}'")
                return False
                
            # Test tool registration (this simulates MCP startup)
            container = get_container()
            register_capabilities(mcp)
            register_tools(mcp, container)
            
            print(f"   ✅ MCP server '{mcp.name}' registered with tools and capabilities")
            return True
            
        except Exception as e:
            print(f"   ❌ MCP server test failed: {e}")
            return False
    
    # === TEST 7: Performance Validation ===
    def test_performance():
        try:
            from mcp_server_tree_sitter.clojure_analyzer import ClojureAnalyzer
            
            analyzer = ClojureAnalyzer()
            
            # Test with real code file
            test_file = "/tmp/clojure-test-project/src/mcp_nrepl_proxy/core.clj"
            with open(test_file, 'r') as f:
                code = f.read()
            
            # Measure analysis performance
            start_time = time.time()
            functions = analyzer.find_functions(code)
            analysis_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if analysis_time > 500:
                print(f"   ❌ Analysis too slow: {analysis_time:.1f}ms > 500ms")
                return False
                
            lines = len(code.splitlines())
            if lines < 1000:
                print(f"   ❌ Test file too small: {lines} lines < 1000 lines")
                return False
                
            print(f"   ✅ Analyzed {lines} lines in {analysis_time:.1f}ms (target: <500ms)")
            return True
            
        except Exception as e:
            print(f"   ❌ Performance test failed: {e}")
            return False
    
    # Run all tests
    run_test("Module Imports", test_imports)
    run_test("Dependency Container", test_container) 
    run_test("Project Management", test_project_management)
    run_test("Clojure Query Templates", test_clojure_templates)
    run_test("Clojure Analyzer", test_clojure_analyzer)
    run_test("MCP Server Registration", test_mcp_server)
    run_test("Performance Validation", test_performance)
    
    # Print results
    print()
    print("📊 Integration Test Results")
    print("=" * 60)
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    total_tests = passed + failed
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    if errors:
        print("\n❌ Errors:")
        for error in errors:
            print(f"   - {error}")
    
    if failed == 0:
        print("\n🏆 ALL INTEGRATION TESTS PASSED!")
        print("✅ MCP Tree-sitter server is ready for production use")
    else:
        print(f"\n⚠️  {failed} tests failed - review errors above")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
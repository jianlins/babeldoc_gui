#!/usr/bin/env python3
"""
Test script to verify BabelDOC and dependencies are working
"""

import sys
import importlib.util

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        if package_name:
            spec = importlib.util.find_spec(module_name, package_name)
        else:
            spec = importlib.util.find_spec(module_name)
        
        if spec is None:
            return False, f"Module {module_name} not found"
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, f"✓ {module_name} imported successfully"
    except Exception as e:
        return False, f"✗ Failed to import {module_name}: {e}"

def main():
    print("PDF Translation GUI - Dependency Check")
    print("=" * 50)
    
    # Test core Python modules
    modules_to_test = [
        ("tkinter", "GUI framework"),
        ("asyncio", "Async support"),
        ("threading", "Threading support"),
        ("pathlib", "Path handling"),
        ("json", "JSON support"),
        ("logging", "Logging support"),
        ("os", "OS interface"),
        ("sys", "System interface"),
    ]
    
    print("\n1. Testing Core Python Modules:")
    all_core_passed = True
    for module, description in modules_to_test:
        success, message = test_import(module)
        print(f"   {message} ({description})")
        if not success:
            all_core_passed = False
    
    # Test external dependencies
    external_deps = [
        ("requests", "HTTP requests for Ollama"),
    ]
    
    print("\n2. Testing External Dependencies:")
    all_external_passed = True
    for module, description in external_deps:
        success, message = test_import(module)
        print(f"   {message} ({description})")
        if not success:
            all_external_passed = False
    
    # Test BabelDOC components
    babeldoc_modules = [
        ("babeldoc", "Main BabelDOC package"),
        ("babeldoc.format.pdf.high_level", "High-level PDF API"),
        ("babeldoc.format.pdf.translation_config", "Translation configuration"),
        ("babeldoc.translator.translator", "Translator classes"),
        ("babeldoc.docvision.doclayout", "Document layout model"),
    ]
    
    print("\n3. Testing BabelDOC Components:")
    all_babeldoc_passed = True
    for module, description in babeldoc_modules:
        success, message = test_import(module)
        print(f"   {message} ({description})")
        if not success:
            all_babeldoc_passed = False
    
    # Test BabelDOC initialization
    print("\n4. Testing BabelDOC Initialization:")
    try:
        import babeldoc.format.pdf.high_level
        babeldoc.format.pdf.high_level.init()
        print("   ✓ BabelDOC initialized successfully")
        babeldoc_init_passed = True
    except Exception as e:
        print(f"   ✗ BabelDOC initialization failed: {e}")
        babeldoc_init_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    
    if all_core_passed:
        print("✓ Core Python modules: OK")
    else:
        print("✗ Core Python modules: FAILED")
    
    if all_external_passed:
        print("✓ External dependencies: OK")
    else:
        print("✗ External dependencies: FAILED")
        print("  Run: pip install requests")
    
    if all_babeldoc_passed:
        print("✓ BabelDOC modules: OK")
    else:
        print("✗ BabelDOC modules: FAILED")
        print("  Make sure you're in the 'pdf' conda environment")
        print("  Run: conda activate pdf")
    
    if babeldoc_init_passed:
        print("✓ BabelDOC initialization: OK")
    else:
        print("✗ BabelDOC initialization: FAILED")
    
    overall_success = all_core_passed and all_external_passed and all_babeldoc_passed and babeldoc_init_passed
    
    if overall_success:
        print("\n🎉 All tests passed! The GUI should work correctly.")
        print("You can now run: python src/main.py")
    else:
        print("\n❌ Some tests failed. Please fix the issues before running the GUI.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

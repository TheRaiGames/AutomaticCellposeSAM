#!/usr/bin/env python3
"""
Test script to validate Cellpose installation and system compatibility
"""

import sys
import os

def test_python_version():
    """Test Python version"""
    print("Testing Python version...")
    recommended_version = (3, 13, 5)
    minimum_version = (3, 8, 0)
    current_version = sys.version_info[:3]
    
    print(f"Current Python version: {'.'.join(map(str, current_version))}")
    print(f"Recommended Python version: {'.'.join(map(str, recommended_version))}")
    
    if current_version >= recommended_version:
        print("✓ Python version optimal")
        return True
    elif current_version >= minimum_version:
        print("⚠ Python version acceptable (older than recommended)")
        return True
    else:
        print("✗ Python version too old")
        return False

def test_cellpose():
    """Test Cellpose installation"""
    print("\nTesting Cellpose installation...")
    try:
        import cellpose
        try:
            version = cellpose.__version__
            print(f"Cellpose version: {version}")
            if version.startswith("4.0"):
                print("✓ Cellpose 4.0.x installed")
            else:
                print(f"⚠ Cellpose {version} installed (4.0.x recommended)")
        except AttributeError:
            print("✓ Cellpose is installed (version detection unavailable)")
        return True
    except ImportError as e:
        print(f"✗ Cellpose not found: {e}")
        return False

def test_torch():
    """Test PyTorch installation and CUDA"""
    print("\nTesting PyTorch installation...")
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        
        # Test CUDA
        if torch.cuda.is_available():
            print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"✓ CUDA version: {torch.version.cuda}")
            return True
        else:
            print("⚠ CUDA not available (will use CPU - slower)")
            return True
    except ImportError as e:
        print(f"✗ PyTorch not found: {e}")
        return False

def test_gui_dependencies():
    """Test GUI dependencies"""
    print("\nTesting GUI dependencies...")
    try:
        import tkinter
        print("✓ tkinter available")
        return True
    except ImportError as e:
        print(f"✗ tkinter not found: {e}")
        return False

def test_numpy():
    """Test NumPy"""
    print("\nTesting NumPy...")
    try:
        import numpy as np
        print(f"NumPy version: {np.__version__}")
        print("✓ NumPy available")
        return True
    except ImportError as e:
        print(f"✗ NumPy not found: {e}")
        return False

def test_file_structure():
    """Test required files exist"""
    print("\nTesting file structure...")
    required_files = [
        "automated_cellpose_segmentation.py",
        "run_automated_cellpose.bat",
        "run_cellpose_cmdline.bat",
        "setup_environment.bat"
    ]
    
    all_found = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} found")
        else:
            print(f"✗ {file} missing")
            all_found = False
    
    return all_found

def test_folders():
    """Test example folders exist"""
    print("\nTesting folders...")
    folders = ["example_images", "output_flows"]
    
    all_found = True
    for folder in folders:
        if os.path.exists(folder):
            print(f"✓ {folder} folder exists")
        else:
            print(f"⚠ {folder} folder missing (will be created automatically)")
    
    return all_found

def main():
    """Run all tests"""
    print("=" * 60)
    print("Automated Cellpose System Validation")
    print("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Cellpose", test_cellpose),
        ("PyTorch", test_torch),
        ("GUI Dependencies", test_gui_dependencies),
        ("NumPy", test_numpy),
        ("File Structure", test_file_structure),
        ("Folders", test_folders)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<20}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n✓ All tests passed! System is ready to use.")
        print("\nTo start segmentation:")
        print("1. Place .tif images in example_images folder")
        print("2. Run: run_automated_cellpose.bat")
    else:
        print(f"\n✗ {len(results) - passed} test(s) failed. Please fix the issues above.")
        print("\nTip: Run setup_environment.bat to install missing dependencies")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
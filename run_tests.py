#!/usr/bin/env python3
"""
Quick test runner for QR Code API
"""

import subprocess
import sys
import time

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 QR Code API Test Runner")
    print("=" * 40)
    
    tests = [
        ("python3 -m py_compile src/main.py", "Syntax check - main.py"),
        ("python3 -m py_compile src/models/requests.py", "Syntax check - models"),
        ("python3 -m py_compile src/services/qr_generator.py", "Syntax check - QR generator"),
        ("python3 -m py_compile src/api/endpoints/qr.py", "Syntax check - endpoints"),
        ("python3 -c 'import qrcode; print(\"QR code library OK\")'", "Library check - qrcode"),
        ("python3 -c 'import fastapi; print(\"FastAPI library OK\")'", "Library check - FastAPI"),
        ("python3 -c 'from PIL import Image; print(\"Pillow library OK\")'", "Library check - Pillow"),
    ]
    
    passed = 0
    total = len(tests)
    
    for cmd, desc in tests:
        if run_command(cmd, desc):
            passed += 1
        print("-" * 40)
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        print("\n🚀 Next steps:")
        print("   1. Run: python3 src/main.py")
        print("   2. Open: http://localhost:8000/docs")
        print("   3. Test: python3 test_mvp.py")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

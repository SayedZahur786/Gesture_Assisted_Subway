"""
Quick test script to verify all components are working
Run this before using the full booth system
"""

def test_imports():
    """Test that all required packages are installed"""
    print("Testing imports...")
    errors = []
    
    try:
        import cv2
        print("  ✓ opencv-python")
    except ImportError as e:
        errors.append(f"  ✗ opencv-python: {e}")
    
    try:
        import mediapipe
        print("  ✓ mediapipe")
    except ImportError as e:
        errors.append(f"  ✗ mediapipe: {e}")
    
    try:
        import pyautogui
        print("  ✓ pyautogui")
    except ImportError as e:
        errors.append(f"  ✗ pyautogui: {e}")
    
    try:
        import mss
        print("  ✓ mss")
    except ImportError as e:
        errors.append(f"  ✗ mss: {e}")
    
    try:
        import pytesseract
        print("  ✓ pytesseract")
    except ImportError as e:
        errors.append(f"  ✗ pytesseract: {e}")
    
    try:
        from PIL import Image
        print("  ✓ pillow")
    except ImportError as e:
        errors.append(f"  ✗ pillow: {e}")
    
    if errors:
        print("\nMissing packages:")
        for err in errors:
            print(err)
        print("\nInstall missing packages with:")
        print("  pip install opencv-python mediapipe pyautogui mss pytesseract pillow")
        return False
    
    print("\n✓ All required packages installed!")
    return True

def test_tesseract():
    """Test if Tesseract OCR is installed and accessible"""
    print("\nTesting Tesseract OCR...")
    try:
        import pytesseract
        import config
        
        # Try to get version
        if hasattr(config, 'TESSERACT_PATH'):
            pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
        
        version = pytesseract.get_tesseract_version()
        print(f"  ✓ Tesseract OCR version {version}")
        return True
    except Exception as e:
        print(f"  ✗ Tesseract OCR not found: {e}")
        print("\n  Download and install from:")
        print("  https://github.com/UB-Mannheim/tesseract/wiki")
        print("\n  Then update TESSERACT_PATH in config.py if needed")
        return False

def test_webcam():
    """Test if webcam is accessible"""
    print("\nTesting webcam...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("  ✗ Cannot open webcam")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("  ✗ Cannot read from webcam")
            return False
        
        print("  ✓ Webcam accessible")
        return True
    except Exception as e:
        print(f"  ✗ Webcam error: {e}")
        return False

def test_config():
    """Test if configuration is valid"""
    print("\nTesting configuration...")
    try:
        import config
        
        # Check score region
        if config.SCORE_REGION['x'] == 100:
            print("  ⚠ Score region not calibrated (using defaults)")
            print("    Run: python calibrate_score_region.py")
        else:
            print("  ✓ Score region configured")
        
        # Check CSV path
        import os
        csv_dir = os.path.dirname(config.CSV_FILE_PATH)
        if csv_dir and not os.path.exists(csv_dir):
            print(f"  ✗ CSV directory doesn't exist: {csv_dir}")
            return False
        
        print("  ✓ Configuration valid")
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False

def test_registration_form():
    """Test registration form (visual test)"""
    print("\nTesting registration form...")
    print("  Opening form for 5 seconds...")
    
    try:
        from registration_form import RegistrationForm
        import threading
        
        form = RegistrationForm()
        
        # Auto-close after 5 seconds
        def auto_close():
            import time
            time.sleep(5)
            if form.root:
                form.root.quit()
                form.root.destroy()
        
        threading.Thread(target=auto_close, daemon=True).start()
        form.show()
        
        print("  ✓ Registration form working")
        return True
    except Exception as e:
        print(f"  ✗ Registration form error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("BOOTH SYSTEM - COMPONENT TESTS")
    print("=" * 60)
    
    results = {}
    
    results['imports'] = test_imports()
    results['tesseract'] = test_tesseract()
    results['webcam'] = test_webcam()
    results['config'] = test_config()
    results['form'] = test_registration_form()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! System ready.")
        print("\nNext steps:")
        print("  1. Calibrate score region: python calibrate_score_region.py")
        print("  2. Run booth system: python main.py")
    else:
        print("\n⚠ Some tests failed. Fix issues before running booth.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()

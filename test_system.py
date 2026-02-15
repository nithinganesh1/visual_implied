#!/usr/bin/env python3
"""
System Component Test Script
Tests individual modules without requiring full hardware setup
"""

import sys
import time

def test_imports():
    """Test if all required modules can be imported"""
    print("\n" + "="*60)
    print("TESTING MODULE IMPORTS")
    print("="*60)
    
    modules = [
        'detector',
        'button_handler',
        'decision_engine',
        'audio_manager',
        'gps_module',
        'gsm_module',
        'utils',
        'config'
    ]
    
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n⚠ {len(failed)} module(s) failed to import")
        return False
    else:
        print(f"\n✓ All {len(modules)} modules imported successfully")
        return True

def test_dependencies():
    """Test if required Python packages are installed"""
    print("\n" + "="*60)
    print("TESTING DEPENDENCIES")
    print("="*60)
    
    packages = [
        'cv2',
        'numpy',
        'gpiozero',
        'serial',
        'ultralytics'
    ]
    
    failed = []
    
    for package in packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except Exception as e:
            print(f"✗ {package}: Not installed")
            failed.append(package)
    
    if failed:
        print(f"\n⚠ {len(failed)} package(s) missing")
        print("Run: pip3 install -r requirements.txt")
        return False
    else:
        print(f"\n✓ All {len(packages)} packages available")
        return True

def test_mock_modules():
    """Test mock GPS and GSM modules"""
    print("\n" + "="*60)
    print("TESTING MOCK MODULES")
    print("="*60)
    
    try:
        from gps_module import MockGPSModule
        from gsm_module import MockGSMModule
        
        # Test Mock GPS
        print("\nTesting Mock GPS...")
        gps = MockGPSModule()
        location = gps.get_location()
        print(f"  Location: {location}")
        print(f"  String: {gps.get_location_string()}")
        print(f"  Available: {gps.is_available()}")
        print("✓ Mock GPS working")
        
        # Test Mock GSM
        print("\nTesting Mock GSM...")
        gsm = MockGSMModule("+1234567890")
        result = gsm.send_sms("Test message")
        print(f"  SMS result: {result}")
        print(f"  Signal: {gsm.check_signal()}")
        print(f"  Available: {gsm.is_available()}")
        print("✓ Mock GSM working")
        
        return True
        
    except Exception as e:
        print(f"✗ Mock module test failed: {e}")
        return False

def test_audio_system():
    """Test audio/TTS system"""
    print("\n" + "="*60)
    print("TESTING AUDIO SYSTEM")
    print("="*60)
    
    try:
        from audio_manager import AudioManager
        
        print("\nInitializing audio manager...")
        audio = AudioManager()
        
        print("Testing speech (check if you hear audio)...")
        audio.speak("Audio system test", block=True)
        
        print("\nTesting priority queue...")
        audio.speak_with_priority("Priority 1", priority=1, obj_type="test1")
        audio.speak_with_priority("Priority 5", priority=5, obj_type="test2")
        
        time.sleep(2)
        
        audio.cleanup()
        print("✓ Audio system test complete")
        print("  If you heard speech, audio is working")
        print("  If not, check espeak installation: sudo apt-get install espeak")
        
        return True
        
    except Exception as e:
        print(f"✗ Audio test failed: {e}")
        return False

def test_utils():
    """Test utility functions"""
    print("\n" + "="*60)
    print("TESTING UTILITIES")
    print("="*60)
    
    try:
        from utils import (
            calculate_distance,
            get_bounding_box_area,
            bboxes_overlap,
            RateLimiter
        )
        
        # Test distance calculation
        dist = calculate_distance((0, 0), (3, 4))
        assert dist == 5.0, "Distance calculation failed"
        print("✓ Distance calculation")
        
        # Test bounding box area
        area = get_bounding_box_area((0, 0, 10, 20))
        assert area == 200, "Area calculation failed"
        print("✓ Bounding box area")
        
        # Test overlap detection
        overlap = bboxes_overlap((0, 0, 10, 10), (5, 5, 15, 15))
        assert overlap == True, "Overlap detection failed"
        print("✓ Bounding box overlap")
        
        # Test rate limiter
        limiter = RateLimiter(max_calls=2, time_window=1.0)
        assert limiter.is_allowed() == True
        assert limiter.is_allowed() == True
        assert limiter.is_allowed() == False
        print("✓ Rate limiter")
        
        print("\n✓ All utility functions working")
        return True
        
    except Exception as e:
        print(f"✗ Utility test failed: {e}")
        return False

def test_configuration():
    """Test configuration file"""
    print("\n" + "="*60)
    print("TESTING CONFIGURATION")
    print("="*60)
    
    try:
        import config
        
        print(f"Emergency Phone: {config.EMERGENCY_PHONE_NUMBER}")
        print(f"Button Pin: {config.PRIMARY_BUTTON_PIN}")
        print(f"Camera: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}")
        print(f"YOLO Model: {config.YOLO_MODEL_PATH}")
        print(f"Confidence: {config.CONFIDENCE_THRESHOLD}")
        print(f"Mock GPS: {config.USE_MOCK_GPS}")
        print(f"Mock GSM: {config.USE_MOCK_GSM}")
        
        print("\n✓ Configuration loaded successfully")
        
        if config.EMERGENCY_PHONE_NUMBER == "+916282670289":
            print("⚠ WARNING: Update EMERGENCY_PHONE_NUMBER in config.py")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SMART NAVIGATION SYSTEM - COMPONENT TEST")
    print("="*60)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Utilities", test_utils),
        ("Mock Modules", test_mock_modules),
        ("Audio System", test_audio_system),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! System ready for deployment.")
        print("\nNext steps:")
        print("1. Place 'best.pt' YOLO model in project directory")
        print("2. Connect hardware (camera, buttons, GPS, GSM)")
        print("3. Run: python3 main.py")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Fix issues before deployment.")
        print("\nTroubleshooting:")
        print("- Run: pip3 install -r requirements.txt")
        print("- Run: sudo apt-get install espeak python3-opencv")
        print("- Check error messages above")
    
    print("\n" + "="*60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

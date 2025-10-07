#!/usr/bin/env python3
import os
import sys
import logging

# Set up minimal logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_all_imports():
    """Test that all modules can be imported"""
    modules_to_test = [
        ("utils.config", "AppConfig"),
        ("utils.logger", "setup_logging"),
        ("utils.helpers", "AsyncHelper"),
        ("core.camera_manager", "CameraManager"),
        ("core.drive_uploader", "DriveUploader"),
        ("core.session_manager", "SessionManager"),
        ("core.network_monitor", "NetworkMonitor"),
        ("core.app", "SelfieBoothCore"),
        ("ui.components.camera_widget", "CameraWidget"),
        ("ui.components.qr_generator", "QRGenerator"),
        ("ui.components.modern_buttons", "ModernButton"),
        ("ui.screens.live_view", "LiveViewScreen"),
        ("ui.screens.preview", "PreviewScreen"),
        ("ui.screens.settings", "SettingsScreen"),
    ]
    
    success = True
    for module_path, class_name in modules_to_test:
        try:
            exec(f"from {module_path} import {class_name}")
            print(f"✓ {module_path}.{class_name}")
        except ImportError as e:
            print(f"✗ {module_path}.{class_name} - {e}")
            success = False
    
    return success

def test_config():
    """Test configuration loading"""
    try:
        from utils.config import AppConfig
        config = AppConfig()
        print("✓ Configuration loaded successfully")
        print(f"  - Camera preview: {config.get('camera.preview_size')}")
        print(f"  - Camera capture: {config.get('camera.capture_size')}")
        print(f"  - Serial port: {config.get('serial.port')}")
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def test_helpers():
    """Test helper functions"""
    try:
        from utils.helpers import FileHelper, ValidationHelper
        
        # Test file helper
        test_dir = "./test_dir"
        FileHelper.ensure_directory(test_dir)
        if os.path.exists(test_dir):
            print("✓ FileHelper.ensure_directory works")
            os.rmdir(test_dir)
        else:
            print("✗ FileHelper.ensure_directory failed")
            return False
        
        # Test validation helper
        if ValidationHelper.validate_pin("1234", "1234"):
            print("✓ ValidationHelper.validate_pin works")
        else:
            print("✗ ValidationHelper.validate_pin failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Helpers error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Selfie Booth Complete Test Suite")
    print("=" * 50)
    
    success = True
    success &= test_all_imports()
    print()
    success &= test_config()
    print()
    success &= test_helpers()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! The application should work correctly.")
        print("\nTo run the full app: python main.py")
    else:
        print("❌ Some tests failed. Check the errors above.")
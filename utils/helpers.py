import os
import json
import asyncio
from datetime import datetime
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class AsyncHelper:
    """Helper class for async operations"""
    
    @staticmethod
    def run_async(coro):
        """Run async coroutine from sync context"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if loop.is_running():
            # If loop is already running, create task
            return asyncio.create_task(coro)
        else:
            # Otherwise run until complete
            return loop.run_until_complete(coro)
    
    @staticmethod
    async def run_in_thread(func, *args, **kwargs):
        """Run function in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)

class FileHelper:
    """Helper class for file operations"""
    
    @staticmethod
    def ensure_directory(path: str) -> bool:
        """Ensure directory exists, create if not"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Error creating directory {path}: {e}")
            return False
    
    @staticmethod
    def safe_json_load(filepath: str, default: Any = None) -> Any:
        """Safely load JSON file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON from {filepath}: {e}")
        return default
    
    @staticmethod
    def safe_json_save(data: Any, filepath: str) -> bool:
        """Safely save data to JSON file"""
        try:
            FileHelper.ensure_directory(os.path.dirname(filepath))
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving JSON to {filepath}: {e}")
            return False
    
    @staticmethod
    def get_unique_filename(directory: str, base_name: str, extension: str) -> str:
        """Generate unique filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_{timestamp}.{extension}"
        return os.path.join(directory, filename)

class ValidationHelper:
    """Helper class for data validation"""
    
    @staticmethod
    def validate_pin(pin: str, correct_pin: str) -> bool:
        """Validate PIN code"""
        return pin == correct_pin
    
    @staticmethod
    def validate_wifi_ssid(ssid: str) -> bool:
        """Validate WiFi SSID"""
        if not ssid or len(ssid) > 32:
            return False
        # Basic SSID validation
        return all(ord(c) < 128 for c in ssid)  # Basic ASCII check
    
    @staticmethod
    def validate_wifi_password(password: str) -> bool:
        """Validate WiFi password"""
        if not password:
            return False
        return 8 <= len(password) <= 63

class NetworkHelper:
    """Helper class for network operations"""
    
    @staticmethod
    def get_ip_address() -> str:
        """Get current IP address"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "Unknown"
    
    @staticmethod
    def check_internet_connection(timeout: int = 5) -> bool:
        """Check internet connection"""
        try:
            import urllib.request
            urllib.request.urlopen('https://www.google.com', timeout=timeout)
            return True
        except:
            return False

class ImageHelper:
    """Helper class for image operations"""
    
    @staticmethod
    def resize_image(image_path: str, max_size: tuple) -> str:
        """Resize image to maximum dimensions"""
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                output_path = image_path.replace('.jpg', '_resized.jpg')
                img.save(output_path, quality=95)
                return output_path
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return image_path
    
    @staticmethod
    def compress_image(image_path: str, quality: int = 85) -> str:
        """Compress image with specified quality"""
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                output_path = image_path.replace('.jpg', '_compressed.jpg')
                img.save(output_path, quality=quality, optimize=True)
                return output_path
        except Exception as e:
            logger.error(f"Error compressing image: {e}")
            return image_path

class SerialHelper:
    """Helper class for serial operations"""
    
    @staticmethod
    def list_serial_ports() -> List[str]:
        """List available serial ports"""
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    @staticmethod
    def test_serial_port(port: str, baudrate: int = 9600) -> bool:
        """Test if serial port is available and working"""
        try:
            import serial
            with serial.Serial(port, baudrate, timeout=1) as ser:
                return ser.is_open
        except:
            return False

class UIHelper:
    """Helper class for UI operations"""
    
    @staticmethod
    def show_toast(message: str, duration: float = 2.0):
        """Show toast message (would need implementation based on UI framework)"""
        # This would be implemented based on your UI framework
        logger.info(f"Toast: {message}")
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names)-1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f}{size_names[i]}"
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds//60}m {seconds%60}s"
        else:
            return f"{seconds//3600}h {(seconds%3600)//60}m"
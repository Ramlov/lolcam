import os
import asyncio
import logging
import serial
import time
import numpy as np
from PIL import Image, ImageOps
from picamera2 import Picamera2

logger = logging.getLogger(__name__)

class CameraManager:
    def __init__(self, config):
        self.config = config
        self.picam2 = None
        self.serial_conn = None
        self.is_initialized = False
        self.current_overlay = None
        self._load_overlay()
        self._init_serial()
    
    def _init_serial(self):
        """Initialize serial connection for flash trigger"""
        try:
            serial_port = self.config.get('serial.port', '/dev/ttyUSB0')
            baud_rate = self.config.get('serial.baud_rate', 9600)
            
            self.serial_conn = serial.Serial(
                port=serial_port,
                baudrate=baud_rate,
                timeout=self.config.get('serial.timeout', 1)
            )
            time.sleep(2)
            logger.info(f"Serial connection established on {serial_port}")
            
        except Exception as e:
            logger.warning(f"Failed to initialize serial connection: {e}")
            self.serial_conn = None
    
    def _trigger_flash(self):
        """Trigger the flash/blitz via serial"""
        if not self.serial_conn:
            logger.warning("No serial connection available for flash trigger")
            return False
        
        try:
            trigger_command = self.config.get('serial.trigger_command', b'1')
            self.serial_conn.write(trigger_command)
            logger.info("Flash trigger signal sent")
            
            flash_delay = self.config.get('serial.flash_delay', 0.1)
            time.sleep(flash_delay)
            return True
            
        except Exception as e:
            logger.error(f"Error triggering flash: {e}")
            return False
    
    def _load_overlay(self):
        """Load overlay image"""
        try:
            overlay_path = self.config.get('overlay.file_path')
            if overlay_path and os.path.exists(overlay_path):
                self.current_overlay = Image.open(overlay_path).convert('RGBA')
                logger.info(f"Overlay loaded: {overlay_path}")
            else:
                logger.warning("No overlay image found")
                self._create_default_overlay()
        except Exception as e:
            logger.error(f"Error loading overlay: {e}")
            self._create_default_overlay()
    
    def _create_default_overlay(self):
        """Create a default overlay for testing"""
        try:
            from PIL import ImageDraw, ImageFont
            overlay = Image.new('RGBA', (400, 200), (255, 255, 255, 128))
            draw = ImageDraw.Draw(overlay)
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            draw.text((50, 80), "SELFIE BOOTH", fill=(255, 0, 0, 255), font=font)
            self.current_overlay = overlay
            logger.info("Default overlay created")
        except Exception as e:
            logger.error(f"Error creating default overlay: {e}")
            self.current_overlay = None
    
    def initialize(self):
        """Initialize camera - simplified without libcamera controls"""
        try:
            self.picam2 = Picamera2()
            
            # Simple configuration without libcamera controls
            preview_config = self.picam2.create_preview_configuration(
                main={"size": tuple(self.config.get('camera.preview_size', [1024, 768]))}
            )
            
            self.picam2.configure(preview_config)
            self.picam2.start()
            self.is_initialized = True
            
            logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Camera initialization failed: {e}")
            # Fallback: create a mock camera for testing
            return self._initialize_mock_camera()
    
    def _initialize_mock_camera(self):
        """Initialize a mock camera for testing when real camera fails"""
        logger.warning("Using mock camera - real camera not available")
        self.is_initialized = True
        return True
    
    def start_preview(self):
        """Start camera preview"""
        if self.is_initialized:
            logger.info("Camera preview started")
    
    def get_preview_frame(self):
        """Get current preview frame"""
        if not self.is_initialized or not self.picam2:
            # Return a test pattern for mock camera
            return self._create_test_pattern()
        
        try:
            return self.picam2.capture_array()
        except Exception as e:
            logger.error(f"Error getting preview frame: {e}")
            return self._create_test_pattern()
    
    def _create_test_pattern(self):
        """Create a test pattern when camera is not available"""
        # Create a simple gradient test pattern
        width, height = 1024, 768
        test_pattern = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Create gradient
        for y in range(height):
            for x in range(width):
                test_pattern[y, x] = [
                    int(255 * x / width),      # Red gradient
                    int(255 * y / height),     # Green gradient  
                    int(255 * (x+y) / (width+height))  # Blue gradient
                ]
        
        # Add text
        cv2 = None
        try:
            import cv2
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(test_pattern, "CAMERA OFFLINE", (200, 384), font, 2, (255, 255, 255), 3)
            cv2.putText(test_pattern, "TEST PATTERN", (250, 450), font, 1, (255, 255, 255), 2)
        except:
            pass
            
        return test_pattern
    
    async def capture_image(self, filename=None):
        """Capture image asynchronously"""
        if not self.is_initialized:
            # Mock capture for testing
            return await self._mock_capture_image(filename)
        
        loop = asyncio.get_event_loop()
        
        if not filename:
            from datetime import datetime
            filename = f"selfie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        filepath = os.path.join(
            self.config.get('directories.pictures_path', '/tmp'),
            filename
        )
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            # Trigger flash
            flash_success = await loop.run_in_executor(None, self._trigger_flash)
            if not flash_success:
                logger.warning("Flash trigger failed")
            
            # Capture image
            capture_config = self.picam2.create_still_configuration(
                main={"size": tuple(self.config.get('camera.capture_size', [1920, 1080]))}
            )
            
            await loop.run_in_executor(
                None, 
                self.picam2.switch_mode_and_capture_file, 
                capture_config, 
                filepath
            )
            
            logger.info(f"Image captured: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error capturing image: {e}")
            # Fallback to mock capture
            return await self._mock_capture_image(filename)
    
    async def _mock_capture_image(self, filename=None):
        """Mock image capture for testing"""
        from datetime import datetime
        if not filename:
            filename = f"mock_selfie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        filepath = os.path.join(
            self.config.get('directories.pictures_path', '/tmp'),
            filename
        )
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Create a mock image
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (1920, 1080), color=(73, 109, 137))
        draw = ImageDraw.Draw(img)
        
        # Add some text
        draw.text((500, 500), "MOCK SELFIE", fill=(255, 255, 0))
        draw.text((400, 600), f"Taken: {datetime.now()}", fill=(255, 255, 255))
        
        img.save(filepath, quality=95)
        logger.info(f"Mock image created: {filepath}")
        
        return filepath
    
    async def apply_overlay(self, image_path):
        """Apply overlay to image"""
        if not self.current_overlay:
            return image_path
        
        try:
            loop = asyncio.get_event_loop()
            output_path = image_path.replace('.jpg', '_overlay.jpg')
            
            def process_image():
                with Image.open(image_path) as base_image:
                    if base_image.mode != 'RGBA':
                        base_image = base_image.convert('RGBA')
                    
                    overlay_resized = self.current_overlay.resize(
                        base_image.size, Image.Resampling.LANCZOS
                    )
                    
                    combined = Image.alpha_composite(base_image, overlay_resized)
                    combined = combined.convert('RGB')
                    combined.save(output_path, quality=95)
                
                os.remove(image_path)
                return output_path
            
            result = await loop.run_in_executor(None, process_image)
            logger.info(f"Overlay applied: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error applying overlay: {e}")
            return image_path
    
    def test_flash(self):
        """Test flash trigger"""
        if self.serial_conn:
            success = self._trigger_flash()
            return success
        return False
    
    def cleanup(self):
        """Cleanup resources"""
        if self.picam2:
            try:
                self.picam2.stop()
                self.picam2.close()
                logger.info("Camera resources cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up camera: {e}")
        
        if self.serial_conn:
            try:
                self.serial_conn.close()
                logger.info("Serial connection closed")
            except Exception as e:
                logger.error(f"Error closing serial connection: {e}")
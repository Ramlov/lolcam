import os
import asyncio
import logging
import serial
import time
from PIL import Image, ImageOps
from picamera2 import Picamera2
from libcamera import controls

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
            time.sleep(2)  # Allow serial connection to establish
            logger.info(f"Serial connection established on {serial_port}")
            
        except Exception as e:
            logger.error(f"Failed to initialize serial connection: {e}")
            self.serial_conn = None
    
    def _trigger_flash(self):
        """Trigger the flash/blitz via serial"""
        if not self.serial_conn:
            logger.warning("No serial connection available for flash trigger")
            return False
        
        try:
            # Send trigger signal (adjust command as needed for your flash)
            trigger_command = self.config.get('serial.trigger_command', b'1')
            self.serial_conn.write(trigger_command)
            logger.info("Flash trigger signal sent")
            
            # Wait briefly for flash to activate
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
        except Exception as e:
            logger.error(f"Error loading overlay: {e}")
    
    def initialize(self):
        """Initialize camera"""
        try:
            self.picam2 = Picamera2()
            
            # Create configurations
            preview_config = self.picam2.create_preview_configuration(
                main={"size": tuple(self.config.get('camera.preview_size', [1024, 768]))},
                lores={"size": tuple(self.config.get('camera.preview_size', [1024, 768]))},
                display="lores"
            )
            
            # Configure camera
            self.picam2.configure(preview_config)
            
            # Set camera controls
            self.picam2.set_controls({
                "AwbMode": controls.AwbModeEnum.Auto,
                "AeEnable": True,
                "ExposureValue": 0.0,
                "Brightness": 0.0,
                "Contrast": 1.0
            })
            
            self.picam2.start()
            self.is_initialized = True
            
            # Apply zoom if configured
            self._apply_zoom()
            
            logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Camera initialization failed: {e}")
            return False
    
    def _apply_zoom(self):
        """Apply zoom configuration"""
        try:
            zoom_level = self.config.get('camera.zoom_level', 1.0)
            if zoom_level > 1.0:
                sensor_res = self.picam2.sensor_resolution
                if sensor_res:
                    width, height = sensor_res
                    new_width = int(width / zoom_level)
                    new_height = int(height / zoom_level)
                    x_offset = (width - new_width) // 2
                    y_offset = (height - new_height) // 2
                    
                    self.picam2.set_controls({
                        "ScalerCrop": (x_offset, y_offset, new_width, new_height)
                    })
                    logger.info(f"Zoom applied: {zoom_level}x")
        except Exception as e:
            logger.warning(f"Could not apply zoom: {e}")
    
    def start_preview(self):
        """Start camera preview"""
        if self.is_initialized:
            logger.info("Camera preview started")
    
    async def capture_image(self, filename=None):
        """Capture image asynchronously with flash trigger"""
        if not self.is_initialized:
            raise RuntimeError("Camera not initialized")
        
        loop = asyncio.get_event_loop()
        
        if not filename:
            from datetime import datetime
            filename = f"selfie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        filepath = os.path.join(
            self.config.get('directories.pictures_path', '/tmp'),
            filename
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            # Trigger flash before capture
            flash_success = await loop.run_in_executor(None, self._trigger_flash)
            if not flash_success:
                logger.warning("Flash trigger failed, capturing without flash")
            
            # Capture in thread pool
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
            raise
    
    async def apply_overlay(self, image_path):
        """Apply overlay to image"""
        if not self.current_overlay:
            return image_path
        
        try:
            loop = asyncio.get_event_loop()
            
            # Process image in thread pool
            output_path = image_path.replace('.jpg', '_overlay.jpg')
            
            def process_image():
                with Image.open(image_path) as base_image:
                    # Convert to RGBA if needed
                    if base_image.mode != 'RGBA':
                        base_image = base_image.convert('RGBA')
                    
                    # Resize overlay to match base image
                    overlay_resized = self.current_overlay.resize(
                        base_image.size, Image.Resampling.LANCZOS
                    )
                    
                    # Composite images
                    combined = Image.alpha_composite(base_image, overlay_resized)
                    
                    # Convert back to RGB for JPEG
                    combined = combined.convert('RGB')
                    combined.save(output_path, quality=95)
                
                # Remove original file
                os.remove(image_path)
                return output_path
            
            result = await loop.run_in_executor(None, process_image)
            logger.info(f"Overlay applied: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error applying overlay: {e}")
            return image_path
    
    def test_flash(self):
        """Test flash trigger (for admin settings)"""
        if self.serial_conn:
            success = self._trigger_flash()
            return success
        return False
    
    def cleanup(self):
        """Cleanup camera and serial resources"""
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
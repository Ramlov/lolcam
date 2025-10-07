import logging
import asyncio
from threading import Thread, Event
from datetime import datetime

from .camera_manager import CameraManager
from .drive_uploader import DriveUploader
from .session_manager import SessionManager
from .network_monitor import NetworkMonitor

logger = logging.getLogger(__name__)

class SelfieBoothCore:
    """Main application core that coordinates all components"""
    
    def __init__(self, config):
        self.config = config
        self.camera = CameraManager(config)
        self.drive_uploader = DriveUploader(config)
        self.session_manager = SessionManager(config)
        self.network_monitor = NetworkMonitor(config)
        
        self.is_initialized = False
        self._stop_event = Event()
        self._background_thread = None
        
    def initialize(self):
        """Initialize all core components"""
        try:
            logger.info("Initializing core components...")
            
            # Initialize camera first
            if not self.camera.initialize():
                logger.error("Camera initialization failed")
                return False
            
            # Initialize network monitor
            self.network_monitor.start_monitoring()
            
            # Initialize drive uploader
            self.drive_uploader.initialize()
            
            # Start background tasks
            self._start_background_tasks()
            
            self.is_initialized = True
            logger.info("Core components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Core initialization failed: {e}")
            return False
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        def background_worker():
            while not self._stop_event.is_set():
                try:
                    # Clean up old sessions every 5 minutes
                    self.session_manager.cleanup_old_sessions()
                    
                    # Process offline queue if online
                    if self.network_monitor.is_online():
                        self._process_offline_queue()
                        
                    # Wait before next iteration
                    self._stop_event.wait(300)  # 5 minutes
                    
                except Exception as e:
                    logger.error(f"Background task error: {e}")
                    self._stop_event.wait(60)  # Wait 1 minute on error
        
        self._background_thread = Thread(target=background_worker, daemon=True)
        self._background_thread.start()
    
    def _process_offline_queue(self):
        """Process photos in offline queue"""
        try:
            queue = self.session_manager.get_offline_queue()
            for item in queue[:5]:  # Process max 5 at a time
                try:
                    # Upload photo
                    drive_url = self.drive_uploader.upload_photo(
                        item['photo_path'], 
                        item['session_id']
                    )
                    
                    # Update session
                    self.session_manager.mark_photo_uploaded(
                        item['session_id'], 
                        item['photo_path'], 
                        drive_url
                    )
                    
                    logger.info(f"Uploaded queued photo: {item['photo_path']}")
                    
                except Exception as e:
                    logger.warning(f"Failed to upload queued photo: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing offline queue: {e}")
    
    def start_camera_preview(self):
        """Start camera preview"""
        if self.is_initialized:
            self.camera.start_preview()
    
    async def capture_photo(self, apply_overlay=True, session_id=None):
        """Capture a photo asynchronously"""
        if not self.is_initialized:
            raise RuntimeError("Core not initialized")
        
        try:
            # Create session if needed
            if not session_id:
                session_id = self.session_manager.create_session()
            
            # Capture photo
            photo_path = await self.camera.capture_image()
            
            # Apply overlay if requested
            if apply_overlay:
                photo_path = await self.camera.apply_overlay(photo_path)
            
            # Upload if online, otherwise queue
            drive_url = None
            if self.network_monitor.is_online():
                try:
                    drive_url = await self.drive_uploader.upload_photo_async(
                        photo_path, session_id
                    )
                except Exception as e:
                    logger.warning(f"Upload failed, queuing for later: {e}")
            
            # Add to session
            self.session_manager.add_photo(
                session_id, photo_path, drive_url
            )
            
            return {
                'success': True,
                'session_id': session_id,
                'photo_path': photo_path,
                'drive_url': drive_url,
                'is_online': drive_url is not None
            }
            
        except Exception as e:
            logger.error(f"Error capturing photo: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_session_qr_data(self, session_id):
        """Get QR code data for a session"""
        return self.session_manager.get_qr_data(session_id)
    
    def get_network_status(self):
        """Get current network status"""
        return {
            'online': self.network_monitor.is_online(),
            'ssid': self.network_monitor.get_current_ssid()
        }
    
    def update_settings(self, new_settings, pin_code):
        """Update application settings"""
        # Verify PIN
        if pin_code != self.config.get('admin.pin_code'):
            raise ValueError("Invalid PIN code")
        
        # Update settings
        for key, value in new_settings.items():
            self.config.set(key, value)
        
        self.config.save()
        
        # Reinitialize components if needed
        if any(k.startswith('camera.') for k in new_settings.keys()):
            self.camera.cleanup()
            self.camera.initialize()
    
    def cleanup(self):
        """Clean up all resources"""
        logger.info("Cleaning up core resources...")
        
        self._stop_event.set()
        if self._background_thread:
            self._background_thread.join(timeout=5)
        
        self.camera.cleanup()
        self.network_monitor.stop_monitoring()
        
        logger.info("Cleanup completed")
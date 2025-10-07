import logging
import subprocess
import time
from threading import Thread, Event

logger = logging.getLogger(__name__)

class NetworkMonitor:
    def __init__(self, config):
        self.config = config
        self.is_online = False
        self.current_ssid = None
        self._stop_event = Event()
        self._monitor_thread = None
    
    def start_monitoring(self):
        """Start network monitoring"""
        self._monitor_thread = Thread(target=self._monitor_network, daemon=True)
        self._monitor_thread.start()
        logger.info("Network monitoring started")
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("Network monitoring stopped")
    
    def _monitor_network(self):
        """Monitor network connectivity in background"""
        while not self._stop_event.is_set():
            try:
                # Check internet connectivity
                previous_status = self.is_online
                
                # Simple ping test
                try:
                    subprocess.run(['ping', '-c', '1', '-W', '3', '8.8.8.8'], 
                                 capture_output=True, timeout=5)
                    self.is_online = True
                except:
                    self.is_online = False
                
                # Get current WiFi SSID
                self.current_ssid = self._get_current_ssid()
                
                # Log status changes
                if previous_status != self.is_online:
                    status = "online" if self.is_online else "offline"
                    logger.info(f"Network status changed: {status}")
                
                # Wait before next check
                self._stop_event.wait(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Network monitoring error: {e}")
                self._stop_event.wait(60)  # Wait longer on error
    
    def _get_current_ssid(self):
        """Get current WiFi SSID"""
        try:
            result = subprocess.run(
                ['iwgetid', '-r'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None
    
    def get_current_ssid(self):
        """Get current SSID"""
        return self.current_ssid
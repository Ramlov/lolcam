#!/usr/bin/env python3
import os
import sys
import logging
from kivy.config import Config
from kivy.core.window import Window

# Configure Kivy before any other imports
Config.set('kivy', 'log_level', 'warning')
Config.set('graphics', 'multisamples', '0')  # Improve performance
Config.set('input', 'mouse', 'mouse,disable_multitouch')  # Better for touch

# Set fullscreen for kiosk mode
Window.fullscreen = 'auto'
Window.show_cursor = False

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivymd.app import MDApp
from core.app import SelfieBoothCore
from utils.logger import setup_logging
from utils.config import AppConfig

class SelfieBoothApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.core = None
        self.config_manager = AppConfig()
        
    def build(self):
        """Build the application"""
        # Setup logging
        setup_logging(self.config_manager)
        
        # Initialize core application
        self.core = SelfieBoothCore(self.config_manager)
        
        # Set theme
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.accent_palette = "Blue"
        
        # Load main screen
        from ui.screens.live_view import LiveViewScreen
        return LiveViewScreen(core=self.core)
    
    def on_start(self):
        """Called when app starts"""
        logging.info("Selfie Booth starting...")
        
        # Initialize core components
        if self.core.initialize():
            logging.info("All components initialized successfully")
        else:
            logging.error("Failed to initialize some components")
            
        # Start camera preview
        self.core.start_camera_preview()
    
    def on_stop(self):
        """Called when app stops"""
        logging.info("Selfie Booth shutting down...")
        if self.core:
            self.core.cleanup()

if __name__ == '__main__':
    try:
        SelfieBoothApp().run()
    except KeyboardInterrupt:
        logging.info("Application stopped by user")
    except Exception as e:
        logging.critical(f"Application crashed: {e}")
        raise
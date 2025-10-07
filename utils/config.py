import json
import os
from pathlib import Path

class AppConfig:
    def __init__(self, config_path="config/settings.json"):
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self):
        """Load configuration with defaults"""
        default_config = {
            "app": {
                "name": "Selfie Booth",
                "version": "2.0.0"
            },
            "camera": {
                "preview_size": [1024, 768],
                "capture_size": [1920, 1080],
                "rotation": 0,
                "zoom_level": 1.0
            },
            "serial": {
                "port": "/dev/ttyUSB0",
                "baud_rate": 9600,
                "timeout": 1,
                "trigger_command": "1",
                "flash_delay": 0.1
            },
            "overlay": {
                "file_path": "ui/assets/overlays/default.png",
                "enabled": True
            },
            "upload": {
                "auto_upload": True,
                "google_drive_folder": "SelfieBooth"
            },
            "google_drive": {
                "token_path": "config/token.json",
                "credentials_file": "config/credentials.json",
                "scopes": ["https://www.googleapis.com/auth/drive.file"],
                "parent_folder_id": None
            },
            "session": {
                "max_photos": 10,
                "timeout_minutes": 30
            },
            "admin": {
                "pin_code": "1234",
                "auto_start": True
            },
            "directories": {
                "pictures_path": "/home/pi/Pictures/selfie-booth",
                "logs_path": "/home/pi/logs"
            }
        }
        
        # Load user config if exists
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    self._deep_merge(default_config, user_config)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return default_config
    
    def _deep_merge(self, base, update):
        """Deep merge two dictionaries"""
        for key, value in update.items():
            if isinstance(value, dict) and key in base:
                self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base
    
    def get(self, key, default=None):
        """Get config value using dot notation"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key, value):
        """Set config value"""
        keys = key.split('.')
        config_ref = self._config
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]
        config_ref[keys[-1]] = value
    
    def save(self):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self._config, f, indent=2)
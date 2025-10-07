import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, config):
        self.config = config
        self.active_sessions = {}
        self.offline_queue = []
        self._load_offline_queue()
    
    def create_session(self) -> str:
        """Create a new photo session"""
        session_id = str(uuid.uuid4())[:8]  # Short ID for QR codes
        
        session = {
            'id': session_id,
            'created_at': datetime.now(),
            'photos': [],
            'folder_id': None,
            'drive_url': None,
            'is_online': True
        }
        
        self.active_sessions[session_id] = session
        logger.info(f"New session created: {session_id}")
        return session_id
    
    def add_photo(self, session_id: str, photo_path: str, drive_url: Optional[str] = None):
        """Add photo to session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        photo_data = {
            'local_path': photo_path,
            'drive_url': drive_url,
            'captured_at': datetime.now(),
            'uploaded': drive_url is not None
        }
        
        self.active_sessions[session_id]['photos'].append(photo_data)
        
        # Add to offline queue if not uploaded
        if not drive_url:
            self.offline_queue.append({
                'session_id': session_id,
                'photo_path': photo_path,
                'added_at': datetime.now().isoformat()
            })
            self._save_offline_queue()
        
        logger.info(f"Photo added to session {session_id}")
    
    def get_qr_data(self, session_id: str) -> Optional[Dict]:
        """Get QR code data for session"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        photo_count = len(session['photos'])
        
        # If online and has drive URL, use that
        if session['drive_url']:
            return {
                'type': 'online',
                'url': session['drive_url'],
                'photo_count': photo_count,
                'session_id': session_id
            }
        else:
            # Generate offline QR data
            return {
                'type': 'offline',
                'session_id': session_id,
                'photo_count': photo_count,
                'message': 'Photos will be available online later'
            }
    
    def get_offline_queue(self):
        """Get offline queue"""
        return self.offline_queue.copy()
    
    def mark_photo_uploaded(self, session_id: str, photo_path: str, drive_url: str):
        """Mark photo as uploaded and remove from queue"""
        # Update session
        if session_id in self.active_sessions:
            for photo in self.active_sessions[session_id]['photos']:
                if photo['local_path'] == photo_path:
                    photo['drive_url'] = drive_url
                    photo['uploaded'] = True
                    break
        
        # Remove from queue
        self.offline_queue = [
            item for item in self.offline_queue 
            if not (item['session_id'] == session_id and item['photo_path'] == photo_path)
        ]
        self._save_offline_queue()
    
    def cleanup_old_sessions(self):
        """Clean up expired sessions"""
        cutoff_time = datetime.now() - timedelta(
            minutes=self.config.get('session.timeout_minutes', 30)
        )
        
        expired_sessions = [
            sid for sid, session in self.active_sessions.items()
            if session['created_at'] < cutoff_time
        ]
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")
    
    def _load_offline_queue(self):
        """Load offline queue from disk"""
        queue_file = os.path.join(
            self.config.get('directories.pictures_path', '/tmp'),
            'offline_queue.json'
        )
        
        if os.path.exists(queue_file):
            try:
                with open(queue_file, 'r') as f:
                    saved_queue = json.load(f)
                    # Convert string dates back to datetime
                    for item in saved_queue:
                        if 'added_at' in item and isinstance(item['added_at'], str):
                            item['added_at'] = datetime.fromisoformat(item['added_at'])
                    self.offline_queue = saved_queue
                logger.info("Offline queue loaded from disk")
            except Exception as e:
                logger.error(f"Error loading offline queue: {e}")
                self.offline_queue = []
    
    def _save_offline_queue(self):
        """Save offline queue to disk"""
        queue_file = os.path.join(
            self.config.get('directories.pictures_path', '/tmp'),
            'offline_queue.json'
        )
        
        try:
            # Convert datetime to string for JSON serialization
            save_queue = []
            for item in self.offline_queue:
                save_item = item.copy()
                if 'added_at' in save_item and isinstance(save_item['added_at'], datetime):
                    save_item['added_at'] = save_item['added_at'].isoformat()
                save_queue.append(save_item)
            
            with open(queue_file, 'w') as f:
                json.dump(save_queue, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving offline queue: {e}")
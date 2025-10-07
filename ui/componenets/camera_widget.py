from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import cv2
import numpy as np

class CameraWidget(BoxLayout):
    """Widget for displaying camera preview"""
    
    texture = ObjectProperty(None)
    
    def __init__(self, camera_manager, **kwargs):
        super().__init__(**kwargs)
        self.camera_manager = camera_manager
        self._update_event = None
        self.start_preview()
    
    def start_preview(self):
        """Start camera preview updates"""
        if self._update_event is None:
            self._update_event = Clock.schedule_interval(self.update_texture, 1.0/30.0)  # 30 FPS
    
    def stop_preview(self):
        """Stop camera preview updates"""
        if self._update_event:
            self._update_event.cancel()
            self._update_event = None
    
    def update_texture(self, dt):
        """Update the texture with current camera frame"""
        try:
            frame = self.camera_manager.get_preview_frame()
            if frame is not None:
                # Convert frame to texture
                buf = frame.tobytes()
                texture = Texture.create(
                    size=(frame.shape[1], frame.shape[0]), 
                    colorfmt='bgr'
                )
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.texture = texture
        except Exception as e:
            print(f"Error updating texture: {e}")
    
    def on_texture(self, instance, value):
        """Handle texture updates"""
        # This will be used by the Kivy rendering
        pass
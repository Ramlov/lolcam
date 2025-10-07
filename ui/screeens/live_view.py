from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog

from ui.components.modern_buttons import CaptureButton
from ui.components.camera_widget import CameraWidget

class LiveViewScreen(MDScreen):
    """Main live view screen with camera preview"""
    
    status_text = StringProperty("Ready to capture")
    is_online = BooleanProperty(False)
    camera_texture = ObjectProperty(None)
    
    def __init__(self, core, **kwargs):
        super().__init__(**kwargs)
        self.core = core
        self.name = "live_view"
        self.current_session = None
        self.camera_widget = None
        self._build_ui()
        
        # Update network status
        Clock.schedule_once(self._update_network_status, 1)
        # Start camera preview after UI is built
        Clock.schedule_once(self._start_camera_preview, 2)
    
    def _build_ui(self):
        """Build the user interface"""
        # Main layout
        layout = BoxLayout(orientation='vertical')
        
        # Top toolbar
        toolbar = MDTopAppBar(
            title="Selfie Booth",
            elevation=4,
            left_action_items=[["cog", self._show_settings]],
            right_action_items=[["wifi", self._show_network_status]],
        )
        layout.add_widget(toolbar)
        
        # Camera preview area
        preview_card = MDCard(
            size_hint=(1, 0.8),
            elevation=8,
            padding="10dp",
            radius=[15, 15, 15, 15]
        )
        
        # Camera preview widget
        self.camera_container = BoxLayout()
        preview_card.add_widget(self.camera_container)
        layout.add_widget(preview_card)
        
        # Capture button area
        button_layout = BoxLayout(
            size_hint=(1, 0.2),
            padding="50dp"
        )
        
        self.capture_btn = CaptureButton(
            on_release=self._capture_photo
        )
        button_layout.add_widget(self.capture_btn)
        layout.add_widget(button_layout)
        
        # Status label
        self.status_label = MDLabel(
            text=self.status_text,
            halign="center",
            size_hint_y=None,
            height="40dp",
            theme_text_color="Primary"
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def _start_camera_preview(self, dt):
        """Start camera preview widget"""
        try:
            if self.core.camera.is_initialized:
                self.camera_widget = CameraWidget(self.core.camera)
                self.camera_container.add_widget(self.camera_widget)
                self.status_text = "Camera ready - Tap to capture!"
            else:
                self.status_text = "Camera not available"
                self.status_label.theme_text_color = "Error"
        except Exception as e:
            self.status_text = f"Camera error: {str(e)}"
            self.status_label.theme_text_color = "Error"
    
    def _update_network_status(self, dt):
        """Update network status display"""
        status = self.core.get_network_status()
        self.is_online = status['online']
        
        if self.is_online:
            self.status_text = "Online - Ready to upload"
            self.status_label.theme_text_color = "Primary"
        else:
            self.status_text = "Offline - Photos saved locally"
            self.status_label.theme_text_color = "Warning"
    
    def _capture_photo(self, instance):
        """Handle photo capture"""
        if self.capture_btn.disabled:
            return
            
        self.status_text = "Capturing photo..."
        self.capture_btn.disabled = True
        
        # Schedule capture in async manner
        Clock.schedule_once(lambda dt: self._perform_capture(), 0.1)
    
    def _perform_capture(self):
        """Perform the actual photo capture"""
        async def capture():
            result = await self.core.capture_photo(session_id=self.current_session)
            
            # Update UI on main thread
            def update_ui():
                self.capture_btn.disabled = False
                
                if result['success']:
                    self.status_text = "Photo captured!"
                    self.current_session = result['session_id']
                    self._show_preview(result)
                else:
                    self.status_text = f"Error: {result.get('error', 'Unknown error')}"
                    self.status_label.theme_text_color = "Error"
            
            Clock.schedule_once(lambda dt: update_ui())
        
        # Start async capture
        import asyncio
        asyncio.create_task(capture())
    
    def _show_preview(self, result):
        """Show photo preview screen"""
        from ui.screens.preview import PreviewScreen
        preview_screen = PreviewScreen(
            core=self.core,
            session_id=result['session_id'],
            name="preview"
        )
        self.manager.add_widget(preview_screen)
        self.manager.current = "preview"
    
    def _show_settings(self, instance):
        """Show settings screen"""
        from ui.screens.settings import SettingsScreen
        settings_screen = SettingsScreen(core=self.core, name="settings")
        self.manager.add_widget(settings_screen)
        self.manager.current = "settings"
    
    def _show_network_status(self, instance):
        """Show network status"""
        status = self.core.get_network_status()
        dialog = MDDialog(
            title="Network Status",
            text=f"Online: {status['online']}\nSSID: {status['ssid'] or 'Unknown'}",
            buttons=[MDLabel(
                text="OK",
                on_release=lambda x: dialog.dismiss()
            )]
        )
        dialog.open()
    
    def on_leave(self):
        """Called when leaving screen"""
        if self.camera_widget:
            self.camera_widget.stop_preview()
    
    def on_enter(self):
        """Called when entering screen"""
        if self.camera_widget:
            self.camera_widget.start_preview()
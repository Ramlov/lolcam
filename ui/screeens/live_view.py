from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar

class LiveViewScreen(MDScreen):
    """Main live view screen with camera preview"""
    
    status_text = StringProperty("Ready to capture")
    is_online = BooleanProperty(False)
    
    def __init__(self, core, **kwargs):
        super().__init__(**kwargs)
        self.core = core
        self.name = "live_view"
        self._build_ui()
        
        # Update network status
        Clock.schedule_once(self._update_network_status, 1)
    
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
            padding="20dp",
            radius=[20, 20, 20, 20]
        )
        
        # TODO: Add actual camera preview widget
        preview_label = MDLabel(
            text="Camera Preview",
            halign="center",
            theme_text_color="Secondary"
        )
        preview_card.add_widget(preview_label)
        layout.add_widget(preview_card)
        
        # Capture button
        button_layout = BoxLayout(
            size_hint=(1, 0.2),
            padding="50dp",
            spacing="20dp"
        )
        
        self.capture_btn = MDFloatingActionButton(
            icon="camera",
            size_hint=(None, None),
            size=("80dp", "80dp"),
            pos_hint={"center_x": 0.5},
            on_release=self._capture_photo
        )
        button_layout.add_widget(self.capture_btn)
        layout.add_widget(button_layout)
        
        # Status label
        self.status_label = MDLabel(
            text=self.status_text,
            halign="center",
            size_hint_y=None,
            height="30dp"
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def _update_network_status(self, dt):
        """Update network status display"""
        status = self.core.get_network_status()
        self.is_online = status['online']
        
        if self.is_online:
            self.status_text = f"Online - Ready to upload"
        else:
            self.status_text = "Offline - Photos saved locally"
    
    def _capture_photo(self, instance):
        """Handle photo capture"""
        self.status_text = "Capturing..."
        self.capture_btn.disabled = True
        
        # Schedule capture in async manner
        Clock.schedule_once(lambda dt: self._perform_capture(), 0.1)
    
    def _perform_capture(self):
        """Perform the actual photo capture"""
        async def capture():
            result = await self.core.capture_photo()
            
            # Update UI on main thread
            def update_ui():
                self.capture_btn.disabled = False
                
                if result['success']:
                    self.status_text = "Photo captured!"
                    self._show_preview(result)
                else:
                    self.status_text = f"Error: {result.get('error', 'Unknown error')}"
            
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
        self.manager.switch_to(preview_screen)
    
    def _show_settings(self, instance):
        """Show settings screen"""
        from ui.screens.settings import SettingsScreen
        settings_screen = SettingsScreen(core=self.core, name="settings")
        self.manager.switch_to(settings_screen)
    
    def _show_network_status(self, instance):
        """Show network status popup"""
        # TODO: Implement network status dialog
        pass
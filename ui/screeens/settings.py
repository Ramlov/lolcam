from kivy.clock import Clock
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDTextButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel

class SettingsScreen(MDScreen):
    """Admin settings screen with PIN protection"""
    
    def __init__(self, core, **kwargs):
        super().__init__(**kwargs)
        self.core = core
        self.name = "settings"
        self.pin_dialog = None
        self._build_ui()
    
    def _build_ui(self):
        """Build settings UI"""
        layout = MDBoxLayout(orientation='vertical', padding="20dp", spacing="20dp")
        
        # Title
        title = MDLabel(
            text="Admin Settings",
            halign="center",
            theme_text_color="Primary",
            font_style="H4",
            size_hint_y=None,
            height="60dp"
        )
        layout.add_widget(title)
        
        # Settings card
        settings_card = MDCard(
            orientation="vertical",
            padding="20dp",
            spacing="15dp",
            size_hint=(1, None),
            height="400dp"
        )
        
        # Camera settings
        cam_title = MDLabel(text="Camera Settings", font_style="H6")
        settings_card.add_widget(cam_title)
        
        # Flash test button
        self.flash_btn = MDRaisedButton(
            text="Test Flash",
            on_release=self._test_flash,
            size_hint=(None, None),
            size=("150dp", "50dp")
        )
        settings_card.add_widget(self.flash_btn)
        
        # Network settings
        net_title = MDLabel(text="Network Settings", font_style="H6")
        settings_card.add_widget(net_title)
        
        # WiFi configuration
        self.wifi_ssid = MDTextField(
            hint_text="WiFi SSID",
            mode="rectangle"
        )
        settings_card.add_widget(self.wifi_ssid)
        
        self.wifi_password = MDTextField(
            hint_text="WiFi Password", 
            password=True,
            mode="rectangle"
        )
        settings_card.add_widget(self.wifi_password)
        
        layout.add_widget(settings_card)
        
        # Action buttons
        button_layout = MDBoxLayout(spacing="10dp", size_hint_y=None, height="60dp")
        
        back_btn = MDTextButton(
            text="Back",
            on_release=self._go_back
        )
        button_layout.add_widget(back_btn)
        
        save_btn = MDRaisedButton(
            text="Save Settings",
            on_release=self._save_settings
        )
        button_layout.add_widget(save_btn)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)
    
    def on_enter(self):
        """Called when screen is entered - show PIN dialog"""
        self._show_pin_dialog()
    
    def _show_pin_dialog(self):
        """Show PIN verification dialog"""
        self.pin_dialog = MDDialog(
            title="Admin Access",
            text="Enter PIN code:",
            type="custom",
            content_cls=MDBoxLayout(
                orientation="vertical",
                spacing="10dp",
                size_hint_y=None,
                height="100dp"
            ),
            buttons=[
                MDTextButton(text="CANCEL", on_release=self._cancel_pin),
                MDRaisedButton(text="OK", on_release=self._verify_pin)
            ]
        )
        
        self.pin_input = MDTextField(
            hint_text="PIN",
            password=True,
            size_hint_y=None,
            height="50dp"
        )
        self.pin_dialog.content_cls.add_widget(self.pin_input)
        self.pin_dialog.open()
    
    def _verify_pin(self, instance):
        """Verify PIN code"""
        pin = self.pin_input.text
        correct_pin = self.core.config.get('admin.pin_code', '1234')
        
        if pin == correct_pin:
            self.pin_dialog.dismiss()
            self._load_current_settings()
        else:
            self.pin_input.error = True
            self.pin_input.helper_text = "Invalid PIN"
    
    def _cancel_pin(self, instance):
        """Cancel PIN entry and go back"""
        self.pin_dialog.dismiss()
        self._go_back()
    
    def _load_current_settings(self):
        """Load current settings into UI"""
        # Load current WiFi settings if available
        current_ssid = self.core.config.get('wifi.ssid', '')
        self.wifi_ssid.text = current_ssid
    
    def _test_flash(self, instance):
        """Test flash trigger"""
        try:
            success = self.core.camera.test_flash()
            if success:
                self._show_message("Flash Test", "Flash triggered successfully!")
            else:
                self._show_message("Flash Test", "Flash trigger failed. Check serial connection.")
        except Exception as e:
            self._show_message("Error", f"Flash test failed: {str(e)}")
    
    def _save_settings(self, instance):
        """Save settings"""
        try:
            new_settings = {}
            
            # WiFi settings
            if self.wifi_ssid.text:
                new_settings['wifi.ssid'] = self.wifi_ssid.text
            if self.wifi_password.text:
                new_settings['wifi.password'] = self.wifi_password.text
            
            # Update settings
            self.core.update_settings(new_settings, self.pin_input.text)
            self._show_message("Success", "Settings saved successfully!")
            
        except Exception as e:
            self._show_message("Error", f"Failed to save settings: {str(e)}")
    
    def _show_message(self, title, message):
        """Show message dialog"""
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
    
    def _go_back(self, instance=None):
        """Return to live view"""
        self.manager.current = "live_view"
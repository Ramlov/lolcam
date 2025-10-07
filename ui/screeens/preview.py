from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDTextButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog

class PreviewScreen(MDScreen):
    """Screen showing captured photo and QR code"""
    
    status_text = StringProperty("Photo captured successfully!")
    
    def __init__(self, core, session_id, **kwargs):
        super().__init__(**kwargs)
        self.core = core
        self.session_id = session_id
        self.name = "preview"
        self._build_ui()
        Clock.schedule_once(self._generate_qr, 0.5)
    
    def _build_ui(self):
        """Build preview UI"""
        layout = BoxLayout(orientation='vertical', padding="20dp", spacing="20dp")
        
        # Title
        title = MDLabel(
            text="Photo Captured!",
            halign="center",
            theme_text_color="Primary",
            font_style="H4"
        )
        layout.add_widget(title)
        
        # Status
        self.status_label = MDLabel(
            text=self.status_text,
            halign="center",
            theme_text_color="Secondary"
        )
        layout.add_widget(self.status_label)
        
        # QR Code area
        qr_card = MDCard(
            orientation="vertical",
            padding="20dp",
            size_hint=(1, 0.6),
            elevation=4
        )
        
        qr_title = MDLabel(
            text="Scan to access your photos",
            halign="center",
            theme_text_color="Primary",
            font_style="H6"
        )
        qr_card.add_widget(qr_title)
        
        self.qr_container = BoxLayout(
            size_hint=(1, 0.8),
            padding="10dp"
        )
        qr_card.add_widget(self.qr_container)
        
        layout.add_widget(qr_card)
        
        # Action buttons
        button_layout = BoxLayout(
            size_hint=(1, 0.2),
            spacing="10dp"
        )
        
        back_btn = MDTextButton(
            text="Done",
            on_release=self._go_back
        )
        button_layout.add_widget(back_btn)
        
        another_btn = MDRaisedButton(
            text="Take Another",
            on_release=self._take_another
        )
        button_layout.add_widget(another_btn)
        
        layout.add_widget(button_layout)
        self.add_widget(layout)
    
    def _generate_qr(self, dt):
        """Generate and display QR code"""
        try:
            qr_data = self.core.get_session_qr_data(self.session_id)
            if not qr_data:
                self.status_text = "Error: Session not found"
                return
            
            if qr_data['type'] == 'online':
                self._show_online_qr(qr_data)
            else:
                self._show_offline_message(qr_data)
                
        except Exception as e:
            self.status_text = f"Error generating QR: {str(e)}"
    
    def _show_online_qr(self, qr_data):
        """Show online QR code"""
        try:
            # Generate QR code
            import qrcode
            from io import BytesIO
            from kivy.core.image import Image as CoreImage
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data['url'])
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to Kivy texture
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Create Kivy image
            from kivy.uix.image import Image
            kivy_img = Image(
                texture=CoreImage(buffer, ext='png').texture,
                size_hint=(None, None),
                size=("300dp", "300dp"),
                pos_hint={'center_x': 0.5}
            )
            
            self.qr_container.add_widget(kivy_img)
            self.status_text = f"Online - {qr_data['photo_count']} photos available"
            
        except ImportError:
            # Fallback if QR code library not available
            self._show_qr_fallback(qr_data['url'])
    
    def _show_offline_message(self, qr_data):
        """Show offline message instead of QR"""
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        
        offline_layout = MDBoxLayout(
            orientation='vertical',
            spacing="10dp",
            padding="20dp"
        )
        
        icon = MDLabel(
            text="📷",
            halign="center",
            font_style="H2"
        )
        offline_layout.add_widget(icon)
        
        message = MDLabel(
            text="Offline Mode",
            halign="center",
            theme_text_color="Primary",
            font_style="H5"
        )
        offline_layout.add_widget(message)
        
        details = MDLabel(
            text=f"Photos taken: {qr_data['photo_count']}\n\n{qr_data['message']}",
            halign="center",
            theme_text_color="Secondary"
        )
        offline_layout.add_widget(details)
        
        self.qr_container.add_widget(offline_layout)
        self.status_text = f"Offline - {qr_data['photo_count']} photos saved locally"
    
    def _show_qr_fallback(self, url):
        """Show URL as text if QR generation fails"""
        from kivymd.uix.label import MDLabel
        url_label = MDLabel(
            text=f"URL: {url}",
            halign="center",
            theme_text_color="Primary"
        )
        self.qr_container.add_widget(url_label)
    
    def _go_back(self, instance):
        """Return to live view and remove this screen"""
        self.manager.current = "live_view"
        self.manager.remove_widget(self)
    
    def _take_another(self, instance):
        """Take another photo and stay in same session"""
        self.manager.current = "live_view"
        # Keep the session active for next photo
        live_screen = self.manager.get_screen('live_view')
        live_screen.current_session = self.session_id
        self.manager.remove_widget(self)
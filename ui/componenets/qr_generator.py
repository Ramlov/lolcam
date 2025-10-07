import qrcode
from io import BytesIO
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from kivy.properties import StringProperty
from kivy.clock import Clock

class QRGenerator(Image):
    """Component for generating and displaying QR codes"""
    
    qr_data = StringProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(qr_data=self.generate_qr)
    
    def generate_qr(self, instance, value):
        """Generate QR code from data"""
        if not value:
            return
            
        Clock.schedule_once(lambda dt: self._generate_qr_sync(value), 0.1)
    
    def _generate_qr_sync(self, data):
        """Generate QR code synchronously"""
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Create Kivy texture
            core_img = CoreImage(buffer, ext='png')
            self.texture = core_img.texture
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
            # Create error image
            from kivy.graphics import Color, Rectangle
            from kivy.uix.label import Label
            
            # Simple fallback - just show text
            self.clear_widgets()
            error_label = Label(
                text=f"QR Error\n{data[:50]}...",
                color=(1, 0, 0, 1),
                text_size=(self.width, None)
            )
            self.add_widget(error_label)
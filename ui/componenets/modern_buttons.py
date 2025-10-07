from kivy.properties import StringProperty, ListProperty
from kivymd.uix.button import MDRaisedButton, MDFloatingActionButton
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivy.animation import Animation

class ModernButton(MDRaisedButton, RoundedRectangularElevationBehavior):
    """Modern button with animations"""
    
    icon_name = StringProperty()
    bg_color = ListProperty([0.2, 0.6, 0.8, 1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_text_color = "Custom"
        self.text_color = (1, 1, 1, 1)
        self.md_bg_color = self.bg_color
        self.elevation = 2
        
        # Bind press animation
        self.bind(on_press=self.animate_press)
    
    def animate_press(self, instance):
        """Animate button press"""
        anim = Animation(elevation=0, duration=0.1) + Animation(elevation=2, duration=0.1)
        anim.start(self)

class CaptureButton(MDFloatingActionButton):
    """Specialized capture button with pulse animation"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon = "camera"
        self.size_hint = (None, None)
        self.size = ("80dp", "80dp")
        self.elevation = 6
        self.md_bg_color = (0.2, 0.8, 0.4, 1)  # Green color
        
        # Start pulse animation
        self.pulse_animation = None
        self.start_pulse()
    
    def start_pulse(self):
        """Start pulse animation"""
        self.pulse_animation = Animation(
            md_bg_color=(0.3, 0.9, 0.5, 1), 
            duration=1.5
        ) + Animation(
            md_bg_color=(0.2, 0.8, 0.4, 1), 
            duration=1.5
        )
        self.pulse_animation.repeat = True
        self.pulse_animation.start(self)
    
    def stop_pulse(self):
        """Stop pulse animation"""
        if self.pulse_animation:
            self.pulse_animation.cancel(self)
    
    def on_press(self):
        """Handle press with animation"""
        self.stop_pulse()
        anim = Animation(
            size=("70dp", "70dp"), 
            duration=0.1
        ) + Animation(
            size=("80dp", "80dp"), 
            duration=0.1
        )
        anim.start(self)
        self.start_pulse()
from kivy.uix.button import Button
from kivy.properties import StringProperty, NumericProperty


class ResetButton(Button):

    image = StringProperty()
    image_size = NumericProperty(200.0)
    label_spacing = NumericProperty(5.0)

    def __init__(self, *args, **kwargs):
        super(ResetButton, self).__init__(*args, **kwargs)

    def on_press(self):
        self.image = "images/reset_button_red.png"

    def on_release(self):
        self.image = "images/reset_button_green.png"

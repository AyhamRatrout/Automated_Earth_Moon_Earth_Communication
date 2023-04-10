from kivy.uix.togglebutton import ToggleButton
from kivy.properties import StringProperty, NumericProperty, ColorProperty
from kivy.clock import Clock


class OnOffToggle(ToggleButton):

    image = StringProperty()
    image_size = NumericProperty(30.0)
    label_spacing = NumericProperty(5.0)

    _text_height = NumericProperty()
    _state_color = ColorProperty()

    def __init__(self, *args, **kwargs):
        super(OnOffToggle, self).__init__(*args, **kwargs)
        self._update_state_color_async()

    def on_state(self, instance, value):
        self._update_state_color_async()

    def _update_state_color_async(self):
        Clock.schedule_once(self._update_state_color)

    def _update_state_color(self, *args, **kwargs):
        if self.state == 'down':
            self._state_color = [0.0, 1.0, 0.0, 1.0]
        else:
            self._state_color = [1.0, 0.0, 0.0, 1.0]

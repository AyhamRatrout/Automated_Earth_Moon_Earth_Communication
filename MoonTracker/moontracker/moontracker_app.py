from kivy.app import App
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
import pigpio
import moontracker.moontracker_util


class MoonTrackerApp(App):

    _azimuth = NumericProperty(170)
    _elevation = NumericProperty(49.7)

    gpio17_pressed = BooleanProperty(False)

    def on_start(self):
        self.set_up_GPIO_and_IP_popup()

    def on_moontracker_is_on(self, instance, value):
        pass

    def on_moontracker_is_reset(self, instance, value):
        pass

    def set_up_GPIO_and_IP_popup(self):
        self.pi = pigpio.pi()
        self.pi.set_mode(17, pigpio.INPUT)
        self.pi.set_pull_up_down(17, pigpio.PUD_UP)
        Clock.schedule_interval(self._poll_GPIO, 0.05)
        self.popup = Popup(title='IP Addresses',
                           content=Label(text='IP ADDRESS WILL GO HERE'),
                           size_hint=(1, 1), auto_dismiss=False)
        self.popup.bind(on_open=self.update_popup_ip_address)

    def update_popup_ip_address(self, instance):
        interface = "wlan0"
        ipaddr = moontracker.moontracker_util.get_ip_address(interface)
        instance.content.text = "{}: {}".format(interface, ipaddr)

    def on_gpio17_pressed(self, instance, value):
        if value:
            self.popup.open()
        else:
            self.popup.dismiss()

    def _poll_GPIO(self, dt):
        self.gpio17_pressed = not self.pi.read(17)

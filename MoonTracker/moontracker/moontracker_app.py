from kivy.app import App
from kivy.properties import BooleanProperty, NumericProperty, AliasProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from math import fabs
import platform
import pigpio
import moontracker.moontracker_util

if 'arm' not in platform.platform():
    class MoonTrackerAzimuthDriver(object):
        def set_azimuth_position(self, delta_azimuth):
            pass

    class MoonTrackerElevationDriver(object):
        def set_elevation_position(self, delta_elevation):
            pass

else:
    from .drivers.moontracker_azimuth_driver import MoonTrackerAzimuthDriver
    from .drivers.moontracker_elevation_driver import MoonTrackerElevationDriver


TOLERANCE = 0.25

class MoonTrackerApp(App):

    azimuth = NumericProperty(5)
    elevation = NumericProperty(10)
    moontracker_is_on = BooleanProperty(False)
    gpio17_pressed = BooleanProperty(False)

    def on_start(self):
        self.set_up_GPIO_and_IP_popup()

    def on_moontracker_is_on(self, instance, value):
        if not value:
            self.azimuth = 0
            self.elevation = 0
        else:
            self.azimuth = 5
            self.elevation = 10
        Clock.schedule_once(lambda dt: self._update_azimuth_motor(), 0.01)
        Clock.schedule_once(lambda dt: self._update_elevation_motor(), 0.01)

    def on_moontracker_is_reset(self, instance, value):
        if self.moontracker_is_on:
            self.azimuth = 0
            self.elevation = 0
            Clock.schedule_once(lambda dt: self._update_azimuth_motor())
            Clock.schedule_once(lambda dt: self._update_elevation_motor())

    def _update_azimuth_motor(self):
        print(self.azimuth)
        

    def _update_elevation_motor(self):
        print(self.elevation)
        

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

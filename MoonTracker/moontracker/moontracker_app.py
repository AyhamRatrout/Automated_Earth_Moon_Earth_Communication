from kivy.app import App
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from math import fabs
import platform
import pigpio
import random
import time
import json
from paho.mqtt.client import Client
from moontracker_common import *
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


class MoonTrackerApp(App):
    _updatingUI = False
    azimuth = NumericProperty(5)
    elevation = NumericProperty(10)
    moontracker_is_on = BooleanProperty(False)
    gpio17_pressed = BooleanProperty(False)

    def on_start(self):
        self._publish_clock = None
        self.mqtt = Client()
        self.mqtt.enable_logger()
        self.mqtt.on_connect = self.on_connect
        self.azimuth_driver = MoonTrackerAzimuthDriver()
        self.elevation_driver = MoonTrackerElevationDriver()
        self.set_up_GPIO_and_IP_popup()

    def on_moontracker_is_on(self, instance, value):
        if not value:
            Clock.schedule_once(lambda dt: self._update_values_and_motors(0.0, 0.0), 0.01)
            print('off')
        else:
            self.azimuth = random.randint(0, 360)
            self.elevation = random.randint(0, 180)
            print('on')

    def on_moontracker_is_reset(self, instance, value):
        if value and self.moontracker_is_on:
            Clock.schedule_once(lambda dt: self._update_values_and_motors(0.0, 0.0), 0.01)
            print('reset')

    def _update_values_and_motors(self, new_azimuth, new_elevation):
        if fabs(self.azimuth - new_azimuth) > TOLERANCE:
            delta_azimuth = new_azimuth - self.azimuth
            Clock.schedule_once(lambda dt: self._update_azimuth_motor(delta_azimuth), 0.01)
            self.azimuth = new_azimuth
            print('updating azimuth...')
        if fabs(self.elevation - new_elevation) > TOLERANCE:
            delta_elevation = new_elevation - self.elevation
            Clock.schedule_once(lambda dt: self._update_elevation_motor(delta_elevation), 0.01)
            self.elevation = new_elevation
            print('updating elevation...')

    def _update_azimuth_motor(self, delta_azimuth):
        Clock.schedule_once(lambda st: self.azimuth_driver.set_azimuth_position(delta_azimuth), 0.01)
        print('azimuth updated!')

    def _update_elevation_motor(self, delta_elevation):
        Clock.schedule_once(lambda dt: self.elevation_driver.set_elevation_position(delta_elevation), 0.01)
        print('elevation updated!')

    def on_connect(self, client, userdata, flags, rc):
        self.mqtt.subscribe(TOPIC_TRACKER_CHANGE_NOTIFICATION)
        self.mqtt.message_callback_add(TOPIC_TRACKER_CHANGE_NOTIFICATION,
                                        self.receive_new_moontracker_state)

    def receive_new_moontracker_state(self, client, userdata, message):
        new_state = json.loads(message.payload.decode('utf-8'))
        Clock.schedule_once(lambda dt: self._update_ui(new_state), 0.01)

    def _update_ui(self, new_state):
        self._updatingUI = True
        try:
            pass
        finally:
            self._updatingUI = False

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

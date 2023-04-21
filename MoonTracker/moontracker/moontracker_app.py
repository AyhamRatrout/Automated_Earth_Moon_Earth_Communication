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


class MoonTrackerApp(App):
    _updatingUI = False
    azimuth = NumericProperty()
    elevation = NumericProperty()
    moontracker_is_on = BooleanProperty()
    gpio17_pressed = BooleanProperty(False)

    def on_start(self):
        self._publish_clock = None
        self.mqtt = Client()
        self.mqtt.enable_logger()
        self.mqtt.on_connect = self.on_connect
        self.mqtt.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT,
                          keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
        self.mqtt.loop_start()
        self.set_up_GPIO_and_IP_popup()

    def on_moontracker_is_on(self, instance, value):
        if self._updatingUI:
            return
        if self._publish_clock is None:
            if not value:
                self.azimuth = 0.0
                self.elevation = 0.0
                print('off')
            else:
                print('on')
            self._publish_clock = Clock.schedule_once(
                    lambda dt: self._update_motors_positions(), 0.01)

    def on_moontracker_is_reset(self, instance, value):
        if self._updatingUI:
            return
        if self._publish_clock is None:
            if value and self.moontracker_is_on:
                self.azimuth = 0.0
                self.elevation = 0.0
                self._publish_clock = Clock.schedule_once(
                    lambda dt: self._update_motors_positions(), 0.01)
                print('reset')

    def _update_motors_positions(self):
            msg = {'azimuth': self.azimuth,
                   'elevation': self.elevation,
                   'on': self.moontracker_is_on}
            self.mqtt.publish(TOPIC_SET_TRACKER_CONFIG,
                              json.dumps(msg).encode('utf-8'))
            self._publish_clock = None

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
            if 'azimuth' in new_state:
                self.azimuth = new_state['azimuth']
            if 'elevation' in new_state:
                self.elevation = new_state['elevation']
            if 'on' in new_state:
                self.moontracker_is_on = new_state['on']
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

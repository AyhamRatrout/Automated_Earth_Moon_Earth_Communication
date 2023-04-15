#!/usr/bin/env python3
import json
import pigpio
import shelve
import platform
import math
from threading import Thread
import paho.mqtt.client as mqtt
from moontracker_common import *


if 'arm' not in platform.platform():
    class MoonTrackerAzimuthDriver(object):
        def set_azimuth_position(self, delta_azimuth):
            pass

    class MoonTrackerElevationDriver(object):
        def set_elevation_position(self, delta_elevation):
            pass

else:
    from .moontracker.drivers.moontracker_azimuth_driver import MoonTrackerAzimuthDriver
    from .moontracker.drivers.moontracker_elevation_driver import MoonTrackerElevationDriver


MOONTRACKER_STATE_FILENAME = "moontracker_state"

MQTT_CLIENT_ID = "moontracker_service"


class InvalidMoonTrackerConfig(Exception):
    pass


class MoonTrackerService(object):

    def __init__(self):
        self.azimuth_driver = MoonTrackerAzimuthDriver()
        self.elevation_driver = MoonTrackerElevationDriver()
        self._client = self._create_and_configure_broker_client()
        self.db = shelve.open(MOONTRACKER_STATE_FILENAME, writeback=True)

        if 'azimuth' not in self.db:
            self.db['azimuth'] = round(0.0, FP_DIGITS) # pull from library here
        if 'elevation' not in self.db:
            self.db['elevation'] = round(0.0, FP_DIGITS) # pull from library here
        if 'on' not in self.db:
            self.db['on'] = True
        if 'client' not in self.db:
            self.db['client'] = ''

        # update hardware here

    def _create_and_configure_broker_client(self):
        client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=MQTT_VERSION)
        client.enable_logger()
        client.on_connect = self.on_connect
        client.message_callback_add(TOPIC_SET_TRACKER_CONFIG,
                                    self.on_message_set_config)
        client.on_message = self.defualt_on_message
        return client

    def serve(self):
        self._client.connect(MQTT_BROKER_HOST,
                                port=MQTT_BROKER_PORT,
                                keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
        self._client.loop_forever()

    def on_connect(self, client, userdata, rc, unknown):
        self._client.subscribe(TOPIC_SET_TRACKER_CONFIG)

    def default_on_message(self, client, userdata, msg):
        print("Received unexpected message on topic " +
              msg.topic + " with payload {" + str(msg.payload) + "}")

    def on_message_set_config(self, client, userdata, msg):
        try:
            new_config = json.loads(msg.payload.decode('utf-8'))
            if 'client' in new_config:
                self.set_last_client(new_config['client'])
            if 'on' in new_config:
                self.set_current_onoff_status(new_config['on'])
            if 'azimuth' in new_config:
                self.set_current_azimuth(new_config['azimuth'])
            if 'elevation' in new_config:
                self.set_current_elevation(new_config['elevation'])
            self.publish_config_change()
        except InvalidMoonTrackerConfig:
            print("Error applying new settings: " + str(msg.payload))

    def publish_config_change(self):
        config = {'azimuth': self.get_current_azimuth(),
                    'elevation': self.get_current_elevation(),
                    'on': self.get_current_onoff_status(),
                    'client': self.get_last_client()}
        self._client.publish(TOPIC_SET_TRACKER_CONFIG,
                            json.dumps(config).encode('utf-8'), retain=True)

    def get_last_client(self):
        return self.db['client']

    def set_last_client(self, new_client):
        self.db['client'] = new_client

    def get_current_azimuth(self):
        return round(self.db['azimuth'], FP_DIGITS)

    def set_current_azimuth(self, new_azimuth):
        if new_azimuth < 0.0 or new_azimuth > 360.0:
            raise InvalidMoonTrackerConfig()
        self.db['azimuth'] = round(new_azimuth, FP_DIGITS)
        # update hardware here in a new thread

    def get_current_elevation(self):
        return round(self.db['elevation'], FP_DIGITS)

    def set_current_elevation(self, new_elevation):
        if new_elevation < 0.0 or new_elevation > 180.0:
            raise InvalidMoonTrackerConfig()
        self.db['elevation'] = round(new_elevation, FP_DIGITS)
        # update hardware here in a different thread

    def get_current_onoff_status(self):
        return self.db['on']

    def set_current_onoff_status(self, new_onoff_status):
        if new_onoff_status not in [True, False]:
            raise InvalidMoonTrackerConfig()
        self.db['on'] = new_onoff_status
        # update hardware here in a new thread


if __name__ == '__main__':
    moontracker = MoonTrackerService.serve()

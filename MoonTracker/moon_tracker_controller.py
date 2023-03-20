#!usr/bin/env python3
import json
import paho.mqtt.cleint as mqtt
import shelve
from moon_tracker_common import *

TRACKER_STATE_FILENAME = "tracker_state"

MQTT_CLIENT_ID = "tracker_controller"

FP_DIGITS = 2


class InvalidTrackerConfig(Exception):
    pass


class MoonTrackerDriver(object):
    def __init__(self):
        pass


class MoonTrackerController(object):
    def __init__(self):
        self.tracker_driver = MoonTrackerDriver()
        self._client = self._create_and_configure_broker_client()
        self.db = shelve.open(TRACKER_STATE_FILENAME, writeback=True)
        if 'azimuth' not in self.db:
            self.db['azimuth'] = 0.0
        if 'elevation' not in self.db:
            self.db['elevation'] = 0.0
        if 'reset' not in self.db:
            self.db['reset'] = False
        if 'client' not in self.db:
            self.db['client'] = ''

        # update hardware here

    def _create_and_configure_broker_client(self):
        client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=MQTT_VERSION)
        client.enable_logger()
        client.on_connect = self.on_connect
        client.message_callback_add(TOPIC_SET_TRACKER_CONFIG,
                                    self.on_message_set_config)
        client.on_message = self.default_on_message
        return client

    def control(self):
        self._client.connect(MQTT_BROKER_HOST,
                                port=MQTT_BROKER_PORT,
                                keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
        self._client.loop_forever()

    def on_connect(self, client, userdata, rc, unknown):
        self._client.subscribe(TOPIC_SET_TRACKER_CONFIG)

    def default_on_message(self, client, userdata, msg):
        print("Received unexpected message on topic " + msg.topic +
                " with payload: " + str(msg.payload))

    def publish_config_change(self):
        config = {'azimuth': self.get_current_azimuth,
                  'elevation': self.get_current_elevation(),
                  'reset': self.get_current_reset_status(),
                  'client': self.get_last_client()}
        self._client.publish(TOPIC_TRACKER_CHANGE_NOTIFICATION,
                             json.dumps(config).encode('utf-8'), retain=True)

    def get_last_client(self):
        return self.db['client']

    def set_last_client(self, new_client):
        self.db['client'] = new_client

    def get_current_azimuth(self):
        return self.db['azimuth']

    def set_current_azimuth(self, new_azimuth):
        if new_azimuth < 0.0 or new_azimuth > 360.0:
            raise InvalidTrackerConfig()
        self.db['azimuth'] = round(new_azimuth, FP_DIGITS)
        # update driver

    def get_current_elevation(self):
        return self.db['elevation']

    def set_current_elevation(self, new_elevation):
        if new_elevation < 0.0 or new_elevation > 180.0:
            raise InvalidTrackerConfig()
        self.db['elevation'] = round(new_elevation, FP_DIGITS)
        # update hardware

    def get_current_reset_status(self):
        return self.db['reset']

    def set_current_reset_status(self, new_reset_status):
        if new_reset_status not in [True, False]:
            raise InvalidTrackerConfig()
        self.db['status'] = new_reset_status
        self.set_current_elevation(0.0)
        self.set_current_azimuth(0.0)



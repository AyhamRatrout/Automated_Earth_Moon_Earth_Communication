#!/usr/bin/env python3
import json
import pigpio
import shelve
import platform
import math
import paho.mqtt.client as mqtt
from threading import Thread
from moontracker_common import *


if 'arm' not in platform.platform():
    class MoonTrackerAzimuthDriver(object):
        def set_azimuth_position(self, delta_azimuth):
            pass

    class MoonTrackerElevationDriver(object):
        def set_elevation_position(self, delta_elevation):
            pass

else:
    from moontracker.drivers.moontracker_azimuth_driver import MoonTrackerAzimuthDriver
    from moontracker.drivers.moontracker_elevation_driver import MoonTrackerElevationDriver


MOONTRACKER_STATE_FILENAME = "moontracker_state"

MQTT_CLIENT_ID = "moontracker_service"


class InvalidMoonTrackerConfig(Exception):
    pass


class MoonTrackerIsOffException(Exception):
    pass


class SmallAzimuthRotationRequested(Exception):
    pass


class SmallElevationRotationRequested(Exception):
    pass


class MoonTrackerService(object):

    def __init__(self):
        self.azimuth_driver = MoonTrackerAzimuthDriver()
        self.elevation_driver = MoonTrackerElevationDriver()
        self._client = self._create_and_configure_broker_client()
        self.db = shelve.open(MOONTRACKER_STATE_FILENAME, writeback=True)

        if 'azimuth' not in self.db:
            self.db['azimuth'] = round(0.0, FP_DIGITS)
        if 'elevation' not in self.db:
            self.db['elevation'] = round(0.0, FP_DIGITS)
        if 'on' not in self.db:
            self.db['on'] = True
        if 'client' not in self.db:
            self.db['client'] = ''

    def _create_and_configure_broker_client(self):
        client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=MQTT_VERSION)
        client.enable_logger()
        client.on_connect = self.on_connect
        client.message_callback_add(TOPIC_SET_TRACKER_CONFIG,
                                    self.on_message_set_config)
        client.on_message = self.default_on_message
        return client

    def serve(self):
        self._client.connect(MQTT_BROKER_HOST,
                             port=MQTT_BROKER_PORT,
                             keepalive=MQTT_BROKER_KEEP_ALIVE_SECS)
        self._client.loop_forever()

    def on_connect(self, client, userdata, rc, unknown):
        print('connected')
        self._client.subscribe(TOPIC_SET_TRACKER_CONFIG)

    def default_on_message(self, client, userdata, msg):
        print("Received unexpected message on topic " +
              msg.topic + " with payload {" + str(msg.payload) + "}")

    def on_message_set_config(self, client, userdata, msg):
        try:
            new_config = json.loads(msg.payload.decode('utf-8'))
            print(new_config)
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
        print('publishing')
        config = {'azimuth': self.get_current_azimuth(),
                  'elevation': self.get_current_elevation(),
                  'on': self.get_current_onoff_status(),
                  'client': self.get_last_client()}
        self._client.publish(TOPIC_TRACKER_CHANGE_NOTIFICATION,
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
        if not self.get_current_onoff_status():
            raise MoonTrackerIsOffException()
        #if fabs(new_azimuth - self.get_current_azimuth()) < TOLERANCE:
        #    raise SmallAzimuthRotationRequested()
        self.db['azimuth'] = round(new_azimuth, FP_DIGITS)
        self._update_db()

    def get_current_elevation(self):
        return round(self.db['elevation'], FP_DIGITS)

    def set_current_elevation(self, new_elevation):
        if new_elevation < 0.0 or new_elevation > 180.0:
            raise InvalidMoonTrackerConfig()
        if not self.get_current_onoff_status():
            raise MoonTrackerIsOffException()
        #if fabs(new_elevation - self.get_current_elevation()) < TOLERANCE:
        #    raise SmallElevationRotationRequested()
        # Update persisted elevtion position and hardware in a new thread
        self.db['elevation'] = round(new_elevation, FP_DIGITS)
        self._update_db()

    def get_current_onoff_status(self):
        return self.db['on']

    def set_current_onoff_status(self, new_onoff_status):
        if new_onoff_status not in [True, False]:
            raise InvalidMoonTrackerConfig()
        self.db['on'] = new_onoff_status
        self._update_db()
        # update hardware here in a new thread

    def _update_db(self):
        self.db.close()
        self.db = shelve.open(MOONTRACKER_STATE_FILENAME, writeback=True)

if __name__ == '__main__':
    moontracker = MoonTrackerService().serve()

import json
import pigpio
import shelve
import paho.mqtt.client as mqtt
from moontracker_common import *

MOONTRACKER_STATE_FILENAME = "moontracker_state"

MQTT_CLIENT_ID = "moontracker_service"

FP_DIGITS = 2


class InvalidMoonTrackerConfig(Exception):
    pass


class MoonTrackerService(object):

    def __init__(self):
        self._client = self._create_and_configure_broker_client()
        self.db = shelve.open(MOONTRACKER_STATE_FILENAME, writeback=True)

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
              msg.topic + " with payload '" + str(msg.payload) + "'")


if __name__ == '__main__':
    moontracker = MoonTrackerService.serve()

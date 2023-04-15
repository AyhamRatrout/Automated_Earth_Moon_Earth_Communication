import paho.mqtt.client

# Global Variables
FP_DIGITS = 2

# MQTT Topic Names
TOPIC_SET_TRACKER_CONFIG = "moontracker/set_config"
TOPIC_TRACKER_CHANGE_NOTIFICATION = "moontracker/changed"
#TOPIC_TRACKER_RESET_NOTIFICATION = "moontracker/reset"

# MQTT Broker Connection info
MQTT_VERSION = paho.mqtt.client.MQTTv311
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_BROKER_KEEP_ALIVE_SECS = 60

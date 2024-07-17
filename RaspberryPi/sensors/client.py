import paho.mqtt.client as mqtt
import time
from datetime import datetime
import json

class Client:
    def __init__(self, type_id, instance_id):
        self.id = instance_id
        self.type_id = type_id
        self.mqtt_publisher = mqtt.Client('Publisher')
        self.mqtt_publisher.connect('127.0.0.1', 1883, 70)
        self.mqtt_publisher.loop_start()
    
    def send_msg(self, msg):
        dt = datetime.now().strftime("%d-%m-%YT%H:%M:%S")
        message = {
        "type-id": self.type_id,
        "instance-id": self.id,
        "timestamp": dt,
        "value": msg
        }
        jmsg = json.dumps(message, indent=4)
        self.mqtt_publisher.publish('sensor/' + str(self.type_id) + '/' + str(self.id), jmsg, 2)
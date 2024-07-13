"""
MQTT subscriber used to turn the led water pump relay on for a specific period of time

Author: Ondrej Galeta
Date: 17.7.2024
"""
import paho.mqtt.client as mqtt
import grovepi
import time

# Variables
port = 2
on_duration = 1

def on_message(client, userdata, message):
    # turn relay on for 
    grovepi.digitalWrite(port, 1)
    time.sleep(on_duration)
    grovepi.digitalWrite(port, 0)


def on_connect(client, userdata, flags, rc):
    print("Water pump connected to gateway")

# crate mqtt subsciber
mqtt_subscriber = mqtt.Client('Water pump subscriber')
mqtt_subscriber.on_message = on_message
mqtt_subscriber.on_connect = on_connect
mqtt_subscriber.connect('127.0.0.1', 1883, 70)
mqtt_subscriber.subscribe('actuator/water_pump', qos=2)
mqtt_subscriber.loop_forever()

grovepi.pinMode(port, "OUTPUT")
grovepi.digitalWrite(port, 0)
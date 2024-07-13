"""
Led Controll Script
MQTT subscriber used to turn the led water level indicator on/off

Author: Ondrej Galeta
Date: 17.7.2024
"""
import paho.mqtt.client as mqtt
import grovepi

# Variables
port = 8

def on_message(client, userdata, message):
    # turn led on/off
    state = message.payload.decode()
    if state == "True":
        grovepi.digitalWrite(port, 1)
    elif state == "False":
        grovepi.digitalWrite(port, 0)
    else:
        return 


def on_connect(client, userdata, flags, rc):
    print("Led indicator connected to gateway")

grovepi.pinMode(port, "OUTPUT")
grovepi.digitalWrite(port, 0)

# create mqtt subsciber
mqtt_subscriber = mqtt.Client('Led indicator subscriber')
mqtt_subscriber.on_message = on_message
mqtt_subscriber.on_connect = on_connect
mqtt_subscriber.connect('127.0.0.1', 1883, 70)
mqtt_subscriber.subscribe('actuator/led_indicator', qos=2)
mqtt_subscriber.loop_forever()


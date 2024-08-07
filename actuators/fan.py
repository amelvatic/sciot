"""
Fan 
MQTT subscriber used to turn fan on/off

Author: Ondrej Galeta
Date: 17.7.2024
"""
import paho.mqtt.client as mqtt
import grovepi

# Variables
port = 7

def on_message(client, userdata, message):
    # turn led on/off
    state = message.payload.decode()
    print("Fan state changed to ", message.payload.decode())
    if state == "True":
        grovepi.digitalWrite(port, 1)
    elif state == "False":
        grovepi.digitalWrite(port, 0)
    else:
        return 


def on_connect(client, userdata, flags, rc):
    print("Fan connected to gateway")

grovepi.pinMode(port, "OUTPUT")
grovepi.digitalWrite(port, 0)


# create mqtt subsciber
mqtt_subscriber = mqtt.Client('Fan subscriber')
mqtt_subscriber.on_message = on_message
mqtt_subscriber.on_connect = on_connect
mqtt_subscriber.connect('127.0.0.1', 1883, 70)
mqtt_subscriber.subscribe('actuator/fan', qos=2)
mqtt_subscriber.loop_forever()


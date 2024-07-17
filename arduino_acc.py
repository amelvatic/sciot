"""
MQTT client and publisher used to communicate between gateway and arduino module MQTT->serial. 
Arduino has a lighting actuator, stepper motor/servo used to open lid and soil humidity sensor

Author: Ondrej Galeta
Date: 17.7.2024
"""
import paho.mqtt.client as mqtt
import time
from datetime import datetime
import json
import serial

id = 4
period = 10

def on_message(client, userdata, message):
    print("GOT MESSAGE")
    state = message.payload.decode()
    if message.topic == "actuator/light":
        # data_to_send = "none"
        if state == "True":
            data_to_send = "LIGHT_ON"
        elif state == "False":
            data_to_send = "LIGHT_OFF"
        else:
            return 
    elif message.topic == "actuator/servo":
        if state == "True":
            data_to_send = "LID_OPEN"
        elif state == "False":
            data_to_send = "LID_CLOSE"
        else:
            return 
    ser.write(data_to_send.encode())

    # time.sleep(1)
    # response = ser.readline().decode()
    # if (response != "Light: ON\n\r" and state == "True") or (response != "Light: OFF\n\r" and state == "False"):
    #     print("Received: ", response)


def on_connect(client, userdata, flags, rc):
    print("Arduino connected to Gateway")

def get_soil_humidity():
    ser.write("GET_HUMIDITY".encode())
    time.sleep(1)
    mes = ser.readline().decode()
    while "Soil_moisture_level" != mes.split(':')[0]:
        ser.write("GET_HUMIDITY".encode())
        mes = ser.readline().decode()
    ser.readline().decode()
    return int(mes[:-2].split(':')[1])

mqtt_subscriber = mqtt.Client('Temperature subscriber')
mqtt_subscriber.on_message = on_message
mqtt_subscriber.on_connect = on_connect
mqtt_subscriber.connect('127.0.0.1', 1883, 70)
mqtt_subscriber.subscribe('actuator/light', qos=2)
mqtt_subscriber.subscribe('actuator/servo', qos=2)
mqtt_subscriber.loop_start()

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

while True:
    time.sleep(period-1)
    soil_humidity = get_soil_humidity()
    dt = datetime.now().strftime("%d-%m-%YT%H:%M:%S")
    message = {
    "type-id": "soil_humidity",
    "instance-id": id,
    "timestamp": dt,
    "value": soil_humidity
    }
    jmsg = json.dumps(message, indent=4)

    mqtt_subscriber.publish('sensor/soil_humidity/'+str(id), jmsg, 2)
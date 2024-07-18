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
    ser.flush() 
    state = message.payload.decode()
    if message.topic == "actuator/light":
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


def on_connect(client, userdata, flags, rc):
    print("Arduino connected to Gateway")

def get_soil_humidity():
    try:
        time.sleep(0.5) 
        ser.flush()
        ser.write("GET_HUMIDITY".encode())
        time.sleep(0.5)
        mes = ser.readline()
        mes = mes.decode()
        return int(mes[:-2].split(':')[1])
    except:
        print("Humidity not received")
        return None

def get_lid_state():
    try:
        ser.flush() 
        ser.write("GET_LID_STATE".encode())
        time.sleep(1)
        mes = ser.readline()
        mes = mes.decode()
        return mes
    except:
        print("LID STATE NOT SEND")
        return None   
    
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
mqtt_subscriber = mqtt.Client('Temperature subscriber')
mqtt_subscriber.on_message = on_message
mqtt_subscriber.on_connect = on_connect
mqtt_subscriber.connect('127.0.0.1', 1883, 70)
mqtt_subscriber.subscribe('actuator/light', qos=2)
mqtt_subscriber.subscribe('actuator/servo', qos=2)
mqtt_subscriber.loop_start()


time.sleep(period-2)
lid_state = get_lid_state()
message = {
"type-id": "lid_state",
"instance-id": id,
"timestamp": datetime.now().strftime("%d-%m-%YT%H:%M:%S"),
"value": int(lid_state)
}
jmsg = json.dumps(message, indent=4)
mqtt_subscriber.publish('sensor/lid_state', jmsg, 2)
while True:
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

    time.sleep(period-1)
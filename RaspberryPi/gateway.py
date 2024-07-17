"""
MQTT client and subscriber used as gateway, collects data from sensors, save them to db and control actuators

Author: Ondrej Galeta
Date: 17.7.2024
"""
import paho.mqtt.client as mqtt
import time
from datetime import datetime
import json
from multiprocessing.connection import Client
import telegram_bot

def water_pump_on():
    _mqtt_gateway.publish('actuator/water_pump', " ", 2)

def servo(state):
    global lid_open
    if lid_open != state:
        _mqtt_gateway.publish('actuator/servo', str(state), 2)
        lid_open = state

def fan(state):
    global fan_state
    _mqtt_gateway.publish('actuator/fan', str(state), 2)
    fan_state = state

def light(state):
    global light_on, _mqtt_gateway
    _mqtt_gateway.publish('actuator/light', str(state), 2)
    light_on = state

def indicator_led(state):
    global led_indicator
    message = datetime.today().strftime('%Y-%m-%d - %H:%M:%S') + ": The water tank needs to be refilled."
    telegram_bot.bot(msg=message, tkn=telegram_bot.api_key)
    _mqtt_gateway.publish('actuator/led_indicator', str(state), 2)
    led_indicator = state

def on_message(client, userdata, message):
    #print('Gateway recieved message from {}'.format(message.topic))
    dbms_address = ('localhost', 6000)
    try:
        with Client(dbms_address, authkey=b'pw') as conn:
            conn.send(["append", json.loads(message.payload.decode())])
        if json.loads(message.payload.decode())["type-id"] == "air_t&h":
            dt = datetime.now().strftime("%d-%m-%YT%H:%M:%S")
            state_mes = {
                "type-id": "act_states",
                "instance-id": 69,
                "timestamp": dt,
                "value": [lid_open, light_on, led_indicator, fan_state]
                }
            try:
                with Client(dbms_address, authkey=b'pw') as conn:
                    conn.send(["append", state_mes])
            except:
                pass
    except:
        pass

def on_connect(client, userdata, flags, rc):
    print("Gateway got connected")


lid_open = False
light_on = False
led_indicator = False
fan_state = False

manual_control = False

_mqtt_gateway = mqtt.Client('Gateway')
_mqtt_gateway.on_message = on_message
_mqtt_gateway.on_connect = on_connect
_mqtt_gateway.connect('127.0.0.1', 1883, 70)
_mqtt_gateway.subscribe('sensor/water_level/+', qos=2)
_mqtt_gateway.subscribe('sensor/light/+', qos=2)
_mqtt_gateway.subscribe('sensor/air_t&h/+', qos=2)
_mqtt_gateway.subscribe('sensor/soil_humidity/+', qos=2)

def x():
    _mqtt_gateway.loop_start()
    while True:
        pass

if __name__ == '__main__':
    #pass
    #gate = Gateway()
    time.sleep(5)
    fan(True)
    print("Fan TURNED ON")

    # # gate.water_pump_on()
    # gate.fan(True)
    # time.sleep(2)
    # gate.fan(False)


    while True:
        pass

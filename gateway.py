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

class Gateway:
    def __init__(self):
        self._mqtt_gateway = mqtt.Client('Gateway')
        self._mqtt_gateway.on_message = self.on_message
        self._mqtt_gateway.on_connect = self.on_connect
        self._mqtt_gateway.connect('127.0.0.1', 1883, 70)
        self._mqtt_gateway.subscribe('sensor/water_level/+', qos=2)
        self._mqtt_gateway.subscribe('sensor/light/+', qos=2)
        self._mqtt_gateway.subscribe('sensor/air_t&h/+', qos=2)
        self._mqtt_gateway.subscribe('sensor/soil_humidity/+', qos=2)
        self._mqtt_gateway.loop_start()

        self.lid_open = False
        self.light_on = False
        self.led_indicator = False
        self.fan_state = False

    def water_pump_on(self):
        self._mqtt_gateway.publish('actuator/water_pump', " ", 2)

    def servo(self, state):
        if self.lid_open != state:
            self._mqtt_gateway.publish('actuator/servo', str(state), 2)
            self.lid_open = state

    def fan(self, state):
        self._mqtt_gateway.publish('actuator/fan', str(state), 2)
        self.fan_state = state

    def light(self, state):
        self._mqtt_gateway.publish('actuator/light', str(state), 2)
        self.light_on = state

    def indicator_led(self, state):
        self._mqtt_gateway.publish('actuator/led_indicator', str(state), 2)
        self.led_indicator = state

    def on_message(self, client, userdata, message):
        print('Gateway recieved message from {}'.format(message.topic))
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
                    "value": [self.lid_open, self.light_on, self.led_indicator, self.fan_state]
                    }
                try:
                    with Client(dbms_address, authkey=b'pw') as conn:
                        conn.send(["append", state_mes])
                except:
                    pass
        except:
            pass

    def on_connect(self, client, userdata, flags, rc):
        print("Gateway got connected")

if __name__ == '__main__':
    gate = Gateway()
    time.sleep(5)
    gate.light(False)

    # # gate.water_pump_on()
    # gate.fan(True)
    # time.sleep(2)
    # gate.fan(False)


    while True:
        pass


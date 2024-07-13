"""
MQTT client used to read data from grovepi temperature and humidity sensor

Author: Ondrej Galeta
Date: 17.7.2024
"""
import grovepi
from client import Client
import argparse
import time
import math

# VARIABLES
port = 4
period = 10

def get_air_temperature_and_humidity(port):
    temperature, air_humidity = grovepi.dht(port, 0) # 0 - according to our sensor type
    if math.isnan(temperature) or math.isnan(air_humidity):  # check if we have a valid reading
        return None, None
    return temperature, air_humidity

parser = argparse.ArgumentParser(description='MQTT client script')
parser.add_argument('--id', type=int, default=1, help='MQTT broker address')
args = parser.parse_args()
client_ins = Client("air_t&h", args.id)

while True:
    time.sleep(period)
    temperature, air_humidity = get_air_temperature_and_humidity(port)
    client_ins.send_msg([temperature, air_humidity])

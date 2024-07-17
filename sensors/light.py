"""
MQTT client used to read data from grovepi light sensor

Author: Ondrej Galeta
Date: 17.7.2024
"""

import grovepi
from client import Client
import argparse
import time

# VARIABLES
port = 0
period = 10

def get_luminance(port):
    full_light = 5
    full_dark = 30
    try:
        val = grovepi.analogRead(port)
        light_level = (val - full_light) / (full_dark - full_light) * 100
        
        # align any inaccuracies
        if light_level > 100:
            light_level = 100
        elif light_level < 0:
            light_level = 0
        
        return val
    except IOError:
        print("Error reading from the light sensor")
        return None

def map_value(x, in_min=0, in_max=710, out_min=0, out_max=100):
    ret = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    return min(ret, 100)

parser = argparse.ArgumentParser(description='MQTT client script')
parser.add_argument('--id', type=int, default=3, help='MQTT broker port')
args = parser.parse_args()
client_ins = Client("light", args.id)

while True:
    time.sleep(period)
    client_ins.send_msg(int(map_value(get_luminance(port))))
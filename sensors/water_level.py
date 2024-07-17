"""
MQTT client used to read data from grovepi ultrasonic sensor to measure water level of tank

Author: Ondrej Galeta
Date: 17.7.2024
"""
import grovepi
from client import Client
import argparse
import time

# VARIABLE
port = 3
period = 10


# generated via CHATGPT
def most_common_value(water_levels):
    if not water_levels:
        return None

    count_dict = {}
    
    # Count occurrences of each element in the list
    for level in water_levels:
        if level in count_dict:
            count_dict[level] += 1
        else:
            count_dict[level] = 1
    
    # Find the element with the highest count
    most_common = None
    max_count = 0
    
    for level, count in count_dict.items():
        if count > max_count:
            max_count = count
            most_common = level
    
    return most_common

# end generated via CHATGPT

def map_value(x, in_min=0, in_max=12, out_min=100, out_max=0):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def get_water_tank_level(port):
    try:
        water_levels = []
        for _ in range(5):
            dist = grovepi.ultrasonicRead(port)
            water_level = map_value(dist)
            
            # align any inaccuracies
            if water_level > 100:
                water_level = 100
            elif water_level < 0:
                water_level = 0
            water_levels.append(water_level)
            time.sleep(0.01)
        
        return most_common_value(water_levels)
    except IOError:
        print("Error reading from the water tank level sensor")
        return None

parser = argparse.ArgumentParser(description='MQTT client script')
parser.add_argument('--id', type=int, default=2, help='MQTT broker address')
args = parser.parse_args()
client_ins = Client("water_level", args.id)


while True:
    time.sleep(period)
    level = get_water_tank_level(port)
    client_ins.send_msg(level)
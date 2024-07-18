from datetime import datetime
import json
import random
import socket
import time

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = socket.gethostbyname('dex')
print(socket.gethostbyname('dex'))
server_port = 10001
buffer_size = 1024

'''
    if 'water_level' in self.input_data:
               try:
                    values = []
                    for reading in self.input_data['water_level']:
                         if(reading!=''):
                              v = reading.strip().split(',')[1]
                              values += [float(v)]

                    most_common_value = float(max(set(values), key=values.count))
                    if most_common_value >= water_level_threshold:
                         context += ["tank-full s"]
               except Exception as e:
                    print("Wrong data format: water_level: " + str(e))
          
          if 'soil_humidity' in self.input_data:
               try:
                    values = []
                    for reading in self.input_data['soil_humidity']:
                         v = reading.strip().split(',')[1]
                         values += [float(v)]

                    latest_value = float(values[len(values)-1])

                    if latest_value < soil_hum_threshold:
                         context += ["low-soil-hum s"]
               except Exception as e:
                    print("Wrong data format: soil_humidity: " + str(e))'''

intervall = 5

type_id = 0
instance_id = 0
filename = '/home/amel/dev/sciot2/sciot/samples/temp.csv'
filenames={ 'air_t&h': 'temp_hum_data.txt',
            'soil_humidity': 'soil_hum_data.txt',
            'water_level': 'waterlevel_data.txt', 
            'act_states': 'actuator_states_data.txt'}

while True: 
    try:
        message = '{},{}'.format("air_t&h", 10)
        client_socket.sendto(message.encode(), (server_address, server_port))
        data, server = client_socket.recvfrom(buffer_size)

        input_data = json.loads(data.decode())

        if 'air_t&h' in input_data:
               try:
                    air_list = []
                    hum_list = []
                    for reading in input_data['air_t&h']:
                        values = reading.strip().split(",[")
                        timestamp = values[0]
                        air_hum = values[1]
                        air_hum = air_hum[:-1]
                        air__and_hum_list = air_hum.split(',')
                        air_list += [timestamp + "," + air__and_hum_list[0].strip()]
                        hum_list += [timestamp + "," + air__and_hum_list[1].strip()]

                    with open('/home/amel/dev/sciot2/sciot/samples/temp.csv', 'w') as file:
                        file.write(",type-id,instance-id,timestamp,value\n")
                        for idx, x in enumerate(air_list):
                            xs = x.split(",")
                            file.write(str(idx) + "," + str(type_id) + "," +  str(instance_id)
                                + "," +  str(xs[0]) + "," + str(xs[1]) + '\n')
                            
                    with open('/home/amel/dev/sciot2/sciot/samples/air_humidity.csv', 'w') as file:
                        file.write(",timestamp,value\n")
                        for idx, x in enumerate(hum_list):
                            xs = x.split(",")
                            file.write(str(idx) + "," +  str(xs[0]) + "," + str(xs[1]) + '\n')
            
               except Exception as e:
                    print("Wrong data format: air_t&h: " + str(e))
        

    except:
        pass

    time.sleep(1)

    try:
        message = '{},{}'.format("soil_humidity", 10)
        client_socket.sendto(message.encode(), (server_address, server_port))
        data, server = client_socket.recvfrom(buffer_size)

        input_data = json.loads(data.decode())

        if 'soil_humidity' in input_data:
               try:
                    with open('/home/amel/dev/sciot2/sciot/samples/soil_humidity.csv', 'w') as file:
                        file.write(",timestamp,value\n")
                        for idx, x in enumerate(input_data['soil_humidity']):
                            file.write(str(idx) + "," + str(x).strip() + '\n')
            
               except Exception as e:
                    print("Wrong data format: air_t&h: " + str(e))
        

    except:
        pass

    time.sleep(1)

    try:
        message = '{},{}'.format("water_level", 10)
        client_socket.sendto(message.encode(), (server_address, server_port))
        data, server = client_socket.recvfrom(buffer_size)

        input_data = json.loads(data.decode())

        if 'water_level' in input_data:
               try:
                    with open('/home/amel/dev/sciot2/sciot/samples/water.csv', 'w') as file:
                        file.write(",timestamp,value\n")
                        for idx, x in enumerate(input_data['water_level']):
                            file.write(str(idx) + "," + str(x).strip() + '\n')
            
               except Exception as e:
                    print("Wrong data format: air_t&h: " + str(e))

    except:
        pass

    time.sleep(intervall)

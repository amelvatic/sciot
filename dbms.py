from multiprocessing import Process
from multiprocessing.connection import Listener
    
class DBMS(Process):
    def __init__(self, filenames={'air_t&h': 'temp_hum_data.txt', 'soil_humidity': 'soil_hum_data.txt', 
                                  'light': 'lum_data.txt',
                                   'weather': 'weather_data.txt', 'water_level': 'waterlevel_data.txt', 
                                   'act_states': 'actuator_states_data.txt', 
                                   'cur_plant_type': 'current_plant_type.txt',
                                   'plant_values': 'plant_values.txt'}):
        super(DBMS, self).__init__()
        self.filenames = filenames
        self.key_list = list(self.filenames.keys())
        self.val_list = list(self.filenames.values())
        
    def run(self):
        dbms_address = ('localhost', 6000)

        #cache
        #number_of_cached_values = 10
        #cache = {key:[None for _ in range(number_of_cached_values)] for key in self.filenames}

        while True:
            try:
                with Listener(dbms_address, authkey=b'pw') as listener:
                    with listener.accept() as dmbs_conn:
                        msg = dmbs_conn.recv()
                        if(isinstance(msg, list)):
                            if (msg[0] == 'close'):
                                dmbs_conn.close()
                                break
                            elif(msg[0] == 'append') and len(msg)==2:
                                data = msg[1]
                                type_id = data["type-id"]
                                timestamp = data["timestamp"]
                                value = data["value"]

                                if type_id in self.filenames:
                                    filename = self.filenames[type_id]

                                    with open(filename, mode='a') as file:
                                        if(value != None):
                                            file.writelines([timestamp, ',', str(value), '\n'])
                                            #json.dump(json.loads(str(value)), file, indent=0)
                                            #json.dump(value, file, indent=0)


                            elif(msg[0] == 'set') and len(msg) >=3:
                                type_id = msg[1]
                                if(type_id == "cur_plant_type"):
                                    try:
                                        value = msg[2].strip()
                                        if value.isnumeric():
                                            filename = self.filenames[type_id]
                                            with open(filename, 'w') as file:
                                                file.write(value)
                                            print("Changed the current plant type to " + value)
                                    except Exception as e:
                                        print("A" + str(e))

                            elif(msg[0] == 'get') and len(msg) >=2:
                                type_id = msg[1]
                                #print('received request for: ' + str(type_id))

                                no_data_blocks = 1
                                if (len(msg)==3):
                                    no_data_blocks = int(msg[2])

                                response = {}
                                if type_id in self.filenames:
                                    try:
                                        filename = self.filenames[type_id]

                                        with open(filename, mode='r') as file:
                                            if no_data_blocks == -1:
                                                response = file.read()
                                            else:
                                                xs = [None] * (no_data_blocks+1)
                                                try:
                                                    line = file.readline()
                                                    while line:
                                                        xs = xs[-1:] + xs[:-1]
                                                        xs[0] = line
                                                        line = file.readline()
                                                    if(xs[0].strip()==''):
                                                        xs = xs[1:]
                                                    else:
                                                        xs = xs[:-1]
                                                    response[type_id] = xs
                                                except Exception as e:
                                                    print("B" + str(e))
                                    except Exception as e:
                                        print(e)

                                if(type_id=="plant"):
                                    try:
                                        filename1 = self.filenames["cur_plant_type"]
                                        pt = '-1'
                                        with open(filename1, mode='r') as file:
                                            try:
                                                pt = file.read()
                                            except Exception as e:
                                                print(e)
                                        
                                        filename2 = self.filenames["plant_values"]
                                        vals = ''
                                        with open(filename2, mode='r') as file:
                                            try:
                                                line = file.readline()
                                                while line:
                                                    linelist = line.split(",")
                                                    if(linelist[0]==pt):
                                                        vals = line.strip()
                                                        break
                                                    line = file.readline()

                                            except Exception as e:
                                                print("C" + str(e))

                                        response['plant'] = pt + ";" + vals
                                    except Exception as e:
                                        print(e)

                                if type_id == 'all':
                                    try:
                                        response = {}
                                        for filename in self.val_list:
                                            try:
                                                with open(filename, mode='r') as file:
                                                    try:
                                                        sensor_name = self.key_list[self.val_list.index(filename)]
                                                        xs = [None] * (no_data_blocks+1)
                                                        try:
                                                            line = file.readline()
                                                            while line:
                                                                xs = xs[-1:] + xs[:-1]
                                                                xs[0] = line
                                                                line = file.readline()
                                                            
                                                            if(xs[0].strip()==''):
                                                                xs = xs[1:]
                                                            else:
                                                                xs = xs[:-1]
                                                            response[sensor_name] = xs
                                                        except Exception as e:
                                                            print("D" + str(e))
                                                    except Exception as e:
                                                        print(e)
                                            except Exception as e:
                                                print(e)

                                    except Exception as e:
                                        response = ["404"]

                                dmbs_conn.send(response)
            except Exception as e:
                print(e)

if __name__ == '__main__':
    db_process = DBMS()
    db_process.start()

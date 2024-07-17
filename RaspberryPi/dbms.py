from multiprocessing import Process
from multiprocessing.connection import Listener
import json
    
class DBMS(Process):
    def __init__(self, filenames={'air_t&h': 'temp_hum_data.txt', 'soil_humidity': 'soil_hum_data.txt', 
                                  'light': 'lum_data.txt',
                                   'weather': 'weather_data.txt', 'water_level': 'waterlevel_data.txt', 
                                   'act_states': 'actuator_states_data.txt'}):
        super(DBMS, self).__init__()
        self.filenames = filenames
        self.key_list = list(self.filenames.keys())
        self.val_list = list(self.filenames.values())
        
    def run(self):
        dbms_address = ('localhost', 6000)

        #cache
        number_of_cached_values = 10
        cache = {key:[None for _ in range(number_of_cached_values)] for key in self.filenames}

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


                            elif(msg[0] == 'get')  and len(msg) >=2:
                                type_id = msg[1]
                                print('received request for: ' + str(type_id))

                                no_data_blocks = -1
                                if (len(msg)==3):
                                    no_data_blocks = int(msg[2])

                                response = ["404"]
                                if type_id in self.filenames:
                                    try:
                                        filename = self.filenames[type_id]

                                        with open(filename, mode='r') as file:
                                            if no_data_blocks == -1:
                                                response = file.read()
                                            else:
                                                try:
                                                    response = [next(file, '') for _ in range(no_data_blocks)]
                                                except StopIteration:
                                                    pass
                                    except:
                                        pass

                                if type_id == 'all':
                                    try:
                                        n_all = 1
                                        response = []
                                        for filename in self.val_list:
                                            try:
                                                with open(filename, mode='r') as file:
                                                    try:
                                                        sensor_name = self.key_list[self.val_list.index(filename)]
                                                        response += [sensor_name, [next(file, '') for _ in range(n_all)]]
                                                    except StopIteration:
                                                        pass
                                            except:
                                                pass

                                    except Exception as e:
                                        response = ["404"]

                                dmbs_conn.send(response)
            except:
                pass

if __name__ == '__main__':
    db_process = DBMS()
    db_process.start()

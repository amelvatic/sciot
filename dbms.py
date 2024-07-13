from multiprocessing import Process
from multiprocessing.connection import Listener
    
class DBMS(Process):
    def __init__(self, filename='data.csv'):
        super(DBMS, self).__init__()
        self.filename = filename
        
    def run(self):
        dbms_address = ('localhost', 6000)
        while True:
            with Listener(dbms_address, authkey=b'pw') as listener:
                with listener.accept() as dmbs_conn:
                    msg = dmbs_conn.recv()
                    print(msg)
                    if(isinstance(msg, list)):
                        if (msg[0] == 'close'):
                            dmbs_conn.close()
                            #break
                        elif(msg[0] == 'append') and len(msg)==2:
                            data = msg[1]
                        elif(msg[0] == 'get'):
                            no_data_blocks = -1
                            if (len(msg)==2):
                                no_data_blocks = int(msg[1])

                            response = ["abc"]

                            dmbs_conn.send(response)       

def append_file(self, data):
        pass  

if __name__ == '__main__':
    db_process = DBMS()
    db_process.start()

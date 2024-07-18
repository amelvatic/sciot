import dbms
import gateway
import json
from multiprocessing.connection import Client
import reasoning
import socket
import telegram_bot
import time
import threading
import weather_forecast

def datasender():
    print(socket.gethostbyname('dex'))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_address = '192.168.137.108'
    server_port = 10001

    buffer_size = 1024

    dbms_address = ('localhost', 6000)

    server_socket.bind((server_address, server_port))
    print('Server up and running at {}:{}'.format(server_address, server_port))

    while True:

        data, address = server_socket.recvfrom(buffer_size)
        msg = data.decode().strip().split(',')

        if data:
            try:
                datatype = msg[0]
                no_data_blocks = int(float(msg[1]))
                with Client(dbms_address, authkey=b'pw') as conn:
                     conn.send(["get", datatype, no_data_blocks])
                     response = conn.recv()
                     #print(response)
                     if not '404' in response:
                          input_data = response
            
            except Exception as e:
                print(e)

            server_socket.sendto(str.encode(json.dumps(input_data)), address)


if __name__ == '__main__':
    db = dbms.DBMS()
    db.start()    

    datasender_thread = threading.Thread(target=datasender)
    datasender_thread.start()

    #g = gateway1.Gateway()

    #time.sleep(5)

    gateway_thread = threading.Thread(target=gateway.x)
    gateway_thread.start()

    telegram_token = ""
    try:
        with open('keys.txt') as f:
            line = f.readline()
            while line:
                line = line.split(" ")
                if(line[0]=="telegram_bot"):
                    telegram_token = line[1].strip()
                    break
                line = f.readline()
    except Exception as e:
        print(e)
        telegram_token = ""

    if (telegram_token != ""):
        telegram_bot.api_key = telegram_token
        telegram_bot_thread = threading.Thread(target=telegram_bot.get_updates, args=[telegram_token])
        telegram_bot_thread.start()

    weather_thread = threading.Thread(target=weather_forecast.weather_loop)
    weather_thread.start()


    time.sleep(5)

    reasoner = reasoning.Reasoner()
    reasoner.start()

from datetime import datetime
import gateway
import json
import requests
import sys
import threading
import time

api_key = "API_KEY_HERE"

def get_updates(tkn=''):
    update_timeout = 10
    lid_open = False

    highest_update_id = -1

    with open('telegram.txt', 'r') as file:
        highest_update_id = int(file.read().strip())

    while True:
        try:
            answer = requests.get("https://api.telegram.org/bot{}/getUpdates?offset={}".format(tkn, highest_update_id))
            content = answer.content
            data = json.loads(str(content, 'utf-8'))
            results = data['result']

            most_recent_update = max(results, key=lambda x:x['update_id'])
            highest_update_id = most_recent_update['update_id']
            with open('telegram.txt', 'w') as file:
                file.write(str(highest_update_id))

            most_recent_update_message = most_recent_update['message']
            most_recent_update_text = most_recent_update_message['text']
            command_list = most_recent_update_text.lower().split(" ")

            if(command_list[0] == "com"):
                if(len(command_list)>=2):

                    if gateway.manual_control == False:
                        if (command_list[1]=="mc"):
                            if(len(command_list)>=3):
                                if(command_list[2]=="t"):
                                    gateway.manual_control = True
                                    print("Manual Control ON")
                    else:
                        if(command_list[1]=="act"):
                            if(len(command_list)>=3):
                                if(command_list[2]=="light"):
                                    if(len(command_list)>=4):
                                        print(command_list[3])
                                        if(command_list[3]=="on"):
                                            gateway.light(True)
                                        elif(command_list[3]=="off"):
                                            gateway.light(False)
                                            gateway.water_pump_on()
                                elif(command_list[2]=="fan"):
                                    if(len(command_list)>=4):
                                        print(command_list[3])
                                        if(command_list[3]=="on"):
                                            gateway.fan(True)
                                        elif(command_list[3]=="off"):
                                            gateway.fan(False)
                                elif(command_list[2]=="lid"):
                                    if(len(command_list)>=4):
                                        print(command_list[3])
                                        print(lid_open)
                                        if(command_list[3]=="open"):
                                            if not lid_open:
                                                lid_open = True
                                                gateway.servo(True)
                                        elif(command_list[3]=="close"):
                                            if lid_open:
                                                lid_open = False
                                                gateway.servo(False)
                                else:
                                    pass
                        elif (command_list[1]=="mc"):
                            if(len(command_list)>=3):
                                if(command_list[2]=="f"):
                                    gateway.manual_control = False
                                    print("Manual Control OFF")
                        else:
                            pass
                    

        except requests.exceptions.ConnectionError:
            print("No connection to the internet.")
        except Exception as e:
            print("Something went wrong: " + str(e))

        time.sleep(update_timeout)
    

def send_message(msg='', tkn='', chat_id='5492197004'):
    try:
        params = {"chat_id":chat_id, "text":msg}
        url = "https://api.telegram.org/bot{}/sendMessage".format(tkn)
        response = requests.post(url, params=params)
        print(response)
    except requests.exceptions.ConnectionError:
        print("No connection to the internet.")
    except Exception as e:
        print("Something went wrong: " + str(e))
    

def bot(msg='', tkn=''):
    t = threading.Thread(target=send_message, args=[msg,tkn])
    #t = threading.Thread(target=get_updates, args=[tkn])
    t.start()

if __name__ == '__main__':
    token = api_key
    message = datetime.today().strftime('%Y-%m-%d - %H:%M:%S') + ": The water tank needs to be refilled."

    if (len(sys.argv) >= 2):
        token = sys.argv[1]

    if (len(sys.argv) >= 3):
        message = sys.argv[2]

    bot(message, token)

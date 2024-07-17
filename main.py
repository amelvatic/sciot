import dbms
import gateway
import reasoning
import telegram_bot
import time
import threading
import weather_forecast

if __name__ == '__main__':
    db = dbms.DBMS()
    db.start()

    #g = gateway1.Gateway()

    time.sleep(5)

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

import dbms
import gateway
import gateway2
import reasoning
import telegram_bot
import time
import threading

if __name__ == '__main__':
    db = dbms.DBMS()
    db.start()

    #g = gateway1.Gateway()

    time.sleep(5)

    gateway_thread = threading.Thread(target=gateway.x)
    gateway_thread.start()


    telegram_token = ""
    telegram_bot_thread = threading.Thread(target=telegram_bot.get_updates, args=[telegram_bot.api_key])
    telegram_bot_thread.start()
    

    time.sleep(5)

    reasoner = reasoning.Reasoner()
    reasoner.start()

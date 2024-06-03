from flask import Flask, request, jsonify
import threading
import time
import interface
import csv
import subprocess
import re

app = Flask(__name__)

grovepi_interface = interface.GrovePiInterface()

@app.route('/data', methods=['GET'])
def get_data():
    [timestamp, temperature, air_humidity, light_level, water_level, artificial_light_status] = grovepi_interface.get_all()
    data = {
        "timestamp": timestamp,
        "temperature": temperature,
        "air humidity": air_humidity,
        "light level": light_level,
        "water_level": water_level,
        "artificial light": artificial_light_status
    }
    return jsonify(data)

@app.route('/led-on', methods=['GET']) # 'POST'
def light_on():
    grovepi_interface.artificial_light_on()
    # content = request.json
    # response = {
    #     "received": content,
    #     "status": "Processed"
    # }
    # return jsonify(response)
    return jsonify({"status": 1})

@app.route('/led-off', methods=['GET'])
def light_off():
    grovepi_interface.artificial_light_off()
    return jsonify({"status": 0})

def background_task():
    try:
        while True:
            frame = grovepi_interface.get_all()
            filename = 'sample_data.csv'

            # Write data to CSV file
            with open(filename, mode='a') as file:
                writer = csv.writer(file)
                writer.writerow(frame)

            time.sleep(2)

    except KeyboardInterrupt:
        print("Exiting the program")
    except IOError:
        print("Error")


if __name__ == '__main__':
    # Start the background task in a separate thread
    thread = threading.Thread(target=background_task)
    thread.daemon = True  # Daemonize the thread to exit when the main program exits
    thread.start()
    
    ifconfig_result = subprocess.check_output(['ifconfig', 'wlan0']).decode('utf-8')
    ip_address = re.search(r'inet addr:(\S+)', ifconfig_result)
    print("Server on ip", ip_address)
    # Start the Flask server
    app.run(host=ip_address, port=5000)
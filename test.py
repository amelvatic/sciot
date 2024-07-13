import grovepi
import time

# Connect the Grove Temperature & Humidity Sensor to digital port D4
sensor = 4  # D4

try:
    while True:
        # Attempt to read temperature and humidity from the sensor
        [temp, humidity] = grovepi.dht(sensor, 0)  # Adjust the sensor type parameter if necessary

        # Check if the readings are valid
        if isinstance(temp, float) and isinstance(humidity, float):
            print("Temperature: ", temp, " C\tHumidity: ", humidity)
        else:
            print("Invalid data received from sensor")
        
        time.sleep(2)  # Read every 2 seconds

except KeyboardInterrupt:
    print("Stopped by User")
except IOError:
    print("Error in reading from sensor")
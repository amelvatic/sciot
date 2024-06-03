import time
import grovepi
import math


class GrovePiInterface:
    def __init__(self, temperature_humidity_port=7, led_port=4, ultrasonic_port=3, light_port=0):
        # Initialize ports and sensor types
        self.temperature_humidity_port = temperature_humidity_port
        self.ultrasonic_port = ultrasonic_port
        self.light_port = light_port
        self.led_port = led_port
        
        # Set up the LED port as output
        grovepi.pinMode(self.led_port, "OUTPUT")
        self.artificial_light_off()

    # temperature sensor
    def get_air_temperature_and_humidity(self):
        try:
            [temperature, air_humidity] = grovepi.dht(self.temperature_humidity_port, 0) # 0 - according to our sensor type
            if math.isnan(temperature) or math.isnan(air_humidity):  # check if we have a valid reading
                raise ValueError('Invalid reading from the air tempereature and humidity sensor')
            return temperature, air_humidity
        except IOError:
            print("Error reading from the air temperature and humidity sensor")
            return None, None
        
    # water tank sensor
    def get_water_tank_level(self):
        # need to adjust these values
        distance_full = 5
        distance_empty = 30
        try:
            dist = grovepi.ultrasonicRead(self.ultrasonic_port)
            if dist > 100:
                print("Invalid value from the water level sensor")
            water_level = (1 - (dist - distance_full) / (distance_empty - distance_full)) * 100
            
            # align any inaccuracies
            if water_level > 100:
                water_level = 100
            elif water_level < 0:
                water_level = 0
            
            return water_level
        except IOError:
            print("Error reading from the water tank level sensor")
            return None
    
    # light sensor
    def get_luminance(self):
        full_light = 5
        full_dark = 30
        try:
            val = grovepi.analogRead(self.light_port)
            light_level = (val - full_light) / (full_dark - full_light) * 100
            
            # align any inaccuracies
            if light_level > 100:
                light_level = 100
            elif light_level < 0:
                light_level = 0
            
            return val
        except IOError:
            print("Error reading from the light sensor")
            return None

    # artificial light
    def artificial_light_on(self):
        grovepi.digitalWrite(self.led_port, 1)
        self.artificial_light_status = 1

    def artificial_light_off(self):
        grovepi.digitalWrite(self.led_port, 0)
        self.artificial_light_status = 0
    

    def get_all(self):
        temperature, air_humidity = self.get_air_temperature_and_humidity()
        light_level = self.get_luminance()
        water_level = self.get_water_tank_level()

        frame = [time.time(), temperature, air_humidity, light_level, water_level, self.artificial_light_status]

        return frame
        

# if __name__ == "__main__":
#     grovepi_interface = GrovePiInterface()

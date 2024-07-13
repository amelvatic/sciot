import requests
import sys

def get_current_weather(city_name, api_key):

    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    url_1 = base_url + "appid=" + api_key + "&q=" + city_name
    
    response = requests.get(url_1)
    response_json = response.json()
    print(response_json)
    output = -1

    if int(response_json["cod"]) == 404:
        print("City Not Found")
    elif int(response_json["cod"]) == 401:
        print("Invalid API key")
    elif int(response_json["cod"]) == 429:
        print("Surpassed maximum number of API calls")
    elif int(response_json["cod"]) in [500, 501, 502, 503, 504]:
        print("Error in the OpenWeather Servers")
    else:
        main = response_json["main"]
        weather = response_json["weather"]

        current_temperature_kelvin = main["temp"]
        current_temperature_celsius = current_temperature_kelvin - 272.15
        #current_pressure = main["pressure"]
        current_humidity = main["humidity"]

    
        weather_id = weather[0]["id"] 
        weather_main = weather[0]["main"]
        weather_description = weather[0]["description"]
    
        print("Temperature (in celsius unit) = " + str(current_temperature_celsius) +
              "\nhumidity (in percentage) = " + str(current_humidity) + 
              "\nweather main = " + str(weather_main) +
              "\nid  = " + str(weather_id) + 
              "\ndescription = " + str(weather_description))

        goodWeather = False
        if ((weather_main.lower() in ["thunderstorm", "drizzle", "rain", "snow"]) or (weather_id < 700) or (weather_id in [711, 751, 761, 762, 771, 781])):
            goodWeather = False
        else:
            goodWeather = True

        output = [goodWeather, weather_id, weather_main, weather_description, current_temperature_celsius, current_humidity]

    return output

api_key = ""
city_name = "Ditzingen"
if (len(sys.argv) >= 2):
    api_key = sys.argv[1]

if (len(sys.argv) >= 3):
    city_name = sys.argv[2]
#city_name = input("Enter city name : ")

current_weather = get_current_weather(city_name, api_key)

""" ===============================
--  Server side Microservice File 

===============================
Prog:   "microserviceServer.py"
Desc:   Gets requests from one socket (req_socket), and publishes reply to another socket (pub_socket).
        Creates an asynchronous microservice. Gets average weather data given specified latitude and longitude,
        does this by using the circumference (with the radius of the circle as 'distance' , initially set to 5km)
        and gets four areas around it (their lat and long), then gets the weather data of those points, and finds
        the average.
===============================

=============================== """

# You may need to install this (and other) package(s) - pip install <name>   Note: pip3 for mac

import zmq      # Microservice API
import math     # Used for calculations of circumference points
import requests 

# Set up ZeroMQ context 
context = zmq.Context()


# Creates request-reply socket - receives request
rep_socket = context.socket(zmq.REP)    
# Bind socket
rep_socket.bind("tcp://*:5555")

# Creates publish-subscribe socket - publishes content
pub_socket = context.socket(zmq.PUB)
# Bind socket
pub_socket.bind("tcp://*:5556")




# ------------------------------------------------------------
# Func: get_weather_data
# Desc: Uses OpenWeatherMap API to get weather data of a provided
#       latitude and longitude, gets min, max, and curr temperatures.
# ------------------------------------------------------------
def get_weather_data(lat, long):
    apiKey = 'c56cc30f3df33acb43dd2b5911ed1d5d';      # personal api key - pls don't copy lol
    api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&appid={apiKey}&units=imperial"

    try:
        response = requests.get(api_url)
        data = response.json()
        allTemp = data["main"]  # Specifies we want temp data
        temp_min = allTemp['temp_min']
        temp_max = allTemp['temp_max']
        curr_temp = allTemp['temp']
        
        weather_info = {
        "temp_min": temp_min,
        "temp_max": temp_max,
        "temp": curr_temp
        }
        return weather_info
        
    except Exception as error:
        print("Could not get weather data: ", error)



# ------------------------------------------------------------
# Func: get_average_data
# Desc: Uses a list of coordinates, gets all their values,
#       finds their averages, stores them up, and returns them.
# ------------------------------------------------------------
def get_average_data(coordinates):

    all_weather_info = {
    "min_temp": [],
    "max_temp": [],
    "current_temp": []
    }

    for each in coordinates:    # Goes through all coordinates, gets their vals
        data = get_weather_data(each["latitude"],each["longitude"])
        all_weather_info["min_temp"].append(data["temp_min"])
        all_weather_info["max_temp"].append(data["temp_max"])
        all_weather_info["current_temp"].append(data["temp"])

    # Finds averages
    min_temp_average = sum(all_weather_info["min_temp"])/len(all_weather_info["min_temp"])
    max_temp_average = sum(all_weather_info["max_temp"])/len(all_weather_info["max_temp"])
    temp_average = sum(all_weather_info["current_temp"])/len(all_weather_info["current_temp"])

    # Sets up data - can change to your preferences, not required to have these names or layout.
    average_weather_info = {
    "min_temp_avg": min_temp_average,
    "max_temp_avg": max_temp_average,
    "current_temp_avg": temp_average
    }

    return average_weather_info




# ------------------------------------------------------------
# Func: calculate_response
# Desc: Given coordinates via a dictionary object, it holds
#       the latitude and longitude of the initial location
#       in degrees. It will use this to get all new coordiantes,
#       it will then call get_average_data() as it's return,
#       using the 'coordinates' list of new coords as input.
# ------------------------------------------------------------
def calculate_response(locationInfo):

    # Variable declarations
    center_lat     = locationInfo["latitude"]  # Get latitude  (y - axis)
    center_long    = locationInfo["longitude"] # Get longitude (x - axis)
    # ========
    # Can add distance here too: distance   = locationInfo["distance"]
    # ========
    distance = 5        # Units are kilometers - (essentially the radius, but for computational reasons we won't call it that) - CHANGE ^ (not required)

    radius = 6371       # Units are kilometers - set radius to radius of earth - DON'T change
    degrees = 0         # Starting degree to find - DON'T change

    coordinates = []    # Make list for new coordinates - DON'T change

    # Just adds center coordinates to list of coords to find the average
    center_vals =  {"latitude": center_lat,
                    "longitude":center_long}
    coordinates.append(center_vals)

    # Convert lat and long to radians for calculations
    center_lat_radians = math.radians(center_lat)
    center_long_radians = math.radians(center_long)

    while degrees < 360:
        # Find lat and long of each point of circumference
        radians = math.radians(degrees)

        # Gets new lat, current calculation leaves it in radians
        new_lat =   math.asin(math.sin(center_lat_radians) * math.cos(distance/radius) + 
                    math.cos(center_lat_radians) * math.sin(distance/radius) * math.cos(radians))

        # Gets new long, current calculation leaves it in radians
        new_long =  center_long_radians + math.atan2(math.sin(radians) *
                    math.sin(distance/radius) * math.cos(center_lat_radians),
                    math.cos(distance/radius) - math.sin(center_lat_radians) * 
                    math.sin(new_lat))

        # Converts from radians to degrees (latitude and longitude 'units')
        new_lat_degrees = math.degrees(new_lat)
        new_long_degrees = math.degrees(new_long)

        # Creates new object with the new lat and long, then appends to our collection
        new_object = {"latitude": new_lat_degrees,
                      "longitude":new_long_degrees}
        coordinates.append(new_object)

        
        # Depending on how accurate you want to be
        # You can change the addad value to anything that'll add up to 360 (5, 15, 30, 45, etc.)
        # However, since this requires a lot of API calls, it's best to keep this lower 
        # (I wouldn't go lower than 30 MAX for now). thanks lol.
        degrees += 90       

    return get_average_data(coordinates)
    


# ======================  THIS HANDLES REQUESTS  ======================
# ------------------------------------------------------------
# Func: request_handler
# Desc: Acts as a thread that will always run and catch requests.
#       Gets requests, sends acknowledgement, then gets all the
#       data needed and publishes it.
# ------------------------------------------------------------
def request_handler():
    while True:
        # Get python object (whatever sent) - serializing using json
        print("== While Loop Running ==")
        locationInfo = rep_socket.recv_json()
        print(f"Message received from microserviceClient.py\n")
        # Send Ack immediately
        ack = "True"
        rep_socket.send(ack.encode())
        print("== ack sent ==")

        # Get data to send
        responseInfo = calculate_response(locationInfo)
        
        # Publish data
        pub_socket.send_json(responseInfo)


import threading    # Allows new threads for server
# Creates new thread for server to always listen for requests
threading.Thread(target=request_handler, daemon=True).start()


# Main server loop, keeps it alive
while True:
    # Nothing is needed here
    pass

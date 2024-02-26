""" ===============================
Example client interaction with microservice

- python
=============================== """

import zmq
import threading
import time


context = zmq.Context()

req_socket = context.socket(zmq.REQ)        # Needed
req_socket.connect("tcp://localhost:5555")  # Needed

location_data = {"latitude": 47.2392691, "longitude": -122.4467710}     # lat and long of center of Tacoma WA - Unneeded

req_socket.send_json(location_data) # use variable with lat and long like above ^ - Needed
ack = req_socket.recv()             # Needed

print(f"ack: {ack.decode()}")       # Unneeded

# Subscribe to response "feed"
sub_socket = context.socket(zmq.SUB)        # Needed
sub_socket.connect("tcp://localhost:5556")  # Needed
sub_socket.subscribe(b"")   # Subscribe to all messages from publisher - Needed

def response_handler():     # Used with threading to make getting the response Asynchronous
    while True:
        print("== thread for response handler working as expected ==")
        response = sub_socket.recv_json()
        print(response)

# Have thread check for stuff from response "feed"
threading.Thread(target=response_handler, daemon=True).start()  # Needed


print("== Request sent ==\n== Continue Work ==\n")

# Do rest of coding here
while True:
    print("-- client doing other stuff every 5 seconds --")
    time.sleep(5)
    pass
WHAT THIS PROJECT DOES -- 
Gets average weather data given specified latitude and longitude,does this by using the circumference 
(with the radius of the circle as 'distance', initially set to 5km) and gets four areas around it 
(their lat and long), then gets the weather data of those points, and finds the average minimum, maximum
(for that day) and current temperature. It'll return those values.


# COMMUNICATION CONTRACT ===================================================================================================

NOTE: Full code examples are provided, here are what each of them are:
- microserviceServer.py   ==  The actual microservice/project. 
- microserviceClient.py   ==  An example of interacting with the microservice using Python3
- serverExample.js        ==  An example of interacting with the microservice using JavaScript/Node.js.
                            If you are running a server for web browsing, and want to use the functions
                            of the microservice in your browser, this will be very helpful to you.
- index.js                == An example of the browser-side JavaScript you would use for the above functionality.
- index.handlebars        == An example webpage for the browser-side use - keep in 'static' directory.
- 404.handlebars          == 404 page for example - keep in 'static' directory.




# PYTHON3 --

    * Assuming you have imported zmq
     
    You'll start by declaring and connecting your request socket(s). You'll also want to define your data in the 
    format shown. Then, you will send it as shown below, and receive the acknowledgement.

    # REQUEST ===================================================================================================

    context = zmq.Context()
    req_socket = context.socket(zmq.REQ)        # Needed
    req_socket.connect("tcp://localhost:5555")  # Needed

    - DEFINE DATA - EX.
    location_data = {"latitude": <latitude>, "longitude": <longitude>}

    - USE VARIABLE WITH LAT AND LONG LIKE ABOVE ^
    req_socket.send_json(location_data)         # Needed

    - SIMPLY AN ACKNOWLEDGEMENT, DATA DOES NOT COME FROM HERE
    ack = req_socket.recv()                     # Needed

    ============================================================================================================

    You'll start by declaring and connecting your subscribe socket. You'll then receive the data. In context,
    you'll most likely want to put the receiving data element in a loop that coninuously checks for data. This
    is easily implemented, and examples are shown in the client files.
    # RECEIVE ==================================================================================================

    sub_socket = context.socket(zmq.SUB)        # Needed
    sub_socket.connect("tcp://localhost:5556")  # Needed
    sub_socket.subscribe(b"")                   # Needed

    response = sub_socket.recv_json()           # Needed
    ============================================================================================================



# JAVASCRIPT/NODE.JS --

    To implement this microservice so that your browser/an action from your browser can call it, you'll need
    to include something like what is shown below in the -BROWSER SIDE section. The '/microservice/data' would
    be whatever link you decide within your server. You will most likely want to actually get data from the browser
    (such as lat and long), which is easy to do, but not implemented in the examples. 
    The server portion of this implementation is given below, where you'll create a new request socket, connect it,
    and send the request with data you are responsible for attaining and putting in the provided form:

    {"latitude": <latitude>, "longitude": <longitude>}

    Where <latitude> and <longitude> are your own variables/coordinates.

    # REQUEST ==================================================================================================

    - BROWSER SIDE

        - USE WHATEVER LINK IN YOUR SERVER YOU SET IT AS
        fetch('/microservice/data')
                .then(response => response.json())
                .then(data => {
                    console.log("Here is the data: ", data)
                })
                .catch(error => {
                    console.log("Error getting data: ", error)
                })

    - SERVER SIDE

        app.get('/microservice/data', async function(req, res){    
            const reqSocket = new zmq.Request;
            reqSocket.connect('tcp://localhost:5555');
            - ADD YOUR OWN DATA
            const locationData = { "latitude": 47.2392691, "longitude": -122.4467710 };
            reqSocket.send(JSON.stringify(locationData));
            const ack = await reqSocket.receive()

            # ===== HERE =====

        })

    ============================================================================================================

    You'll need to add a few things to the function provided above, and you'll need to add a function (or not, if
    you don't care about it being asynchronous) that creates a subscription socket, connects it, and gets the
    first bit of data it can. The code you'll need to add is what is responsible for getting that data back to
    the browser, so if you aren't interested in that, don't worry about it.

    # RECEIVE ==================================================================================================

    # ALL SERVER SIDE 

        - ADD THIS TO THE ABOVE FUNCTION, WHERE INDICATED WITH ===== HERE =====
        var data = await subResponse()
        res.send(data)

        - ADD THIS FUNCTION TO SERVER FOR ASYNC FUNCTION
        async function subResponse() {
            try {  
                const subSocket = new zmq.Subscriber;
                subSocket.connect('tcp://localhost:5556');
                subSocket.subscribe('');
                for await (const data of subSocket){
                    return JSON.parse(data) ;
                }
            } catch (error) {
                console.log("Error: " , error)
            }
        }
    ============================================================================================================


# UML DIAGRAM
[UML DIAGRAM](UML2.drawio.png)

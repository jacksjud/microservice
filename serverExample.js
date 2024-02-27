/* 
Example of implementation of using the microservice on browser

- Server side

*/


// // Likely need to download this == npm install zeromq 
const zmq = require('zeromq');
const express = require('express'); // Or whatever you use
const app = express();

var exphbs = require("express-handlebars")
var port = process.env.PORT || 2000
app.use(express.static('static'))

app.get('/microservice/data', async function(req, res){    // This should be catching a request from your index.js file (browser-environment JS)

    // REQ socket for sending request
    const reqSocket = new zmq.Request;
    // Set up to wherever you want it ran (keep tcp)
    reqSocket.connect('tcp://localhost:5555');


    // This should probably be data you send from index.js file in initial fetch
    const locationData = { "latitude": 47.2392691, "longitude": -122.4467710 };

    // Actually sends request - make sure to do it like below
    reqSocket.send(JSON.stringify(locationData));
    console.log("== Request Sent ==")

    // This isn't where you get the data
    // This just returns an acknowledgement, you don't even need to console.log it
    // But you do need to receive it
    const ack = await reqSocket.receive()
    console.log("== ACK : ", ack)

    // Waits for subscription response
    var data = await subResponse()
    // Sends data back to browser JS
    // res.json(data)
    console.log("== Data Received:",data)

    res.send(data)

})

app.get('/', function(req, res){
    res.render("static/index")
    next()
})

app.get('*', function (req, res) { 
    res.status(404).render("/static/404")
})


async function subResponse() {
    try {   // This is where you'll actually get the data

        // SUB socket for subscribing to response feed
        const subSocket = new zmq.Subscriber;
        // Set up to wherever you want it ran (keep tcp)
        subSocket.connect('tcp://localhost:5556');

        // Subscribes for all content outputted
        subSocket.subscribe('');
        for await (const data of subSocket){
            return JSON.parse(data) ;
        }
        
    } catch (error) {
        console.log("Error: " , error)
    }
}


app.listen(port, () => {
    console.log("== Server Listening on Port ", port)
})



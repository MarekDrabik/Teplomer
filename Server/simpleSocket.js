
//this is a server listening to Thermometer's connections through simple tcp socket

const Net = require('net');
const cs = require(__dirname + '/correspondence_crypting');

const server = new Net.Server();


function listen (port) {    
    server.listen(port, function() {
    console.log(`Server listening on socket, port:${port}`);
    });
}

server.on('connection', function(socket) {
    // Now that a TCP connection has been established, send current instructions to Thermometer.
    socket.write((global.spravaForTEP) ? (global.spravaForTEP + '\r\n') : '00\r\n'); //send 00 message if there is no new instructions
    global.spravaForTEP = null; //reset so to not resend same instructions on next connection
    
    // And read the data from Thermomter into a global object that is shared further on http server with the Web Application
    socket.on('data', function(data) {
        var dataString = data.toString()
        message_obj = new cs.Rozbal(dataString);
        global.lastTimeReceived = Date.now();
        global.spravaFromTEP = {
            casOdosielania : message_obj.casOdosielania,
            intervalMerTep : message_obj.intervalMerTep,
            intervalMerGps : message_obj.intervalMerGps, 
            intervalInfTep : message_obj.intervalInfTep, 
            intervalInfGps : message_obj.intervalInfGps, 
            tolerLow : message_obj.tolerLow, 
            tolerHigh : message_obj.tolerHigh, 
            onOffAlarmPark : message_obj.onOffAlarmPark, 
            aktBoxy : message_obj.aktBoxy,
            tv_snz1 : message_obj.vysledkyTepVlhLI[0],
            tv_snz2 : message_obj.vysledkyTepVlhLI[1],
            tv_snz3 : message_obj.vysledkyTepVlhLI[2],
            tv_snz4 : message_obj.vysledkyTepVlhLI[3], 
            tv_snz5 : message_obj.vysledkyTepVlhLI[4], 
            tv_snz6 : message_obj.vysledkyTepVlhLI[5], 
            tv_snzVonkajsi : message_obj.vysledkyTepVlhLI[6],
            tv_snzRPI : message_obj.vysledkyTepVlhLI[7], 
            tv_snzWTPI : message_obj.vysledkyTepVlhLI[8], 
            senzorySNezdrTeplotami : message_obj.senzorySNezdrTeplotami, 
            senzorySOscilTeplotami : message_obj.senzorySOscilTeplotami, 
            senzorySoZasekTeplotami : message_obj.senzorySoZasekTeplotami, 
            gps_suradnice : message_obj.gps_suradnice      
        };
        console.log("Teplomer poslal spravu. Cas odosielania:", global.spravaFromTEP.casOdosielania)
        socket.end()
    });

    //error:
    socket.on('error', function(err) {
        console.log(`Error: ${err}`);
    });
});

module.exports.listen = listen;
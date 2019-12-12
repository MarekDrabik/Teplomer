// This is the main module of the server.

global.spravaForTEP = null; //2 message objects are shared between https server and simple socket server ...
global.spravaFromTEP = null; //... to join both ends of communication between webApp and Thermomter
global.lastTimeReceived = null; //keeps time when last message was received from Thermometer, this time is sent to the client to update the timer

console.log('dir: ' + __dirname);

const fs = require('fs');
const http = require('http');
const https = require('https');
const Joi = require('joi');
const express = require('express'); //class
const helmet = require('helmet');
const morgan = require('morgan');
const path = require('path');
const config = require('config');
const cookieParser = require('cookie-parser');
//custom require:
const simpleSocket = require(__dirname + '/simpleSocket');

//declarations:
const app = express();
const privateKey = fs.readFileSync(__dirname + '/encryption/key.pem', 'utf-8');
const certificate = fs.readFileSync(__dirname + '/encryption/cert.pem', 'utf-8');
const passphrase = config.get('passphrase');
const port = config.get('port');

//ROUTERS:
const homeRouter = require(__dirname + '/routes/home');
const loginRouter = require(__dirname + '/routes/login');


//MIDDLEWARE:
app.use(cookieParser());
app.use(express.json());
app.use(helmet());  //dajaky bezpecnostny balicek
app.use(morgan('combined')); //logging http komunikacie
app.use('/', homeRouter);
app.use('/home', homeRouter);
app.use('/login', loginRouter);
app.use(express.static(path.join(__dirname, 'public'))); //serving public files automatically


// //http server:
// const httpPort = 5555;
// let server = http.createServer(app).listen(httpPort, () => {console.log(`http on port: ${httpPort}`)});

//https server:
const httpsPort = port;
const sslOptions = {
   key: privateKey,
   cert: certificate,
   passphrase: passphrase
};
const serverHttps = https.createServer(sslOptions, app).listen(httpsPort, () => {console.log(`https on port: ${httpsPort}`)});
//socket server:
const socketPort = 3080;
simpleSocket.listen(socketPort, () => {console.log(`simple socket on port: ${socketPort}`)});

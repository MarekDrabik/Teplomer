
const express = require("express");
const router = express.Router();
const config = require("config");
const jwt = require("jsonwebtoken");
const path = require('path');
//vlastne:
const cs = require(__dirname + '/../correspondence_crypting');

//declarations:
const jwtPrivateKey = config.get('jwtPrivateKey');
const domain = config.get('domain');
var lastMessageSent_ID = null; //neskor to bude property casOdosielania ktore sluzi ako ID poslednej spravy od teplomeru



//token validation when home page is loaded:
var validateCookieTokenHome = function (req, res, next) {
  if (req.cookies) {
    if (req.cookies.access_token) {
      var receivedToken = req.cookies.access_token;
      try {
        jwt.verify(receivedToken, jwtPrivateKey); //verify with environmen privatekey
        next();
        return;
      } catch(e) {
        console.log(e.message);
      }
    }
  }
  res.redirect(domain +'/login'); //redirect to login page when cookie expires
  return;
}
//token validation on each 2s request:
var validateCookieTokenLoop = function (req, res, next) {
  if (req.cookies) {
    if (req.cookies.access_token) {
      var receivedToken = req.cookies.access_token;
      try {
        jwt.verify(receivedToken, jwtPrivateKey);
        next();
        return;
      } catch(e) {
        console.log(e.message);
      }
    }
  }
  res.status(302).end();
  return;
}

router.get('/', validateCookieTokenHome, (req, res) => {  //validateCoo.. je middleware
  res.sendFile(path.join(__dirname + '/../public/main/index.html'));
});

router.get('/update/:id', validateCookieTokenLoop, (req, res) => {
  var messageObj = {}
  if (global.spravaFromTEP) { //if there is any message at all (server was already talking with teplomer)
    var pageRefreshed = (parseInt(req.params.id) == 1) ? true : false;  //id=1 je dodane od cliente len na uplne 1. request
    if (global.spravaFromTEP.casOdosielania !== lastMessageSent_ID || pageRefreshed ) { //if that message is a new one - not yet sent to the user yet OR
      // Page was newly open/refreshed then send new message and update lastMessegeSent_ID
      messageObj = global.spravaFromTEP; 
      lastMessageSent_ID = messageObj.casOdosielania;
    }
    if (pageRefreshed) {
      res.status(202);  //202 = status ako reakcia na id=1 request (refreshnuta stranka) aby client vedel, ze nema zobrazit zelenu obalku
    }
    else {
      res.status(200);  //200 = standard update
    }
  } 
  //lastTimeReceived is handling all three cases:
  //1. no message yet received (server fresh start) - global.lastTimeReceived is infinitely large
  //2. message received but not new - global.lastTimeReceived is > 0 and corresponds to last received time
  //3. new message received - global.lastTimeReceived is 0 or very close and corresponds to last received time
  messageObj.lastTimeReceived = parseInt((Date.now() - global.lastTimeReceived) / 1000);
  res.send(messageObj); //messageObj is either full message from teplomer with all its properties OR
  //it contains only .lastTimeReceived property
});

router.post('/instructions', validateCookieTokenLoop, (req, res) => { 
  global.spravaForTEP = cs.Zabal.vytvorSpravu(req.body); //update global message object with received instructions, 
  //this object is taken by simple socket server and sent to Thermometer
  res.status(201).end(); //201 = instructions received
});

module.exports = router;

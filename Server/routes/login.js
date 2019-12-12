const express = require("express");
const config = require("config");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const Joi = require("joi");
const router = express.Router();
const path = require('path');
const jwtPrivateKey = config.get('jwtPrivateKey'); //privatekey used for crypting the token that is checked on every page reload
const pass = config.get('password');
const name = config.get('name');

const milisecondsInADay = 60*60*24*1000
tokenValidityTime_inMiliseconds = milisecondsInADay * 5; //5 days without relogin is allowed

//nie az taka podstatna validacia, islo by to aj bez toho:
function validateFields (req, res, next) {
  const schema = Joi.object().keys({
    name: Joi.string().required(),
    password: Joi.string().required()
  });

  Joi.validate(req.body, schema, (err,value) => {
    if (err) {
      // send a 422 error response if validation fails
      res.status(422).send('Invalid data.')
      // console.log(err.message)
      return;
    }
    next()
  })
}

router.get('/', async (req, res) => {
  res.sendFile(path.join(__dirname + '/../public/login/login.html'));
})

router.post('/', validateFields, async (req, res) => {
  //verify name
  if (req.body.name != name) return res.status(400).send('Invalid name or password.');
  //verify password
  const validPassword = await bcrypt.compare(req.body.password, pass);
  if (!validPassword) return res.status(400).send('Invalid name or password.');

  //at this point, user is authenticated:
  const token = jwt.sign({email: "marek.drabik@protonmail.com"}, jwtPrivateKey); //sign the token with privatekey
  // res.sendFile(path.join(__dirname+'/../public/index.html'));
  res.cookie('access_token',token, { //send the signed token in the cookie
    maxAge : tokenValidityTime_inMiliseconds,
    secure : true,
    httpOnly : true
  });


  res.status(202).end()

});


module.exports = router;
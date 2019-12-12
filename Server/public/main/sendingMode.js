
//function that makes the interface animation of html elements that user interacted with
function Disco() {
  this.cancelParty = false;
  this.party = function (firstParty, secondParty, firstDuration, secondDuration, arg) {
    //first postman.renderHtml should be called before this function 
    setTimeout(()=>{
      if (this.cancelParty == false) {
        secondParty(arg);
        setTimeout(()=>{
          if (this.cancelParty == false) {
            firstParty();
            this.party(firstParty, secondParty, firstDuration, secondDuration, arg);
          }
        }, firstDuration);
      }
    }, secondDuration)
  }
};

var postman = {
  //requestedArrays dole sluzia na evidenciu vsetkych settings ktore maju byt odosielane <=> ak su vsetky prazdne, user nic nepozaduje zmenit
  //vsetky slidery ktorych current.value je ina ako req.value
  requestedSliders: [],
  //vsetky boxy ktorych current.value je ina ako req.value.
  requestedBoxes: [],
  //vsetky tolerancie ktorych current.value je ina ako req.value:
  requestedTolers: [],
  //obsahuje alarmDiv element ak je jeho child.input.checked opacny ako curr checked
  requestedAlarm: [],

  mapa: {
    slider: "requestedSliders",
    boxy: "requestedBoxes",
    toler: "requestedTolers",
    alarm: "requestedAlarm"
  },

  //push object to postman arrays above (because user clicked/modified some settings)
  in: function (obj, dont_check = false) { //dont check is used by slider_oninput to not mess up the colors while changing sliders.
    var arrayName = postman.mapa[obj.className];
    if (!postman[arrayName].includes(obj)) { //push in only if it's not already there
      postman[arrayName].push(obj);
    }
    if (dont_check == false) { 
      postman.check(); //check if there is anything in any of the requested arrays, if so, initiate disco party
    }
  },
  //take out object from it's requested array (user set previously selected settings back to their current values)
  out: function (obj, dont_check = false) {
    var arrayName = postman.mapa[obj.className];
    if (postman[arrayName].includes(obj)) { //if any postman.requestedArray contains postman obj
      postman[arrayName].splice(postman[arrayName].indexOf(obj),1);
    }
    if (dont_check == false) { 
      postman.check();
    }
  },
  initiate: function () { //function called because user modified some setting
    postmanBtn.style.visibility = "visible"; //show SEND button
    disco.cancelParty = true; //cancel the old party if there is one;
    postman.renderHtml(); //render firstParty first    
    disco = new Disco(); //disco.cancelParty = False on creation
    discoMode_on = true; //information for other functions
    disco.party(postman.renderHtml, currentState.renderHtml, 700, 1500, true); //initiate the whole flashing animation
  },
  unload: function (fromClick = true) { //fromClick false is when user moved modified settings back to default values
    discoMode_on = false;
    if (fromClick === true){ //if sending is canceled by user, delete all requested values
      postman.requestedSliders = []; 
      postman.requestedBoxes = [];
      postman.requestedTolers = [];
      postman.requestedAlarm = [];
      currentState.renderHtml();
      showSendingStatus('Cancelled.', color = colorRed, repeat = false);
    }
    postmanBtn.style.visibility = "hidden";
    //cancel the party and render currentState
    disco.cancelParty = true;
    currentState.renderHtml(discoMode_on = false);
  },
  check: function () { //if any of your request Arrays contains any value, initiate postman
    for (var ar in postman.mapa) {
      var arrayName = postman.mapa[ar];
      if (postman[arrayName].length != 0) { 
        postman.initiate();
        return;
      }
    }
    //if they are all empty, unload the postman (otherwise 'return' above is called)
    postman.unload(fromClick = false);
  },
  //EVEN FUNCTIONS on user interaction with html inputs:
  box_onchange: function (obj) { //html event
    console.log("boxonchange");
    var box_obj = obj.parentElement;
    var is_checked = obj.checked; //obj is html input element
    if (is_checked != currentState.boxes[box_obj.id].active) {
      postman.in(box_obj); //push to postman if setting is different from default
    }
    else {
      postman.out(box_obj); //take out (if it's there) from postman if setting isn't different from default
    }
  },
  alarm_onchange: function () { //html event
    var div_obj = alarmDiv;
    var is_checked = alarmInput.checked;
    if (is_checked != currentState.alarm) {
      postman.in(div_obj);
    }
    else {
      postman.out(div_obj);
    }
  },
  toler_onchange: function (isHigh) { //html event
    var tol_obj = (isHigh) ? tolerHighInput : tolerLowInput;
    var currValue = (isHigh) ? currentState.tolerHigh : currentState.tolerLow;
    if (Number(tol_obj.value) != currValue) {
      postman.in(tol_obj);
    }
    else {
      postman.out(tol_obj);
    }
  },
  slider_oninput: function(sliderino) { //html event
    //because Informing interval cannot be smaller than 12 seconds, move slider's handle if 6seconds is selected
    if ((sliderino.id == 'iITslider' || sliderino.id == 'iIGslider') && sliderino.value == intSprav_int.indexOf(6)) {
      sliderino.value = intSprav_int.indexOf(12); 
    }

    var sliderValue = sliderino.value;
    var sliderId = sliderino.id;
    var representant = representants[sliderId]; //slider's value element displayed on the panel
    var partner = partners[sliderId]; // temperature sliders are partners, gps sliders are partners
    var partnerRepresentant = representants[partner.id]; //partner's (slider) value element displayed on the panel

    var mainCurrentColor = slidersBackgroundColors[sliderId]; //user selected slider's default color
    var partnerCurrentColor = slidersBackgroundColors[representants[sliderId]]; //its partner default color

    //if slider's handle was moved back on default position, set it's color back to normal + exclude from postman
    if (sliderValue == intSprav_int.indexOf(getCurrentInterval(sliderino))) {
      representant.style.backgroundColor = mainCurrentColor;
      postman.out(sliderino, dont_check = true); //dont_check because we check just once at the end of this function (not 4 times to not go crazy)
    } else {
    //else, set the color green + include in postman
      representant.style.backgroundColor = colorRequestState;
      postman.in(sliderino, dont_check = true);
    }

    // update slider's value displayed on the panel (representant element)
    representant.innerHTML = intSprav_reversed[sliderValue];
    //adjust partner slider to "measuring-informing" logic = "we cannot inform faster than we measure"
    //informing sliders cannot set lower interval than their partner's current value (measuring)
    if (sliderId == "iMTslider" || sliderId == "iMGslider"){
      if (parseInt(sliderValue) < parseInt(partner.value)) { //if user moved informing slider above measuring slider
        partner.value = sliderValue; //then move the measuring slider with it
      }
    }
    //and measuring sliders cannot set higher interval than their partner's current value (informing)
    else {
      if (parseInt(sliderValue) > parseInt(partner.value)) { //if user moved measuring slider bellow informing slider
        partner.value = sliderValue; //then move the informing slider with it
      }
    }
    //now update all sliders because postman.disco is messing up colors.
    if (partner.value == intSprav_int.indexOf(getCurrentInterval(partner))) { //if partner was consequently moved back to default value
      partnerRepresentant.style.backgroundColor = partnerCurrentColor; //set its color to default
      postman.out(partner, dont_check = true); //and exclude it from postman
    } else { //if partner was consequently moved to different than default setting then
      partnerRepresentant.style.backgroundColor = colorRequestState; //set its color green 
      postman.in(partner, dont_check = true); //and include it in postman
    }
    partnerRepresentant.innerHTML = intSprav_reversed[partner.value];

    postman.check(); //check postman just now
  },
  //renderHTML elements with green colors:
  renderHtml: function () { //based on handles' values so to make sure the requested values are the ones user has set up 
    if (postman.requestedSliders.length > 0){ //some sliders are requested for change
      for (var sl in postman.requestedSliders) { //select only requested sliders
        var id = postman.requestedSliders[sl].id;
        var val = postman.requestedSliders[sl].value;  //val is value of actual physical slider
        representants[id].innerHTML = intSprav_reversed[val];  //value here is new value
        representants[id].style.backgroundColor = colorRequestState;
      }
    }
    //
    //boxes
    if (postman.requestedBoxes.length > 0){
      for (var b = 0; b < boxes.length; b++){  //global boxes
        var is_boxChecked = checkboxes[b].checked;
        if (is_boxChecked){
          boxes[b].style.backgroundImage = colorImageRequested;
        }else{
          boxes[b].style.backgroundImage = colorImageNone;
        }
      }
    }
    //render tolerLow, tolerHigh
    if(postman.requestedTolers.length > 0){
      for (var tol in postman.requestedTolers){
        var id = postman.requestedTolers[tol].id;
        var val = postman.requestedTolers[tol].value;
        representants[id].innerHTML = String(val); //tolerText
        representants[id].parentElement.style.backgroundColor = colorRequestState; //parent mark
        console.log(representants[id].parentElement);
      }
    }
    //render alarm box
    if (postman.requestedAlarm.length > 0) { //alarm change is requested
      var is_alarmChecked = alarmInput.checked;
      alarmMark.style.backgroundColor = colorRequestState;
      if (is_alarmChecked) {
        alarmValue.innerHTML = "ON!";
      }else {
        alarmValue.innerHTML = "off";
      }
    }
    
  },
  //user's instructions //function returns message object that is sent to server
  message: function () { 
  //zasielame len zmenene veliciny
    var message_obj = {};
    //intervals:
    message_obj["casOdosielania"] = [19,25,7,13,25,4]; //nepodstatny udaj
    message_obj["intervalMerTep"] = "-";  //toto su defaultne hodnoty ktore server chape ako "ziadna zmena"
    message_obj["intervalInfTep"] = "-";  //su hned prepisane o 3 riadky nizsie ak nejake sliders boli zmenene uzivatelom
    message_obj["intervalMerGps"] = "-";
    message_obj["intervalInfGps"] = "-";
    if (postman.requestedSliders.length > 0){ //some sliders are requested for change
      for (var sl in postman.requestedSliders) { //select only requested sliders
        var id = postman.requestedSliders[sl].id;
        var val = postman.requestedSliders[sl].value;  //val is value of actual physical slider
        var corresInt = correspondingInterval[id];
        message_obj[corresInt] = intSprav_int[val];  //value here is new value
      }
    }
    
    //aktBoxes:
    if (postman.requestedBoxes.length > 0) {
      var binString = '';
      for (ch in checkboxes){
        binString += (checkboxes[ch].checked) ? '1' : '0';
      }
      binString += '00'; //to finish the string to 8 places
      message_obj["aktBoxy"] = binString;
    }
    else { message_obj["aktBoxy"] = "-";} //ak su boxy neziadane, odosli "ziadna zmena"
    
    //tolerance:
    message_obj["tolerLow"] = "-";
    message_obj["tolerHigh"] = "-";
    if(postman.requestedTolers.length > 0){
      for (var tol in postman.requestedTolers){
        var id = postman.requestedTolers[tol].id;
        var val = parseFloat(postman.requestedTolers[tol].value);
        if (id == "tolerLowInput"){
          message_obj["tolerLow"] = val;
        }
        else if (id == "tolerHighInput"){
          message_obj["tolerHigh"] = val;
        }
      }
    }
    //onOffAlarmPark:
    if (postman.requestedAlarm.length > 0) { //send only if requested by user
      message_obj["onOffAlarmPark"] = (alarmInput.checked) ? '10000000' : '00000000';
    }
    else {
      message_obj["onOffAlarmPark"] = "-"; //otherwise send empty
    }
    return message_obj;
  },
  //send instructions to the server
  send: function () {
    console.log("running")
    var xhttp = new XMLHttpRequest();
    xhttp.onloadend = function() {
      if (this.readyState == 4 && this.status == 201) { //201 = server confirming received instructions
        showSendingStatus(text = 'Message sent!', color = colorGreen, repeat = false);
        console.log("sent")
      }
    };
    var messageTosend = postman.message();
    xhttp.open("POST", "/instructions");
    xhttp.setRequestHeader("Content-Type", "application/json");
    postman.unload(fromClick = true);
    console.log("INSTRUCTIONS:", messageTosend);
    xhttp.send(JSON.stringify(messageTosend));
    showSendingStatus(text = 'sending...', color = false, repeat = true);
  } 
}


//currentState object holds :
// * sliders, boxes , alarm, etc. = objects hodling values assigned/to be assigned to corresponding html elements 
// * other objects hodling useful values for other functions
// * update() updates above objects with the message when received from server
// * renderHTML() updates html with data from above objects (current state) 

var currentState = {
  //INITIALIZATIONS:
  sliders: {
    iMTslider: null,
    iITslider: null,
    iMGslider: null,
    iIGslider: null
  },
  boxes: { //[active?, temp, humid, heatIndex]
    box1: {},
    box2: {},
    box3: {},
    box4: {},
    box5: {},
    box6: {}
  },
  alarm: null, //true/false
  tolerLow: null,
  tolerHigh: null,
  weather: {},
  rpi: null,
  signal: null,
  //other objects that store data useful for other functions:
  senzorySNezdrTeplotami : "000000",
  senzorySOscilTeplotami : "000000",
  senzorySoZasekTeplotami : "000000",
  intervalMerTep : null,
  intervalInfTep : null,
  intervalMerGps : null,
  intervalInfGps : null,

  //update all currentState properties with the message object
  update: function (message) { 
    //update currentState.sliders:
    for (var s in currentState.sliders){ //loop through currentState.sliders
      var corresInt = correspondingInterval[s];
      currentState.sliders[s] = intSprav_int.indexOf(message[corresInt]);
    }
    //update currentState.boxes with 4 properties
    for (var b in currentState.boxes) {
      var boxNumber = boxToNumber[b];
      var active = (message["aktBoxy"][boxNumber - 1] == '1') ? true : false;
      representingValue = correspondingInterval[b];
      currentState.boxes[b] = {
        active: active,
        temp: message[representingValue][0],
        humid: message[representingValue][1],
        heatIndex: heatIndex(message[representingValue][0], message[representingValue][1])
      }
    }
    //alarm:
    currentState.alarm = (message["onOffAlarmPark"][0] == '1') ? true : false;
    //tolerance:
    currentState.tolerLow = message["tolerLow"];
    currentState.tolerHigh = message["tolerHigh"];
    //outside Temp:
    currentState.weather = {
      temp: message["tv_snzVonkajsi"][0],
      humid: message["tv_snzVonkajsi"][1],
      heatIndex: heatIndex(message["tv_snzVonkajsi"][0], message["tv_snzVonkajsi"][1]),
    };
    //rpi Temp:
    currentState.rpi = message["tv_snzRPI"][0];
    currentState.signal = message["tv_snzRPI"][1];
    //chyby na senzoroch:
    currentState.senzorySNezdrTeplotami = message["senzorySNezdrTeplotami"];
    currentState.senzorySOscilTeplotami = message["senzorySOscilTeplotami"];
    currentState.senzorySoZasekTeplotami = message["senzorySoZasekTeplotami"];
    currentState.intervalMerTep = message.intervalMerTep;
    currentState.intervalInfTep = message.intervalInfTep;
    currentState.intervalMerGps = message.intervalMerGps;
    currentState.intervalInfGps = message.intervalInfGps;
  },
  renderHtml: function () { //display current state on screen
    //discoMode_on is information if this function is called during Sending Mode or not
    //render sliders and it's representants
    for (var sl in sliders) { //loop through GLOBAL sliders
      var id = sliders[sl].id;
      var val = currentState.sliders[id];
      if (discoMode_on == false) { sliders[sl].value = val; } //move slider's handle only if we are not in Sending Mode 
      representants[id].innerHTML = intSprav_reversed[val];  //value here is new value
      representants[id].style.backgroundColor = slidersBackgroundColors[id];
    }
    //render boxes current to dark color based on currentState.boxes values
    for (var b in boxes) { 
      var currBox = currentState.boxes[boxes[b].id];
      var is_boxChecked = currBox.active;
      if (discoMode_on == false) { //modify checkbox of this box only if we are not in Sending Mode
        checkboxes[b].checked = is_boxChecked;  //check the  box
      }
      //render current mesurements of each box:
      boxes[b].querySelector('.tempBox').innerHTML = (currBox.temp == null) ? "-" : currBox.temp;
      boxes[b].querySelector('.humidBox').innerHTML = (currBox.humid == null) ? "-" : currBox.humid;
      boxes[b].querySelector('.hiBox').innerHTML = currBox.heatIndex; //if HI is null, this is "-"
      if (is_boxChecked){
        boxes[b].style.backgroundImage = colorImageCurrent;
      }else{
        boxes[b].style.backgroundImage = colorImageNone;
      }
    }
    //render alarm box:
    var is_alarmChecked = currentState.alarm;
    if (discoMode_on == false) { alarmInput.checked = is_alarmChecked; }////modify checkbox of this alarm only if we are not in Sending Mode
    alarmMark.style.backgroundColor = "transparent";
    if (is_alarmChecked) {
      body.style.backgroundColor = colorImageAlarm;
      alarmValue.innerHTML = "ON!"; 
    }else {
      body.style.backgroundColor = "#ffffe6";
      alarmValue.innerHTML = "off";
    }
    //tolerLow/high:
    if (discoMode_on == false) { //modify toler input values only if we are not in Sending Mode
      tolerHighInput.value = currentState["tolerHigh"];
      tolerLowInput.value = currentState["tolerLow"];
    }
    tolerHighText.innerHTML = currentState["tolerHigh"];
    tolerHighMark.style.backgroundColor = colorRed;
    tolerLowText.innerHTML = currentState["tolerLow"];
    tolerLowMark.style.backgroundColor = colorBlue;
    //further elements are not interactive discoMode_on variable is irelevant here:
    //outside Temp:
    outTemp.innerHTML = (currentState.weather.temp == null) ? "-" : currentState.weather.temp;
    outHumid.innerHTML = (currentState.weather.humid == null) ? "-" : currentState.weather.humid;
    outHI.innerHTML = currentState.weather.heatIndex;
    //rpi temp:
    rpi.innerHTML = currentState.rpi;
    signal.innerHTML = (currentState.signal == 99) ? "-" : currentState.signal;
  }
};

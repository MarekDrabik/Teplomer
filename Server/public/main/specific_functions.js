
function loadAlarmIframe() {
  // Adds an element to the document
  var newElement = document.createElement('iframe');
  newElement.setAttribute('src', "../alarm/alarm.html");
  newElement.setAttribute('id', "alarmIframe");
  newElement.setAttribute('style', "position: absolute; display: block; height: 50%; background-color: white; opacity: 0.9; z-index: 6;" );
  body.appendChild(newElement);
}

function loadTolerIframe(isHigh) {
  // Adds an element to the document
  isTolerHigh = isHigh;
  var newElement = document.createElement('iframe');
  newElement.setAttribute('src', "../heatIndex/heatIndex.html");
  newElement.setAttribute('id', "hiIframe");
  newElement.setAttribute('style', "position: absolute; display: block; height: 95%; background-color: white; opacity: 0.9; z-index: 5;" );
  body.appendChild(newElement);
}

function updateTimersIfNeeded (lastTimeReceived) {
  //funkcia obsahuje currentState variable ktora este nebola definovana. 
  //To je ale v poriadku kedze bola automaticky declarovana JavaScriptom na undefined a tato funkcia je volana az v poslednom module
  if (timerForLast.time != lastTimeReceived) { //if fresh message was received
    timerForLast.stop()
    timerForNext.stop()
    var curr_interval = Math.min(currentState.intervalInfTep, currentState.intervalInfGps);
    // reinitialize the timer objects, previous ones will be garbage collected automatically:
    timerForLast = new MessageTimer(owner = last, interval = curr_interval, timeReceived = lastTimeReceived, increasing = true);
    timerForNext = new MessageTimer(owner = next, interval = curr_interval, timeReceived = lastTimeReceived, increasing = false);
    timerForLast.start()
    timerForNext.start()
  }
}

function getCurrentInterval (sliderino) {
  //get current value provided by thermometer for specified slider
  var sliderId = sliderino.id;
  var interval = correspondingInterval[sliderId];
  return currentState[interval];
}

//not used function:
function reportProblem (message) {
  function alertProblem(){  
    alert(message);
    errButton.style.display = 'none';
    errButton.removeEventListener("click", alertProblem);
  }
  errButton.addEventListener("click", alertProblem);
  errButton.style.display = 'block';
}

//called by postman
function showSendingStatus(text, color = false, repeat = false){
  //shows flashing message under the SEND button of specified color
  messageStatus.innerHTML = text;
  messageStatus.style.display = 'block';
  if (color) {
    messageStatus.style.backgroundColor = color;
  } else {
    messageStatus.style.backgroundColor = '#f1f9a4';
  }
  if (repeat == false) { //cancel the repeating animation if required
    setTimeout(() => {messageStatus.style.display = 'none';
    }, 2000)
  }
}

//show envelope and hide it again after 2 seconds
function showEnvelope(){
  envelope.style.display = 'block';
  setTimeout(() => {
    envelope.style.display = 'none';
  }, 2000)
}
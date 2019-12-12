
const currentState = window.parent.currentState;  //import data from main app code
var senzorySNezdrTeplotami = currentState.senzorySNezdrTeplotami
var senzorySOscilTeplotami = currentState.senzorySOscilTeplotami
var senzorySoZasekTeplotami = currentState.senzorySoZasekTeplotami

//vypln arrays pre kazdy typ chyby prislusnym cislom boxu:
nezdraveSenzory = [];
for (var i = 1; i <= 6; i++){
  if (senzorySNezdrTeplotami[i-1] == '1'){
    nezdraveSenzory.push(i)
  }
}
oscilujuceSenzory = [];
for (var i = 1; i <= 6; i++){
  if (senzorySOscilTeplotami[i-1] == '1'){
    oscilujuceSenzory.push(i)
  }
}
zaseknuteSenzory = [];
for (var i = 1; i <= 6; i++){
  if (senzorySoZasekTeplotami[i-1] == '1'){
    zaseknuteSenzory.push(i)
  }
}

//zobraz chybovu spravu so zoznamom chybnych boxov ak sa nejake chyby najdu:
if (nezdraveSenzory.length != 0) {
  var statusLine = document.createElement('p');
  var text = '- teplota presiahla medze na senzoroch cislo: '
  for (i in nezdraveSenzory) {
    text += String(nezdraveSenzory[i] + ', ')
  }
  text += ' !'
  statusLine.innerHTML = text;
  statusLine.style.color = 'red';
  document.body.appendChild(statusLine);
}
if (oscilujuceSenzory.length != 0) {
  var statusLine = document.createElement('p');
  var text = '- teplota v boxoch cislo '
  for (i in oscilujuceSenzory) {
    text += String(oscilujuceSenzory[i] + ', ')
  }
  text += ' je prilis premenliva alebo senzor neodpoveda! Skontroluj.'
  statusLine.innerHTML = text;
  statusLine.style.color = 'red';
  document.body.appendChild(statusLine);
}
if (zaseknuteSenzory.length != 0) {
  var statusLine = document.createElement('p');
  var text = '- senzory cislo '
  for (i in zaseknuteSenzory) {
    text += String(zaseknuteSenzory[i] + ', ')
  }
  text += ' nemenia hodnoty, su zaseknute! Skontroluj.'
  statusLine.innerHTML = text;
  statusLine.style.color = 'red';
  document.body.appendChild(statusLine);
}

function unloadFrame(){
  var ifrm = window.parent.document.getElementById('alarmIframe');
  ifrm.parentNode.removeChild(ifrm);
}
function testAlarm(){ //test alarm nie je momentalne implementovany
  var inputAlarm = window.parent.document.getElementById('alarmInput');
  inputAlarm.checked = true
  window.parent.postman.alarm_onchange();
  unloadFrame();
}
function turnOffAlarm(){
  var inputAlarm = window.parent.document.getElementById('alarmInput');
  inputAlarm.checked = false;
  window.parent.postman.alarm_onchange();
  unloadFrame();
}









//####### DEFINITIONS first, execution at the end of code, see "RUN":

//this works because script is run at the end of body where body is already loaded:
const teploty = document.querySelectorAll('#HItable-grid div:nth-child(8n+1)');
// const test = document.querySelectorAll('#HItable-grid>div:not(.hum):not(.teploty):not(#HItable-grid):not(#roh)');
const vsetkyDiv = document.querySelectorAll('#HItable-grid > div');

//assing classname to all temperatures
for (var i in teploty) {
  if (i != 0) teploty[i].className = 'teploty';
}
//assign classname to all heat indexes
for (var i in vsetkyDiv) {
  if (vsetkyDiv[i].className != 'hum' && vsetkyDiv[i].className != 'teploty' && vsetkyDiv[i].id != 'HItable-grid' && vsetkyDiv[i].id != 'roh'){
    vsetkyDiv[i].className = 'HI';
  }
}

// vsetky mozne hodnoty HI v tabulke (unique array of Numbers), sluzi na matematicke porovnavanie neskor
valuesOfAllHI = [];
const elemsOfAllHI = document.getElementsByClassName('HI');
for (var i in elemsOfAllHI) {
  var hiValue = Number(elemsOfAllHI[i].innerText);
  if (!valuesOfAllHI.includes(hiValue)) {  //zaruc nech tam nie su duplikaty
    valuesOfAllHI.push(hiValue)
  }
}
valuesOfAllHI.sort((a, b) => a - b); //zorad od namensieho po najvacsie

function selectAllElemsWithTheseValues(stringValues) {
  var currentElems = [];
  for (var v in stringValues) {
    for (var i in elemsOfAllHI) {
      if (elemsOfAllHI[i].innerHTML == stringValues[v]){
        // elemsOfAllHI[i].style.backgroundColor = 'purple'
        currentElems.push(elemsOfAllHI[i]);
      }
    }
  }
  return currentElems;
}

function resetToDefaultStyle(elems) {
  for (var i in elems) {
    elems[i].style.borderStyle = 'none';
    elems[i].style.backgroundColor = 'white';
    elems[i].style.color = 'black';
    elems[i].style.textShadow = 'none';
  } 
}

class HeatIndex {
  constructor() { //some variables that store values specific to selected HI value in the table
    this.isTolerHigh = null;  //specifies if its Upper/Lower tolerance
    this.selectedHIValue = null; //value of current/newly selected HI
    this.currentUnhealthyElems = {};  //all elements that are/will be colored red/blue
  }

  //DEFINITIONS:
  //(of _functions that are called by the last defined function 'rerenderTableGraphics')
  _setFocus (val) { //focus the view on the selected element
    for (var el in elemsOfAllHI) {
      if (elemsOfAllHI[el].innerText == val){
        elemsOfAllHI[el].scrollIntoView({block: 'center', behaviour:"smooth"});
      }
    }
  }
  _border (elements) {  //modify css borders
    if (elements.className == 'teploty'){ //special case elements=only one div of teploty
      elements.style.borderStyle = "dashed";
      elements.style.borderWidth = "2px";
      return;
    }
    for (var i in elements) {
      elements[i].style.borderStyle = "dashed";
      elements[i].style.borderWidth = "2px";
    }
  }
  _colorBackground(elements) {  //css background-color
    var color = (this.isTolerHigh) ? '#ff1500' : "#4d72b3"; //red : blue
    for (var i in elements) {
      elements[i].style.backgroundColor = color;
      elements[i].style.color = '#FAE03C';
      elements[i].style.textShadow = "1px 1px black";
      elements[i].style.opacity = '1';
    }
  }
  _allUnhealthyValues (currentHI, isTolerHigh = this.isTolerHigh) { //returns array of unique unhealthy values (as strings)
    var indexOfCurrentHI = valuesOfAllHI.indexOf(currentHI);
    var allUnhealthyValues = (isTolerHigh) ? valuesOfAllHI.slice(indexOfCurrentHI, valuesOfAllHI.length) : valuesOfAllHI.slice(0, indexOfCurrentHI+1);
    //vrat to ako strings:
    return allUnhealthyValues.map(x => String(x));
  }

  //render all the interactive graphics:
  //function is called when: 1. window is loaded, 2. user selects a value in the table
  rerenderTableGraphics(selectedHIValue = this.selectedHIValue) { 
    this._setFocus(selectedHIValue);
    this.elemsOfSelectedHI = selectAllElemsWithTheseValues([selectedHIValue]);
    this.previousUnhealthyElems = this.currentUnhealthyElems;
    this.currentUnhealthyElems = selectAllElemsWithTheseValues(this._allUnhealthyValues(Number(selectedHIValue)))

    //render style:
    resetToDefaultStyle(this.previousUnhealthyElems);
    this._border(this.elemsOfSelectedHI);
    this._colorBackground(this.currentUnhealthyElems)
  }
}

//RUN--------
var hi = new HeatIndex();
hi.isTolerHigh = window.parent.isTolerHigh; //ide o horny alebo spodny heat index?
//nacitaj selectedElemHIButton = html "input" element (horny/spodny heatindex tlacidlo). 
//Tento element je smerodatne ulozisko aktualnej hodnoty heatindexhi.:
var selectedElemHIButton = window.parent.document.getElementById((hi.isTolerHigh) ? 'tolerHighInput' : 'tolerLowInput')
hi.selectedHIValue = selectedElemHIButton.value;
hi.rerenderTableGraphics();
//-----------

//EVENTS definitions:
//click event when user selects new value:
window.onclick = e => {
  if (e.target.className == 'HI'){
    hi.selectedHIValue = Number(e.target.innerHTML)
    hi.rerenderTableGraphics();
  }  
}
//function called on "cancel window" button click event:
function unloadFrame(){ //funkcia je volana na click event
  var ifrm = window.parent.document.getElementById('hiIframe');
  ifrm.parentNode.removeChild(ifrm);
}
//function called on "OK" button click event:
function loadToleranceValue() {
  //first check if tolerance value is allowed (compare to the opposite tolerance value)
    if (hi.isTolerHigh) {
    var oppositeElemHIButton = window.parent.document.getElementById('tolerLowInput')
    if (oppositeElemHIButton.value >= hi.selectedHIValue) {
      window.parent.reportProblem("Horna hodnota Heat Indexu nemoze byt mensia (ani rovna) ako dolna hodnota! Ingorujem zadanie.")
      unloadFrame();
      return;
    }
  }
  else {
    var oppositeElemHIButton = window.parent.document.getElementById('tolerHighInput')
    if (oppositeElemHIButton.value <= hi.selectedHIValue) {
      window.parent.reportProblem("Dolna hodnota Heat Indexu nemoze byt vacsia (ani rovna) ako horna hodnota! Ingorujem zadanie.")
      unloadFrame();
      return;
    }
  }
  //if above passed, then proceed and load new selected value in html
  selectedElemHIButton.value = hi.selectedHIValue; //nacitaj vybranu hodnotu do elementu na hlavnej stranke (horny alebo spodny HeatIndex)
  window.parent.postman.toler_onchange(hi.isTolerHigh); //zavolaj toler_onchange hlavnej stranky nech zareaguje postman na nove instrukcie
  unloadFrame();
}

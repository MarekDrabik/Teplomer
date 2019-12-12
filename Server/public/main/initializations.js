//initial declarations:
const body = document.querySelector('body');
const alarmDiv = document.getElementById('alarmDiv');
const alarmValue = document.getElementById('alarmValue');
const kontrolka = document.getElementById('kontrolka');

const outTemp = document.getElementById('outTemp');
const outHumid = document.getElementById('outHumid');
const outHI = document.getElementById('outHI');

const tolerLowInput = document.getElementById("tolerLowInput");
const tolerHighInput = document.getElementById("tolerHighInput");

const alarmInput = document.getElementById("alarmInput");

const iMTslider = document.getElementById('iMTslider');
const iITslider = document.getElementById('iITslider');
const iMGslider = document.getElementById('iMGslider');
const iIGslider = document.getElementById('iIGslider');
const mesTempValueMark = document.getElementById('mesTempValueMark');
const infTempValueMark = document.getElementById('infTempValueMark');
const mesGpsValueMark = document.getElementById('mesGpsValueMark');
const infGpsValueMark = document.getElementById('infGpsValueMark');
const alarmMark = document.getElementById('alarmMark');

const errButton = document.getElementById("errorBtn");

const intSprav_int = [6 , 12, 24, 48, 96, 192, 384, 768, 1536, 3072, 6144, 12288, 24576, 49152, 123456789].reverse();
const intSprav = ["6 s", "12 s", "24 s", "48 s", "1.5 m", "3 m", "6.5 m", "13 m", "30 m", "50 m", "1.5 h", "3.5 h", "7 h", "13.5 h", "OFF"];
const intSprav_reversed = ["6 s", "12 s", "24 s", "48 s", "1.5 m", "3 m", "6.5 m", "13 m", "30 m", "50 m", "1.5 h", "3.5 h", "7 h", "13.5 h", "OFF"].reverse();

const currentMesTemp = document.getElementById('currentMesTemp');
const currentInfTemp = document.getElementById('currentInfTemp');
const currentMesGps = document.getElementById('currentMesGps');
const currentInfGps = document.getElementById('currentInfGps');
const box1 = document.getElementById('box1');
const box2 = document.getElementById('box2');
const box3 = document.getElementById('box3');
const box4 = document.getElementById('box4');
const box5 = document.getElementById('box5');
const box6 = document.getElementById('box6');
const box1Checkbox = box1.querySelector('input');
const box2Checkbox = box2.querySelector('input');
const box3Checkbox = box3.querySelector('input');
const box4Checkbox = box4.querySelector('input');
const box5Checkbox = box5.querySelector('input');
const box6Checkbox = box6.querySelector('input');

const tolerHighText = document.getElementById('tolerHighText');
const tolerLowText = document.getElementById('tolerLowText');
const tolerHighMark = document.getElementById('tolerHighMark');
const tolerLowMark = document.getElementById('tolerLowMark');

const alarmOnOff = document.getElementById('alarmOnOff');
const weather = document.getElementById('weather');
const rpi = document.getElementById('rpi');
const signal = document.getElementById('signal');

const messageBtn = document.getElementById('messageBtn');
const postmanBtn = document.getElementById('postmanBtn');
const messageStatus = document.getElementById('messageStatus');
const envelope = document.getElementById('envelope');

const last = document.getElementById('lastTime');
const next = document.getElementById('nextTime');

const colorImageNone = "linear-gradient(to bottom right, #d9d9d9, white)";
const colorImageCurrent = "linear-gradient(to bottom right, #4d3319, #cc6600)";
const colorImageRequested = "linear-gradient(to bottom right, #009933, #00b300)";
const colorImageAlarm = "red";
const colorCurrentState = "#663500";
const colorRequestState = "#5cd65c";
const colorBoxBorders = "#331a00";
const colorRed = "#FF6F61";
const colorBlue = "#91A8D0";
const colorGreen = '#c6ffb3';

const boxy = [box1, box2, box3, box4, box5, box6];
var sliderValue;

var isTolerHigh;

const sliders =  [iMTslider, iITslider, iMGslider, iIGslider];
const boxes = [box1, box2, box3, box4, box5, box6];
const checkboxes = [box1Checkbox, box2Checkbox, box3Checkbox, box4Checkbox, box5Checkbox, box6Checkbox];
const boxToNumber = {box1: 1, box2: 2, box3: 3, box4: 4, box5: 5, box6: 6}//DECLARATIONS

//dummy objects:
var disco = {};
var discoMode_on = false;
var timerForLast = {stop: function () {}};
var timerForNext = {stop: function () {}};

const slidersBackgroundColors = {
  iMTslider: "#FF6F61",
  iITslider: "#f2f2f2",
  iMGslider: "#91A8D0",
  iIGslider: "#f2f2f2"
}

const representants = {
  iMTslider: mesTempValueMark,
  iITslider: infTempValueMark,
  iMGslider: mesGpsValueMark,
  iIGslider: infGpsValueMark,
  mesTempValueMark : iMTslider,
  infTempValueMark : iITslider,
  mesGpsValueMark : iMGslider,
  infGpsValueMark : iIGslider,
  tolerHighInput: tolerHighText,
  tolerLowInput: tolerLowText
}
const correspondingInterval = {
  iMTslider : "intervalMerTep",
  mesTempValueMark : "intervalMerTep",
  iITslider : "intervalInfTep",
  infTempValueMark : "intervalInfTep",
  iMGslider : "intervalMerGps",
  mesGpsValueMark : "intervalMerGps",
  iIGslider : "intervalInfGps",
  infGpsValueMark : "intervalInfGps",
  tolHighText: "tolerHigh",
  tolLowText: "tolerLow",
  box1: "tv_snz1",
  box2: "tv_snz2",
  box3: "tv_snz3",
  box4: "tv_snz4",
  box5: "tv_snz5",
  box6: "tv_snz6",
  weather: "tv_snzVonkajsi",
  rpi: "tv_snzRPI",
}
const partners = {
  iMTslider : iITslider,
  iITslider : iMTslider,
  iMGslider : iIGslider,
  iIGslider : iMGslider
}

const pocetIntervalov = intSprav.length;
for (s in sliders) {
  sliders[s].max = pocetIntervalov - 1;
  sliders[s].step = 1;
}
// -------------------------

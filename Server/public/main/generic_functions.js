
function heatIndex (T, R) {
  var HI = T;
  if (T >= 24.5){ //HeatIndex differs from temperature only above 24 degrees celsius
    var c1 = -8.78469475556;
    var c2 = 1.61139411;
    var c3 = 2.33854883889;
    var c4 = -0.14611605;
    var c5 = -0.012308094;
    var c6 = -0.0164248277778;
    var c7 = 0.002211732;
    var c8 = 0.00072546;
    var c9 = -0.000003582;
    HI = c1 + c2*T + c3*R + c4*T*R + c5*T*T + c6*R*R + c7*T*T*R + c8*T*R*R + c9*T*T*R*R;
  }
  if (T == null) {  //if temp and humid is NaN
    return "-"
  }
  return (Math.round(HI)).toString();
}

function makeStringAndAppendZeroIfSingleDigit(n){
  if(n <= 9){
    return "0" + String(n);
  }
  return String(n)
}

function run() {
  //update the current state object at the beginning in case there is no better message available
  currentState.update({
    aktBoxy: "00000000",
    intervalInfGps: 123456789,
    intervalInfTep: 123456789,
    intervalMerGps: 123456789,
    intervalMerTep: 123456789,
    onOffAlarmPark: "00000000",
    tolerHigh: null,
    tolerLow: null,
    tv_snz1: [null, null],
    tv_snz2 : [null, null],
    tv_snz3 : [null, null],
    tv_snz4 : [null, null],
    tv_snz5 : [null, null],
    tv_snz6 : [null, null],
    tv_snzVonkajsi : [null, null],
    tv_snzRPI : [null, null],
    tv_snzWTPI : [null, null],
    senzorySNezdrTeplotami : "00000000",
    senzorySOscilTeplotami : "00000000",
    senzorySoZasekTeplotami : "00000000",
    gps_suradnice : null,
    timeServerReceived : 999999999 //big number to render >24 hours
  });

  //initiate the loop of requests to the server:
  loopRequest();
}

run();

// This module is providing functionality to encode and decode message string from/into information that is shared between WebApp and Thermometer

const SV = require('./SHARED_VAR');


class Toolkit { //some helping functions for the code bellow
  
  static fromIntervalToCODE(num) {
    //interval is just a number in max range 0-127
    var index = SV.MOZNEIntervalySprav.indexOf(num);
    return SV.CODE[index];
  }
  static fromTempToCODE(num) {
    var index = SV.TEPLOTY.indexOf(num); 
    return SV.CODE[index];
  }
  static fromBinstringToCODE(binString){
    //binString size is 8
    var num = 0;
    var i = 0;
    for (var bit in binString){
      if (binString[bit] === '1'){
        //calculate decimal representation of this binString
        num += 2**(7-i); //we are starting from left so first "1" is 2**7
      }
      i += 1; //loop through bits of binString
    }
    return SV.CODE[num];
  }
  static fromIntToBinstring(num){
    var binString = '';
    for (var i = 0; i < 8; i++) {
      var divider = 2 ** (7-i);
      var bit = parseInt(num / divider); //napr. 84/48 = 1.75 => parseInt() => 1
      if (bit == 1){
        num = num - divider; //zmensi cislo kedze sme jeho "1" uz zaznamenali
      }
      binString += String(bit); //pridaj reprezentanta '0'/'1' do finalneho stringu
    }
    return binString;
  }

}

class Zabal {
  // jo = jsonObject = { casOdosielania = b'', intervalMerTep = b'', intervalInfTep = b'', intervalMerGps = b'', intervalInfGps = b'', \
  //        tolerLow = b'', tolerHigh = b'', onOffAlarmPark = b'', aktBoxy = b'' }
  static vytvorSpravu (jo){
    var intervalMerTep = (jo.intervalMerTep != "-") ? Toolkit.fromIntervalToCODE(jo.intervalMerTep) : "";
    //console.log(intervalMerTep);
    var intervalInfTep = (jo.intervalInfTep != "-") ? Toolkit.fromIntervalToCODE(jo.intervalInfTep) : "";
    //console.log(intervalInfTep);
    var intervalMerGps = (jo.intervalMerGps != "-") ? Toolkit.fromIntervalToCODE(jo.intervalMerGps) : "";
    //console.log(intervalMerGps);
    var intervalInfGps = (jo.intervalInfGps != "-") ? Toolkit.fromIntervalToCODE(jo.intervalInfGps) : "";
    //console.log(intervalInfGps);

    var tolerHigh = (jo.tolerHigh != "-") ? Toolkit.fromTempToCODE(jo.tolerHigh) : "";
    var tolerLow = (jo.tolerLow != "-") ? Toolkit.fromTempToCODE(jo.tolerLow) : "";

    var onOffAlarmPark = (jo.onOffAlarmPark != "-") ? Toolkit.fromBinstringToCODE(jo.onOffAlarmPark) : "";
    var aktBoxy = (jo.aktBoxy != "-") ? Toolkit.fromBinstringToCODE(jo.aktBoxy) : "";

    var dataArray = [intervalMerTep, intervalMerGps, intervalInfTep, intervalInfGps, tolerLow, tolerHigh, onOffAlarmPark, aktBoxy];
    //console.log("dataarray:", dataArray);
    var spravaDat = ""; for (var i in dataArray) {spravaDat += dataArray[i]};
    // //console.log(spravaDat)
    var dlzkaDat = Zabal.__dlzkaDat(dataArray);
    var dlzkaPovinnychVelicin = (1 + 6 + 1) * 2 //dlzkaSpravy + casOdosielania + zastupenie
    //tri prve veliciny:
    //1B:
    var dlzkaSpravy = SV.CODE[dlzkaPovinnychVelicin + dlzkaDat]
    //console.log(dlzkaSpravy)
    //6B:
    var casOdosielania = Zabal.__cas(jo.casOdosielania);
    //console.log("cas", casOdosielania);
    //2B:
    var zastupenie = Zabal.__zastupenie(dataArray);
    //console.log("zas", zastupenie);
    var message = dlzkaSpravy + casOdosielania + zastupenie + spravaDat
    ////console.log(message);
    return message;
    //VRATI spravu vo formate sv.CODE
  }

  static __dlzkaDat(dataarray) {
    var dlzka = 0;
    for (var i in dataarray) {
      if (dataarray[i] != ""){ 
        dlzka += dataarray[i].length 
      } 
    }
    ////console.log("dlzka:", dlzka);
    return dlzka;
  }

  static __zastupenie(dataarray) {
    var zastupenie = ''
    for (var i in dataarray) {
      if (dataarray[i] != "") {
        zastupenie += '1';
      } else {
        zastupenie += '0';
      }
    }
    while (zastupenie.length < 8) { //fill the rest of zastupenie with zeros, until its length is 8
      zastupenie += '0';
    }
    ////console.log("zastupenie", zastupenie);
    return Toolkit.fromBinstringToCODE(zastupenie);
    
  }

  //date+time is send as array [19,4,5,12,34,54] = [year, month ...] so just process that
  static __cas(casOdo){
    var casCODE = '';
    for (var i in casOdo) {
      casCODE += SV.CODE[casOdo[i]] //
    }
    ////console.log("casCODE", casCODE);
    return casCODE; //should be a string of 6B*2
  }// nastavenia
}   

class Rozbal { //nastavenia + vysledky

  constructor (sprava) {
    this.sprava = sprava;
    this.spravaL = []; //najprv premen kodovane dataVSprave 'E0H0M0' na list hodnot ktore zastupuju (index v ZP.CODE) : [23, 45, 15]
    for (var i = 0; i < sprava.length; i += 2) {
      var chunk = sprava.slice(i, i+2);
      this.spravaL.push(SV.CODE.indexOf(chunk));
    }
    this.dlzkaSpravy = this.spravaL[0];
    this.casOdosielania = this.spravaL.slice(1,7);
    //zastupnie is 8 * 3 = 24 bits long string '1001001001001...'
    this.zastupenie = '';
    for (var i = 7; i < 10; i++){
      this.zastupenie += Toolkit.fromIntToBinstring(this.spravaL[i])
    }
    // console.log("zastupenie ma byt 24 * '01010':", this.zastupenie)
    this.zastupenieLI = []
    for (var bit in this.zastupenie) {
      this.zastupenieLI.push(this.zastupenie[bit])
    }
    // console.log("zastupenieLI ma byt zastupenie ale list: ", this.zastupenieLI)
    this.listHodnot = this.vytvorListHodnot(this.spravaL.slice(10, this.spravaL.length))
    var sl = this.listHodnot.slice(0,8); //there is some bug, if i miss this useless line then further unpacking won't work.
    //unpack nastavenia:
    [this.intervalMerTep, this.intervalMerGps, this.intervalInfTep, this.intervalInfGps, 
    this.tolerLow, this.tolerHigh, this.onOffAlarmPark, this.aktBoxy] = this.listHodnot.slice(0,8);
    // console.log(this.intervalMerTep)
    //unpack vysledky teplot/vlhkosti:
    this.vysledkyTepVlhLI = this.listHodnot.slice(8,17);
    // console.log("vysledkyTepVlhLI", this.vysledkyTepVlhLI);
    //unpack errorSenzory:
    [this.senzorySNezdrTeplotami, this.senzorySOscilTeplotami, this.senzorySoZasekTeplotami] = this.listHodnot.slice(17,20);
    this.gps_suradnice = this.listHodnot[20];
  }

  vytvorListHodnot (dataVSprave) {
    //dataVSprave vo formate: [12, 9, 123, 33, 22 ....]
    var i = 0; //index zastupenia
    var k = 0; //index dataVsprave
    var result = [];
    var zas = this.zastupenieLI;
    for (var bit in zas) {
      if (zas[bit] == '0'){
        result.push(null);
      }
      else { //pripady velicin ktore su zastupene:
        if ([0, 1, 2, 3].includes(i)) { //intervaly
          result.push(SV.MOZNEIntervalySprav[dataVSprave[k]])
        }
        else if ([4, 5].includes(i)) { //tolerancie
          result.push(SV.TEPLOTY[dataVSprave[k]])
        }
        else if ([6].includes(i)) { //onOffAlarmPark
          result.push(Toolkit.fromIntToBinstring(dataVSprave[k]))
        }
        else if ([7].includes(i)) { //aktBoxy
          result.push(Toolkit.fromIntToBinstring(dataVSprave[k]))
        }
        else if ([8,9,10,11,12,13,14,15,16].includes(i)) { //i = 0/1 = ci je dany senzor vo vysledkoch alebo nie
          result.push([SV.TEPLOTY[dataVSprave[k]], SV.VLHKOSTI[dataVSprave[k+1]]]);
          k += 1 //pricitaj dalsie k pretoze SV.TEPLOTY maju kazda 2B
        }
        else if ([17, 18, 19].includes(i)) { //senzoryErrory
          result.push(Toolkit.fromIntToBinstring(dataVSprave[k]))
        }
        else if ([20].includes(i)) { //gps suradnice
          result.push(null);
        }
        else { //for further development
          result.push(null);
        }
        k += 1; //dalsia hodnota v DataVsprave
      }
      i++; //dalsi bit v zastupeni
    }
    // console.log(result);
    return result; //snad toto: [True, 5, 300, None, 1800, ('marek','drabik'), None, None)]
  }
}

module.exports = {
  Zabal: Zabal,
  Rozbal: Rozbal
}

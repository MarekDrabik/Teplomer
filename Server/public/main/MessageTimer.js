
//creates timer objects ("last", "next") on demand and automatically to simulate ticking clock
class MessageTimer {
  constructor(owner, interval = 6, timeReceived = 0, increasing = true) {
    this.owner = owner; //"last" or "next" element
    this.interval = interval; //current interval of thermometer's communication
    this.increasing = increasing;  //"last" is increasing true, "next" is false
    this.timeReceived = timeReceived; //time since last message from thermometer was received
    //by server - for synchronisation purpose
    this.time = timeReceived; //setter function
    this.timerMarkedToStop = false;
  }

  set time(t) { //calculate all the properties depending on current time to be displayed
    this._time = (this.increasing) ? t : (this.interval - t);
    this.hours = makeStringAndAppendZeroIfSingleDigit(Math.abs(parseInt(this._time / 3600)));
    this.minutes = makeStringAndAppendZeroIfSingleDigit(Math.abs(parseInt((this._time % 3600) / 60)));
    this.seconds = makeStringAndAppendZeroIfSingleDigit(Math.abs((this._time % 3600) % 60));
    this.sign = (this.time < 0) ? '-' : ' ';
    if (this.increasing == true) { //if it's "last" timer use default font color
      this.color = colorBoxBorders
    }
    else { //otherwise ("next" timer) use red/green depending if delayed or not
      if (this.time < 0) {
        this.color = "red";
      } else {
        this.color = "green";
      }
    }
  }
  get time() {
    return this._time;
  }

  get formatedTime () {
    return (this.sign + this.hours + ':' + this.minutes + ':' + this.seconds); 
  }

  stop () { this.timerMarkedToStop = true; } //jsut mark timer for stop, for actual stop see start()

  start() { //this is basically a looping recursive function that calls itself every 1 second which effectivelly works as ticking clock 
    if (this.timeReceived > 86399) { //stop both timers and display text if no message was received for one whole day
      this.owner.innerHTML = (this.increasing) ? ">24hours" : "-";
      this.stop(); //mark the timer to stop (see the code bellow)
    }
    if (this.interval == 123456789) { //stop the "next" timer if rpi was turned off by the user
      if (this.increasing == false) {
        this.owner.innerHTML = "off";
        this.stop(); //mark the timer to stop (see the code bellow)
      }
    }
    if ( this.timerMarkedToStop == false ) { //if this timer wasn't marked to be stopped
      //then render timer with newly calculated properties
      this.owner.innerHTML = this.formatedTime;
      this.owner.style.color = this.color;
      //and repeat function to tick another second
      setTimeout(()=>{
        this.start(); //repeat the function
      }, 1000)
      //finally increment the timeReceived because one more second passed since message was received:
      this.timeReceived += 1;
      this.time = this.timeReceived;  //this function is written after the "this.start()" 4 lines above but
      //it is actually executed before that function (bc.of setTimeout). This position in code makes 
      //no delay in this ticking second (not so important, just fun fact).
    }
  }
}


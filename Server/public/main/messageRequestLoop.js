//request on server every 2 seconds

function loopRequest(fresh = true) {
  setTimeout(() => {
    var options, url;
    if (fresh) { //on the absolutelly first request true/ otherwise false
      url = "/update/1"; //to fix the issue where enveloppe appears on first response from server yet it is not a fresh message from thermometer
    }else {
      url = "/update/0";
    }
    options = {
      method: 'GET',
      credentials: 'include',
      redirect: 'follow'
    };

    fetch(url, options) //returns promise
    .then(function (response) {
      if (response.ok) { //status 200 or 202 (201 is handled in sendingMode.js)
        kontrolka.style.display = 'block'; //flashing green light because server is responding
        setTimeout(() => {kontrolka.style.display = 'none';}, 1000);
        console.log("MESSAGE:", response);
        
        var message = response.json() //returns promise
        .then ((messJson) => { //messJson contains either all properties (if thermometer sent message) OR
          //it contains .lastTimeReceived property only if no fresh message from thermometer is available
          if (messJson) {
            console.log("New message received! :", messJson, "status:", this.status);
            if (messJson.casOdosielania) { //if this exists then its a fresh message from thermometer
              currentState.update(messJson); //update current state object (not screen yet)
              if (response.status != 202){ //202 is response status on 1. request to not show envelope
                showEnvelope();
              }
              console.log("New message received with status:", response.status, ". Seconds on next timer: ", timerForNext.time)
            }         
            // in any case, udpate timers if they are in delay with server:
            updateTimersIfNeeded(messJson.lastTimeReceived);

            if (discoMode_on === false){
              currentState.renderHtml(); //update the screen with new data but 
              //only if user didn't modify settings in a mean time cause discoMode is updating screen in that case
            }
          }
          else {
            console.log("no message received!");
          }
        })
        // console.log(message);
        
      }
      else if(response.status == 302) { //302 cookie expired
        console.log("responseRedirected");
        window.location.replace("/login"); // redirect to login page
        return;
      }
      else{
        console.log(response.status);
      }
    })
    loopRequest(fresh = false); //all except first one are not fresh requests anymore
  }
    , 2000) //request period
}
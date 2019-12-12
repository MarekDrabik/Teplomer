#!/usr/bin/python3.7

#this module reads the output from serial port and communicates it to the worker.

import serial, time, re, os, datetime

import ZDIELANE_PREMENNE as ZP
from ZDIELANE_PREMENNE import log, logSerial
#adapter staff needed:
from adapter import serialWorker as worker

def read():
  novyRiadok = b''
  CastSpravy = None
  serverUnreachable_count = 0

  while True:
    try:
      ZP.event_cakajNaPripojenie.wait()

      predoslyRiadok = novyRiadok
      novyRiadok = worker.serialPort.readline()

      logSerial.debug('line: ' + str(novyRiadok))

      #SIGNAL OK?
      najdi = re.search(r'b\'\+CSQ: (\d+),', str(novyRiadok))
      if najdi != None:
        try:
          signal = int(najdi.group(1))
        except:
          worker.queueSignal.put("CHYBA")
          log.error("SerialRead nacital neznamu hodnotu signalu: " + str(najdi.group(1)))
        else:
          if signal < 100:
            worker.queueSignal.put(signal)
      if b'+CSQ: 15,0' in novyRiadok:
        worker.queueSignal.put()

      #NET BLIKA?
      if b'AT+CREG?' in predoslyRiadok:
        if b'+CREG: 0,1' in novyRiadok: #registered, home network
          ZP.netBlika_queue.put(1)
        elif b'+CREG: 0,2' in novyRiadok or b'+CREG: 0,0' in novyRiadok:  #Not  registered,  but  MT  is  currently  searching  a  new  operator to register to
          ZP.netBlika_queue.put(2)
        elif b'+CREG: 0,3' in novyRiadok: #registration denied
          ZP.netBlika_queue.put(3)
        elif b'+CREG: 0,4' in novyRiadok: #unknown
          ZP.netBlika_queue.put(4)
        elif b'+CREG: 0,5' in novyRiadok: #registered, roaming
          ZP.netBlika_queue.put(5)
        else:
          log.error("CHYBA: cgreg odpoved:" + str(novyRiadok))

      #ODPOVEDA?
      if b'AT\r' in predoslyRiadok and b'OK\r' in novyRiadok:
        ZP.adapterOdpoveda_queue.put(1)

      #VYPNI internet:
        #CIPCLOSE
      if b'AT+CIPCLOSE' in predoslyRiadok: #-2 pretoze serial sam prida dva znaky do vystupu
        if (b'OK' in novyRiadok or b'ERROR' in novyRiadok):
          logSerial.debug("cipclose OK")
          worker.queueVypni.put('cipcloseOK')
        else:
          log.error("CHYBA: cipclose odpoved:" + str(novyRiadok))
          worker.queueVypni.put('chyba')
      
      #CIPSHUT
      if b'AT+CIPSHUT' in predoslyRiadok: #-2 pretoze serial sam prida dva znaky do vystupu
        if (b'SHUT OK' in novyRiadok):
          logSerial.debug("cipshut OK")
          worker.queueVypni.put('cipshutOK')
        else:
          log.error("CHYBA: cipshut odpoved:" + str(novyRiadok))
          worker.queueVypni.put('chyba')

      #PDP DEACT problem
      #tento problem podla mna nastava ked nevypnem poriadne internet pred vypnutim RPI.
      #to by sa nemalo stavat ak do toho nekafrem pri debugovani
      #nie celkom slusny pokus o vyriesenie problemu s +pdp deact po cipshut prikaze
      # if (b'+PDP: DEACT' in novyRiadok):
      #   print ("PDP FOUND")
        # worker.queueVypni.put('pdpDeactProblem')   

      #CIPSTATUS:
      if (b'STATE:' in novyRiadok):
        if (b'STATE: IP INITIAL' in novyRiadok):
          worker.queueZapni.put('IP INITIAL')
        elif (b'STATE: IP STATUS' in novyRiadok):
          worker.queueZapni.put('IP STATUS')
        # elif (b'STATE: TCP CLOSED' in novyRiadok):
        #   worker.queueZapni.put('TCP CLOSED')
        else:
          log.error("CHYBA: CIPSTATUS odpoved:"+ str( novyRiadok))
          worker.queueZapni.put('chyba')


      #ZAPNI internet:
        #CSTT
      if worker.prikazyNaZapni[0] in predoslyRiadok: #-2 pretoze serial sam prida dva znaky do vystupu
        if (b'OK' in novyRiadok):
          worker.queueZapni.put('csttOK')
        else:
          log.error("CHYBA: CSTT odpoved:"+ str( novyRiadok))
          worker.queueZapni.put('chyba')
        #CIICR
      if worker.prikazyNaZapni[1] in predoslyRiadok: #-2 pretoze serial sam prida dva znaky do vystupu
        if (b'OK' in novyRiadok):
          worker.queueZapni.put('ciicrOK')
        else:
          log.error("CHYBA: CIICR odpoved:"+ str( novyRiadok))
          worker.queueZapni.put('chyba')
        #CIFSR
      if worker.prikazyNaZapni[2] in predoslyRiadok: #-2 pretoze serial sam prida dva znaky do vystupu
        if re.search(r'b\'\d+.\d+.\d+.\d+', str(novyRiadok)) != None:
          worker.queueZapni.put('cifsrOK')
        else:
          log.warning("CHYBA: CIFSR odpoved:"+ str( novyRiadok))
          worker.queueZapni.put('chyba')

      #SOCKET:
      if b'ALREADY CONNECT' in novyRiadok:
        worker.queueSocket.put('alreadyConnect')

      if b'CONNECT FAIL' in novyRiadok:
        worker.queueSocket.put('serverUnreachable')

      if b'CONNECT OK' in predoslyRiadok and b'STATE:' not in predoslyRiadok:
        #reset counters since connection was successful
        ZP.troubleMonitor.alreadyConnect_resetCount()
        ZP.troubleMonitor.serverUnreachable_resetCount()
        
        
        dlzSpravy_code = novyRiadok[:2] #2byte
        dlzSpravy_int = ZP.CODE.index(dlzSpravy_code.decode())
        if dlzSpravy_int == 0: #server nema ziadnu spravu od androidu, poslal default: b'\x00\x00\x00\x00'
          worker.prijataSpravaOsekana = '00'
        else: #nacitaj prijatu spravud

          worker.prijataSpravaOsekana = novyRiadok.decode()[:-2]
        log.debug("prijataSprava " + str(worker.prijataSpravaOsekana))
        worker.queueSocket.put('cipstartOKspravaPrijata')
      
      #CIPSEND, ak dostanes cerstvu poziadavnku na odosielanie tak len pockaj chvilu a daj zelenu:
      if worker.prikazyPosliSpravu[0] in novyRiadok:
        time.sleep(0.3)
        worker.queueSocket.put('cipsendOK')
      if b'SEND OK' in novyRiadok:
        
        worker.queueSocket.put('sendOK') #put sendOK just now so that Socket() reads message just now
      if b'CLOSED' in novyRiadok and b'TCP CLOSED' not in novyRiadok and b'CLOSE OK' not in novyRiadok and b'STATE:' not in novyRiadok: #TCP CLOSED is when connection fails. we dont want to mistaken it for successful communication (CLOSED)
        worker.queueSocket.put('closed')         

      time.sleep(0.01)


    except AttributeError:
      log.error("SerialRead hlasi nepripojeny adapter! (ser == None)")
      ZP.event_cakajNaPripojenie.clear()
    except serial.serialutil.SerialException:
      log.error("SerialRead hlasi nepripojeny adapter! (SerialException)")
      ZP.event_cakajNaPripojenie.clear()
    except:
      if datetime.datetime.now().microsecond % 999000 == 0:
        log.exception("serialRead problem!")
      else:
        pass
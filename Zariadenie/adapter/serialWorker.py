#!/usr/bin/python3.7

#this module is sending commands on serial port of the GSM adapter.


import serial, time, queue, os
import RPi.GPIO as GPIO

import pomocne_funkcie.specialne_pomocne_funkcie as specialne
import ZDIELANE_PREMENNE as ZP
from ZDIELANE_PREMENNE import log


#queue... sluzia na komunikaciu medzi serialWorker a serialReader
queueSocket = queue.Queue(1)  
queueZapni = queue.Queue(1)
queueVypni = queue.Queue(1)
queueSignal = queue.Queue(1)

prijataSpravaOsekana = b''

prikazyPrijmiSpravu = [b'AT+CIPSTART="TCP","87.197.183.237",3080\r']
prikazyPosliSpravu = [b'AT+CIPSEND\r', b'AT+CIPCLOSE\r']
prikazyNaVypni = [b'AT+CIPCLOSE\r',b'AT+CIPSHUT\r']
prikazyNaZapni = [b'AT+CSTT=\"o2internet\"\r', b'AT+CIICR\r', b'AT+CIFSR\r']
internetByMalBytPripraveny = False #False pri cerstvom adapteri - idealne
serialPort = None # pri starte RPI je toto zacne odkazovat na serial port. pomocou zavolania funkcie pripojAdapter()   

def telefonuj():
  try:      
    log.info("Telefonujem!")    
    volajTelefon =  b'ATD' + ZP.TEL_CISLO + b';\r\n'
    zlozTelefon = b'ATH\r\n'

    serialPort.write(zlozTelefon)  #najprv zloz telefon lebo niekedy sa moze stat, ze ostane vysiet z predchadzajuceho hovoru
    time.sleep(0.1)
    serialPort.write(volajTelefon)
    time.sleep(60) #8 sekund vytaca a zvoni 52 sekund
    serialPort.write(zlozTelefon)
    return 0
  except:
    log.exception("EXCEPTION!")
    return 1

def prijmiSpravu():
  global prijataSpravaOsekana

  for pocetZlyhani in range (3): #normally there is just one loop because there a return statement appears.
    try:

      prijataSpravaOsekana = 1  #prepare to return 1 in case serialRead didn't read any better value for the message
      if queueSocket.full():
        queueSocket.get()

      log.debug("Prijmam spravu...")
      #initiate connection
      serialPort.reset_input_buffer()
      serialPort.write(prikazyPrijmiSpravu[0])
      q_get = queueSocket.get(timeout = 10) #raises queue.Empty when serialRead doesnt reply and we run another loop of this function
      if q_get == 'cipstartOKspravaPrijata':
        prijataSprava = prijataSpravaOsekana
        return prijataSprava
      elif q_get == 'alreadyConnect':
        ZP.troubleMonitor.alreadyConnect_addCount()
        log.error("Already connected.")
        return 1  #this return will make manager redo 'posta' work but only if above count is not exceeded.
      elif q_get == 'serverUnreachable':
        ZP.troubleMonitor.serverUnreachable_addCount()
        log.error("Server unreachable.")
        return 2 #this return will make manager redo 'posta' work but only if above count is not exceeded.
      else:
        log.error("Vyskytla sa neznama chyba, restartujem internet!")
        return 1 #this can be repeating infinitelly as long as serialRead doesnt get fixed. I expect this to not happen.
  
    except queue.Empty:
      if pocetZlyhani >= 2: #only when we tried 3 times, restart adapter
        ZP.adapterJob_prioDeq.put('pwrKeyAdapter', delete = False) #keep other jobs pending as we are just fixing something
        return 1  #this can be repeating infinitelly as long as serialRead doesnt get fixed. I expect this to not happen.
      log.exception("Spravu sa asi nepodarilo PRIJAT - serial neodpoveda. Pokus " + str(pocetZlyhani) + "/3. Potom restartujem.")

def posliSpravu(response):
  #this function, in order to work properly, has to follow prijmiSpravu() function in serial logic
  for pocetZlyhani in range (3):
    try:
      #initiate sending:
      serialPort.write(prikazyPosliSpravu[0])
      #cakaj na ODOSIELANIE:
      if queueSocket.get(timeout = 10) == 'cipsendOK':
        serialPort.write(bytes(response, 'utf-8') + b'\x1a\r\n')
      else:
        log.error("Serial neprijal spravu na odoslanie.")
        return 1  #AdapterManager o tom upozorni ale tento pripad zatial ignorujeme.
      #cakaj na SEND OK:
      if queueSocket.get(timeout = 10) == 'sendOK':
        log.info("Sprava odoslana.")\
        #serialPort.write(prikazyPosliSpravu[1]) #ignoruj, socket sa zatvara automaticky
      else:
        log.critical("Serial odpoved na odoslanie spravy je necakana. SERVER neodpoveda?!")
        return 1 #AdapterManager o tom upozorni ale tento pripad zatial ignorujeme.
      #cakaj na closed:
      if queueSocket.get(timeout = 10) == 'closed':
        log.debug("Socket closed.")
        cistyCipshut()
      else:
        log.warning("Socket closed didn't work but I ignore it.")
      
      #ak nenastal problem, return 0:
      return 0  #message was sent at this point 

    except queue.Empty:
      if pocetZlyhani >= 2: #only when we tried 3 times, restart adapter
        ZP.adapterJob_prioDeq.put('pwrKeyAdapter', delete = False) #keep other jobs pending as we are just fixing something
        return 1 #AdapterManager o tom upozorni ale tento pripad zatial ignorujeme.
      log.exception("Spravu sa asi nepodarilo odoslat - serial neodpoveda. Pokus " + str(pocetZlyhani) + "/3. Potom restartujem.")




def otazkaSignalOk():
  log.debug("Signal ok?")
  if queueSignal.full():
    queueSignal.get()

  try:
    serialPort.write(b'AT+CSQ\r')
    q_get = queueSignal.get(timeout = 5)
    specialne.ulozSiluSignalu(q_get)
    if type(q_get) is int:
      if q_get in [0,99]:
        log.error("Ziaden signal!")
        return False
      elif q_get in [1,2,3,4]:
        log.debug("Slaby signal: " + str(q_get))
        return True
      else:
        log.debug("Sila signalu dostacujuca: " + str(q_get))
        return True
    else:
      log.error("Serial vratil chybu!")
      return False

  except:
    log.error("serialRead neodpovedal nacas!")
    return False

def otazkaPripravenyNaSpojenie():
  global internetByMalBytPripraveny
  #otazka: AT+CIPSTATUS
  #odpoved: STATE: TCP CLOSED je status po uspesnej komunikacii (odoslanej sprave)
  #odpoved: STATE: CONNECT OK je status po cerstom cipstart pripojeni (po prijati spravy) na server pred odoslanim spravy
  #odpoved: STATE: IP INITIAL je pred spustenim internetu (=cerstvy adapter pred AT+CSTT>AT+CIICR>AT+CIFSR procedurou)
  #                           je aj po CIPSHUT ale po procedure AT+CSTT>AT+CIICR>AT+CIFSR
  #odpoved: STATE: IP STATUS je zapnuty internet (cifsr odpoved je IPcka) = pripraveny na AT+CIPSTART komunikaciu so serverom
  #odpoved: STATE: IP START je ked je cstt o2internet ale ciicr este nie je nic
  #odpoved: STATE: IP GPRSACT je ked je ciicr OK (po cstt) ale cisfr este nie je nic
  # cipshut je recommended pred cipstart stale ak status nie je IP STATUS / IP INITIAL
  #vyprazdni queue
  log.debug("Zapnuty internet?")
  if queueZapni.full():
    queueZapni.get()

  try:
    serialPort.write(b'AT+CIPSTATUS\r')
    q_get = queueZapni.get(timeout = 5)
    if q_get == "IP STATUS":
      log.debug("Internet zapnuty. status: IP STATUS (pripraveny na komunikaciu CIPSTART)")
      return True
    if q_get == "IP INITIAL":
      log.debug("status: IP INITIAL")
      # log.debug("INTERNET PRIPRAVENY VARIABLE: " + str(internetByMalBytPripraveny))
      if internetByMalBytPripraveny == True: #ak si uz zapinal internet (stane sa pri spusteni RPI) tak vrat true a ani sa nepytaj na cifsr nech nezatazujeme adapter pri kazdej sprave
        return True                         #ak by to bol problem (co by standardne nemal) tak ten sa vyriesi nejak sam v druhom pokuse
      serialPort.write(b'AT+CIFSR\r')
      if queueZapni.get(timeout = 5) == "cifsrOK":  #ak nevrati cifsrOK, tak sa dostaneme dole restartujeme internet
        log.debug("Internet zapnuty. AT+CIFSR vratil IP")
        return True
    # if q_get == "TCP CLOSED":
    #   log.debug("Internet zapnuty. status: TCP CLOSED (predosla komuniakcia prebehla uspesne).\
    #    Riskujem lebo v manualy nie je explicitne uvedene, ze tento status je ok na nasledny CIPSTART.")
    #   return True

    #return false vo vsetkych pripadoch okrem IP STATUS a IP INITIAL + CIFSR OK. Pretoze aj ked je mozno internet pripojeny,
    #nie sme v spravnom stave (ako je uvedene v manuale)
    vypniInternet() #toto je poistka pre PDP DEACT problem. v inych pripadoch by stacilo raz.
    #vypniInternet je lepsie ako priamo volat CIPSHUT lebo skript v druhom pripade necaka na odpoved a prepisuje adapter halabala.
    return False
    #teraz ocakavam, ze volajuca funkcia zavola AT+CIPSHUT + zapniInternet()

    

  #STARE:
  # try:
  #   serialPort.write(b'AT+CIFSR\r')
  #   if queueZapni.get(timeout = 5) == "cifsrOK":
  #     log.debug("Internet zapnuty")
  #     return True
  #   else:
  #     log.warning("Internet nie je zapnuty.")
  #     return False

  except:
    log.error("serialRead neodpovedal nacas!")
    return False

def restartujInternet():
  log.debug("Restartujem internet...")
  vypniInternet()
  zapniInternet()

def otazkaNETblika():
  log.debug("Blika NET (sim registrovana)?")
  #vyprazdni queue
  if ZP.netBlika_queue.full():
    ZP.netBlika_queue.get()

  try:
    serialPort.write(b'AT+CREG?\r\n')
    q_get = ZP.netBlika_queue.get(timeout = 7)
    if q_get == 1:  #cakam na odpoved, do 10 sekund
      log.debug("Net blika - home network")
      return True
    elif q_get == 5:  #cakam na odpoved, do 10 sekund
      log.debug("Net blika - roaming network")
      return True
    elif q_get == 2:  #cakam na odpoved, do 10 sekund
      log.error("Net neblika - hlada siet ...")
      return 2
    elif q_get == 3:  #cakam na odpoved, do 10 sekund
      log.error("Net neblika - registracia zamietnuta")
      return False
    elif q_get == 4:  #cakam na odpoved, do 10 sekund
      log.error("Net neblika - neznamy problem")
      return False
    else:
      log.error("serialRead nevratil co bolo ocakavane.")
      return False

  except:
    log.error("serialRead neodpovedal nacas!")
    return False

def zacniBlikat(verzieBlikania): #zaregistruj sa na siet
  #verzieBlikania su True/False/2
  if verzieBlikania == True:
    return 0
  elif verzieBlikania == 2:
    log.debug("Zda sa, ze siet sa pripaja, cakam par sekund.")
    time.sleep(7) #pockaj par sekund a snad uz to bude ok
    return 0
  elif verzieBlikania == False:
    log.error("Nepodarilo sa pripojit na operator <=> NET neblika pomaly.")
    return 1
  
def otazkaOdpoveda():
  #vyprazdni queue
  log.debug("Odpoveda adapter na prikazy?")
  if ZP.adapterOdpoveda_queue.full():
    ZP.adapterOdpoveda_queue.get()

  #ak nie tak repripoj/restartuj Rpi. lebo moze byt pripojeny (ttyUSB existuje) ale moze byt OFF
  try:
    serialPort.write(b'AT\r\n')
    ZP.adapterOdpoveda_queue.get(timeout = 2) #cakam na odpoved, par sekund
    log.debug("Adapter odpoveda na prikazy.")
    ZP.troubleMonitor.adapterNotRestarting_resetCount()
    return True
  except:
    log.warning("Adapter neodpoveda na prikazy!")
    ZP.troubleMonitor.adapterNotRestarting_addCount()
    return False

def otazkaPripojeny():
  #vrati true ak ser je pripojeny na serial, problem je ak sa medzicasom odpojil preto tuto funkciu vynechavam
  pripojeny = type(serialPort) is serial.serialposix.Serial
  log.debug("Adapter je pripojeny? True/False: " + str(pripojeny))
  return pripojeny
  
def pripojAdapter():
  #len pri zapnuti RPI
  global serialPort

  try:
    #v pripade ze subor /dev/ttyUSB* chyba, restaruj USB porty resp. RPI
    adapterFile = os.popen('ls /dev/ttyUSB*').readlines()[0][:-1]
    serialPort = serial.Serial(adapterFile, 115200)
    log.debug("Pripojil som adapter.")
    ZP.event_cakajNaPripojenie.set()
    # time.sleep(2)
    return 0
  except:
    serialPort = None
    log.exception("EXCEPTION!")
    log.error("Adapter sa nepodarilo pripojit!")
    return 1

def pwrKeyAdapter():
  try:
    log.debug("Posielam signal na spinac adaptera!")
    #BCM numbering:
    GPIO.setmode(GPIO.BCM)
    #set to output mode = adapter will not modify its value
    GPIO.setup(19, GPIO.OUT)
    #change state to LOW/HIGH
    GPIO.output(19, GPIO.LOW)
    time.sleep(4)
    GPIO.output(19, GPIO.HIGH)
    GPIO.cleanup()
    log.debug("Poslal som signal na spinac adaptera. Cakam par sekund na nacitanie SIM.")
    time.sleep(7)
    log.debug("hotovo")
    return 0
  except:
    log.exception("EXCEPTION!")

def cistyCipshut():
  try:      #funguje len ak bezi thread serialRead()
    #CIPSHT:
    #najprv vymaz queue
    if queueVypni.full():
      queueVypni.get()

    serialPort.write(prikazyNaVypni[1])
    try:
      if queueVypni.get(timeout = 4) == 'cipshutOK':
        log.info("AT+CIPSHUT > SHUT OK.")
        return 0
      else:
        log.error("postup nebol dodrzany alebo sa vyskytla chyba, restartuj internet")
        return 1
    except:
      log.error("Nepodarilo sa.")
      return 1

  except queue.Empty:
    log.exception("serialRead neodpovedal nacas!")
  except:
    log.exception("EXCEPTION!")


def vypniInternet():
  try:      #funguje len ak bezi thread serialRead()
    
    #VYPNI INTERNET:
    #najprv vymaz queue
    if queueVypni.full():
      queueVypni.get()

    log.info("Vypinam internet...")
    serialPort.write(prikazyNaVypni[0])
    try:
      if queueVypni.get(timeout = 3) == 'cipcloseOK':
        log.debug("cipclose OK")
        serialPort.write(prikazyNaVypni[1]) #cipshut
      else:
        log.error("A postup nebol dodrzany alebo sa vyskytla chyba, restartuj internet")
        return 1
    except:
      log.error("Nepodarilo sa.")
      return 1

    try:
      if queueVypni.get(timeout = 5) == 'cipshutOK':
        log.info("AT+CIPSHUT > SHUT OK.")
        return 0
      else:
        log.error("postup nebol dodrzany alebo sa vyskytla chyba, restartuj internet")
        return 1
    except:
      log.error("Nepodarilo sa.")
      return 1

  except queue.Empty:
    log.exception("serialRead neodpovedal nacas!")
  except:
    log.exception("EXCEPTION!")

def zapniInternet():
  global internetByMalBytPripraveny

  try:      #funguje len ak bezi thread serialRead()
    
    #ZAPNI INTERNET
    if queueZapni.full():
      queueZapni.get()

    log.info("Zapinam internet...")
    serialPort.write(prikazyNaZapni[0])
    if queueZapni.get(timeout = 5) == 'csttOK':
      serialPort.write(prikazyNaZapni[1])
    else:
      log.error("postup nebol dodrzany alebo sa vyskytla chyba, restartuj internet")
      return 1
    if queueZapni.get(timeout = 5) == 'ciicrOK':
      serialPort.write(prikazyNaZapni[2])  
    else:
      log.error("postup nebol dodrzany alebo sa vyskytla chyba, restartuj internet")
      return 1
    if queueZapni.get(timeout = 5) == 'cifsrOK':
      log.info("Internet zapnuty!")
      internetByMalBytPripraveny = True
      return 0
    else:
      log.error("postup nebol dodrzany alebo sa vyskytla chyba, restartuj internet")
      return 1

  except queue.Empty:
    log.exception("serialRead neodpovedal nacas!")
  except:
    log.exception("EXCEPTION!")

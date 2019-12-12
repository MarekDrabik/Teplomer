#!/usr/bin/python3.7

#this module provides helping functions that call operating system functionalities (Bash) or WittyPi scripts.

import threading, time, sys, os, datetime
import RPi.GPIO as GPIO

import ZDIELANE_PREMENNE as ZP
from ZDIELANE_PREMENNE import log


def pin_to_HighState():
  #BCM numbering:\
  log.debug("Putting pin 19 high.")
  GPIO.setmode(GPIO.BCM)
  #set to output mode = adapter will not modify its value
  GPIO.setup(19, GPIO.OUT)
  #chanGPIOe state to LOW/HIGH
  GPIO.output(19, GPIO.HIGH)
  time.sleep(1)
  GPIO.cleanup()
# def jeVybitaBateria():
#   status = os.popen("dmesg | grep --silent Under-voltage; echo $?").readlines()[0][0]
#   if status == '0':
#     log.warning("Under-voltage detected.")
#     return True
#   else:
#     return False

def clearStartupTime():
  try:      
    skript = "clear_startup_time.sh"
    os.system('bash ' + ZP.MAIN_DIR + skript)

  except:
    log.exception("EXCEPTION!")

def systemTimeToRtc():
  try:
    skript = 'systemTimeToRtc.sh'
    os.system('bash ' + ZP.MAIN_DIR + skript)

  except:
    log.exception("EXCEPTION!")

def startupTime(wittySched):
  try:      
    skript = 'set_startupWitty.sh'
    os.system('bash ' + ZP.MAIN_DIR + skript + " " + wittySched)

  except:
    log.exception("EXCEPTION!")

def utilities():
  try:      
    skript = "utilities.sh"
    return os.popen('bash ' + ZP.MAIN_DIR + skript).readlines()

  except:
    log.exception("EXCEPTION!")

def getRpiTemperature():
  try:      
    return os.popen("/opt/vc/bin/vcgencmd measure_temp").readlines()

  except:
    log.exception("EXCEPTION!")

def vypniRpiPomocouWittyPi():
  #wittyPi pin state
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(4, GPIO.OUT)
  GPIO.output(4, GPIO.LOW)
  time.sleep(5)
  GPIO.output(4, GPIO.HIGH)
  GPIO.cleanup()

def isDebugMode(): #testovanie WittyPi = rpi sa realne nevypne
  with open(ZP.MAIN_DIR + "debug", "r") as f:
    text = f.read()
    if text[0] == '1':
      return True
    else:
      return False

def uspiRpi(trvanieSpanku, pociatok):
  try:      
    '''tato funkcia:
    1.vypina RPI a zapise default odpocet
    2.uspava RPI a odrata dlzku spanku z odpoctu
    3.len chvilu caka(ak sa neoplati spat alebo ide o DEBUG mod), odrata dlzku cakania z odpoctu
    '''
    #1. vypni RPI:
    if trvanieSpanku == None:
      log.info("Vypinam RPI natrvalo! Zapisujem defaultne hodnoty do konfig.json a odpocet.json.")
    
    #2. uspi pomocou WittyPi:
    else: 
      trvanieSpanku = round(trvanieSpanku)
      systemTimeToRtc()
      time.sleep(4)
      #pociatok je nadiktovany uz v Main pri vypocte oddychu
      casZapnutia = pociatok + datetime.timedelta(seconds = trvanieSpanku) #datetime object
      if trvanieSpanku < 60: #sekundova schedule sluzi len pre RPI restart
        wittySched = "?? ?? ?? " + str(casZapnutia.second)
        log.info("Pozadovany spanok je " + str(trvanieSpanku) + "s. Pociatok: " + str(pociatok) + ". Zapisujem Witty Startup Time:" + str(wittySched))
      elif trvanieSpanku < 3600: #minutova schedule
        wittySched = "?? ?? " + str(casZapnutia.minute) + " " + str(casZapnutia.second)
        log.info("Pozadovany spanok je " + str(trvanieSpanku) + "s. Pociatok: " + str(pociatok) + ". Zapisujem Witty Startup Time:" + str(wittySched))
      else: #hodinova schedule
        BUG = 2 #v set_startup_time.sh je nejaka chyba a zapisany spanok ma inu hodnotu ako ten pozadovany, toto to opravi
                #to co sa zobrazuje vo wittyPi.sh skripte je to co wittyPi respektuje
        wittySched_bezBUGU =  "?? " + str(casZapnutia.hour) + " " + str(casZapnutia.minute) + " " + str(casZapnutia.second)
        wittySched = "?? " + str(casZapnutia.hour - BUG) + " " + str(casZapnutia.minute) + " " + str(casZapnutia.second)
        log.info("Pozadovany spanok je " + str(trvanieSpanku) + "s. Pociatok: " + str(pociatok) + ". Zapisujem Witty Startup Time:" + str(wittySched_bezBUGU))
      startupTime(wittySched)
    
    #turn off GPS if it is running
    active_threads = [x.name for x in threading.enumerate()]
    if 'MerajGps' in active_threads:
      log.debug("Vypinam spustene GPS.")
      Meraj.vypni_GPS()
      time.sleep(5)

    #in case we are in debug mode, dont shut down RPI, just stop the program
    debugModeON = isDebugMode()
    log.debug("debug?: " + str(debugModeON))
    if (debugModeON):     
      log.debug("Debug je zapnuty, nevypinam RPI")
    else:
      log.debug("RPI sa vypina!")
      vypniRpiPomocouWittyPi()
      
    sys.exit(0)
  
  except:
    log.exception("EXCEPTION!")
      


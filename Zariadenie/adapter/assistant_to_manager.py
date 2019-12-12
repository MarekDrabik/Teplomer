#!/usr/bin/python3.7

# This module is the assistant to adapter manager that takes orders from manager and calls worker to perform the calls on serial port of adapter.

import ZDIELANE_PREMENNE as ZP
from ZDIELANE_PREMENNE import log
#adapter staff needed:
from adapter import serialWorker as worker

MAX_POCET_POKUSOV = 5

def pripravOdosielanie():
  #najprv zisti ci je treba nieco robit, ak ano tak nastav adapter na odosielanie
  #indexy pripadne nulovat v behu...
  if (zarucInternetZapnuty() == 0 and worker.otazkaSignalOk() == True):
    log.info("Adapter pripraveny na odosielanie.")
    #kedze adapter evidentne funguje a je v poriadku, resetni adapterNotRestarting
    ZP.troubleMonitor.adapterNotRestarting_resetCount() 
    return 0
  else:
    return 1
    
def pripravTelefonovanie():
  #najprv zisti ci je treba nieco robit, ak ano tak nastav adapter na telefonovanie
  #indexy pripadne nulovat v behu...
  if (zarucNETblika() == 0 and worker.otazkaSignalOk() == True):
    log.info("Adapter pripraveny na telefonovanie.")
    #kedze adapter evidentne funguje a je v poriadku, resetni adapterNotRestarting
    ZP.troubleMonitor.adapterNotRestarting_resetCount()
    return 0
  else:
    return 1

def zarucInternetZapnuty():
  i = 0
  while not worker.otazkaPripravenyNaSpojenie():
    if i >= MAX_POCET_POKUSOV:
      critical()
      return 1
    i += 1
    
    zarucNETblika()
    worker.restartujInternet() #najprv vypneInternet.

  return 0 

def zarucNETblika():
  i = 0
  netBlika = worker.otazkaNETblika()
  while not netBlika == True:
    if i >= MAX_POCET_POKUSOV:
      critical()
      worker.pwrKeyAdapter() #turn off adapter, it is probably stucked. Next job will turn it back on.
      return 1
    i += 1

    if netBlika == False:
      zarucOdpAPripojenie()
      #over podmienku while ked si opravil internet:
      netBlika = worker.otazkaNETblika()
      continue

    if netBlika == 2:
      pass #zacniBlikat(caka par sekund)
    
    worker.zacniBlikat(netBlika)#argument to znova moze byt True/False/2
    netBlika = worker.otazkaNETblika()
  return 0

def zarucOdpAPripojenie():
  #ze odpoveda a je pripojeny na /dev/ttyUSB*
  i = 0
  while not (worker.otazkaOdpoveda() and worker.otazkaPripojeny()):
    if i >= MAX_POCET_POKUSOV:
      log.critical("Adapter nie je pripojeny!")
      return 1
    i += 1  

    worker.pwrKeyAdapter()
    worker.pripojAdapter()
  return 0

def critical():
  log.critical("FATAL ERROR")

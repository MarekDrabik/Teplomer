#!/usr/bin/python3.7

#this module defines some helping functions that are specific to certain parts of the whole progam.

import time
from functools import *
from math import ceil

import pomocne_funkcie.vseobecne_pomocne_funkcie as vseobecne
import ZDIELANE_PREMENNE as ZP
from ZDIELANE_PREMENNE import log, logVysledky


def initiatePhoneCallOnAlarm(): #function running endless loop that triggers a phone call if mainAlarm is triggered.
  try:
  #vyzvana kym ma konfigD nastavene onOffAlarmPark na 1, toto moze zmenit na 0 len android!
    poslednyVolanieCas = 155 #prvotna dummy hodnota
    casOdPoslednehoVolania = 0
    while True:
      if ZP.troubleMonitor.isOn_mainAlarm():
        if casOdPoslednehoVolania >= 150:  # sekund medzi volaniami
          ZP.adapterJob_prioDeq.put('telefonuj')  #toto nech vrati az ked skonci vyzvananie!
          poslednyVolanieCas = time.time()
        casOdPoslednehoVolania = time.time() - poslednyVolanieCas

      time.sleep(1)  #kontroluj v tejto periode

  except:
    log.exception("EXCEPTION!")


def checkIfHeatIndexIsHealthy(tuple_tep_vlh):
  try:
    t = tuple_tep_vlh[0]
    v = tuple_tep_vlh[1]
    tolerLow, tolerHigh = ZP.konfigD["tolerLow"],  ZP.konfigD["tolerHigh"]
    
    heatIndex = vseobecne.Pomoc.heatIndexCalculate(t,v)
    if heatIndex > tolerLow and heatIndex < tolerHigh:  #teplota je ok aj v hranicnych hodnotach
      return True
    else:
      return False

  except:
    log.exception("EXCEPTION!")


def obycajnyPriemerMerani(snz): #makes an average of last couple of measurings for given sensor
  with ZP.zhromTep_lock:
    vstupnyList = list(ZP.zhromazdisko_tep[snz])[-ZP.VELKOST_OKNA_MERANI:]  #toto je casto asi aj ovela mensie ako VELKOST_OKNA_MERANI ked ide o cerstve odosielanie za cerstvym meranim 
  if len(vstupnyList) == 0:  #toto by aj tak nikdy nemalo nastat
    return (None,None)
  elif len(vstupnyList) == 1:
    return (vstupnyList[0])
  else:
    #vyluc (None,None),(12,None),(None,12) pripady:
    vstupnyList_redukovany = list(filter(lambda x: x[0] is not None and x[1] is not None, vstupnyList))
    #vyluc teploty mimo kalibr. rozsahu:
    vstupnyList_redukovany = list(filter(lambda x: x[0] >= -40 and x[0] <= 80 and x[1] >=0 and x[1] <= 100, vstupnyList_redukovany))

  if len(vstupnyList_redukovany) == 0:  #vsetky hodnoty boli chybne
    return (None,None)
  else:
    teploty = [x[0] for x in vstupnyList_redukovany]
    vlhkosti = [x[1] for x in vstupnyList_redukovany]
    return(vseobecne.Pomoc.priemer(teploty), vseobecne.Pomoc.priemer(vlhkosti)) #(avg. temp, avg. humid)

def vysledkyAkoPriemeryMerani():
  
  AktTepVlh = [obycajnyPriemerMerani(snz) for snz in ZP.SENZORY[:7]]
  #stare AktTepVlh = [ZP.zhromazdisko_tep[x][-1] for x in ZP.SENZORY[:6]]
  #round the values:
  vsetkyTepVlh_rounded_LI = []
  for x in AktTepVlh:
    if x == (None,None): #(None,None) only when there is really no other valid reading available:
      vsetkyTepVlh_rounded_LI.append(x)
    else:
      vsetkyTepVlh_rounded_LI.append((vseobecne.Pomoc.zaokruhli_napoli(x[0]),vseobecne.Pomoc.zaokruhli_napoli(x[1])))
  #pridaj aj ostatne - rpi, wittyPI:
  #tv_rpi obsahuje hodnotu GSM signalu namiesto vlhkosti!!!
  vsetkyTepVlh_rounded_LI.append((vseobecne.Pomoc.zaokruhli_napoli(ZP.zhromazdisko_tep['rpi'][-1][0]), ZP.silaSignalu))
  vsetkyTepVlh_rounded_LI.append((vseobecne.Pomoc.zaokruhli_napoli(ZP.zhromazdisko_tep['wittyPi'][-1][0]),vseobecne.Pomoc.zaokruhli_napoli(ZP.zhromazdisko_tep['wittyPi'][-1][1])))
  ########
  return vsetkyTepVlh_rounded_LI #[(23.4,23),(12.4,54.3)...]


def vyberValidneMerania(snz):
  #vstupom je list merani zo zhromazdiska, moze byt roznej velkosti!
  #my musime zarucit, ze z neho vieme vybrat VELKOST_OKNA_MERANI validnych merani
  #tzn. ze ak tam je vela None alebo chyb alebo je zhromazdisko este nenaplnene tak vratime None aby teplomer nameral dalsiu hodnotu
  velkostOkna = ZP.VELKOST_OKNA_MERANI
  #maximalny pocet None/chybnych merani je urceny touto podmienkou:
  while velkostOkna <= ceil(ZP.VELKOST_OKNA_MERANI * ZP.ZVACSENIE_KVOLI_MOZNYM_CHYBAM):
    with ZP.zhromTep_lock:
      vstupnyList = list(ZP.zhromazdisko_tep[snz])[-velkostOkna:]
    if len(vstupnyList) < velkostOkna: 
      return None #lebo zhromazdisko este ani nema dostatok nameranych hodnot\
    #vyluc (None,None),(12,None),(None,12) pripady:
    vstupnyList_redukovany = list(filter(lambda x: x[0] is not None and x[1] is not None, vstupnyList))
    #vyluc teploty mimo kalibr. rozsahu:
    #taketo hodnoty sa tu v skutocnosti nikdy neobjavia pretoze uz boli zmenene na (None, None) v measure.Temp... Ale pre istotu tento pripad je osetreny aj tu.
    vstupnyList_redukovany = list(filter(lambda x: x[0] >= -40 and x[0] <= 80 and x[1] >=0 and x[1] <= 100, vstupnyList_redukovany))  
    #ak nie je dost validnych merani, zvacsi okno
    if (len(vstupnyList_redukovany) < ZP.VELKOST_OKNA_MERANI):
      velkostOkna = velkostOkna + 1 
    else:
      return vstupnyList_redukovany[-ZP.VELKOST_OKNA_MERANI:] #vrat poslednych VELKOST_OKNA_MERANI validnych hodnot

  return None #lebo prilis vela chybnych merani

  #vratime None ak potrebujeme teplomer namerat viac hodnot
  ##vratime poslednych VELKOST_OKNA_MERANI validnych hodnot ak sme take nasli

def MessageNotInAdapterQueue(): #check if "posta" (message sending) is in the managers work queue 
  with ZP.adapterJob_prioDeq.lock:
    for List in ZP.adapterJob_prioDeq.deqList:
      for task in List:
        if task == 'posta':
          return False
    return True
  
def zapniInternetVopred(intInfTep, intInfGps): #zapni internet ak je potrebny
  #ak je informovanie neziaduce, tak zadaj velke hodnoty ktore neprejdu podmienkou dole:
  intInfTep = 99999999 if intInfTep == None else intInfTep
  intInfGps = 99999999 if intInfGps == None else intInfGps
  
  #priprav odosielanie len ak odpocet je rovny (aby som to spustil len raz a nie neustale kvoli <> znakom)
  #predpriprava nie je narocna na adpater, zvycajne bud zapneInternet alebo ak internetByMalBytZapnuty == True tak len overi ci CIPSTATUS = IP INITIAL
  if intInfTep == ZP.PREDPRIPRAVA_ODOSIELANIA or intInfGps == ZP.PREDPRIPRAVA_ODOSIELANIA:
    try:
      log.debug("Internet je potrebny, priprav odosielanie.")
      ZP.adapterJob_prioDeq.put('pripravOdosielanie')
    except:
      log.warning("Prikaz 'pripravOdosielanie' ignorovany - ManagerThread je zaneprazdneny")
  
def ulozSiluSignalu(signal): #safe signal value to ZP.signal in proper format for further messaging
  if type(signal) is int:
    if signal in range(0,32):
      ZP.silaSignalu = signal
      return
  ZP.silaSignalu = 99  #not int or 99 (undetectable) - zobrazi sa ako pomlcka

def aktualizujKonfigDSpravou(sprava_obj):
  #return new konfigD dictionary which is the modification of ZP.konfigD based on the message object
  try:
    konfigD = {}
    with ZP.konfigD_lock:
      if sprava_obj.casOdosielania != None:
        konfigD['casOdosielania'] = sprava_obj.casOdosielania
      else:
        konfigD['casOdosielania'] = ZP.konfigD['casOdosielania']
      #ZMENI DATA LEN TAM KDE NIE JE NONE, tzn. hodnoty ktore neboli pozadovane ostavaju povodne
      #skontroluj co bolo prijate a nacitaj slovnik
      if sprava_obj.intervalMerTep != None:
        konfigD['intervalMerTep'] = sprava_obj.intervalMerTep
      else:
        konfigD['intervalMerTep'] = ZP.konfigD['intervalMerTep']
      if sprava_obj.intervalMerGps != None:
        konfigD['intervalMerGps'] = sprava_obj.intervalMerGps
      else:
        konfigD['intervalMerGps'] = ZP.konfigD['intervalMerGps']
      if sprava_obj.intervalInfTep != None:
        konfigD['intervalInfTep'] = sprava_obj.intervalInfTep
      else:
        konfigD['intervalInfTep'] = ZP.konfigD['intervalInfTep']
      if sprava_obj.intervalInfGps != None:
        konfigD['intervalInfGps'] = sprava_obj.intervalInfGps
      else:
        konfigD['intervalInfGps'] = ZP.konfigD['intervalInfGps']
      if sprava_obj.aktBoxy != None:
        konfigD['aktBoxy'] = sprava_obj.aktBoxy
      else:
        konfigD['aktBoxy'] = ZP.konfigD['aktBoxy']
      if sprava_obj.tolerLow != None:
        konfigD['tolerLow'] = sprava_obj.tolerLow
      else:
        konfigD['tolerLow'] = ZP.konfigD['tolerLow']
      if sprava_obj.tolerHigh != None:
        konfigD['tolerHigh'] = sprava_obj.tolerHigh
      else:
        konfigD['tolerHigh'] = ZP.konfigD['tolerHigh']
      if sprava_obj.onOffAlarmPark != None:
        konfigD['onOffAlarmPark'] = sprava_obj.onOffAlarmPark
      else:
        konfigD['onOffAlarmPark'] = ZP.konfigD['onOffAlarmPark']

    return konfigD

  except:
    log.exception("EXCEPTION!")

def resetujOdpocetD(konfigD, freq): #set all values of active tasks to FREQ (6 seconds) so that they all run on the next Main Loop
  try:
    odpocetD = dict()
    for i in ZP.INTERVALOVE_PREMENNE:
      odpocetD[i] = freq if konfigD[i] != 123456789 else None
    return odpocetD
    
  except:
    log.exception("EXCEPTION!")

def zapisDefaultnyOdpocet():  #odpocet.json file
  try:
    #zapis defaultne hodnoty do odpocet.json
    odpocet = {'intervalMerTep': 0, 'intervalMerGps': 0, 'intervalInfTep': 0, 'intervalInfGps': 0}
    vseobecne.Pomoc.prepisJsonFile(odpocet, ZP.MAIN_DIR + 'odpocet.json')

  except:
    log.exception("EXCEPTION!")

def zapisDefaultnyKonfig(): #konfig.json file
  try:
    #zapis defaultne hodnoty do konfig.json
    konfigD_dummy = vseobecne.Pomoc.precitajJsonFile(ZP.MAIN_DIR + "konfig.json")
    # konfigD_dummy['cas'] = cas
    konfigD_dummy['intervalMerTep'] = ZP.MOZNEIntervalySprav[1]
    konfigD_dummy['intervalMerGps'] = ZP.MOZNEIntervalySprav[-1]
    konfigD_dummy['intervalInfTep'] = ZP.MOZNEIntervalySprav[2]
    konfigD_dummy['intervalInfGps'] = ZP.MOZNEIntervalySprav[-1] 
    vseobecne.Pomoc.prepisJsonFile(konfigD_dummy, ZP.MAIN_DIR + 'konfig.json')
  except:
    log.exception("EXCEPTION!")




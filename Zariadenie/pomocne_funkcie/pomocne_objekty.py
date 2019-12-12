#!/usr/bin/python3.7

#This module defines classes that create helping objects that store information shared between other modules.

import threading, random
from functools import *

import pomocne_funkcie.vseobecne_pomocne_funkcie as vseobecne
import ZDIELANE_PREMENNE as ZP
from ZDIELANE_PREMENNE import log, logVysledky



class TroubleMonitor:
  # stores the information about troubling situations that might appear during runtime
  # other modules check status of these troubles with this object and take co action if needed

  def __init__(self):
    
    self.noSignal = False
    self.noSimRegistration = False
    
    #main alarm due to actual sensor problems:
    self.mainAlarm_konfigD = {'intervalMerTep': ZP.MOZNEIntervalySprav[0], 'intervalInfTep': ZP.MOZNEIntervalySprav[1]}
    self.mainAlarm_modifyKonfigD = False  #this is set to true by turnOn alarm only once. Back to false by either user explicit request or
                                          #after actual modification of konfigD
    #server unreachable:
    self.serverUnreachable_tryAgain = True
    self.serverUnreachable_count = 0
    self.serverUnreachable_MAXcount = 1
    
    #already connected:
    self.alreadyConnect_tryAgain = True
    self.alreadyConnect_count = 0
    self.alreadyConnect_MAXcount = 3

    #ak adapter nereaguje na pwrKeyGSM signal, treba restartovat RPI
    #to, ze nereaguje, zistim tak ze neodpoveda na serialy velakrat po sebe
    #POZOR, moglo by to sposobovat nezelany restart ak vypadne signal po ceste a podobne.
    #reset a addcount sa spusti v hw.Adapter.otazkaOdpoveda + reset aj v pripravOdosielanie a pripravTelefonovanie ak vratia 0
    self.adapterNotRestarting_tryAgain = True
    self.adapterNotRestarting_count = 0
    self.adapterNotRestarting_MAXcount = 4 #trva to zhruba 15 sekund kym sa opakuje test ci odpoveda, takze po cca 5 minutach restartuj RPI 

  '''Monitor main alarm "onOffAlarmPark[0] - it is triggered ON only by meranie.py module. It is turned off only by the user.
  if this alarm is on, we modify (in MainTep.py) intervals of mesuring and informing'''
  def turnOn_mainAlarm(self):
    #prepare the modification of konfigD but only if alarm is freshly triggered!
    #this is so that function modifyKonfigDIfTroubles() can work properly on not get overwritten on every loop
    # if not self.isOn_mainAlarm():
    #   self.mainAlarm_modifyKonfigD = True
    with ZP.konfigD_lock:
      ZP.konfigD["onOffAlarmPark"] = vseobecne.Pomoc.modifyString(ZP.konfigD["onOffAlarmPark"],'1',0)
  def turnOff_mainAlarm(self):
    #only triggered by user:
    # self.mainAlarm_modifyKonfigD = False
    with ZP.konfigD_lock:
      ZP.konfigD["onOffAlarmPark"] = vseobecne.Pomoc.modifyString(ZP.konfigD["onOffAlarmPark"],'0',0)
  def isOn_mainAlarm(self):
    with ZP.konfigD_lock:
      if ZP.konfigD["onOffAlarmPark"][0] == '1':
        return True
      else:
        return False

  #already connect situation:
  def alreadyConnect_addCount(self):
    self.alreadyConnect_count += 1
    if (self.alreadyConnect_count > self.alreadyConnect_MAXcount):
      self.alreadyConnect_tryAgain = False
  def alreadyConnect_resetCount(self):
    self.alreadyConnect_count = 0
    self.alreadyConnect_tryAgain = True

  #serverUnreachable situation:
  def serverUnreachable_addCount(self):
    self.serverUnreachable_count += 1
    if (self.serverUnreachable_count > self.serverUnreachable_MAXcount):
      self.serverUnreachable_tryAgain = False
  def serverUnreachable_resetCount(self):
    self.serverUnreachable_count = 0
    self.serverUnreachable_tryAgain = True


  #adapterNotRestarting problem:
  def adapterNotRestarting_addCount(self):
    self.adapterNotRestarting_count += 1
    log.warning("Zvacsujem counter adapterNotRestarting. Stav: " + str(self.adapterNotRestarting_count) + "/" + str(self.adapterNotRestarting_MAXcount))
    if (self.adapterNotRestarting_count > self.adapterNotRestarting_MAXcount):
      self.adapterNotRestarting_tryAgain = False
  def adapterNotRestarting_resetCount(self):
    log.debug("Resetujem counter adapterNotRestarting.")
    self.adapterNotRestarting_count = 0
    self.adapterNotRestarting_tryAgain = True



class LogPerRun:
  # Logs data to log files (infoLog - csv format) on one-line-per-one-loop basis (Main Loop in Main.py)

  def __init__(self): #creates logger
    try:
      self.dictNameToValue = {}
      self.dictNameToPosition = {}
      self.hlavicka = []
      self.hodnoty = []
      self.run = True
    except:
      log.exception("EXCEPTION!")

  def addItem(self, itemName, itemValue, itemPosition, specialType = None):  #functions to assign specific item (data type) to be logged 
    try:
      #pozicia je len orientacne cislo ktore urcuje poradie ale nie presnu poziciu.
      #specialType je potrebny ak je treba: 
        #- dynamicky menit nazov (viac senzorov na jeden logPerRun.add())
        #- ak nie je zarucene, ze logPerRun.add() je volany na kazdy main Loop (kontroly)
      if (specialType == 'osilacie_a_zaseknutia'):
        #Item input: itemName = str(senz), itemValue = (oscilujeTeplota_l, zaseknutySenzor_l), startingPosition = 9, specialType = 'osilacie_a_zaseknutia'
        #zelany output: snz1_osci/zasek -> (12/98,65/88) od pozicie uvedenej a dalej
        itemName = itemName + '_osci/zasek'
        #pekny format dat:
        if itemValue != None: 
          maxoscilacie = str(max(itemValue[0])) + '/' + str(ZP.CAS_KNTRL_OSCIL) if itemValue[0] != [] else '-'
          maxzaseknutia = str(max(itemValue[1])) + '/' + str(ZP.CAS_KNTRL_ZASEK) if itemValue[1] != [] else '-'
          itemValue = str((maxoscilacie, maxzaseknutia))
        else:
          itemValue = "(-, -)" #to je len ak neboli na zaciatku spustene kontroly pre niektore senzory (troska matuce)
      
      if (specialType == 'filter'):
        itemName = itemName + "_filter: priemer, kvalita"
        if itemValue == None:
          itemValue = "-"
        else:
          itemValue = str(itemValue)

      #teploty a vlhkosti:
      elif (specialType == 'teplota_a_vlhkost'):
        itemName = itemName + '_tep/vlh'
        itemValue = str(itemValue)

      #vypln pomocne slovniky
      self.dictNameToValue[itemName] = itemValue
      self.dictNameToPosition[itemName] = itemPosition
    
    except:
      log.exception("EXCEPTION!")

  def __updateLists(self):
    try:

      menaNeusporiadane = list(self.dictNameToPosition.keys()) #list vsetkych velicin v logu - neusporiadny
      #usporiadaj podla pozicie (od najmensej po najvacsiu)
      self.hlavicka = sorted(menaNeusporiadane, key = lambda meno: self.dictNameToPosition[meno])
      #podla usporiadanej hlavicky vypln hodnoty
      self.hodnoty = [self.dictNameToValue[meno] for meno in self.hlavicka]

    except:
      log.exception("EXCEPTION!")

  def printHlavicku (self):
    try:

      if self.run == True:  #self.run zaruci, ze hlavicka sa tlaci iba raz
        self.__updateLists()
        formatHlavicky = ''
        for meno in self.hlavicka:
          formatHlavicky += '; '+meno
        ZP.logVysledky.info(formatHlavicky)
        self.run = False #never run this function again 
      else:
        return

    except:
      log.exception("EXCEPTION!")

  def print (self):
    try:
      self.__updateLists()
      formatHodnot = ''
      for hod in self.hodnoty:
        formatHodnot += '; ' + hod
      ZP.logVysledky.info(formatHodnot) #log to file using python logging module
    except:
      log.exception("EXCEPTION!")


class PrioDeque: 
  #provides custom defined queue with activities that are output based on their given priority 
  # + some activities can share priority value
  # + an option to delete the rest of the queue is available (usecase: newly assigned job covers the work of those deleted lower priority jobs)

  prioritaAPozicia = {'pwrKeyAdapter' : 0, 'restartujInternet': 1, 'telefonuj': 2, 'posta': 2, 'zapniInternet': 3, 'pripravOdosielanie': 4, 'pripravTelefonovanie': 5,\
 'pripojAdapter': 6, 'vypniInternet': 7}

  def __init__(self):
    self.velkost = len(set(PrioDeque.prioritaAPozicia.values()))  #vrati len pocet jedinecnych hodnot
    #*args su tuples(data,priority)
    self.deqList = []
    for i in range(self.velkost):
      self.deqList.append([])
    self.lock = threading.Lock()
    self.getEvent = threading.Event()


  def put(self, cinnost, delete = True):
    #mozna cinnost je v slovniku hore 
    with self.lock:
      bolPrazdny = True if reduce((lambda x,y: x+y), list(map(len,self.deqList))) == 0 else False
      
      pozicia = PrioDeque.prioritaAPozicia[cinnost]
      listTejtoCinnosti = self.deqList[pozicia]
      if cinnost not in listTejtoCinnosti:
        listTejtoCinnosti.append(cinnost)
        self.deqList[pozicia] = listTejtoCinnosti
      
      #delete == True makes all jobs with lower priority to be deleted from the queue
      #because the work of these lower priority jobs is mostly performed by the newly assigned job
      if delete == True:
        for i in range(pozicia + 1,len(self.deqList)):
          self.deqList[i] = []
      else: #keep the other jobs pending
        pass 

      if bolPrazdny:
        self.getEvent.set()

  def get(self):
    # get by mal nemal byt volany dvakrat za ten isty cas - lebo vsetky volania cakaju..
    self.getEvent.wait() #blokuj kym je  nejaky prvok v deque
    with self.lock:
      jePosledny = True if reduce((lambda x,y: x+y), list(map(len,self.deqList))) == 1 else False
      if jePosledny:
        self.getEvent.clear() #zadaj blokovanie ak vyberas posledny prvok
      #ak mas zadanych viac cinnosti pre jednu prioritu, vyber cinnost nahodne:
      for i in range(self.velkost):
        l = len(self.deqList[i])
        if l >= 2:
          return self.deqList[i].pop(random.choice(range(l))) #pick random activity if they share priority value
        elif l == 1:
          return self.deqList[i].pop(0)
        elif l == 0:
          continue
      
      raise Exception("PrioDequeEmpty")


class Filter: 
  """this provides pseudo statistical evaluation of the measured values of temperature and humidity 
  for the purpose of evaluating the situation in the trailer """
  """Briefly: 
  it takes a range of values (temperature and/or humidity) that were measured during some predefined time period.
  It provides information about the variation in these measurings. Meaning that, with predefined tolerance in variation,
  it groups together temperatures that are inside this tolerance around the group's average value. 
  There can be more such groups in case the temperature varies too much.
  The return value is the average value of the biggest group and the quality of the resulting estimate. 
  Quality of estimate is a ration between number of input measuring and number of members inside the resulting group.
  """

  #aplikuj len na vysledky z Ada senzorov, nie rpi/wittyPi !
  def __init__(self, listParovTepVlh, rozptylTep = ZP.rozptylTep, rozptylVlh = ZP.rozptylVlh):
  #vstup je stale o velkost VELKOST_OKNA_MERANI - to je zarucene funkciou specialne.vyberValidneMerania()
  #a je list len validnych merani, neobsahuje (None,None)
    try:
      self.rozptylTep = rozptylTep
      self.rozptylVlh = rozptylVlh
      
      if listParovTepVlh == None: #toto vratila funkcia specialne.vyberValidneMerania()
        self.vysledok = (None,None)
        self.zostavyT = None
        self.zostavyV = None
        self.repreZostavaT = None
        self.repreZostavaV = None
        #kvalita je zlomok (float) (0-1) vyjadrujuci ako velmi su data kvalitne (nefluktuuju), kvalitu znizuje ked vstup vzorka obsahuje: 1. None, 2. tep mimo kalib. rozsah, 3. velky sum
        self.kvalitaDatT = 0
        self.kvalitaDatV = 0

      else:
        #vytvor dva listy (su vylucene pripady (None, None) a tep/vlh mimo kalibr. rozsahu)
        #listParovTepVlh_redukovany uz obsahuje len validne data (12.3, 23)...
        teploty = list(x[0] for x in listParovTepVlh)
        vlhkosti = list(x[1] for x in listParovTepVlh)
        self.zostavyT = self.zoradDoZostavT(teploty)
        self.zostavyV = self.zoradDoZostavV(vlhkosti)
        self.repreZostavaT = self.vyberRepreZostavuT(self.zostavyT)
        self.repreZostavaV = self.vyberRepreZostavuV(self.zostavyV)
        self.vysledok = tuple([self.repreZostavaT[1], self.repreZostavaV[1]])
        #kvalita je zlomok (float) (0-1) vyjadrujuci ako velmi su data kvalitne (nefluktuuju), kvalitu znizuje ked vstup vzorka obsahuje: 1. None, 2. tep mimo kalib. rozsah, 3. velky sum
        self.kvalitaDatT = len(self.repreZostavaT[0]) / len(listParovTepVlh)
        self.kvalitaDatV = len(self.repreZostavaV[0]) / len(listParovTepVlh)

    except:
      log.exception("EXCEPTION!")

  def zoradDoZostavT(self, teploty):
    try:
      #input = [23.4,23.4,12.5,0.4,-200]
      if len(teploty) == 1:
        return [[teploty[0]],teploty[0]]
      else:
        #teraz ich chcem posortirovat do skupin podla velkosti teploty:
        skupiny = [[teploty[0]]]
        priemerySkupin = [teploty[0]]
        for ixtep in range(1,len(teploty)): #vezmi teplotu po teplote, okrem prvej lebo ta je uz tam
          for ixprm in range(len(priemerySkupin)):  #tento list sa postupne zvacsuje
            #ak je teplota v rozmedzi niektorej skupin tak ju k nej prirad
            if abs(teploty[ixtep]-priemerySkupin[ixprm])<self.rozptylTep:
              skupiny[ixprm].append(teploty[ixtep])
              break
            #ak nie je v rozmedzi tak vytvor novu skupinu s tymto clenom
            elif ixprm == len(priemerySkupin) - 1: #posledna iteracia tiez nepresla
              skupiny.append([teploty[ixtep]])
          priemerySkupin = Filter.priemerujListy(skupiny) #vytvor novy priemerovy list za kazdym priradenim teploty
        
      zostavy = list(zip(skupiny, Filter.priemerujListy(skupiny)))
      return zostavy #[[12.3,244,12],PRIEMER]]

    except:
      log.exception("EXCEPTION!")

  def zoradDoZostavV(self, vlhkosti):
    try:
      #input = [23.4,23.4,12.5,0.4]
      if len(vlhkosti) == 1:
        return [[vlhkosti[0]],vlhkosti[0]]
      else:
        #teraz ich chcem posortirovat do skupin podla velkosti teploty:
        skupiny = [[vlhkosti[0]]]
        priemerySkupin = [vlhkosti[0]]
        for ixtep in range(1,len(vlhkosti)): #okrem prvej lebo ta je uz tam
          for ixprm in range(len(priemerySkupin)):  #tento list sa postupne zvacsuje
            #ak je teplota v rozmedzi niektorej skupin tak ju k nej prirad
            if abs(abs(vlhkosti[ixtep])-abs(priemerySkupin[ixprm]))<self.rozptylVlh:  #rozmedzie: [priemer - rozptyl, priemer + rozptyl]
              skupiny[ixprm].append(vlhkosti[ixtep])
              break
            #ak nie je v rozmedzi tak vytvor novu skupinu s tymto clenom
            elif ixprm == len(priemerySkupin) - 1: #posledna iteracia tiez nepresla
              skupiny.append([vlhkosti[ixtep]])
          priemerySkupin = Filter.priemerujListy(skupiny) #vytvor novy priemerovy list za kazdym priradenim vlhkosti
      
      zostavy = list(zip(skupiny, Filter.priemerujListy(skupiny)))
      return zostavy #[[[12.3,244,12],PRIEMER],[[13,-23],PRIEMER]]

    except:
      log.exception("EXCEPTION!")

  def vyberRepreZostavuT(self, zostavy):
    try:
      #vstup: #[[[12.3,23,12],PRIEMER],[[13,-23],PRIEMER]]
      # vyber zostavu ktora ma najvacsie zastupenie clenov (= najvacsia pravdepodobnost, ze je spravna)
      repreZostava = zostavy[0] #predpokladajme, ze prave 1. clen je najvacsi
      for i in zostavy:
        if len(i[0]) >= len(repreZostava[0]):
          repreZostava = i
      return repreZostava

    except:
      log.exception("EXCEPTION!")

  def vyberRepreZostavuV(self, zostavy):
    try:
      repreZostava = zostavy[0]
      for i in zostavy:
        if len(i[0]) >= len(repreZostava[0]):
          repreZostava = i
      return repreZostava

    except:
      log.exception("EXCEPTION!")

  def priemerujListy(listListov):
    try:
      #vysledok je list priemerov ktoreho len je rovnaky ako len vstupu
      vstup = listListov
      vystup = []
      for l in listListov:
        if len(l) == 1:
          priemer = l[0]
        else:
          priemer = (reduce(lambda x,y: x+y, l))/len(l)
          priemer = round(priemer,1)

        vystup.append(priemer)
      assert len(vstup)==len(vystup)
      return vystup
    except:
      log.exception("EXCEPTION!")

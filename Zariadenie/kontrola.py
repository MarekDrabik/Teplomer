#!/usr/bin/python3.7

# This module contains function that controls proper functioning of sensor and healthy range of temperature/humidity inside each box.
# Each sensor has it's own thread that runs this function in parallel.

import pomocne_funkcie.specialne_pomocne_funkcie as specialne
import pomocne_funkcie.pomocne_objekty as pomocneObj
import pomocne_funkcie.vseobecne_pomocne_funkcie as vseobecne
import ZDIELANE_PREMENNE as ZP
from ZDIELANE_PREMENNE import log


def run(snz):
  '''postup (na to aby sme presli na dalsi bod musi byt splneny ten predosly): 
          1. pockaj kym sa teplota ustali (filter -> kvalita merani (1,1) (zavisla na sume)). To preto, ze nechceme hocijaky
          dychnutie vyhlasit za poplach. Takisto nechceme vyhlasit, ze vsetko je v poriadku ak nam teplota skace hore dole. 
          moze mat aj extremne hodnoty a my to zpriemerujeme a vyhlasime za ok? - radsej alarmuj
          2. teplota je ustalena, skontroluj ci je zdrava.
          3. nakoniec este over, ze senzor zasiela premenlive hodnoty <= nie je zaseknuty a je funkcny.
  '''
  try:
  #okno_merani = [(21,55),(54,65),(54,5),(54,65)], stale styri cleny (tep,vlh)
  #bezi neustale ale kontroluje len oficialne merania
  #kontroluju sa len standarnde senzory (nie vonkajsi,rpi,wittypi)
    oscilujeTeplota_l = []
    zaseknutySenzor_l = []
    index_snz = ZP.SENZORY.index(snz)

    while True:
      Debug = {0: snz, 1: "-", 2: '-', 3: '-', 4: '-', 5: '-', 6: '-', 7: '-' }
      #cakaj na signal od Mainu
      # event_kntrlTep.wait()
      # cakaj na ulohu
      filterVysledky = None
      ZP.Q[index_snz].get() #spusti len kontroly pre aktBoxy
      
      if ZP.resetujKontroly == True:
        oscilujeTeplota_l = []
        zaseknutySenzor_l = []
        filterVysledky = None
      else: #v pripade, ze prisla nova sprava => zrus vsetky prebiehajuce kontroly
        with ZP.zhromTep_lock:
          okno_merani_snz = list(ZP.zhromazdisko_tep[snz])[-ZP.VELKOST_OKNA_MERANI:]
          #okno_merani_snz = [(23.5,12),(12.5,55),(12.5,55),(12.5,55),(None,None)...] - velkos je = ZP.VELKOST_OKNA_MERANI
        validneMeraniaSenzora = specialne.vyberValidneMerania(snz)  #vrati osetrene od (None,None)
        f1 = pomocneObj.Filter(validneMeraniaSenzora)
        (tep,vlh) = f1.vysledok
        filterVysledky = (f1.vysledok, f1.kvalitaDatT, f1.kvalitaDatV)
        if ZP.kntrlEventy[index_snz].is_set(): #ak je tento snz aktivny tak prenho spusti kontrolu
          with ZP.kntrlTepOk_lock:
            ZP.Kntrl_tep_succesfully_finished[index_snz] = False  #set False pretoze prave ides overit ci je vsetko v poriadku (True)
          oscilujeTeplota_l.append(0)
        
        #ak sa teplota ustalila, vsetky merania presli kontrolou oscilacie a posli ich na overenie zdravosti teploty
        #staci jedno meranie (None, None) (=alebo meranie mimo rozsahu (chyba senzora) - takisto reprezentovane (None, None)) a kvalita merani nebude (1,1)
        #=> ak senzor neodpoveda/zasiela hodnoty mimo realistickeho rozsahu (None, None)) tak sa to nakoniec ohlasi ako chyba oscilujucich senzorov
        if f1.kvalitaDatT >= ZP.MINIMALNA_TOLEROVANA_KVALITA and f1.kvalitaDatV >= ZP.MINIMALNA_TOLEROVANA_KVALITA:
          if oscilujeTeplota_l != []:  #takze ak prave prebieha nejake (/viac) kontrol merani
            if specialne.checkIfHeatIndexIsHealthy((tep,vlh)) == False:
              Debug[1] = 'tA!'
              with ZP.nezdraveTep_senzory_lock:
                ZP.nezdraveTep_senzory = vseobecne.Pomoc.modifyString(ZP.nezdraveTep_senzory,'1',index_snz) #informacia pre android
              log.warning("prepisujem onOffAlarmPark na ALARM! nezdraveTep_senzory")
              ZP.troubleMonitor.turnOn_mainAlarm()
            else:
              #testujeme zaseknutie len ak sme presli kontrolov zdravosti teploty
              zaseknutySenzor_l.append(0) #takze do tohto listu sa pridava clen len ak ide o oficialne meranie

          Debug[2] = 'o[]'
          oscilujeTeplota_l = [] #uznaj kontroly oscilacie ak teplota neosciluje


        #uznaj kontrolu zaseknutia ale len v pripade, ze medzi porovnavanymi hodnotami sa neobjavuje (None,None) - nemusi ist nevyhnutie o zaseknutie ale tento zjednoduseny pripad je urcite dostatocne osetrenie problemu
        if zaseknutySenzor_l != []:
          #senzor nie je zaseknuty ak posledne dva namerane tuply (tep, vlh) nie su rovnake a neide o (None,None) - porovnavane hodnoty (t,v) su v raw formate = nezaokruhlene takze aj ked sa realne teplota/vlhkost nemeni tak senzor by mal posielat mierne rozne hodnoty
          #napriek tomu, ze senzor zasiela desatinne miesta, jeho mozne hodnoty sa opakuju (e.g. medzi 0.0 - 1.0 dokaze senzor zmerat len cca 4 rozne hodnoty <= nedostatocna citlivost)
          #if okno_merani_snz[-1] != okno_merani_snz[-2] and (okno_merani_snz[-1] != (None,None) and okno_merani_snz[-2] != (None,None)):
          zaseknutySenzor_l = [] #uznaj kontroly zaseknutia 
          Debug[3] = 'z[]'

      #ak su vsetky kontroly senzora v poriadku, zadaj True
      if oscilujeTeplota_l == [] and zaseknutySenzor_l == []:
        with ZP.kntrlTepOk_lock:
          ZP.Kntrl_tep_succesfully_finished[ZP.SENZORY.index(snz)] = True
          
      #pridaj casovy interval k obidvom listom
      if oscilujeTeplota_l != []:
        oscilujeTeplota_l = [x+ZP.FREQ for x in oscilujeTeplota_l]
      if zaseknutySenzor_l != []:
        zaseknutySenzor_l = [x+ZP.FREQ for x in zaseknutySenzor_l]

      if oscilujeTeplota_l != []:
        if max(oscilujeTeplota_l) == ZP.CAS_KNTRL_OSCIL:
          Debug[4] = 'oA!'  #toto oznamuje aj nefunkcny senzor (None,None)
          with ZP.oscilujuceTep_senzory_lock:
            ZP.oscilujuceTep_senzory = vseobecne.Pomoc.modifyString(ZP.oscilujuceTep_senzory,'1',index_snz)
          log.warning("prepisujem onOffAlarmPark na ALARM! osci_senzory")
          ZP.troubleMonitor.turnOn_mainAlarm()
          oscilujeTeplota_l.remove(ZP.CAS_KNTRL_OSCIL)
      if zaseknutySenzor_l != []:
        if max(zaseknutySenzor_l) == ZP.CAS_KNTRL_ZASEK:
          Debug[5] = 'zA!'
          with ZP.zaseknute_senzory_lock:
            ZP.zaseknute_senzory = vseobecne.Pomoc.modifyString(ZP.zaseknute_senzory,'1',index_snz) #informacia pre android
          log.warning("Senzor zasiela rovnake hodnoty (zaseknuty!). Zapinam alarm.")
          ZP.troubleMonitor.turnOn_mainAlarm()
          zaseknutySenzor_l.remove(ZP.CAS_KNTRL_ZASEK)

      Debug[6] = oscilujeTeplota_l
      Debug[7] = zaseknutySenzor_l
      ##vloz do logPerRun. Pozicia po tep/vlh
      with ZP.logPerRun_lock:
        #ked su kontroly zresetovane (prisla sprava), itemValue su prazdne listy a vsetky vypnute boxy budu mat prazdne listy v logPerRun odteraz
        ZP.logPerRun.addItem(itemName = str(snz), itemValue = (oscilujeTeplota_l, zaseknutySenzor_l), itemPosition = index_snz + 150, specialType = 'osilacie_a_zaseknutia')
        ZP.logPerRun.addItem(itemName = str(snz), itemValue = filterVysledky, itemPosition = index_snz + 170, specialType = 'filter')

      with ZP.debug_lock:
        ZP.DEBUG[snz] = Debug
      

      ZP.Q[index_snz].task_done()
  except:
    log.exception("EXCEPTION!")
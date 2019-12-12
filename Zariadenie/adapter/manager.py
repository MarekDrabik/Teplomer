#!/usr/bin/python3.7

"""This file is part of the 4 files under "adapter" folder. These 4 modules are managing operations of GSM communication module
that is physically connected to Raspberry Pi. Rpi communicates with this module through a serial port. This code is complicated due to the nature of the adapter
functionality. I am not providing detailed documentation on logic of this program here as it is very detailed and long."""

# This module is the manager module that gathers orders related to adapter work from other modules and distributes the work on the assistant and adapterWorker.

import threading, datetime
import pomocne_funkcie.specialne_pomocne_funkcie as specialne
import korespondencia
import ZDIELANE_PREMENNE as ZP
from ZDIELANE_PREMENNE import log
#adapter staff needed:
from adapter import assistant_to_manager as assistant
from adapter import serialReader as reader
from adapter import serialWorker as worker

def praca():
	
	#spusti serial reader v predstihu:
	threading.Thread(target = reader.read, name='serialRead', daemon = True).start()
	
	pocet_pokusov = 3

	while True:
		try:	
			q_get = ZP.adapterJob_prioDeq.get()

			log.info("pracujem na: '" + str(q_get) + "', zbytok Q:" + str(ZP.adapterJob_prioDeq.deqList))

			if q_get == 'pripojAdapter':
				worker.pripojAdapter()
				assistant.zarucOdpAPripojenie()

			elif q_get == 'restartujInternet':
				worker.restartujInternet()
			
			elif q_get == 'telefonuj':
				#ak sa nepodari ani pripravit telefonovanie tak ho urcite vloz naspat do queue
				if assistant.pripravTelefonovanie() == 0:
					#telefonuj:
					#a v pripade, ze sa nepodari tak vloz telefonovanie naspat do queue
					if worker.telefonuj() == 1:
						ZP.adapterJob_prioDeq.put('telefonuj')
				else:
					ZP.adapterJob_prioDeq.put('telefonuj')

			elif q_get == 'posta':
				ZP.AdapterNeodosielaSpravu = False
				assistant.pripravOdosielanie()
				prijataSprava = worker.prijmiSpravu()	#neosekana
				#if no new instructions were received, just reply with current KonfigD
				if prijataSprava == 1:
					log.error("Sprava neodoslana (server prestal reagovat alebo AlreadyConnect error). Restartujem internet !") 
					if (ZP.troubleMonitor.alreadyConnect_tryAgain): #try again if required.
						log.error("Novy pokus cislo" + str(ZP.troubleMonitor.alreadyConnect_count) + "/" + str(ZP.troubleMonitor.alreadyConnect_MAXcount))
						#restartuj internet kedze alreadyConnect sa len tak nevyriesi..
						ZP.adapterJob_prioDeq.put('restartujInternet', delete = False) #do not delete other jobs - keep them pending as we are just fixing something
						if specialne.MessageNotInAdapterQueue():
							ZP.adapterJob_prioDeq.put("posta")
					else:
						log.error("Pocet pokusov vyprsal. Pravdepodobne nie je server vobec dostupny. Nastavujem informovanie na minimalne 3 min.")
						#load the property, it will be used at the beginning of the next main run
						ZP.troubleMonitor.konfigD_modifiedProperties = ZP.troubleMonitor.alreadyConnect_konfigD
						ZP.troubleMonitor.alreadyConnect_tryAgain = True #(reset) opakuj pokusy pri dalsich korespondenciach

				elif prijataSprava == 2:
					log.error("Sprava neodoslana (server unreachable) !") 
					if (ZP.troubleMonitor.serverUnreachable_tryAgain): #try again if required.
						log.error("Novy pokus cislo" + str(ZP.troubleMonitor.serverUnreachable_count) + "/" + str(ZP.troubleMonitor.serverUnreachable_MAXcount))
						if specialne.MessageNotInAdapterQueue():
							ZP.adapterJob_prioDeq.put("posta")
					else:
						log.error("Pocet pokusov vyprsal, vzdavam to!")
						ZP.troubleMonitor.serverUnreachable_tryAgain = True #opakuj pokusy pri dalsich korespondenciach

				elif prijataSprava == None:
					log.critical("Socket vratil prijatu spravu NONE, skontroluj co to je za problem.")
				else:
					if len(prijataSprava) < 6: #no new instructions is something like this b'\x00\x00\r\n' 
						log.debug("Neprisla sprava.")
						prijataSprava = None #neviem uz preco...
						odpoved = korespondencia.sformulujOdpoved(ZP.konfigD)
						#if new instructions were received, reply with updated konfigD(dummy for this moment) first.
					else:
						log.debug("Prijata sprava zpracovana: " + str(prijataSprava))
						prijataSprava_obj = korespondencia.Rozbal(prijataSprava)
						#ak prisla sprava, zapis konfigy do txt a z toho txt nacitaj premenne. Nenacitavaj premenne znova v kazdom While loope ale len ak prisla sprava.
						#nacitaj ZP.konfigD a odpocetD (ak neprisla sprava tak nastavenia su 1.defaultne alebo 2.relax mod)
						print ("ZP.konfigD PRED:", ZP.konfigD)
						konfigD_dummy = specialne.aktualizujKonfigDSpravou(prijataSprava_obj)
						print ("konfigD_dummy", konfigD_dummy)
						print ("ZP.konfigD PO:", ZP.konfigD)
						with ZP.prijataSprava_dequelock:
							ZP.prijataSprava_deque.append((prijataSprava_obj, konfigD_dummy))
						#loguj data z prijatej spravy
						log.info("Prijata sprava!: "+ " " + str(prijataSprava_obj.intervalMerTep) + " " + str(prijataSprava_obj.intervalMerGps) + " " + str(prijataSprava_obj.intervalInfTep)  \
							+ " " + str(prijataSprava_obj.intervalInfGps) + " " + str(prijataSprava_obj.tolerLow) + " " + str(prijataSprava_obj.tolerHigh) + " " + str(prijataSprava_obj.onOffAlarmPark) + " " + str(prijataSprava_obj.aktBoxy))
														
						odpoved = korespondencia.sformulujOdpoved(konfigD_dummy)
					if worker.posliSpravu(odpoved) == 1:
						log.critical('Nepodarilo sa odoslat spravu. Necakana chyba!')
					else:
						pass #odosle spravu


				ZP.AdapterNeodosielaSpravu = True
						

			elif q_get == 'pripravOdosielanie':
				assistant.pripravOdosielanie()

			elif q_get == 'pripravTelefonovanie':
				assistant.pripravTelefonovanie()

			elif q_get == 'vypniInternet':
				#nie je treba sa ani pytat, proste to skus
				worker.vypniInternet()
			
			elif q_get == 'pwrKeyAdapter':
				worker.pwrKeyAdapter()
				worker.pripojAdapter()


		except:
			pocet_pokusov -= 1 	
			if pocet_pokusov == 0:
				log.exception("AdapterManager zlyhal vela krat, restartujem ho!")
				ZP.adapterJob_prioDeq.put('pwrKeyAdapter', delete = False) #keep other jobs pending as we are just fixing something
				pocet_pokusov = 3
			else:
				log.exception("Adapter zlyhal, restartujem po dalsich " + str(pocet_pokusov) + " zlyhaniach.")



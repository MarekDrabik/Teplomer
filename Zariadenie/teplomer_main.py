#!/usr/bin/python3.7
#author: Marek Drabik, marek.drabik@protonmail.com

#About this file: Main code, core logic for the whole program.


import time, sys, os, random, threading, queue
from datetime import datetime, timedelta
import pomocne_funkcie.vseobecne_pomocne_funkcie as vseobecne
import pomocne_funkcie.specialne_pomocne_funkcie as specialne
import pomocne_funkcie.pomocne_objekty as pomocneObj
import pomocne_funkcie.systemove_funkcie as sysfun
import meranie
import kontrola
import korespondencia
import ZDIELANE_PREMENNE as ZP
from ZDIELANE_PREMENNE import log, logVysledky
#adapter staff needed:
from adapter import manager as adapterManager
from adapter import serialWorker as adapterWorker


ZP.adapterJob_prioDeq = pomocneObj.PrioDeque()

def main():
	try:

		log.debug("RPI STARTED!")
		loop_count = 0		#just informative
		pociatokSpanku = 0 #used for calculating sleeping periode
		cas_celkoveho_behu = 0 #time of the whole run counter
	
	
		'''load main konfiguration dictionary ZP.konfigD for the current run
			konfig.json file contains:
			- settings written at the end of previous run (<= we are in relaxing mode)
			- default settings due to user explicit request to shut down the machine. 
			Or if crash of this program happens during running process - this is why we keep
			konfig.json on default values during running of this program. See overwriting of this file few lines bellow...
		'''
		ZP.konfigD = vseobecne.Pomoc.precitajJsonFile(ZP.MAIN_DIR + "konfig.json")
		#load main counter dictionary odpocetD that keeps current value of counter for each interval (if counter is == 0, activity is run). Counter is decresead be ZP.FREQ value after each main loop
		odpocetD = vseobecne.Pomoc.precitajJsonFile(ZP.MAIN_DIR + "odpocet.json")
		#rewrite odpocet.json to default value just in case program crashes - it will restart with default values.
		specialne.zapisDefaultnyOdpocet()

		'''since we just started the program. Add some pre-load time to every interval-counter value. This makes sure we run mesuring of temperature or gps beforehand
		so that we have some values to work when counter == 0. This is because the sensors' controls are starting at counter == 0 and they need some current temperatures mesurements to work with.
		It also secures the cases when gps/temp mesuring is not started at the same time'''
		for prem in ZP.INTERVALOVE_PREMENNE:	#for synchronisation purpose we are assigning ZP.LOADING_CAS to each of 4 interval-counters
			if odpocetD[prem] != None:	#interval-counter == None means this activity is to be ignored (requested by user)
				odpocetD[prem] = odpocetD[prem] + ZP.LOADING_CAS

		#rewrite konfig.json to default value in case program crashes. It will then restart with default configuration.
		specialne.zapisDefaultnyKonfig()	
		


		"""Create troubleMonitor object to monitor all troubles in one place and manage runLevels through it."""
		ZP.troubleMonitor = pomocneObj.TroubleMonitor()
		"""Create logger for one run per line logging."""
		ZP.logPerRun = pomocneObj.LogPerRun() #prefill with these specific names or dummy (None) value. Otherwise they would be ignored <- see 'run' variable in pomocneObj.LogPerRun 
		for i in range(ZP.POCET_SENZOROV): 
			with ZP.logPerRun_lock: 
				ZP.logPerRun.addItem(itemName = str(ZP.SENZORY[i]), itemValue = None, itemPosition = i + 150, specialType = 'osilacie_a_zaseknutia') #to have the header of all controls in the log even if some won't run
				ZP.logPerRun.addItem(itemName = "((ZP.rozptylTep, ZP.rozptylVlh), ZP.VELKOST_OKNA_MERANI, ZP.MINIMALNA_TOLEROVANA_KVALITA)", itemValue = str(((ZP.rozptylTep, ZP.rozptylVlh), ZP.VELKOST_OKNA_MERANI, ZP.MINIMALNA_TOLEROVANA_KVALITA)), itemPosition = 250, specialType = None) #just one log of current constants setup: ZP.rozptylTep, ZP.rozptylVlh
				ZP.logPerRun.addItem(itemName = str(ZP.SENZORY[i]), itemValue = None, itemPosition = i + 170, specialType = 'filter') #to have the header of all controls in the log even if some won't run

		#THREADS:
		'''create and start thread (running in the background) that manages GPRS adapter work over serial port
			It is necessary that there is only one access to serial port at a time because of the serial port nature. Therefore we can assign any work for the adapter
			through the following thread (specifically through it's custom made queue defined here: pomocneObj.PrioDeque). This queue has defined priorities and special order of specific activities.
			AdapterManager is working on them based on this given order. 
		'''
		adapterManager_thread = threading.Thread(target = adapterManager.praca, name = 'AdapterManager', daemon = True)
		adapterManager_thread.start()

		#adapter is booted together with RPI (unconvenient GPIOs setup at boot that is difficult to modify) but it doesnt work well so it's better to restart it.
		#so shut it down:
		sysfun.pin_to_HighState()	#first put it to high state (necessary, otherwise adapter doesn't work properly)
		ZP.adapterJob_prioDeq.put('pwrKeyAdapter', delete = False) #first shutdown/startup is necessary in all cases
		#pripojAdapter work is already included in pwrKeyAdapter work
		#adapter jobs are running in the background so just give adapter some time to restart
		log.debug("Giving adapter some time to start/shutdown before proceeding...")
		time.sleep(12)
		if not adapterWorker.otazkaOdpoveda():	#at this time we are checking if adapter was started or shut down. in latter case, turn it back on
			log.debug("Adapter je zrejme vypnuty. Startujem...")
			#it's now turned OFF so start it again:
			ZP.adapterJob_prioDeq.put('pwrKeyAdapter', delete = False)
			# time.sleep(4) - we cannot put sleep here because it would change starting time if there was problem with adapter
		else:
			time.sleep(1.9)	#if it's replying, hw.Adapter.otazkaOdpoveda will return faster than if it's not. so wait for about otazkaOdpoveda timeout time

		#start AlarmCheck thread that is assigning 'telefonuj' work to AdapterManager in case alarm is on
		alarmCheckThread = threading.Thread(target = specialne.initiatePhoneCallOnAlarm, name='AlarmCheck', daemon = True)
		alarmCheckThread.start()

		#for each of the sensors, create one sensor-check thread that is checking it's proper functionality and heat index healthy range:
		for snz in ZP.SENZORY[:6]:
			meno = 'kontrolaThread' + snz 
			kntrl = threading.Thread(target = kontrola.run, args = (snz, ), name = meno, daemon = True)
			kntrl.start()
		sysfun.clearStartupTime()	


		###	MAIN LOOP:
		#this is the core code. It runs every ZP.FREQ seconds (6 seconds) from the start of RPI until shutdown is called.
		while True:
			log.info("BEH CISLO: " + str(loop_count))
			start_cas = time.time()

			#1. #############################
			#  		MESSAGE RECEIVED?					#
			#																#
			#check if new message was received, if so, load requested configuration:
			with ZP.prijataSprava_dequelock:
				if len(ZP.prijataSprava_deque) == 1: #this is only == 1 if adapterManager filled it prijataSprava_deque with a newly received message
					log.debug("Nacitavam novy konfigD (lebo prisla sprava).")
					with ZP.konfigD_lock:
						(prijataSprava, ZP.konfigD) = ZP.prijataSprava_deque.pop() #left side of this assignment is what this deque normally contains
					#reset interval-counters for simplicity. Mainly to keep intervals synchronized in case one of them is to be modified by the message.
					log.debug("Resetujem odpocetD (lebo prisla sprava).")
					odpocetD = specialne.resetujOdpocetD(ZP.konfigD, ZP.FREQ)
					
					'''reset all sensor-checks mainly to avoid controling some old state that the user is no longer interested in.
					(Run them with empty lists and set all semaphores True):
					'''
					log.debug("Resetujem kontroly (lebo prisla sprava).")
					ZP.resetujKontroly = True
					for q in ZP.Q:
						q.put(1)
						q.join()
					#all sensor-checks were just run "unloaded".
					ZP.resetujKontroly = False
					'''Negate information about sensors' issues because the user just requested to turn off the alarm:
					In case there are still problems with sensors, they will be rediscovered on freshly started sensor-checks which are triggered by just received message.'''
					if not ZP.troubleMonitor.isOn_mainAlarm(): #reset the information about troubles to all ok
						ZP.nezdraveTep_senzory = "00000000"
						ZP.oscilujuceTep_senzory = "00000000"
						ZP.zaseknute_senzory = "00000000"
			################################


			#2. ###########################
			# 				TROUBLES?						#
			#															#
			#Check if you there are some troubles and if necessary, modify the running intervals.
			#1. main alarm is ON => configD will be modified to default intervals no matter what user has requested. 
			if (ZP.troubleMonitor.isOn_mainAlarm()):
				log.debug("Alarm je zapnuty, prepisujem konfiguraciu (konfiD) na neustaly rezim.")
				with ZP.konfigD_lock:
					for i in ZP.troubleMonitor.mainAlarm_konfigD:
						ZP.konfigD[i] = ZP.troubleMonitor.mainAlarm_konfigD[i] #modify running intervals to restless mode
					for i in ZP.troubleMonitor.mainAlarm_konfigD:
						#reset odpocetD in case it is not aware of new configuration. This condition is true at most one time after alarm was started
						#further times, this condition will always be false because interval-counters will never get bigger than konfigD corresponding values
						if odpocetD[i] == None or odpocetD[i] > ZP.konfigD[i]:
							odpocetD = specialne.resetujOdpocetD(ZP.konfigD, 0)
			###############################
			
			
			#3. ###########################
			# 				INFORMING						#
			#															#
			#when the time comes, perform informing ( = receive instructions if any AND send current configuration and results). This work is assigned to AdapterManager.
			if odpocetD["intervalInfTep"] == 0 or odpocetD["intervalInfGps"] == 0:
				ZP.adapterJob_prioDeq.put('posta')
			################################



			###############################
			#			some side tasks		 			#
			#															#
			#ZP.adapterJob_prioDeq.put('pripravTelefonovanie') #no longer necessary
			
			#make adapter ready in advance for communication with the server (ZP.PREDPRIPRAVA_ODOSIELANIA seconds ahead)
			#(this code isn't crucial for proper functionality, it's only convenient to prepare the adapter beforehand):
			specialne.zapniInternetVopred(odpocetD['intervalInfTep'], odpocetD['intervalInfGps'])

			#inicializations for logging:
			ZP.DEBUG = {'snz1': {}, 'snz2': {}, 'snz3': {}, 'snz4': {}, 'snz5': {}, 'snz6': {}, 'snz7': {}, 'snz8': {} }
			ZP.filterVysledkyD = {'snz1': (), 'snz2': (), 'snz3': (), 'snz4': (), 'snz5': (), \
			'snz6': (), 'vonkajsi':  (('-','-'), '-', '-'), 'rpi':  (('-','-'), '-', '-'), 'wittyPi':  (('-','-'), '-', '-')}
			#logging "per line" of current sensors with issues:
			ZP.logPerRun.addItem('nezdraveTep_senzory', ZP.nezdraveTep_senzory, 200)
			ZP.logPerRun.addItem('oscilujuceTep_senzory', ZP.oscilujuceTep_senzory, 201)
			ZP.logPerRun.addItem('zaseknute_senzory', ZP.zaseknute_senzory, 202)
			#logging of current konfigD and odpocetD:
			log.info("		{}	{}	{}	{}	{}	{}	{}		{}".format('mT','mG','iT','iG', 'tLow', 'tHigh', 'onOff', 'aktBoxy'))
			znenie = ''
			for i in ZP.VOLBY_ANDROID:
				hodnota = str(ZP.konfigD[i])
				if hodnota == "123456789":
					znenie += '\t' + "off"
				else:
					znenie += '\t' + str(ZP.konfigD[i])
			log.info ("konfigD: " + znenie)
			znenie = ''
			for i in ZP.INTERVALOVE_PREMENNE:
				znenie += '\t' + str(odpocetD[i])
			log.info("odpocetD: " + znenie)
			##############################


			#4. #########################
			#					MESURING					#
			#Run temperature mesuring ahead of time (ZP.LOADING_CAS) if measuring is required or if sensor-checks didn't yet confirm all checks ok
			onSenzory = ZP.SENZORY[:9]	#just FYI that we are mesuring all sensors every time.
			if odpocetD['intervalMerTep'] != None: #since GPS mesuring is not yet available, this is always True
				if (odpocetD['intervalMerTep'] <= ZP.LOADING_CAS or not all(ZP.Kntrl_tep_succesfully_finished)): #meraj uz v predstihu resp. pri kontrole
					tepMer_thread = threading.Thread(target = meranie.TemperatureHumidity.ofSensors, name = "MerajTep", args = (onSenzory, ), daemon = False)
					tepMer_thread.start()

			#IGNORED. GPS feature is not fully implemented yet
			meranieGpsJePozadovane = False
			# meranieGpsJePozadovane = True if odpocetD['intervalMerGps'] != None else False
			if meranieGpsJePozadovane:
				if odpocetD['intervalMerGps'] <= ZP.LOADING_CAS or not ZP.Kntrl_gps_OK: #meraj uz v predstihu resp. pri kontrole
					if False:
						startGps_thread = threading.Thread(target = mka.Gps.startuj_GPS, name = "StartGps")
						gpsMer_thread = threading.Thread(target = mka.Gps.meraj_GPS, name = "MerajGps")
						#spustanie gps pocas behu:
						if event_gpsNastartovane.is_set():
							gpsMer_thread.start()
						else:
							startGps_thread.start()
							print("startGPS started")
				#should be moved few lines bellow
				if 'MerajGps' in active_threads:
	 				gpsMer_thread.join()
			
			#Temperature mesuring. Lasts maximum 5.1 seconds. In case it's not yet finished, wait for it to finish.
			active_threads = [x.name for x in threading.enumerate()]
			if 'MerajTep' in active_threads:
				tepMer_thread.join()
				casMerania = time.time() - ZP.merTepCas_debug
				if casMerania > 5.9:
					log.warning("Meranie teploty prebehlo nezvycajne pomaly, trvalo:" + str(casMerania))
				ZP.merTepCas_debug = 0
			#############################



			#5. #########################
			#			SENSORS-CHECKS				#
			#														#
			#first clear all checks' events to not check sensors that are not active (empty cages). 
			for e in ZP.kntrlEventy:
				e.clear()
			#started exactly on mesuring intervals counter == 0 (odpocetD[intervalMerTep])
			if odpocetD['intervalMerTep'] == 0:
				#INITIATE CHECKS - only for non-empty cages (konfigD[aktBoxy])
				for ix in range(ZP.POCET_SENZOROV):
					if ZP.konfigD['aktBoxy'][ix] == '1':
						ZP.kntrlEventy[ix].set()
					else:
						#this is just for logging:
						ZP.filterVysledkyD[ZP.SENZORY[ix]] = (('-','-'), '-', '-')	
			#CONTINUE with running checks until they all confirm their check value True
			if odpocetD['intervalMerTep'] == 0 or not all(ZP.Kntrl_tep_succesfully_finished):
				for ix in range(ZP.POCET_SENZOROV):
					if ZP.konfigD['aktBoxy'][ix] == '1':
						ZP.Q[ix].put(1)
			for q in ZP.Q:
				q.join()

			
			#6. ###################################
			#			WRITE-OFF INTERVAL-COUNTERS			#
			#																			#
			#work has been performed, write-off the counter for each activity
			#work to be performed on the next run will have it's counter == 0
			for inter in ZP.INTERVALOVE_PREMENNE:
				if odpocetD[inter] != None:
					if odpocetD[inter] == 0:
						odpocetD[inter] = ZP.konfigD[inter] - ZP.FREQ
					else:
						odpocetD[inter] -= ZP.FREQ
				if ZP.konfigD[inter] == 123456789:
					odpocetD[inter] = None
			#######################################


			###############################
			#			some side tasks		 			#
			#															#
			log.debug("Tabulka kontrol:")
			i = 0
			for senz in ZP.SENZORY[:6]:
				znenie = ''
				for k in ZP.DEBUG[senz]:
					znenie += str(ZP.DEBUG[senz][k]) + "\t"
				log.debug(znenie)
				
			# log.debug("kontorly:" + str(ZP.Kntrl_tep_succesfully_finished))
			log.debug("adapterManagerQ:" + str(ZP.adapterJob_prioDeq.deqList))
			ZP.logPerRun.printHlavicku()
			ZP.logPerRun.print()
			###############################


			#7. ###################################
			#			SHUTDOWN / SLEEP / CONTINUE			#
			#																			#
			#check if there is a need to shutdown RPI (sleep or shutdown forever)
			#1. specialny pripad - restaruj RPI ak adapter neodpoveda na restarty:
			if (ZP.troubleMonitor.adapterNotRestarting_tryAgain == False):
				vseobecne.Pomoc.prepisJsonFile(ZP.konfigD, ZP.MAIN_DIR + "konfig.json")
				#resetuj odpocet.json na nuly aby sa vsetko spustilo pri zapnuti RPI
				for i in ZP.INTERVALOVE_PREMENNE:
					odpocetD[i] = 0 if odpocetD[i] != None else None
				vseobecne.Pomoc.prepisJsonFile(odpocetD,"odpocet.json")
				log.warning("Restartujem RPI kvoli problemu s restartovanim adaptera!")
				sysfun.uspiRpi(ZP.TRVANIE_RESTARTU, datetime.now()) # THIS LINE ENDS THE!

			#if above didn't end the program, then we continue here:
			#check if there are any intervals in ZP.konfigD different than None
			nieNoneOdpocty = [x for x in odpocetD.values() if x != None]
			#if all intervals in ZP.konfigD == None (nieNoneOdpocty is []) 
			if nieNoneOdpocty == []: #then it's signal to shutdown RPI forever:
				oddych = None #this value is used at the bottom (outside of Main loop)
				specialne.zapisDefaultnyOdpocet()	#for fresh RPI start
				specialne.zapisDefaultnyKonfig()	#for fresh RPI start
				log.info("Dostal som instrukcie na vypnutie RPI.")
				break	#breaks the main loop, jumps at the bottom to shut down RPI
			else:	#else, check if there is a need to sleep
				pozadovany_oddych = min(nieNoneOdpocty)	#the minimum interval-counter is the maximum possible "sleep" time of RPI
				cas_do_konca_behu = ZP.FREQ - (time.time() - start_cas)
				korekcia = 0 #correction to make the sleep time fit perfectly. 0 means no correction needed
				#oddych sa vyratava zlozitejsou formulkou ale plati, ze cas do konca behu nie je podstatny pretoze sa prekryva s SOME_TIME_TO_FINISH_ADA.JOBS
				#sysfun.uspiRpi() rata spanok od "pociatokSpanku" po dobu "oddych"
				oddych = round(pozadovany_oddych + cas_do_konca_behu - ZP.RPI_BOOTUP_CAS - ZP.LOADING_CAS + korekcia) 
				log.debug("Vyratany oddych (min Odpocet):" + str(pozadovany_oddych) + ", Skutocny mozny oddych:" + str(oddych))
				
				#now check that new message wasn't received around this moment
				#we dont' want to ignore that new message so don't proceed with shutdown if received
				if len(ZP.prijataSprava_deque) == 0:
				#also check other stuff before shutting down:
					if (oddych > ZP.MIN_ODDYCH and not ZP.troubleMonitor.isOn_mainAlarm() and all(ZP.Kntrl_tep_succesfully_finished) and ZP.AdapterNeodosielaSpravu and specialne.MessageNotInAdapterQueue()):
						log.info("Uspavam RPI.")
						log.debug("Uspavam RPI pretoze 1. oddych > 90 sekund, 2.nie je zapnuty alarm, 3. nebezi ziadna kontrola, 4. AdapterNeodosielaSpravu a 5. sprava nie je v adapterQueue: ")
						#store current configuration in a file for it to be used for next run
						vseobecne.Pomoc.prepisJsonFile(ZP.konfigD, ZP.MAIN_DIR + "konfig.json")
						#since we are putting RPI to sleep, we need to write-off interval-counters by the lenght of the sleep so that they are ready for the new run
						for i in ZP.INTERVALOVE_PREMENNE:
							odpocetD[i] = odpocetD[i] - pozadovany_oddych if odpocetD[i] != None else None
						vseobecne.Pomoc.prepisJsonFile(odpocetD,"odpocet.json")
						pociatokSpanku = datetime.now()
						break	#breaks the main loop, jumps at the bottom to shut down RPI
			#######################################
			

			#8. ###################################
			#			CONTINUE WITH THE MAIN LOOP			#
			#																			#
			loop_count += 1
			#assure the run is no shorter than 6 seconds, then repeat the Main loop:
			end_cas = time.time()
			cas_behu = end_cas - start_cas
			if cas_behu < ZP.FREQ:
				cakaj = ZP.FREQ - cas_behu
			else:
				cakaj = 0
				log.warning("Beh prebehol prilis pomaly, trval" + str(cas_behu) + "sekund!")
			cas_celkoveho_behu += (cas_behu + cakaj)
			log.info("Cas celkoveho behu: " + str(cas_celkoveho_behu) + " sekund.")
			log.info("")
			time.sleep(cakaj)
			#######################################


		###################################
		#		 WE ARE SHUTTING DOWN 				#
		#																	#
		"""We will get here only if "all runs" of Main loop were succesfully finished (RPI wasn't physically shut down):"""
		#there is no more "posta" jobs in adapter queue so we can shut down the adapter:
		ZP.adapterJob_prioDeq.put('pwrKeyAdapter', delete = False) #shut down adapter functionality gracefully
		"""adapter might have some jobs to do and we are already shuting the device down - but there are only 2 crucial jobs that might be of concern:
		1. phone calling in alarm situation - this wont happen because we wouldnt ask for Rpi shutdown in case of alarm
		2. message sending - if we got to this line it means that either there is no need for informing in this DAY or ... 
		 in any case we give adapter SOME_TIME_TO_FINISH_ADAPTER_JOBS anyway."""
		log.info("Giving adapterManager some time to finish assigned jobs: " + str(ZP.SOME_TIME_TO_FINISH_ADAPTER_JOBS) + " seconds")
		time.sleep(ZP.SOME_TIME_TO_FINISH_ADAPTER_JOBS)
		sysfun.uspiRpi(oddych, pociatokSpanku)	#program is shut down by this function
		###################################

	except:
		log.exception("EXCEPTION!")
		sys.exit()

	

if __name__ == '__main__':
	main()

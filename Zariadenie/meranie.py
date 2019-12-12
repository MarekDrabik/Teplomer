#!/usr/bin/python3.7

# This module provides measuring functionality of temperature and humidity on all sensors, raspberryPI and wittyPi

import threading, time, re
import Adafruit_DHT as ada

import pomocne_funkcie.systemove_funkcie as sysfun
import ZDIELANE_PREMENNE as ZP
from ZDIELANE_PREMENNE import log


class TemperatureHumidity:
	
	def ofSensors(senzoryNaMeranie):
		try:
			ZP.merTepCas_debug = time.time()	#debug (trvanie merania teploty)

			rpi_tepMer_thread = threading.Thread(target = TemperatureHumidity.ofRpi, name = 'rpi_tepMer')
			#inicializuj zhromazdisko, lock by snad ani nebol nutny kedze toto bezi len raz
			#vytvor prazdne zhromazdisko
			#ZP.zhromazdisko_tep = {'wittyPi': deque([(21.2, None), (21.2, None), (21.5, None), (21.5, None)], maxlen=4), atd....}
		
			vysledkyTohtoBehu = []
			start = time.time()
			
			if ('rpi' in senzoryNaMeranie):
				rpi_tepMer_thread.start()
			if ('wittyPi' in senzoryNaMeranie):
				#meraj len raz za cas
				tepWitty = sysfun.utilities()
				reSearch = re.search (r'(.*)\.', tepWitty[0][:4])
				if reSearch:
					teplota = float(reSearch.group(1))
				else:
					teplota = None
				vlhkost = None
				vysledkyTohtoBehu.append(('wittyPi', (teplota,vlhkost)))	# humidity not available for wittyPi
				with ZP.logPerRun_lock:
					ZP.logPerRun.addItem(itemName = 'wittyPi', itemValue = (teplota,vlhkost), itemPosition = 115, specialType = 'teplota_a_vlhkost')
			
			senz_index = 0
			for senz in senzoryNaMeranie:
				if senz == 'rpi' or senz == 'wittyPi': #preskoc tieto dva
					continue
				pin = ZP.SENZ_TO_PIN[senz]
				vlhkost, teplota = ada.read(22, pin)
				vysledkyTohtoBehu.append((senz, (teplota,vlhkost)))
				with ZP.logPerRun_lock:
					##pozicie 100-105
					ZP.logPerRun.addItem(itemName = senz, itemValue = (teplota,vlhkost), itemPosition = senz_index + 100, specialType = 'teplota_a_vlhkost')
				senz_index += 1

			with ZP.zhromTep_lock:
				#update vysledky do ZP.zhromazdisko_tep, chybne hodnoty senzora (123123.232, 123000.0) su zapisane ako (None, None) a preto sa taketo hodnoty nedostanu ani na kontrolu a cez funkciu pomocneObj.Filter.
				for i in vysledkyTohtoBehu:	#obshaje aj wittyPi raz za cas
				#vysledkyTohtoBehu = [(senz, (teplota,vlhkost), (senz, (teplota,vlhkost))...)]
					(t,v) = (i[1][0], i[1][1])	#t,v su v raw formate = nezaokruhlene
					#nasledujucim testom prejdu hodnoty t=None alebo 21.23 ale nie t mimo rozsahu ZP.TEPLOTY, v=None/23.123 ale nie v mimo rozsahu ZP.VLHKOSTI
					if (t == None or int(t) in ZP.TEPLOTY) and (v == None or int(v) in ZP.VLHKOSTI):	#int() pretoze napr. hodnota 24.2 je ok ale nie je v TEPLOTY, tak to zaokruhli na 24
						ZP.zhromazdisko_tep[i[0]].append(i[1]) #t,v su v raw formate = nezaokruhlene
					else:
					#ostatne hodnoty (vratane chybnych senzorovych hodnot mimo rozsahu) sa prezentuju ako (None,None)
						ZP.zhromazdisko_tep[i[0]].append((None, None))
						log.warning("Chybne meranie teploty/vlhkosti senzora: " + str(i[0]) + ". Hodnota " + str((t,v)) + " nie je realna! Povazujem za (None,None)")

			if senz == 'rpi':
				rpi_tepMer_thread.join()
			#v tomto bode obsahuje zhromazdisko aktualne vysledky zaziadanych senzorov (vsetky senzory) 
			#Info zasiela vsetky vysledky, nielen aktBoxy

		except:
			log.exception("EXCEPTION!")

	def ofRpi():	#no humidity available for Rpi
		try:
			#spusta sa len raz za cas spolu s WittyPi
			tepRPI = sysfun.getRpiTemperature()
			reSearch = re.search(r'(.*)\'', tepRPI[0][5:])
			if reSearch:
				teplota = int(float(reSearch.group(1)))	#int ak by nahodou nebola ciarka
			else:	#ak sa nejaka somarina precita
				teplota = None
			vlhkost = None
			if teplota != None:
				if int(teplota) not in ZP.TEPLOTY:
					log.warning("Chybne meranie teploty RPI! Hodnota " + str(teplota) + " nie je realna! Povazujem za None")
					teplota = None

			with ZP.zhromTep_lock:
				ZP.zhromazdisko_tep['rpi'].append((teplota,vlhkost))
			with ZP.logPerRun_lock:
				ZP.logPerRun.addItem(itemName = 'rpi', itemValue = (teplota,vlhkost), itemPosition = 110, specialType = 'teplota_a_vlhkost')

		except:
			log.exception("EXCEPTION!")




## GPS nie je implementovane, toto je len koncept:
class Gps:
	
	def gps():
		try:
			Meraj.startuj_GPS()
			Meraj.meraj_GPS()

		except:
			log.exception("EXCEPTION!")

	def pull_data_GPS():
		try:
			ser.write(b'AT+CGNSINF\r\n')
			time.sleep(0.5)
			vystup = ser.read(ser.inWaiting())
			match = re.search(r'CGNSINF:.*?,.*?,.*?,(.*?),(.*?),', str(vystup))
			if match:
				if match.group(1) == '':
					return (None,None)
				else:
					return (match.group(1),match.group(2))
			#vrati (None,None) alebo ($altitude, $longitude)

		except:
			log.exception("EXCEPTION!")

	def startuj_GPS():
		try:
			#vrati 1 ak sa nenacital modul
			#vrati 0 ak nasiel signal
			try:
				global ser
				ser = serial.Serial("/dev/ttyUSB0", 115200)
				ser.write(b'AT+CGNSPWR=1\r\n')
				ser.flushInput()
				time.sleep(0.5)
			except:
				event_alrm_GPS_modulNenacitany.set()
				return 1 #nenacital som ttyUSB0 port, restartuj RPI
			odpoved = str(ser.read(ser.inWaiting()))

			event_gpsNastartovane.set()
			return 0

		except:
			log.exception("EXCEPTION!")

	def meraj_GPS():
		try:
			global zhromazdisko_gps
			
			zhromazdisko_gps.append(Meraj.pull_data_GPS())
			
			with print_lock:
				print (list(zhromazdisko_gps)[-1])
			
		#vypni gps:
		except:
			log.exception("EXCEPTION!")

	def vypni_GPS():
		try:
			ser.write(b'AT+CGNSPWR=0\r\n')
			time.sleep(1)
			odpoved = str(ser.read(ser.inWaiting()))
		except:
			log.exception("EXCEPTION!")



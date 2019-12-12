#!/usr/bin/python3.7

# This module contains functions that encode/decode data into/from message string that is sent over network socket.

import sys, queue, time, threading
from datetime import datetime
from functools import *

import ZDIELANE_PREMENNE as ZP
from ZDIELANE_PREMENNE import log
import pomocne_funkcie.vseobecne_pomocne_funkcie as vseobecne
import pomocne_funkcie.specialne_pomocne_funkcie as specialne


def sformulujOdpoved(konfigD):	#outputs message that will be sent to the server
	
	#All temperature/humidity values are sent as average values of newest measurings
	listVysledkovMerani = specialne.vysledkyAkoPriemeryMerani()

	#create the message:
	nast = Zabal.nastavenia(\
		intervalMerTep = konfigD['intervalMerTep'], \
		intervalMerGps = konfigD['intervalMerGps'], \
		intervalInfTep = konfigD['intervalInfTep'], \
		intervalInfGps = konfigD['intervalInfGps'], \
		tolerLow = konfigD['tolerLow'], \
		tolerHigh = konfigD['tolerHigh'], \
		onOffAlarmPark = konfigD['onOffAlarmPark'], \
		aktBoxy = konfigD['aktBoxy'])
	vysl = Zabal.vysledky(\
		tv_snz1 = listVysledkovMerani[0],\
		tv_snz2 = listVysledkovMerani[1],\
		tv_snz3 = listVysledkovMerani[2], \
		tv_snz4 = listVysledkovMerani[3], \
		tv_snz5 = listVysledkovMerani[4], \
		tv_snz6 = listVysledkovMerani[5], \
		tv_snzVonkajsi = listVysledkovMerani[6], \
		tv_snzRPI = listVysledkovMerani[7], \
		tv_snzWTPI = listVysledkovMerani[8], \
		senzorySNezdrTeplotami = ZP.nezdraveTep_senzory, \
		senzorySOscilTeplotami = ZP.oscilujuceTep_senzory, \
		senzorySoZasekTeplotami = ZP.zaseknute_senzory, \
		gps_suradnice = '')
	odosielanaSprava = Zabal.celkovuSpravu(nast, vysl)
	return odosielanaSprava 	#resulting message

					
#SPRAVY:
class Rozbal:	#decode the message received from server

	def __init__(self, sprava): 
		try:	
			
			self.sprava = sprava #sprava je v tomto formate: E0H0M020E050D0j31050C040f2h1B1 jedna hodnota ma velkost 2
			#najprv premen kodovane dataVSprave 'E0H0M0' na list hodnot ktore zastupuju (index v ZP.CODE) : [23, 45, 15] 
			print ("sprava:", sprava)
			self.spravaL = [ZP.CODE.index(sprava[i:i+2]) for i in range(0, len(sprava), 2)]
			
			self.dlzkaSpravy = self.spravaL[0]
			self.casOdosielania = self.spravaL[1:7]# list vo formate [19, 23, 12, 32,43,23] = [rok, mesiac, den, hodina, minuta, sekunda]
			#PRVE TRI POLIA:
			self.zastupenie = list(vseobecne.ConvertFromIntTo.binarkaSTR(self.spravaL[7]))#[0, 1, 1, 1, 0, 0, 0, 1] 8bitov
	
			#DATA:		
			self.listHodnot = self.__listZoradenychHodnot(self.spravaL[8:])
			self.intervalMerTep, self.intervalMerGps, self.intervalInfTep, self.intervalInfGps, \
			self.tolerLow, self.tolerHigh, self.onOffAlarmPark, self.aktBoxy = self.listHodnot

		except:
			log.exception("EXCEPTION!")

	def __listZoradenychHodnot(self, dataVSprave):
		#data v Sprave maju format: [19, 23, 12, 32, 43, 23]
		#return funkcie snad nieco taketo: [12,24,24,123456879,35,15,'10001100', '10001100']
		print("dataVSprave", dataVSprave)
		try:
			i= 0	#index velicin
			k = 0	#index spravy
			result = []
			for bit in self.zastupenie:
				if i > 8: #po 8 bitoch skonci
					break
				if bit == '1':
					if i in [0,1,2,3]:	#intervalove veliciny
						#print ("index je %d k je %d, sprava je %d ", i, k, self.sprava[8:])
						result.append(self.__vyratajInterval(dataVSprave[k]))	#ostatne IntervalVeliciny
					elif i in [4,5]:	#tolerLow, tolerHigh
						result.append(ZP.TEPLOTY[dataVSprave[k]])
					elif i in [6]:	#onOffAlarmPark
						result.append(vseobecne.ConvertFromIntTo.binarkaSTR(dataVSprave[k]))	#
					elif i in [7]:	#aktBoxy
						result.append(vseobecne.ConvertFromIntTo.binarkaSTR(dataVSprave[k]))
					k += 1	#chod na dalsiu hodnotu v sprave
				else:
					result.append(None)
				i += 1
			return result #snad nieco taketo: [12,24,24,123456879,35,15,'10001100', '10001100']


		except:
			log.exception("EXCEPTION!")

	def __vyratajInterval(self, index):
		try:
			return ZP.MOZNEIntervalySprav[index]

		except:
			log.exception("EXCEPTION!")


class Zabal: #encode the data into a message that will be sent to the server
	
	def celkovuSpravu(nastavenia_box = None, vysledky_box = None, casOdosielania = datetime.now()):
		try:
			# print(nastavenia_box, vysledky_box)	
			dlzkaDat = nastavenia_box[0] + vysledky_box[0] #int
			dlzkaPovinnychVelicin =  2 * (1 + 6 + 3)	#int

			zastupenie = nastavenia_box[1] + vysledky_box[1] #b'\x03\x23' + b'\x03\x23' = 4B
			dlzkaSpravy = ZP.CODE[dlzkaPovinnychVelicin + dlzkaDat]	##int + int vrati CODE 1B
			casOdosielania = Zabal.__cas(casOdosielania)	#CODE 6B
			sprava = nastavenia_box[2] + vysledky_box[2]

			#return dlzkaSpravy1B + casOdosielania6B + zastupenie4B + spravaXB
			return dlzkaSpravy + casOdosielania + zastupenie + sprava

		except:
			log.exception("EXCEPTION!")

	def nastavenia(intervalMerTep = '', intervalMerGps = '', intervalInfTep = '', intervalInfGps = '', \
					tolerLow = '', tolerHigh = '', onOffAlarmPark = '', aktBoxy = ''):
		try:
			#mozne intervaly su v ZP.MOZNEIntervalySprav, tolerancie su teplota, onoff su True, False, wifi meno heslo je ("meno", "heslo")
			intervalMerTep = vseobecne.ConvertToCODEFrom.intervalINT(intervalMerTep) if intervalMerTep != '' else ''
			intervalMerGps = vseobecne.ConvertToCODEFrom.intervalINT(intervalMerGps) if intervalMerGps != '' else ''
			intervalInfTep = vseobecne.ConvertToCODEFrom.intervalINT(intervalInfTep) if intervalInfTep != '' else ''
			intervalInfGps = vseobecne.ConvertToCODEFrom.intervalINT(intervalInfGps) if intervalInfGps != '' else ''
			tolerLow = vseobecne.ConvertToCODEFrom.teplotaINT(tolerLow) if tolerLow != '' else ''
			tolerHigh = vseobecne.ConvertToCODEFrom.teplotaINT(tolerHigh) if tolerHigh != '' else ''
			onOffAlarmPark = vseobecne.ConvertToCODEFrom.binarkaSTR(onOffAlarmPark) if onOffAlarmPark != '' else '' #reprezentuje on/off
			aktBoxy = vseobecne.ConvertToCODEFrom.binarkaSTR(aktBoxy) if aktBoxy != '' else '' #reprezentuje on/off

			dataTUPLE = (intervalMerTep, intervalMerGps, intervalInfTep, intervalInfGps, \
			tolerLow, tolerHigh, onOffAlarmPark, aktBoxy)
			#tuple ktory obsahuje CODE objekty v poradi akom budu v sprave		
			zastupenie = Zabal.__zastupenie(dataTUPLE) 
			dlzkaDat = Zabal.__dlzkaDat(dataTUPLE)
			sprava = reduce(lambda x,y: x+y, dataTUPLE)
			
			return dlzkaDat, zastupenie, sprava
			#VRATI spravu vo formate b'sd131fsdfas', zastupenie b'x\034', dlzkudat ako int 23

		except:
			log.exception("EXCEPTION!")

	def vysledky(tv_snz1 = '',tv_snz2 = '',tv_snz3 = '', tv_snz4 = '', tv_snz5 = '', tv_snz6 = '', \
			tv_snzVonkajsi = '',  tv_snzRPI = '', tv_snzWTPI = '', senzorySNezdrTeplotami = '', senzorySOscilTeplotami = '',\
			senzorySoZasekTeplotami = '', gps_suradnice = ''):
		try:
			#tv_snz: input = (teplota, indexTepelny) -> 2B CODE
			#gps_suradnice: input = (altitude, longitude) -> velke cislo v jednoduchom formate: b'123.45,56.423435')
			gps_suradnice = (str(gps_suradnice[0])+","+str(gps_suradnice[1])).encode() if gps_suradnice != '' else '' #jednoduchy format b'123.45,56.423435'

			dataTUPLE = (\
				vseobecne.ConvertToCODEFrom.tepInd(tv_snz1),\
				vseobecne.ConvertToCODEFrom.tepInd(tv_snz2),\
				vseobecne.ConvertToCODEFrom.tepInd(tv_snz3),\
				vseobecne.ConvertToCODEFrom.tepInd(tv_snz4),\
				vseobecne.ConvertToCODEFrom.tepInd(tv_snz5),\
				vseobecne.ConvertToCODEFrom.tepInd(tv_snz6),\
				vseobecne.ConvertToCODEFrom.tepInd(tv_snzVonkajsi),\
				vseobecne.ConvertToCODEFrom.tepInd(tv_snzRPI),\
				vseobecne.ConvertToCODEFrom.tepInd(tv_snzWTPI),\
				vseobecne.ConvertToCODEFrom.binarkaSTR(senzorySNezdrTeplotami) if senzorySNezdrTeplotami != '' else '',\
				vseobecne.ConvertToCODEFrom.binarkaSTR(senzorySOscilTeplotami) if senzorySOscilTeplotami != '' else '',\
				vseobecne.ConvertToCODEFrom.binarkaSTR(senzorySoZasekTeplotami) if senzorySoZasekTeplotami != '' else '',\
				gps_suradnice)
			zastupenie = Zabal.__zastupenie(dataTUPLE[:8]) + Zabal.__zastupenie(dataTUPLE[8:])
			dlzkaDat = Zabal.__dlzkaDat(dataTUPLE)
			sprava = reduce(lambda x,y: x+y, dataTUPLE)
			return dlzkaDat, zastupenie, sprava

		except:
			log.exception("EXCEPTION!")

	def __zastupenie(data):
		try:
			#vystup je int do 128, ktore urci ktore parametre su v sprave zastupene
			#funguje len pre tuple o velkosti 7
			zastupenie = ''
			for velicina in data:
				if velicina != '':
					zastupenie += '1'
				else:
					zastupenie += '0'
			if len(data) < 8:
				zastupenie += '0'*(8-len(data))
			return vseobecne.ConvertToCODEFrom.binarkaSTR(zastupenie)
			#vrati CODE

		except:
			log.exception("EXCEPTION!")

	def __dlzkaDat(data):
		try:
			#toto funguje aj pre data o velkosti 1 a 0
			dlzka = 0
			for i in data:
				if i != '':
					dlzka += len(i)
			return dlzka
			#vrati int

		except:
			log.exception("EXCEPTION!")

	def __cas(cas_datetime):
		try:
			casList = [cas_datetime.year - 2000, cas_datetime.month, cas_datetime.day, cas_datetime.hour, cas_datetime.minute, cas_datetime.second]
			casCODE = ''
			for i in casList:
				casCODE += ZP.CODE[int(i)]
			
			return casCODE
			#vrati CODE
		except:
			log.exception("EXCEPTION!")


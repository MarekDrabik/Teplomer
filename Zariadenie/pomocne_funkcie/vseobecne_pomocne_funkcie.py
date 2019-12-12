#!/usr/bin/python3.7

# This file defines functions that are more universal in a sense that they can be reused outside of this project.

import serial, sys, json, threading, queue, re, os, time, math
from datetime import datetime
from functools import *

import ZDIELANE_PREMENNE as ZP
from ZDIELANE_PREMENNE import log


class Pomoc:

	def priemer(lst):
		return sum(lst) / len(lst) 

	def modifyString(strng, chrcter, indx):
		try:
			strng_list = list(strng)
			strng_list[indx] = chrcter
			return ''.join(strng_list)

		except:
			log.exception("EXCEPTION!")

	def zaokruhli_napoli(teplotu):
		try:
			if teplotu == None:
				return None
			else:
				return round(teplotu * 2) / 2
		except:
			log.exception("EXCEPTION!")

	def datetimeToList(datetimeobjekt):
		try:
			l1 = datetimeobjekt
			#vytvor list:
			return [l1.year - 2000,l1.month,l1.day,l1.hour,l1.minute,l1.second]

		except:
			log.exception("EXCEPTION!")

	def precitajJsonFile(filename):
		try:
			with open(filename) as f:
				return json.load(f)

		except:
			log.exception("EXCEPTION!")

	def prepisJsonFile(slovnik, filename):
		try:
			with open(filename, "w") as f:
				json.dump(slovnik, f, indent = 2, sort_keys = True)

		except:
			log.exception("EXCEPTION!")

	def heatIndexCalculate(T,R): #calculate heatindex based on temp and humidity
		try:
			# teplota v stupnoch celsia
			if T >= 24.5:
				c1 = -8.78469475556
				c2 = 1.61139411
				c3 = 2.33854883889
				c4 = -0.14611605
				c5 = -0.012308094
				c6 = -0.0164248277778
				c7 = 0.002211732
				c8 = 0.00072546
				c9 = -0.000003582
				HI = c1 + c2*T + c3*R + c4*T*R + c5*T*T + c6*R*R + c7*T*T*R + c8*T*R*R + c9*T*T*R*R
			else:
				#vsetky ostatne teploty maju heatindex rovny teplote v stupnoch celsia
				HI = T
			return round(HI)

		except:
			log.exception("EXCEPTION!")


class ConvertToCODEFrom:

	def tepInd(tv_snz):
		try:
			if tv_snz == '':
				return ''
			else:
				return ConvertToCODEFrom.teplotaINT(tv_snz[0])+ConvertToCODEFrom.vlhkostINT(tv_snz[1])

		except:
			log.exception("EXCEPTION!")

	def intervalINT(cislo):
		try:
			#(INT) cislo = jedno z tych v ZP.MOZNEIntervalySprav
			index = ZP.MOZNEIntervalySprav.index(cislo)
			assert index < 254
			return ZP.CODE[index]
			#vystup CODE je poradie intervalu v ZP.MOZNEIntervalySprav

		except:
			log.exception("EXCEPTION!")

	def teplotaINT(teplota):
		try:
			#(INT) teplota = -40, -25.5, ...., 80
			index = ZP.TEPLOTY.index(teplota)
			assert index < 254
			return ZP.CODE[index]

		except:
			log.exception("EXCEPTION!")

	def vlhkostINT(vlhkost):
		try:
			index = ZP.VLHKOSTI.index(vlhkost)
			assert index < 254
			return ZP.CODE[index]

		except:
			log.exception("EXCEPTION!")

	def binarkaSTR(jednotkynuly):
		assert len(jednotkynuly) == 8
		try:
			#(STRING) jednotkynuly = '00100110' 8 bitov !!! 
			#alebo (True/False)
			if jednotkynuly == False:
				return ZP.CODE[0]
			elif jednotkynuly == True:
				return ZP.CODE[1]

			cislo = 0
			i = 0
			for bit in jednotkynuly:
				if bit == '1':
					cislo += 2**(7-i)
				i += 1
			return ZP.CODE[cislo]

		except:
			log.exception("EXCEPTION!")


class ConvertFromIntTo:
	
	def binarkaSTR(bajtCislo):
		try:
			binarkaSTR = ''
			for i in range(8):
				bit = bajtCislo // int(math.pow(2,(7-i)))
				if bit == 1:
					bajtCislo = bajtCislo - int(math.pow(2,(7-i)))
				binarkaSTR += str(bit)
			return binarkaSTR #prirodzene poradie bitov, prvy zastupuje hodnotu 128 poslendny 1
		except:
			log.exception("EXCEPTION!")

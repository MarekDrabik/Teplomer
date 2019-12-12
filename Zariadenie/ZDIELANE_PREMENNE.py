#!/usr/bin/python3.7

#This is a storage for all variables that are shared between modules

import queue, threading
from collections import deque
import threading, logging, logging.handlers


MOZNEIntervalySprav = (6, 12, 24, 48, 96, 192, 384, 768, 1536, 3072, 6144, 12288, 24576, 49152, 123456789)
            #insomnia je < MIN_ODDYCH
#0 (vzdy som vymazal)
# konfiguracia (defaultna):
#MOZNEIntervalySpravText = ('vždy', '4s', '15s', '1m', '4m', '8m', '16m', '32m', '1h', '2h', '4h', '8h', 'vypni Teplomer')

#BCM cislovanie pinov:
SENZ_TO_PIN = {'snz1':21, 'snz2':13 , 'snz3':6, 'snz4':5, 'snz5':20, \
      'snz6': 16, 'vonkajsi': 12, 'rpi':0, 'wittyPi':0} 

VOLBY_ANDROID = ('intervalMerTep','intervalMerGps','intervalInfTep', 'intervalInfGps',\
        'tolerLow', 'tolerHigh', 'onOffAlarmPark', 'aktBoxy')

INTERVALOVE_PREMENNE = ('intervalMerTep', 'intervalMerGps', 'intervalInfTep', 'intervalInfGps')

SENZORY = ['snz1', 'snz2', 'snz3', 'snz4', 'snz5', 'snz6', 'vonkajsi', 'rpi', 'wittyPi']
POCET_SENZOROV = 6

FREQ = 6
#NASTAVENIA:
VELKOST_OKNA_MERANI = 6 # * FREQ = casova perioda taka, ze ak je teplota ustalena po takuto dobu, 
                        #povazujem jej hodnotu za realnu teplotu boxu
CAS_KNTRL_OSCIL = 300 #ak sa teplota neustalila po tejto dobe, spusti alarm (teplota osciluje)
                    #hodnota musi byt rozumna. moze is aj o pripad, ze teplota sa neustaluje v dosledku toho, ze 
                    #pes ma krizovu teplotu a je nepokojny, v tom pripade je dobre spustit alarm.
CAS_KNTRL_ZASEK = 1200 #ak zasiela senzor uplne rovnake hodnoty po tuto dobu spusti alarm (senzor zaseknuty)
                      # pravdepodobnost, ze to nastane je mala a je asi lepsie velke cislo nech to zbytocne nerobi plany poplach
                      # a kontroly aj tak bezia takze jedine, ze by sa bol senzor naozaj zasekol v krizovej situacii by to mohol byt problem - velmi mala sanca
rozptylTep = 0.5 # aky rozptyl teploty (+/-)(takze hodnoty medzi x-0.4:x+0.4) este tolerujeme a povazujeme za normalnu fluktuaciu vzduchu
rozptylVlh = 6 # ak su tieto cisla prilis male, mozme mat velmi dlhe intervaly kontroly oscilacii lebo vsetko 
              #sa bude povazovat za podozrivu oscilacii teploty.
              #ak prilis velke tak mozme odignorovat pripady ked je teplota uz zcasu-nacas nezdrava ale my sme ju zpriemerovali na zdravu
ZVACSENIE_KVOLI_MOZNYM_CHYBAM = 1.5 #pozri specialne.vyberValidneMerania()
POCET_DOVOLENYCH_OUTLIERS = 0 #to su teploty mimo reprezentat. zostavy
MINIMALNA_TOLEROVANA_KVALITA = 1 - (POCET_DOVOLENYCH_OUTLIERS / VELKOST_OKNA_MERANI)

VelkostZhrKazdejTep = VELKOST_OKNA_MERANI*2 #krat 2 lebo potrebujeme nejaku rezervu na specialne.vyberValidneMerania()

RPI_TEP_TOLER = 75 #not used
WITTY_TEP_TOLER = 80 #not used

#KONSTANTY:
MAIN_DIR = '/home/pi/teplomer/'
LOADING_CAS = 18 #pociatocny cas (skracuje dlzku spanku). 
        #je dost dlhy aby sa stihol resetnut adapter ak nastane problem
        #  interval od startu merania kedy sa odosle a kontroluje prva teplota				 
        #pociatocny cas. interval od startu merania kedy sa odosle a kontroluje prve gps
# RPI_BOOTUP_CAS = 21.7
RPI_BOOTUP_CAS = 58.7
SOME_TIME_TO_FINISH_ADAPTER_JOBS = 6
MIN_ODDYCH = 90
PREDPRIPRAVA_ODOSIELANIA = 24 #je kolko casu pred odosielanim zapiname internet
# MIN_INTERVAL_KEDY_VYPNEME_INTERNET = MOZNEIntervalySprav[3]
TRVANIE_RESTARTU = 30 #najnizsia hodnota teoreticky by mala byt cca 18 sekund

TEL_CISLO = b'+421910208334' #marek
# TEL_CISLO = b'+421911235302'  #andrej


#PREMENNE:

AdapterNeodosielaSpravu = True

troubleMonitor = 'to be pomocneObj.TroubleMonitor object'

#create loggers:
log = logging.getLogger('log')  #main debug logger
logVysledky = logging.getLogger('logVysledky') #results logger to csv format
logSerial = logging.getLogger('logSerial') #serial console logger

log.setLevel(logging.DEBUG)
logVysledky.setLevel(logging.INFO)
logSerial.setLevel(logging.DEBUG)
#their format:
formatDebug = logging.Formatter('%(asctime)8s %(levelname)8s:%(threadName)10s>%(funcName)12s: %(message)s')
formatVysledky = logging.Formatter('%(asctime)8s %(message)s')

#log debug to file:
debugLog_handler = logging.handlers.TimedRotatingFileHandler(MAIN_DIR + 'debugLog_dir/' + 'debugLog', when='midnight', backupCount=50, encoding=None, delay=False, utc=False)
debugLog_handler.setFormatter(formatDebug)
debugLog_handler.setLevel(logging.DEBUG)
#log debug to console too:
consoleOutput_handler = logging.StreamHandler()
consoleOutput_handler.setFormatter(formatDebug)
consoleOutput_handler.setLevel(logging.DEBUG)
#log results to file (one log per one main loop)
vysledkyLog_handler = logging.handlers.TimedRotatingFileHandler(MAIN_DIR + 'vysledkyLog_dir/' + 'vysledkyLog', when='midnight', backupCount=50, encoding=None, delay=False, utc=False)
vysledkyLog_handler.setFormatter(formatVysledky)
vysledkyLog_handler.setLevel(logging.INFO)
#log adapter serial console to file:
serialLog_handler = logging.handlers.TimedRotatingFileHandler(MAIN_DIR + 'serialLog_dir/' + 'serialLog', when='midnight', backupCount=50, encoding=None, delay=False, utc=False)
serialLog_handler.setFormatter(formatVysledky)
serialLog_handler.setLevel(logging.DEBUG)
# assign handlers:
log.addHandler(debugLog_handler)
log.addHandler(consoleOutput_handler)
logVysledky.addHandler(vysledkyLog_handler)
logSerial.addHandler(serialLog_handler)


logPerRun = "object logPerRun"
logPerRun_lock = threading.Lock()

DEBUG = {'snz1': {}, 'snz2': {}, 'snz3': {}, 'snz4': {}, 'snz5': {}, \
			'snz6': {}}
merTepCas_debug = 0


konfigD = dict()
konfigD_dummy = dict()
Kntrl_tep_succesfully_finished = [True] * 11
Kntrl_gps_OK = True

event_alarm = threading.Event()
event_kntrlTep = threading.Event()
event_snz1 = threading.Event()
event_snz2 = threading.Event()
event_snz3 = threading.Event()
event_snz4 = threading.Event()
event_snz5 = threading.Event()
event_snz6 = threading.Event()
kntrlEventy = [event_snz1, event_snz2, event_snz3,event_snz4, event_snz5, event_snz6]

q1=queue.Queue(maxsize=1)
q2=queue.Queue(maxsize=1)
q3=queue.Queue(maxsize=1)
q4=queue.Queue(maxsize=1)
q5=queue.Queue(maxsize=1)
q6=queue.Queue(maxsize=1)
Q = [q1,q2,q3,q4,q5,q6]

adapterJob_prioDeq = 'pomocneObjekty.PrioDeque neskor'
adapterOdpoveda_queue = queue.Queue(1)
netBlika_queue = queue.Queue(1)

prijataSprava_deque = deque([],1) #po prijati spravy obsahuje tuple: (prijataSprava_obj, konfigD_dummy)
prijataSprava_dequelock = threading.Lock()

resetujKontroly = False

nezdraveTep_senzory = "00000000"
oscilujuceTep_senzory = "00000000"
zaseknute_senzory = "00000000"

zhromazdisko_tep = {'snz1': deque([],VelkostZhrKazdejTep), 'snz2': deque([],VelkostZhrKazdejTep), 'snz3': deque([],VelkostZhrKazdejTep), 'snz4': deque([],VelkostZhrKazdejTep), 'snz5': deque([],VelkostZhrKazdejTep), \
			'snz6': deque([],VelkostZhrKazdejTep), 'vonkajsi': deque([],VelkostZhrKazdejTep), 'rpi': deque([],VelkostZhrKazdejTep), 'wittyPi': deque([],VelkostZhrKazdejTep)}
# zhromazdisko_tep  = {'snz1': deque([(tep,vlh),(tep,vlh)...],size=VelkostZhrKazdejTep)
filterVysledkyD = {'snz1': None, 'snz2': None, 'snz3': None, 'snz4': None, 'snz5': None, \
			'snz6': None, 'vonkajsi':  None}
#filterVysledkyD = {'snz1': ((priemerTep, priemerVlh), kvalitaT, kvalitaV), ...}
silaSignalu = 99 #default value 99 means not detactable (shows - )


zhromTep_lock = threading.Lock()
kntrlTepOk_lock = threading.Lock()
debug_lock = threading.Lock()
konfigD_lock = threading.Lock()
zaseknute_senzory_lock = threading.Lock()
oscilujuceTep_senzory_lock = threading.Lock()
nezdraveTep_senzory_lock = threading.Lock()	

event_cakajNaPripojenie = threading.Event()
event_vypniGPS = threading.Event()
event_alrm_GPS_modulNenacitany = threading.Event()
event_zapisRpiTeplotu = threading.Event()
event_tepSenzorNeodpoveda = threading.Event()
event_gpsNastartovane = threading.Event()


TEPLOTY = (None, -40, -39.5, -39, -38.5, -38, -37.5, -37, -36.5, -36, -35.5, -35, -34.5, -34, -33.5, -33, \
-32.5, -32, -31.5, -31, -30.5, -30, -29.5, -29, -28.5, -28, -27.5, -27, -26.5, -26, -25.5, -25, -24.5, \
-24, -23.5, -23, -22.5, -22, -21.5, -21, -20.5, -20, -19.5, -19, -18.5, -18, -17.5, -17, -16.5, -16, \
-15.5, -15, -14.5, -14, -13.5, -13, -12.5, -12, -11.5, -11, -10.5, -10, -9.5, -9, -8.5, -8, -7.5, -7, \
-6.5, -6, -5.5, -5, -4.5, -4, -3.5, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, \
4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, \
15.5, 16, 16.5, 17, 17.5, 18, 18.5, 19, 19.5, 20, 20.5, 21, 21.5, 22, 22.5, 23, 23.5, 24, 24.5, 25, \
25.5, 26, 26.5, 27, 27.5, 28, 28.5, 29, 29.5, 30, 30.5, 31, 31.5, 32, 32.5, 33, 33.5, 34, 34.5, 35, \
35.5, 36, 36.5, 37, 37.5, 38, 38.5, 39, 39.5, 40, 40.5, 41, 41.5, 42, 42.5, 43, 43.5, 44, 44.5, 45, \
45.5, 46, 46.5, 47, 47.5, 48, 48.5, 49, 49.5, 50, 50.5, 51, 51.5, 52, 52.5, 53, 53.5, 54, 54.5, 55, \
55.5, 56, 56.5, 57, 57.5, 58, 58.5, 59, 59.5, 60, 60.5, 61, 61.5, 62, 62.5, 63, 63.5, 64, 64.5, 65, \
65.5, 66, 66.5, 67, 67.5, 68, 68.5, 69, 69.5, 70, 70.5, 71, 71.5, 72, 72.5, 73, 73.5, 74, 74.5, 75, \
75.5, 76, 76.5, 77, 77.5, 78, 78.5, 79, 79.5, 80)

VLHKOSTI = (None, 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, \
4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, \
15.5, 16, 16.5, 17, 17.5, 18, 18.5, 19, 19.5, 20, 20.5, 21, 21.5, 22, 22.5, 23, 23.5, 24, 24.5, 25, \
25.5, 26, 26.5, 27, 27.5, 28, 28.5, 29, 29.5, 30, 30.5, 31, 31.5, 32, 32.5, 33, 33.5, 34, 34.5, 35, \
35.5, 36, 36.5, 37, 37.5, 38, 38.5, 39, 39.5, 40, 40.5, 41, 41.5, 42, 42.5, 43, 43.5, 44, 44.5, 45, \
45.5, 46, 46.5, 47, 47.5, 48, 48.5, 49, 49.5, 50, 50.5, 51, 51.5, 52, 52.5, 53, 53.5, 54, 54.5, 55, \
55.5, 56, 56.5, 57, 57.5, 58, 58.5, 59, 59.5, 60, 60.5, 61, 61.5, 62, 62.5, 63, 63.5, 64, 64.5, 65, \
65.5, 66, 66.5, 67, 67.5, 68, 68.5, 69, 69.5, 70, 70.5, 71, 71.5, 72, 72.5, 73, 73.5, 74, 74.5, 75, \
75.5, 76, 76.5, 77, 77.5, 78, 78.5, 79, 79.5, 80, 80.5, 81, 81.5, 82, 82.5, 83, 83.5, 84, 84.5, 85, \
85.5, 86, 86.5, 87, 87.5, 88, 88.5, 89, 89.5, 90, 90.5, 91, 91.5, 92, 92.5, 93, 93.5, 94, 94.5, 95, \
95.5, 96, 96.5, 97, 97.5, 98, 98.5, 99, 99.5, 100)

CODE = ('00', '10', '20', '30', '40', '50', '60', '70', '80', '90', '?0', '@0', 'A0', 'B0', 'C0', 'D0', 
'E0', 'F0', 'G0', 'H0', 'I0', 'J0', 'K0', 'L0', 'M0', 'N0', 'O0', 'P0', 'Q0', 'R0', 'S0', 'T0', 'U0', 'V0',
 'W0', 'X0', 'Y0', 'Z0', 'a0', 'b0', 'c0', 'd0', 'e0', 'f0', 'g0', 'h0', 'i0', 'j0', 'k0', 'l0', 'm0', 'n0', 
 'o0', 'p0', 'q0', 'r0', 's0', 't0', 'u0', 'v0', 'w0', 'x0', 'y0', 'z0', '01', '11', '21', '31', '41', '51', 
 '61', '71', '81', '91', '?1', '@1', 'A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1', 'J1', 'K1', 'L1', 
 'M1', 'N1', 'O1', 'P1', 'Q1', 'R1', 'S1', 'T1', 'U1', 'V1', 'W1', 'X1', 'Y1', 'Z1', 'a1', 'b1', 'c1', 'd1', 
 'e1', 'f1', 'g1', 'h1', 'i1', 'j1', 'k1', 'l1', 'm1', 'n1', 'o1', 'p1', 'q1', 'r1', 's1', 't1', 'u1', 'v1', 
 'w1', 'x1', 'y1', 'z1', '02', '12', '22', '32', '42', '52', '62', '72', '82', '92', '?2', '@2', 'A2', 'B2',
  'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2', 'J2', 'K2', 'L2', 'M2', 'N2', 'O2', 'P2', 'Q2', 'R2', 'S2', 'T2', 
  'U2', 'V2', 'W2', 'X2', 'Y2', 'Z2', 'a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2', 'i2', 'j2', 'k2', 'l2', 
  'm2', 'n2', 'o2', 'p2', 'q2', 'r2', 's2', 't2', 'u2', 'v2', 'w2', 'x2', 'y2', 'z2', '03', '13', '23', '33', 
  '43', '53', '63', '73', '83', '93', '?3', '@3', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'I3', 'J3', 
  'K3', 'L3', 'M3', 'N3', 'O3', 'P3', 'Q3', 'R3', 'S3', 'T3', 'U3', 'V3', 'W3', 'X3', 'Y3', 'Z3', 'a3', 'b3', 
  'c3', 'd3', 'e3', 'f3', 'g3', 'h3', 'i3', 'j3', 'k3', 'l3', 'm3', 'n3', 'o3', 'p3', 'q3', 'r3', 's3', 't3', 
  'u3', 'v3', 'w3', 'x3', 'y3', 'z3')



# Teplomer IOT

<img align="right" src="/.doc/trailer.png" width="300">
Teplomer IOT je zariadenie ktoré som vytvoril pre svojho brata, ktorý sa zúčastňuje pretekov psích záprahov. Na prevoz a ubytovanie psov na podujatí používa prívesný vozík s nadstavbou, kde majú psy svoje boxy. Tieto boxy sú dobre tepelne izolované na zimné obdobie, ale to zároveň spôsobuje starosti v teplejšom počasí. Psy sa môžu prehriať, keďže nemôžu regulovať svoju teplotu bez prísunu chladného vzduchu. Na to, aby boli v bezpečí, je treba pravidelne manuálne kontrolovať či je teplota primeraná, a prípadne ju regulavať otváraním a zatváraním dverí na vozíku.
<br><br>
<img align="left" src="/.doc/box.png" width="175">
Toto zariadenie som vytvoril aby pomohlo s prevenciou takýchto situácií, ktoré môžu byť až život ohrozujúce. Teplomer meria teploty v boxoch a upozorní brata ak je v niektorom boxe príliš teplo alebo príliš zima tak, že mu zavolá na telefón.
Súčasťou projektu je aj webová aplikácia cez ktorú si brat vie skontrolovať situáciu vo vozíku na diaľku, prípadne prestaviť parametre Teplomera.<br>
Účelom zariadnia je poskytnúť dodatočné monitorovanie ako ďalší prvok ochrany k tomu čo už brat manuálne robí. Tým sa zmenšuje pravdepodobnosť, že by sa krízová situácia "prehliadla". 


<br><br><br>

## Hlavné prvky

 * Teplomer je počítač **Raspberry Pi** s ďalšími pridanými modulmi <img align="right" src=".doc/hw.png" width="300" /> a batériou, ktorý je uložený v plastovej krabičke. Táto krabička sa vkladá do zadnej časti prívesného vozíka kde sa zapojí na kabeláž senzorov a spustí stlačením tlačidla.
 * meria sa nielen teplota ale aj vlhkosť z čoho sa potom počíta takzvaná [**pocitová teplota**](https://en.wikipedia.org/wiki/Heat_index), čo je relevatnejší ukazovateľ komfortu tela
 * zariadenie upozorňuje užívateľa na problém **zavolaním na telefón**
 * počítač kontroluje nielen to či je teplota na senzoroch v zdravom rozsahu, ale aj to či sa niektorý senzor nezasekol, alebo či je teplota ustálená 
 * k dispozícii je **webová aplikácia** ktorá zobrazuje informácie Teplomera a ponúka možnosti jeho nastavenia
   * okrem iného, zobrazuje hlavne **teplotu a vlhkosť v jednotlivých boxoch**
   * na **šetrenie batérie**, ktorá vydrží približne 24 hodín pri neustálom behu, je možné zvýšiť interval v akom má Teplomer merať a počítač sa potom sám vypne medzi týmito meraniami.
   * na **šetrenie mobilných dát** je zase môžné prestaviť interval informovania
 

## Možnosť reálne vyskúšať <img align="right" src=".doc/screenshot.png" width="180" />
Aplikácia je k dispozícii na vyskúšanie na adrese: https://87.197.183.237:5443/home <br>
Na zobrazenie stránky je potrebné odsúhlasiť bezpečnostnú výnimku na certifikát.

Ak o to teda máte záujem a dáte mi vedieť, tak ja zapnem aj Teplomer, aby aplikácia zobrazovala reálne dáta. <br>

**Prihlasovacie údaje:** <br>
meno: _teplomer_ <br>
heslo: _Jk2;Ak1ma_ <br>

 
## Github Repository
V tomto repository nájdete kód celého projektu:
* [Zariadenie](https://github.com/MarekDrabik/Teplomer/tree/master/Zariadenie) - celý kód Teplomera, teda toho zariadenia ktoré je vložené do prívesného vozíka (Python)
* [Server](https://github.com/MarekDrabik/Teplomer/tree/master/Server) - backend kód servera ktorý beží doma na druhom Raspberry Pi (Node.js) 
* [Server/public](https://github.com/MarekDrabik/Teplomer/tree/master/Server/public) - frontend webová aplikácia (Javascript, html, css)


## Detailný popis Web Aplikácie

1. Web aplikácia zobrazuje základné informácie o stave vo vozíku.

<img float="center" src=".doc/informacieApp.png" />

2. Ponúka možnosť zmeniť nastavenia Teplomera.<br>
_Zmenené hodnoty blikajú nazeleno v pozadí so súčastným nastavením. Nastavenia sa odosielajú rázovo tlačidlom SEND a potom čakajú na serveri kým ich Teplomer neprevezme._
   
<img float="center" src=".doc/instrukcieApp.png" />

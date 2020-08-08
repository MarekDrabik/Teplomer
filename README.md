# Teplomer IOT

<img align="right" src="/.doc/trailer.png" width="300">
Teplomer IOT je zariadenie na monitorovanie teploty v psích boxoch s funkciou alarmu. Vytvoril som ho pre svojho brata, ktorý sa zúčastňuje pretekov psích záprahov. 
Na prevoz a ubytovanie psov na podujatí používa prívesný vozík s nadstavbou, kde majú psy svoje boxy. Tieto boxy sú dobre tepelne izolované na zimné obdobie, čo ale vytvára rizoko prehriatia v teplejšom počasí. Teplotu teda treba pravidelne kontrolovať a regulovať otváraním/zatváraním dverí. Okrem toho, teplota občas stúpne "neintuitívne", napríklad keď je pes nervózny, čo majiteľ nedokáže predvídať.
<br><br>
<img align="left" src="/.doc/box.png" width="175">
Na pomoc tejto situacii som vytvoril zariadenie ktore teplotu v kazdom boxe monitoruje pomocou tepelnych senzorov. V pripade prekrocenia stanoveneho limitu v niektorom z nich, upozorni majitela tak, ze mu zavola na telefon.
K tomuto zariadeniu som vytvoril webovú aplikáciu ktorá poskytuje pohodlné nastavovanie zariadenia na diaľku a zobrazuje aktuálny stav v boxoch.

Zakladnou myslienkou riesenia tohto problemu bolo teda monitorovanie teploty vo vozíku a upozornenie uzívatela na krízovú situáciu.

Aby som moje zariadenie predstavil co naefektivnejsim sposobom. 

1 V idealnom pripade, je zariadenie na monitorovanie byt mobilne, skladne a čo najmenej narocne na obsluhu. 
RIESENIE: * Teplomer je počítač **Raspberry Pi** s ďalšími pridanými modulmi <img align="right" src=".doc/hw.png" width="300" /> a batériou, ktorý je uložený v plastovej krabičke. Táto krabička sa vkladá do zadnej časti prívesného vozíka kde sa zapojí na kabeláž senzorov. Po spustení, stlačením tlačidla, je už ďalej ovládané webovou aplikáciou a žiadna ďalšia manipulácia nie je nutná.

ľ. Zariadenie potrebuje vlastny zdroj elektrickej energie vzhladom na to, ze vozik je pocas pretekov zvacsa odparkovany mimo dosahu elektrickej siete.



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

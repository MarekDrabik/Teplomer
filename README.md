# Teplomer IOT

<img align="right" src="/.doc/trailer.png" width="300">
Teplomer IOT je zariadenie na monitorovanie teploty v psích boxoch s funkciou alarmu. Vytvoril som ho pre svojho brata, ktorý sa zúčastňuje pretekov psích záprahov. 
Na prevoz a ubytovanie psov na podujatí používa prívesný vozík s nadstavbou, kde majú psy svoje boxy. Tieto boxy sú dobre tepelne izolované na zimné obdobie, čo ale vytvára rizoko prehriatia v teplejšom počasí. Teplotu teda treba pravidelne kontrolovať a regulovať otváraním/zatváraním dverí. Okrem toho, teplota občas stúpne "neintuitívne", napríklad keď je pes nervózny, čo majiteľ nedokáže predvídať.
<br><br>
<img align="left" src="/.doc/box.png" width="175">
Na pomoc tejto situacii som vytvoril zariadenie ktore teplotu v kazdom boxe monitoruje pomocou tepelnych senzorov. V pripade prekrocenia stanoveneho limitu v niektorom z nich, upozorni majitela tak, ze mu zavola na telefon.

Zakladnou myslienkou riesenia tohto problemu bolo teda monitorovanie teploty vo vozíku a upozornenie uzívatela na krízovú situáciu.

Mojim riesenim je zariadenie pocitac raspberry pi s dalsou potrebnou elektronikou ulozene v kompaktnej krabicke. Fyzicka manipulacia so zariadenim je nenarocna, krabicku staci vlozit do predripraveneho priestoru vo voziku, pripojit kabel od senzorov a zapnut zariadenie jednoduchym tlacidlom. 

Zariadenie je napajene z vlastnej baterie kedze pocas standardnej prevadzky nie je k dispozicii elektricka siet.

V kazdom z boxov je senzor na meranie teploty a vlhkosti. Zariadenie z tychto hodnot rata pocitovu teplotu, co je korektnejsi ukazovatel komfortu psieho tela ako len teplota samotna.

Ak namerana pocitova teplota v niektorom z boxov prekroci zdrave hodnoty, zariadenie spusti poplach tak, ze uzivatelovi zavola na mobilny telefon. Tato funkcionalita je k dispozicii vdaka GSM modulu s vlastnou SIM kartou.

Sucastou tohto riesenia je webova aplikacia ktora umoznuje uzivatelovi kedykolvek pohodlne zmenit nastavenie zariadenia. 
Uzivatel si v nej navoli hranicne hodnoty pocitovej teploty ktore uz nemaju byt tolerovane, a taktiez urci ktore konkretne boxy je treba monitorovat.

Aplikacia okrem toho zobrazuje aktualne namerane hodnoty v jednotlivych boxoch ako aj aktualne nastavenie zariadenia.

Bateria zariadenia vydrzi priblizne 24 hodín neustáleho behu, avšak preteky trvajú často dlhšie. Okrem ľahko vymeniteľnej náhradnej batérie je preto k dispozicii funkcia šetrenia batérie. 

Algoritmus lalala.


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

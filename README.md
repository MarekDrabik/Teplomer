# Teplomer IOT - zariadenie na monitorovanie teploty v psích boxoch

<img align="right" src="/.doc/trailer.png" width="300">
Toto zariadenie som vyrobil pre svojho brata, ktorý sa zúčastňuje pretekov psích záprahov. Na prevoz a ubytovanie psov na podujatí používa prívesný vozík s nadstavbou, kde majú psy svoje boxy. Tieto boxy sú dobre tepelne izolované na zimné obdobie, čo ale vytvára riziko prehriatia psa v teplejšom počasí. Teplotu teda treba pravidelne kontrolovať a regulovať otváraním dverí. Teplota v boxe ale nezávisí len od vonkajšieho počasia, zvýši sa napríklad aj keď je pes nervózny, čo majiteľ nedokáže predvídať.

Na pomoc v tejto situácii som teda vytvoril zariadenie ktoré boxy monitoruje elektronicky, pomocou teplotno-vlhkostných senzorov. 
V prípade, že prostredie dosiahne nezdravé hodnoty, upozorní majiteľa zatelefonovaním. 
Meria sa nie len teplota, ale aj vlhkosť, aby sa z týchto veličín odvodila hodnota takzvanej [**pocitovej teploty**](https://en.wikipedia.org/wiki/Heat_index).
Tá je korektnejším ukazovateľom komfortu psieho tela ako len teplota samotná.
<img align="right" src=".doc/hw.png" width="300"/>

* Zariadením je počítač Raspberry Pi, ktorý je uložený v plastovej krabičke spolu s ďalšou potrebnou elektronikou. 
Inštalácia zariadenie je jednoduchá a rýchla. Krabičku stačí vložiť do predripraveného priestoru vo voziku, 
pripojiť kábel napájania senzorov a zapnúť zariadenie stlačením tlačidla. Zariadenie je ďalej už sebestačné a 
ďalšia interakcia s užívateľom prebiaha už len pomocou webovej aplikácie.

* Užívateľ si pomocou aplikácie určí základné nastavenia: 
	1. Interval hodnôt pocitovej teploty ktorý bude považovaný za zdravý
	2. Boxy, ktoré je treba aktuálne monitorovať.

<img align="right" src="/.doc/box.png" width="175"/><img align="right" src="/.doc/inside.png" width="175"/>

* Ak namerana pocitova teplota v niektorom z boxov prekroci stanovene hranice, zariadenie spusti poplach tak, ze uzivatelovi zavola na mobilny telefon. *Tato funkcionalita je k dispozicii vdaka GPRS modulu s vlastnou SIM kartou.*

* Kontrola zdravosti prostredia nie je úplne triviálna. Namerné hodnoty na senzore nemusia stále odpovedať stavu v celom boxe. 
Vietor na senzore, manipulácia s vozíkom, psí dych na senzore a ďalšie vplyvy môžu spôsobiť zavádzajúce výsledky meraní. 
Preto sú merania vyhodnocované algoritmom ktorý pomáha predísť falošným poplachom a, v horšom prípade, prehliadnutiu kritických situácii.

* Zariadenie zasiela informacie o svojom nastaveni na webovu aplikaciu v pravidelnych intervaloch. Vdaka tomu si uzivatel moze kedykolvek pohodlne skontrolovat, že zariadenie funguje a ze je spravne nastavene. Okrem toho, aplikacia zobrazuje dalsie uzitocne informacie, najme aktualne namerane hodnoty v kazdom boxe.

* Počas štandardnej prevádzky nie je k dispozícii pripojenie na elektrickú sieť, preto je zariadenie napájané z vlastnej batérie. Spotreba batérie je nízka a vydrží približne 24 hodín pri neustále zapnutom zariadení. Preteky ale trvajú často dlhšie. Okrem ľahko vymeniteľnej náhradnej batérie je preto k dispozicii funkcia šetrenia batérie. Štandardne, sa kontrola boxov vykoná 12-krát za minútu, čo ale vo väčšine prípadov nie je nevyhnutne potrebné. Túto frekvenciu je preto možné znížiť, a už pri frekvencii 1 kontrola za každé 3 minúty sa zariadenie samé vypína medzi meraniami, čím sa šetrí batéria. *Táto funkcionalita je k dispozicii vdaka modulu WittyPi.*

* Podobným spôsobom je umožnené šetrenie mobilných dát ktoré sú spotrebuvávané pri komunikácii medzi aplikáciou a zariadením. Užívateľ má možnosť frekvenciu tejto komunikácie zmeniť, čím priamo ovplyvňuje spotrebu dát.
<img align="right" src=".doc/screenshot.png" width="180" />

 ## Github Repository
V tomto repository nájdete kód celého projektu:
* [Zariadenie](https://github.com/MarekDrabik/Teplomer/tree/master/Zariadenie) - celý kód Teplomera, teda toho zariadenia ktoré je vložené do prívesného vozíka (Python)
* [Server](https://github.com/MarekDrabik/Teplomer/tree/master/Server) - backend kód servera ktorý beží doma na druhom Raspberry Pi (Node.js) 
* [Server/public](https://github.com/MarekDrabik/Teplomer/tree/master/Server/public) - frontend webová aplikácia (Javascript, html, css)


---
name: enexis-vo-stationsgebieden
description: Ontwerp of verbeter LS-stationsgebieden in DXF/DWG met KLIC, Enexis-WFS, een gekozen kader en een goedgekeurde CAD-referentie. Gebruik bij richtingverdeling, kabelhergebruik, moffen, tracés, overzetters en richting- of trafoberekeningen. Volg Luka's regels en de referentie 011.601 correct zonder projectaantallen naar andere stations te kopiëren.
---

# Enexis VO stationsgebieden

Lees vóór het ontwerpen `docs/universele-info.md`. Lees bij stijlovername of proceskalibratie ook `docs/referentie-011601-correct.md`. Actuele opdrachten en expliciete gebruikerscorrecties gaan voor op oudere voorbeelden.

## Werkvolgorde

1. Inventariseer bronnen, eenheden, kader, stationuitrusting, rode grens, aansluitingencategorieën en buurstations. Bewaar bronbestanden. Bij lege buurgebieden hun haalbaarheid bewaken; bij uitgewerkte buren voedingen en scheidingen respecteren. Neem de goedgekeurde stijlreferentie als er geen uitgewerkte buren zijn.
2. Reconstrueer aansluitregister en bestaande structuur: WFS `service_connection → conn_cable → map_cable`, met code én onderbouwde verbinding. Filter `omschrijving`: LS en LS/OV opnemen, uitsluitend OV uitsluiten. KLIC-geulentekst geeft kabeltype; geen Al betekent Cu, 50+6 betekent 50Cu+6Cu. `-01` kan ook een zelfstandige stationsrichting met één aansluiting zijn.
3. Onderzoek **eerst herbruikbare stukken en splitsingen**, niet gelijke woninggroepen. Een bestaande hoofdkabel mag over onafhankelijke richtingen worden verdeeld. Ontwerp echte scheidingen, registreer per deel alle aansluitingen, voeding en achterblijvende delen. Iedere aansluiting eenmaal; geen onbedoelde koppeling tussen richtingen.
4. Kies samenhangende richtingen en een gezamenlijke gleuf. Moffen mogen op ieder geschikt punt van bestaande hoofdkabels, ook midden op een WFS-object. Benut dit tegen kruisingen en afzonderlijke sleuven. Nieuwe LS standaard 150Al; alleen noodzakelijke verbinding met bestaande combikabel rechtvaardigt 150Al+. OV heeft een aparte tekening.
5. Ontwerp de bundel **in of langs de stoep**, ook direct bij het station. Gras, pleinen en tegels mogen; boom-/beplantingsstroken niet als gras behandelen. Controleer projecttopografie, BGT-boompunten én vegetatievlakken en bekende beschermingszones. Rechte segmenten tussen noodzakelijke bochten, 0,20 m offset tussen richtingen, geen kruisingen of rastertrapjes. Minimaliseer rechte, gezamenlijke wegoversteken. Bewaak bundelvolgorde tot moffen en uiteinden. Controleer percelen én eigendom/beheer; openbare toegankelijkheid of BGT bewijst geen overheidsgrond.
6. Bereken ieder station→hoofd-/aftakeindpad apart. Gemeenschappelijk stuk eenmaal per pad; zijtakken niet achter elkaar optellen. De **laagste maximaal toegestane afzekering** begrenst de hele richting; alle belastingen eenmaal. Ook een korter pad met dunnere kabel kan maatgevend zijn. Huisaansluitkabels alleen voor koppeling en belasting, nooit als richtinglengte/tak of aanleiding voor een eindmof.
7. Kies het belastingprofiel uit onderbouwde aansluitverdeling of expliciete kaderinvoer. Referentie R2/R3/R11: evenredig; R4/R5/R9/R10: laatste helft. Geen universeel profiel hieruit afleiden. Bij onbekende verdeling beide profielen tonen en onderbouwen.
8. Reken eerst tot het fysieke hoofdkabeluiteinde. Als dat niet past, toets tot de **laatste aansluiting op ieder betrokken hoofdkabel-/aftakpad**, langs de hoofdkabel tot haar aansluitpunt. Huisaansluitkabel niet meerekenen. Houd alle toegewezen aansluitingen en belasting. Bewaar beide varianten. Een korter rekeneinde verplaatst geen fysieke eindmof en verwijdert geen kabelstaart. Herverdeel, splits of vervang beperkende stukken als ook dit niet past.
9. Vertaal elke aansluiting via haar categorie naar afzonderlijke kabel- en trafowaarden van hetzelfde kader. Verbruik/opwek apart, daarna hoogste totaal. Trafolimiet = kVA/0,23/3, ongerond vergelijken. Geen algemene omrekenfactor of som van richtingszekeringen.
10. Teken moffen, behouden stukken, labels en RT-overzicht uit de gecontroleerde structuur. Overzetter alleen als een aansluiting op een **nieuwe kabel** komt; niet bij behoud op haar oorspronkelijke kabel met nieuwe voeding. Neem laagkleuren, blokken, tekststijl en labelopbouw uit de referentie. Eén logische nieuwe polyline per kabelroute; decoratieve lijnopbouw niet als extra elektrische lengte tellen.
11. Vergelijk totaalplan én stationsdetail met de referentie. Controleer aansluitingen, alle paden/materialen, scheidingen, bundelruimte, kruisingen, bomen, grondpositie, labels en rekenlengtes. Lever tekening met controleblad en bronregister; benoem ontbrekende controles concreet.

## Rekenhulpmiddel en grenzen

`scripts/reken_richtingen.py` controleert een **expliciete** netstructuur voor kader 2024. Het reconstrueert geen verbindingen uit nabijheid, ontwerpt geen tracé en controleert geen eigendom of CAD-moffen. Gevalideerde catalogus: 150Al, 95Al, 50Al, 50Cu. Andere types vereisen aanvullende gecontroleerde bronwaarden. De JSON-referentie herberekent gekozen kaderpaden; zij bewijst niet dat alle mogelijke DXF-paden automatisch zijn gevonden.

Uitvoeren: `python scripts/reken_richtingen.py references/011601-correct.json --output controle.json`.
Toetsen: `python scripts/test_reken_richtingen.py`.

Zeven richtingen, 78 overzetters en RT1/RT12 met 80A Tamp zijn kenmerken van 011.601, geen algemene aantallen of voorschriften.

Gebruik `last_connection_paths` alleen met volledige, ongewijzigde aansluitingstoewijzing: `connection_ids` en `last_connection_coverage`. Bewaar fysieke uiteinden en moffen apart. Rapporteer een tekort als onvoldoende.

De oude lokale `.analysis/finalize_station.py` maakt de achterhaalde acht-richtingenvariant met vrijwel alles nieuw. Alleen gebruiken voor expliciete historische reproductie; niet voor nieuwe ontwerpen.

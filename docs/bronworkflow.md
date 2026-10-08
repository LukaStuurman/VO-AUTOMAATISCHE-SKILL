# Bronontwerp en herhaalbare vergelijking

Begin met originele CAD, dezelfde RD-coördinaten/eenheden, KLIC/WFS, BGT/topografie en kader. Gebruik het zichtbare stationsblok, rode grens en oorspronkelijke stroomrondjes. Feitcorrecties bewaren locatie, categorie, bron en geplande/bestaande status; routes of gewenste zekeringen zijn geen broncorrecties.

## Invoer en uitvoering

Een JSON bevat `station_id`, `kader`, `kva`, `base_dxf`, `klic_dxf`, `topo_dxf`, `boundary_handle`, `station_handle`, `network_prefix`, `wfs_map`, `wfs_conn`, `wfs_service`, `bgt`, `direction_slots`, `special_slots`, `source_corrections`, `connection_categories`, `parcels_geojson`, `rules` en `solution_paths_to_block`. Speciale slots komen uit stationsuitrusting. De laatste sleutel blokkeert oplossingsbestanden/mappen tijdens genereren.

`bgt`: snapshots van wegdeel, begroeidterreindeel, vegetatieobject_punt, vegetatieobject_vlak, pand en onbegroeidterreindeel. Controleer actieve objecten en volledige selectie. Topografie levert boom-symbolen en conservatief vermeden onverklaarde gesloten ronde contouren; dat zijn geen bewezen wortelzones. BRK-percelen geven geometrie, geen eigendom. Bewaar eigendoms-/beheerbewijs apart.

`source_corrections`: `source_circle_handle`, `xy`, `cable_current_A`, `category`, `planned_connection`, `provenance`. `connection_categories` koppelt rondjeshandles aan categorienamen bij ambiguïteit. De 2024-categorietabel komt uit het oningevulde kader, niet de gebruikersoplossing. Collectieve warmtepomp/type-5-toeslagen vragen aanvullende kaderinvoer.

Routekosten, raster, profielcriteria en vereenvoudiging zijn expliciete zoekafwegingen. Offset is 0.20 m. Boomlichaam/routingmarge zijn numerieke instellingen, geen verzonnen wettelijke wortelafstand. Een gezamenlijke route wordt eenmaal als graafwerk gewaardeerd. Selecteer op capaciteit, gezamenlijke sleuf en gecontroleerde geometrie; wijzig geen kosten om verborgen voorbeeldpunten te treffen.

Bij een correctie op een bestaand ontwerp kan `rules.refinement_scope` de door de gebruiker aangewezen richtingen voor `straight_frontage` en `earlier_joint` bevatten. De algemene corridorregel zoekt voldoende ruimte en rechte lijnstukken, zonder onnodig naar erf te verschuiven. `straight_frontage_clearance_m` is een numerieke ontwerpmarge. Zie [eindmoffen, bomenrijen en doorgaande mofaanloop](correcties-06-10-2026.md). Een ongewijzigde bestaande eindmof wordt herkend uit oorspronkelijke kabelgeometrie én KLIC; vervallen ontwerp-mof/tekst/conceptlijn worden als samenhangende wijziging opgeruimd.

Benodigd: Python met ezdxf, shapely, numpy, scipy en matplotlib.

De oplevering bevat daarnaast verplicht de ingevulde officiële kader-Excel, per richting en met gezamenlijk trafoblad. Volg [kader-Excel invullen](kader-excel.md) voor de bronbestanden in Enexis Kabelchecker, de verschillende bladindelingen, afzonderlijke aftakcontroles en de vergelijking met het definitieve ontwerp. De bronpipeline genereert deze `.xlsx` nog niet zelf; voer dit onderdeel aanvullend uit voordat je de volledige opdracht als afgerond meldt.

## Een eigen bronkandidaat corrigeren

Gebruik `herzie_bronontwerp.py vorige-kandidaat.json broninvoer.json --output resultaat` voor een gerichte tracé-/symboolcorrectie op een eigen eerder uit bronnen gemaakte kandidaat. De aansluitinventaris moet gelijk zijn; groepen en bestaande voedingen blijven behouden. Een uitgewerkte gebruikersoplossing of referentiegestuurde reconstructie is niet toegestaan als vorige kandidaat. Dit is een revisie, geen nieuwe onafhankelijke ontwerptest vanaf nul.

De revisie onderzoekt de daadwerkelijk getekende erfdoorsnijding, ook als de oorspronkelijke middenlijn nog op de stoep lag. Het herstelde gezamenlijke tracé wordt opnieuw doorgerekend en teruggelezen. Moflocaties zijn beschermde contactpunten tijdens bundelherstel. Houd de bestaande stationsuitloop stabiel wanneer een lokale stoepaanloop langer/korter wordt.

`rules.bundle_erf_margin_m` reserveert zoekruimte aan de erfzijde voor de bundel. `rules.drawing_stoep_tolerance_m` is beperkte grafische ruimte buiten de BGT-voetpadstrook bij krapte; standaard 0. Voor de beoordeelde correctie is 0,20 m als werkwaarde gebruikt. Dit is geen toegestane fysieke afstand in een tuin en geen versoepeling voor bomen. De fysieke zoekroute houdt erf uitgesloten. Een kleine tekenoverschrijding bij de stoep kan daardoor worden geaccepteerd zonder een grote omweg af te dwingen.

Het stijlbestand bevat `BESTAANDE MOF` uitsluitend voor bronmatig reeds aanwezige moffen, met **Bestaand** ernaast. Nieuwe knip-/eindlocaties op oude kabel zijn `NIEUWE MOF`. Nieuwe VM/AM-verbindingen gebruiken het bestaand-nieuw-blok. Controleer dat de mof alle aangesloten kabels raakt en dat een VM geen ongebruikte arm houdt.

```text
python scripts/ontwerp_uit_bronnen.py broninvoer.json --output resultaat
python scripts/test_reken_richtingen.py
python scripts/test_autonomous_rules.py
```

`--dependency-path` kan herhaald worden voor bestaande bibliotheken. Uitvoer: DXF, previews, aansluitregister, bron-/scripthashes, deelverwijderregister en controleblad. Bekijk beelden én CAD. Onvoldoende bronnen/complexere situaties worden als ontbrekend ontwerpwerk behandeld, niet als toestemming om verbindingen te raden.

De modules scheiden broninventarisatie, terreinroutes, richtingkeuze, gezamenlijke lijnopbouw, padberekening, verwijdering en nacontrole. De stijlset bevat lokale symbolen/lege attributen; zij werkt zonder ingevulde buurgebieden. Nieuwe-behouden kabelintersecties, oorspronkelijke voedingen, eigendom, wortelzones en bronconflicten vragen afzonderlijke beoordeling. Een positieve kabelberekening bewijst geen uitvoeringsgereedheid.

## Vergelijken achteraf

Een afzonderlijke evaluator leest de opgeslagen kandidaat en de gebruikersoplossing. Vergelijk aansluit-ID's, zekeringen, behouden delen, overzetters en de werkelijk opgeslagen polylines. Meet corridorovereenkomst in beide richtingen met verklaarde tolerantie. Bewaar ook mislukte kandidaten en de algemene regelwijzigingen. Een kalibratie op hetzelfde station bewijst reproduceerbaarheid uit bronnen; test vervolgens een ander station voordat je algemene nauwkeurigheid claimt.

## Bronafwijkingen en materiaalstukken

Een verschoven rondje blijft alleen automatisch gekoppeld wanneer rondje en WFS-servicepunt binnen hetzelfde actieve BGT-pand vallen en de aansluitkabel met dezelfde code werkelijk op de LS-hoofdkabel aansluit. Bewaar de bewijs-ID's. Afstand alleen is onvoldoende. Leg nieuwe geplande aansluitingen zonder bestaand WFS-servicepunt vast als expliciete projectinvoer met categorie en locatie.

Eén hoofdkabelcode kan LS- en LS/OV-delen met verschillende materialen hebben. Koppel KLIC-labels aan de afzonderlijke WFS-lijnstukken met overeenkomende functie; toets tegenstrijdige labels en volledige lengtedekking. Bereken 35Cu-aftakken en andere behouden materiaalstukken afzonderlijk per elektrisch pad. Bepaal `150Al+` uit het behouden combideel aan het echte nieuwe mofcontact. Een combideel elders op dezelfde code maakt de nieuwe aanloop niet automatisch een combikabel. Werkelijke tussengelegen bronmoffen blijven zichtbaar; teken geen bestaande mof uitsluitend omdat twee WFS-records of materiaalintervallen elkaar raken.

Splits een broninterval opnieuw bij berekende capaciteitsproblemen, met alle oorspronkelijke aansluitingen eenmaal en beschikbare stationsposities als grens. Kies scheidingen uit de aansluitingstopologie; gewenste voorbeeldzekeringen zijn geen invoer. Geometrische herstelstappen mogen niet terugschieten door een beschermde stationsuitloop. Controleer de native objecten uit de lege tekening en de ongewijzigde xrefs na opslaan, inclusief kabelkruisingen met de aangrenzende stations.

## Lange rechte bundels en mofcorrecties

Maak de mofinventaris vóór het verwijderen van ongebruikte aftakken. `vo_kabelafwerking.py` behoudt een bewezen bron-aftakmof met Bestaand, tekent een kort afgedopt stuk en een nieuwe eindmof, en weigert dit als een andere richting het aftakdeel gebruikt of een aansluiting erop achterblijft. Controleer ook het kabeluiteinde aan de andere zijde van iedere scheiding, inclusief een buurgebied. Knippen en verwijderen betreft uitsluitend eigen kabelobjecten in de hoofdtekening. Externe referenties en hun koppelingen blijven intact.

`rules.splice_after_crossing` wijst richtingen aan waarvan de AM veilig naar het eerste broncontact na een haakse oversteek kan. De helper ontleent die positie aan het eigen tracé en de oorspronkelijke hoofdkabel, bewaakt dezelfde belasting en herberekent de paden. Als geen veilig contact bestaat, beoordeel de corridor; vul geen voorbeeldcoördinaten in. De standaard kabelafwerking zet bestaand/nieuw op global width 0,1 en nieuw op DASHED met entity linetype scale 0,0035. De controle leest mofsymbolen, bronstatus, contactsituatie en kabelstijl terug uit het echte resultaat.

`verfijn_opgeslagen_vo.py vorige-kandidaat.json broninvoer.json --output resultaat --straight <richtinggroepen>` herziet een eigen bronkandidaat. Geef de richtingen op die dezelfde straat/bomenrij volgen; geen voorbeeldcoördinaten of gewenste zekeringen. Alle betrokken kabels krijgen één rechte corridor en vaste lanevolgorde. Echte oversteken worden opnieuw haaks gemaakt. `rules.straight_bundle_groups` kan dezelfde groepen in de bronmaker aanwijzen.

Mofcontacten worden naar het echte snijpunt gebracht; op een VM wordt het behouden interval op de mof afgekapt. Externe referenties blijven volledig intact en gekoppeld aan hun oorspronkelijke bron; er wordt geen bewerkte KLIC-projectkopie aangemaakt of gekoppeld. Alleen eigen kabelobjecten in de hoofdtekening worden geknipt of gestileerd. Nieuwe eindmoffen en hun EM-teksten krijgen de laag van de betrokken richting, inclusief de achterblijvende zijde bij een buurgebied.

## Aansluitbereik en vaste gedeelde offsets

Voor een twaalfpositiesstation gebruikt `vo_stationsuitloop.py` het werkelijke frontvlak van het CAD-blok. Dit voorkomt een schuine uitloop uit het verkeerde blok-insertpunt. Fysieke nummerposities liggen op 0,20 m afstand; de bezettingsvolgorde is 2, 11, 3, 10, 4, 9, 5, 8, 6, 7. Richting 1/12 krijgt elk circa 5 m tamp met eindmof. De poort-, bank- en tampcontrole leest de opgeslagen CAD terug. De korte haakse vertrekstukken en bankovergang worden beschermd bij verdere tracéverfijning.

`vo_gedeelde_oversteek.py` herkent nabijgelegen oversteken op dezelfde lokale rijbaan. Kies één oversteek voor de hele betrokken bundel en vertak pas aan de overzijde via een toegestane, boomvrije voetpadcorridor. Behoud 0,20 m afstand en dezelfde haakse wegas; toets de echte bundelbreedte en voorkom een tweede rijbaankruising door de connector. Pas stationsuitloop pas na deze gezamenlijke opbouw toe, daarna herberekenen en CAD teruglezen. Tampen krijgen geen aansluiting of extra trafobelasting.

`vo_annotaties.py` plaatst overzetters achter de stroombollen, van het kabelcontact af. Het standaard centrum ligt 2,6 m achter de bol; wijzig het via `rules.overzetter_circle_offset_m` als de tekenruimte dit vraagt. De bollen en kabels worden hiervoor niet verschoven. Leg de koppeling aansluiting-ID → blokhandle vast. Voor richtinginformatie bepaalt de helper de eerste aansluiting langs de voeding: nieuwe main of aanloop naar de mof plus behouden hoofd-/aftakpad. Zet ampèretotaal en rekenlengte samen naast die bol en kies leesruimte tussen aanwezige annotaties. Lees deze grafische plaatsing terug uit de opgeslagen CAD.

`extend_past_last_connection` controleert oorspronkelijke taplocaties langs het eindsegment, zonder ze op het bestaande uiteinde af te klemmen. Een nieuwe hoofdkabel loopt net voorbij de laatste aansluitkabel; de standaard tekenruimte is 0,6 m, zonder een stationsspecifieke eindpositie vast te leggen. Controleer service-/gedeelde aansluitkabels en de eindmof, herprojecteer taps op de aangepaste lijn en reken alle paden opnieuw.

`vo_gedeelde_offsets.py` bouwt de gedeelde lijnen uit één referentielijn met vaste lanevolgorde en 0,20 m offset, inclusief de hoekverbindingen. Controleer de opgeslagen geometrie tegen de offsetcurve. Verander na deze opbouw geen bocht of oversteek onafhankelijk per richting; toets de hele bundel tegen terrein, oversteken, andere kabels en mofcontacten. `rules.straight_frontage_house_side` kiest binnen deze voorwaarden een lange rechte stoepcorridor dichter bij de huizen; het is geen toestemming om door tuinen te gaan.

Pas na `vo_annotaties.py` de tekstafwerking met `vo_tekst_en_draworder.py` toe. Bepaal kabelteksthoeken uit lokale rechte stukken. Plaats bundelteksten gezamenlijk, met minstens 1,5 m regelafstand bij de standaard teksthoogten; volg hun geometrische lanevolgorde en houd echte tekstvlakken vrij van kabels en andere annotaties. EM/AM/VM/Bestaand blijft bij de juiste mof en op de juiste laag. Registreer teksthandle → kabelstuk of mofhandle. Toets zichtbare tekstafstand tot de mof in plaats van uitsluitend het insertpunt: een links geplaatste tekst kan rechts vlak naast de mof eindigen. Zet alle host-mofblokken bovenaan ACAD_SORTENTS, activeer regeneratie-/plotvolgorde en controleer dit na opslaan en teruglezen. Wijzig hiervoor geen xref-inhoud, bronpad, kabelgeometrie of symbolen. Bekijk het stationsdetail en minimaal één gebogen bestaande kabel en één stapel parallelle kabelteksten.

Werk vóór de tekstafwerking het eigen afzekeringsblok af met `vo_afzekeringsblok.py`. Maak een private blokkopie, zet de twaalf rondjes exact op één verticale as en lijn de attributen ernaast uit. Bepaal plusjes uit aanwezige ampère-afzekering in de attributen, ook voor tampen; vrije velden blijven leeg. De twee pluslijnen gebruiken de rondjeslaag en zijn horizontaal/verticaal gecentreerd. Meet de totale werkelijke blok- én attributentekstextents en voeg daarachter één wipeout met marge toe. Geef de wipeout de eerste interne redraw-positie, rondjes/plusjes daarna. Controleer na opslaan/teruglezen de kolom, plusjes, lagen en dekking van ieder attribuut, ook de langste tekst. Bekijk het afzekeringsblok apart.

Voor de plusjes gebruiken beide lijnhelften de volledige cirkelstraal. De vier eindpunten moeten op de omtrek liggen; de controle weigert kortere lijnen binnen de cirkel.

## Herstellen uit de eigen controle

Een geplande aansluiting zonder WFS-servicepunt hoeft niet naar een nieuwe hoofdkabel. `vo_geplande_aansluitingen.py` vergelijkt alle actieve nieuwe en behouden hoofdkabels en kiest een dichtbijgelegen contact dat met de extra belasting past. Bewaar de nieuwe service als gepland, met eigen locatie, gekozen hoofdcode/contact en aansluitafstand; maak geen fictief WFS-servicepunt of bestaande aansluitkabel. Een koppeling op behouden hoofdtracé krijgt geen overzetter. Neem kabelverbruik en kabelopwek afzonderlijk in de capaciteitstoets mee. De geplande serviceleiding telt niet als hoofdkabel-rekenlengte.

Gebruik uitsluitend de eigen opgeslagen bronkandidaat en dezelfde oorspronkelijke bronnen. Kies de betrokken richtingen uit echte fouten in het controleblad; richtingnummers, mofposities of groepsaantallen uit een uitgewerkte doeltekening zijn geen herstelinput.

Een nieuwe aanloop die een behouden hoofdkabel kruist vraagt eerst een topologische keuze. `vo_herverdeel_bestaand.py` onderzoekt een aansluitingsvrije scheidingsopening en overdracht naar een aangrenzende behouden voeding. Aansluitingen die op dezelfde fysieke kabel blijven krijgen geen overzetter. Bescherm ook WFS-aansluitingen buiten de eigen groep, andere stations en actieve OV; verwijder geen beschermd stuk om een geometriecontrole te laten slagen. Herbereken ontvangende én afgevende richting en het deelverwijderregister.

`vo_andere_mofaanloop.py` onderzoekt voeding vanaf de andere zijde van hetzelfde gebruikte kabeldeel. Een kortere aanloop is alleen bruikbaar als hij alle aansluitingen en behouden paden blijft voeden en geen nieuwe conflicten maakt. Leg de nieuwe voedingszijde vast en bepaal daarna de richtingvolgorde opnieuw uit de volledige elektrische route.

`vo_aanloop_herstel.py` biedt gerichte geometrische herstelkeuzes. `public_feeder_tail` zoekt een openbare omloop rond een beschermd bestaand kabeluiteinde. `shared_feeder` bouwt een parallelle aanloop uit één eigen referentierichting en vertakt pas voor de eigen mof. `pavement_corner` vereenvoudigt/verplaatst alle betrokken lanes samen op een door de eigen controle gevonden stoepbocht. Gebruik de terreinobstakels, toegestane oppervlakken en echte behouden kabels als grenzen. Deze functies wijzigen geen aansluitingstoewijzing en accepteren een aanloop alleen met een nieuwe kabelberekening. Voer daarna altijd de volledige opgeslagen-CAD-controle uit; een lokale verbetering kan elders een fout veroorzaken.

Bewaar voldoende ruimte voor de **hele** bundel: een boomvrije binnenste kabel bewijst niet dat de 0,20 m offsetkabel ook boomvrij is. Gebruik bij een buitenste kabelconflict een grotere corridorafstand voor de referentielijn, bouw opnieuw de gezamenlijke offsets en toets opnieuw. Verplaats niet alleen de buitenste kabel met losse knikken.

Bij haaks maken kan een rechte verbinding op de overzijde een tuin of boomcontour raken. `perpendicular_crossings` kan met expliciete `surfaces` een boomvrije voetpadverbinding voor en na de rechte rijbaanpassage zoeken. Werk daarna de andere lanes uit dezelfde oversteekas bij. Een contact uitsluitend **op** de geometrische rijbaangrens is geen passage door de rijbaan; de controle sluit alleen numerieke grenscoïncidentie op micrometerniveau uit. Schuine passages door het wegvlak blijven afgekeurd.

Bij een nieuwe voeding op een behouden kabel komt de mof op het eerste bruikbare echte contact als alle eigen hoofd-/aftaklasten aan de behouden zijde liggen. Laat de nieuwe kabel niet door die bronkabel kruisen en teruglopen naar een voorlopige mof verderop. `align_splice_contacts` stopt daar, knipt uitsluitend de ongebruikte eigen arm en bepaalt opnieuw VM/AM.

Voor ontbrekende BGT-dekking bij het stationsfront is een expliciet onderbouwd projectfeit nodig. Bewaar bevestigde open grond met locatie en herkomst in `source_station_access`; maak niet automatisch alle onbekende grond vrij. Bekende bomen, tuinen en panden blijven obstakels.

Een eigen checkpoint na een offsetbewerking wordt met de **actuele** geometrie hervat. Bewaar de fase vóór de bewerking apart, verwijder het fasekenmerk na uitvoering en synchroniseer `display_main` vóór de stationsuitloop. Lees opgeslagen hoofdkabels via hun eigen gegenereerde handles terug; een afstandsfilter rond het blok-insertpunt kan geldige fysieke buitenpoorten missen. Bronbollen, native buurontwerpen en xrefs blijven gelijk.

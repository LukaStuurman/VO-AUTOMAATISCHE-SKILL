# Bronontwerp en herhaalbare vergelijking

Begin met originele CAD, dezelfde RD-coördinaten/eenheden, KLIC/WFS, BGT/topografie en kader. Gebruik het zichtbare stationsblok, rode grens en oorspronkelijke stroomrondjes. Feitcorrecties bewaren locatie, categorie, bron en geplande/bestaande status; routes of gewenste zekeringen zijn geen broncorrecties.

## Invoer en uitvoering

Een JSON bevat `station_id`, `kader`, `kva`, `base_dxf`, `klic_dxf`, `topo_dxf`, `boundary_handle`, `station_handle`, `network_prefix`, `wfs_map`, `wfs_conn`, `wfs_service`, `bgt`, `direction_slots`, `special_slots`, `source_corrections`, `connection_categories`, `parcels_geojson`, `rules` en `solution_paths_to_block`. Speciale slots komen uit stationsuitrusting. De laatste sleutel blokkeert oplossingsbestanden/mappen tijdens genereren.

`bgt`: snapshots van wegdeel, begroeidterreindeel, vegetatieobject_punt, vegetatieobject_vlak, pand en onbegroeidterreindeel. Controleer actieve objecten en volledige selectie. Topografie levert boom-symbolen en conservatief vermeden onverklaarde gesloten ronde contouren; dat zijn geen bewezen wortelzones. BRK-percelen geven geometrie, geen eigendom. Bewaar eigendoms-/beheerbewijs apart.

`source_corrections`: `source_circle_handle`, `xy`, `cable_current_A`, `category`, `planned_connection`, `provenance`. `connection_categories` koppelt rondjeshandles aan categorienamen bij ambiguïteit. De 2024-categorietabel komt uit het oningevulde kader, niet de gebruikersoplossing. Collectieve warmtepomp/type-5-toeslagen vragen aanvullende kaderinvoer.

Routekosten, raster, profielcriteria en vereenvoudiging zijn expliciete zoekafwegingen. Offset is 0.20 m. Boomlichaam/routingmarge zijn numerieke instellingen, geen verzonnen wettelijke wortelafstand. Een gezamenlijke route wordt eenmaal als graafwerk gewaardeerd. Selecteer op capaciteit, gezamenlijke sleuf en gecontroleerde geometrie; wijzig geen kosten om verborgen voorbeeldpunten te treffen.

Bij een correctie op een bestaand ontwerp kan `rules.refinement_scope` de door de gebruiker aangewezen richtingen voor `straight_frontage` en `earlier_joint` bevatten. De algemene corridorregel zoekt voldoende ruimte en rechte lijnstukken, zonder onnodig naar erf te verschuiven. `straight_frontage_clearance_m` is een numerieke ontwerpmarge. Zie [eindmoffen, bomenrijen en doorgaande mofaanloop](correcties-06-10-2026.md). Een ongewijzigde bestaande eindmof wordt herkend uit oorspronkelijke kabelgeometrie én KLIC; vervallen ontwerp-mof/tekst/conceptlijn worden als samenhangende wijziging opgeruimd.

Benodigd: Python met ezdxf, shapely, numpy, scipy en matplotlib.

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

## Lange rechte bundels en mofcorrecties

Maak de mofinventaris vóór het verwijderen van ongebruikte aftakken. `vo_kabelafwerking.py` behoudt een bewezen bron-aftakmof met Bestaand, tekent een kort afgedopt stuk en een nieuwe eindmof, en weigert dit als een andere richting het aftakdeel gebruikt of een aansluiting erop achterblijft. Controleer ook het kabeluiteinde aan de andere zijde van iedere scheiding, inclusief een buurgebied. Knippen en verwijderen betreft uitsluitend eigen kabelobjecten in de hoofdtekening. Externe referenties en hun koppelingen blijven intact.

`rules.splice_after_crossing` wijst richtingen aan waarvan de AM veilig naar het eerste broncontact na een haakse oversteek kan. De helper ontleent die positie aan het eigen tracé en de oorspronkelijke hoofdkabel, bewaakt dezelfde belasting en herberekent de paden. Als geen veilig contact bestaat, beoordeel de corridor; vul geen voorbeeldcoördinaten in. De standaard kabelafwerking zet bestaand/nieuw op global width 0,1 en nieuw op DASHED met entity linetype scale 0,0035. De controle leest mofsymbolen, bronstatus, contactsituatie en kabelstijl terug uit het echte resultaat.

`verfijn_opgeslagen_vo.py vorige-kandidaat.json broninvoer.json --output resultaat --straight <richtinggroepen>` herziet een eigen bronkandidaat. Geef de richtingen op die dezelfde straat/bomenrij volgen; geen voorbeeldcoördinaten of gewenste zekeringen. Alle betrokken kabels krijgen één rechte corridor en vaste lanevolgorde. Echte oversteken worden opnieuw haaks gemaakt. `rules.straight_bundle_groups` kan dezelfde groepen in de bronmaker aanwijzen.

Mofcontacten worden naar het echte snijpunt gebracht; op een VM wordt het behouden interval op de mof afgekapt. Externe referenties blijven volledig intact en gekoppeld aan hun oorspronkelijke bron; er wordt geen bewerkte KLIC-projectkopie aangemaakt of gekoppeld. Alleen eigen kabelobjecten in de hoofdtekening worden geknipt of gestileerd. Nieuwe eindmoffen en hun EM-teksten krijgen de laag van de betrokken richting, inclusief de achterblijvende zijde bij een buurgebied.

## Aansluitbereik en vaste gedeelde offsets

`extend_past_last_connection` controleert oorspronkelijke taplocaties langs het eindsegment, zonder ze op het bestaande uiteinde af te klemmen. Een nieuwe hoofdkabel loopt net voorbij de laatste aansluitkabel; de standaard tekenruimte is 0,6 m, zonder een stationsspecifieke eindpositie vast te leggen. Controleer service-/gedeelde aansluitkabels en de eindmof, herprojecteer taps op de aangepaste lijn en reken alle paden opnieuw.

`vo_gedeelde_offsets.py` bouwt de gedeelde lijnen uit één referentielijn met vaste lanevolgorde en 0,20 m offset, inclusief de hoekverbindingen. Controleer de opgeslagen geometrie tegen de offsetcurve. Verander na deze opbouw geen bocht of oversteek onafhankelijk per richting; toets de hele bundel tegen terrein, oversteken, andere kabels en mofcontacten. `rules.straight_frontage_house_side` kiest binnen deze voorwaarden een lange rechte stoepcorridor dichter bij de huizen; het is geen toestemming om door tuinen te gaan.

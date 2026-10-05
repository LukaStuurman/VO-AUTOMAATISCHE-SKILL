# Bronontwerp en herhaalbare vergelijking

Begin met originele CAD, dezelfde RD-coördinaten/eenheden, KLIC/WFS, BGT/topografie en kader. Gebruik het zichtbare stationsblok, rode grens en oorspronkelijke stroomrondjes. Feitcorrecties bewaren locatie, categorie, bron en geplande/bestaande status; routes of gewenste zekeringen zijn geen broncorrecties.

## Invoer en uitvoering

Een JSON bevat `station_id`, `kader`, `kva`, `base_dxf`, `klic_dxf`, `topo_dxf`, `boundary_handle`, `station_handle`, `network_prefix`, `wfs_map`, `wfs_conn`, `wfs_service`, `bgt`, `direction_slots`, `special_slots`, `source_corrections`, `connection_categories`, `parcels_geojson`, `rules` en `solution_paths_to_block`. Speciale slots komen uit stationsuitrusting. De laatste sleutel blokkeert oplossingsbestanden/mappen tijdens genereren.

`bgt`: snapshots van wegdeel, begroeidterreindeel, vegetatieobject_punt, vegetatieobject_vlak, pand en onbegroeidterreindeel. Controleer actieve objecten en volledige selectie. Topografie levert boom-symbolen en conservatief vermeden onverklaarde gesloten ronde contouren; dat zijn geen bewezen wortelzones. BRK-percelen geven geometrie, geen eigendom. Bewaar eigendoms-/beheerbewijs apart.

`source_corrections`: `source_circle_handle`, `xy`, `cable_current_A`, `category`, `planned_connection`, `provenance`. `connection_categories` koppelt rondjeshandles aan categorienamen bij ambiguïteit. De 2024-categorietabel komt uit het oningevulde kader, niet de gebruikersoplossing. Collectieve warmtepomp/type-5-toeslagen vragen aanvullende kaderinvoer.

Routekosten, raster, profielcriteria en vereenvoudiging zijn expliciete zoekafwegingen. Offset is 0.20 m. Boomlichaam/routingmarge zijn numerieke instellingen, geen verzonnen wettelijke wortelafstand. Een gezamenlijke route wordt eenmaal als graafwerk gewaardeerd. Selecteer op capaciteit, gezamenlijke sleuf en gecontroleerde geometrie; wijzig geen kosten om verborgen voorbeeldpunten te treffen.

Benodigd: Python met ezdxf, shapely, numpy, scipy en matplotlib.

```text
python scripts/ontwerp_uit_bronnen.py broninvoer.json --output resultaat
python scripts/test_reken_richtingen.py
python scripts/test_autonomous_rules.py
```

`--dependency-path` kan herhaald worden voor bestaande bibliotheken. Uitvoer: DXF, previews, aansluitregister, bron-/scripthashes, deelverwijderregister en controleblad. Bekijk beelden én CAD. Onvoldoende bronnen/complexere situaties worden als ontbrekend ontwerpwerk behandeld, niet als toestemming om verbindingen te raden.

De modules scheiden broninventarisatie, terreinroutes, richtingkeuze, gezamenlijke lijnopbouw, padberekening, verwijdering en nacontrole. De stijlset bevat lokale symbolen/lege attributen; zij werkt zonder ingevulde buurgebieden. Nieuwe-behouden kabelintersecties, oorspronkelijke voedingen, eigendom, wortelzones en bronconflicten vragen afzonderlijke beoordeling. Een positieve kabelberekening bewijst geen uitvoeringsgereedheid.

## Vergelijken achteraf

Een afzonderlijke evaluator leest de opgeslagen kandidaat en de gebruikersoplossing. Vergelijk aansluit-ID's, zekeringen, behouden delen, overzetters en de werkelijk opgeslagen polylines. Meet corridorovereenkomst in beide richtingen met verklaarde tolerantie. Bewaar ook mislukte kandidaten en de algemene regelwijzigingen. Een kalibratie op hetzelfde station bewijst reproduceerbaarheid uit bronnen; test vervolgens een ander station voordat je algemene nauwkeurigheid claimt.

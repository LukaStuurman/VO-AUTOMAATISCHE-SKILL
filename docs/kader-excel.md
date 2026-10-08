# Kader-Excel per richting invullen en opleveren

Bij ieder LS-VO wordt ook de officiële kader-Excel ingevuld voor alle richtingen van het ontworpen station. Dit is een opleverbestand, niet alleen een bron voor een eigen berekening. Een leeg template, aansluitregister of JSON/CSV vervangt deze werkmap niet. Bij meerdere stations krijgt ieder station een herkenbare eigen werkmap.

## Officiële bron en kaderkeuze

De werkmappen staan in [Enexis Kabelchecker — Resources](https://github.com/LukaStuurman/AutoCAD-Enexis-kabels-checker/tree/4009601e15fa4b1b6926380395132b0c1630ce21/src/Enexis.KabelChecker.AutoCAD/Resources). Onderstaande namen en bladstructuren zijn gecontroleerd tegen broncommit `4009601e15fa4b1b6926380395132b0c1630ce21` op 8 oktober 2026. Controleer bij een nieuwe bronversie opnieuw de werkmap en de bijbehorende export-/rekenregels; celadressen zijn geen universele constante.

| Projectkader | Originele werkmap | Richtingbladen | Trafoblad |
| --- | --- | --- | --- |
| 2024 — 1.0 | `Eea-0205.K 1.0 - Copy.xlsx` | Kopie van `Ontwerpstroom_kabel` per richting, met eigen kopie van de toepasselijke `Controle_kabel_evenredig` of `Controle_kabel_laatste_helft` | `Ontwerpstroom_trafo` |
| 2025 — 2.0 | `Eea-0205.K 2.0.xlsx` | Dezelfde werkwijze met de eigen 2.0-rijindeling | `Ontwerpstroom_trafo` |
| 2026 — 3.0 | `Eea-0205.K 3.0.xlsx` | Bestaande bladen `(1)` t/m `(12)` | `Transformator` |
| 2026 — 3.2 | `Eea-0205.K 3.2.xlsx` | Bestaande bladen `(1)` t/m `(12)`, met de eigen 3.2-rijindeling | `Transformator` |

Gebruik het expliciet gekozen projectkader. Kies geen ander kader omdat het kalenderjaar later is of de plugin een andere standaard heeft. Een vermelding van alleen 2026 vereist onderscheid tussen 3.0 en 3.2 uit de projectinvoer; vraag dit na als het ontbreekt. De huidige Python-kabelcatalogus is voor 2024: andere kaders vragen eigen gecontroleerde bronwaarden.

Bewaar repository, commit, bestandsnaam en SHA-256 van het originele `.xlsx`. Maak een projectkopie, bijvoorbeeld `<station> - Kader <versie> - ingevuld.xlsx`; wijzig het originele template niet. Gebruik bij daadwerkelijke werkmapbewerking de spreadsheet-skill.

## Invoer uit het definitieve ontwerp

Gebruik de definitieve richtingtoewijzing en teruggelezen CAD, niet een eerdere kandidaat of de oude uitwerking van het doelstation. Vul per richting:

- Het juiste richtingnummer en de aantallen per oorspronkelijke aansluitcategorie, inclusief bevestigde geplande aansluitingen. Leid categorieën niet af uit alleen een afgeronde ontwerpstroom als meerdere categorieën dezelfde waarde hebben.
- De kabeltypes en meterwaarden van de gecontroleerde elektrische paden: nieuwe aanloop plus gebruikte bestaande hoofd-/aftakstukken, met de werkelijke materialen. Binnen één pad mogen lengtes van hetzelfde kabeltype volgens het template worden samengevoegd; bewaar de afzonderlijke segmenten en hun volgorde in het padregister.
- Het onderbouwde belastingprofiel: evenredig of laatste helft. Gebruik het toepasselijke controleblad of controleblok en de bijbehorende kaderwaarden.
- De berekende ontwerpstroom, gekozen afzekering en maatgevend pad, met een herleidbare relatie naar het richtingoverzicht in de tekening. Gebruik daarvoor invoervelden waar beschikbaar, of een aanvullend overzichtsblad; overschrijf geen resultaatformules om een gewenste uitkomst te tonen.

Stroomrondjes en categorieaantallen blijven leidend voor de aansluitbelasting. Een huisaansluitkabel telt niet mee in de hoofdkabel-rekenlengte. Een tamp krijgt nul aansluitingen en geen extra trafobelasting, maar wel zijn werkelijke kabeltype/lengte en vastgelegde tamp-afzekering in het overzicht. Vrije richtingen blijven leeg of nul volgens het template, zonder voorbeeldbelasting.

### Aftakken en rekeneindpunten

Vul niet alle takken achter elkaar als één seriekabel in. Controleer ieder station → hoofd-/aftakeindpad afzonderlijk, met het gezamenlijke voedingsstuk eenmaal per pad. Toon per richting alle betrokken paduitkomsten en gebruik de **laagste toegestane afzekering** voor de hele richting.

Als één standaard controleblok maar één seriepad kan bevatten, gebruik dat voor het maatgevende pad en voeg herkenbare kopieën van controlebladen/-blokken toe voor de overige paden. Extra padcontroles zijn geen extra richtingen en mogen categorieaantallen niet nogmaals aan het trafoblad toevoegen. Behoud dezelfde toegewezen aansluitingstoewijzing en de voor het ontwerp gehanteerde belastingtoets; wijzig de belasting niet om een Excel-uitkomst te laten passen.

Toets eerst fysieke uiteinden. Als de geaccepteerde berekening tot de laatste aansluiting gaat, vul die rekenlengte in, vermeld het gekozen rekeneindpunt en bewaar ook de fysieke variant. Houd fysieke tekenlengte en rekenlengte apart; verplaats geen eindmof uitsluitend omdat het rekeneinde korter is.

## Gezamenlijk trafoblad

Het trafoblad krijgt de gezamenlijke, unieke aantallen per categorie van alle richtingen. Bij 1.0/2.0 worden deze aantallen op het losse trafoblad ingevuld. Bij 3.0/3.2 blijven de formulekoppelingen naar de twaalf richtingbladen werkzaam; de rijmapping van 3.2 verschilt van 3.0. Voeg bij aanvullende padbladen geen extra stationaantallen toe.

Gebruik de **trafowaarden** van de categorieën, niet de kabelstromen. Tel verbruik en opwek afzonderlijk op. Voor de standaard automatische stroombasis wordt daarna het hoogste kolomtotaal gebruikt; sommeer niet het maximum per aansluiting of de afzonderlijke richtingmaxima. Een expliciet gekozen Verbruik/Opwek-basis blijft herkenbaar, terwijl beide stationtotalen zichtbaar blijven. Toets tegen de ongeronde limiet `kVA / 0,23 / 3`.

## Invullen, herberekenen en controleren

De Kabelchecker heeft een Excel-export voor alle vier kaders. Als die beschikbaar is, sla eerst alle definitieve richtingen op en exporteer met het gekozen kader. Controleer de export alsnog, vooral bij aftakken en afwijkende rekeneindpunten: een export die alle geselecteerde segmenten als één seriepad behandelt, vervangt de afzonderlijke padcontroles niet. Alternatief: vul een kopie van het originele template met spreadsheetgereedschap in volgens dezelfde gecontroleerde indeling.

Behoud formules, opmaak, validaties, categorieomschrijvingen en eenheden. Wis alleen voorbeeldinvoer en oude richtingaantallen/lengtes. Controleer bladroutes en lokale verwijzingen na kopiëren of hernoemen. De bronexport herstelt onder meer de kabeltotaalformule en richting-/trafokoppelingen in 3.2; voer zulke aanpassingen uitsluitend gecontroleerd in de projectkopie uit.

Laat de ingevulde werkmap daadwerkelijk herberekenen. `Automatisch herberekenen bij openen` of het alleen bewaren van formules bewijst geen gecontroleerde uitkomst; gebruik geen oude gecachte voorbeeldresultaten. Lees het opgeslagen `.xlsx` terug en vergelijk:

1. Categorieaantallen en aansluit-ID's: ieder aansluitpunt eenmaal op één richting, het stationtotaal gelijk aan het aansluitregister.
2. Kabeltypes, lengtes per elektrisch pad, profiel en gekozen rekeneindpunt: gelijk aan het definitieve CAD-/padregister.
3. Kabelverbruik/opwek en maatgevende afzekering: gelijk aan de onafhankelijke richtingberekening en het afzekeringsblok.
4. Trafoverbruik/opwek, categorievertaling en kVA-limiet: gelijk aan de stationberekening.
5. Formules en bladroutes: geen `#REF!`, `#VALUE!` of onbedoelde externe verwijzingen; geen achtergebleven voorbeeldbelasting.

Bekijk de ingevulde richtingbladen en het trafoblad op leesbaarheid. Lever de ingevulde `.xlsx` samen met DXF/DWG, previews en controles op en koppel het werkmapbestand en de richting-/padbladnamen aan het opleverregister. Werk de Excel na iedere wijziging van toewijzing, mof, tracé, materiaal, rekenlengte, profiel of afzekering opnieuw bij. Ontbreekt de werkmap of kan herberekening/vergelijking niet worden bevestigd, meld precies welk deel ontbreekt en presenteer de volledige oplevering niet als afgerond.

## Gecontroleerde broncode

- [Kadernamen en templatebestanden](https://github.com/LukaStuurman/AutoCAD-Enexis-kabels-checker/blob/4009601e15fa4b1b6926380395132b0c1630ce21/src/Enexis.KabelChecker.AutoCAD/KaderVersion.cs).
- [Ontwerpstroom per kader: kabel-/trafokolommen en rijmapping](https://github.com/LukaStuurman/AutoCAD-Enexis-kabels-checker/blob/4009601e15fa4b1b6926380395132b0c1630ce21/docs/ontwerpstroom-per-kader.md).
- [Excel-export: richtingkopieën, aantallen, kabeltypes en lengtes](https://github.com/LukaStuurman/AutoCAD-Enexis-kabels-checker/blob/4009601e15fa4b1b6926380395132b0c1630ce21/src/Enexis.KabelChecker.ExcelWorker/ExcelWorker.cs).

De huidige Python-bronpipeline levert zelf nog geen ingevulde kader-Excel. De agent moet deze werkmap aanvullend maken/exporteren en controleren; een geslaagde CAD/JSON-controle geldt niet als bewijs dat dit Excel-onderdeel is uitgevoerd.

---
name: enexis-vo-stationsgebieden
description: Maak of verbeter Enexis LS-VO-stationsgebieden uit oorspronkelijke CAD, KLIC/WFS, BGT en kadergegevens. Gebruik voor hergebruik, splitsingen, gezamenlijke tracés, moffen, overzetters en kabel-/trafoberekeningen. Vergelijk een uitgewerkt doelstation pas achteraf.
---

# LS-VO uit brongegevens

Gebruik Luka's [universele regels](docs/universele-info.md) en [bronworkflow](docs/bronworkflow.md). Een tekenopdracht vraagt een echte DXF/DWG met bekeken overzicht en stationsdetail, aansluitregister en controles. Alleen instructies of berekeningen voldoen niet.

## Ontwerpen vanaf een leeg stationsgebied

De invoer bestaat uit oorspronkelijke CAD, stationsuitrusting/grens, KLIC, WFS, BGT/topografie, perceel-/grondgegevens en kader. Expliciete projectcorrecties zijn apart vastgelegde bronfeiten. Neem geen routes, groepen, moffen, overzetters of zekeringen over uit een uitgewerkt doelstation. Een stijlset bevat uitsluitend lagen, lokale symbolen en tekstconventies.

1. Reconstrueer rondje → WFS-aansluitpunt → aansluitkabel → hoofdkabel/aftak. WFS `omschrijving`: LS en LS/OV opnemen, alleen OV uitsluiten. Code én echte verbinding onderbouwen de koppeling; `-01` kan een zelfstandige stationsrichting zijn. KLIC geeft materiaal: zonder Al betekent Cu; 50+6 is Cu-combi. Registreer onzekerheden.
2. Onderzoek bruikbare bestaande stukken en echte scheidingen vóór vervanging. Verdeel een bestaande kabel zo nodig over meerdere onafhankelijke richtingen. Een mof mag op ieder geschikt punt van een hoofdkabel. Toets nieuwe voeding, behouden hoofd-/aftakpaden en alle belasting samen.
3. Bouw één gezamenlijke gleuf. Richtingen blijven naast elkaar met **0,20 m offset**. Vereenvoudig gedeelde bochten eenmaal. Geen kruisingen, overlappende lijnen of onnodige rastertrapjes. Bij bomenrijen kies je één lang recht gezamenlijk tracé aan dezelfde kant van de bomen; vermijd losse uitwijkingen per boom en blijf bij de stoepstrook; verschuif niet onnodig naar erf. Een eerder rechte wegoversteek kan teruglopen naar een mof voorkomen. Houd de doorgaande kabelrichting bij de mof aan. Voorkeur in/langs stoep; gras, pleinen en tegels mogen. Oversteken recht, zo weinig mogelijk en gezamenlijk.
4. Lees BGT **fysiek_voorkomen én plus_fysiek_voorkomen**. Groenvoorziening met bomen/bos/heesters is geen gras. Controleer boompunten, vegetatievlakken, eigen topo en bekende beschermingszones. Onbekend groen is geen bewezen boomvrije doorgang. Toets de complete bundel na iedere offset/vereenvoudiging. Perceelgeometrie of openbare stoep bewijst geen overheidseigendom.
5. Nieuw LS standaard **150Al**; **150Al+** uitsluitend bij benodigde aansluiting op een behouden combikabel. OV heeft een aparte tekening. Huisaansluitkabels dienen voor koppeling/belasting, niet als richtingtracé of rekenlengte. Geen eindmof per huisaansluiting. Overzetter uitsluitend als de aansluiting op een nieuwe kabel komt.
6. Bereken elk station→hoofd-/aftakeindpad apart met echte materialen. Gedeeld stuk eenmaal per pad; aftakken niet achter elkaar optellen. Laagste maximaal toegestane afzekering geldt voor de hele richting. Alle aansluitingen eenmaal; kabelverbruik/-opwek afzonderlijk. Onderbouw het belastingprofiel uit aansluitverdeling, niet uit voorbeeldrichtingnummers.
7. Toets eerst fysieke uiteinden. Indien onvoldoende: laatste aansluiting op ieder betrokken pad, met dezelfde volledige belasting en vertakkingen. Bewaar beide varianten. Korter rekenen verplaatst geen eindmof.
8. Bepaal na toewijzing van **alle** richtingen de unie van gebruikte delen per bestaande kabeldeel. Alleen ongebruikte delen mogen geknipt/verwijderd worden. Houd geen aansluitingsvrije staart aan een aftakmof zonder benodigde doorvoeding. Bescherm andere richtingen, externe voedingen, onzeker gebruik en actieve OV op combi. Wijzig de oorspronkelijke KLIC/WFS niet.
9. Vertaal categorieën afzonderlijk naar kabel-/trafowaarden. Trafoverbruik en -opwek apart; limiet ongerond **kVA / 0,23 / 3**. Niet-eenduidige stroomwaarden vragen een expliciete categorie.
10. Teken uit de gecontroleerde structuur en lees de CAD terug. Een ongewijzigd bestaand einde met een KLIC-eindmof krijgt geen nieuwe eindmof. Bij vervanging van een fysieke ontwerpeindlocatie verwijder je de oude ontwerp-mof én tekst en werk je de oude conceptlijn bij. Toets opnieuw lengtes/capaciteit, kruisingen, moffen, overzetters, vegetatie, rechte oversteken, grondpositie en leesbaarheid. Herstel mislukkingen; ontbrekende eigendom/wortelzones/bronverbindingen blijven concrete open punten.

Uitgewerkte buren leveren grenzen, bestaande voedingen en stijl. Zonder ingevulde buren gebruik je `assets/cad-stijl.json` en bewaak je haalbaarheid voor overige stations. Kopieer geen aantallen, stationnummers of bijzondere RT-bezetting uit een voorbeeld.

**Wegoversteken zijn altijd haaks:** recht is niet genoeg. De kabel kruist onder **90° ten opzichte van de lokale wegrichting**, afgeleid uit BGT/topografie. Geen schuine oversteek; knikken blijven buiten de rijbaan. Meerdere kabels gebruiken dezelfde plaats en een gezamenlijke lokale wegas, met 0,20 m offset. Toets rechtheid én hoek na alle verschuivingen, ook bij bestaande kruisingsvrije kandidaten.

**Binnen de stoep blijven:** gebruik meestal de BGT-voetpadstrook als leidraad. Controleer alle richtingen na offset, bochten en vereenvoudiging; een veilige middenlijn kan een buitenste kabel nog in een tuin leggen. Bij gebrek aan ruimte mag de getekende bundel iets over de stoepgrens komen, omdat de echte kabels dichter bij elkaar liggen dan de 0,20 m tekenoffset. Dit is beperkte tekenruimte bij een stoeptracé, geen toestemming voor een route door een tuin. BGT-erf is geen vrije strook. Gras, pleinen en geschikte tegels blijven toegestane alternatieven. Voor deze gewone tracékeuze is geen uitgebreide perceelanalyse nodig.

**Mofstatus volgt de werkelijke bron:** alleen een al aanwezige mof krijgt `BESTAANDE MOF` met **Bestaand** ernaast. Een nieuw einde/knippunt krijgt `NIEUWE MOF`, ook op behouden kabel. Nieuwe VM/AM-verbindingen krijgen het bestaand-nieuw-blok. Een VM heeft één behouden arm; knip op de mof en verwijder alleen het ongebruikte deel. Een AM staat op de werkelijke verbinding van alle kabelarmen: toets nieuwe én bestaande kabel tegen de mofpositie. Bescherm ander gebruik en werk ook de projectweergave van oude lijnen/teksten bij. De originele KLIC/WFS blijft intact.

Een bron-aftakmof op een behouden hoofdkabel blijft zichtbaar met **Bestaand**, ook wanneer de aftakkabel wordt vervangen. Dop de ongebruikte aftak direct na die mof af met een nieuwe eindmof; behoud alleen het benodigde korte stuk. Controleer bij een knip ook het achterblijvende uiteinde van het aangrenzende trafogebied en teken daar een nieuwe eindmof. Een geschikte AM komt bij voorkeur direct na de haakse oversteek op het echte bronkabelcontact, zonder onnodige nieuwe kabel langs dezelfde oude kabel. Bereken daarna opnieuw alle paden.

Kabelpolylijnen, bestaand en nieuw, krijgen **global width 0,1**. Nieuwe kabels krijgen expliciet **DASHED** en **linetype scale 0,0035**. Pas dit ook toe op de eigen projectweergave van bestaande kabels. Lees de eigenschappen terug uit de opgeslagen CAD; wijzig geen grenzen, topografie, symbolen of oorspronkelijke bronbestanden om deze kabelstijl toe te passen.

## Hulpmiddelen en grenzen

`scripts/ontwerp_uit_bronnen.py` inventariseert bronnen, maakt een kandidaat, tekent en controleert de opgeslagen geometrie. Alleen gedeclareerde CAD/GIS-bronnen zijn invoer; oplossingspaden kunnen geblokkeerd worden. Bron-/scripthashes en gelezen bronnen worden bewaard. `scripts/reken_richtingen.py` rekent ook losse expliciete structuren.

Automatische kandidaatmaker: getest op Laarbeek-bronnen en een variant zonder getekende buren. Gevalideerde 2024-kabelcatalogus: 150Al, 95Al, 50Al, 50Cu. Andere/materialen binnen één code, complexe lussen, meer dan twee noodzakelijke splitsingen en onvolledige bronnen vragen een gecontroleerde uitbreiding. De workflow is universeel; de generator is nog niet op een tweede onbekend station gevalideerd. Hij bewijst geen eigendom, wortelzones of volledige uitvoeringsgereedheid.

## Vergelijken en verbeteren

Sla eerst een bronkandidaat op. Vergelijk daarna met de gebruikersoplossing: aansluitgroepen, zekeringen, behouden delen, overzetters, echte CAD-routes en vormgeving. Pas algemene beslisregels aan en genereer opnieuw uit dezelfde oorspronkelijke bronnen. Houd de oplossing buiten de generator; hardcode geen voorbeeldcoördinaten, codes, aantallen of gewenste zekeringen. Rapporteer afwijkingen én matches.

Lees [kalibratieverslag](docs/kalibratie-bronontwerp.md) en [historische referentieanalyse](docs/referentie-011601-correct.md) alleen voor vergelijking/kalibratie. Het oude `maak_vo_tekening.py` is een referentiegestuurde reconstructie, geen onafhankelijk bronontwerp en niet de standaard voor een nieuw VO.

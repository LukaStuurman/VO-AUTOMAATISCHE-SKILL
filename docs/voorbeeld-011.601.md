# Plan van aanpak — stationsgebied 011.601

Concept ter beoordeling door Luka · 2 oktober 2026 · Project D.26936, fase 7 · Kader 2024

Dit plan beschrijft hoe het ontbrekende kabelontwerp van 011.601 wordt opgebouwd en gecontroleerd. De oorspronkelijke DXF, DWG en externe referenties zijn niet gewijzigd. De richtingnummers, definitieve hergebruikstukken, nieuwe tracés en afzekeringen worden pas tijdens de ontwerpuitwerking vastgesteld. De algemene werkwijze staat in [Universeel plan van aanpak stationsgebieden](universele-info.md); dit document is de projecttoepassing en het uitgewerkte referentievoorbeeld.

## 1. Wat uit de tekening en bronnen blijkt

Bekeken: de modelgeometrie, lagen, teksten, blokken en gebiedsgrenzen van `VO-LS PILS Laarbeek Beek D.26936 - Fase 7.dxf`; de kabel- en aansluitgeometrie van `04. KLIC/Laarbeek GEN KLIC_ls.dwg`; de topografische referentie; de stations- en richtingvoorbeelden; en de 2024-bronwerkmap en rekenregels uit Enexis Kabelchecker. De twee beschikbare DWG-referenties zijn voor inspectie op kopieën naar DXF geëxporteerd. Aanvullend zijn de Enexis-WFS-laagschema's en een begrensde selectie rond het project gecontroleerd; de bekeken WFS-objecten hebben peildatum 26 september 2026. De definitieve individuele koppeling van alle 125 aansluitingen volgt bij de ontwerpuitwerking.

- Er zijn zes gesloten rode gebiedspolylijnen. Ook rond de aanduiding **Trafo 15-011.601** staat al een grens. De ontbrekende stap is hier vooral de uitwerking van kabelrichtingen, hergebruik, moffen, belastingen en het richtingoverzicht.
- De stationsaanduiding bij 011.601 luidt **Plaatsen Pacto 25 / Trafo 15-011.601 / 12 Richtingen + DALI (630kVA)**. Het stationssymbool is aanwezig.
- Binnen die bestaande grens liggen geometrisch **125 aansluitblokken en 125 ontwerpstroomteksten**: 112 × 7,8 A; 10 × 8,8 A; 2 × 10,3 A; 1 × 8,4 A. De som is **990,6 A op kabelniveau**. Dit is een inventarisatie op basis van de grens, nog geen bevestigde elektrische toewijzing aan het station.
- De KLIC bevat hier bestaande kabels, aansluitkabels, moffen en doorsnedeteksten. Relevante onderzoekskandidaten zijn onder meer **6749-00/01/02**, **6752-00/01**, **6750-00**, **6751-00** en **6756-00**. Bij de gebiedsovergangen zijn ook 6733, 6747 en 6748 zichtbaar. Een label binnen de grens bewijst niet dat de hele kabel aan 011.601 moet worden toegewezen.
- De KLIC toont bij het Wikkeplein het bestaande station **011.514**. De overgang van die bestaande voeding naar het nieuwe ontwerp moet expliciet worden vastgelegd; een kruising of gebiedsgrens is geen elektrische scheiding.
- Bij de buurstations zie ik nieuwe 150Al-kabels, hergebruik van bestaande kabels, gekleurde richtingen, VM/AM/EM-aanduidingen, overzetters, stroom- en lengteaanduidingen en richtingblokken. Hun vormgeving is het voorbeeld. Hun zekeringwaarden worden niet zonder herberekening overgenomen.

De hoofdtekening heeft `INSUNITS = 0`. Bij het bepalen van lengtes moet daarom expliciet worden bevestigd dat één tekeneenheid één meter is. De eTransmit noemt tevens uitgesloten referenties, waaronder de aparte huisaansluitingstekening. De aanwezige aansluitblokken en KLIC kunnen voor dit plan worden gebruikt; bij ontbrekende of tegenstrijdige aansluitinformatie blijft die aansluiting een open punt.

## 2. Eerst het bestaande net en de aansluitingen reconstrueren

1. Gebruik de huidige rode grens als ruimtelijk uitgangspunt en leg de raakvlakken met de buurstations vast.
2. Koppel per ontwerpstroomrondje het aansluitpunt uit WFS-laag `asm_e_lv_service_connection`. Volg via `asm_e_lv_conn_cable` de aansluitkabel en lees de kabelcode uit `label`. Zoek met dezelfde code én de geometrische verbinding het juiste deel in `asm_e_lv_map_cable`. Vergelijk vervolgens de code met de KLIC-geulentekst voor kabeltype en materiaal. Nabijheid tot een kabel is geen bewijs van voeding. Een gemeenschappelijke huisaansluitkabel kan meerdere aansluitingen bedienen.
3. Bouw het net op uit de afzonderlijke WFS-kabeldelen en echte verbindingen: station, verbindingsmof, aftakmof, eindmof en eindpunt. Een lijnkruising wordt alleen een verbinding als de bron dit ondersteunt. Behoud kabeldeelgrenzen, maar behandel een objecteinde niet automatisch als elektrische scheiding of vastgesteld moftype.
4. Leg per kabeldeel vast: kabelnummer, materiaal, doorsnede, lengte, aansluitingen, begin- en eindverbinding, eventuele aftakken en de huidige voeding. Bewaar per aansluiting ook de bestaande hoofdkabel of aftak waarop zij daadwerkelijk uitkomt; die wordt later vergeleken met de ontworpen hoofdkabel of aftak die haar bedient.
5. Volg verbonden delen ook buiten de rode grens totdat de werkelijke scheiding bekend is. Knip een berekening niet bij de gebiedsgrens af.
6. Controleer bij iedere overname van een bestaande kabel of deze nog verbinding met een andere voeding heeft. Beschrijf de benodigde scheiding en moffen in het ontwerp.

De eerste uitkomst is een aansluitlijst en een overzicht van de bestaande kabelgroepen, inclusief onduidelijke aansluitingen. Leg per koppeling de WFS-objectidentificaties, oorspronkelijke labels, kabelcode en bijbehorende KLIC-geulentekst vast. De WFS-labels kunnen beginnen met `Kabelgroep:` of `Kabelgroup:`; vergelijk de kabelcode zelf, inclusief achtervoegsel. Werk in EPSG:28992 met bevestigde tekeneenheden, controleer functie/status en registreer eventuele verschillen tussen WFS en KLIC met hun peildatum.

**WFS-functieselectie:** lees bij kabelobjecten de kolom `omschrijving`. Kabels met functie **LS** en **LS/OV** zijn nodig voor deze LS-tekening en worden meegenomen in de aansluitkoppeling en berekeningen. Kabels met functie **alleen OV** worden uitgesloten. Bewaar de oorspronkelijke omschrijving en de herleide functie. Ontbrekende of onduidelijke functies blijven open punten. De bekeken aansluitpunten heten `Huisaansluiting`; bepaal hun LS-koppeling via de aansluitkabel en hoofdkabel. De functie LS/OV vervangt niet het fysieke kabeltype uit de KLIC en betekent niet automatisch dat nieuwe combikabel moet worden aangelegd.

**Kabelcoderegel:** `-00` is de hoofdkabel; `-01` kan een aftak zijn, maar is ook de standaardcode voor een eigen richting uit het station met één aansluiting. Maak het onderscheid met de bronroute, verbindingen en aangesloten punten. Behandel een zelfstandige `-01` niet automatisch als aftak van een `-00`.

**Materiaalregel:** zonder `Al` achter de doorsnedecijfers is het Cu. De KLIC-aanduiding `50+6` is dus een koperen combikabel (**50Cu + 6Cu**); `95Al` is aluminium. De WFS levert geen doorsnede of materiaal ter vervanging van deze geulentekst.

De 125 geometrisch getelde aansluitingen dienen als controlegetal: afwijkingen moeten verklaard worden. De koppeling aan de bestaande kabel vormt de basis voor hergebruik én voor de beslissing of een aansluiting een overzetter nodig heeft.

## 3. Richtingen ontwerpen met kader 2024

Selecteer expliciet **2024 — Eea-0205.K 1.0**. De huidige plugin start standaard met een nieuwer kader; die standaard mag niet worden gebruikt voor dit project.

Onderzoek eerst welke bestaande kabelstukken bruikbaar zijn. **Nieuwe LS-kabels zijn standaard altijd 150Al.** Gebruik standaard een aparte LS-kabel en een aparte OV-kabel; de OV-kabels worden in de afzonderlijke OV-tekening uitgewerkt.

**Een combikabel is uitsluitend aan de orde als aansluiting op een bestaande combikabel nodig is om aansluitingen van stroom te voorzien.** Een kabelgeulaanduiding zoals `50+6` met kabelcode identificeert een bestaande combikabel. Een nieuwe kabel die daarmee wordt verbonden krijgt de kabeltekst **`150Al+`**. De gewone nieuwe LS-kabel krijgt **`150Al`**. Het plusteken geeft de combi-uitvoering aan; de extra ader wordt niet als parallelle LS-hoofddoorsnede in de capaciteitsberekening opgeteld. Bewaar de combi-eigenschap expliciet bij het kabeldeel en de verbindingsmof.

Als een richting met de nieuwe 150Al-stukken en het beoogde hergebruik niet voldoet, onderzoek dan een andere verdeling over beschikbare richtingen, andere scheidingspunten of vervanging van beperkende bestaande stukken door 150Al. Kies niet zelfstandig een ander standaardtype voor nieuwe kabels.

**Tracévoorwaarden:** ontwerp zonder kabelkruisingen en zet kabelweergavelijnen naast elkaar. De fysieke route ligt bij voorkeur in de stoep en vermijdt bomen en vastgelegde boom-/wortelbeschermingszones. Gebruik bijvoorbeeld BGT via PDOK om stoepen, parkeerplaatsen en wegen te beoordelen. Als het niet anders kan, zijn parkeerplaatsdoorgangen en wegoversteken toegestaan. Beperk het aantal wegoversteekplaatsen; iedere oversteek is recht zonder boog in de kabels. Meerdere overstekende kabels gebruiken dezelfde plaats, naast elkaar zonder onderlinge kruisingen. Leg de gezamenlijke oversteek, betrokken kabels, reden, alternatieven en fysieke lengtes vast. Controleer ook bochten, stationsuitgangen, moffen en gebiedsovergangen; een grafische lijnverschuiving vervangt geen uitvoerbare fysieke route. Leg perceelgrenzen over de mogelijke tracés en beoordeel per betrokken perceel de grondpositie met actuele eigendoms-/beheerinformatie. Geef voorkeur aan geverifieerde gemeentelijke of andere overheidsgrond en vermijd privéterrein waar mogelijk. Leg bron, datum, perceelidentificatie en eigenaar-/beheerklasse vast. Een openbaar toegankelijke stoep of BGT-topografie is op zichzelf geen bewijs van gemeente-eigendom. Ontbrekende eigendomsinformatie, onvermijdelijke privédoorgangen of ontbrekende uitvoerbare doorgangen blijven open ontwerppunten met onderzochte alternatieven. Deze perceel-, BGT- en tracécontrole is nog niet definitief uitgevoerd voor 011.601.

Verdeel de aansluitingen in samenhangende richtingen met een herkenbare route en uitvoerbare overzettingen. Begin met de bestaande kabelgroepen en hun zijtakken, in plaats van uitsluitend gelijke aantallen woningen per richting te kiezen. Leg daarna per richting vast welke stukken worden hergebruikt, waar nieuwe kabel komt en welke moffen en overzetters nodig zijn. Respecteer de beschikbare richtingen en de DALI-aanduiding. De `80A Tamp`-posities uit andere stations zijn een te bevestigen projectconventie, geen automatisch opgelegde bezetting van RT 01 en RT 12.

**Plaats een `OVERZETTER`-blok pas nadat vaststaat dat de aansluiting — het rondje met kabelontwerpstroom — op een nieuwe kabel terechtkomt.** Blijft zij op dezelfde bestaande kabel waarop zij al zit, dan komt er geen overzetter naast het rondje. Dit geldt ook als die bestaande kabel een nieuwe voeding krijgt via een nieuwe kabel en verbindingsmof. Een gewijzigde stationsvoeding of richtingkleur is op zichzelf geen overzetting. Bepaal de overzetters dus per aansluiting, na de definitieve kabeltoewijzing, en niet voor alle aansluitingen in het gebied.

Per volledig pad geldt:

`R = Σ(R per km × lengte / 1000)`

`X = Σ(X per km × lengte / 1000)`

`Z = √(R² + X²)`

Toets zowel de impedantie als de stroombelastbaarheid van alle gebruikte doorsneden. Controleer bovendien de fysieke kabelverjonging: zwaardere kabel aan het begin en dunnere aan het einde. De checker telt lengtes per kabeltype op en controleert deze fysieke volgorde niet zelf.

| gG-afzekering | Maximale ontwerpstroom | Z-max evenredig | Z-max laatste helft |
|---:|---:|---:|---:|
| 63 A | 57 A | 0,250 Ω | 0,215 Ω |
| 80 A | 72 A | 0,250 Ω | 0,170 Ω |
| 100 A | 90 A | 0,204 Ω | 0,136 Ω |
| 125 A | 113 A | 0,163 Ω | 0,109 Ω |
| 160 A | 144 A | 0,128 Ω | 0,085 Ω |
| 200 A | 180 A | 0,092 Ω | 0,068 Ω |
| 250 A | 225 A | 0,062 Ω | 0,055 Ω |

Kies het belastingprofiel op basis van de aansluitlocaties langs het pad. Bij een onzekere verdeling worden beide profielen doorgerekend en blijft de ongunstigste uitkomst het uitgangspunt totdat de verdeling onderbouwd is.

Ter illustratie zijn hieronder lengtegrenzen afgeleid uit de bronwaarden voor een pad dat geheel uit één kabeltype bestaat. Het zijn geen gemeten lengtes van 011.601. Gemengde kabelpaden worden met bovenstaande formule berekend; de afzonderlijke lengtegrenzen mogen niet bij elkaar worden opgeteld.

| Kabeltype en afzekering | Evenredig | Laatste helft |
|---|---:|---:|
| 4×150 mm² Al, 250 A / 225 A ontwerpstroom | 281,0 m | 249,3 m |
| 4×150 mm² Al, 200 A / 180 A ontwerpstroom | 417,0 m | 308,2 m |
| 4×95 mm² Al, 200 A / 180 A ontwerpstroom | 278,5 m | 205,8 m |
| 4×95 mm² Al, 160 A / 144 A ontwerpstroom | 387,5 m | 257,3 m |
| 4×50 mm² Al, 125 A / 113 A ontwerpstroom | 252,1 m | 168,6 m |
| 4×50 mm² Cu, 160 A / 144 A ontwerpstroom | 323,0 m | 214,5 m |

De getoonde lengtes zijn afgerond voor presentatie; de toets gebruikt ongeronde waarden. 95Al kan in dit model geen 250 A-richting vormen; 50Al is maximaal 125 A en 50Cu maximaal 160 A, eventueel lager door de lengte. Daarom verdienen de dunnere zijtakken bij de kandidaten 6749 en 6752 bijzondere aandacht.

## 4. Aftakkingen: jouw regel als vaste ontwerpregel

Een aftak wordt niet als extra kabellengte achter het einde van de hoofdkabel opgeteld. Ieder pad wordt afzonderlijk vanaf het station getoetst:

- pad naar het hoofdkabeleinde: station → gemeenschappelijk stuk → aftakmof → hoofdkabeleinde;
- pad naar een aftakeinde: station → hetzelfde gemeenschappelijke stuk → aftakmof → aftakeinde;
- bij meerdere aftakmoffen: ieder volledig pad naar een eindpunt, met de juiste gemeenschappelijke stukken.

Het gemeenschappelijke stuk staat eenmaal in iedere afzonderlijke padberekening. Vervolgens geldt voor de hele richting **de laagste maximaal toegestane afzekering van alle paden**, met de bijbehorende maximale ontwerpstroom. Er worden geen afzonderlijke aftakzekeringen verondersteld.

**Alle aansluitbelastingen op de hoofdkabel én de aftakken tellen wel mee.** Iedere aansluiting wordt eenmaal geteld. De totale richtingbelasting moet onder de capaciteit van de gekozen afzekering blijven. Een richting wordt dus niet kunstmatig ruimer doordat de aftaklengtes afzonderlijk worden getoetst.

Voorbeeld ter verduidelijking, geen ontwerpresultaat: een gemeenschappelijk stuk van 60 m 150Al, gevolgd door 80 m bestaande 95Al naar het hoofdeinde, laat in het evenredige model maximaal 200 A gG / 180 A ontwerpstroom toe. Een tweede pad met hetzelfde gemeenschappelijke stuk en 120 m bestaande 50Al laat maximaal 125 A gG / 113 A toe. De **hele richting** wordt dan begrensd op **125 A / 113 A**.

Als de totale belasting niet past: onderzoek verdeling over een extra richting, een andere scheiding of vervanging van het beperkende kabeldeel. Beoordeel elke variant opnieuw op alle paden en aansluitingen.

## 5. Ook de transformator toetsen

De som van kabelontwerpstromen is niet de trafobelasting. **Vertaal iedere aansluiting eerst naar haar aansluitcategorie en gebruik voor die categorie de afzonderlijke waarden van `Ontwerpstroom_trafo` in de 2024-werkmap.** Neem dezelfde aantallen en categorieën uit alle richtingen samen. Bereken verbruik en opwek apart; gebruik daarna de maatgevende situatie. Gebruik geen algemene omrekenfactor van kabelstroom naar trafostroom en geen som van afzonderlijke richtingmaxima als vervanging voor deze categorievertaling.

Een voorlopige vertaling van de 125 stroomteksten naar de overeenkomstige Type 1-rijen geeft:

| Aansluitcategorie kader 2024 | Aantal | Kabelstroom in rondje | Trafostroom verbruik per aansluiting | Trafostroom opwek per aansluiting |
|---|---:|---:|---:|---:|
| Type 1 — rijtjeswoning | 112 | 7,8 A | 7,0 A | 7,3 A |
| Type 1 — twee onder een kap | 10 | 8,8 A | 8,0 A | 7,3 A |
| Type 1 — vrijstaand | 2 | 10,3 A | 9,5 A | 9,5 A |
| Type 1 — onbekend woningtype | 1 | 8,4 A | 7,6 A | 7,3 A |

Deze categorieën zijn voorlopig herleid uit de unieke overeenkomst van de rondjeswaarden met de 2024-kabeltabel. De uiteindelijke aansluitlijst bewaart de categorie expliciet; bij een dubbelzinnige stroomwaarde wordt het type uit aanvullende aansluitinformatie vastgesteld. `Onbekend woningtype` is een bestaande categorie met eigen waarden, geen vrij gekozen schatting.

Verbruik: `112 × 7,0 + 10 × 8,0 + 2 × 9,5 + 1 × 7,6 = 890,6 A`.

Opwek: `112 × 7,3 + 10 × 7,3 + 2 × 9,5 + 1 × 7,3 = 916,9 A`.

Voor de transformator geldt de door Luka opgegeven algemene formule: **maximale trafo-ontwerpstroom = trafocapaciteit in kVA ÷ 0,23 ÷ 3**. Hier is 0,23 de fasespanning in kV en 3 het aantal fasen. Voor de opgenomen **630 kVA-transformator is de grens 630 ÷ 0,23 ÷ 3 = 913,043478… A**, weergegeven als **913 A**. De capaciteitstoets gebruikt de ongeronde grens.

| Situatie | Som volgens trafowaarden | Limiet | Resterende ruimte |
|---|---:|---:|---:|
| Verbruik | 890,6 A | 913,0 A | 22,4 A |
| Opwek | 916,9 A | 913,0 A | −3,9 A |

De maatgevende voorlopige trafo-ontwerpstroom is **916,9 A**. Deze ligt afgerond **3,9 A boven de berekende grens** (circa 0,42%). De categorievertaling blijft uit het 2024-Excel komen; de capaciteitstoets gebeurt rechtstreeks in ampères tegen `630 ÷ 0,23 ÷ 3`. De tabel toont afgeronde waarden; de berekening gebruikt ongeronde waarden.

Dit wordt eerst geverifieerd met de werkelijke stationstoewijzing en aansluittypes. Het bewijst nog niet dat de opgenomen transformator gewijzigd moet worden. Als de overschrijding na verificatie blijft bestaan, moet de verdeling op de gebiedsgrens of de stationskeuze worden besproken en onderbouwd. Een verschuiving naar een buurstation vereist ook een controle van dat station en zijn getroffen richting.

## 6. Vormgeving overnemen uit de bestaande uitwerking

| Onderdeel | Vastgesteld voorbeeld en werkwijze |
|---|---|
| Gebiedsgrens | `01 - Stationsgebied`; gesloten polyline; rood, ACI 1; vaste breedte 1,0; aansluitende grenspunten met de buren behouden. |
| Richtingen | Lagen `Aansluiting LS K01` t/m `K12`; bestaande laagkleuren en eigenschappen hergebruiken. K01 4, K02 52, K03 5, K04 3, K05 6, K06 30, K07 252, K08 244, K09 114, K10 1, K11 190, K12 201. |
| Kabeltracés | Hetzelfde verloop, de parallelle lijnopbouw en onderlinge afstand als een vergelijkbaar uitgewerkt tracé. De kaart kan verschoven lijnen gebruiken voor leesbaarheid; rekenlengtes horen bij de fysieke route. |
| Bestaande kabels | `01 - Bestaande kabel`, grijs ACI 250; bestaande nummering en brontracé herkenbaar houden. |
| Moffen | Bestaande blokken `NIEUWE MOF`, `MOF bestaand-nieuw` en `BESTAANDE MOF`; VM/AM/EM-teksten volgens de voorbeelden, met doorsneden, overgangsrichting en oud kabelnummer. |
| Overzettingen | Bestaand blok `OVERZETTER` uitsluitend naast aansluitingen die naar een nieuwe kabel gaan. Geen blok bij een aansluiting die op haar oorspronkelijke bestaande kabel blijft; pas plaatsen na de definitieve kabeltoewijzing. |
| Ontwerpstroomrondjes | Bestaande `KA_K01`-blokken en teksten op `Aansluiting LS_OntwerpstroomKabel`; tekststijl ARIAL, hoogte 0,75. |
| Kabelteksten | Nieuwe standaard-LS-kabel: `150Al / ????-00`. Nieuwe combikabel voor noodzakelijke verbinding met een bestaande combikabel: `150Al+ / ????-00`. Bestaande kabel bijvoorbeeld `95Al / (was …)`; onbekende nieuwe nummers blijven zichtbaar als onbekend. |
| Richtingoverzicht | Bestaand `RT 1-12`-blok en kleurgebruik; per bezette richting de berekende afzekering, kabelnummer waar bekend en kabeltype opnemen. |
| Resultaatteksten | De bestaande notatie met decimale komma, `Amp.` en `Met.`; vastleggen welke lengte wordt getoond bij een vertakte richting, zodat deze overeenkomt met het maatgevende rekenpad. |

Exacte plaatsing, teksthoogte van overige labels, blokoriëntatie en lijnopbouw worden van een passend voorbeeld overgenomen. Bestaande blokken kunnen hun zichtbare geometrie en attributen op een andere locatie hebben dan het invoegpunt; beoordeling gebeurt op de zichtbare inhoud. Leg geen nieuwe algemene afstands- of lijndikteregel vast op basis van één afwijkend object.

## 7. Ontwerpcontrole en oplevering na beoordeling

De ontwerpuitwerking levert één samenhangend stationsgebied op, met een aansluitingsoverzicht en een controleblad per richting. Per richting worden vastgelegd: unieke aansluitingen, ontwerpstroom, nieuwe en hergebruikte kabeldelen, kabeltypes en fysieke lengtes, aftakstructuur, belastingprofiel, uitkomsten per pad, maatgevend pad, gekozen gG-afzekering, maximale ontwerpstroom en resterende ruimte.

Controleer vóór oplevering:

1. iedere aansluiting is precies eenmaal toegewezen; verschillen met de inventarisatie zijn verklaard;
2. alle complete paden voldoen, inclusief dunne aftakken en verbonden stukken buiten de grens; WFS-codes en geometrie ondersteunen de aansluitingstoewijzing, eigen `-01`-richtingen zijn van aftakken onderscheiden en kabeltypes zijn uit de KLIC-geulenteksten gelezen;
3. de volledige richtingbelasting past onder de laagste toegestane afzekering;
4. kabelverjonging, eenheden, fysieke route en getoonde lengtes zijn gecontroleerd;
5. overnames van bestaande voedingen en de scheidingen naar buren zijn expliciet;
6. iedere aansluitcategorie is afzonderlijk vertaald naar de trafowaarden van hetzelfde 2024-kader, met aparte verbruik- en opwektotalen; de maatgevende trafo-ontwerpstroom is maximaal `trafocapaciteit in kVA ÷ 0,23 ÷ 3` (voor 630 kVA circa 913 A);
7. labels, moffen, richtingoverzicht en tracés stemmen met de berekening overeen; nieuwe kabels zijn 150Al, noodzakelijke combi-verbindingen herkenbaar als 150Al+, en overzetters staan uitsluitend bij aansluitingen die naar een nieuwe kabel gaan;
8. de vormgeving is visueel vergeleken met de uitgewerkte stations en de tekening leest goed op de gebruikte planschaal;
9. kabelroutes en weergavelijnen kruisen elkaar niet, lijnen staan naast elkaar, tracés liggen bij voorkeur in de stoep en vermijden bomen en vastgelegde beschermingszones; noodzakelijke parkeerplaatsdoorgangen zijn onderbouwd, wegoversteken zijn zo weinig mogelijk toegepast, recht zonder boog en voor meerdere kabels op dezelfde oversteekplaats;
10. perceelgrenzen en eigendoms-/beheerinformatie zijn gecontroleerd; privéterrein is waar mogelijk vermeden en onbekende grondpositie of onvermijdelijke privédoorgangen zijn als open punten met alternatieven vastgelegd.

**Voor jouw beoordeling:** akkoord op deze reken- en ontwerpvolgorde; de betekenis en gewenste bezetting van de `80A Tamp`-richtingen; en de omgang met de trafotoets als de kleine overschrijding na de definitieve aansluittoewijzing blijft bestaan. De grensoverschrijdende kabelkoppelingen worden als onderdeel van de uitwerking uitgezocht.

Na verwerking van jouw beoordeling kan de vaardigheid worden gemaakt. Die legt de aftakregel, bronkeuze per kader, aansluittoewijzing, scheidingen, rekencontrole en stijlovername vast. Projectspecifieke stationnummers, kabelnummers en de voorlopige telling van 011.601 worden voorbeelden en geen algemene voorschriften.

## Bronnen

- Aanvullende tracéregels van Luka: geen kabelkruisingen, lijnen naast elkaar, voorkeur voor de stoep en buiten bomen; privégrond waar mogelijk vermijden en perceelgrenzen en grondpositie beoordelen. BGT via PDOK kan worden gebruikt. Noodzakelijke parkeerplaatsdoorgangen en wegoversteken zijn toegestaan; wegoversteken zo weinig mogelijk, altijd recht zonder boog en meerdere kabels op dezelfde oversteekplaats. De benodigde definitieve topografie- en eigendoms-/beheercontrole volgt bij de ontwerpuitwerking.
- [PDOK — BGT](https://www.pdok.nl/introductie/-/article/basisregistratie-grootschalige-topografie-bgt-), voor de topografische bron bij de latere tracécontrole.

- Aanvullende WFS-selectieregel van Luka: controleer de kolom `omschrijving`; LS en LS/OV opnemen in de LS-tekening, uitsluitend OV uitsluiten.

- Hoofdtekening: `FW_ Proefsleuven 25_42043 REC Oss Meanderende Maas DS 3BC/VO-LS PILS Laarbeek Beek D.26936 - Fase 7.dxf`.
- Kabel- en aansluitbron: `04. KLIC/Laarbeek GEN KLIC_ls.dwg`; topografie: `01. Topo en werktekeningen/topo juiste.dwg`.
- [Enexis-WFS](https://opendata.enexis.nl/geoserver/wfs?service=WFS&request=GetCapabilities&version=2.0.0): `Enexis_Opendata:asm_e_lv_conn_cable`, `Enexis_Opendata:asm_e_lv_map_cable` en `Enexis_Opendata:asm_e_lv_service_connection`; schemas en begrensde selectie gecontroleerd op 2 oktober 2026, bekeken peildatum 26 september 2026.
- [Enexis Kabelchecker — gecontroleerde commit 4009601](https://github.com/LukaStuurman/AutoCAD-Enexis-kabels-checker/tree/4009601e15fa4b1b6926380395132b0c1630ce21).
- [Koppeling van kader 2024 aan versie 1.0](https://github.com/LukaStuurman/AutoCAD-Enexis-kabels-checker/blob/4009601e15fa4b1b6926380395132b0c1630ce21/src/Enexis.KabelChecker.AutoCAD/KaderVersion.cs).
- [Bronwerkmap Eea-0205.K 1.0](https://github.com/LukaStuurman/AutoCAD-Enexis-kabels-checker/blob/4009601e15fa4b1b6926380395132b0c1630ce21/src/Enexis.KabelChecker.AutoCAD/Resources/Eea-0205.K%201.0%20-%20Copy.xlsx). Bekeken: beide kabelcontrolebladen, rijen 12–38; kabelontwerpstromen C5:D8 en C38; trafowaarden C5:D8, vermogensformules G/H en totalen C38:C42.
- [Herleiding van kabelgegevens, impedantie en zekeringen](https://github.com/LukaStuurman/AutoCAD-Enexis-kabels-checker/blob/4009601e15fa4b1b6926380395132b0c1630ce21/docs/excel-model.md).
- [Ontwerpstroom voor kabel en trafo per kader](https://github.com/LukaStuurman/AutoCAD-Enexis-kabels-checker/blob/4009601e15fa4b1b6926380395132b0c1630ce21/docs/ontwerpstroom-per-kader.md).
- Aanvullende ontwerpregels van Luka: aftakkingen en de laagste afzekering voor de hele richting; **maximale trafo-ontwerpstroom = kVA ÷ 0,23 ÷ 3**, voor 630 kVA circa 913 A; overzetters alleen bij aansluitingen die naar een nieuwe kabel gaan; nieuwe kabels standaard 150Al; combi uitsluitend bij noodzakelijke aansluiting op een bestaande combikabel, met kabeltekst 150Al+; standaard gescheiden LS en OV, met OV in een aparte tekening. De losse kabelberekening in de repository voert de netstructuurcontrole niet zelfstandig uit.
- Aanvullende bron- en interpretatieregels van Luka: WFS voor de koppeling aansluitpunt/aansluitkabel/hoofdkabel en kabelcodes; KLIC-geulentekst voor kabeltype; `-01` kan naast een aftak ook een eigen richting met één aansluiting zijn; doorsnedecijfers zonder `Al` betekenen Cu.

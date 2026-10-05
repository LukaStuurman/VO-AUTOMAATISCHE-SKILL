# LS-VO ontwerpen uit brongegevens

Gebruik `SKILL.md` voor werk aan LS-stationsgebieden.

Bij een ontwerp vanaf een leeg stationsgebied zijn de oorspronkelijke CAD, bestaande KLIC/WFS, topografie/BGT, perceel-/grondinformatie, kader en expliciete projectfeiten de invoer. Lees of importeer geen uitgewerkte versie van datzelfde station om routes, richtinggroepen, mofposities, overzetters of labels over te nemen. Een voorbeeld mag na een opgeslagen kandidaat als vergelijking dienen. Leer algemene regels uit verschillen; hardcode geen voorbeeldcoördinaten, kabelcodes, groepsaantallen of verwachte zekeringen in de generator.

Leg broncorrecties (zoals een geplande aansluiting met categorie en locatie) apart vast. Een correctie is geen routinginvoer. Bewaar bron- en scriptversies per test. Vergelijk rekenen én de daadwerkelijk opgeslagen CAD en afbeeldingen; een plan of herberekening alleen is geen tekenresultaat.

- Lees bij BGT **zowel `fysiek_voorkomen` als `plus_fysiek_voorkomen`**. `groenvoorziening` kan bomen, bosplantsoen, heesters of struiken bevatten. Alleen gras/plein/tegels mogen niet als vrijbrief voor een boomstrook gelden. Een onbekend plustype is een bronvraag, geen bewezen boomvrije doorgang.
- Laat nieuwe richtingen zoveel mogelijk één gezamenlijke gleuf gebruiken. Betaal een gezamenlijk tracé/oversteek eenmaal in de ontwerpkeuze. Gebruik één gedeelde lijnopbouw met **0,20 m offset**; simplificeer gedeelde bochten eenmaal. Corrigeer rastertrapjes zonder stoep- of boomvoorwaarden te verliezen. Oversteken zijn recht en gezamenlijk.
- Een mof mag op ieder geschikt punt van een bestaande hoofdkabel. Toets nieuwe main, oude delen, alle aftakpaden en aansluitingstoewijzingen samen; de goedkoopste afzonderlijke feeder is niet automatisch een bruikbare richting.
- Bestaande hoofdkabels mogen over meerdere onafhankelijke richtingen worden verdeeld. Leg echte scheidingen en effecten op achterblijvende voedingen vast.
- Bereken eerst tot het fysieke kabeluiteinde en, als dat niet past, tot de laatste aansluiting op ieder betrokken pad. Houd alle belasting en aftakken. Een korter rekeneinde verplaatst geen fysieke eindmof.
- Een ongebruikt deel mag bij de mof worden geknipt en verwijderd. Bepaal **eerst het gebruik door alle richtingen** en externe/achterblijvende voedingen. Verwijder alleen het resterende ongebruikte deel; nooit de rest van een kabelcode als een ander stuk door een andere richting wordt gebruikt. Onbevestigd gebruik blijft beschermd. De bestaande KLIC/WFS-bron wordt niet gewijzigd.
- Bescherm fysieke combikabeldelen zolang hun OV-gebruik in de aparte OV-uitwerking niet is vastgesteld. LS buiten gebruik betekent niet dat de hele combikabel weg kan.
- Huisaansluitkabels zijn bron voor koppeling en belasting, geen richtingtracés of rekenlengtes. Plaats geen eindmof per huisaansluiting. Bij een overzetting mag een aansluiting op een nabijgelegen nieuw hoofdtracé komen; verleng de hoofdroute niet naar het oude huisaansluitpunt.
- Standaard nieuw LS: **150Al**. Alleen een noodzakelijke aansluiting op een behouden combikabel krijgt **150Al+**. OV heeft een aparte tekening. WFS `omschrijving`: LS en LS/OV opnemen, uitsluitend OV uitsluiten. KLIC bepaalt kabeltype; zonder `Al` betekent Cu.
- Overzetter uitsluitend bij overgang naar een nieuwe kabel. Bij behoud op de oorspronkelijke kabel, ook met nieuwe voeding, geen overzetter.
- Bereken elke hoofd-/aftakroute apart met eenmaal het gedeelde voedingsstuk. De laagste maximaal toegestane afzekering begrenst de gehele richting; alle aansluitstromen tellen eenmaal.
- Vertaal per aansluitcategorie naar kabel- én trafowaarden. Verbruik en opwek apart. Trafolimiet ongerond: **kVA / 0,23 / 3**.

Lever DXF/DWG, overzicht en stationsdetail, aansluitregister, fysieke/rekenkundige paden en geometriecontrole. Meld concrete ontbrekende broninformatie. Noem een afgeleide herbouw nooit een onafhankelijke bronontwerptest, en noem een nog kruisende of overbelaste kandidaat niet gereed.

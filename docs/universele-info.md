# Universeel plan van aanpak — stationsgebieden

Concept ter beoordeling door Luka · 2 oktober 2026

Dit plan geldt voor het ontwerpen van één of meerdere stationsgebieden vanuit een situatie zoals 011.601: stationslocaties en beschikbare uitrusting zijn aangegeven, bestaande kabels en aansluitkabels staan in een KLIC-referentie, de Enexis-WFS geeft aansluitpunten, kabelcodes en kabeldeelgeometrie, en rondjes geven de kabelontwerpstromen van aansluitingen aan. De nieuwe kabelrichtingen, hergebruikstukken, moffen, overzettingen en richtingoverzichten moeten nog worden uitgewerkt. Rode gebiedsgrenzen kunnen al aanwezig zijn.

Het plan werkt zowel als **nog geen station in de tekening is uitgewerkt**, als wanneer **een deel van de omliggende stations al is uitgewerkt**. De rekenregels zijn gelijk; de vrijheid om aansluitingen, kabelgroepen en gebiedsgrenzen te verdelen verschilt. De huidige referentie is kader 2024. Een volgend project krijgt altijd een expliciet gekozen kader en de daarbij behorende bronwaarden.

## 1. Beginsituatie en ontwerpgegevens vastleggen

Inventariseer vóór de eerste ontwerpkeuze:

- hoofdtekening, beschikbare KLIC- en toporeferenties, versie en ontbrekende referenties; WFS-bron, opvraagdatum en peildatum;
- kaderjaar en bronwerkmap voor kabel- en trafo-ontwerpstromen;
- bestaande en geplande stations, locatie, trafocapaciteit, stroomlimiet, aantal beschikbare richtingen en bijzondere functies zoals DALI;
- bestaande gebiedsgrenzen en aansluitingen aan beide zijden van iedere grens;
- status per station: nog uit te werken, gedeeltelijk uitgewerkt of reeds uitgewerkt;
- bestaande kabelgroepen, moffen, aansluitkabels en huidige voedingen;
- stoepgeometrie, boomlocaties, beschikbare boom- en wortelbeschermingszones, perceelgrenzen en actuele eigendoms-/beheerinformatie voor de mogelijke tracés;
- beschikbare lagen, blokken en goedgekeurde vormgevingsreferentie;
- eenheden en schaal van de tekening.

Maak één register voor het onderzochte projectdeel. Per aansluiting wordt de bron, locatie, aansluitcategorie, kabelontwerpstroom, huidige voeding, oorspronkelijke bestaande kabel en ontworpen kabelbestemming vastgelegd. Bewaar de WFS-objectidentificatie van aansluitpunt, aansluitkabel en hoofdkabel/aftak, de oorspronkelijke labels en de herleide kabelcode. Bewaar per kabeldeel of het een gewone LS-kabel of een combikabel is en uit welke KLIC-geulentekst het kabeltype is gelezen. Een ontbrekende categorie of verbinding blijft zichtbaar als ontbrekend gegeven. Nieuwe aansluitwaarden of een netverbinding worden niet uit nabijheid of uiterlijke gelijkenis verzonnen.

## 2. Werkwijze kiezen op basis van de omliggende stations

| Beginsituatie | Werkwijze voor verdeling en grenzen | Werkwijze voor vormgeving |
|---|---|---|
| Geen stations uitgewerkt | Inventariseer het hele te ontwerpen projectdeel. Verdeel aansluitingen en bestaande kabelgroepen voorlopig over alle betrokken stations. Toets eerst of de verdeling als geheel uitvoerbaar is. Werk een station uit terwijl ook de resterende stations voldoende aansluitmogelijkheden en capaciteit houden. | Gebruik de goedgekeurde referentietekening of stijlset. Uitgewerkte buren zijn niet nodig om de vormgeving vast te stellen. |
| Omliggende stations geheel of gedeeltelijk uitgewerkt | Leg de al ontworpen voedingen, aansluittoewijzingen, scheidingen, richtingen en gebiedsgrenzen vast. Gebruik deze als bestaande ontwerpuitgangspunten en ontwerp de resterende aansluitingen aansluitend daarop. | Gebruik de goedgekeurde stijlset en passende voorbeelden uit de tekening. Controleer of afwijkingen plaatselijk zijn of een vastgelegde projectconventie. |

Wanneer een grenswijziging of aansluitoverdracht een al uitgewerkt station raakt, wordt de invloed op zijn richting en trafo opnieuw berekend. Toon de oude en voorgestelde toewijzing en het effect voordat die wijziging wordt doorgevoerd. Een uitgewerkt buurstation is geen automatische bestemming voor belasting die elders niet meer past.

Ook als slechts één station wordt uitgewerkt, worden de relevante raakvlakken met de overige stations meegenomen. Een nog onuitgewerkt buurstation wordt niet als station met onbeperkte vrije capaciteit behandeld.

## 3. De elektrische structuur uit WFS en KLIC reconstrueren

Gebruik de [Enexis-WFS](https://opendata.enexis.nl/geoserver/wfs?service=WFS&request=GetCapabilities&version=2.0.0) voor de bestaande aansluitkoppeling, kabelcodes en de geometrische grenzen van kabeldelen. Gebruik de KLIC-geulenteksten voor kabeltype, doorsnede en materiaal. De WFS bevat die kabeltypes niet als vervanging voor de KLIC.

| WFS-laag | Betekenis | Gebruik |
|---|---|---|
| `Enexis_Opendata:asm_e_lv_service_connection` | Aansluitpunt | Koppel het rondje uit de ontwerptekening aan het juiste bestaande aansluitpunt. |
| `Enexis_Opendata:asm_e_lv_conn_cable` | Aansluitkabel | Volg het aansluitpunt naar zijn kabelgroep; lees de kabelcode uit `label`. |
| `Enexis_Opendata:asm_e_lv_map_cable` | Hoofdkabel of bestaand aftakdeel | Zoek de betreffende kabelgroep via `label` en geometrie; behoud de afzonderlijke kabeldelen en eindpunten. |

Werk in hetzelfde bevestigde coördinatenstelsel en dezelfde eenheden. De gecontroleerde WFS gebruikt **EPSG:28992 (RD)**. Vraag het relevante gebied met een randzone op en controleer of alle resultaten zijn opgehaald; vergroot het gebied wanneer een verbonden kabelgroep verder doorloopt. Leg de opvraagdatum, `peildatum`, bronidentificaties en gebruikte gebiedsselectie vast.

De koppeling verloopt als volgt:

1. Koppel het ontwerpstroomrondje via de bestaande aansluitinformatie aan het WFS-aansluitpunt.
2. Volg de aansluitkabelgeometrie vanaf dat punt. Houd rekening met meerdere aansluitingen op een gemeenschappelijke huisaansluitkabel en onderscheid LS- van OV-aansluitkabels.
3. Lees de kabelcode uit het `label` van de aansluitkabel en vergelijk die met de code in de hoofdkabellabels. In de gecontroleerde data komen zowel `Kabelgroep: …` als `Kabelgroup: …` voor. Vergelijk de herleide code, bijvoorbeeld `LBK6750-00`, en bewaar ook het oorspronkelijke label. De code inclusief achtervoegsel blijft behouden.
4. Controleer met de geometrie en de aansluitpunten op welk hoofdkabel- of aftakdeel de aansluiting uitkomt. Een gelijke code kan meerdere kabeldeelobjecten bevatten en is op zichzelf geen unieke objectkoppeling. Bij meerdere kandidaten is de dichtstbijzijnde lijn onvoldoende bewijs; de verbinding en kabelcode moeten samen kloppen.
5. Vergelijk die kabelcode met de bijbehorende geulentekst van de KLIC. Lees daar het kabeltype en de combi-eigenschap en leg de herkomst vast.

**Materiaalregel van Luka:** staat achter de doorsnedecijfers geen `Al`, dan is het **Cu (koper)**. `95Al` is aluminium; `50+6` is een koperen combikabel, dus **50Cu + 6Cu**. Het ontbreken van een materiaalwoord in de WFS wordt niet gebruikt om een kabeltype te raden: de doorsnedecijfers komen uit de KLIC-geulentekst. Een onleesbare of ontbrekende geulentekst blijft een ontbrekend kabeltype.

**Kabelcode en aftakken:** `kabelcode-00` duidt de hoofdkabel aan en `kabelcode-01` kan een bestaande aftak aanduiden. Er is een belangrijke uitzondering: een **eigen richting vanuit een station met één aansluiting** heeft standaard eveneens `kabelcode-01`. Classificeer daarom niet uitsluitend op het achtervoegsel. Volg de route naar een stationsuitgang of echte aftakverbinding en controleer de aangesloten punten. Een afzonderlijke `-01`-richting wordt niet als zijtak van een toevallig nabijgelegen `-00` behandeld. Andere achtervoegsels worden eveneens via de kabelstructuur gecontroleerd.

Maak vervolgens een overzicht van kabeldelen en echte verbindingen: bestaande voeding, stationsuitgang, verbindingsmof, aftakmof, eindmof en eindpunt. Behoud WFS-deelgrenzen voor de traceerbaarheid; een geometrisch objecteinde bewijst op zichzelf nog niet welk moftype aanwezig is of dat het elektrische pad daar eindigt. Een lijnkruising is alleen een verbinding als de bron dit onderbouwt.

**Selecteer kabels op de functie in de WFS-kolom `omschrijving`:**

| Functie uit `omschrijving` | Gebruik in de LS-tekening |
|---|---|
| LS | Opnemen in de aansluitkoppeling, netstructuur en LS-berekening. |
| LS/OV | Ook opnemen: deze kabel heeft een LS-functie. Lees het fysieke kabeltype en de combi-uitvoering uit de KLIC. |
| Alleen OV | Uitsluiten van deze LS-uitwerking; niet als LS-voeding, aansluitpad of LS-belasting meetellen. |
| Ontbrekend of onduidelijk | Als open punt vastleggen en de functie verifiëren voordat de kabel als LS wordt gebruikt. |

De gecontroleerde hoofdkabeldata bevatten bijvoorbeeld `Laagspanningskabel met functie LS`, `Laagspanningskabel met functie LS/OV` en `Laagspanningskabel met functie OV`. De aansluitkabeldata bevatten `Aansluitkabel met functie LS.`. Lees de functie uit de omschrijving en houd rekening met spaties, hoofdletters en afsluitende leestekens. Sluit niet ieder label met `OV` uit: **LS/OV is juist nodig voor deze LS-tekening**. Leid de functie niet alleen af uit de laagnaam, kabelcode of nabijheid. De bekeken aansluitpunten hebben omschrijving `Huisaansluiting`; hun LS-koppeling wordt vastgesteld via de bijbehorende aansluitkabel en hoofdkabel, niet door op het aansluitpunt zelf een letterlijke LS-omschrijving te eisen.

Bewaar de oorspronkelijke `omschrijving` en de herleide functie bij ieder kabelobject in het register. Controleer daarnaast de status: een buitengebruikgesteld of fictief stuk wordt niet automatisch als actieve voeding aangemerkt. Een functie LS/OV bepaalt niet zelfstandig de doorsnede, het materiaal of de noodzaak van een nieuwe combikabel. Bij verschillen tussen WFS en KLIC worden peildatum en brongegevens naast elkaar vastgelegd en wordt de afwijking uitgezocht. De actuele bestaande situatie vervangt niet stilzwijgend een al vastgesteld nieuw ontwerp bij een buurstation.

Volg verbonden kabeldelen buiten een rode grens door tot de werkelijke elektrische scheiding. De gebiedsgrens is een ruimtelijke grens en geen rekenkundig kabeluiteinde. Leg bij hergebruik vast hoe de kabel van zijn bestaande voeding wordt gescheiden en aan de nieuwe richting wordt gekoppeld. Beoordeel ook wat er met de achterblijvende aansluitingen op die bestaande voeding gebeurt.

**Uitkomst:** één aansluitregister met de keten ontwerpstroomrondje → aansluitpunt → aansluitkabel → hoofdkabel/aftak → KLIC-kabeltype, en een onderbouwd overzicht van de kabelgroepen, zelfstandige richtingen, aftakken, bestaande voedingen en mogelijke scheidingspunten. Deze oorspronkelijke kabeltoewijzing is ook de basis voor de latere beslissing over overzetters.

## 4. Stationsbelasting bepalen door categorievertaling

Vertaal **iedere aansluiting via haar aansluitcategorie** naar de juiste kabel- én trafowaarden van het gekozen kader. De aantallen en categorieën worden bewaard; daardoor kan een gewijzigde richtingtoewijzing steeds opnieuw worden doorgerekend.

Bereken per station:

`Itrafo,verbruik = Σ(aantal per categorie × trafowaarde verbruik per categorie)`

`Itrafo,opwek = Σ(aantal per categorie × trafowaarde opwek per categorie)`

`Itrafo,maatgevend = max(Itrafo,verbruik; Itrafo,opwek)`

De maximaal toegestane trafo-ontwerpstroom wordt voor iedere trafocapaciteit berekend met de door Luka opgegeven formule:

`Itrafo,max [A] = trafocapaciteit [kVA] ÷ 0,23 [kV] ÷ 3`

Hier is 0,23 de fasespanning in kV en 3 het aantal fasen. De capaciteit in kVA is de variabele invoer. Reken met de ongeronde uitkomst; rond alleen af voor presentatie.

| Trafocapaciteit | Berekening | Maximale trafo-ontwerpstroom, afgerond |
|---:|---|---:|
| 630 kVA | 630 ÷ 0,23 ÷ 3 | 913,0 A |
| 400 kVA | 400 ÷ 0,23 ÷ 3 | 579,7 A |
| 250 kVA | 250 ÷ 0,23 ÷ 3 | 362,3 A |

Beide situaties moeten voldoen: `Itrafo,verbruik ≤ Itrafo,max` en `Itrafo,opwek ≤ Itrafo,max`. De resterende traforuimte is `Itrafo,max − Itrafo,maatgevend`. Een negatieve uitkomst betekent een overschrijding. De categorievertaling bepaalt de benodigde stroom; bovenstaande formule bepaalt de beschikbare capaciteit. Pas bij een andere trafocapaciteit de kVA-invoer aan en bereken de grens opnieuw.

Voorbeelden uit kader 2024:

| Categorie | Kabelwaarde verbruik | Trafowaarde verbruik | Trafowaarde opwek |
|---|---:|---:|---:|
| Type 1 — rijtjeswoning | 7,8 A | 7,0 A | 7,3 A |
| Type 1 — twee onder een kap | 8,8 A | 8,0 A | 7,3 A |
| Type 1 — vrijstaand | 10,3 A | 9,5 A | 9,5 A |
| Type 1 — onbekend woningtype | 8,4 A | 7,6 A | 7,3 A |

De volledige categorietabel komt uit de bronwerkmap. De voorbeelden hierboven zijn geen volledige catalogus. Een stroomwaarde wordt alleen naar een categorie vertaald als de koppeling eenduidig is; anders is aanvullende aansluitinformatie nodig. De som van kabelstromen, een algemene omrekenfactor en de som van afzonderlijke richtingmaxima vervangen de trafoberekening niet.

**Bij geen uitgewerkte stations:** pas de voorlopige stationsverdeling aan totdat alle stations kunnen voldoen, met uitvoerbare kabelroutes. **Bij uitgewerkte buren:** beoordeel eerst oplossingen binnen het nog uit te werken gebied; reken een overdracht aan de grens voor beide betrokken stations door.

## 5. Kabelrichtingen opbouwen en hergebruik kiezen

Onderzoek welke bestaande kabelgroepen en kabelstukken behouden kunnen worden. Beoordeel de bestaande kabels inclusief hun dunnere aftakken; een bruikbare hoofdstreng kan door een zijtak toch een lagere afzekering krijgen.

Maak per richting een samenhangend ontwerp met:

- toegewezen aansluitingen en hun categorieën;
- nieuwe en hergebruikte kabeldelen met fysieke lengtes en kabeltypes;
- uitvoerbare route vanaf het station;
- benodigde scheidingen, verbindingsmoffen, aftakmoffen, eindmoffen en overzettingen;
- alle hoofdeinden en aftakeinden waarop de richting wordt getoetst;
- passende uitrusting binnen het beschikbare aantal richtingen.

**Nieuwe LS-kabels zijn standaard altijd 150Al.** De standaarduitvoering is een aparte LS-kabel en een aparte OV-kabel. De OV-kabels worden in de afzonderlijke OV-tekening uitgewerkt. Het LS-ontwerp houdt de relevante raakvlakken met die tekening herkenbaar; de 150Al-keuze voor dit LS-ontwerp bepaalt niet het kabeltype in de aparte OV-tekening.

**Vrije moflocatie op een bestaande kabel (aanvulling Luka, 5 oktober 2026):** een nieuwe voeding mag op ieder geschikt punt van een bestaande kabel worden ingemofft, ook midden in een kabeldeel. De mof hoeft niet op het oorspronkelijke beginpunt, eindpunt of een WFS-objectgrens te liggen. Onderzoek deze mogelijkheid actief om kabelkruisingen te voorkomen en hergebruik mogelijk te maken. Leg de exacte moflocatie en de gekozen verbinding vast. Splits het bestaande kabeldeel op die locatie in de netstructuur en bereken vanaf de mof ieder gevoed vervolgpad afzonderlijk, met de nieuwe voedingskabel als gemeenschappelijk pad. Leg zo nodig scheidingen vast zodat er geen onbedoelde koppeling met een andere voeding ontstaat. Aansluitingen die op hun oorspronkelijke bestaande kabel blijven krijgen hierdoor geen overzetter. Controleer de plek ook op ruimte, kabeltype, stoep, bomen, grondpositie en gevolgen voor de afzonderlijke OV-uitwerking bij een combikabel.

### Tracé, kruisingen, bomen en grondpositie

**Kabels mogen elkaar niet kruisen.** Ontwerp zowel de fysieke kabelroutes als de getekende lijnen zonder kabelkruisingen. Leg lijnen consequent naast elkaar. Gebruik volgens Luka's aanvulling van 5 oktober 2026 **0,20 m onderlinge offset tussen richtingen** op gedeelde tracés en mooie rechte lijnstukken tussen noodzakelijke bochten. Vermijd rasterachtige trapjes en onnodige knikken. Controleer na het vereenvoudigen opnieuw de fysieke ligging, bochten, aansluitingen en kruisingen. Controleer dit ook bij stationsuitgangen, bochten, moffen, aftakken, aansluitoverzettingen en overgangen naar andere stationsgebieden. Een bedoelde verbinding in een mof wordt als verbinding weergegeven; een kruising is geen vervanging voor een mof. Los een kruising op door de route, lijnvolgorde of aansluitingstoewijzing te herzien en bereken gewijzigde paden opnieuw. Alleen een lijn voor de leesbaarheid verschuiven lost een fysieke kruising niet op.

**Het kabeltracé ligt bij voorkeur in de stoep en gaat niet door bomen.** Gras, pleinen en andere betegelde of verharde oppervlakken zijn eveneens toegestaan (aanvulling Luka, 5 oktober 2026). Beoordeel daar dezelfde voorwaarden voor bomen, grondpositie, ruimte en uitvoerbaarheid; deze oppervlakken worden niet als verboden gebied behandeld. Gebruik bijvoorbeeld **BGT via PDOK** om stoepen, parkeerplaatsen en wegen te onderscheiden en de route op de topografie te beoordelen. [PDOK biedt de BGT als kaart en als opvraagbare objectgegevens aan](https://www.pdok.nl/introductie/-/article/basisregistratie-grootschalige-topografie-bgt-). Bewaar bron, opvraagdatum en relevante objectidentificaties; vergelijk de bron met de projecttopografie. Gebruik daarnaast de bomenbron om bomen en beschikbare beschermingszones te herkennen. Vermijd bomen en de vastgelegde boom-/wortelbeschermingszones; verzin geen algemene afstand wanneer een projectafstand ontbreekt. De parallelle kabelbundel moet in de beschikbare strook passen, ook in bochten en bij versmallingen. Controleer de fysieke route én de weergegeven lijnen op deze voorwaarden.

**Als het niet anders kan, mag het tracé door parkeerplaatsen en mag het de weg oversteken.** Onderzoek eerst een uitvoerbare stoepvariant en beperk weg oversteken tot zo weinig mogelijk plaatsen. Iedere wegoversteek is **recht, zonder boog in de kabels binnen de oversteek**. Wanneer meerdere kabels moeten oversteken, gebruiken zij **dezelfde oversteekplaats**, naast elkaar en zonder onderlinge kruisingen. Beoordeel daarom de oversteek voor de gezamenlijke kabelbundel en de betrokken stations; kies niet per richting een afzonderlijke oversteek. Geef de gemeenschappelijke oversteek een identificatie en leg de kabels, rechte geometrie, reden, vergeleken alternatieven, grondpositie en fysieke lengtes vast. Een wegoversteek is toegestaan binnen deze voorwaarden; kabels die elkaar kruisen blijven uitgesloten.

**Vermijd privéterrein waar mogelijk**, omdat dit volgens de projectuitgangspunten een moeilijk en lang proces kan veroorzaken. Geef voorkeur aan een uitvoerbaar tracé op gemeentelijke of andere overheidsgrond. Beoordeel mogelijke routes met perceelgrenzen én actuele eigendoms-/beheerinformatie. Een stoep, openbare toegankelijkheid of een kadastrale perceelgrens bewijst op zichzelf geen overheidseigendom.

Leg per betrokken perceel en tracédeel vast: perceelidentificatie, geraadpleegde bron en datum, eigenaar-/beheerklasse (gemeente, andere overheid, privé of onbekend), de onderbouwing en eventuele relevante projectvoorwaarden. Noteer eigenaar en beheerder afzonderlijk waar ze verschillen. Een onbekende grondpositie wordt niet als gemeentelijke grond aangenomen. Maak een alternatief langs de stoep op geverifieerde overheidsgrond wanneer een route privégrond raakt. Als privégrond onvermijdelijk lijkt of eigendom niet kan worden vastgesteld, toon de locatie en alternatieven als open ontwerppunt; neem de doorgang niet stilzwijgend als definitief uitvoerbaar aan.

**Gebruik uitgewerkte buurgebieden als aanvullende tracéreferentie (aanvulling Luka, 5 oktober 2026):** bekijk over welke delen van de topografie de bestaande stationsontwerpen lopen. Vergelijk die ligging met de BGT en de projecttopografie om te herkennen welke stoepen, grasstroken, pleinen en verhardingen in het project voor kabeltracés worden gebruikt. Neem passende voorbeelden mee in de routekeuze en houd dezelfde lijnopbouw aan. Beoordeel voor het nieuwe tracé ook de lokale ruimte, bomen, oversteek en grondpositie.

**Gezamenlijke kabelgleuf als ontwerpdoel (aanvulling Luka, 5 oktober 2026):** gebruik het uitgewerkte stationsgebied **011.602** als voorbeeld. Houd richtingen zo lang mogelijk gebundeld naast elkaar, met 0,20 m onderlinge offset, zodat de uitvoering één gezamenlijke gleuf kan gebruiken. Bepaal eerst een gemeenschappelijk hoofdtracé en laat een richting pas op een functioneel noodzakelijk punt uit de bundel gaan. Onderzoek vrije moflocaties op bestaande kabels om die bundeling te behouden en onnodige afzonderlijke sleuven te voorkomen. Vergelijk varianten op de gezamenlijke graafroute; de som van afzonderlijk kortste kabelroutes is geen bewijs van de kleinste benodigde graaflengte. Behoud ook in de bundel de kabelcapaciteit, kruisingsvrije volgorde, rechte gemeenschappelijke wegoversteken en de lokale voorwaarden voor ruimte, bomen en grondpositie. Leg de gezamenlijke gleufdelen en de reden van iedere splitsing vast. De getekende kabeloffset bepaalt niet zelfstandig de volledige uitvoeringsbreedte of aanlegdiepte van de sleuf.

Vergelijk tracévarianten op kruisingvrij verloop, voorkeur voor de stoep, noodzaak van parkeerplaatsdoorgang, minimaal aantal rechte en gezamenlijke wegoversteekplaatsen, boomvrij verloop, grondpositie, fysieke ruimte, kabelcapaciteit en gevolgen voor andere stations. Een korter kabelpad heeft niet automatisch voorrang op deze tracévoorwaarden. BGT-geometrie vervangt de eigendoms-/beheercontrole niet.

**Gebruik alleen een combikabel wanneer aansluiting op een bestaande combikabel nodig is om aansluitingen van stroom te voorzien.** Een kabelgeulaanduiding zoals `50+6` met kabelcode duidt een bestaande combikabel aan. Een nieuwe kabel die daarmee wordt verbonden krijgt de kabeltekst **`150Al+`**; een gewone nieuwe LS-kabel krijgt **`150Al`**. Bewaar de combi-eigenschap en de betreffende overgang bij het kabeldeel en de mof. De aanvullende ader wordt niet als parallelle hoofddoorsnede in de LS-berekening opgeteld. Een combikabel in de omgeving is op zichzelf geen reden om een nieuwe combikabel te kiezen.

**Beslis overzettingen per aansluiting en plaats de blokken pas na de definitieve kabeltoewijzing:**

| Ontworpen aansluiting | `OVERZETTER` naast het ontwerpstroomrondje |
|---|---|
| De aansluiting komt op een nieuwe kabel terecht. | Ja. |
| De aansluiting blijft op dezelfde bestaande kabel waarop zij al zit. | Nee. |
| De aansluiting blijft op haar oorspronkelijke bestaande kabel, die via een nieuwe kabel en mof een andere voeding krijgt. | Nee. |

Een gewijzigde stationsvoeding, gebiedsgrens of richtingkleur is op zichzelf geen overzetting. De vergelijking betreft de kabel waarop de aansluiting wordt aangesloten. Leg in het aansluitregister de beslissing en reden vast. Moffen tussen nieuwe en bestaande hoofdkabels worden apart bepaald; zo'n mof betekent niet dat alle aansluitingen op het behouden kabelstuk overzetters krijgen.

Verdeel aansluitingen op basis van kabelstructuur, route, belasting, lengtegrens en uitvoering. Gelijke aantallen woningen per richting zijn geen zelfstandige ontwerpregel. Gebruik geverifieerde projectafspraken voor tijdelijke, reserve- of bijzondere richtingen; leid bijvoorbeeld een verplichte `80A Tamp`-bezetting niet alleen uit één voorbeeld af.

**Huisaansluitkabels en moffen (aanvulling Luka, 5 oktober 2026):** huisaansluitkabels maken geen deel uit van het richtingdesign. Gebruik ze uitsluitend als bron om aansluitingen aan de juiste hoofdkabel te koppelen en de belasting toe te wijzen. Neem ze niet als LS-hoofdkabeltakken op in de tracégeometrie of de lengte-/afzekeringsberekening van de richting en plaats geen eindmof bij iedere huisaansluitkabel. Teken moffen alleen op het ontworpen hoofdkabelnet: daadwerkelijke verbindingen, hoofdkabelaftakken, scheidingen en kabeluiteinden. De rondjes en hun ontwerpstromen blijven wel meetellen voor richting en trafo; de eerdere overzetterregel blijft gelden.

## 6. Richtingen berekenen, inclusief aftakkingen

Bereken per richting verbruik en opwek afzonderlijk met de **kabelwaarden** van de categorieën. Alle aansluitingen op de hoofdstreng en aftakken tellen eenmaal mee. Bij een automatische beoordeling is het hoogste totaal maatgevend; een andere expliciet gekozen stroombasis wordt vastgelegd.

Meet ieder fysiek kabeldeel met de bevestigde tekeneenheid. Lees echte booglengtes mee. Gebruik bij grafisch verschoven of parallel weergegeven lijnen de vastgestelde fysieke rekenroute; tel de weergavelijnen niet als meerdere elektrische kabels op.

Toets ieder volledig pad vanaf het station naar een hoofd- of aftakeinde. Per pad:

`R = Σ(R per km × lengte in meter / 1000)`

`X = Σ(X per km × lengte in meter / 1000)`

`Z = √(R² + X²)`

Controleer impedantie, stroombelastbaarheid van iedere doorsnede, passende belastingverdeling en de fysieke kabelverjonging. Gebruik de bronwaarden van het gekozen kader. Bij twijfel over de belastingverdeling worden de ondersteunde profielen doorgerekend en wordt de ongunstigste uitkomst aangehouden totdat een andere keuze onderbouwd is.

**Vaste aftakregel:** het gemeenschappelijke kabelstuk tot de aftakmof wordt in ieder afzonderlijk volledig pad eenmaal opgenomen. De hoofdkabel na de mof en de zijtakken worden als afzonderlijke vervolgpaden getoetst. Hun lengtes worden niet als één lange seriekabel achter elkaar opgeteld. Bij meerdere aftakmoffen worden alle complete eindpaden beoordeeld.

De **laagste maximaal toegestane afzekering van alle paden geldt voor de hele richting**. De totale richtingbelasting, inclusief aftakken, moet onder de bijbehorende maximale ontwerpstroom blijven. Er worden geen aparte aftakzekeringen verondersteld om een beperkende zijtak buiten de beoordeling te laten.

Voor de gecontroleerde 2024-bron gelden onderstaande stappen:

| gG | Max. ontwerpstroom | Z-max evenredig | Z-max laatste helft |
|---:|---:|---:|---:|
| 63 A | 57 A | 0,250 Ω | 0,215 Ω |
| 80 A | 72 A | 0,250 Ω | 0,170 Ω |
| 100 A | 90 A | 0,204 Ω | 0,136 Ω |
| 125 A | 113 A | 0,163 Ω | 0,109 Ω |
| 160 A | 144 A | 0,128 Ω | 0,085 Ω |
| 200 A | 180 A | 0,092 Ω | 0,068 Ω |
| 250 A | 225 A | 0,062 Ω | 0,055 Ω |

Een maximale kabellengte hoort bij een kabeltype, samenstelling, belastingprofiel en afzekering. Er is geen universele lengte per doorsnede. Voor gemengde kabelpaden worden R en X samengesteld; afzonderlijke lengtegrenzen mogen niet worden opgeteld.

Als een richting niet voldoet, onderzoek dan een andere aansluitverdeling, een extra beschikbare richting, een andere scheiding of vervanging van het beperkende bestaande kabeldeel door 150Al. Kies niet zelfstandig een ander standaardtype voor nieuwe kabels. Een nieuwe berekening omvat ook de betrokken aftakken en eventuele gevolgen voor buurstations. Bij een gewijzigde kabeltoewijzing wordt de beslissing over overzetters opnieuw gecontroleerd.

## 7. Stationsverdeling en gebiedsgrenzen afronden

Maak de gebiedsgrens definitief op basis van de gecontroleerde ontwerpbestemming van de aansluitingen en de uitvoerbare kabelscheidingen. Een bestaande rode grens is het vertrekpunt; als deze tot een onuitvoerbare verdeling leidt, wordt een onderbouwde aanpassing voorgesteld.

Controleer na iedere relevante wijziging:

- de belasting en kabelpaden van de getroffen richtingen;
- de categorieaantallen en trafobelasting van beide betrokken stations;
- de scheiding van de bestaande voedingen;
- de mogelijkheden voor nog onuitgewerkte aangrenzende stations;
- unieke aansluitingstoewijzing en aansluitende gebiedsgrenzen.

Rond een station niet af als daarmee noodzakelijke aansluitingen zonder haalbare voeding bij een ander station achterblijven. Werk een onzekere grens of aansluiting herkenbaar uit als open punt.

## 8. Dezelfde vormgeving gebruiken, ook zonder uitgewerkte buren

Leg de goedgekeurde vormgeving als zelfstandige stijlreferentie vast. Die bevat de laageigenschappen, benodigde blokdefinities, tekststijlen, lijnopbouw, voorbeeldlabels en een volledig uitgewerkt stationsvoorbeeld. Daardoor hoeft een nieuwe tekening geen al ingevuld station te bevatten om dezelfde vormgeving te kunnen gebruiken.

Voor de huidige Laarbeek-referentie geldt:

| Onderdeel | Vormgeving |
|---|---|
| Gebied | Gesloten rode polyline op `01 - Stationsgebied`, ACI 1, vaste breedte 1,0. |
| Richtingen | `Aansluiting LS K01` t/m `K12`; behoud de vastgelegde kleuren: 4, 52, 5, 3, 6, 30, 252, 244, 114, 1, 190, 201. |
| Bestaande kabels | `01 - Bestaande kabel`, ACI 250; nummering en hergebruik herkenbaar houden. |
| Moffen | Bestaande blokken `NIEUWE MOF`, `MOF bestaand-nieuw` en `BESTAANDE MOF`; bijbehorende VM/AM/EM-notatie en herkenbare combi-overgang waar van toepassing. |
| Overzettingen | Bestaand `OVERZETTER`-blok uitsluitend bij aansluitingen die naar een nieuwe kabel gaan; pas plaatsen na definitieve toewijzing. Geen blok als de aansluiting op haar oorspronkelijke bestaande kabel blijft. |
| Aansluitingen | Bestaande `KA_K01`-blokken en ontwerpstroomteksten op `Aansluiting LS_OntwerpstroomKabel`, stijl ARIAL, hoogte 0,75. |
| Richtingoverzicht | Passend bestaand RT-blok; richtingkleur, gekozen afzekering, bekende kabelnummering en kabeltype. |
| Kabelteksten | Gewone nieuwe LS-kabel: `150Al / ????-00`. Noodzakelijke nieuwe combi-verbinding met een bestaande combikabel: `150Al+ / ????-00`. Behoud de bestaande kabelnotatie voor hergebruik; onbekende nummers zichtbaar als onbekend. |
| Resultaten | Decimale komma, `Amp.` en `Met.` volgens de referentie. |

Gebruik dezelfde parallelle lijnopbouw, afstanden, blokoriëntaties en tekstplaatsing als de goedgekeurde referentie. Leg de weergegeven lengte bij een vertakte richting eenduidig vast en laat deze overeenkomen met het aangegeven rekenpad. Een blok wordt beoordeeld op zijn zichtbare geometrie en attribuutlocaties, niet uitsluitend op het invoegpunt.

Houd alle kabelweergavelijnen naast elkaar zonder kruisingen. Controleer de ligging ten opzichte van stoep, bomen en perceelgrenzen op planschaal én bij detailaanzicht. Een grafische verschuiving mag geen onuitvoerbare fysieke route maskeren.

Bij een lege ontwerptekening worden de benodigde stijlonderdelen uit de referentie of projecttemplate overgenomen. Kopieer daarmee geen oude stationsnummers, kabelnummers, belastingen of zekeringresultaten. Bij bestaande uitwerking worden de projecteigenschappen hergebruikt en relevante afwijkingen eerst vastgesteld.

## 9. Controle en oplevering

Een stationsgebied is gereed wanneer:

1. alle aansluitingen binnen de afgesproken scope precies eenmaal zijn toegewezen, of expliciet als onopgelost zijn gemeld;
2. huidige en ontworpen voedingen, aftakken en scheidingen traceerbaar zijn; de WFS-kabelfunctie via `omschrijving` is gecontroleerd, LS en LS/OV zijn meegenomen en uitsluitend OV is uitgesloten van de LS-uitwerking;
3. alle volledige kabelpaden voldoen en de laagste toelaatbare afzekering correct op de hele richting is toegepast;
4. de volledige richtingbelasting past onder de bijbehorende ontwerpstroomgrens;
5. de categorievertaling voor de trafo compleet is en de maatgevende stroom maximaal `trafocapaciteit in kVA ÷ 0,23 ÷ 3` bedraagt, getoetst met ongeronde waarden;
6. de beschikbare richtingen en bijzondere functies zijn gerespecteerd;
7. wijzigingen op gebiedsovergangen voor alle getroffen stations zijn gecontroleerd;
8. de vormgeving overeenkomt met de stijlreferentie en op planschaal leesbaar is;
9. tracés, moffen, labels, richtingoverzichten en berekeningen dezelfde ontwerpkeuzes weergeven;
10. ieder geplaatst overzetterblok hoort bij een aansluiting die naar een nieuwe kabel gaat en geen overzetter staat bij een aansluiting die op haar oorspronkelijke bestaande kabel blijft;
11. alle nieuwe LS-kabels 150Al zijn, combi uitsluitend voor noodzakelijke aansluiting op een bestaande combikabel wordt gebruikt, die nieuwe kabels als 150Al+ zijn gelabeld en de standaard-OV-uitwerking in de afzonderlijke OV-tekening blijft;
12. fysieke kabelroutes en weergegeven lijnen geen kabelkruisingen hebben en de lijnen naast elkaar staan;
13. de kabelroutes bij voorkeur in de stoep liggen en bomen en vastgelegde beschermingszones vermijden; noodzakelijke parkeerplaatsdoorgangen zijn onderbouwd en wegoversteken zijn geminimaliseerd, recht zonder boog uitgevoerd en voor meerdere kabels op dezelfde oversteekplaats gebundeld;
14. perceelgrenzen en grondpositie per relevant tracédeel zijn beoordeeld met herleidbare eigendoms-/beheerinformatie, privégrond waar mogelijk is vermeden en onbekende grondposities of onvermijdelijke privédoorgangen expliciet als onopgelost zijn vermeld.

Lever op: de uitgewerkte tekening, een aansluitingstoewijzing, een controleoverzicht per richting en per station, en eventuele resterende beslispunten. Het richtingoverzicht bevat de kabeldelen, fysieke lengtes, profielen, paduitkomsten, maatgevend pad, afzekering en resterende stroomruimte. Het stationoverzicht bevat de aantallen per categorie, verbruik, opwek, capaciteit en resterende traforuimte.

Voor meerdere stations hoort ook een projectoverzicht bij de controle: unieke aansluitingstoewijzing, stationsbelasting en status per station. Dit voorkomt dat afzonderlijk passende ontwerpen gezamenlijk aansluitingen missen of dubbel tellen.

## 10. Basis voor de toekomstige vaardigheid

Na jouw beoordeling wordt deze algemene werkwijze vastgelegd in de vaardigheid, met de goedgekeurde stijlreferentie en een projectinvoer voor kader, stations, uitrusting en ontwerpstatus. De twee beginsituaties worden expliciet ondersteund. Station 011.601 blijft een voorbeeld met eigen gegevens; het stationnummer, de voorlopige 125 aansluitingen en de betreffende kabelnummers worden geen algemene voorschriften.

De vaardigheid bewaart de categorieën en bronversie en bevat controles voor aftakken, scheidingen, richtingcapaciteit, trafocapaciteit en samenhang tussen stations. Zij koppelt aansluitpunt, aansluitkabel en hoofdkabel via WFS-code én geometrie en koppelt het kabeltype via de KLIC-geulentekst. Zij bevat expliciet de `-01`-uitzondering voor een eigen richting met één aansluiting en de materiaalregel zonder `Al` = Cu. Zij bewaart per aansluiting de oorspronkelijke en ontworpen kabel en leidt daaruit de overzetters af. Zij hanteert 150Al als standaard voor nieuwe kabels en maakt 150Al+ alleen voor de vastgelegde noodzakelijke combi-verbinding. De trafo-stroomgrens wordt berekend uit de kVA-invoer met `kVA ÷ 0,23 ÷ 3`; 913 A wordt niet als vaste limiet voor alle stations opgeslagen. Een kabelchecker die alleen geselecteerde serielengtes berekent, wordt aangevuld met deze netstructuur- en toewijzingscontrole.

De toekomstige vaardigheid selecteert kabels via de functie in WFS-kolom `omschrijving`: LS en LS/OV worden meegenomen; uitsluitend OV wordt uitgesloten van de LS-uitwerking. Aansluitpunten worden via hun kabelverbinding beoordeeld en onduidelijke functies blijven open punten.

De toekomstige vaardigheid toetst kabelroutes en lijnweergave op kruisingen, parallelle ligging, stoepgrenzen, bomen en vastgelegde beschermingszones. Zij gebruikt bijvoorbeeld BGT via PDOK voor stoepen, parkeerplaatsen en wegen. Stoeptracés hebben voorkeur; noodzakelijke parkeerplaatsdoorgangen en wegoversteken zijn toegestaan. Zij minimaliseert het aantal oversteekplaatsen, voert iedere oversteek recht zonder boog uit en bundelt meerdere overstekende kabels naast elkaar op dezelfde plaats. Zij betrekt perceelgrenzen en eigendoms-/beheerbronnen bij de routekeuze, geeft voorkeur aan geverifieerde gemeentelijke of andere overheidsgrond en vermijdt privégrond waar mogelijk. Ontbrekende eigendomsinformatie wordt niet vervangen door een aanname dat een openbare stoep gemeentelijk eigendom is.

## Bronnen en vastgelegde uitgangspunten

- Aanvullende tracéregels van Luka: geen kruisende kabels; lijnen naast elkaar; voorkeur voor de stoep; niet door bomen; privéterrein zoveel mogelijk vermijden; perceelgrenzen bekijken en gemeentelijke/overheidsgrond onderscheiden van privégrond. BGT via PDOK kan worden gebruikt voor de topografie. Als het niet anders kan zijn parkeerplaatsdoorgangen en wegoversteken toegestaan; beperk het aantal wegoversteken, voer ze recht zonder boog uit en gebruik voor meerdere kabels dezelfde oversteekplaats. De definitieve tracé- en eigendomscontrole is onderdeel van de latere ontwerpuitwerking en is met dit document nog niet uitgevoerd.

- [PDOK — BGT-bron en toegang tot kaart-/objectgegevens](https://www.pdok.nl/introductie/-/article/basisregistratie-grootschalige-topografie-bgt-), geraadpleegd op 2 oktober 2026. Deze bronverificatie is nog geen BGT-tracécontrole van 011.601.

- Aanvullende WFS-selectieregel van Luka: controleer `omschrijving`; LS en LS/OV horen bij deze LS-tekening, uitsluitend OV niet. Deze regel is ook gecontroleerd tegen de omschrijvingen in de begrensde WFS-selectie.

- Luka's instructies: aftakken afzonderlijk toetsen met hun gemeenschappelijke voedingsstuk; laagste toelaatbare afzekering voor de hele richting; aansluitcategorieën vertalen naar trafowaarden; **maximale trafo-ontwerpstroom = kVA ÷ 0,23 ÷ 3** (630 kVA is circa 913 A); beide beginsituaties ondersteunen; overzetters uitsluitend bij aansluitingen die naar een nieuwe kabel gaan; nieuwe kabels standaard altijd **150Al**; combi alleen bij noodzakelijke aansluiting op een bestaande combikabel, met kabeltekst **150Al+**; standaard aparte LS- en OV-kabels, met OV in een afzonderlijke tekening; WFS voor aansluitkoppelingen en kabelcodes, KLIC voor kabeltypes; de `-01`-uitzondering voor eigen richtingen met één aansluiting; zonder `Al` bij de doorsnedecijfers is het materiaal Cu.
- [Enexis-WFS: mogelijkheden en beschikbare lagen](https://opendata.enexis.nl/geoserver/wfs?service=WFS&request=GetCapabilities&version=2.0.0). De drie genoemde laagschema's en een begrensde Laarbeek-selectie zijn gecontroleerd op 2 oktober 2026; de bekeken objecten hadden peildatum 26 september 2026. Er is nog geen definitieve koppeling van alle 125 ontwerpstroomrondjes uitgevoerd.
- Laarbeek-projecttekening en beschikbare KLIC- en toporeferenties, onderzocht op 2 oktober 2026, voor de stijlreferentie en het praktijkvoorbeeld.
- [Kabelchecker: gecontroleerde bronversie](https://github.com/LukaStuurman/AutoCAD-Enexis-kabels-checker/tree/4009601e15fa4b1b6926380395132b0c1630ce21).
- [2024-bronwerkmap Eea-0205.K 1.0](https://github.com/LukaStuurman/AutoCAD-Enexis-kabels-checker/blob/4009601e15fa4b1b6926380395132b0c1630ce21/src/Enexis.KabelChecker.AutoCAD/Resources/Eea-0205.K%201.0%20-%20Copy.xlsx).
- [Kabelrekenregels en kabelcatalogus](https://github.com/LukaStuurman/AutoCAD-Enexis-kabels-checker/blob/4009601e15fa4b1b6926380395132b0c1630ce21/docs/excel-model.md).
- [Gescheiden kabel- en trafowaarden per kader](https://github.com/LukaStuurman/AutoCAD-Enexis-kabels-checker/blob/4009601e15fa4b1b6926380395132b0c1630ce21/docs/ontwerpstroom-per-kader.md).

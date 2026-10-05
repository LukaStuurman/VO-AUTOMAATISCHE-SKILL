# Referentieanalyse: 011.601 correct

Proceskalibratie op Luka's gecorrigeerde DXF en ingevulde 2024-werkmap, 5 oktober 2026.

## Gewijzigde uitgangspunten

De rode grens en de 125 aansluitrondjes zijn behouden. Rondje 1113BD is verplaatst en aangepast van 8,4 naar 4,6 A. De werkmap benoemt dit als Type 8, netbewust publiek laden 3×25A: 3,8 A trafoverbruik, zonder opwekbijdrage in deze categorie.

De categorieën zijn 112 rijtjeswoningen, 10 twee-onder-een-kap, 2 vrijstaand en 1 publieke laadvoorziening. Dit geeft **886,8 A trafoverbruik en 909,6 A trafo-opwek**. De 630 kVA-grens is 913,043478… A; maatgevende ruimte 3,443478… A. De eerdere 916,9 A hoorde bij de oorspronkelijke categorie-invoer en is geen actuele uitkomst voor de gecorrigeerde versie.

Zeven normale richtingen: R2, R3, R4, R5, R9, R10, R11. R6/R7/R8 vrij; RT1/RT12 met 80A Tamp. Er staan 78 OVERZETTER-blokken, tegenover 125 in de eerdere eigen variant. Blokaantallen ondersteunen behoud, maar bewijzen geen elektrische aansluitingstoewijzing. Bij een nieuw ontwerp volgt elke blokbeslissing uit het aansluitregister.

## Gereproduceerde kaderberekeningen

| Richting | Profiel | 150Al rekenpad m | 95Al rekenpad m | Kabelverbruik A | Kabelopwek A | gG A |
|---|---|---:|---:|---:|---:|---:|
| R2 | Evenredig | 257,49 | 0 | 179,4 | 172,5 | 250 |
| R3 | Evenredig | 223,82 | 0 | 163,8 | 157,5 | 250 |
| R4 | Laatste helft | 373,05 | 0 | 140,4 | 135,0 | 160 |
| R5 | Laatste helft | 298,86 | 53,05 | 129,4 | 120,0 | 160 |
| R9 | Laatste helft | 141,95 | 108,81 | 132,6 | 127,5 | 200 |
| R10 | Laatste helft | 201,03 | 145,51 | 109,9 | 99,8 | 125 |
| R11 | Evenredig | 37,73 | 104,78 | 131,3 | 122,3 | 200 |

Bron: bladen `Ontwerpstroom_kabel R…`, categorieaantallen en C/D; controlebladen Q18 (150Al), Q20 (95Al). Trafo: `Ontwerpstroom_trafo`, A5:D7 en A36:D36. De werkmap heeft geen berekende formulecaches. Dit is een onafhankelijke herberekening van expliciete invoer met het gecontroleerde 2024-model, geen native Excel-herberekening.

De gemeten nieuwe hoofdpolylines zijn achtereenvolgens 257,49; 223,82; 373,05; 367,62; 200,32; 201,03; 37,73 m, samen circa 1661,06 m. Dit is geen totale sleuflengte: gedeelde gleuven daarvoor eenmaal tellen.

De nieuwe hoofdtak van R5 is langer dan het gemengde kaderpad. Het **kortere pad met 95Al heeft meer impedantie en begrenst de afzekering**. R9 heeft eveneens een nieuwe hoofdroute en behouden 95Al-vervolg. Alleen de gekleurde nieuwe polyline meten is onvoldoende.

Bestaande 95Al blijft in R5/R9/R10/R11. Kabelgroep 6749-00 is verdeeld over R11 en R9; R11 neemt ook aftak 6749-01 mee. R10 behoudt 6733-00; R5 behoudt 6752-00. Een volgende automatische uitwerking moet daadwerkelijke isolaties en alle aansluitingstoewijzingen reconstrueren en toetsen; deze herberekening reproduceert de gekozen invoerpaden.

## Aangepast proces

1. Inventariseer groepen, belasting, categorieën en gecorrigeerde aansluitposities.
2. Onderzoek hergebruik, vrije moflocaties en splitsing over onafhankelijke richtingen.
3. Kies gezamenlijke gleuven langs de stoep en noodzakelijke nieuwe 150Al-voedingen.
4. Bereken alle volledige materiële paden met onderbouwd profiel.
5. Toets eerst het kabeluiteinde; als dat niet past de laatste aansluiting. Dezelfde belasting en alle zijtakken behouden. Rekeneindpunten onderscheiden van echte kabelscheidingen en eindmoffen.
6. Kies afzekeringen; werk daarna moffen, kabelteksten, overzetters en RT-overzicht uit.
7. Vergelijk stationsuitloop en totaalbeeld met de referentie; corrigeer bundelvolgorde, bochten en labels.

## Vormgeving

Per richting een logische nieuwe hoofdpolyline, BYLAYER, breedte 0 en rechte stukken tussen noodzakelijke bochten. Kabels lang gebundeld; 0,20 m onderlinge offset blijft de expliciete gebruikersregel. Grijze behouden stukken tellen mee in het elektrische pad.

Kabelinformatie bij herkenbare straatdelen van de bundel; stroom en lengte op afzonderlijke regels met `Amp.` en `Met.`. VM/AM/EM en RT-attributen volgen het project. Beoordeel zichtbare geometrie en attributen: het invoegpunt kan elders liggen. Projectnummering en resultaten niet kopiëren naar andere stations.

## Controle en grenzen

Het hulpmiddel reproduceert alle zeven afzekeringen en trafototalen. Zes gerichte tests controleren de referentie, beperkende aftakken, profileffect, laatste-aansluitingvariant zonder belastingverlies, dubbeltelling en variabele trafocapaciteit.

Dit valideert het rekenproces op de opgegeven paden. Volledige automatische tracégeneratie, alle mogelijke kabelpaden, eigendom en uitvoerbaarheid op nieuwe locaties zijn hiermee niet bewezen. De bron-DXF en werkmap zijn ongewijzigd; ze worden niet naar GitHub geüpload.

Bronnen: `011.601 correct/VO-LS PILS Laarbeek Beek D.26936 - Fase 7.dxf` en `011.601 correct/011.601 kader ingevuld.xlsx`. Hashes in `references/011601-correct.json`. Enexis Kabelchecker commit `4009601e15fa4b1b6926380395132b0c1630ce21`, kader 2024 Eea-0205.K 1.0.

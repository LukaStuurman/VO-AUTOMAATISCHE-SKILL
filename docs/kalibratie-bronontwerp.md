# Kalibratie van het bronontwerp — 011.601

Getest op 5 oktober 2026. De eerdere `maak_vo_tekening.py`-uitwerking gebruikte de gebruikersoplossing voor routes/toewijzingen en is een referentiegestuurde reconstructie. De nieuwe pipeline reconstrueert aansluitingen, kiest hergebruik/splitsingen, routes, vrije moffen, overdrachten en zekeringen uit oorspronkelijke bronnen. De oplossing is tijdens genereren door een runtime-leescontrole geblokkeerd en wordt pas in de evaluator gelezen.

Dit is kalibratie met kennis van de vergelijking, geen claim dat eerdere kennis is gewist. Algemene regels zijn na verschillen aangepast; er zijn geen voorbeeldroutes, kabelcodes, gewenste groepsaantallen, mofcoördinaten of zekeringen in de generator gezet. Eén expliciet bronfeit is gecorrigeerd: het oorspronkelijke niet betrouwbaar gekoppelde 8,4A-rondje is een geplande 4,6A-publieke laadvoorziening op de door de gebruiker gecorrigeerde locatie. Die categorie/locatie is projectinvoer, niet een opgelegde richting.

## Waarom de regels veranderden

| Gevonden probleem | Algemene aanpassing |
|---|---|
| Onafhankelijke kortste routes geven meerdere sleuven of ongunstige omwegen | Gezamenlijke route/oversteek eenmaal waarderen; kandidaatvoorraad daarna als één gleuf beoordelen |
| De kortste feeder kiest een onbruikbare mof | Nieuwe hoofdroute, behouden materiaalpaden en vervangen aftak tegelijk toetsen; moffen vrij op de oude main |
| Verlichting/huisaansluiting verkeerd als hoofdtak gebruikt | WFS LS/LS-OV-filter en code/geometriecontrole; service leads alleen voor bronkoppeling/belasting |
| Lang Cu-pad voldoet niet | Kleinste benodigde eindcluster naar een haalbare nabije nieuwe hoofdkabel overzetten; ontvangende richting volledig hertoetsen |
| Verschillende bochtvereenvoudigingen veroorzaken kruisingen | Gemeenschappelijke lijnas eenmaal vereenvoudigen, 0,20m lane-offsets, lokale gezamenlijke correctie |
| Een dun oud pad begrenst de richting | Alle hoofd-/aftakpaden met hun echte materialen; laagste maximaal toegestane zekering |
| Buitenste lanes raken de haag bij het station | Uitgang als doorgang voor volledige bundelbreedte toetsen, ook buiten het stationsblok |
| Oude bocht kruist de nieuwe bundel meerdere keren | Behouden downstream-geometrie als vaste route meewegen; mof langs oude kabel opschuiven vóór alle aansluitingen |
| Kleine terugloop bij een WFS-contact geeft een slechte offset | Terminale rasteroverschrijding wegwerken vóór de kabel naar de exacte vrije mof gaat |
| Rasterknikken in wegkruising | De complete wegkruising als recht segment vervangen en kruisingen/vegetatie opnieuw toetsen |
| Een kabelcode valt onder meerdere richtingen | Gebruikte delen verenigen vóór verwijdering; andere richtingen en externe/OV-voeding beschermen |

De lokale testreeks bevat ook afgebroken en mislukte kandidaten. Vooral alleen een langste-frontage-route als start kiezen gaf een te lange Cu-vervanging; die methode is niet als succesvolle uitkomst gepresenteerd. Kandidaten met kruisingen of vegetatieraakpunten zijn hersteld. Vroege ontwikkelruns zijn geen onveranderlijke softwarebenchmarks; de definitieve run bewaart bron- en scripthashes.

## Gemeten resultaat

Laatste gecontroleerde bronkandidaat: dezelfde 125 aansluitingen in dezelfde zeven richtingnummers, dezelfde zeven zekeringen en 78 overzetters/47 aansluitingen op hun oorspronkelijke kabel. Beide trafototalen komen overeen: 886,8A verbruik en 909,6A opwek bij een ongeronde 630kVA-limiet van 913,043478…A.

| Richting | Aansluitingen | Kabelontwerpstroom | Zekering |
|---|---:|---:|---:|
| R2 | 23 | 179,4A | 250A |
| R3 | 21 | 163,8A | 250A |
| R4 | 18 | 140,4A | 160A |
| R5 | 17 | 129,4A | 160A |
| R9 | 17 | 132,6A | 200A |
| R10 | 13 | 109,9A | 125A |
| R11 | 16 | 131,3A | 200A |

De vergelijking gebruikt de daadwerkelijk opgeslagen CAD-geometrie: circa **92,9% van het gebruikersreferentietracé ligt binnen 2m van de kandidaat**, en **81,6% van het kandidaatnet ligt binnen 2m van het referentienet**. Dit is tweezijdige corridordekking, geen pixelovereenkomst of identiek ontwerp. Routes en vrije moffen verschillen. De gekozen profielheuristiek gebruikt voor R3 laatste helft waar de ingevulde referentie evenredig gebruikt; de nieuwe fysieke route voldoet ook met dit strengere profiel en dezelfde 250A.

De kandidaat heeft geen gevonden nieuwe-nieuwe of nieuwe-behouden kruisingen, geen zelfkruisingen, geen doorsnijding van gebruikte actieve vegetatie-/boom/topo-obstakels, rechte wegsegmenten en een foutloze DXF-audit. Twaalf gerichte tests toetsen rekenen, categorieën/trafo, aftakken, dubbele telling, laatste-aansluitingterugval, BGT-plustype en bescherming van meerdere richtingen bij verwijdering.

## Beginsituatie en grenzen

Ook getest: dezelfde oorspronkelijke bron met 747 buurontwerp-entiteiten verwijderd. Stationlocaties, stroomrondjes, rode grenzen en bestaande bronkoppelingen blijven behouden; de lege lokale stijlset levert de benodigde moffen/overzetters/RT. Beide definitieve bronruns voldoen aan dezelfde controles. Aansluitingstoewijzingen en zekeringen zijn identiek; de maximale geometrieafwijking tussen beide nieuwe kabelnetten is 0 m. De verplaatste testbron heeft zijn native xrefpaden achteraf uit de oorspronkelijke bronmetadata hersteld, zonder routes of toewijzingen te wijzigen. Dit controleert de beginsituatie zonder ingevulde buurgebieden, niet een tweede onbekend station.

Stationaantal, richtingnummers, categoriecorrectie, trafocapaciteit en speciale RT-functies in deze tabel zijn projectfeiten. De volgende locatie krijgt eigen bronnen en uitrusting. De automatische maker ondersteunt de vier gevalideerde kabeltypes en eenvoudige boomstructuren; complexe lussen, wisselende materiaaltypen binnen één code of meerdere noodzakelijke splitsingen vragen uitbreiding.

Nog open: twee afwijkende LS/OV-WFS-labelkoppelingen, niet bewezen eigendom/beheer van betrokken percelen, echte wortelzones, gevolgen voor oorspronkelijke voedingen en actieve OV op oude combi. Drie oorspronkelijke xrefs ontbreken. De beschikbare KLIC/topo zijn gebruikt, maar het ontwerp wordt hierdoor niet als uitvoeringsgereed verklaard. Bron-CAD, ingevulde werkmap en volledige aansluitregisters blijven lokaal; de repository bevat generieke regels, code, stijl en deze samenvatting.

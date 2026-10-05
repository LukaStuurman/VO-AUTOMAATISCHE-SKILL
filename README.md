# VO AUTOMAATISCHE SKILL

Herbruikbare ontwerpskill en universele afspraken voor Enexis-LS-stationsgebieden.

- [Skill en werkvolgorde](SKILL.md)
- [Universele informatie](docs/universele-info.md)
- [Kalibratie op Luka's 011.601 correct](docs/referentie-011601-correct.md)
- [Expliciete referentie-invoer](references/011601-correct.json)
- [2024-rekenhulpmiddel](scripts/reken_richtingen.py) en [gerichte controles](scripts/test_reken_richtingen.py)

De werkwijze ondersteunt lege ontwerptekeningen en reeds uitgewerkte buurgebieden. Eerst bestaande structuur, hergebruik en splitsingen; daarna gezamenlijke gleuf, nieuwe150Al-voedingen en paden. Moffen mogen op geschikte punten midden op bestaande hoofdkabels. Reken eerst tot het kabeluiteinde en, als dat niet past, tot de laatste aansluiting met dezelfde volledige belasting. Een rekeneinde wijzigt geen fysieke eindmof.

Richtingen blijven lang naast elkaar met0,20m offset, bij voorkeur in of langs de stoep, buiten bomen en beplantingsstroken. Gras, pleinen en tegels mogen. Minimaliseer rechte gezamenlijke wegoversteken; controleer percelen én eigendom. WFS-functie: LS/LS-OV opnemen, uitsluitend OV uitsluiten. KLIC bepaalt kabeltype. Overzetters alleen bij overgang naar een nieuwe kabel.

## Validatie en grenzen

Bijgewerkt5oktober2026 op basis van de gecorrigeerde DXF en ingevulde2024-werkmap. De herberekening reproduceert alle zeven opgegeven afzekeringen en886,8A trafoverbruik /909,6A opwek; de630kVA-limiet is913,043478…A. Zes tests controleren de rekenbeslissingen. Projectaantallen en RT-bezetting zijn geen universele voorschriften.

Het hulpmiddel rekent expliciete paden; het genereert geen volledige CAD-tekening en bewijst geen complete aansluitingstopologie, eigendom of uitvoerbaarheid op nieuwe locaties. Die controles horen bij iedere nieuwe uitwerking. De achterhaalde eigen acht-richtingenvariant is geen standaard voor nieuwe ontwerpen.

De bron-CAD, ingevuldeExcel en volledigeWFS-datasets zijn niet geüpload. Het referentiebestand bewaart bronhashes. Kader en catalogus worden per project expliciet gekozen.

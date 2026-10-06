# VO AUTOMAATISCHE SKILL

LS-VO maken uit oorspronkelijke CAD, KLIC/WFS, BGT/topografie en kadergegevens, met dezelfde ontwerplogica en vormgeving als Luka's werk.

- [Skill](SKILL.md) en [universele regels](docs/universele-info.md)
- [Bronworkflow en invoer](docs/bronworkflow.md)
- [Bronontwerpgenerator](scripts/ontwerp_uit_bronnen.py)
- [Lokale CAD-stijl zonder routes/keuzes](assets/cad-stijl.json)
- [Kalibratie en bewezen bereik](docs/kalibratie-bronontwerp.md)
- [Correcties uit de beoordeling van 6 oktober](docs/correcties-06-10-2026.md): bestaande eindmoffen, rechte bomenrijcorridors, eerdere oversteken, ongebruikte mofarmen en complete annotatie-opruiming.
- [Los rekenhulpmiddel](scripts/reken_richtingen.py)

De standaard is genereren vanuit bronnen, een kandidaat opslaan en de gebruikersoplossing pas daarna vergelijken. De generator leest geen doelstationoplossing; broncorrecties en bron-/scriptversies zijn expliciet. Uitgewerkte buren leveren grenzen en stijl; zonder ingevulde buren werkt de lokale stijlset.

Hergebruik en splitsingen eerst, moffen op geschikte vrije punten, gezamenlijke gleuf, 0,20 m offset, stoepvoorkeur en rechte gezamenlijke wegkruisingen. Lees BGT hoofd- én plustype. Huisaansluitkabels geven koppeling/belasting, geen richtinglengte of eindmof. Standaard 150Al; 150Al+ alleen bij noodzakelijke behouden combi. Overzetters uitsluitend bij overgang naar nieuw.

Voor verwijdering telt de unie van gebruikte delen door ALLE richtingen. Alleen het resterende ongebruikte deel mag worden geknipt/verwijderd. Bescherm externe/onbekende voedingen en nog actieve OV; verander de KLIC/WFS-bron niet.

Laagste maximaal toegestane zekering van alle hoofd-/aftakpaden geldt voor de richting. Toets fysieke uiteinden eerst, daarna eventueel laatste aansluitingen met dezelfde belasting. Trafo via categorievertaling, verbruik/opwek apart; limiet kVA / 0,23 / 3.

## Bereik

Automatische kandidaatmaker voor kader 2024, getoetst op Laarbeek-bronnen. Kabelcatalogus: 150Al, 95Al, 50Al, 50Cu. De universele workflow ondersteunt andere stations; de generator is nog niet op een tweede onbekend station gevalideerd. Complexe topologie of andere kabeltypes vraagt gecontroleerde uitbreiding. Eigendom, wortelzones en bronconflicten blijven afzonderlijke controles.

De oudere `maak_vo_tekening.py` reconstrueert met een uitgewerkte referentie; dat is geen onafhankelijk bronontwerp. Bron-CAD, ingevulde Excel en volledige WFS-registers blijven lokaal.

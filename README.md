# BBL Standings

Flask-Webapp zur Simulation der BBL-Tabelle (Saison 2025/26).

## Features

- Gespielte Spiele aus `data/games.py` laden
- Hypothetische Ergebnisse für ausstehende Spiele eintragen
- Live-Tabellenberechnung mit korrektem Tiebreaking (H2H-Minitage)
- Direktvergleich (DV) zwischen ausgewählten Teams
- Ergebnisse per 🔒-Button dauerhaft festschreiben
- Zustand (Hypothesen, Team-Auswahl) wird in `data/state.json` gespeichert

## Starten

```bash
cd result_preview
python main.py
```

Die App läuft dann unter `http://localhost:5000`.

## Lizenz

MIT

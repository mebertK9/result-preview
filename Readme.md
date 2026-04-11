# Eigentlich ne TODO-Liste, aber wen stört's?
## TODO

+ [x] überprüfen, ob rettungsgasse und kalkulator synchron sind
    + [x] Grid wieder ins jsonbin-json
        + [x] Check (Synchron?)
    + [x] Grid ganz aus user data raus
        + [x] wahrscheinlich kein speichern des grid-status
    + [x] Eigener Grid-Cache
    + [x] Weitere Analyse, immer noch nicht synchron
+ [ ] Puffer-Reihen
    + [ ] Das richtige Spiel zumindest anzeigen
    + [ ]  Initial: Löwen-Spiele auf Seitenstreifen
    + [ ] _BAD_-Eregnis? Verdrängt neutrales Spiel vom Seitenstreifen auf 1
    + [ ] Dieses Spiel
        + [ ] Gewonnen? _fremnder_ = linker Seitensterifen
        + [ ] Verloren? normale _BAD_-Logik
+ [ ] Mehrretungsgassigkeit    
    + [ ] Aktuelle Rettungsgasse aus Schleife
    + [ ] **Achung:** Auch das _div_ in Schleife!
    + [ ] _MANDATORY_ und _ROW_ konfigurierbar machen
        + [ ] _ROW:_ Zu spielende Spiele (Löwen = Pending, wird schon errechnet)
        + [ ] _MANDATORY:_ Siegdifferenz
+ [?] Auswertung der Gasse: Geschafft/nicht geschafft (Löwe erreicht?)
+ [?] Meta-Auswertung der Rettungsgassen: Reichen die Gassen für den Klassenerhalt?
+ [ ] Spiele rückgängig machen
    + [ ] neue Züge?
    + [ ] immer von vore rendern
        + [ ] dabei dann nicht das Eintrag-Ereignis (/move), sondern beim rendern IMMER das kalkulator-Ergebnis
+ [-] ~~Ausrechnen, welche Mannschaften infrage kommen~~
    + [ ] => games.COMPETITORS
+ [-] ~~Direkter Verglech~~
    + [-] ~~Aufzeigen, wer in den direkten Vergleich kommen **könnte**~~
    + [-] ~~Direkter Verlgeich als Kriterium, insgesamt grün oder Rot~~
# Promts
## 0)


Verschaffe dir bitte zuerst einen Überblick über den aktuellen Stand des Projekts.

1. Prüfe die `CLAUDE.md` auf Konsistenz mit dem aktuellen Projektstand und schlage nötige Anpassungen vor. Noch nichts ändern.
    
2. Was ist bereits umgesetzt?
    
3. Was haben wir zuletzt gemacht?
    
4. Gibt es aktuell offene, uncommittete oder unvollständige Änderungen?
    
5. Welche Aufgaben oder User Stories sind noch offen?
    
6. Was wäre jetzt der sinnvollste nächste Schritt?


## 1)

Wir arbeiten ab jetzt an Version 0.2 des Festival Planners.

Die bisherige Anwendung war als MVP angelegt. In mehreren Projektdateien und Beschreibungen wird deshalb noch der Begriff „MVP“ verwendet.

Bitte prüfe das gesamte Projekt und passe die Bezeichnungen so an, dass die aktuelle Version nicht mehr generell als MVP bezeichnet wird.

Regeln:

- Entferne „MVP“ dort, wo damit die aktuelle Anwendung oder Architektur bezeichnet wird.
    
- Verwende stattdessen je nach Kontext neutrale Begriffe wie „Festival Planner“, „aktuelle Version“, „Domain Model“, „Architecture“ oder „Implementation“.
    
- Wenn ausdrücklich die alte erste Version beschrieben wird, darf „MVP“ weiterhin verwendet werden.
    
- Ändere keine fachlichen Anforderungen, keine Architektur und keinen Programmcode.
    
- Führe ausschließlich diese begriffliche Bereinigung durch.
    
- Zeige mir anschließend kurz, welche Dateien du geändert hast und welche Formulierungen ersetzt wurden.


## 2)

Analysiere die bestehende Festival-Planner-Anwendung v0.2. Verändere noch keinen Code.

Untersuche:

- Projektstruktur und Verantwortlichkeiten von `main.py`, `db.py`, `schedule.py`, `seed.py`
    
- aktuelles Domain Model und SQLite-Struktur
    
- bestehende Beziehungen
    
- vermischte Verantwortlichkeiten
    
- betroffene Stellen für das geplante Refactoring
    

Ziel von Refactoring Phase 1:

- Funktionalität erhalten
    
- SQLite beibehalten
    
- `Artist`, `Stage`, `Act` als getrennte Entitäten
    
- neue Struktur mit `models.py`, `crud.py`, `routers.py`
    
- `schedule.py` möglichst als eigenständige Fachlogik erhalten
    

Erstelle eine kurze Ist-Analyse mit:

1. aktueller Architektur
    
2. aktuellem Domain Model
    
3. Problemen/Grenzen
    
4. betroffenen Dateien
    
5. empfohlenen nächsten Refactoring-Schritten
    

Noch keine Dateien ändern und keinen Code erzeugen.
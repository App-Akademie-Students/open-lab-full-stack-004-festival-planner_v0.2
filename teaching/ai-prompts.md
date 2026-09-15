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
Wir starten ein neues Lernprojekt: Festival Planner.

Ziel ist ein bewusst kleines MVP für Festivalbesucher.

Leitfrage:
"Wo ist was wann?"

Analysiere das Projektziel und formuliere eine kurze, klare Projektbeschreibung.

Noch keine Anforderungen, kein Domain Model und keinen Code erzeugen.


## 6)

Die Projektbeschreibung ist bestätigt.

Wir sind jetzt bei Roadmap-Schritt 6:
Anforderungen definieren.

Leite aus der Projektbeschreibung Anforderungen für ein bewusst kleines MVP ab.

Erstelle:

- Muss-Anforderungen
- optionale Anforderungen
- typische Benutzeraktionen
- eine klare Scope-Abgrenzung

Wichtig:
- Das MVP soll so klein wie möglich bleiben.
- Noch kein Domain Model entwerfen.
- Noch keine Architektur festlegen.
- Noch keinen Code erzeugen.

Zeige mir zunächst deinen Vorschlag.


## 7)
Wir sind bei Roadmap-Schritt 7: Domain Model entwerfen.

Leite aus den Muss-Anforderungen das minimal notwendige Domain Model für das MVP ab.

Prüfe:
- welche Entitäten wirklich notwendig sind
- welche Attribute sie minimal brauchen
- welche Daten persistent gespeichert werden müssen

Halte das Modell so klein wie möglich.

Noch keinen Code erzeugen.

## 8)

Wir sind bei Roadmap-Schritt 8: Architektur und Projektstruktur festlegen.

Grundlage:
- FastAPI
- SQLAlchemy
- SQLite
- HTML/CSS/JavaScript
- genau eine persistente Entity
- Konflikterkennung als reine Business-Logik
- Anwendung soll bewusst klein und verständlich bleiben

Entwirf eine minimale Projektstruktur für das MVP.

Beschreibe:
- welche Ordner und Dateien wirklich notwendig sind
- welche Verantwortung jede Datei hat
- wo API, Datenbankzugriff, Business-Logik und Frontend liegen
- wo die Tests liegen

Vermeide unnötige Abstraktionen und Overengineering.

Noch keinen Anwendungscode erzeugen.
Zeige mir zunächst nur den Vorschlag.

## 9)

Wir sind bei Roadmap-Schritt 9: User Stories und Backlog konkretisieren.

Leite aus den Muss-Anforderungen in doc/requirements.md kleine, umsetzbare User Stories für das MVP ab.

Für jede Story:
- Formulierung: Als ... möchte ich ... damit ...
- 2–4 Akzeptanzkriterien
- möglichst klein und unabhängig
- nur MVP-Scope berücksichtigen

Noch keinen Code erzeugen.
Zeige mir zunächst nur den Vorschlag.


## 10) Anwendungscode implementieren (Freitag, 11.09.)

Setze die noch offenen User Stories aus `doc/user-stories.md` bzw. dem Backlog nacheinander um.

Arbeite die Stories in der festgelegten Reihenfolge ab, ohne nach jeder Story auf meine Bestätigung zu warten.

Für jede User Story:

- prüfe zuerst die bestehenden Anforderungen und die Architektur,
    
- implementiere nur den beschriebenen Scope,
    
- ergänze oder aktualisiere sinnvolle Tests,
    
- führe die Tests aus,
    
- prüfe anschließend kurz, ob die Akzeptanzkriterien erfüllt sind,
    
- gehe danach selbstständig zur nächsten User Story über.
    
Halte dich an `CLAUDE.md` sowie an die bestehenden Requirements-, Domain-Model- und Architektur-Dokumente.

Keine zusätzlichen Features, Frameworks oder Architekturänderungen einführen, wenn sie nicht für die jeweilige Story notwendig sind.

Nur dann stoppen und nachfragen, wenn:

- Anforderungen einander widersprechen,
    
- eine Entscheidung nötig ist, die nicht aus der vorhandenen Dokumentation ableitbar ist,
    
- eine Änderung den vereinbarten Scope oder die Architektur wesentlich verändern würde.
    
Ansonsten arbeite die User Stories selbstständig bis zum Ende ab.

## 11) Abschluss und Review (Freitag, 11.09.)

bitte in einem unabhängigen sub-task durchführen.
Reviewe gezielt den Backend-Code des Festival Planners.



Konzentriere dich auf:

* `app/main.py`
* `app/models.py`
* `app/schedule.py`
* die zugehörigen Tests

Führe keine Änderungen durch.

Prüfe den Code aus zwei Perspektiven:

1. **Erfüllt die Implementierung die Akzeptanzkriterien der bereits umgesetzten User Stories?**
2. **Ist der Code qualitativ so, dass du ihn in einem Pull Request freigeben würdest?**

Bewerte dabei insbesondere:

* Verständlichkeit
* Struktur
* Robustheit
* Wartbarkeit
* Tests
* Übereinstimmung mit `CLAUDE.md`
* Übereinstimmung mit Requirements, Domain Model und Architektur
* Erfüllung der Akzeptanzkriterien aus dem Backlog

Prüfe bei den Akzeptanzkriterien nicht nur den Happy Path, sondern auch relevante Grenzfälle.

Klassifiziere jedes relevante Finding als:

* ✅ OK
* ⚠️ Änderungswunsch
* ❌ Blocker

Nenne nur relevante Findings. Vermeide rein kosmetische Vorschläge und unnötiges Refactoring.

Strukturiere den Review-Bericht so:

1. Erfüllung der Akzeptanzkriterien
2. Code-Review-Findings
3. Fehlende oder unzureichende Tests
4. Abweichungen von Requirements, Domain Model, Architektur oder `CLAUDE.md`
5. Gesamturteil: freigeben / freigeben mit Änderungen / nicht freigeben

Ändere noch keinen Code.

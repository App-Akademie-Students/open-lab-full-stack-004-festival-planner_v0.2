# Roadmap Festival Planner

* Entscheide über Einsatz von AI!
* in welchen Phasen ist AI besonders hilfreich?

1. **Project Goal**
   Wir entwickeln gemeinsam einen kleinen minimalistischen **Festival Planner**.
   User: Wo ist Was Wann?

2. **Backlog anlegen**
   Erste Arbeitspakete sichtbar machen.

3. **Technischen Rahmen festlegen**


4. **Projekt-Setup**
   

5. **Projektkontext / Projektregeln**
   `CLAUDE.md` anlegen und Development Rules definieren.

6. **Anforderungen definieren**
   → [`requirements.md`](requirements.md)

   * Was soll die Anwendung konkret können?
   * Was ist Muss, was ist optional?
   * Welche Benutzeraktionen gibt es?
   * Was gehört bewusst **nicht** zum Scope?

7. **Minimales Domain Model entwerfen**
   → [`domain-model.md`](domain-model.md)
   

8. **Architektur und Projektstruktur festlegen**
   → [`architecture.md`](architecture.md)

9. User Stories ableiten & Backlog konkretisieren
   Backlog verfeinern und erste Features priorisieren.
   → [`backlog.md`](backlog.md)

10. **Implementieren**
    In kleinen Schritten mit Claude.

11. **Testen und Reviewen**

12. **Refactoring / Dokumentation**
    Für v0.1 dokumentiert und freigegeben (siehe [`review.md`](review.md)). Datenbank-Fokus
    wird in Phase 2 (v0.2) unten fortgesetzt.

## Phase 2 – Refactoring v0.2 (Datenbank-Fokus)

Ziel: `Artist`, `Stage`, `Act` als getrennte Entitäten statt einer flachen `ProgramItem`-Tabelle,
bei erhaltener Funktionalität und SQLite. Neue Struktur: `models.py`, `crud.py`, `routers.py`.

13. **Domain Model erweitern**
    → [`domain-model.md`](domain-model.md) – erledigt.

14. **Architektur aktualisieren**
    → [`architecture.md`](architecture.md) – erledigt.

15. **`app/models.py` anlegen**
    `Artist`, `Stage`, `Act` mit Beziehungen – erledigt.

16. **API-Vertrag entscheiden**
    Flache `title`/`stage`-Strings im JSON bleiben (befüllt über die Beziehung) statt
    verschachtelter Objekte – entschieden, siehe `architecture.md`.

17. **`app/seed.py` umstellen**
    Erst `Artist`/`Stage` anlegen, dann `Act` mit FK-Referenzen.

18. **`app/crud.py` einführen**
    Bühnen- und Programm-Query als Funktionen, jetzt mit Joins.

19. **`app/routers.py` einführen**
    Endpunkte aus `main.py` verschieben; `main.py` bindet nur noch den Router ein.

20. **Tests umstellen**
    `tests/test_api.py` auf neue Modelle/Fixtures anpassen.

21. **`app/db.py` auf Infrastruktur reduzieren**
    `ProgramItem` entfernen – erst wenn Schritt 17–20 abgeschlossen sind und nichts mehr
    darauf referenziert.

22. **Testen und Reviewen**
    `python -m pytest`, danach Review analog zu `review.md`.






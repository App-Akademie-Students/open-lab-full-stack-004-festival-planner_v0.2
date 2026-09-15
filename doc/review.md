# Backend-Review – Festival Planner

Stand: 2026-09-11. Unabhängiges Code-Review von `app/main.py`, `app/db.py`, `app/schedule.py`,
`app/seed.py` und den zugehörigen Tests gegen `CLAUDE.md`, `doc/requirements.md`,
`doc/domain-model.md`, `doc/architecture.md` und `doc/backlog.md`.

**Hinweis vorab:** `app/models.py` existiert nicht. Das Datenmodell `ProgramItem` sowie
Engine/Session/`init_db()`/`get_db()` liegen – wie in `doc/architecture.md` vorgesehen – in
`app/db.py`. Geprüft wurde stattdessen `app/db.py`, zusammen mit `app/main.py`,
`app/schedule.py`, `app/seed.py`, `tests/test_api.py` und `tests/test_schedule.py`. Zur
Verifikation wurde lesend `python -m pytest -q` im Projekt ausgeführt: **14 passed** (2 harmlose
Deprecation-Warnings zu `httpx`/`anyio`, keine Fehler).

## 1. Erfüllung der Akzeptanzkriterien

**T-0 · Projektgerüst — erfüllt.** Ordnerstruktur entspricht `architecture.md`;
`app/__init__.py` ist leer und macht `app/` zum Package; `requirements-dev.txt` enthält pytest +
httpx; `python -m pytest` läuft grün (verifiziert).

**US-1 · Programm einspielen — erfüllt.** `app/seed.py` legt 14 Programmpunkte auf 3 Bühnen an
(im geforderten Rahmen 10–15), alle auf `festival_now().date()`, also dem heutigen Datum in
Festival-Zeit. Parallele Acts auf unterschiedlichen Bühnen sind vorhanden, ebenso mindestens
zwei Acts mit identischer Startzeit (`Opener Band` und `Folk Trio`, je 12:00). Alle Einträge
erfüllen `ends_at > starts_at`, Titel/Bühne nicht leer. Erneutes Ausführen löscht vorher alle
Zeilen (`db.query(ProgramItem).delete()`) und fügt neu ein – keine Duplikate.

**US-2 · Programm als Liste sehen — erfüllt.** `GET /api/program` sortiert per
`ORDER BY starts_at, stage` (`app/main.py:49`), identisch zur Doku. Frontend zeigt Start/Ende
(HH:MM), Titel, Bühne ohne Login. Leere Liste wird im Frontend über `#empty-hint` abgefangen
(`static/app.js:31`). Funktional erfüllt, inzwischen auch automatisiert getestet (siehe
Abschnitt 3 / Nachtrag).

**US-3 · Sehen, was gerade läuft — erfüllt.** Grenzfälle (`starts_at == now` → „now",
`ends_at == now` → nicht mehr „now", mehrere gleichzeitig) sind in `tests/test_schedule.py`
exakt abgedeckt und bestehen. `now` kommt serverseitig aus `festival_now()` (UTC+02:00, naiv)
und wird im JSON sowie im Frontend (`#now-hint`) angezeigt. Kein Auto-Refresh (Scope korrekt
eingehalten).

**US-4 · Sehen, was als Nächstes kommt — erfüllt.** Frühester Startzeitpunkt nach `now`, inkl.
Ties, korrekt in `compute_statuses` (`app/schedule.py:17-36`) und durch
`test_multiple_items_with_same_next_start_time` getestet. Vor Festivalbeginn nur „next", kein
„now" (`test_before_festival_start_only_next_no_now`); nach dem letzten Act nichts markiert,
kein Fehler (`test_after_last_item_nothing_highlighted`). Optisch unterscheidbar via
CSS-Klassen `status-now`/`status-next` mit unterschiedlichen Farben.

**US-5 · Nach Bühne filtern — erfüllt.** `GET /api/stages` liefert alphabetisch sortierte,
distincte Bühnen (`app/main.py:39`); Frontend baut daraus das Dropdown inkl. „Alle Bühnen".
`GET /api/program?stage=X` filtert serverseitig, unbekannte Bühne liefert leere Liste
(getestet). Status wird **nach** dem Filter berechnet (Filter zuerst in der Query, danach
`compute_statuses(items, now)` auf der bereits gefilterten Liste, `app/main.py:49-54`) – korrekt
und durch `test_next_is_computed_within_given_items_only` sinngemäß abgesichert.

**US-6 · Programm auf dem Smartphone nutzen — erfüllt** (soweit anhand des Codes beurteilbar;
kein visueller Browsertest bei 360 px durchgeführt). `static/style.css` verwendet
`box-sizing: border-box`, Flex-Wrap, relative Einheiten, kein festbreites Element über
Viewport-Breite hinaus; kein Build-Tooling, reines HTML/CSS/Vanilla JS.

## 2. Code-Review-Findings

- ✅ **Zeitzonen-Handling korrekt.** `festival_now()` (`app/schedule.py:12-14`) nutzt
  `datetime.now(FESTIVAL_TZ).replace(tzinfo=None)` – das liefert korrekt die aktuelle
  Wanduhrzeit in UTC+02:00 als naives Datetime, exakt konsistent mit den naiv in
  Festival-Ortszeit gespeicherten `starts_at`/`ends_at`. Das ist eine Stelle, an der leicht
  Fehler passieren (z. B. `utcnow()` + falscher Offset, oder Systemzeitzone statt fixem
  Offset) – hier ist es richtig gelöst.
- ✅ **`festival_now` als Funktion und als FastAPI-Dependency.** `app/seed.py` ruft
  `festival_now()` direkt auf, `app/main.py` nutzt sie über `Depends(festival_now)`
  (`app/main.py:47`). Da es sich um dieselbe Funktionsreferenz aus `app.schedule` handelt,
  funktioniert `app.dependency_overrides[festival_now] = ...` in `tests/test_api.py` wie in der
  Architektur beschrieben – durch den grünen Testlauf (`test_program_includes_status_and_now`
  erwartet exakt den überschriebenen Zeitpunkt) verifiziert.
- ✅ **Status wird nach dem Bühnenfilter berechnet**, wie in `architecture.md` gefordert
  (`app/main.py:49-54`).
- ✅ **Threadsafety SQLite.** `connect_args={"check_same_thread": False}` in `app/db.py:9`, mit
  Begründung im Kommentar exakt wie in der Architektur dokumentiert.
- ✅ **Kein Scope-Creep.** main.py enthält nur die zwei dokumentierten Endpunkte + Static-Mount +
  Lifespan; `schedule.py` nur `FESTIVAL_TZ`, `festival_now`, `compute_statuses`; keine
  zusätzlichen Felder (Genre, Beschreibung), keine Konflikterkennung, kein Tagesfilter, keine
  Suche/Favoriten. Entspricht `CLAUDE.md` ("Do not implement functionality that is not part of
  the agreed requirements").
- ⚠️ **Änderungswunsch – Fragile Test-Isolation in `tests/test_api.py`.**
  `app.dependency_overrides[get_db]` und `[festival_now]` werden auf Modulebene gesetzt (Zeilen
  35, 38), nicht in einer Fixture mit Teardown. Aktuell unproblematisch, da es das einzige
  Testmodul mit Overrides ist, aber sobald ein weiteres Testmodul dieselbe `app`-Instanz
  importiert, "leaken" diese Overrides prozessweit. Empfehlung (kein Blocker): Overrides in eine
  `autouse`-Fixture mit `app.dependency_overrides.clear()` im Teardown verschieben, falls das
  Projekt wächst.
- ⚠️ **Änderungswunsch – Domain-Invarianten nicht technisch erzwungen.**
  `doc/domain-model.md` nennt als Invarianten „title/stage nicht leer" und
  „ends_at > starts_at". In `app/db.py:14-21` gibt es dafür kein `CheckConstraint`, keine
  Validierung – nur `nullable=False`. Da es keine Schreib-API gibt (Daten kommen ausschließlich
  aus dem kontrollierten Seed-Skript), ist das Risiko im MVP gering, aber es ist eine Lücke
  zwischen dokumentierter Invariante und tatsächlicher Durchsetzung. Kein Blocker, aber
  erwähnenswert.
- ⚠️ **Änderungswunsch (sehr geringe Relevanz) – relative Pfade CWD-abhängig.**
  `DATABASE_URL = "sqlite:///./festival.db"` (`app/db.py:5`) und
  `StaticFiles(directory="static", ...)` (`app/main.py:69`) sind relativ zum Arbeitsverzeichnis.
  Funktioniert exakt wie in `CLAUDE.md`/`architecture.md` dokumentiert (`uvicorn` wird im
  Projektordner gestartet), ist also kein Fehler, nur ein impliziter Kontrakt ohne Fallback –
  für dieses MVP akzeptabel.
- ✅ **Keine Findings zu Sortierung/Filter/Serialisierung.** JSON-Format (`now`,
  `items[].status` als `"now"`/`"next"`/`null`, naive ISO-Zeitstempel ohne Offset) stimmt exakt
  mit dem in `architecture.md` dokumentierten Beispiel überein (durch Test
  `test_program_includes_status_and_now` mit `"2026-09-11T14:00:00"` verifiziert).

Keine ❌-Blocker gefunden.

## 3. Fehlende oder unzureichende Tests

- ~~Kein Test für „leere Datenbank" auf API-Ebene.~~ **Nachtrag:** Dieser Punkt wurde inzwischen
  behoben – `tests/test_api.py::test_program_and_stages_with_empty_database` prüft jetzt
  `GET /api/program` und `GET /api/stages` gegen eine leere Tabelle (leere Liste, kein Fehler).
  Suite läuft mit 15 Tests grün.
- Kleinere Lücke: `compute_statuses([], now)` (komplett leere Liste) ist nicht explizit getestet,
  obwohl das Verhalten trivial korrekt ist (leere Liste zurück).
- Ansonsten ist die Testabdeckung der Grenzfälle in `tests/test_schedule.py` sehr gut: exakter
  Start-/Endzeitpunkt, mehrere gleichzeitige „now", mehrere gleichzeitige „next" bei Tie, Status
  vor Festivalbeginn, Status nach letztem Act, sowie „next" nur innerhalb der übergebenen
  (gefilterten) Liste.
- `tests/test_api.py` deckt Sortierung, Statusfeld inkl. `now`, Bühnenfilter, unbekannte Bühne,
  Bühnenliste, Auslieferung von `index.html` und (neu) leere Datenbank ab – entspricht der in
  `architecture.md` beschriebenen Minimalabdeckung für die API-Schicht.

## 4. Abweichungen von Requirements, Domain Model, Architektur oder CLAUDE.md

Keine inhaltlichen Abweichungen gefunden. Im Detail geprüft und bestätigt konsistent:

- Tech-Stack exakt wie in `CLAUDE.md`/T1 (fastapi, uvicorn[standard], sqlalchemy; pytest+httpx
  nur in `requirements-dev.txt`).
- Dateiaufteilung entspricht 1:1 der Tabelle in `architecture.md` (inkl. der bewussten
  Abwesenheit von `routers/`, `schemas.py`, `crud.py`, `services/`).
- Sprache: Doku (`doc/`) Deutsch, Code (Docstrings/Kommentare) Englisch – eingehalten.
- `.gitignore` schließt `*.db`/`*.sqlite*` aus, wie in `architecture.md` verlangt.
- Domain Model exakt eine Entität `ProgramItem` mit den fünf dokumentierten Feldern, keine
  zusätzlichen Entitäten.
- Kein Tagesfilter, keine Mehrsprachigkeit, kein Login, keine Admin-UI – Scope-Abgrenzung aus
  `requirements.md` eingehalten.

## 5. Gesamturteil

**Freigeben mit (nicht blockierenden) Änderungswünschen.**

Die Implementierung erfüllt alle Akzeptanzkriterien von T-0 und US-1 bis US-6 fachlich korrekt,
inklusive der kritischen Grenzfälle bei Zeitzonen und Status-Berechnung. Der Code ist klein,
lesbar, konsistent mit der dokumentierten Architektur und ohne Scope-Creep. Keine Blocker. Der
ursprünglich empfohlene Nachtrag (Test für leere Datenbank) ist bereits umgesetzt. Die
verbleibenden ⚠️-Punkte (Test-Isolation der Dependency-Overrides, fehlende DB-seitige
Durchsetzung der Domain-Invarianten, CWD-abhängige Pfade) können als Backlog-Notiz für später
festgehalten werden, ohne die aktuelle Freigabe zu verzögern.

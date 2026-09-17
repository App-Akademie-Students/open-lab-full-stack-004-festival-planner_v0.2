# Festival Planner

## Project Goal

Wir entwickeln einen minimalistischen Festival-Planer für Festivalbesucher.
"Wo ist was wann?"

## Project Status

Phasen und Vorgehen: [`doc/roadmap.md`](doc/roadmap.md).
User Stories, Priorität und Status: [`doc/backlog.md`](doc/backlog.md).

Stand 2026-09-17: v0.1 (Roadmap-Schritt 9, User Stories US-1 bis US-6) ist umgesetzt. Phase 2
/ v0.2 (Refactoring, Datenbank-Fokus, T-1 bis T-9) ist ebenfalls umgesetzt: `Artist`, `Stage`,
`Act` als getrennte Entitäten, Struktur aufgeteilt in `models.py`, `db.py`, `crud.py`,
`schedule.py`, `routers.py`, `main.py`, `seed.py`. Die Datenbank wurde von SQLite auf
PostgreSQL (Neon) umgestellt. Offen: Testen und Reviewen (Roadmap-Schritt 22).

Ab Phase 2 gilt eine neue Leitlinie für die Architektur: nicht mehr „so klein wie möglich"
(MVP), sondern gut strukturiert und erweiterbar – die Struktur wächst Schritt für Schritt mit
der Komplexität, sobald ein konkreter Bedarf besteht. Details:
[`doc/architecture.md`](doc/architecture.md).
Nach jeder Story/Aufgabe den Status in `doc/backlog.md` aktualisieren.

## Tech Stack

* Python 3
* FastAPI, gestartet über uvicorn
* SQLAlchemy
* PostgreSQL (gehostet bei Neon), Treiber `psycopg` (v3)
* HTML + CSS
* Vanilla JavaScript – kein Framework, kein Build-Tooling

Nur für die Entwicklung (bewusste Ausnahme von T1 in `doc/requirements.md`):

* pytest
* httpx (wird von FastAPIs `TestClient` benötigt)

## Project Decisions

* **Festival-Zeitzone (T3):** fester Offset UTC+02:00. Keine Sommer-/Winterzeit-Logik und
  damit keine zusätzliche Dependency (`tzdata` wäre unter Windows für `zoneinfo` nötig).
  Für ein eintägiges Festival ausreichend.
* **Tests:** pytest + httpx ausschließlich als Dev-Dependencies, nicht für den Betrieb.
* **Sprache:** Projektdokumentation (`doc/`, README) auf Deutsch; Code (Bezeichner,
  Kommentare, Docstrings) auf Englisch.
* **Datenbank (v0.2):** PostgreSQL bei Neon statt SQLite. `DATABASE_URL` liegt in `.env`
  (nicht eingecheckt, siehe `.gitignore`) und wird in `db.py` per `python-dotenv` geladen.
  Treiber ist `psycopg` (v3); eine `postgresql://`-URL wird in `db.py` automatisch auf
  `postgresql+psycopg://` normalisiert, da SQLAlchemy sonst `psycopg2` erwartet, das nicht
  installiert ist. Datenintegrität `ends_at > starts_at` wird zusätzlich als DB-seitige
  `CheckConstraint` auf `Act` erzwungen, nicht nur in der Business-Logik.
  Tests laufen weiterhin gegen eine In-Memory-SQLite-DB (siehe `tests/test_api.py`), nicht
  gegen Neon.

## Functional Requirements

Die Anforderungen (Muss / optional / Benutzeraktionen / Scope-Abgrenzung) sind in
[`doc/requirements.md`](doc/requirements.md) definiert.

Kurzfassung: Ein eintägiges Festival, Programm als chronologische Liste, Filter nach Bühne,
Anzeige „läuft jetzt / kommt als Nächstes". Daten per Seed, kein Login. Bewusst so klein
wie möglich, aber im Datenmodell auf Mehrtägigkeit vorbereitet.

## Architecture

Vollständig in [`doc/architecture.md`](doc/architecture.md).

Kurzfassung – Leitlinie seit Phase 2: nicht mehr „so klein wie möglich", sondern gut
strukturiert und erweiterbar; die Struktur wächst Schritt für Schritt mit der Komplexität,
sobald ein konkreter Bedarf besteht (nicht spekulativ auf Vorrat):

| Bereich | Ort |
|---|---|
| API (`GET /api/program?stage=`, `GET /api/stages`) | `app/routers.py` |
| App-Objekt, Lifespan, bindet Router + `static/` ein | `app/main.py` |
| Datenbank-Infrastruktur: Engine (PostgreSQL/Neon, `DATABASE_URL` aus `.env`), Session, `init_db()` | `app/db.py` |
| ORM-Modelle `Artist`, `Stage`, `Act` | `app/models.py` |
| Datenbank-Queries (Joins über `Artist`/`Stage`) | `app/crud.py` |
| Business-Logik: Festival-Zeit, Status „now" / „next" (reine Funktionen, ohne DB/HTTP) | `app/schedule.py` |
| Seed-Skript (Festival auf das heutige Datum) | `app/seed.py` |
| Frontend (HTML/CSS/Vanilla JS) | `static/` |
| Tests | `tests/` |

Kernregeln:

* Queries stehen in `crud.py`, nicht direkt in den Endpunkten.
* Der Status wird **nach** dem Bühnenfilter berechnet.
* Zeitstempel werden naiv in Festival-Ortszeit (UTC+02:00) gespeichert.
* Die Business-Logik bekommt `now` als Parameter; `festival_now` ist in `schedule.py`
  definiert und wird in `routers.py` als FastAPI-Dependency verwendet; Tests ersetzen sie per
  `dependency_overrides`.
* Aktuell noch nicht vorhanden, aber kein grundsätzliches Verbot mehr: `schemas.py`,
  `services/`, Repository-Klassen, Paket-Split (`app/api/`, `app/domain/`, …) – kommen, sobald
  ein konkreter Bedarf entsteht. Bedingungen dafür: [`doc/architecture.md`](doc/architecture.md).

## Domain Model

Vollständig in [`doc/domain-model.md`](doc/domain-model.md).

Kurzfassung: Drei Entitäten `Artist`, `Stage`, `Act` (statt einer flachen
`ProgramItem`-Tabelle). `Act` referenziert `Artist` und `Stage` per Fremdschlüssel und trägt
`starts_at`/`ends_at`. Die API liefert weiterhin flache `title`/`stage`-Strings, befüllt aus
den Beziehungen (Entscheidung siehe `architecture.md`).
„Läuft jetzt / kommt als Nächstes", Sortierung und Bühnenliste werden zur Laufzeit berechnet
bzw. abgeleitet. Keine Festival- oder User-Entität im Domain Model.

## Development Rules

* Let the application grow in complexity step by step; introduce new structure (files,
  packages, layers) only when a concrete need justifies it, not speculatively.
* Do not add unnecessary frameworks or dependencies.
* Analyze requirements before implementing changes.
* Keep the existing project structure and coding style consistent.
* Write simple, readable code.
* Add tests for important business logic.
* Document important decisions and non-obvious code.
* Review existing code before making larger changes.

## Working with Claude

* Analyze the existing project before making changes.
* Prefer small, incremental changes.
* Explain larger structural changes before implementing them.
* Do not introduce new dependencies without a clear reason.
* Do not implement functionality that is not part of the agreed requirements.
* Ask for clarification when requirements are ambiguous.
* Update this file when important project decisions change.

## Project Commands

Alle Befehle im Projektordner mit aktivierter virtueller Umgebung.

### Create and activate virtual environment

```bash
python -m venv .venv
```

* Windows PowerShell: `.venv\Scripts\Activate.ps1`
* macOS / Linux: `source .venv/bin/activate`

### Install dependencies

```bash
pip install -r requirements.txt       # Betrieb
pip install -r requirements-dev.txt   # Entwicklung inkl. pytest + httpx
```

`requirements-dev.txt` wird mit dem ersten Code angelegt.

### Configure database connection

`.env` im Projektordner anlegen (nicht eingecheckt) mit:

```
DATABASE_URL=postgresql://<user>:<password>@<host>/<db>?sslmode=require
```

Verbindungsdaten kommen aus dem Neon-Projekt.

### Seed database

```bash
python -m app.seed
```

Legt die Tabellen in der über `DATABASE_URL` konfigurierten PostgreSQL-Datenbank an bzw.
setzt sie zurück und füllt das Programm für das heutige Datum.

### Start backend

```bash
uvicorn app.main:app --reload
```

Danach im Browser: <http://127.0.0.1:8000> (API-Doku: <http://127.0.0.1:8000/docs>).

### Run tests

```bash
python -m pytest
```

`python -m` statt nur `pytest`, damit das Projektverzeichnis im Importpfad liegt.

## Teaching Material

Files in `teaching/` are intended for participants only.

Do not read, analyze, summarize, or use files from this directory unless the user explicitly asks for it.

For you teaching/ is write only. When ever you think you have interesting information for teaching you can add it to teaching/


## Requirements Policy

`doc/requirements.md` represents the current required
behavior of the system.

When requirements change:

- update the current requirements instead of appending
  historical changes;
- remove requirements that are no longer valid;
- do not document implementation details as requirements;
- preserve important previous milestone specifications
  as snapshots under `doc/requirements-history/`;
- use Git history for detailed change history.
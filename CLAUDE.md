# Festival Planner

## Project Goal

Wir entwickeln einen minimalistischen Festival-Planer für Festivalbesucher.
"Wo ist was wann?"

## Project Status

Phasen und Vorgehen: [`doc/roadmap.md`](doc/roadmap.md).
User Stories, Priorität und Status: [`doc/backlog.md`](doc/backlog.md).

Stand 2026-09-10: Anforderungen (Schritt 6), Domain Model (Schritt 7), Architektur und
Projektstruktur (Schritt 8) sowie User Stories und Backlog (Schritt 9) sind bestätigt.
Es gibt noch keinen Anwendungscode.
Nächster Schritt: Implementieren (Schritt 10) – in Backlog-Reihenfolge, beginnend mit T-0.
Nach jeder Story den Status in `doc/backlog.md` aktualisieren.

## Tech Stack

* Python 3
* FastAPI, gestartet über uvicorn
* SQLAlchemy
* SQLite
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

## Functional Requirements

Die MVP-Anforderungen (Muss / optional / Benutzeraktionen / Scope-Abgrenzung) sind in
[`doc/requirements.md`](doc/requirements.md) definiert.

Kurzfassung: Ein eintägiges Festival, Programm als chronologische Liste, Filter nach Bühne,
Anzeige „läuft jetzt / kommt als Nächstes". Daten per Seed, kein Login. Bewusst so klein
wie möglich, aber im Datenmodell auf Mehrtägigkeit vorbereitet.

## Architecture

Vollständig in [`doc/architecture.md`](doc/architecture.md).

Kurzfassung – bewusst ohne zusätzliche Schichten (keine `routers/`, `schemas.py`, `crud.py`,
`services/`):

| Bereich | Ort |
|---|---|
| API (`GET /api/program?stage=`, `GET /api/stages`) + Auslieferung des Frontends | `app/main.py` |
| Datenbank: Engine, Session, Modell `ProgramItem`, `init_db()` | `app/db.py` |
| Business-Logik: Festival-Zeit, Status „now" / „next" (reine Funktionen, ohne DB/HTTP) | `app/schedule.py` |
| Seed-Skript (Festival auf das heutige Datum) | `app/seed.py` |
| Frontend (HTML/CSS/Vanilla JS) | `static/` |
| Tests | `tests/` |

Kernregeln:

* Die zwei Queries stehen direkt in den Endpunkten – keine Repository-Schicht.
* Der Status wird **nach** dem Bühnenfilter berechnet.
* Zeitstempel werden naiv in Festival-Ortszeit (UTC+02:00) gespeichert.
* Die Business-Logik bekommt `now` als Parameter; `festival_now` ist in `main.py` eine
  FastAPI-Dependency und wird in Tests per `dependency_overrides` ersetzt.

## Domain Model

Vollständig in [`doc/domain-model.md`](doc/domain-model.md).

Kurzfassung: Genau eine Entität `ProgramItem` mit `id`, `title`, `stage` (String),
`starts_at`, `ends_at` (volle Zeitstempel). Nur diese Tabelle wird persistiert.
„Läuft jetzt / kommt als Nächstes", Sortierung und Bühnenliste werden zur Laufzeit
berechnet bzw. abgeleitet. Keine Festival-, Stage- oder User-Entität im MVP.

## Development Rules

* Keep the application small and focused.
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

### Seed database

```bash
python -m app.seed
```

Legt `festival.db` an bzw. setzt sie zurück und füllt das Programm für das heutige Datum.

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

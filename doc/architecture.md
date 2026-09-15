# Architektur & Projektstruktur

Status: Zielstand Refactoring Phase 1 (v0.2), Stand 2026-09-15. Löst die bisherige
Ein-Datei-Struktur (`db.py` mit Modell + Queries direkt in `main.py`) ab.

Grundlage: [`requirements.md`](requirements.md), [`domain-model.md`](domain-model.md) und die
Entscheidungen in [`../CLAUDE.md`](../CLAUDE.md) (Festival-Zeitzone UTC+02:00, pytest + httpx
als Dev-Dependencies).

Leitlinie weiterhin: so klein und verständlich wie möglich. Mit drei Entitäten (`Artist`,
`Stage`, `Act`) und Joins reicht eine einzige Datei für Modell + Queries + Endpunkte aber nicht
mehr aus – deshalb kommen `models.py`, `crud.py` und `routers.py` dazu. Weiterhin keine
Repository-Klassen, kein `schemas.py`, keine `services/`.

## Projektstruktur

```text
festival-planner/
├── app/
│   ├── __init__.py        leer – macht app/ zum importierbaren Paket
│   ├── main.py            FastAPI-App: Objekt, Lifespan (init_db), bindet routers.py + static/ ein
│   ├── models.py          ORM-Modelle: Artist, Stage, Act (siehe domain-model.md)
│   ├── db.py              Datenbank-Infrastruktur: Engine, Session, init_db(), get_db()
│   ├── crud.py            Queries: Bühnenliste, Programmliste (Joins über Artist/Stage)
│   ├── routers.py         API-Endpunkte: GET /api/program, GET /api/stages
│   ├── schedule.py        Business-Logik: Festival-Zeit, „läuft jetzt" / „als Nächstes"
│   └── seed.py            Seed-Skript: Artists/Stages anlegen, dann Acts einfügen
├── static/
│   ├── index.html         die einzige Seite
│   ├── style.css          Layout (mobiltauglich), Hervorhebung von Status
│   └── app.js             API abrufen, Liste rendern, Bühnenfilter
├── tests/
│   ├── test_schedule.py   Unit-Tests der Business-Logik (ohne DB, ohne HTTP)
│   └── test_api.py        wenige API-Tests (TestClient + In-Memory-SQLite)
├── requirements.txt       Laufzeit: fastapi, uvicorn[standard], sqlalchemy
└── requirements-dev.txt   -r requirements.txt + pytest + httpx
```

`festival.db` entsteht zur Laufzeit im Projektordner und ist per `*.db` von Git ausgeschlossen.

## Verantwortlichkeiten

| Datei | Verantwortung | Abhängig von |
|---|---|---|
| `app/models.py` | ORM-Modelle `Artist`, `Stage`, `Act` inkl. `relationship()` (siehe `domain-model.md`). | SQLAlchemy, `db.Base` |
| `app/db.py` | SQLite-Pfad, Engine, Session-Factory, FastAPI-Dependency `get_db()`, `Base`, `init_db()` (Tabellen anlegen). Reine Infrastruktur, kein Modell mehr. | SQLAlchemy |
| `app/crud.py` | Queries als einfache Funktionen: Bühnenliste (sortiert), Programmliste (`Act` mit Join auf `Artist`/`Stage`, sortiert, optional nach Bühne gefiltert). | `models`, `db` (Session) |
| `app/routers.py` | Die zwei API-Endpunkte, Pydantic-Antwortmodelle; ruft `crud.py` für die Daten und `schedule.py` für den Status auf. | `crud`, `schedule`, FastAPI |
| `app/schedule.py` | `FESTIVAL_TZ`, `festival_now()` und reine Funktion(en), die Acts anhand eines übergebenen Zeitpunkts einen Status zuordnen. | nur `datetime` – **kein** FastAPI, **keine** Session |
| `app/main.py` | App-Objekt, `init_db()` beim Start, bindet `routers.py` und `static/` ein. Enthält selbst keine Endpunkte mehr. | `db`, `routers` |
| `app/seed.py` | `python -m app.seed`: Tabellen anlegen, vorhandene Zeilen löschen, Artists und Stages anlegen, ca. 10–15 Acts auf 3 Bühnen mit FK-Referenzen einfügen. | `db`, `models`, `schedule` |
| `static/*` | Reines HTML/CSS/Vanilla JS. Lädt Bühnen und Programm über die API, rendert die Liste, filtert per Dropdown, hebt Status hervor. | nur die HTTP-API |

## Wo liegt was?

| Bereich | Ort |
|---|---|
| API | `app/routers.py` |
| Datenbank-Infrastruktur | `app/db.py` |
| Modelle | `app/models.py` |
| Datenbank-Queries | `app/crud.py` (Joins über `Artist`/`Stage` – weiterhin nur Funktionen, keine Repository-Klassen) |
| Business-Logik | `app/schedule.py` |
| Frontend | `static/` |
| Tests | `tests/` |

Ablauf einer Anfrage:

```text
app.js ──GET /api/program?stage=X──▶ routers.py ──ruft auf──▶ crud.py ──select+join──▶ db.py (SQLite)
                                          │
                                          └──items + now──▶ schedule.py ──status──▶ JSON
```

## HTTP-API

Ein Prozess (uvicorn) liefert API und Frontend aus (T2).

**API-Vertrag bleibt unverändert (Entscheidung):** Obwohl `Act` selbst keine `title`/`stage`-
Felder mehr hat (siehe `domain-model.md`), liefert die API weiterhin flache Strings – befüllt
aus `act.artist.name` bzw. `act.stage.name`. So bleibt `static/app.js` unverändert; das ist
Voraussetzung für „Funktionalität erhalten" in Phase 1.

### `GET /api/program?stage=<name>`

Programmpunkte chronologisch nach `starts_at` sortiert, bei gleicher Startzeit alphabetisch
nach Bühnenname (`ORDER BY Act.starts_at, Stage.name` über den Join – feste Reihenfolge, auch
für Tests), optional nach Bühne gefiltert (B1).
Eine unbekannte Bühne liefert eine leere Liste, keinen Fehler.

```json
{
  "now": "2026-09-10T14:05:00",
  "items": [
    {
      "id": 1,
      "title": "Band A",
      "stage": "Hauptbühne",
      "starts_at": "2026-09-10T13:30:00",
      "ends_at": "2026-09-10T14:30:00",
      "status": "now"
    }
  ]
}
```

`title` kommt aus `Artist.name`, `stage` aus `Stage.name` (Join in `crud.py`). `status` ist
`"now"`, `"next"` oder `null`. `now` ist die serverseitig bestimmte Festival-Zeit (T3), damit
das Frontend sie anzeigen kann.

### `GET /api/stages`

Alphabetisch sortierte Liste der Bühnennamen aus der `Stage`-Tabelle, für das Filter-Dropdown.

```json
["Hauptbühne", "Waldbühne", "Zeltbühne"]
```

### `GET /`

Liefert `static/index.html`; `static/` wird per `StaticFiles` eingebunden.

## Business-Logik: „läuft jetzt" / „kommt als Nächstes"

Regeln für einen Zeitpunkt `now`:

- **now:** `starts_at <= now < ends_at`. Mehrere Treffer sind möglich (parallele Bühnen).
- **next:** alle Punkte, deren `starts_at` der früheste Startzeitpunkt nach `now` ist
  (bei gleicher Startzeit mehrere).
- sonst `null`.

Der Status wird **nach** dem Bühnenfilter berechnet. Dadurch ist „als Nächstes" auf einer
gefilterten Bühne automatisch korrekt (Benutzeraktion 4).

Die Funktionen bekommen `now` als Parameter – sie lesen die Uhr nicht selbst. Das macht sie
ohne Tricks testbar.

## Zeit und Zeitzone

- `FESTIVAL_TZ` ist der feste Offset UTC+02:00 (Entscheidung in `CLAUDE.md`).
- Zeitstempel werden **naiv in Festival-Ortszeit** gespeichert (ohne Zeitzonen-Info).
  SQLite speichert ohnehin keine Zeitzone, und die Seed-Daten bleiben lesbar.
- `festival_now()` liefert passend dazu die aktuelle Zeit in UTC+02:00, ebenfalls naiv.
- In `routers.py` wird `festival_now` als FastAPI-Dependency verwendet. Tests ersetzen sie über
  `app.dependency_overrides` durch einen festen Zeitpunkt.

## Datenbank

- Drei Tabellen für `Artist`, `Stage`, `Act` (siehe `domain-model.md`), angelegt per
  `Base.metadata.create_all` in `init_db()` – beim App-Start und im Seed-Skript.
- Keine Migrationen: Bei Schemaänderungen wird die Datenbank gelöscht und neu geseedet.
- Nicht offensichtlich: Die Engine braucht `connect_args={"check_same_thread": False}`, weil
  FastAPI synchrone Endpunkte in einem Threadpool ausführt und SQLite Verbindungen sonst an
  einen Thread bindet.

## Seed-Daten

Das Seed-Skript legt das Festival auf das **heutige Datum** (in Festival-Zeit). So läuft in
einer Demo tatsächlich gerade etwas, ohne dass eine Funktion zum Simulieren der Uhrzeit nötig ist.
Reihenfolge beim Einfügen: erst `Artist`- und `Stage`-Zeilen, danach `Act`-Zeilen mit den
passenden FK-Referenzen.

## Frontend

- Beim Laden: `GET /api/stages` für das Dropdown, dann `GET /api/program`.
- Bei Filterwechsel: erneut `GET /api/program?stage=…`.
- Anzeige: Liste mit Uhrzeit (HH:MM), Titel, Bühne; `status` wird als CSS-Klasse gesetzt.
- Aktualisierung durch Neuladen der Seite – keine Echtzeit-Updates (Scope-Abgrenzung).

## Tests

Start mit `python -m pytest` im Projektordner. Durch `python -m` liegt das Projektverzeichnis
im Importpfad – daher keine `conftest.py` und keine `pytest.ini` nötig.

- `tests/test_schedule.py` – der Schwerpunkt: Statusregeln inkl. Randfällen (genau
  Start-/Endzeitpunkt, parallele Acts, gleiche Startzeiten, nichts mehr kommt, gefilterte Liste).
- `tests/test_api.py` – wenige Tests: Sortierung, Bühnenfilter, Bühnenliste, `status` im JSON.
  Nutzt In-Memory-SQLite und ersetzt `get_db` und `festival_now` per `dependency_overrides`.
  Fixtures legen jetzt erst `Artist`- und `Stage`-Zeilen an und referenzieren sie aus `Act`.
  Nicht offensichtlich: In-Memory-SQLite existiert nur pro Verbindung – deshalb mit
  `poolclass=StaticPool`, damit alle Sessions dieselbe Datenbank sehen.

## Bewusst weggelassen

- `schemas.py`, `services/`, Repository-Klassen – Pydantic-Antwortmodelle bleiben in
  `routers.py`, `crud.py` besteht aus einfachen Funktionen statt Klassen.
- `config.py` / `.env` – DB-Pfad und Zeitzone sind Konstanten im Code
- Alembic-Migrationen
- Jinja-Templates, npm/Build-Tooling, `src/`-Layout, Docker, `conftest.py`

## Erweiterungspunkte (nicht in der aktuellen Version)

- **Konflikterkennung** ist nicht Teil der bestätigten Anforderungen (nur O7, setzt Favoriten
  O4 voraus; laut Domain Model sind Überlappungen erlaubt). Käme sie hinzu, wäre sie eine
  weitere reine Funktion in `app/schedule.py` – erst nach Anpassung der Anforderungen.
- **Tagesfilter (O1):** zusätzlicher Query-Parameter in `/api/program`, kein Schema-Umbau.
- **Weitere Attribute:** Genre auf `Artist`, Kapazität/Standort auf `Stage` – durch die
  Entitätstrennung jetzt ohne Umbau von `Act` möglich (siehe `domain-model.md`).

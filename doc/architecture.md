# Architektur & Projektstruktur

Status: laufend, Stand 2026-09-18. Phase 1 (v0.2) hat die ursprüngliche Ein-Datei-Struktur
(`db.py` mit Modell + Queries direkt in `main.py`) abgelöst; die Struktur wächst seitdem
schrittweise mit den Anforderungen weiter, statt auf einem MVP-Stand zu verharren. Phase 2
(v0.2) hat die Datenhaltung von SQLite auf PostgreSQL (Neon) umgestellt – ohne Änderung an
Modellen, API-Vertrag oder Frontend.

Grundlage: [`requirements.md`](requirements.md), [`domain-model.md`](domain-model.md) und die
Entscheidungen in [`../CLAUDE.md`](../CLAUDE.md) (Festival-Zeitzone UTC+02:00, pytest + httpx
als Dev-Dependencies).

Leitlinie: nicht mehr „so klein wie möglich" (MVP), sondern gut strukturiert und erweiterbar –
die Struktur nimmt Schritt für Schritt an Komplexität zu, sobald das Projekt es verlangt. Mit
drei Entitäten (`Artist`, `Stage`, `Act`) und Joins reicht eine einzige Datei für Modell +
Queries + Endpunkte nicht mehr aus – deshalb kommen `models.py`, `crud.py` und `routers.py`
dazu. Jede weitere Schicht (Datei, Paket, Klasse) wird eingeführt, sobald sie einen konkreten
Bedarf löst – nicht spekulativ auf Vorrat, aber auch nicht mehr aus Prinzip vermieden. Siehe
„Erweiterungspunkte" für absehbare nächste Schritte.

## Projektstruktur

```text
festival-planner/
├── app/
│   ├── __init__.py        leer – macht app/ zum importierbaren Paket
│   ├── main.py            FastAPI-App: Objekt, Lifespan (init_db), bindet routers.py + static/ ein
│   ├── models.py          ORM-Modelle: Artist, Stage, Act (siehe domain-model.md)
│   ├── db.py              Datenbank-Infrastruktur: DATABASE_URL aus .env, Engine, Session, init_db(), get_db()
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
│   ├── test_models.py     DB-seitige Invarianten der Modelle (In-Memory-SQLite)
│   └── test_api.py        wenige API-Tests (TestClient + In-Memory-SQLite, nicht Neon)
├── .env                   DATABASE_URL (nicht eingecheckt)
├── requirements.txt       Laufzeit: fastapi, uvicorn[standard], sqlalchemy, psycopg[binary], python-dotenv
└── requirements-dev.txt   -r requirements.txt + pytest + httpx
```

Die Programmdaten liegen in einer PostgreSQL-Datenbank bei Neon; es entsteht keine lokale
Datenbankdatei mehr. `.env` mit der `DATABASE_URL` ist per `.gitignore` von Git ausgeschlossen.

## Verantwortlichkeiten

| Datei | Verantwortung | Abhängig von |
|---|---|---|
| `app/models.py` | ORM-Modelle `Artist`, `Stage`, `Act` inkl. `relationship()` (siehe `domain-model.md`). | SQLAlchemy, `db.Base` |
| `app/db.py` | `DATABASE_URL` aus `.env` laden und auf den `psycopg`-Treiber normalisieren, Engine, Session-Factory, FastAPI-Dependency `get_db()`, `Base`, `init_db()` (Tabellen anlegen). Reine Infrastruktur, kein Modell mehr. | SQLAlchemy, `psycopg`, `python-dotenv` |
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
app.js ──GET /api/program?stage=X──▶ routers.py ──ruft auf──▶ crud.py ──select+join──▶ db.py (PostgreSQL/Neon)
                                          │
                                          └──items + now──▶ schedule.py ──status──▶ JSON
```

## HTTP-API

Ein Prozess (uvicorn) liefert API und Frontend aus (T2).

**API-Vertrag: flach statt verschachtelt (Entscheidung, T-4).** Obwohl `Act` selbst keine
`title`/`stage`-Felder mehr hat (siehe `domain-model.md`), liefert die API weiterhin flache
Strings – befüllt aus `act.artist.name` bzw. `act.stage.name`.

Verworfene Alternative – verschachtelte Objekte, die die neue Entitätstrennung 1:1 abbilden:

```json
{
  "id": 1,
  "artist": { "name": "Band A" },
  "stage": { "name": "Hauptbühne" },
  "starts_at": "2026-09-10T13:30:00",
  "ends_at": "2026-09-10T14:30:00",
  "status": "now"
}
```

Dagegen entschieden, weil:

* `static/app.js` erwartet `item.title` und `item.stage` als Strings; mit verschachtelten
  Objekten müsste das Frontend angepasst werden.
* Phase 1 hat als Ziel „Funktionalität erhalten, nur Datenbank-Struktur ändern" – ein
  Frontend-Umbau gehört nicht dazu und würde Scope und Risiko unnötig vergrößern.
* Der flache Vertrag ist für die aktuellen zwei Endpunkte ausreichend; eine spätere
  Erweiterung um zusätzliche Felder (z. B. Genre, Kapazität) ist auch mit flachen Strings
  möglich (siehe „Erweiterungspunkte" unten), ohne dass sich der Vertrag grundsätzlich
  ändern muss.

Der Preis dieser Entscheidung: `crud.py` muss die Umbenennung (`artist.name` → `title`,
`stage.name` → `stage`) explizit vornehmen – die Pydantic-Antwortmodelle in `routers.py`
bilden das ORM-Modell also nicht direkt ab.

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
  Die Spalten sind `DateTime` ohne `timezone=True`, in PostgreSQL also
  `timestamp without time zone`; damit bleiben die Seed-Daten lesbar und es gibt keine
  implizite Umrechnung.
- `festival_now()` liefert passend dazu die aktuelle Zeit in UTC+02:00, ebenfalls naiv.
- In `routers.py` wird `festival_now` als FastAPI-Dependency verwendet. Tests ersetzen sie über
  `app.dependency_overrides` durch einen festen Zeitpunkt.

## Datenbank

- **PostgreSQL, gehostet bei Neon** (seit v0.2 Phase 2, vorher eine lokale SQLite-Datei).
  Treiber ist `psycopg` (v3).
- Die Verbindung kommt aus `DATABASE_URL` in `.env` und wird in `db.py` per `python-dotenv`
  geladen – nicht im Code verdrahtet (B2). `.env` ist nicht eingecheckt.
- Fehlt die Variable, bricht `db.py` beim Import mit einem `RuntimeError` ab, der `.env` und
  das erwartete Format nennt. Bewusst **kein** stiller SQLite-Fallback: der würde eine
  Fehlkonfiguration im Betrieb verdecken.
- `pool_pre_ping=True` an der Engine: Neon fährt die Compute-Instanz im Leerlauf herunter, und
  im Pool bleiben dann tote Verbindungen liegen. Ohne den Check scheitert der erste Request
  nach einer Pause; mit ihm verwirft SQLAlchemy die Verbindung und baut eine neue auf.
- Nicht offensichtlich: `load_dotenv()` sucht die `.env` **datei-relativ** (aufwärts ab
  `app/db.py`), nicht im Arbeitsverzeichnis – der Start aus einem anderen Ordner funktioniert
  also. Ausnahme: im REPL, unter einem Debugger oder bei `python -c` fällt python-dotenv auf
  das aktuelle Arbeitsverzeichnis zurück; dann wird die `.env` nur dort gefunden.
- Nicht offensichtlich: Eine `postgresql://`-URL wird in `db.py` auf `postgresql+psycopg://`
  normalisiert. SQLAlchemy erwartet bei der kurzen Form sonst `psycopg2`, das nicht
  installiert ist.
- Drei Tabellen für `Artist`, `Stage`, `Act` (siehe `domain-model.md`), angelegt per
  `Base.metadata.create_all` in `init_db()` – beim App-Start und im Seed-Skript.
- Datenintegrität: `ends_at > starts_at` ist als `CheckConstraint` auf `Act` DB-seitig
  erzwungen, nicht nur in der Business-Logik.
- Keine Migrationen: Bei Schemaänderungen wird die Datenbank gelöscht und neu geseedet.
- `connect_args={"check_same_thread": False}` ist mit dem Wechsel weggefallen – das war eine
  reine SQLite-Eigenheit. In `tests/test_api.py` steht es weiterhin, weil die Tests eine
  In-Memory-SQLite-DB verwenden.

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
- `tests/test_models.py` – die DB-seitige Invariante `ends_at > starts_at` (`CheckConstraint`):
  Ende nach Start wird angenommen, Ende vor Start und Ende gleich Start werden mit
  `IntegrityError` abgelehnt. Eigene Engine pro Test (Fixture), kein `TestClient`. Läuft unter
  In-Memory-SQLite, weil SQLite CHECK-Constraints ebenfalls durchsetzt.
- `tests/test_api.py` – wenige Tests: Sortierung, Bühnenfilter, Bühnenliste, `status` im JSON.
  Nutzt In-Memory-SQLite – bewusst **nicht** die PostgreSQL-Datenbank: die Tests laufen so
  ohne Netzwerk und hinterlassen keine Daten in Neon. Der Preis: die migrierte
  Infrastrukturschicht (URL-Normalisierung, psycopg-Verbindung, PostgreSQL-spezifisches
  Verhalten) wird dadurch nicht abgedeckt. Ersetzt `get_db` und `festival_now` per
  `dependency_overrides`.
  Nicht offensichtlich: Eine gesetzte `DATABASE_URL` brauchen die Tests trotzdem. Sie
  importieren `Base`/`get_db` aus `app.db`, und `db.py` prüft die Variable beim Import – ohne
  `.env` bricht `python -m pytest` deshalb schon beim Collect ab, allerdings mit einer klaren
  Meldung (siehe „Datenbank"). Eine Verbindung wird dabei nicht aufgebaut, `create_engine`
  verbindet erst bei Bedarf.
  Fixtures legen jetzt erst `Artist`- und `Stage`-Zeilen an und referenzieren sie aus `Act`.
  Nicht offensichtlich: In-Memory-SQLite existiert nur pro Verbindung – deshalb mit
  `poolclass=StaticPool`, damit alle Sessions dieselbe Datenbank sehen.

## Aktuell nicht vorhanden (kein grundsätzliches Verbot mehr, nur noch kein Bedarf)

- `schemas.py`, `services/`, Repository-Klassen, Paket-Split (`app/api/`, `app/domain/`,
  `app/infra/`, …) – bei 7 flachen Modulen noch kein klarer Vorteil; siehe
  „Erweiterungspunkte" für die Bedingungen, unter denen das sinnvoll wird.
- `config.py` – `.env` gibt es inzwischen (`DATABASE_URL`), aber nur eine einzige Variable,
  direkt in `db.py` gelesen; ein eigenes Konfigurationsmodul lohnt sich erst bei mehreren
  Werten oder mehreren Umgebungen. Die Zeitzone bleibt eine Konstante im Code.
- Alembic-Migrationen – kommt, sobald Schemaänderungen nicht mehr per Löschen und
  Neu-Seeden gelöst werden sollen (z. B. produktive Daten, die erhalten bleiben müssen).
- Jinja-Templates, npm/Build-Tooling, Docker, `conftest.py` – kommen mit den jeweiligen
  Anforderungen (serverseitiges Rendering, Frontend-Build, Deployment, wachsende Testsuite).

## Erweiterungspunkte (nicht in der aktuellen Version)

- **Konflikterkennung** ist nicht Teil der bestätigten Anforderungen (nur O7, setzt Favoriten
  O4 voraus; laut Domain Model sind Überlappungen erlaubt). Käme sie hinzu, wäre sie eine
  weitere reine Funktion in `app/schedule.py` – erst nach Anpassung der Anforderungen.
- **Tagesfilter (O1):** zusätzlicher Query-Parameter in `/api/program`, kein Schema-Umbau.
- **Weitere Attribute:** Genre auf `Artist`, Kapazität/Standort auf `Stage` – durch die
  Entitätstrennung jetzt ohne Umbau von `Act` möglich (siehe `domain-model.md`).
- **Paket-Split (`app/api/`, `app/domain/`, `app/infra/`, …):** sinnvoll, sobald einzelne
  Module wachsen (z. B. mehrere Router-Dateien, mehrere Domain-Module) oder neue fachliche
  Bereiche dazukommen. Die heutige Verantwortlichkeiten-Tabelle oben ist bereits die
  Layer-Zuordnung (`main.py` = Composition Root, `routers.py` = API, `crud.py` = Data Access,
  `models.py`/`schedule.py` = Domain, `db.py` = Infrastruktur) – ein Split würde bestehende
  Dateien nur in Unterpakete gruppieren, ohne ihre Verantwortung zu ändern.

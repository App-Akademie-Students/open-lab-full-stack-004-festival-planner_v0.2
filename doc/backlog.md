# Backlog

Status: Stand 2026-09-18. v0.1 bestätigt und umgesetzt (Roadmap-Schritt 9). v0.2 ist
umgesetzt, in zwei Phasen: Refactoring Phase 1 (T-1 bis T-9, `Artist`/`Stage`/`Act` statt
`ProgramItem`) und Refactoring Phase 2 (T-10 bis T-13, Umstellung von SQLite auf PostgreSQL
bei Neon) – siehe die beiden Abschnitte unten.

Testen und Reviewen ist für beide Phasen erledigt und in [`review.md`](review.md)
freigegeben: Phase 1 in Abschnitt 6 (Stand 2026-09-16), die PostgreSQL-Umstellung in
Abschnitt 7 (Stand 2026-09-18). Beide Urteile: „Freigeben mit nicht blockierenden
Änderungswünschen", keine Blocker. T-19 bis T-21 aus dem Phase-2-Review sind inzwischen
umgesetzt; offen sind nur noch T-15 bis T-18 im Abschnitt „Offene Punkte aus dem Review".

Abgeleitet aus den Muss-Anforderungen in [`requirements.md`](requirements.md).
Technischer Rahmen: [`architecture.md`](architecture.md).

## Übersicht

Reihenfolge = Priorität. Status: `offen` · `in Arbeit` · `erledigt`

| ID | Titel | Abhängig von | Anforderungen | Status |
|---|---|---|---|---|
| T-0 | Projektgerüst (technische Aufgabe) | – | B2, T2 | erledigt |
| US-1 | Programm einspielen | T-0 | B2, B3, B4, C4 | erledigt |
| US-2 | Programm als Liste sehen | US-1 | C1, F1, B1, T2 | erledigt |
| US-3 | Sehen, was gerade läuft | US-2 | C2, F3, T3 | erledigt |
| US-4 | Sehen, was als Nächstes kommt | US-2 | C2, F3 | erledigt |
| US-5 | Nach Bühne filtern | US-2 | C3, F2, B1 | erledigt |
| US-6 | Programm auf dem Smartphone nutzen | US-2 | F4, T1 | erledigt |

```text
T-0 ──▶ US-1 ──▶ US-2 ──┬──▶ US-3  „läuft jetzt"
                        ├──▶ US-4  „als Nächstes"
                        ├──▶ US-5  Bühnenfilter
                        └──▶ US-6  Mobil
```

Nach US-2 existiert eine lauffähige, bereits nützliche Version. US-3 bis US-6 hängen nur von
US-2 ab und sind untereinander unabhängig.

## Stories

### T-0 · Projektgerüst (technische Aufgabe)

Kein Nutzen für Besucher, aber Voraussetzung dafür, dass Start, Tests und Struktur
funktionieren, bevor Features gebaut werden.

- [x] Ordner und Dateien laut `architecture.md` sind angelegt (`app/`, `static/`, `tests/`),
      dazu `requirements-dev.txt` mit pytest und httpx.
- [x] `uvicorn app.main:app --reload` startet fehlerfrei; `/` liefert eine (noch leere) `index.html`.
- [x] `python -m pytest` läuft grün.

### US-1 · Programm einspielen

> Als **Betreiber** möchte ich das Festivalprogramm per Skript in die Datenbank laden,
> damit Besucher ohne Admin-Oberfläche echte Programmdaten sehen.

- [x] `python -m app.seed` legt das Schema in der über `DATABASE_URL` konfigurierten Datenbank
      an und füllt ca. 10–15 Programmpunkte auf 3 Bühnen.
- [x] Alle Punkte liegen auf dem heutigen Datum (Festival-Zeit) mit vollständigen Zeitstempeln –
      inklusive paralleler Acts auf verschiedenen Bühnen und mindestens zwei Acts mit gleicher Startzeit.
- [x] Jeder Punkt erfüllt die Invarianten: Titel und Bühne nicht leer, Ende nach Start.
- [x] Erneutes Ausführen ersetzt die Daten (keine Duplikate).

### US-2 · Programm als Liste sehen

> Als **Besucher** möchte ich das komplette Tagesprogramm als chronologische Liste sehen,
> damit ich weiß, welcher Act wann auf welcher Bühne spielt.

- [x] Die Startseite zeigt alle Programmpunkte mit Start- und Endzeit (HH:MM), Titel und Bühne – ohne Login.
- [x] Sortiert nach Startzeit; bei gleicher Startzeit alphabetisch nach Bühne.
- [x] `GET /api/program` liefert dieselben Punkte in derselben Reihenfolge als JSON.
- [x] Ist die Datenbank leer, zeigt die Seite einen Hinweis statt einer leeren Fläche.

### US-3 · Sehen, was gerade läuft

> Als **Besucher** möchte ich sofort sehen, was gerade läuft,
> damit ich weiß, wo ich jetzt hingehen kann.

- [x] Punkte mit `Start ≤ jetzt < Ende` sind als „läuft jetzt" hervorgehoben; mehrere gleichzeitig möglich.
- [x] Genau zur Startzeit gilt ein Act als „läuft jetzt", genau zur Endzeit nicht mehr.
- [x] „Jetzt" ist die serverseitige Festival-Zeit (UTC+02:00), nicht die Geräteuhr; sie wird auf der Seite angezeigt.
- [x] Aktualisierung durch Neuladen der Seite (kein Auto-Refresh).

### US-4 · Sehen, was als Nächstes kommt

> Als **Besucher** möchte ich sehen, was als Nächstes kommt,
> damit ich meinen nächsten Bühnenwechsel planen kann.

- [x] Die Punkte mit der frühesten Startzeit nach „jetzt" sind als „als Nächstes" hervorgehoben –
      bei gleicher Startzeit mehrere.
- [x] „Als Nächstes" ist optisch von „läuft jetzt" unterscheidbar.
- [x] Vor Festivalbeginn ist nichts „läuft jetzt", die ersten Acts sind „als Nächstes";
      nach dem letzten Act ist nichts hervorgehoben – ohne Fehler.

### US-5 · Nach Bühne filtern

> Als **Besucher** möchte ich das Programm auf eine Bühne einschränken,
> damit ich mich auf diese Bühne konzentrieren kann.

- [x] Ein Auswahlfeld bietet „Alle Bühnen" und alle Bühnen aus `GET /api/stages` (alphabetisch).
- [x] Die Auswahl zeigt nur Punkte dieser Bühne, weiterhin chronologisch; „Alle Bühnen" zeigt wieder alles.
- [x] `GET /api/program?stage=X` filtert serverseitig; eine unbekannte Bühne liefert eine leere Liste.
- [x] Sind US-3/US-4 umgesetzt, beziehen sich „läuft jetzt" und „als Nächstes" auf die gewählte Bühne.

### US-6 · Programm auf dem Smartphone nutzen

> Als **Besucher** möchte ich das Programm auf dem Smartphone bequem lesen,
> damit ich es auf dem Festivalgelände nutzen kann.

- [x] Bei 360 px Breite ist alles ohne horizontales Scrollen lesbar.
- [x] Der Bühnenfilter ist per Touch bedienbar.
- [x] Nur HTML, CSS und Vanilla JS – kein Build-Schritt.

## Abdeckung der Muss-Anforderungen

| Anforderung | Story | Anforderung | Story |
|---|---|---|---|
| C1 | US-2 | B1 | US-2, US-5 |
| C2 | US-3, US-4 | B2 | T-0, US-1 |
| C3 | US-5 | B3 | US-1 |
| C4 | US-1 | B4 | US-1 |
| F1 | US-2 | T1 | US-6, alle |
| F2 | US-5 | T2 | T-0, US-2 |
| F3 | US-3, US-4 | T3 | US-3 |
| F4 | US-6 | | |

## Definition of Done (für jede Story)

- Alle Akzeptanzkriterien erfüllt und im Browser geprüft.
- Neue Business-Logik in `app/schedule.py` ist in `tests/test_schedule.py` getestet;
  neue oder geänderte Endpunkte haben einen Test in `tests/test_api.py`.
- `python -m pytest` ist grün.
- Keine neuen Dependencies; Doku und `CLAUDE.md` sind aktuell, falls sich Entscheidungen geändert haben.
- Status in der Übersicht oben aktualisiert.

## v0.2 – Refactoring Phase 1 (Datenbank-Fokus)

Technische Aufgaben ohne direkten Besucher-Nutzen, Voraussetzung für spätere Erweiterungen
(z. B. Genre auf `Artist`, Kapazität auf `Stage`). Funktionalität und Datenbank bleiben in
dieser Phase unverändert (damals noch SQLite; die Umstellung auf PostgreSQL erfolgt erst in
Phase 2, T-10 bis T-13).
Details und Reihenfolge: [`roadmap.md`](roadmap.md) (Phase 2), technischer Rahmen:
[`architecture.md`](architecture.md).

| ID | Titel | Abhängig von | Status |
|---|---|---|---|
| T-1 | Domain Model erweitern (`Artist`, `Stage`, `Act`) | – | erledigt |
| T-2 | Architektur aktualisieren | T-1 | erledigt |
| T-3 | `app/models.py` anlegen | T-2 | erledigt |
| T-4 | API-Vertrag entscheiden (flach vs. verschachtelt) | T-3 | erledigt |
| T-5 | `app/seed.py` auf `Artist`/`Stage`/`Act` umstellen | T-4 | erledigt |
| T-6 | `app/crud.py` einführen (Queries mit Joins) | T-5 | erledigt |
| T-7 | `app/routers.py` einführen, `main.py` auf App-Setup reduzieren | T-6 | erledigt |
| T-8 | Tests umstellen (`tests/test_api.py` auf neue Modelle/Fixtures) | T-7 | erledigt |
| T-9 | `app/db.py` auf reine Infrastruktur reduzieren (`ProgramItem` entfernen) | T-8 | erledigt |

**T-4 – Entscheidung:** API-Vertrag bleibt flach (nicht verschachtelt). Begründung und
Beispiel: [`architecture.md`](architecture.md#http-api).

## v0.2 – Refactoring Phase 2 (Umstellung auf PostgreSQL)

Ebenfalls technische Aufgaben ohne direkten Besucher-Nutzen: die Datenhaltung wechselt von
der lokalen SQLite-Datei auf eine gehostete PostgreSQL-Datenbank (Neon). Funktionalität,
API-Vertrag und Frontend bleiben unverändert. Entscheidung und Begründung:
[`../CLAUDE.md`](../CLAUDE.md#project-decisions), technischer Rahmen:
[`architecture.md`](architecture.md#datenbank).

| ID | Titel | Abhängig von | Status |
|---|---|---|---|
| T-10 | `DATABASE_URL` aus `.env` laden (`python-dotenv`), Engine auf PostgreSQL umstellen | – | erledigt |
| T-11 | Treiber `psycopg` (v3): URL-Normalisierung in `db.py`, `requirements.txt` ergänzen | T-10 | erledigt |
| T-12 | `ends_at > starts_at` zusätzlich als DB-seitige `CheckConstraint` auf `Act` | T-10 | erledigt |
| T-13 | Doku nachziehen (`requirements.md` B2/T1, `domain-model.md`, `architecture.md`, `CLAUDE.md`, Backlog, Roadmap) | T-11, T-12 | erledigt |
| T-14 | Review-Nachtrag zur Umstellung in [`review.md`](review.md) ergänzen | T-13 | erledigt |

**T-10 bis T-12 – Entscheidungen:** `.env` ist nicht eingecheckt (siehe `.gitignore`); eine
`postgresql://`-URL wird in `db.py` auf `postgresql+psycopg://` normalisiert, weil SQLAlchemy
sonst `psycopg2` erwartet. Tests laufen weiterhin gegen In-Memory-SQLite, nicht gegen Neon.

## Offene Punkte aus dem Review (nicht blockierend)

Aus [`review.md`](review.md) (Abschnitte 2–4 und Nachtrag). Keiner dieser Punkte verletzt eine
Muss-Anforderung; sie sind hier nur festgehalten, damit sie nicht verloren gehen.

Aus Abschnitt 6 (Phase 1):

| ID | Titel | Status |
|---|---|---|
| T-15 | TODO `# TODO move to rest_schema.py` in `app/routers.py` klären – widerspricht der dokumentierten „kein `schemas.py`"-Entscheidung; entweder entfernen oder als neue Entscheidung in `architecture.md` dokumentieren | offen |
| T-16 | Test-Overrides in `tests/test_api.py` von Modulebene in eine Fixture mit Teardown überführen | offen |
| T-17 | `StaticFiles`-Pfad in `app/main.py` unabhängig vom aktuellen Arbeitsverzeichnis auflösen | offen |
| T-18 | Invarianten `Artist.name` / `Stage.name` nicht leer als DB-`CheckConstraint` (analog T-12) | offen |

Aus Abschnitt 7 (PostgreSQL-Umstellung) – alle drei umgesetzt am 2026-09-18:

| ID | Titel | Status |
|---|---|---|
| T-19 | Fehlende `DATABASE_URL` klar melden statt `KeyError`: `app/db.py` prüft die Variable und bricht mit Hinweis auf `.env` ab. Wichtig, weil ohne `.env` auch `python -m pytest` beim Collect abbricht – obwohl die Tests nur In-Memory-SQLite brauchen | erledigt |
| T-20 | `create_engine(..., pool_pre_ping=True)` gegen abgestandene Verbindungen nach Neons Idle-Suspend | erledigt |
| T-21 | Test für die `CheckConstraint` `ends_at > starts_at` (läuft auch unter In-Memory-SQLite) | erledigt |

**Hinweis (keine Aufgabe):** Da `app/seed.py` per `DELETE` löscht, laufen die
PostgreSQL-Sequenzen beim Neu-Seeden weiter – die `id`-Werte beginnen also nicht wieder bei 1
wie früher unter SQLite. Rein kosmetisch (IDs sind technisch und werden im Frontend nicht
genutzt); falls doch gewünscht: `TRUNCATE ... RESTART IDENTITY`. Details in
[`review.md`](review.md), Abschnitt 7.

Langfristig, ohne aktuellen Bedarf: `create_all` beim App-Start durch Migrationen ersetzen
(siehe „Aktuell nicht vorhanden" in [`architecture.md`](architecture.md)).

## Bewusst nicht im Backlog

Favoriten, Suche, Tagesfilter, Detailansicht, Admin-UI, Auto-Refresh, Konflikterkennung –
siehe optionale Anforderungen O1–O8 und Scope-Abgrenzung in [`requirements.md`](requirements.md).

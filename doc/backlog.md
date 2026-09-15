e# Backlog – MVP

Status: bestätigt (Roadmap-Schritt 9)

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

- [x] `python -m app.seed` legt `festival.db` an und füllt ca. 10–15 Programmpunkte auf 3 Bühnen.
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

## Bewusst nicht im Backlog

Favoriten, Suche, Tagesfilter, Detailansicht, Admin-UI, Auto-Refresh, Konflikterkennung –
siehe optionale Anforderungen O1–O8 und Scope-Abgrenzung in [`requirements.md`](requirements.md).

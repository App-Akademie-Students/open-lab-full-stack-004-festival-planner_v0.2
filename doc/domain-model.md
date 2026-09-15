# Domain Model – MVP

Status: bestätigt (Roadmap-Schritt 7)

Abgeleitet aus den Muss-Anforderungen in [`requirements.md`](requirements.md).
Ziel: das kleinstmögliche Modell, das die Anforderungen trägt.

## Ableitung aus den Anforderungen

| Anforderung | Bedarf am Modell |
|---|---|
| F1 – Liste (Titel, Bühne, Start, Ende) | ein Datensatz pro Programmpunkt mit genau diesen Feldern |
| F2 / C3 – Filter nach Bühne | Bühne als abfragbares Feld; Bühnenliste via `SELECT DISTINCT stage` |
| F3 / C2 – „läuft jetzt" / „als Nächstes" | rein aus `starts_at` / `ends_at` vs. aktueller Zeit berechnet – nichts Zusätzliches zu speichern |
| B1 – sortierte API | Sortierung über `starts_at`, kein Feld nötig |
| B2 / B3 – SQLite, Seed | eine Tabelle, die das Seed-Skript füllt |
| B4 – volle Zeitstempel | `starts_at` / `ends_at` als `datetime`, nicht nur `time` |
| C1 – kein Login | keine User-/Auth-/Favoriten-Entität |
| C4 – eine Instanz = ein Festival | „Festival" ist Konfiguration/Kontext, keine Entität |

## Das Modell

**Genau eine Entität: `ProgramItem`** (Programmpunkt / Act-Slot)

| Attribut | Typ | Pflicht | Zweck / Regel |
|---|---|---|---|
| `id` | Integer, PK, autoincrement | ja | technische Identität |
| `title` | String (nicht leer) | ja | Name des Acts / Programmpunkts (F1) |
| `stage` | String (nicht leer) | ja | Bühnenname, Freitext (F1/F2) |
| `starts_at` | DateTime (Datum + Uhrzeit) | ja | Beginn (F1/F3/B1/B4) |
| `ends_at` | DateTime (Datum + Uhrzeit) | ja | Ende (F1/F3), Regel: `ends_at > starts_at` |

### Invarianten (fachlich)

- `title` und `stage` sind nicht leer.
- `ends_at` liegt echt nach `starts_at`.
- Zeiten werden in einer festen Festival-Zeitzone interpretiert (siehe T3 in `requirements.md`).
- Überlappungen auf derselben Bühne sind erlaubt – keine Validierung im MVP.

## Was persistent gespeichert wird

- Nur `ProgramItem`-Zeilen (eine Tabelle in SQLite).

## Was NICHT gespeichert / nicht modelliert wird

- „läuft jetzt" / „als Nächstes" – zur Laufzeit berechnet.
- Sortierreihenfolge – Query (`ORDER BY starts_at, stage`).
- Liste der Bühnen – abgeleitet (`SELECT DISTINCT stage`).
- Festival, Tag/Datum als eigene Entität, Genre, Beschreibung, Künstlerprofil.
- Nutzer, Sessions, Favoriten, Merkzettel (C1 – kein Login).

## Erweiterbarkeits-Leitplanke (nur Hinweis, keine Umsetzung)

- `starts_at` / `ends_at` als volle Zeitstempel ⇒ späterer Tagesfilter (O1) ist reine
  Query-/Anzeige-Logik (`GROUP BY date(starts_at)`), kein Schema-Umbau.
- Spätere Normalisierung zu einer `Stage`-Entität bleibt möglich, indem `stage` (String)
  durch `stage_id` (FK) ersetzt wird – bewusst nicht jetzt.

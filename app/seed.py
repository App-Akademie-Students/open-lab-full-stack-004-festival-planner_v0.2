"""Seed script: creates the schema and fills the program for today.

Run with `python -m app.seed`. Re-running replaces all existing data
(no duplicates).
"""
from datetime import date, datetime

from app.db import ProgramItem, SessionLocal, init_db
from app.schedule import festival_now

# (title, stage, start_hour, start_minute, end_hour, end_minute)
SLOTS = [
    ("Opener Band", "Hauptbühne", 12, 0, 13, 0),
    ("Folk Trio", "Waldbühne", 12, 0, 13, 0),
    ("DJ Sunrise", "Zeltbühne", 12, 30, 13, 30),
    ("Rock Rebels", "Hauptbühne", 13, 0, 14, 30),
    ("Acoustic Set", "Waldbühne", 13, 30, 14, 30),
    ("Beat Collective", "Zeltbühne", 14, 0, 15, 0),
    ("Indie Waves", "Hauptbühne", 14, 30, 16, 0),
    ("String Quartet", "Waldbühne", 15, 0, 16, 0),
    ("Electro Pulse", "Zeltbühne", 15, 30, 17, 0),
    ("Headliner One", "Hauptbühne", 16, 30, 18, 30),
    ("Chill Session", "Waldbühne", 16, 30, 17, 30),
    ("Bass Drop", "Zeltbühne", 17, 30, 19, 0),
    ("Sunset Groove", "Waldbühne", 18, 0, 19, 0),
    ("Headliner Two", "Hauptbühne", 19, 0, 21, 0),
]


def build_items(day: date) -> list[ProgramItem]:
    return [
        ProgramItem(
            title=title,
            stage=stage,
            starts_at=datetime(day.year, day.month, day.day, sh, sm),
            ends_at=datetime(day.year, day.month, day.day, eh, em),
        )
        for title, stage, sh, sm, eh, em in SLOTS
    ]


def seed() -> None:
    init_db()
    day = festival_now().date()
    items = build_items(day)

    db = SessionLocal()
    try:
        db.query(ProgramItem).delete()
        db.add_all(items)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()

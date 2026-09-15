"""API tests: sorting, stage filter, stage list, status field."""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, ProgramItem, get_db
from app.main import app

# In-memory SQLite only exists per connection - StaticPool makes every
# session share the same connection, so all sessions see the same data.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_festival_now():
    return datetime(2026, 9, 11, 14, 0)


app.dependency_overrides[get_db] = override_get_db
from app.schedule import festival_now  # noqa: E402

app.dependency_overrides[festival_now] = override_festival_now

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    db.add_all(
        [
            ProgramItem(
                title="Rock Rebels",
                stage="Hauptbühne",
                starts_at=datetime(2026, 9, 11, 13, 0),
                ends_at=datetime(2026, 9, 11, 14, 30),
            ),
            ProgramItem(
                title="Folk Trio",
                stage="Waldbühne",
                starts_at=datetime(2026, 9, 11, 12, 0),
                ends_at=datetime(2026, 9, 11, 13, 0),
            ),
            ProgramItem(
                title="DJ Sunrise",
                stage="Zeltbühne",
                starts_at=datetime(2026, 9, 11, 12, 0),
                ends_at=datetime(2026, 9, 11, 13, 0),
            ),
            ProgramItem(
                title="Headliner",
                stage="Hauptbühne",
                starts_at=datetime(2026, 9, 11, 16, 0),
                ends_at=datetime(2026, 9, 11, 18, 0),
            ),
        ]
    )
    db.commit()
    db.close()
    yield


def test_program_is_sorted_by_start_then_stage():
    response = client.get("/api/program")
    titles = [item["title"] for item in response.json()["items"]]
    assert titles == ["Folk Trio", "DJ Sunrise", "Rock Rebels", "Headliner"]


def test_program_includes_status_and_now():
    response = client.get("/api/program")
    body = response.json()
    assert body["now"] == "2026-09-11T14:00:00"
    statuses = {item["title"]: item["status"] for item in body["items"]}
    assert statuses["Rock Rebels"] == "now"
    assert statuses["Headliner"] == "next"
    assert statuses["Folk Trio"] is None
    assert statuses["DJ Sunrise"] is None


def test_program_filtered_by_stage():
    response = client.get("/api/program", params={"stage": "Hauptbühne"})
    titles = [item["title"] for item in response.json()["items"]]
    assert titles == ["Rock Rebels", "Headliner"]


def test_program_filtered_by_unknown_stage_returns_empty_list():
    response = client.get("/api/program", params={"stage": "Nirgendwo"})
    assert response.json()["items"] == []


def test_stages_are_sorted_alphabetically():
    response = client.get("/api/stages")
    assert response.json() == ["Hauptbühne", "Waldbühne", "Zeltbühne"]


def test_root_serves_index_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_program_and_stages_with_empty_database():
    db = TestSessionLocal()
    db.query(ProgramItem).delete()
    db.commit()
    db.close()

    program_response = client.get("/api/program")
    assert program_response.status_code == 200
    assert program_response.json()["items"] == []

    stages_response = client.get("/api/stages")
    assert stages_response.status_code == 200
    assert stages_response.json() == []

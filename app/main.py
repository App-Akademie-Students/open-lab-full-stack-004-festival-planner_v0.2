"""FastAPI app: API endpoints and delivery of the frontend."""
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import ProgramItem, get_db, init_db
from app.schedule import compute_statuses, festival_now


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


class ProgramItemOut(BaseModel):
    id: int
    title: str
    stage: str
    starts_at: datetime
    ends_at: datetime
    status: str | None


class ProgramResponse(BaseModel):
    now: datetime
    items: list[ProgramItemOut]


@app.get("/api/stages")
def get_stages(db: Session = Depends(get_db)) -> list[str]:
    rows = db.query(ProgramItem.stage).distinct().order_by(ProgramItem.stage).all()
    return [row[0] for row in rows]


@app.get("/api/program", response_model=ProgramResponse)
def get_program(
    stage: str | None = None,
    db: Session = Depends(get_db),
    now: datetime = Depends(festival_now),
) -> ProgramResponse:
    query = db.query(ProgramItem).order_by(ProgramItem.starts_at, ProgramItem.stage)
    if stage is not None:
        query = query.filter(ProgramItem.stage == stage)
    items = query.all()

    statuses = compute_statuses(items, now)
    out_items = [
        ProgramItemOut(
            id=item.id,
            title=item.title,
            stage=item.stage,
            starts_at=item.starts_at,
            ends_at=item.ends_at,
            status=status,
        )
        for item, status in zip(items, statuses)
    ]
    return ProgramResponse(now=now, items=out_items)


app.mount("/", StaticFiles(directory="static", html=True), name="static")

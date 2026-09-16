"""Database queries: stage list and program list (joins over Artist/Stage).

Program rows come back already flattened to `title`/`stage` - the API
contract stays flat (see architecture.md, T-4), so callers don't need to
know about `Artist`/`Stage` at all.
"""
from sqlalchemy.orm import Session

from app.models import Act, Artist, Stage



def list_stages(db: Session) -> list[str]:
    """Alphabetically sorted stage names, for the filter dropdown."""
    rows = db.query(Stage.name).order_by(Stage.name).all()
    return [row[0] for row in rows]


def list_program(db: Session, stage: str | None = None):
    """Acts chronologically sorted, joined to Artist/Stage, optionally filtered by stage.

    Returns rows with `.id`, `.title`, `.stage`, `.starts_at`, `.ends_at`.
    """
    query = (
        db.query(
            Act.id,
            Artist.name.label("title"),
            Stage.name.label("stage"),
            Act.starts_at,
            Act.ends_at,
        )
        .join(Artist)
        .join(Stage)
        .order_by(Act.starts_at, Stage.name)
    )
    if stage is not None:
        query = query.filter(Stage.name == stage)
    return query.all()

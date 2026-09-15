"""Database setup: engine, session factory, ProgramItem model."""
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./festival.db"

# check_same_thread=False: FastAPI runs sync endpoints in a threadpool,
# but SQLite otherwise binds a connection to a single thread.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ProgramItem(Base):
    __tablename__ = "program_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    stage = Column(String, nullable=False)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def get_db_path() -> Path:
    """Return the path to the SQLite database file."""
    data_dir = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    db_dir = data_dir / "active-pauses"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "active_pauses.db"


def get_engine(db_url: str | None = None) -> Engine:
    """Create and return a SQLAlchemy engine."""
    if db_url is None:
        db_url = f"sqlite:///{get_db_path()}"
    return create_engine(db_url, connect_args={"check_same_thread": False})


def get_session_factory(engine: Engine | None = None) -> sessionmaker[Session]:
    """Return a session factory bound to the given engine."""
    if engine is None:
        engine = get_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)

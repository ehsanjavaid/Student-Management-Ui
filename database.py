from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

try:
    from .config import get_database_path
except ImportError:  # Running as a script without package context
    from config import get_database_path


class Base(DeclarativeBase):
    pass


def _sqlite_url(db_path: Path) -> str:
    return f"sqlite:///{db_path.as_posix()}"


engine = create_engine(
    _sqlite_url(get_database_path()),
    echo=False,
    future=True,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_database() -> None:
    # Import models to register them with the Base metadata
    try:
        from . import models  # noqa: F401
    except ImportError:  # Running as a script without package context
        import models  # noqa: F401

    Base.metadata.create_all(bind=engine)



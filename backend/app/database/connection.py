"""
SQLite connection management.

This module owns exactly one responsibility: knowing where the application
database file lives on disk and handing out connections to it. Nothing in
this file should contain business/query logic - that lives in
``repository.py``. Centralizing this avoids the previous situation where
three different modules (`db.py`, `db_new.py`, `simple_db.py`) each computed
their own path and opened their own connections independently.
"""

import os
import sqlite3
from pathlib import Path

from app.core.config import settings

_DEFAULT_DB_PATH: Path = Path(__file__).resolve().parents[2] / "data" / "energy_management.db"

_DB_PATH_FROM_ENV = os.getenv("DATABASE_PATH", "").strip()
DB_PATH: Path = (
    Path(_DB_PATH_FROM_ENV)
    if _DB_PATH_FROM_ENV
    else Path(settings.database_path)
    if settings.database_path
    else _DEFAULT_DB_PATH
)


def get_connection() -> sqlite3.Connection:
    """Open a new SQLite connection to the application database.

    A fresh connection is returned on every call rather than sharing one
    globally, since ``sqlite3`` connections are not safe to share across
    threads/async tasks. Callers should use the connection as a context
    manager (``with get_connection() as conn:``) so it is committed and
    closed deterministically.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

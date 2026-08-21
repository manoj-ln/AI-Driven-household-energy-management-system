"""
Standalone entry point to initialize (or verify) the application database.

Useful for first-time setup, deployment scripts, and CI, without having to
boot the whole FastAPI app first (importing `app.database.repository`
already initializes the schema as a side effect, but this gives an explicit,
scriptable way to do it and to confirm where the DB file ended up).

Run directly:
    cd backend
    python -m app.database.init_db
"""

from app.database.connection import DB_PATH, get_connection
from app.database.schema import create_schema


def init_db() -> None:
    with get_connection() as conn:
        create_schema(conn)
    print(f"Database ready at: {DB_PATH}")


if __name__ == "__main__":
    init_db()

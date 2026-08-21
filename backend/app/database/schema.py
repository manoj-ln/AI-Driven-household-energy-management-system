"""
Schema definitions (DDL) for the SQLite datastore.

Kept separate from both the connection factory (``connection.py``) and the
query/repository layer (``repository.py``) so the table shapes are visible
at a glance without wading through query methods. This is a straight
extraction of the ``CREATE TABLE IF NOT EXISTS`` statements that previously
lived inline inside ``Database._init_db`` - table definitions are unchanged.
"""

import sqlite3

ENERGY_READINGS_TABLE = """
    CREATE TABLE IF NOT EXISTS energy_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        device_id TEXT NOT NULL,
        device_type TEXT NOT NULL,
        voltage REAL,
        current REAL,
        power REAL,
        energy_consumption REAL,
        temperature REAL,
        humidity REAL,
        is_anomaly BOOLEAN DEFAULT 0,
        prediction REAL
    )
"""

DEVICES_TABLE = """
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT UNIQUE NOT NULL,
        device_type TEXT NOT NULL,
        name TEXT NOT NULL,
        location TEXT,
        is_active BOOLEAN DEFAULT 1,
        last_seen TEXT,
        ip_address TEXT,
        rated_power_w REAL DEFAULT 100.0,
        standby_power_w REAL DEFAULT 0.0,
        priority INTEGER DEFAULT 3,
        efficiency REAL DEFAULT 1.0,
        operating_state TEXT DEFAULT 'on'
    )
"""

DEVICE_STATE_EVENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS device_state_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT NOT NULL,
        device_name TEXT NOT NULL,
        state TEXT NOT NULL CHECK (state IN ('on', 'off', 'standby')),
        changed_at TEXT NOT NULL,
        source TEXT NOT NULL DEFAULT 'software'
    )
"""

CHATBOT_MESSAGES_TABLE = """
    CREATE TABLE IF NOT EXISTS chatbot_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        intent TEXT,
        created_at TEXT NOT NULL
    )
"""

USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identifier TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        age TEXT,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TEXT NOT NULL,
        updated_at TEXT
    )
"""

FAQ_TABLE = """
    CREATE TABLE IF NOT EXISTS faq (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keywords TEXT NOT NULL,
        answer TEXT NOT NULL
    )
"""

APPLIANCE_CATALOG_TABLE = """
    CREATE TABLE IF NOT EXISTS appliance_catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        rated_power TEXT,
        status TEXT,
        description TEXT,
        smart_features TEXT
    )
"""

# Indexes matter here: get_recent_readings/get_readings_by_date_range filter
# and sort by (device_id, timestamp) on every call, and the table can grow to
# hundreds of thousands of rows once real ingestion runs for a while.
INDEXES = (
    "CREATE INDEX IF NOT EXISTS idx_energy_readings_timestamp ON energy_readings(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_energy_readings_device_id ON energy_readings(device_id)",
    "CREATE INDEX IF NOT EXISTS idx_energy_readings_device_ts ON energy_readings(device_id, timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_chatbot_messages_session_id ON chatbot_messages(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_users_identifier ON users(identifier)",
)


def create_schema(conn: sqlite3.Connection) -> None:
    """Create all application tables/indexes if they do not already exist."""
    cursor = conn.cursor()
    cursor.execute(ENERGY_READINGS_TABLE)
    cursor.execute(DEVICES_TABLE)
    cursor.execute(DEVICE_STATE_EVENTS_TABLE)
    cursor.execute(CHATBOT_MESSAGES_TABLE)
    cursor.execute(USERS_TABLE)
    cursor.execute(FAQ_TABLE)
    cursor.execute(APPLIANCE_CATALOG_TABLE)
    existing_columns = {row[1] for row in cursor.execute("PRAGMA table_info(devices)").fetchall()}
    migrations = {
        "rated_power_w": "REAL DEFAULT 100.0",
        "standby_power_w": "REAL DEFAULT 0.0",
        "priority": "INTEGER DEFAULT 3",
        "efficiency": "REAL DEFAULT 1.0",
        "operating_state": "TEXT DEFAULT 'on'",
    }
    for column, definition in migrations.items():
        if column not in existing_columns:
            cursor.execute(f"ALTER TABLE devices ADD COLUMN {column} {definition}")
    for statement in INDEXES:
        cursor.execute(statement)
    conn.commit()

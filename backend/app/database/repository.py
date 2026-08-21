"""
Energy datastore repository.

This is the single, consolidated data-access implementation for the
application. It replaces three previously coexisting implementations:

- ``db.py``        - the complete, actually-used SQLite implementation
                      (five services imported this one).
- ``db_new.py``     - an unused duplicate of ``db.py`` with a real bug
                      (``get_energy_stats`` used
                      ``end_date.replace(hour=end_date.hour - hours)``,
                      which raises ``ValueError`` for ``hours`` greater than
                      the current hour - never caught because nothing
                      imported this module).
- ``simple_db.py``  - an unused JSON-file mock with hardcoded fake devices.

Every method below is behavior-identical to the working ``db.py`` version;
only *where* the code lives has changed (connection handling moved to
``connection.py``, table DDL moved to ``schema.py``). No method signature,
return shape, or query result has changed, so callers do not need to change
anything beyond their import line.
"""

import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.database.connection import get_connection
from app.database.schema import create_schema


class EnergyRepository:
    """Read/write access to energy readings, devices, and chat history."""

    def __init__(self) -> None:
        with get_connection() as conn:
            create_schema(conn)

    # -- energy readings ---------------------------------------------------

    def insert_reading(self, record: dict) -> None:
        """Insert a new energy reading."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO energy_readings
                (timestamp, device_id, device_type, voltage, current, power,
                 energy_consumption, temperature, humidity, is_anomaly, prediction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.get("timestamp", datetime.now(timezone.utc).isoformat()),
                    record["device_id"],
                    record["device_type"],
                    record.get("voltage"),
                    record.get("current"),
                    record.get("power"),
                    record.get("energy_consumption"),
                    record.get("temperature"),
                    record.get("humidity"),
                    record.get("is_anomaly", False),
                    record.get("prediction"),
                ),
            )
            conn.commit()

    def get_recent_readings(self, limit: int = 24, device_id: str = None) -> List[Dict[str, Any]]:
        """Get the most recent energy readings, oldest first."""
        with get_connection() as conn:
            cursor = conn.cursor()
            if device_id:
                cursor.execute(
                    """
                    SELECT * FROM energy_readings
                    WHERE device_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (device_id, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM energy_readings
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
            rows = cursor.fetchall()
            return [self._row_to_dict(row, cursor) for row in reversed(rows)]

    def get_readings_by_date_range(
        self, start_date: datetime, end_date: datetime, device_id: str = None
    ) -> List[Dict[str, Any]]:
        """Get readings within an inclusive date range, ascending by time."""
        with get_connection() as conn:
            cursor = conn.cursor()
            start_str = start_date.isoformat()
            end_str = end_date.isoformat()
            if device_id:
                cursor.execute(
                    """
                    SELECT * FROM energy_readings
                    WHERE timestamp >= ? AND timestamp <= ? AND device_id = ?
                    ORDER BY timestamp
                    """,
                    (start_str, end_str, device_id),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM energy_readings
                    WHERE timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp
                    """,
                    (start_str, end_str),
                )
            rows = cursor.fetchall()
            return [self._row_to_dict(row, cursor) for row in rows]

    def get_energy_stats(self, device_id: str = None, hours: int = 24) -> dict:
        """Aggregate stats (total/avg/max/min) over the trailing window."""
        with get_connection() as conn:
            cursor = conn.cursor()
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(hours=hours)
            start_str = start_date.isoformat()
            end_str = end_date.isoformat()

            if device_id:
                cursor.execute(
                    """
                    SELECT COUNT(*), SUM(energy_consumption), AVG(power), MAX(power), MIN(power)
                    FROM energy_readings
                    WHERE timestamp >= ? AND timestamp <= ? AND device_id = ?
                    """,
                    (start_str, end_str, device_id),
                )
            else:
                cursor.execute(
                    """
                    SELECT COUNT(*), SUM(energy_consumption), AVG(power), MAX(power), MIN(power)
                    FROM energy_readings
                    WHERE timestamp >= ? AND timestamp <= ?
                    """,
                    (start_str, end_str),
                )
            row = cursor.fetchone()
            if row and row[0] > 0:
                return {
                    "total_energy": row[1] or 0,
                    "avg_power": row[2] or 0,
                    "max_power": row[3] or 0,
                    "min_power": row[4] or 0,
                    "count": row[0],
                }
            return {"total_energy": 0, "avg_power": 0, "max_power": 0, "min_power": 0, "count": 0}

    # -- devices -------------------------------------------------------------

    def get_devices(self) -> List[Dict[str, Any]]:
        """Get all registered devices."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices")
            rows = cursor.fetchall()
            return [self._device_row_to_dict(row, cursor) for row in rows]

    def register_device(self, device_data: Dict[str, Any]) -> None:
        """Register a new device (upsert by device_id)."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO devices
                (device_id, device_type, name, location, is_active, last_seen, ip_address,
                 rated_power_w, standby_power_w, priority, efficiency, operating_state)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    device_data["device_id"],
                    device_data["device_type"],
                    device_data["name"],
                    device_data.get("location"),
                    device_data.get("is_active", True),
                    device_data.get("last_seen", datetime.now(timezone.utc).isoformat()),
                    device_data.get("ip_address"),
                    device_data.get("rated_power_w", 100.0),
                    device_data.get("standby_power_w", 0.0),
                    device_data.get("priority", 3),
                    device_data.get("efficiency", 1.0),
                    device_data.get("operating_state", "on"),
                ),
            )
            conn.commit()

    def update_device_metadata(self, device_id: str, device_data: Dict[str, Any]) -> None:
        with get_connection() as conn:
            conn.execute(
                """
                UPDATE devices
                SET rated_power_w = ?, standby_power_w = ?, priority = ?,
                    efficiency = ?, operating_state = ?
                WHERE device_id = ?
                """,
                (
                    device_data.get("rated_power_w", 100.0),
                    device_data.get("standby_power_w", 0.0),
                    device_data.get("priority", 3),
                    device_data.get("efficiency", 1.0),
                    device_data.get("operating_state", "on"),
                    device_id,
                ),
            )
            conn.commit()

    def update_device_status(
        self, device_id: str, is_active: bool, last_seen: Optional[datetime] = None
    ) -> None:
        """Update device online/offline status."""
        with get_connection() as conn:
            cursor = conn.cursor()
            last_seen_str = last_seen.isoformat() if last_seen else datetime.now(timezone.utc).isoformat()
            cursor.execute(
                """
                UPDATE devices
                SET is_active = ?, last_seen = ?
                WHERE device_id = ?
                """,
                (is_active, last_seen_str, device_id),
            )
            conn.commit()

    def record_device_state(
        self,
        device_id: str,
        device_name: str,
        state: str,
        changed_at: Optional[datetime] = None,
        source: str = "software",
    ) -> Dict[str, Any]:
        """Record a device state transition for time-aware energy accounting."""
        timestamp = changed_at or datetime.now(timezone.utc)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO device_state_events
                (device_id, device_name, state, changed_at, source)
                VALUES (?, ?, ?, ?, ?)
                """,
                (device_id, device_name, state, timestamp.isoformat(), source),
            )
            conn.commit()
            return {
                "id": cursor.lastrowid,
                "device_id": device_id,
                "device_name": device_name,
                "state": state,
                "changed_at": timestamp.isoformat(),
                "source": source,
            }

    def get_device_state_events(self, device_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Return the most recent state transitions, oldest first."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, device_id, device_name, state, changed_at, source
                FROM device_state_events
                WHERE device_id = ?
                ORDER BY changed_at DESC
                LIMIT ?
                """,
                (device_id, limit),
            )
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in reversed(cursor.fetchall())]

    def update_device(self, device_id: str, device_data: Dict[str, Any]) -> None:
        """Update editable device fields."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE devices
                SET device_type = ?, name = ?, location = ?, is_active = ?, last_seen = ?
                WHERE device_id = ?
                """,
                (
                    device_data.get("device_type", "appliance"),
                    device_data.get("name", device_id),
                    device_data.get("location"),
                    device_data.get("is_active", True),
                    device_data.get("last_seen", datetime.now(timezone.utc).isoformat()),
                    device_id,
                ),
            )
            conn.commit()

    def delete_device(self, device_id: str) -> None:
        """Delete a registered device and its associated readings."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM devices WHERE device_id = ?", (device_id,))
            cursor.execute("DELETE FROM energy_readings WHERE device_id = ?", (device_id,))
            conn.commit()

    # -- chatbot history -----------------------------------------------------

    def save_chat_message(
        self, session_id: str, role: str, message: str, intent: Optional[str] = None
    ) -> None:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO chatbot_messages (session_id, role, message, intent, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, role, message, intent, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()

    def get_chat_history(self, session_id: str, limit: int = 12) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT session_id, role, message, intent, created_at
                FROM chatbot_messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, max(1, int(limit))),
            )
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in reversed(rows)]

    # -- user operations -------------------------------------------------

    def create_user(self, identifier: str, name: str, age: str, password_hash: str, role: str = "user") -> dict:
        """Create a new user. Returns the user dict or raises on duplicate."""
        with get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute(
                """
                INSERT INTO users (identifier, name, age, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (identifier, name, age, password_hash, role, now),
            )
            conn.commit()
            return {
                "identifier": identifier,
                "name": name,
                "age": age,
                "role": role,
                "created_at": now,
            }

    def get_user_by_identifier(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Get a user by their identifier (email/phone)."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE identifier = ?",
                (identifier,),
            )
            row = cursor.fetchone()
            if row:
                return self._user_row_to_dict(row, cursor)
            return None

    def update_user_profile(self, identifier: str, name: str, age: str) -> Optional[Dict[str, Any]]:
        """Update user name and age. Returns updated user or None."""
        with get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute(
                """
                UPDATE users SET name = ?, age = ?, updated_at = ?
                WHERE identifier = ?
                """,
                (name, age, now, identifier),
            )
            conn.commit()
            if cursor.rowcount > 0:
                return self.get_user_by_identifier(identifier)
            return None

    # -- FAQ ---------------------------------------------------------------

    def save_faq(self, keywords: List[str], answer: str) -> None:
        """Insert a single FAQ row (keywords stored as JSON array)."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO faq (keywords, answer) VALUES (?, ?)",
                (json.dumps(keywords), answer),
            )
            conn.commit()

    def bulk_sync_faq(self, faq_list: List[tuple]) -> None:
        """Replace all FAQ rows with the provided list of (keywords, answer)."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM faq")
            cursor.executemany(
                "INSERT INTO faq (keywords, answer) VALUES (?, ?)",
                [(json.dumps(kw), ans) for kw, ans in faq_list],
            )
            conn.commit()

    def count_faqs(self) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM faq")
            return cursor.fetchone()[0]

    def query_faq(self, message: str) -> Optional[str]:
        """Return the best FAQ answer for a message, or None."""
        msg = message.lower().strip()
        words = [w for w in re.split(r"\W+", msg) if len(w) > 3]
        if not words:
            words = [w for w in re.split(r"\W+", msg) if w]

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT keywords, answer FROM faq")
            rows = cursor.fetchall()

            cursor.execute("SELECT answer FROM faq WHERE keywords LIKE ?", (f"%{msg}%",))
            row = cursor.fetchone()
            if row:
                return row["answer"]

            best_answer = None
            max_overlap = 0
            for r in rows:
                kws = [k.lower() for k in json.loads(r["keywords"])]
                overlap = 0
                for w in words:
                    if any(w in k or k in w for k in kws):
                        overlap += 1
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_answer = r["answer"]

            return best_answer if max_overlap >= 1 else None

    def get_all_appliances(self) -> List[Dict[str, Any]]:
        """Return all appliance catalog entries (same shape as DatabaseService.get_all_devices)."""
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM appliance_catalog")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def bulk_sync_appliances(self, appliances: List[Dict[str, Any]]) -> None:
        """Replace all appliance catalog rows."""
        import json as _json

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM appliance_catalog")
            cursor.executemany(
                "INSERT INTO appliance_catalog (name, category, rated_power, status, description, smart_features) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (
                        a["name"],
                        a.get("category"),
                        a.get("ratedPower"),
                        a.get("status"),
                        a.get("description"),
                        _json.dumps(a.get("smartFeatures", [])),
                    )
                    for a in appliances
                ],
            )
            conn.commit()

    # -- helpers ---------------------------------------------------------

    @staticmethod
    def _row_to_dict(row, cursor) -> Dict[str, Any]:
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))

    @staticmethod
    def _device_row_to_dict(row, cursor) -> Dict[str, Any]:
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))

    @staticmethod
    def _user_row_to_dict(row, cursor) -> Dict[str, Any]:
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))


# Module-level singleton, kept for drop-in compatibility with existing
# `from app.database.db import db` call sites (now `from app.database.repository import db`).
db = EnergyRepository()

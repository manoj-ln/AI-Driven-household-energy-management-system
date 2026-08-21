"""
Knowledge-base service (FAQ + appliance catalog).

Originally this module owned a second SQLite database file
(``household_energy.db``) with its own ``devices`` table that had a different
schema from ``repository.py``'s ``devices`` table.  The chatbot was the only
consumer.  This consolidation makes ``DatabaseService`` use the same shared
database (``energy_management.db``) via the centralised connection factory and
the new ``faq`` / ``appliance_catalog`` tables defined in ``schema.py``.

All public methods are preserved — callers (``chatbot.py``, tests, startup
hook in ``main.py``) need zero changes.
"""

import json
import re
from pathlib import Path

from app.core.config import settings
from app.database.connection import DB_PATH, get_connection
from app.database.schema import create_schema
from app.database.repository import db as _repository_db
from app.utils.logger import logger


class DatabaseService:
    DB_PATH = DB_PATH
    _initialized = False

    @classmethod
    def ensure_db(cls):
        if not cls._initialized:
            cls.init_db()
            cls._initialized = True

    @classmethod
    def init_db(cls):
        with get_connection() as conn:
            create_schema(conn)

    @classmethod
    def get_connection(cls):
        cls.ensure_db()
        return get_connection()

    @classmethod
    def sync_devices(cls, devices_list):
        _repository_db.bulk_sync_appliances(devices_list)

    @classmethod
    def get_all_devices(cls):
        return _repository_db.get_all_appliances()

    @classmethod
    def get_device_by_name(cls, name):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM appliance_catalog WHERE name LIKE ?", (f"%{name}%",))
            row = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row)) if row else None

    @classmethod
    def sync_faq(cls, faq_list):
        _repository_db.bulk_sync_faq(faq_list)

    @classmethod
    def faq_count(cls):
        return _repository_db.count_faqs()

    @classmethod
    def ensure_knowledge_base(cls):
        """Load FAQ and device catalog into SQLite when empty."""
        cls.ensure_db()
        if cls.faq_count() == 0:
            from app.services.chatbot_faq import FAQ_DB
            from app.services.project_knowledge import PROJECT_FAQ
            cls.sync_faq(FAQ_DB + PROJECT_FAQ)

        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM appliance_catalog")
        device_count = cursor.fetchone()[0]
        conn.close()

        if device_count == 0:
            from app.services.dataset_service import DatasetService
            catalog = DatasetService.get_catalog()
            payload = []
            for idx, device in enumerate(catalog.get("devices", []), start=1):
                payload.append({
                    "id": idx,
                    "name": device.get("name", f"Device {idx}"),
                    "category": device.get("category", "General"),
                    "ratedPower": device.get("power", "150W"),
                    "status": "active",
                    "description": device.get(
                        "description",
                        f"Monitored {device.get('name', 'device')} in the active household energy system.",
                    ),
                    "smartFeatures": ["AI Tracking", "Anomaly Detection", "Off-Peak Scheduling"],
                })
            if payload:
                cls.sync_devices(payload)

    @classmethod
    def query_faq(cls, message):
        return _repository_db.query_faq(message)


if __name__ == "__main__":
    DatabaseService.init_db()
    logger.info("Database initialized at %s", DB_PATH)

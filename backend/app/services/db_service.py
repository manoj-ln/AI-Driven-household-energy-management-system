import sqlite3
import json
import re
from pathlib import Path

class DatabaseService:
    DB_PATH = Path(__file__).resolve().parents[2] / "data" / "household_energy.db"
    _initialized = False

    @classmethod
    def ensure_db(cls):
        if not cls._initialized:
            cls.init_db()
            cls._initialized = True

    @classmethod
    def init_db(cls):
        cls.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(cls.DB_PATH)
        cursor = conn.cursor()
        
        # Create Devices Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                rated_power TEXT,
                status TEXT,
                description TEXT,
                smart_features TEXT
            )
        ''')
        
        # Create FAQ Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faq (
                id INTEGER PRIMARY KEY,
                keywords TEXT,
                answer TEXT
            )
        ''')
        
        # Create Energy Meta Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    @classmethod
    def get_connection(cls):
        cls.ensure_db()
        return sqlite3.connect(cls.DB_PATH)

    @classmethod
    def sync_devices(cls, devices_list):
        conn = cls.get_connection()
        cursor = conn.cursor()
        for d in devices_list:
            cursor.execute('''
                INSERT OR REPLACE INTO devices (id, name, category, rated_power, status, description, smart_features)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (d['id'], d['name'], d['category'], d['ratedPower'], d['status'], d['description'], json.dumps(d.get('smartFeatures', []))))
        conn.commit()
        conn.close()

    @classmethod
    def get_all_devices(cls):
        conn = cls.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @classmethod
    def get_device_by_name(cls, name):
        conn = cls.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices WHERE name LIKE ?", (f"%{name}%",))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @classmethod
    def sync_faq(cls, faq_list):
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM faq") # Refresh FAQ
        for keywords, answer in faq_list:
            cursor.execute('''
                INSERT INTO faq (keywords, answer)
                VALUES (?, ?)
            ''', (json.dumps(keywords), answer))
        conn.commit()
        conn.close()

    @classmethod
    def faq_count(cls):
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM faq")
        count = cursor.fetchone()[0]
        conn.close()
        return count

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
        cursor.execute("SELECT COUNT(*) FROM devices")
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
        conn = cls.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        msg = message.lower().strip()
        
        # 1. Exact phrase match in keywords
        cursor.execute("SELECT answer FROM faq WHERE keywords LIKE ?", (f"%{msg}%",))
        row = cursor.fetchone()
        if row:
            conn.close()
            return row['answer']
            
        # 2. Advanced Fuzzy Match: Check for significant keyword overlap
        # Split message into words and look for entries that contain most words
        words = [w for w in re.split(r'\W+', msg) if len(w) > 3]
        if not words:
            # Fallback for short words
            words = [w for w in re.split(r'\W+', msg) if w]
            
        cursor.execute("SELECT keywords, answer FROM faq")
        rows = cursor.fetchall()
        
        best_answer = None
        max_overlap = 0
        
        for r in rows:
            kws = [k.lower() for k in json.loads(r['keywords'])]
            overlap = 0
            for w in words:
                # Check for exact word or simple typo (start-with or end-with)
                if any(w in k or k in w for k in kws):
                    overlap += 1
            
            if overlap > max_overlap:
                max_overlap = overlap
                best_answer = r['answer']
                
        conn.close()
        # Return if at least some words matched
        if max_overlap >= 1:
            return best_answer
            
        return None

if __name__ == "__main__":
    DatabaseService.init_db()
    print("Database initialized.")

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).resolve().parents[2] / "data" / "energy_management.db"

        self.db_path = str(db_path)
        self._init_db()

    def _init_db(self):
        """Initialize database and create tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create energy_readings table
            cursor.execute('''
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
            ''')

            # Create devices table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT UNIQUE NOT NULL,
                    device_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    location TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    last_seen TEXT,
                    ip_address TEXT
                )
            ''')

            conn.commit()

    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def insert_reading(self, record: dict) -> None:
        """Insert a new energy reading"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO energy_readings
                (timestamp, device_id, device_type, voltage, current, power,
                 energy_consumption, temperature, humidity, is_anomaly, prediction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('timestamp', datetime.utcnow().isoformat()),
                record['device_id'],
                record['device_type'],
                record.get('voltage'),
                record.get('current'),
                record.get('power'),
                record.get('energy_consumption'),
                record.get('temperature'),
                record.get('humidity'),
                record.get('is_anomaly', False),
                record.get('prediction')
            ))

            conn.commit()

    def get_recent_readings(self, limit: int = 24, device_id: str = None) -> List[Dict[str, Any]]:
        """Get recent energy readings"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if device_id:
                cursor.execute('''
                    SELECT * FROM energy_readings
                    WHERE device_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (device_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM energy_readings
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))

            rows = cursor.fetchall()
            return [self._row_to_dict(row, cursor) for row in reversed(rows)]

    def get_readings_by_date_range(self, start_date: datetime, end_date: datetime, device_id: str = None) -> List[Dict[str, Any]]:
        """Get readings within a date range"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            start_str = start_date.isoformat()
            end_str = end_date.isoformat()

            if device_id:
                cursor.execute('''
                    SELECT * FROM energy_readings
                    WHERE timestamp >= ? AND timestamp <= ? AND device_id = ?
                    ORDER BY timestamp
                ''', (start_str, end_str, device_id))
            else:
                cursor.execute('''
                    SELECT * FROM energy_readings
                    WHERE timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp
                ''', (start_str, end_str))

            rows = cursor.fetchall()
            return [self._row_to_dict(row, cursor) for row in rows]

    def get_devices(self) -> List[Dict[str, Any]]:
        """Get all registered devices"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM devices')

            rows = cursor.fetchall()
            return [self._device_row_to_dict(row, cursor) for row in rows]

    def register_device(self, device_data: Dict[str, Any]) -> None:
        """Register a new device"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO devices
                (device_id, device_type, name, location, is_active, last_seen, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                device_data['device_id'],
                device_data['device_type'],
                device_data['name'],
                device_data.get('location'),
                device_data.get('is_active', True),
                device_data.get('last_seen', datetime.utcnow().isoformat()),
                device_data.get('ip_address')
            ))

            conn.commit()

    def update_device_status(self, device_id: str, is_active: bool, last_seen: Optional[datetime] = None) -> None:
        """Update device status"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            last_seen_str = last_seen.isoformat() if last_seen else datetime.utcnow().isoformat()

            cursor.execute('''
                UPDATE devices
                SET is_active = ?, last_seen = ?
                WHERE device_id = ?
            ''', (is_active, last_seen_str, device_id))

            conn.commit()

    def get_energy_stats(self, device_id: str = None, hours: int = 24) -> dict:
        """Get energy statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            end_date = datetime.utcnow()
            start_date = end_date.replace(hour=end_date.hour - hours)

            start_str = start_date.isoformat()
            end_str = end_date.isoformat()

            if device_id:
                cursor.execute('''
                    SELECT COUNT(*), SUM(energy_consumption), AVG(power), MAX(power), MIN(power)
                    FROM energy_readings
                    WHERE timestamp >= ? AND timestamp <= ? AND device_id = ?
                ''', (start_str, end_str, device_id))
            else:
                cursor.execute('''
                    SELECT COUNT(*), SUM(energy_consumption), AVG(power), MAX(power), MIN(power)
                    FROM energy_readings
                    WHERE timestamp >= ? AND timestamp <= ?
                ''', (start_str, end_str))

            row = cursor.fetchone()

            if row and row[0] > 0:
                return {
                    "total_energy": row[1] or 0,
                    "avg_power": row[2] or 0,
                    "max_power": row[3] or 0,
                    "min_power": row[4] or 0,
                    "count": row[0]
                }
            else:
                return {"total_energy": 0, "avg_power": 0, "max_power": 0, "min_power": 0, "count": 0}

    def _row_to_dict(self, row, cursor) -> Dict[str, Any]:
        """Convert database row to dictionary"""
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))

    def _device_row_to_dict(self, row, cursor) -> Dict[str, Any]:
        """Convert device row to dictionary"""
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))

# Global database instance
db = Database()
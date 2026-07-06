
import sys
import os
sys.path.append(r'c:\myproject\backend')
from app.services.db_service import DatabaseService

try:
    devices = DatabaseService.get_all_devices()
    print(f"Total devices in DB: {len(devices)}")
    for d in devices[:2]:
        print(f" - {d['name']}")
except Exception as e:
    print(f"Error: {e}")

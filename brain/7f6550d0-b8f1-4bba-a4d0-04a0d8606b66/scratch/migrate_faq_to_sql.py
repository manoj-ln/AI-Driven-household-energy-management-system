
import sys
import os
sys.path.append(r'c:\myproject\backend')
from app.services.db_service import DatabaseService
from app.services.chatbot_faq import FAQ_DB

def migrate():
    print("Initializing DB...")
    DatabaseService.init_db()
    print(f"Syncing {len(FAQ_DB)} FAQ entries to SQLite...")
    DatabaseService.sync_faq(FAQ_DB)
    print("Migration complete.")

if __name__ == "__main__":
    migrate()

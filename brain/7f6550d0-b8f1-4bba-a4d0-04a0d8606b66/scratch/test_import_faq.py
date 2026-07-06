
import sys
sys.path.append(r'c:\myproject\backend')
try:
    from app.services.chatbot_faq import FAQ_DB
    print(f"Imported FAQ_DB with {len(FAQ_DB)} entries.")
except Exception as e:
    print(f"Error importing FAQ_DB: {e}")

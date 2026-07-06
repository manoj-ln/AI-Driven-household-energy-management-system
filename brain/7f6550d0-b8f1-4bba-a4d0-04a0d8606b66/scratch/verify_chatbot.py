
import sys
from pathlib import Path

# Add backend to path
sys.path.append(r'c:\myproject\backend')

from app.services.chatbot import help_bot

def test_bot():
    queries = [
        "hi",
        "how much did i get monthely bill",
        "live weather report"
    ]
    
    print("--- STARTING CHATBOT VERIFICATION ---\n")
    
    for q in queries:
        print(f"User: {q}")
        try:
            response = help_bot.generate_response(q, session_id="test-session")
            print(f"Bot [Intent: {response['intent']}]:")
            print(f"{response['response']}")
            print("-" * 30)
        except Exception as e:
            print(f"CRITICAL ERROR for query '{q}': {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_bot()


import sys
import os
import shutil

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.database import Database
from src.core.session_manager import SessionManager

DB_PATH = "test_fix.db"

def test_missing_components():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    print("Initialize Database...")
    db = Database(DB_PATH)
    sm = SessionManager(DB_PATH)
    
    # Create User
    username = "test_user"
    sm.db.create_user(username, "password123")
    sm.set_user(username)
    
    print("\n--- Testing Vitals ---")
    sm.save_vital("heart_rate", "80", "bpm")
    sm.save_vital("blood_pressure", "120/80", "mmHg")
    
    vitals = sm.get_recent_vitals(limit=5)
    print(f"Vitals Count: {len(vitals)}")
    assert len(vitals) == 2, "Should have 2 vitals"
    print("✅ Vitals OK")
    
    print("\n--- Testing Symptoms ---")
    sm.save_symptom("SYM001", "High", "2 days")
    sm.save_symptom("SYM001", "Medium", "1 day") # Trend check
    
    symptoms = sm.get_recent_symptoms(limit=5)
    print(f"Symptoms Count: {len(symptoms)}")
    assert len(symptoms) == 2, "Should have 2 symptoms"
    
    trends = sm.get_symptom_trends(days=7)
    print(f"Trends: {trends}")
    assert "SYM001" in trends, "Should have trends for SYM001"
    assert trends["SYM001"]["count"] == 2, "Should have count 2"
    print("✅ Symptoms OK")
    
    # Cleanup
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except:
             pass
    print("\n🎉 ALL TESTS PASSED")

if __name__ == "__main__":
    test_missing_components()

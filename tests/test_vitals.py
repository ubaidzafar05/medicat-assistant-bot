import os
import sys
import unittest

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.database import Database
from src.core.session_manager import SessionManager

class TestVitals(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_vitals.db"
        self.db = Database(self.test_db_path)
        self.sm = SessionManager(self.test_db_path)

    def tearDown(self):
        self.db.get_connection().close()
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except PermissionError:
                pass

    def test_add_get_vital(self):
        # 1. Add Vital
        self.sm.save_vital("Blood Pressure", "120/80", "mmHg")
        
        # 2. Get Vital
        vitals = self.sm.get_recent_vitals("Blood Pressure")
        self.assertEqual(len(vitals), 1)
        self.assertEqual(vitals[0]['value'], "120/80")
        self.assertEqual(vitals[0]['unit'], "mmHg")

    def test_get_recent_limit(self):
        self.sm.save_vital("Heart Rate", "80", "bpm")
        self.sm.save_vital("Heart Rate", "85", "bpm")
        self.sm.save_vital("Heart Rate", "90", "bpm")
        
        vitals = self.sm.get_recent_vitals("Heart Rate", limit=2)
        self.assertEqual(len(vitals), 2)
        # Check ordering (most recent first)
        self.assertEqual(vitals[0]['value'], "90")
        self.assertEqual(vitals[1]['value'], "85")

if __name__ == '__main__':
    unittest.main()

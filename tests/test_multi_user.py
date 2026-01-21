import os
import sys
import unittest

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.database import Database
from src.core.session_manager import SessionManager

class TestMultiUser(unittest.TestCase):
    def setUp(self):
        import uuid
        self.test_db_path = f"test_multi_user_{uuid.uuid4().hex}.db"
        self.sm = SessionManager(self.test_db_path)

    def tearDown(self):
        # Close all connections before deleting
        if hasattr(self, 'db'):
            self.db.get_connection().close()
        if hasattr(self, 'sm') and hasattr(self.sm, 'db'):
            self.sm.db.get_connection().close()
            
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except PermissionError:
                pass

    def test_user_isolation(self):
        # 1. Setup User 1
        self.sm.set_user("user1")
        self.sm.add_message("user", "Hello, I am user 1")
        
        # 2. Setup User 2
        self.sm.set_user("user2")
        self.sm.add_message("user", "Hello, I am user 2")
        
        # 3. Verify Isolation
        self.sm.set_user("user1")
        history1 = self.sm.get_active_history()
        self.assertEqual(len(history1), 1)
        self.assertEqual(history1[0]['content'], "Hello, I am user 1")
        
        self.sm.set_user("user2")
        history2 = self.sm.get_active_history()
        self.assertEqual(len(history2), 1)
        self.assertEqual(history2[0]['content'], "Hello, I am user 2")

    def test_vital_isolation(self):
        # 1. User 1 saves vital
        self.sm.set_user("user1")
        self.sm.save_vital("BP", "120/80", "mmHg")
        
        # 2. User 2 saves vital
        self.sm.set_user("user2")
        self.sm.save_vital("BP", "140/90", "mmHg")
        
        # 3. Check isolation
        self.sm.set_user("user1")
        vitals1 = self.sm.get_recent_vitals("BP")
        self.assertEqual(vitals1[0]['value'], "120/80")
        
        self.sm.set_user("user2")
        vitals2 = self.sm.get_recent_vitals("BP")
        self.assertEqual(vitals2[0]['value'], "140/90")

if __name__ == '__main__':
    unittest.main()

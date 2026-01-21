import os
import shutil
import sys
import unittest

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.database import Database
from src.core.session_manager import SessionManager

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_chatbot.db"
        self.db = Database(self.test_db_path)
        self.sm = SessionManager(self.test_db_path)

    def tearDown(self):
        self.db.get_connection().close()
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except PermissionError:
                pass # Windows file lock potential issue on rapid delete

    def test_session_creation(self):
        session_id = self.db.create_session("user1")
        self.assertIsNotNone(session_id)
        
        sessions = self.db.get_recent_sessions("user1")
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]['id'], session_id)

    def test_message_persistence(self):
        session_id = self.db.create_session("user1")
        self.db.add_message(session_id, "user", "Hello")
        self.db.add_message(session_id, "assistant", "Hi there")
        
        history = self.db.get_history(session_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['content'], "Hello")
        self.assertEqual(history[1]['content'], "Hi there")

    def test_session_manager(self):
        # 1. Start new session
        sid1 = self.sm.start_new_session()
        self.assertIsNotNone(sid1)
        
        # 2. Add messages
        self.sm.add_message("user", "Test 1")
        self.sm.add_message("assistant", "Response 1")
        
        # 3. Verify history
        hist = self.sm.get_active_history()
        self.assertEqual(len(hist), 2)
        
        # 4. Ensure session persistence (simulating app restart)
        sm2 = SessionManager(self.test_db_path)
        sid2 = sm2.ensure_session()
        self.assertEqual(sid2, sid1) # Should recover the previous session
        
        hist2 = sm2.get_active_history()
        self.assertEqual(len(hist2), 2)

    def test_duplicate_user_creation(self):
        """Test that creating a duplicate user returns False instead of crashing."""
        # First creation should succeed
        result1 = self.db.create_user("duplicate_test_user", "password123")
        self.assertTrue(result1)
        
        # Second creation with same username should fail gracefully
        result2 = self.db.create_user("duplicate_test_user", "different_password")
        self.assertFalse(result2)

if __name__ == '__main__':
    unittest.main()

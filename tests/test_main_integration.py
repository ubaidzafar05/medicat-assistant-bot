import os
import sys
import unittest

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Determine paths for cleanup
DB_PATH = "chatbot.db" # Default used by main.py
TEST_DB_PATH = "test_integration.db"

# Hack to inject test DB path into SessionManager before main imports it
# This is tricky because main.py initializes components at module level.
# We will just verify main.py works with the default DB or try to patch it.
# Actually, since main.py initializes 'components' on import, we can patch components['session_manager']
from src.core.session_manager import SessionManager
from src.services.database import Database

# Import main (will print initialization logs)
import main

class TestMainIntegration(unittest.TestCase):
    def setUp(self):
        # Patch the session manager in main.components to use a test DB
        self.test_db = Database(TEST_DB_PATH)
        self.sm = SessionManager(TEST_DB_PATH)
        main.components["session_manager"] = self.sm
        
        # We also need to patch other components if they rely on IO, like LLM?
        # For this test, we might want to mock the LLM or just let it fail/mock the execution.
        # execute_chat_logic calls LLM. 
        # To avoid actual LLM calls, we should mock 'execute_chat_logic' or 'decide_action'.
        
        # Let's mock 'execute_chat_logic' to return a fixed string
        self.original_execute = main.execute_chat_logic
        main.execute_chat_logic = self.mock_execute_chat_logic
        
        # also mock decide_action to be simple
        self.original_decide = main.decide_action
        main.decide_action = lambda u, h: {"action": "CHAT"}

    def tearDown(self):
        main.execute_chat_logic = self.original_execute
        main.decide_action = self.original_decide
        self.test_db.get_connection().close()
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except PermissionError:
                pass

    def mock_execute_chat_logic(self, action, user_input, history, decision, components):
        yield "Mock response"

    def test_chat_logic_persistence(self):
        # 1. Simulate User Message
        gen = main.chat_logic("Hello Bot", [])
        response = "".join(list(gen))
        
        self.assertEqual(response, "Mock response")
        
        # 2. Verify DB has user message
        hist = self.sm.get_active_history()
        self.assertEqual(len(hist), 2)
        self.assertEqual(hist[0]['role'], "user")
        self.assertEqual(hist[0]['content'], "Hello Bot")
        self.assertEqual(hist[1]['role'], "assistant")
        self.assertEqual(hist[1]['content'], "Mock response")

if __name__ == '__main__':
    unittest.main()

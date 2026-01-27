from src.services.database import Database

class SessionManager:
    def __init__(self, db_path="chatbot.db"):
        self.db = Database(db_path)
        self.current_session_id = None
        self.user_id = "admin" # Default user

    def set_user(self, user_id):
        """Switches the active user context and resets the current session ID."""
        if self.user_id != user_id:
            self.user_id = user_id
            self.current_session_id = None # Forces re-selection of session for new user

    def start_new_session(self):
        """Force starts a new session for the current user."""
        self.current_session_id = self.db.create_session(self.user_id)
        return self.current_session_id

    def ensure_session(self):
        """Ensures there is an active session for the current user."""
        if not self.current_session_id:
            # Try to load the most recent session for THIS user
            recent = self.db.get_recent_sessions(self.user_id, limit=1)
            if recent:
                self.current_session_id = recent[0]['id']
            else:
                self.start_new_session()
        return self.current_session_id

    def add_message(self, role, content):
        """Adds a message to the current user's active session."""
        session_id = self.ensure_session()
        self.db.add_message(session_id, role, content)

    def get_active_history(self):
        """Returns the history of the current user's active session."""
        session_id = self.ensure_session() # Re-verify session context
        raw_history = self.db.get_history(session_id)
        return [{"role": msg["role"], "content": msg["content"]} for msg in raw_history]

    def save_vital(self, vital_type, value, unit):
        """Saves a vital sign for the current user."""
        self.db.add_vital(self.user_id, vital_type, value, unit)

    def get_recent_vitals(self, vital_type=None, limit=5):
        """Retrieves recent vitals for the current user."""
        return self.db.get_vitals(self.user_id, vital_type, limit)

    # --- SYMPTOM METHODS ---
    def save_symptom(self, symptom_code, severity, duration=None, metadata=None):
        """Saves a normalized symptom for the current user."""
        self.db.add_symptom(self.user_id, symptom_code, severity, duration, metadata)

    def get_symptom_trends(self, days=30):
        """Gets symptom trend analysis for the current user."""
        return self.db.get_symptom_trends_summary(self.user_id, days)

    def get_recent_symptoms(self, limit=10):
        """Gets recent symptoms for the current user."""
        return self.db.get_recent_symptoms(self.user_id, limit)


    def verify_user(self, username, password):
        """Proxy to database verification."""
        return self.db.verify_user(username, password)

    def get_active_mode(self):
        """Gets the active mode for the current session."""
        session_id = self.ensure_session()
        return self.db.get_active_mode(session_id)

    def set_active_mode(self, mode):
        """Sets the active mode for the current session (e.g., 'MEDICAL', None)."""
        session_id = self.ensure_session()
        self.db.set_active_mode(session_id, mode)
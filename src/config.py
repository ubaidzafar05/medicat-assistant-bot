# ==============================================================================
# CONFIGURATION
# This file serves as the central control panel for the application.
# It stores API keys, model settings, and memory limits.
# ==============================================================================

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ------------------------------------------------------------------------------
# 1. API Credentials
# We use environment variables for security (never hardcode real keys in code!).
# ------------------------------------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("Missing GROQ_API_KEY")

# ------------------------------------------------------------------------------
# 2. JWT & Security Settings
# ------------------------------------------------------------------------------
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
ADMIN_DEFAULT_PASSWORD = os.getenv("ADMIN_PASSWORD", "change_me_in_prod")

# ------------------------------------------------------------------------------
# 3. Model Settings
# We use Llama 3.1 (8B parameter version) via Groq for ultra-fast inference.
# ------------------------------------------------------------------------------
MODEL_NAME = "llama-3.3-70b-versatile"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ------------------------------------------------------------------------------
# 4. Google Authentication
# ------------------------------------------------------------------------------
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# ------------------------------------------------------------------------------
# 5. Email Service (SMTP)
# ------------------------------------------------------------------------------
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# ------------------------------------------------------------------------------
# 6. Memory Architecture Settings
# ------------------------------------------------------------------------------
# MAX_HISTORY_LIMIT: 
# (Currently unused in app.py logic as we allow infinite session history, 
# but kept here for future reference or safety limits).
MAX_HISTORY_LIMIT = 100  

# CONTEXT_WINDOW_SIZE:
# How many recent messages (turns) the Brain/Agent actually "sees" 
# to make decisions. Too many = confuses the AI, Too few = loses context.
CONTEXT_WINDOW_SIZE = 30

# MEMORY_CONFIDENCE_THRESHOLD:
# Minimum similarity score (0.0-1.0) required for memory retrieval.
# Lower = more permissive matching, Higher = stricter matching.
MEMORY_CONFIDENCE_THRESHOLD = 0.28

# MEDICAL_COMPLETION_MARKERS:
# Phrases that indicate the medical agent has completed its diagnosis.
# Used to unlock from MEDICAL mode.
MEDICAL_COMPLETION_MARKERS = ["Final_Answer", "Possible Causes", "Next Steps", "Severity Level"]
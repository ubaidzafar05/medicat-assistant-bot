# ==============================================================================
# CONFIGURATION
# This file serves as the central control panel for the application.
# It stores API keys, model settings, and memory limits.
# ==============================================================================

import os

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
# 3. Memory Architecture Settings
# ------------------------------------------------------------------------------
# MAX_HISTORY_LIMIT: 
# (Currently unused in app.py logic as we allow infinite session history, 
# but kept here for future reference or safety limits).
MAX_HISTORY_LIMIT = 100  

# CONTEXT_WINDOW_SIZE:
# How many recent messages (turns) the Brain/Agent actually "sees" 
# to make decisions. Too many = confuses the AI, Too few = loses context.
CONTEXT_WINDOW_SIZE = 30
# deprecated.
# How to Run: run python -m uvicorn web_app:app --host 127.0.0.1 --port 8000 --reload Then visit: http://127.0.0.1:8000
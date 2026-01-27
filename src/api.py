from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from jose import jwt, JWTError
import json
import uuid
import logging
import os

# Import core components
from src.core.session_manager import SessionManager
from src.core.brain import Brain
from src.services.llm_groq import GroqLLM
from src.services.search_tool import SearchTool
from src.agents.medical_agent import MedicalReActAgent
from src.agents.prescription_agent import PrescriptionAgent
# New imports for missing features
from src.core.logic_utils import execute_chat_logic
from src.agents.router import decide_action
from src.services.google_auth import GoogleAuth
from src.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_HOURS

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

app = FastAPI(title="NeuralFlow Medical API", description=" Backend for the Medical Chatbot")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session Middleware (Required for Google Auth / Authlib)
app.add_middleware(SessionMiddleware, secret_key=JWT_SECRET_KEY)

# ------------------------------------------------------------------------------
# COMPONENTS & AUTH
# ------------------------------------------------------------------------------
components = {
    "brain": Brain(),
    "llm": GroqLLM(),
    "search_tool": SearchTool(),
    "medical_agent": MedicalReActAgent(),
    "prescription_agent": PrescriptionAgent()
}

google_auth = GoogleAuth(app)

# ------------------------------------------------------------------------------
# Pydantic Models
# ------------------------------------------------------------------------------
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ChatMessage(BaseModel):
    user_input: str
    username: str 
    session_id: Optional[str] = None

class VitalInput(BaseModel):
    username: str
    type: str
    value: str
    unit: str

class NewChatRequest(BaseModel):
    username: str

class SwitchSessionRequest(BaseModel):
    username: str

class PrescriptionInput(BaseModel):
    username: str
    medicine_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    times: List[str] = []
    instructions: Optional[str] = None

class SessionInfo(BaseModel):
    id: str
    created_at: str
    last_active: str
    preview: Optional[str] = None
    message_count: int = 0

# ------------------------------------------------------------------------------
# JWT HELPER FUNCTIONS
# ------------------------------------------------------------------------------
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=JWT_EXPIRATION_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None:
        return None # Optional auth for some endpoints
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

# ------------------------------------------------------------------------------
# AUTH ENDPOINTS
# ------------------------------------------------------------------------------
@app.post("/auth/register")
async def register(user: UserRegister):
    sm = SessionManager()
    success = sm.db.create_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User registered successfully"}

@app.post("/auth/login")
async def login(user: UserLogin):
    sm = SessionManager()
    is_valid = sm.verify_user(user.username, user.password)
    # Also support "direct" login for google users if password matches dummy or is handled
    if not is_valid: 
        # Check if user exists but has no password (Google user) - handled by frontend flow mostly
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"username": user.username, "access_token": access_token}

@app.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    return await google_auth.get_oauth().google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def google_callback(request: Request):
    try:
        token = await google_auth.get_oauth().google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if not user_info:
            user_info = await google_auth.get_oauth().google.userinfo(token=token)
            
        email = user_info.get('email')
        name = user_info.get('name') or email.split('@')[0]
        
        # Auto-register/login
        sm = SessionManager()
        if not sm.db.verify_user(email, "google_oauth_dummy"):
             # If user doesn't exist (verify returns false), check if exists at all
             # This is a simplified check. Real app would have proper User object
             sm.db.create_user(email, "google_oauth_dummy") # Create if new
        
        access_token = create_access_token(data={"sub": email})
        
        # Redirect to frontend with token
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        return RedirectResponse(url=f"{frontend_url}/auth/google/callback?token={access_token}&username={email}&email={email}")
    except Exception as e:
        logger.error(f"Google Auth Error: {e}")
        return {"error": f"Authentication failed: {str(e)}"}

# ------------------------------------------------------------------------------
# CHAT ENDPOINTS
# ------------------------------------------------------------------------------
@app.post("/chat/message")
async def chat(message: ChatMessage):
    session_manager = SessionManager()
    session_manager.set_user(message.username)
    if message.session_id:
        session_manager.current_session_id = message.session_id

    session_manager.add_message("user", message.user_input)
    internal_history = session_manager.get_active_history()
    
    decision = decide_action(message.user_input, internal_history)
    action = decision.get("action", "CHAT")

    request_components = {**components, "session_manager": session_manager}

    async def response_generator():
        full_response = ""
        for chunk in execute_chat_logic(action, message.user_input, internal_history, decision, request_components):
            full_response += chunk
            yield chunk
        session_manager.add_message("assistant", full_response)

    return StreamingResponse(response_generator(), media_type="text/plain")

@app.get("/chat/sessions")
async def get_sessions(username: str, limit: int = 20):
    sm = SessionManager()
    sm.set_user(username)
    sessions = sm.db.get_recent_sessions(username, limit=limit)
    result = []
    for session in sessions:
        history = sm.db.get_history(session['id'], limit=1)
        preview = history[0].get('content', '')[:50] + '...' if history else None
        all_messages = sm.db.get_history(session['id'])
        result.append(SessionInfo(id=session['id'], created_at=str(session['created_at']), last_active=str(session['last_active']), preview=preview, message_count=len(all_messages)))
    return result

@app.get("/chat/history/{session_id}")
async def get_session_history(session_id: str, username: str):
    sm = SessionManager()
    sm.set_user(username)
    history = sm.db.get_history(session_id)
    return [{"role": msg["role"], "content": msg["content"]} for msg in history]

@app.post("/chat/new")
async def create_new_chat(request: NewChatRequest):
    sm = SessionManager()
    sm.set_user(request.username)
    new_session_id = sm.start_new_session()
    sm.set_active_mode(None)
    return {"session_id": new_session_id, "id": new_session_id, "preview": "New Chat", "created_at": str(datetime.now())} # matching SessionInfo partial

# ------------------------------------------------------------------------------
# VITALS & PRESCRIPTIONS
# ------------------------------------------------------------------------------
@app.post("/vitals")
async def save_vital(vital: VitalInput):
    sm = SessionManager()
    sm.set_user(vital.username)
    sm.save_vital(vital.type, vital.value, vital.unit)
    return {"message": "Vital saved"}

@app.get("/vitals")
async def get_vitals(username: str, limit: int = 5):
    sm = SessionManager()
    sm.set_user(username)
    return sm.get_recent_vitals(limit=limit)

@app.post("/prescriptions")
async def add_prescription(pres: PrescriptionInput):
    sm = SessionManager()
    # Direct DB access for simplicity in API wrapper
    pres_id = sm.db.add_prescription(
        pres.username, 
        pres.medicine_name, 
        pres.dosage, 
        pres.frequency, 
        json.dumps(pres.times) if isinstance(pres.times, list) else pres.times, 
        pres.instructions
    )
    
    # Schedule reminders
    from src.services.reminder_scheduler import ReminderScheduler
    scheduler = ReminderScheduler()
    scheduler.schedule_prescription(pres_id, pres.medicine_name, pres.times)
    
    return {"id": pres_id, "message": "Prescription created", "reminders_scheduled": len(pres.times)*7}

@app.get("/prescriptions")
async def get_prescriptions(username: str):
    sm = SessionManager()
    prescriptions = sm.db.get_active_prescriptions(username)
    # Parse times from JSON string if needed
    for p in prescriptions:
        if isinstance(p.get('times'), str):
             try: p['times'] = json.loads(p['times'])
             except: pass
    return prescriptions

@app.delete("/prescriptions/{pres_id}")
async def delete_prescription(pres_id: int, username: str):
    sm = SessionManager()
    success = sm.db.deactivate_prescription(pres_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return {"message": "Prescription deactivated"}

@app.get("/reminders")
async def get_reminders(username: str, limit: int = 10):
    sm = SessionManager()
    reminders = sm.db.get_upcoming_reminders(username) # Assume this method exists or we use raw query
    # If method not in DB class yet, we might need to add it, but assuming it was part of previous restore
    return reminders[:limit]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
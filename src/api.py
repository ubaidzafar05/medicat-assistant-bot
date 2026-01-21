from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
from jose import jwt, JWTError
import json
import uuid
import logging

# Import our existing core components
from src.core.session_manager import SessionManager
from src.core.brain import Brain
from src.services.llm_groq import GroqLLM
from src.services.search_tool import SearchTool
from src.agents.medical_agent import MedicalReActAgent
from src.core.logic_utils import execute_chat_logic
from src.agents.router import decide_action
from src.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_HOURS

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

app = FastAPI(title="NeuralFlow Medical API", description="Backend for the Medical Chatbot")

# CORS (Allow Frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# GLOBAL COMPONENTS (Stateless Only)
# ------------------------------------------------------------------------------
# We removed 'session_manager' from here to prevent user state bleeding.
components = {
    "brain": Brain(),
    "llm": GroqLLM(),
    "search_tool": SearchTool(),
    "medical_agent": MedicalReActAgent()
}

# ------------------------------------------------------------------------------
# Pydantic Models for Request/Response
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

class VitalInput(BaseModel):
    username: str
    type: str
    value: str
    unit: str

class NewChatRequest(BaseModel):
    username: str

class SwitchSessionRequest(BaseModel):
    username: str

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
    """Creates a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=JWT_EXPIRATION_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to verify JWT token and return username."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return username
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ------------------------------------------------------------------------------
# AUTH ENDPOINTS
# ------------------------------------------------------------------------------
@app.post("/auth/register")
async def register(user: UserRegister):
    """Register a new user."""
    sm = SessionManager()
    success = sm.db.create_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User registered successfully"}

@app.post("/auth/login")
async def login(user: UserLogin):
    """Login and receive a JWT token."""
    sm = SessionManager()
    is_valid = sm.verify_user(user.username, user.password)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate real JWT token
    access_token = create_access_token(data={"sub": user.username})
    return {
        "username": user.username, 
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/auth/me")
async def get_current_user(username: str = Depends(verify_token)):
    """Get current authenticated user info."""
    return {"username": username}

# ------------------------------------------------------------------------------
# CHAT ENDPOINTS
# ------------------------------------------------------------------------------
@app.post("/chat/message")
async def chat(message: ChatMessage):
    """
    Streaming chat endpoint.
    """
    # 1. Create a request-scoped session manager
    # This ensures we are talking about THIS user, not 'admin'
    session_manager = SessionManager()
    session_manager.set_user(message.username)
    
    # 2. Persist User Message
    session_manager.add_message("user", message.user_input)
    internal_history = session_manager.get_active_history()
    
    # 3. Decision Logic
    decision = decide_action(message.user_input, internal_history)
    action = decision.get("action", "CHAT")

    # 4. Inject the scoped session_manager into components
    request_components = {
        **components,
        "session_manager": session_manager
    }

    async def response_generator():
        full_response = ""
        # Pass request_components so the agents use the correct user context
        for chunk in execute_chat_logic(action, message.user_input, internal_history, decision, request_components):
            full_response += chunk
            yield chunk
            
        # 5. Persist Assistant Response
        session_manager.add_message("assistant", full_response)

    return StreamingResponse(response_generator(), media_type="text/plain")

@app.get("/chat/history")
async def get_history(username: str):
    # Request-scoped instance
    sm = SessionManager()
    sm.set_user(username)
    return sm.get_active_history()

@app.post("/chat/new")
async def create_new_chat(request: NewChatRequest):
    """Create a new chat session for the user."""
    sm = SessionManager()
    sm.set_user(request.username)
    
    # Create new session and clear any active mode
    new_session_id = sm.start_new_session()
    sm.set_active_mode(None)
    
    return {
        "session_id": new_session_id,
        "message": "New chat created"
    }

@app.get("/chat/sessions")
async def get_sessions(username: str, limit: int = 20):
    """Get list of user's chat sessions with previews."""
    sm = SessionManager()
    sm.set_user(username)
    
    sessions = sm.db.get_recent_sessions(username, limit=limit)
    
    # Enrich each session with preview and message count
    result = []
    for session in sessions:
        # Get first user message as preview
        history = sm.db.get_history(session['id'], limit=1)
        preview = None
        if history:
            preview = history[0].get('content', '')[:50]
            if len(history[0].get('content', '')) > 50:
                preview += '...'
        
        # Get message count
        all_messages = sm.db.get_history(session['id'])
        
        result.append(SessionInfo(
            id=session['id'],
            created_at=str(session['created_at']),
            last_active=str(session['last_active']),
            preview=preview,
            message_count=len(all_messages)
        ))
    
    return result

@app.get("/chat/history/{session_id}")
async def get_session_history(session_id: str, username: str):
    """Get history for a specific session."""
    sm = SessionManager()
    sm.set_user(username)
    
    # Verify session belongs to user
    sessions = sm.db.get_recent_sessions(username, limit=100)
    session_ids = [s['id'] for s in sessions]
    
    if session_id not in session_ids:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history = sm.db.get_history(session_id)
    return [{"role": msg["role"], "content": msg["content"]} for msg in history]

@app.post("/chat/switch/{session_id}")
async def switch_session(session_id: str, request: SwitchSessionRequest):
    """Switch to a specific session."""
    sm = SessionManager()
    sm.set_user(request.username)
    
    # Verify session belongs to user
    sessions = sm.db.get_recent_sessions(request.username, limit=100)
    session_ids = [s['id'] for s in sessions]
    
    if session_id not in session_ids:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Set the current session
    sm.current_session_id = session_id
    
    # Get history for the session
    history = sm.db.get_history(session_id)
    
    return {
        "session_id": session_id,
        "history": [{"role": msg["role"], "content": msg["content"]} for msg in history]
    }

# ------------------------------------------------------------------------------
# VITALS ENDPOINTS
# ------------------------------------------------------------------------------
@app.post("/vitals")
async def save_vital(vital: VitalInput):
    # Request-scoped instance
    sm = SessionManager()
    sm.set_user(vital.username)
    sm.save_vital(vital.type, vital.value, vital.unit)
    return {"message": "Vital saved"}

@app.get("/vitals")
async def get_vitals(username: str, limit: int = 5):
    # Request-scoped instance
    sm = SessionManager()
    sm.set_user(username)
    return sm.get_recent_vitals(limit=limit)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
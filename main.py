import gradio as gr
import os
import logging
from src.agents.router import decide_action
from src.utils import strip_internal_markers
from src.core.brain import Brain
from src.services.llm_groq import GroqLLM
from src.services.search_tool import SearchTool
from src.agents.medical_agent import MedicalReActAgent
from src.config import CONTEXT_WINDOW_SIZE
from src.core.logic_utils import execute_chat_logic

# ------------------------------------------------------------------------------
# 1. WINDOWS / SHARING SAFEGUARDS
# These prevent the app from hanging when share=True is enabled.
# ------------------------------------------------------------------------------
os.environ["HF_HUB_OFFLINE"] = "1" # Prevents HuggingFace timeout hangs

# Manually point to the FRPC binary if it exists (Fixes sharing on some Windows PCs)
frpc_path = os.path.expanduser("~/.gradio/frpc_windows_amd64_v0.2.exe")
if os.path.exists(frpc_path):
    os.environ["GRADIO_FRPC_BINARY"] = frpc_path

# ------------------------------------------------------------------------------
# 2. GLOBAL STATE
# ------------------------------------------------------------------------------
# NOTE: active_mode is now stored per-user in the session_manager (database)
# This prevents state bleeding between users

# Initialize Components
try:
    print("Initializing NeuralFlow Components...")
    from src.core.session_manager import SessionManager
    components = {
        "brain": Brain(),
        "llm": GroqLLM(),
        "search_tool": SearchTool(),
        "medical_agent": MedicalReActAgent(),
        "session_manager": SessionManager()
    }
    # components["brain"].clear_memory() # OPTIONAL: Determine if you want to wipe long-term memory on restart
    print("System Online.")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")

# ------------------------------------------------------------------------------
# 3. CHAT LOGIC
# ------------------------------------------------------------------------------
def auth_fn(username, password):
    """Verifies credentials against the database."""
    return components["session_manager"].verify_user(username, password)

def chat_logic(message, history, request: gr.Request):
    global active_mode
    
    # 0. Identify User
    username = request.username if request else "admin"
    session_manager = components["session_manager"]
    session_manager.set_user(username)

    user_input = message.strip()
    if not user_input:
        yield "Please enter a message."
        return
    
    # 1. Get History (Before adding current message, to avoid duplication in context)
    internal_history = session_manager.get_active_history()
    
    # 2. Persist User Message
    session_manager.add_message("user", user_input)

    # --- STATE-AWARE ROUTING ---
    active_mode = session_manager.get_active_mode()
    
    if active_mode == "MEDICAL":
        # Locked in Medical Mode -> Bypass Router
        action = "MEDICAL"
        decision = {"action": "MEDICAL"}
    else:
        # Normal Mode -> Ask Router
        decision = decide_action(user_input, internal_history)
        action = decision.get("action", "CHAT")
        
        # If Router chooses MEDICAL, Lock the State
        if action == "MEDICAL":
            session_manager.set_active_mode("MEDICAL")

    # --- EXECUTION ---
    full_response = ""
    # Stream the response chunk by chunk
    for chunk in execute_chat_logic(action, user_input, internal_history, decision, components):
        full_response += chunk
        yield full_response
    
    # 3. Persist Assistant Response
    session_manager.add_message("assistant", full_response)
        
    # --- UNLOCK CONDITION ---
    # If the Medical Agent is done, release the lock
    if action == "MEDICAL" and "Final_Answer" in full_response:
        session_manager.set_active_mode(None)

# ------------------------------------------------------------------------------
# 4. LAUNCH INTERFACE
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    demo = gr.ChatInterface(
        fn=chat_logic,
        title="NeuralFlow Medical Specialist",
        description="Secure medical consultant with persistent, private memory. Login required.",
        examples=["I have a headache.", "What is Vitamin C?", "Symptoms of jaundice"],
    )
    
    print("Launching Web Interface...")
    print("Note: If 'share=True' gets stuck, ensure you have internet access.")
    
    # Authenticated Launch
    demo.launch(
        share=True,
        auth=auth_fn,
        auth_message="Please log in with your NeuralFlow credentials."
    )
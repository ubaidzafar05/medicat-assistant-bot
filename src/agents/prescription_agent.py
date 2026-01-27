from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from src.utils import get_llm
import json
import datetime

# --- State Definitions ---
class AgentState(TypedDict):
    messages: List[str]
    user_id: str
    medicine: str
    times: List[str]
    dosage: str
    instructions: str
    next_step: str

# --- Graph Nodes ---

def extract_info(state: AgentState):
    """
    Extracts medicine, times, dosage from the last user message using an LLM.
    """
    llm = get_llm()
    last_message = state['messages'][-1]
    
    extraction_prompt = f"""
    You are a medical assistant extracting prescription details.
    User Input: "{last_message}"
    
    Extract the following JSON (return NULL if missing):
    {{
        "medicine": "name of medicine",
        "times": ["HH:MM", "HH:MM"], (convert to 24-hour format lists, e.g. ["08:00", "20:00"])
        "dosage": "dosage amount",
        "instructions": "special instructions like 'with food'"
    }}
    
    If the user says "twice daily", "every 8 hours", etc., infer likely times (e.g. 09:00, 21:00).
    """
    
    response = llm.invoke([HumanMessage(content=extraction_prompt)])
    content = response.content.strip()
    
    # Simple parsing (robustness would use structured outputs)
    try:
        data = json.loads(content.replace('```json', '').replace('```', ''))
    except:
        # Fallback if raw text
        data = {}

    updates = {}
    if data.get('medicine'): updates['medicine'] = data['medicine']
    if data.get('times'): updates['times'] = data['times']
    if data.get('dosage'): updates['dosage'] = data['dosage']
    if data.get('instructions'): updates['instructions'] = data['instructions']
    
    return updates

def check_missing(state: AgentState):
    """
    Determines if we have enough info to schedule.
    """
    if not state.get('medicine'):
        return {"next_step": "ask_medicine"}
    if not state.get('times') or len(state['times']) == 0:
        return {"next_step": "ask_times"}
    return {"next_step": "save"}

def save_prescription(state: AgentState):
    """
    Saves the prescription to database/scheduler.
    (Mock implementation detail - usually calls service)
    """
    from src.services.database import Database
    from src.services.reminder_scheduler import ReminderScheduler
    
    db = Database()
    scheduler = ReminderScheduler()
    
    # Save to DB
    pres_id = db.add_prescription(
        state['user_id'],
        state['medicine'],
        state.get('dosage'),
        "custom",
        state['times'],
        state.get('instructions')
    )
    
    # Schedule
    scheduler.schedule_prescription(pres_id, state['medicine'], state['times'])
    
    return {"messages": [f"✅ Prescription Saved! I'll remind you to take {state['medicine']} at {', '.join(state['times'])}."]}

# --- Workflow Definition ---

workflow = StateGraph(AgentState)

workflow.add_node("extract", extract_info)
workflow.add_node("check", check_missing)
workflow.add_node("save", save_prescription)

workflow.set_entry_point("extract")
workflow.add_edge("extract", "check")

def router(state):
    if state['next_step'] == "save":
        return "save"
    return END # Should actually loop back to ask questions, keeping simple for now

workflow.add_conditional_edges("check", router)
workflow.add_edge("save", END)

app = workflow.compile()

class PrescriptionAgent:
    def run_streaming(self, user_input, user_id, history):
        """
        Entry point for the agent.
        """
        initial_state = {
            "messages": [user_input],
            "user_id": user_id,
            "medicine": None,
            "times": [],
            "dosage": None,
            "instructions": None,
            "next_step": None
        }
        
        # In a real app we'd maintain state across turns. 
        # Here we run one pass. If missing info, we ask.
        
        result = app.invoke(initial_state)
        
        if result.get('next_step') == 'ask_medicine':
            yield "What medicine do you need to take?"
        elif result.get('next_step') == 'ask_times':
            yield f"When should I remind you to take {result['medicine']}? (e.g., '8am and 8pm')"
        elif result.get('messages') and "Saved" in result['messages'][-1]:
            yield result['messages'][-1]
        
def infer_times_with_llm(frequency_text: str) -> List[str]:
    """
    Helper to convert natural language frequency to list of times.
    """
    llm = get_llm()
    prompt = f"""
    Convert "{frequency_text}" into a JSON list of 24-hour format times (HH:MM).
    Examples:
    "thrice daily" -> ["08:00", "14:00", "20:00"]
    "every 4 hours" -> ["06:00", "10:00", "14:00", "18:00", "22:00"]
    "bedtime" -> ["22:00"]
    
    Return ONLY the JSON list.
    """
    try:
        response = llm.invoke(prompt).content.strip()
        times = json.loads(response.replace('```json', '').replace('```', ''))
        return times
    except:
        return []

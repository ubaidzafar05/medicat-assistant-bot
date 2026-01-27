# ==============================================================================
# AGENT (Decision Maker)
# This file acts as the 'Frontal Lobe' of the chatbot.
# Its sole purpose is to classify the USER'S INTENT into specific categories.
# ==============================================================================

from src.services.llm_groq import GroqLLM
from src.config import CONTEXT_WINDOW_SIZE

# Initialize a separate LLM instance for the Agent's thought process
llm_agent = GroqLLM()

import json
import re
    
def decide_action(user_input: str, history: list = None) -> dict:
    """
    Decides the action based on user input and conversation context.
    Returns a dict: {"action": "CHAT"|"SEARCH"|"MEMORY"|"MEDICAL"|"TEACH"|"RESET", "learn": "fact string"|None}
    """
    history = history or []
    
    # --------------------------------------------------------------------------
    # 1. Prepare Context
    # --------------------------------------------------------------------------
    context_text = ""
    if history:
        context_text = "Recent History:\n" + "\n".join([f"- {msg['role'].title()}: {msg['content']}" for msg in history[-CONTEXT_WINDOW_SIZE:]]) + "\n"

    # --------------------------------------------------------------------------
    # 2. Construct the Decision Prompt
    # --------------------------------------------------------------------------
    prompt = f"""
{context_text}
User Input: "{user_input}"

You are the Intent Router. Your job is to classify the USER'S INTENT using a ReAct (Reasoning + Acting) loop.

### AVAILABLE ACTIONS:
- MEDICAL: User discusses symptoms, physical sensations, or health concerns (e.g., "My head hurts", "I have a rash").
- PRESCRIPTION: User asks to SET A REMINDER or SCHEDULE MEDICATION (e.g., "Remind me to take Panadol", "Schedule my meds").
- TEACH: User shares A NEW PERSONAL FACT (e.g., "I am allergic to peanuts", "My name is John"). NEVER use for questions.
- MEMORY: User asks a QUESTION about their own identity, history, or previous facts (e.g., "What am I allergic to?", "What is my name?", "Can I have this?").
- SEARCH: User asks a QUESTION about general knowledge, medical facts, or recipes (e.g., "What is Vitamin C?", "How to bake bread").
- CHAT: User greets or makes social small talk.
- RESET: User wants to clear session.

### ROUTING ANALYSIS INSTRUCTIONS:
1. **MEMORY PRIORITY**: Any question starting with "What is my...", "What am I...", "Do I have...", or "Can I..." that relies on personal context -> ALWAYS **MEMORY**.
2. **MEDICAL PRIORITY**: MEDICAL PRIORITY: Any mention of a symptom, pain, injury, **OR MEDICATION name** -> ALWAYS MEDICAL.
3. **SEARCH PRIORITY**: Any general "What is...", "How to...", or news query -> ALWAYS **SEARCH**.
4. **TEACH PRIORITY**: Any statement starting with "I am...", "I have [allergy/condition]...", or "My name is..." -> ALWAYS **TEACH**.
5. **CONTINUITY PRIORITY (STRICT)**: If the conversation is already in a MEDICAL loop, STAY in MEDICAL mode for any short answers (e.g., "yes", "no", "5 hours", "stabbing"). Do NOT switch to CHAT unless the user specifically says "Goodbye" or "Stop".- IF INPUT ENDS IN '?' -> CHOOSE **MEMORY**, **SEARCH**, or **MEDICAL**.
- IF INPUT CONTAINS "MY" or "AM I" -> FAVOR **MEMORY**.
- IF IN DOUBT -> **MEDICAL**.

### FORMAT:
Thought: [Step 1: What was the last active topic? Step 2: Does this input connect to it?]
Action: [Select ONE action]
Learn: [If TEACH, extract fact. Else, leave blank]

Now, provide your Thought, Action, and Learn.
"""

    # --------------------------------------------------------------------------
    # 3. Get Classification
    # --------------------------------------------------------------------------
    try:
        response_text = llm_agent(prompt).strip()
        
        # Parse Action - allow for "Action: **SEARCH**" or similar
        action_match = re.search(r"Action:\s*\*?\*?(MEDICAL|CHAT|SEARCH|TEACH|MEMORY|RESET)\*?\*?", response_text, re.IGNORECASE)
        chosen_action = action_match.group(1).upper() if action_match else "CHAT"
        
        # Parse Learn (if any)
        learn_match = re.search(r"Learn:\s*\*?\*?(.*)", response_text, re.IGNORECASE)
        fact_to_learn = learn_match.group(1).strip().strip('*').strip() if (learn_match and chosen_action == "TEACH") else None
            
        return {
            "action": chosen_action,
            "learn": fact_to_learn,
            "search_query": None
        }

    except Exception as e:
        print(f"[DEBUG-AGENT] Error: {e}")
        return {"action": "CHAT", "learn": None, "search_query": None}

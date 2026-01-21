
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logic_utils import execute_chat_logic
from brain import Brain
from llm_groq import GroqLLM
from search_tool import SearchTool
from medical_agent import MedicalReActAgent
from agent import decide_action

def test_bleeding_redundancy():
    components = {
        "brain": Brain(),
        "llm": GroqLLM(),
        "search_tool": SearchTool(),
        "medical_agent": MedicalReActAgent()
    }
    
    # Simulate the user's reported multi-turn scenario
    history = [
        {"role": "user", "content": "Hey"},
        {"role": "assistant", "content": "How are you feeling today?"}
    ]
    
    # TURN 1: Initial report
    user_input_1 = "im actually in quite pain, i accidently hurt my finger with a knife while cutting fruits. the bleeding isnt stopping, what should i do"
    print(f"\nUser: {user_input_1}")
    decision_1 = decide_action(user_input_1, history)
    action_1 = decision_1["action"]
    
    response_1 = ""
    for chunk in execute_chat_logic(action_1, user_input_1, history, decision_1, components):
        response_1 += chunk
    
    print(f"Bot: {response_1}")
    
    # Check for search leakage
    if "Thinking..." in response_1 or "Searching for" in response_1:
        print("FAIL: Leaked search thought.")
    else:
        print("PASS: Search thought suppressed.")

    # Check for redundant location question
    if "where is the cut" in response_1.lower() or "location" in response_1.lower():
         # It's okay to ask for location if it wasn't clear, but here "finger" is explicit.
         # However, asking specifically "where on the finger" might be too granular, generally "where is the cut" implies they missed the "finger" part.
        print("FAIL: Bot asked 'Where is the cut' despite 'finger' being known.")
    else:
        print("PASS: Bot did not ask redundant location question.")

    # Check for Deep Cut recognition
    if "pressure" in response_1.lower() or "emergency" in response_1.lower() or "stitches" in response_1.lower() or "hospital" in response_1.lower():
        print("PASS: Recognized urgency/treatment.")
    else:
        print("FAIL: Did not provide immediate pressure/ER advice.")

if __name__ == "__main__":
    test_bleeding_redundancy()

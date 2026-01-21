
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logic_utils import execute_chat_logic
from brain import Brain
from llm_groq import GroqLLM
from search_tool import SearchTool
from medical_agent import MedicalReActAgent
from agent import decide_action

def test_kidney_redundancy():
    components = {
        "brain": Brain(),
        "llm": GroqLLM(),
        "search_tool": SearchTool(),
        "medical_agent": MedicalReActAgent()
    }
    
    # Simulate the user's reported multi-turn scenario
    history = []
    
    # TURN 1: Initial report
    user_input_1 = "from the past few days i have been feeling smal sharp needle like pain in my left kidney"
    print(f"User: {user_input_1}")
    decision_1 = decide_action(user_input_1, history)
    action_1 = decision_1["action"]
    
    response_1 = ""
    for chunk in execute_chat_logic(action_1, user_input_1, history, decision_1, components):
        response_1 += chunk
    
    print(f"Bot: {response_1}")
    
    # Check if redundant question "How long" is in the response
    if "how long" in response_1.lower() or "how many days" in response_1.lower():
        print("FAIL: Bot asked 'How long' even though user said 'past few days'.")
    else:
        print("PASS: Bot did not ask redundant duration question.")

    # Check for bridge phrases
    if "i'd like to ask" in response_1.lower() or "to better understand" in response_1.lower():
        print("FAIL: Bot leaked bridge phrases.")
    else:
        print("PASS: No bridge phrases leaked.")

if __name__ == "__main__":
    test_kidney_redundancy()

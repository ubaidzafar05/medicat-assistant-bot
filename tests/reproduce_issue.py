
import sys
import os

# Add parent directory to sys.path to import agent.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent import decide_action

def test_routing():
    print("Testing Routing Logic (Round 2)...")
    
    # Case 1: Ambiguous input with Medical Context
    history = [
        {"role": "user", "content": "I hurt my arm"},
        {"role": "assistant", "content": "Is the pain sharp or dull?"}
    ]
    user_input = "Sharp"
    print(f"\nCase 1 Context: {history[-1]['content']}")
    print(f"Input: {user_input}")
    decision = decide_action(user_input, history)
    print(f"Decision: {decision['action']}")
    if decision['action'] == "MEDICAL":
        print("PASS: Correctly identified as MEDICAL")
    else:
        print(f"FAIL: Identified as {decision['action']}")

    # Case 2: Ambiguous input with Chat Context
    history_chat = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there! How are you?"}
    ]
    user_input_chat = "Good"
    print(f"\nCase 2 Context: {history_chat[-1]['content']}")
    print(f"Input: {user_input_chat}")
    decision_chat = decide_action(user_input_chat, history_chat)
    print(f"Decision: {decision_chat['action']}")
    if decision_chat['action'] == "CHAT":
        print("PASS: Correctly identified as CHAT")
    else:
        print(f"FAIL: Identified as {decision_chat['action']}")

    # Case 3: "Yes" follow-up
    history_yes = [
        {"role": "user", "content": "im also burping and it smells strongly like olives"},
        {"role": "assistant", "content": "That's an interesting symptom. would you like to discuss this further?"}
    ]
    user_input_yes = "yes"
    print(f"\nCase 3 Context: {history_yes[-1]['content']}")
    print(f"Input: {user_input_yes}")
    decision_yes = decide_action(user_input_yes, history_yes)
    print(f"Decision: {decision_yes['action']}")
    if decision_yes['action'] == "MEDICAL":
        print("PASS: Correctly identified 'yes' as MEDICAL")
    else:
        print(f"FAIL: Identified 'yes' as {decision_yes['action']}")

    # Case 4: "what to do" follow-up (Full Context)
    history_do = [
        {"role": "user", "content": "i am feeling a little dizzy after eating lunch"},
        {"role": "assistant", "content": "That's concerning..."},
        {"role": "user", "content": "im also burping and it smells strongly like olives"},
        {"role": "assistant", "content": "That's an interesting symptom. would you like to discuss this further?"},
        {"role": "user", "content": "yes"},
        {"role": "assistant", "content": "I'm glad you're here. telling me more helps me understand."}
    ]
    user_input_do = "can you tell me what to do"
    print(f"\nCase 4 Context: {history_do[-1]['content']}")
    print(f"Input: {user_input_do}")
    decision_do = decide_action(user_input_do, history_do)
    print(f"Decision: {decision_do['action']}")
    if decision_do['action'] == "MEDICAL":
        print("PASS: Correctly identified 'what to do' as MEDICAL")
    else:
        print(f"FAIL: Identified 'what to do' as {decision_do['action']}")

if __name__ == "__main__":
    test_routing()

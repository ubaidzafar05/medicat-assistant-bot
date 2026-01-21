
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from medical_agent import MedicalReActAgent
from agent import decide_action

def test_heart_attack_failure():
    print("Testing Heart Attack Scenario...")
    agent = MedicalReActAgent()
    
    # 1. User reports Heart Attack symptoms
    history = []
    user_input_1 = "I have chest pain spreading to my left arm and I feel dizzy"
    print(f"\nUser: {user_input_1}")
    
    response_1 = ""
    for chunk in agent.run(user_input_1, history):
        response_1 += chunk
    print(f"Bot: {response_1}")
    
    # Check if it was an emergency response OR a question
    if "?" in response_1 and "ER" not in response_1:
         print("FAIL: Bot asked a question instead of triggering Emergency Protocol.")
    elif "ER" in response_1 or "911" in response_1 or "emergency" in response_1.lower():
         print("PASS: Bot triggered Emergency Protocol.")
    else:
         print("WARNING: ambiguous response.")

    # 2. User says "severe" (Simulating context loss)
    history.append({"role": "user", "content": user_input_1})
    history.append({"role": "assistant", "content": response_1})
    
    user_input_2 = "severe"
    print(f"\nUser: {user_input_2}")
    
    # Check Routing first (Is "severe" MEDICAL or CHAT?)
    decision = decide_action(user_input_2, history)
    print(f"Router Decision: {decision['action']}")
    
    if decision['action'] != "MEDICAL":
        print(f"FAIL: Router sent 'severe' to {decision['action']}")
    else:
        # If routed correctly, check Medical Agent response
        response_2 = ""
        for chunk in agent.run(user_input_2, history):
            response_2 += chunk
        print(f"Bot: {response_2}")
        
        if "mean by" in response_2.lower() or "clarify" in response_2.lower():
            print("FAIL: Bot lost context and asked clarification for 'severe'.")
        else:
            print("PASS: Bot understood 'severe' context.")

if __name__ == "__main__":
    test_heart_attack_failure()

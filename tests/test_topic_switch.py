
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent import decide_action

def test_topic_switch():
    print("Testing Topic Switching...")
    
    # Context: User had a headache, Bot gave a final diagnosis/advice.
    history = [
        {"role": "user", "content": "I have a headache"},
        {"role": "assistant", "content": "Action: MEDICAL\nFinal_Answer: It sounds like a tension headache. Rest and hydration recommended."},
    ]
    
    # New Input: asking about a different medical topic (Fact/Search)
    user_input_1 = "what is diabetes?"
    print(f"\nContext: Diagnosis given.\nInput: {user_input_1}")
    
    decision_1 = decide_action(user_input_1, history)
    print(f"Decision: {decision_1['action']}")
    
    # We expect SEARCH (for facts) or MEDICAL (informational)
    # But crucially, it shouldn't be "stuck" thinking it's about the headache.
    
    # New Input 2: Personal symptom (New topic)
    user_input_2 = "actually my leg hurts now"
    print(f"\nInput: {user_input_2}")
    decision_2 = decide_action(user_input_2, history)
    print(f"Decision: {decision_2['action']}")
    
    # 3. Verify Agent Response to "What is diabetes?" (Topic Switch)
    # We want to ensure it defines it, rather than asking "How long have you had diabetes?"
    print("\n--- Verifying Agent Response ---")
    from medical_agent import MedicalReActAgent
    agent = MedicalReActAgent()
    
    # Re-create history for Agent
    history_agent = [
        {"role": "user", "content": "I have a headache"},
        {"role": "assistant", "content": "It sounds like a tension headache. Rest is recommended."},
    ]
    
    # Input: General question
    user_input_diabetes = "what is diabetes?"
    print(f"User: {user_input_diabetes}")
    
    response_diabetes = ""
    for chunk in agent.run(user_input_diabetes, history_agent):
        response_diabetes += chunk
        
    print(f"Bot: {response_diabetes}")
    
    # Fail if it asks about personal symptoms for a general question
    # We check for "how long" or "your symptoms" or "experiencing"
    lower_response = response_diabetes.lower()
    if "how long" in lower_response or "your symptoms" in lower_response or "are you experiencing" in lower_response:
        print("FAIL: Bot treated general question as personal diagnosis.")
    else:
        print("PASS: Bot treated query as informational.")

if __name__ == "__main__":
    test_topic_switch()

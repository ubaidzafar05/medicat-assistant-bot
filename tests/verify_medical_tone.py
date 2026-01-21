import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from medical_agent import MedicalReActAgent
import datetime

def test_medical_tone():
    print("=== Testing Refined Medical Tone ===")
    
    agent = MedicalReActAgent()
    
    # Scenario: Back pain after fall
    history = [
        {"role": "user", "content": "I have back pain"},
        {"role": "assistant", "content": "That sounds painful. Can you tell me more about when it started and if it's constant or intermittent?"}
    ]
    user_input = "i fell one week ago and then i started to have back pain"
    
    print(f"\nUser Input: '{user_input}'")
    print("Expected: Direct advice/question without 'I'm so sorry' or 'I'd be happy to help'.")

    try:
        print("\n--- Generating Agent Response ---")
        full_response = ""
        for chunk in agent.run(user_input, history):
            print(chunk, end="", flush=True)
            full_response += chunk
        print("\n--------------------------------")

        # Basic checks for pleasing language
        pleasing_phrases = ["happy to help", "glad to assist", "sorry to hear", "I'd be happy"]
        found_pleasing = [p for p in pleasing_phrases if p in full_response.lower()]
        
        if found_pleasing:
            print(f"[FAIL] Found pleasing fluff: {found_pleasing}")
        else:
            print("[PASS] No pleasing fluff detected.")
            
        if "doctor" in full_response.lower() or "er" in full_response.lower() or "severity" in full_response.lower() or "how long" in full_response.lower():
            print("[PASS] Response seems medically relevant.")

    except Exception as e:
        print(f"[ERROR] Error during test: {e}")

if __name__ == "__main__":
    test_medical_tone()

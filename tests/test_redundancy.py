
import sys
import os
import re

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from medical_agent import MedicalReActAgent

def test_redundancy():
    print("Testing Medical Redundancy (Bloating Scenario)...")
    agent = MedicalReActAgent()
    
    # Scenario: User says they have bloating for "7" severity, "a few days" duration.
    # The bot should NOT ask "how long" or "when did it start".
    
    history = [
        {"role": "user", "content": "i have been feeling bloated for a few days"},
        {"role": "assistant", "content": "That sounds uncomfortable. Can you tell me how severe the bloating is?"},
        {"role": "user", "content": "7, im not able to eat enough food."},
        {"role": "assistant", "content": "I'm concerned. Can you tell me more about when these symptoms started?"}
    ]
    
    # Crucial input where user answers the redundant question
    user_input = "a few days ago when i started burping."
    
    print(f"\nUser Input: {user_input}")
    print("Bot Response Stream:")
    
    full_response = ""
    # Run the generator
    for chunk in agent.run(user_input, history):
        print(chunk, end="")
        full_response += chunk
        
    print("\n\n--- Verification ---")
    
    # Check if the bot asked "when" or "how long" again
    redundant_phrases = ["when did", "how long", "what time", "duration"]
    found_redundancy = False
    
    for phrase in redundant_phrases:
        if phrase in full_response.lower():
            found_redundancy = True
            print(f"FAIL: Found redundant phrase '{phrase}' in response.")
            break
            
    if not found_redundancy:
        print("PASS: No redundant timing questions found.")
        # Optional: Check if it moved to other topics like 'vomit' or 'triggers'
        if "vomit" in full_response.lower() or "nausea" in full_response.lower() or "food" in full_response.lower() or "trigger" in full_response.lower():
             print("PASS: Addressed other symptoms (vomit/nausea) or triggers.")
        else:
             print("NOTE: Did not explicitly mention vomit/nausea, but passed redundancy check.")

if __name__ == "__main__":
    test_redundancy()

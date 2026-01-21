
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from medical_agent import MedicalReActAgent

def test_efficiency():
    print("Testing Medical Efficiency & Logic...")
    agent = MedicalReActAgent()
    
    # Scenario: User reports "Yellow eyes, vomiting, fever"
    # Expected: Bot identifies Jaundice/Liver issues immediately (Pattern Recognition)
    
    history = [
        {"role": "user", "content": "hey"},
        {"role": "assistant", "content": "Hello. I am here to help with medical concerns."},
    ]
    
    user_input = "i have yellow eyes, vomitting and fever for three days"
    print(f"\nUser Input: {user_input}")
    
    # Capture first response
    response_1 = ""
    for chunk in agent.run(user_input, history):
        response_1 += chunk
    
    print(f"Bot Response 1: {response_1}")
    
    # Check for Pattern Recognition
    keywords = ["jaundice", "liver", "hepatitis", "urgent", "immediate attention"]
    found_pattern = any(k in response_1.lower() for k in keywords)
    
    if found_pattern:
        print("PASS: Recognized severe pattern (Jaundice/Liver) immediately.")
    else:
        print("FAIL: Did not recognize severe pattern immediately. Bot is too slow.")
        
    # Check for Tone (No "happy to help", limited "sounds tough")
    if "happy to help" in response_1.lower():
        print("FAIL: Used pleasing language.")
    else:
        print("PASS: No pleasing language.")
        
    # Scenario 2: Testing "No" Logic
    # Update history
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": response_1})
    
    # User says "no" (meaning no other symptoms)
    user_input_no = "no"
    print(f"\nUser Input: {user_input_no}")
    
    response_2 = ""
    for chunk in agent.run(user_input_no, history):
        response_2 += chunk
        
    print(f"Bot Response 2: {response_2}")
    
    # Expect: Bot should NOT be confused. Should provide advice/diagnosis.
    if "clarify" in response_2.lower() or "referring to" in response_2.lower():
         print("FAIL: Bot was confused by 'No'.")
    else:
         print("PASS: Bot accepted 'No' as completion.")

if __name__ == "__main__":
    test_efficiency()

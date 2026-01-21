
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from medical_agent import MedicalReActAgent

def test_internal_monologue():
    print("Testing Hidden Monologue...")
    agent = MedicalReActAgent()
    
    # Simple input that triggers the checklist
    user_input = "im feeling headache"
    history = []
    
    full_response = ""
    for chunk in agent.run(user_input, history):
        full_response += chunk
        
    print(f"Full Response:\n{full_response}\n")
    
    # Verification
    forbidden_terms = ["SYMPTOMS:", "DURATION:", "SEVERITY:", "OBSERVATION CHECKLIST", "GAP ANALYSIS"]
    failed = False
    
    for term in forbidden_terms:
        if term in full_response:
            print(f"FAIL: Found internal term '{term}' in output.")
            failed = True
            
    if not failed:
        print("PASS: No internal monologue leaked.")
        
if __name__ == "__main__":
    test_internal_monologue()

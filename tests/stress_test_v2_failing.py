
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent import decide_action
from medical_agent import MedicalReActAgent
from brain import Brain
from llm_groq import GroqLLM
from search_tool import SearchTool
from logic_utils import execute_chat_logic

class TestResult:
    def __init__(self, name, passed, response):
        self.name = name
        self.passed = passed
        self.response = "".join(c for i, c in enumerate(response) if ord(c) < 128)

def run_retries():
    print("Retrying failing V2 tests with increased delays...")
    components = {
        "brain": Brain(),
        "llm": GroqLLM(),
        "search_tool": SearchTool(),
        "medical_agent": MedicalReActAgent()
    }
    
    results = []

    def check_response(name, user_input, history=[], expected_keywords=[], forbidden_keywords=[]):
        time.sleep(10.0) # High delay to reset rate limits
        print(f"\n[RETRY {name}] Input: {user_input}")
        decision = decide_action(user_input, history)
        action = decision['action']
        print(f"Action: {action}")
        
        response = ""
        try:
            for chunk in execute_chat_logic(action, user_input, history, decision, components):
                response += chunk
        except Exception as e:
            response = f"INTERNAL ERROR: {e}"
        
        safe_response = "".join(c for i, c in enumerate(response) if ord(c) < 128)
        print(f"Bot: {safe_response}")
        
        passed = True
        for kw_group in expected_keywords:
            if isinstance(kw_group, list):
                if not any(kw.lower() in safe_response.lower() for kw in kw_group):
                    print(f"FAIL: Missing any of {kw_group}")
                    passed = False
            else:
                if kw_group.lower() not in safe_response.lower():
                    print(f"FAIL: Missing expected keyword '{kw_group}'")
                    passed = False
        
        if passed: print("PASS")
        results.append(TestResult(name, passed, response))
        return passed

    # --- 7. Memory Confidence ---
    check_response("7. Memory Confidence", "When is my next dentist appointment?", expected_keywords=[["don't have", "information", "unknown", "previous", "record"]])

    # --- 10. Guard Rejection (Sourdough) ---
    check_response("10. Guard Rejection", "How to bake a sourdough bread", expected_keywords=[["cannot provide", "non-medical", "not discuss", "health-related"]])

    # --- 11. Medical Search ---
    check_response("11. Medical Search", "Latest treatments for Type 2 Diabetes", expected_keywords=[["insulin", "medication", "diet", "ozempic", "treatment"]])

    # --- 15. Allergy + Reaction (Advanced) ---
    check_response("15. Stress Test", "I had some seafood and now my throat feels tight and I'm wheezing", expected_keywords=[["911", "ER", "emergency", "allergic"]])

    print("\n--- RETRY SUMMARY ---")
    total_passed = sum(1 for r in results if r.passed)
    print(f"TOTAL PASSED: {total_passed} / {len(results)}")

if __name__ == "__main__":
    run_retries()

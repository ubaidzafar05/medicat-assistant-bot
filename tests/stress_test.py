
import sys
import os
import time
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent import decide_action
from medical_agent import MedicalReActAgent
from brain import Brain
from llm_groq import GroqLLM
from search_tool import SearchTool
from logic_utils import execute_chat_logic

# Standardize results
class TestResult:
    def __init__(self, name, passed, response):
        self.name = name
        self.passed = passed
        # Extreme sanitization for CMD
        self.response = "".join(c for i, c in enumerate(response) if ord(c) < 128)

def run_stress_test():
    print("Initializing components for Stress Test...")
    components = {
        "brain": Brain(),
        "llm": GroqLLM(),
        "search_tool": SearchTool(),
        "medical_agent": MedicalReActAgent()
    }
    
    results = []

    def check_response(name, user_input, history=[], expected_keywords=[], forbidden_keywords=[]):
        time.sleep(5.0) # Conservative delay to avoid Groq 429s during reasoning
        print(f"\n[TEST {name}] Input: {user_input}")
        decision = decide_action(user_input, history)
        action = decision['action']
        print(f"Action: {action}")
        
        response = ""
        try:
            for chunk in execute_chat_logic(action, user_input, history, decision, components):
                response += chunk
        except Exception as e:
            response = f"INTERNAL ERROR: {e}"
        
        # Sanitize for printing
        safe_response = "".join(c for i, c in enumerate(response) if ord(c) < 128)
        print(f"Bot: {safe_response}")
        
        passed = True
        # Flexible keyword check (supports list of lists for 'any of')
        for kw_group in expected_keywords:
            if isinstance(kw_group, list):
                if not any(kw.lower() in safe_response.lower() for kw in kw_group):
                    print(f"FAIL: Missing any of {kw_group}")
                    passed = False
            else:
                if kw_group.lower() not in safe_response.lower():
                    print(f"FAIL: Missing expected keyword '{kw_group}'")
                    passed = False
        
        for kw in forbidden_keywords:
            if kw.lower() in safe_response.lower():
                print(f"FAIL: Found forbidden keyword '{kw}'")
                passed = False
        
        results.append(TestResult(name, passed, response))
        return passed

    # --- 1. Emergency ---
    check_response("1. Emergency", "I have chest pain spreading to my left arm and I feel dizzy", expected_keywords=[["911", "ER", "emergency"]])

    # --- 2. Minor ---
    check_response("2. Minor Burn", "I burned my finger slightly while cooking", forbidden_keywords=["how long"])

    # --- 3. Vague ---
    check_response("3. Vague", "I feel unwell and tired", expected_keywords=[["?", "details", "symptoms", "experience"]])

    # --- 4. Lookup ---
    check_response("4. Knowledge Lookup", "Can ibuprofen cause stomach bleeding?", expected_keywords=[["bleeding", "stomach", "ibuprofen"]])

    # --- 5. Stop Questioning ---
    hist_5 = [
        {"role": "user", "content": "I fell off my bike yesterday"},
        {"role": "assistant", "content": "I see. How does your wrist feel?"}
    ]
    check_response("5. Stop Questioning", "My wrist hurts when I move it", history=hist_5, forbidden_keywords=["cause", "happen", "bike"])

    # --- 6. Teach + Infer ---
    components["brain"].clear_memory()
    time.sleep(1)
    components["brain"].teach("I am allergic to peanuts")
    check_response("6. Teach + Infer", "Can I eat a Snickers bar?", expected_keywords=[["peanut", "Snickers", "allergic", "safe"]])

    # --- 7. Memory Confidence ---
    components["brain"].teach("My favorite color is blue")
    check_response("7. Memory Confidence", "What's my blood type?", expected_keywords=[["don't have", "information", "unknown", "previous", "record"]])

    # --- 8. Mixed ---
    check_response("8. Mixed Query", "My arm hurts and what are Pfizer's stock prices?", expected_keywords=[["Pfizer", "price", "arm", "dizzy"]])

    # --- 9. Non-Medical (Guard) ---
    check_response("9. Non-Medical Topic", "Who won the World Cup?", expected_keywords=[["medical", "health", "specialized"]])

    # --- 10. Medical Guard Rejection ---
    check_response("10. Guard Rejection", "Latest iPhone release date", expected_keywords=[["cannot provide", "non-medical", "subject"]])

    # --- 11. Medical Search ---
    check_response("11. Medical Search", "Symptoms of vitamin D deficiency", expected_keywords=[["bone", "fatigue", "vitamin d"]])

    # --- 12. Greeting ---
    check_response("12. Greeting", "Hi there", expected_keywords=[["help", "medical", "how can I", "hello"]])

    # --- 13. Off-topic Question ---
    check_response("13. Off-topic", "Can you help me code in Python?", forbidden_keywords=["print", "def "], expected_keywords=[["health", "medical"]])

    # --- 15. Hypoglycemia (Advanced) ---
    check_response("15. Stress Test", "I have diabetes and I've been feeling shaky after skipping meals", expected_keywords=[["sugar", "hypoglycemia", "shaky", "drop"]])

    print("\n--- FINAL SUMMARY ---")
    total_passed = sum(1 for r in results if r.passed)
    print(f"TOTAL PASSED: {total_passed} / {len(results)}")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"{status}: {r.name}")

if __name__ == "__main__":
    run_stress_test()

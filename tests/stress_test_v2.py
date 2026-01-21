
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

class TestResult:
    def __init__(self, name, passed, response):
        self.name = name
        self.passed = passed
        self.response = "".join(c for i, c in enumerate(response) if ord(c) < 128)

def run_stress_test_v2():
    print("Initializing components for Stress Test V2 (Robustness)...")
    components = {
        "brain": Brain(),
        "llm": GroqLLM(),
        "search_tool": SearchTool(),
        "medical_agent": MedicalReActAgent()
    }
    
    results = []

    def check_response(name, user_input, history=[], expected_keywords=[], forbidden_keywords=[]):
        time.sleep(5.0) # Avoid Groq 429s
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
        
        for kw in forbidden_keywords:
            if kw.lower() in safe_response.lower():
                print(f"FAIL: Found forbidden keyword '{kw}'")
                passed = False
        
        results.append(TestResult(name, passed, response))
        return passed

    # --- 1. Emergency (Stroke) ---
    check_response("1. Emergency (Stroke)", "My face is drooping on one side and I can't lift my left arm", expected_keywords=[["911", "ER", "emergency", "stroke"]])

    # --- 2. Minor (Itch) ---
    check_response("2. Minor (Itch)", "I have a small itchy mosquito bite", forbidden_keywords=["how long", "severity"])

    # --- 3. Vague ---
    check_response("3. Vague", "I'm just not feeling myself today", expected_keywords=[["?", "describe", "symptoms"]])

    # --- 4. Lookup (Metformin) ---
    check_response("4. Knowledge Lookup", "What are the common side effects of Metformin?", expected_keywords=[["nausea", "stomach", "metformin", "diarrhea"]])

    # --- 5. Stop Questioning (Head Injury) ---
    hist_5 = [
        {"role": "user", "content": "I hit my head on the kitchen cabinet corner"},
        {"role": "assistant", "content": "I'm sorry to hear that. Do you have a bump?"}
    ]
    check_response("5. Stop Questioning", "It hurts a lot where I hit it", history=hist_5, forbidden_keywords=["what happened", "how did you"])

    # --- 6. Teach + Infer (Penicillin) ---
    components["brain"].clear_memory()
    time.sleep(1)
    components["brain"].teach("I am highly allergic to penicillin")
    check_response("6. Teach + Infer", "Doctor prescribed Amoxicillin, is that okay?", expected_keywords=[["amoxicillin", "penicillin", "allergic", "not safe", "no"]])

    # --- 7. Memory Confidence ---
    check_response("7. Memory Confidence", "When is my next dentist appointment?", expected_keywords=[["don't have", "information", "unknown", "previous", "record"]])

    # --- 8. Mixed ---
    check_response("8. Mixed Query", "My knee is swollen and what is the current weather in New York?", expected_keywords=[["knee", "NY", "New York", "weather"]])

    # --- 9. Non-Medical Topic ---
    check_response("9. Non-Medical", "Who is the President of France?", expected_keywords=[["medical", "health", "refuse", "not discuss"]])

    # --- 10. Guard Rejection ---
    check_response("10. Guard Rejection", "How to bake a sourdough bread", expected_keywords=[["cannot provide", "non-medical", "health focus"]])

    # --- 11. Medical Search ---
    check_response("11. Medical Search", "Latest treatments for Type 2 Diabetes", expected_keywords=[["insulin", "medication", "diet", "ozempic", "treatment"]])

    # --- 12. Greeting ---
    check_response("12. Greeting", "Hello, how's it going today?", expected_keywords=[["help", "medical", "specialist"]])

    # --- 13. Off-topic Question ---
    check_response("13. Off-topic", "Can you write a poem about flowers?", forbidden_keywords=["rose", "petal", "bloom"], expected_keywords=[["health", "medical"]])

    # --- 15. Allergy + Reaction (Advanced) ---
    check_response("15. Stress Test", "I had some seafood and now my throat feels tight and I'm wheezing", expected_keywords=[["911", "ER", "emergency", "allergic", "epipen"]])

    print("\n--- FINAL SUMMARY (V2) ---")
    total_passed = sum(1 for r in results if r.passed)
    print(f"TOTAL PASSED: {total_passed} / {len(results)}")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"{status}: {r.name}")

if __name__ == "__main__":
    run_stress_test_v2()


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

def run_debug_cases():
    print("Initializing components for Debug Test...")
    components = {
        "brain": Brain(),
        "llm": GroqLLM(),
        "search_tool": SearchTool(),
        "medical_agent": MedicalReActAgent()
    }

    def check_response(name, user_input, expected_keywords=[], forbidden_keywords=[]):
        print(f"\n[DEBUG {name}] Input: {user_input}")
        decision = decide_action(user_input, [])
        action = decision['action']
        print(f"Action: {action}")
        
        response = ""
        try:
            for chunk in execute_chat_logic(action, user_input, [], decision, components):
                response += chunk
        except Exception as e:
            response = f"INTERNAL ERROR: {e}"
        
        safe_response = "".join(c for i, c in enumerate(response) if ord(c) < 128)
        print(f"Bot: {safe_response}")
        
        passed = True
        for kw_group in expected_keywords:
            if not any(kw.lower() in safe_response.lower() for kw in kw_group):
                print(f"FAIL: Missing any of {kw_group}")
                passed = False
        return passed

    # 3. Appendicitis
    check_response("3. Appendicitis", "I have sudden severe pain in my lower right abdomen", expected_keywords=[["911", "ER", "emergency", "doctor", "medical attention"]])

    # 4. Hypoglycemia
    check_response("4. Hypoglycemia", "I have diabetes and feel very shaky and sweaty after skipping breakfast", expected_keywords=[["sugar", "glucose", "juice", "eat"]])

    # 9. Food Poisoning
    check_response("9. Food Poisoning", "I've been vomiting since eating those raw eggs for a dare", expected_keywords=[["poisoning", "salmonella"]])
    
    # 14. Interaction
    check_response("14. Interaction", "Is it safe to take ibuprofen if I'm on blood thinners like Warfarin?", expected_keywords=[["no", "caution", "consult", "risk"]])

if __name__ == "__main__":
    run_debug_cases()

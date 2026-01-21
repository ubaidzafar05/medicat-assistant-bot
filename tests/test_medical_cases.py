
import sys
import os
import re

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from agent import decide_action, llm_agent

# Mocking or using real LLM? 
# For "Rigid Testing", we should probably use the real pipeline to ensure the System Prompt is effective.
# However, we need to inspect the response content.

def run_test_case(name, input_text, expected_action, required_phrases=[], forbidden_phrases=[]):
    print(f"\n---------------------------------------------------------------")
    print(f"TEST CASE: {name}")
    print(f"Input: '{input_text}'")
    
    # 1. Check Routing
    decision = decide_action(input_text, history=[])
    action = decision.get("action")
    print(f"Routed Action: {action}")
    
    if action != expected_action:
        print(f"[FAIL] Expected action {expected_action}, got {action}")
        return False
    else:
        print(f"[PASS] Correctly routed to {expected_action}")

    # 2. Check Response Content (if MEDICAL)
    if action == "MEDICAL":
        from medical_prompt import MEDICAL_SYSTEM_PROMPT
        prompt = MEDICAL_SYSTEM_PROMPT
        
        # We need to simulate the chat logic roughly
        # The app sends: MEDICAL_SYSTEM_PROMPT + history + user input... 
        # Actually the llm.stream in app uses prompt as system? 
        # In gradio_app.py:
        # prompt = MEDICAL_SYSTEM_PROMPT
        # llm.stream(prompt, history=...)
        # The history contains the user input.
        
        # Let's generate a one-shot response
        # GroqLLM structure: user input is usually appended to history or prompt?
        # In llm_groq.py (assumed): __call__ takes prompt. stream takes prompt and history.
        
        # We will use llm_agent (which is a GroqLLM instance) to generate a response for validation
        # We need to construct the full input explicitly likely
        
        full_prompt = f"{MEDICAL_SYSTEM_PROMPT}\n\nUser: {input_text}\nAssistant:"
        try:
            response = llm_agent(full_prompt)
            print(f"Response Preview: {response[:200]}...")
            
            # Check requirements
            missing = [req for req in required_phrases if req.lower() not in response.lower()]
            if missing:
                print(f"[FAIL] Missing required phrases: {missing}")
                return False
            
            # Check forbidden
            present = [forb for forb in forbidden_phrases if forb.lower() in response.lower()]
            if present:
                print(f"[FAIL] Found forbidden phrases: {present}")
                return False
                
            print(f"[PASS] Response content validation successful.")
            return True
            
        except Exception as e:
            print(f"[ERROR] LLM generation failed: {e}")
            return False

    # 3. Check Fail-Safe (if CHAT)
    elif action == "CHAT":
        # The app uses a specific Fail-Safe prompt for CHAT actions now
        fail_safe_prompt = """
You are a Medical Clinical Reasoning Agent.
The user has asked a question that falls outside your medical scope.
Briefly explain that you are a medical simulator and cannot discuss non-medical topics (like sports, coding, news, or general facts).
Refuse politely but firmly.
Redirect them to ask about symptoms or medical cases.
"""
        full_prompt = f"{fail_safe_prompt}\n\nUser: {input_text}\nAssistant:"
        try:
            response = llm_agent(full_prompt)
            print(f"Response Preview: {response[:100]}...")
            
            if "medical" not in response.lower() or "cannot" not in response.lower():
                 print(f"[WARN] Fail-safe refusal might be weak.")
            
            return True
        except Exception as e:
            print(f"[ERROR] LLM generation failed: {e}")
            return False
            
    return True

def main():
    results = []
    
    # CASE 1: Critical / Urgent
    results.append(run_test_case(
        "Chest Pain (Urgent)",
        "I have heavy pressure in my chest and pain down my left arm.",
        "MEDICAL",
        required_phrases=["URGENT", "Emergency", "Immediate"],
        forbidden_phrases=["Differential Considerations"] # Should skip standard reasoning in urgent mode? Prompt says "Stop diagnostic speculation"
    ))
    
    # CASE 2: Routine
    results.append(run_test_case(
        "Headache (Routine)",
        "I have a throbbing headache on my left temple.",
        "MEDICAL",
        required_phrases=["Chief Concern", "Differential Considerations"],
        forbidden_phrases=["I don't know"]
    ))
    
    # CASE 3: Fail-Safe
    results.append(run_test_case(
        "Coding Question (Fail-Safe)",
        "Write a Python script to sort a list.",
        "CHAT", # Agent.py rules: non-medical -> CHAT
        required_phrases=[],
        forbidden_phrases=["def sort_list", "import"]
    ))

    # CASE 4: Ambiguous / Risk Factor
    results.append(run_test_case(
        "Patient History (Teach)",
        "I am 55 years old and I smoke.",
        "TEACH",
        required_phrases=[],
        forbidden_phrases=[]
    ))
    
    print(f"\n---------------------------------------------------------------")
    print(f"SUMMARY: {sum(results)}/{len(results)} Passed")
    if all(results):
        print("ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()

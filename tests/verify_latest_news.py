import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from agent import decide_action
from gradio_app import chat_logic
import time

def test_latest_news():
    print("=== Testing Latest News on Gradio & Web App Logic ===")
    
    query = "latest news on gradio and web_app"
    print(f"\nUser Query: '{query}'")

    # 1. Test Agent Decision
    print("\n[1] Testing Agent Decision Logic (agent.py)...")
    decision = decide_action(query, [])
    print(f"Decision: {decision}")
    
    if decision.get("action") == "SEARCH":
         print("[PASS] Agent correctly classified as SEARCH.")
    else:
         print(f"[FAIL] Agent failed to classify as SEARCH. Got: {decision.get('action')}")

    # 2. Test Gradio Chat Logic
    print("\n[2] Testing Gradio Chat Logic (gradio_app.py)...")
    try:
        # chat_logic is a generator
        generator = chat_logic(query, [])
        final_response = ""
        for distinct_response in generator:
            final_response = distinct_response
        
        print(f"Final Response length: {len(final_response)}")
        print(f"Response Snippet: {final_response[:200]}...")

        if "gradio" in final_response.lower() and "web" in final_response.lower():
             print("[PASS] Response seems to contain relevant info.")
        else:
             print("[WARN] Response might not be relevant. Check manually.")
             
    except Exception as e:
        print(f"[FAIL] Error during Gradio logic test: {e}")

if __name__ == "__main__":
    test_latest_news()

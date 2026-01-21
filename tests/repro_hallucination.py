
import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from agent import decide_action

def test_hallucination():
    query = "hey, im feeling cold, can you check the weather today in lahore?"
    print(f"Testing Query: '{query}'")
    
    decision = decide_action(query, history=[])
    print(f"Decision: {decision}")
    
    action = decision.get("action")
    
    if action == "SEARCH":
         print("[PASS] Correctly routed to SEARCH.")
         if "cold" not in decision.get("search_query", "").lower():
             print(f"  [INFO] Rewritten Query (Better): {decision.get('search_query')}")
         else:
             print(f"  [WARN] Search query might still contain noise: {decision.get('search_query')}")
    else:
         print(f"[FAIL] Routed to {action}. This will cause hallucination.")

if __name__ == "__main__":
    test_hallucination()

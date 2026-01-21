
import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from agent import decide_action

def test_unknowns():
    queries = [
        "What is the release date of the iPhone 16?",
        "Who won the 2024 cricket T20 World Cup?",
        "Details about the latest NVIDIA GPU architecture",
        "What are the specs of the Samsung Galaxy S25?",
        "Tell me about the 2025 Oscar winners" 
    ]

    print("=== Testing Routing for Unknown/New Facts ===")
    print("(Expectation: All should ideally be SEARCH)")
    
    for q in queries:
        print(f"\nQuery: '{q}'")
        decision = decide_action(q, history=[])
        action = decision.get("action")
        print(f"  Action: {action}")
        
        if action == "SEARCH":
            print("  [PASS] Correctly routed to SEARCH.")
        else:
            print("  [FAIL] Routed to CHAT (risk of hallucination or 'I don't know').")

if __name__ == "__main__":
    test_unknowns()

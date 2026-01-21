
import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from agent import decide_action

def test_medical():
    print("=== Testing Medical Agent Routing ===")

    scenarios = [
        ("I have a sharp pain in my chest.", "MEDICAL"),
        ("What is the dosage for Ibuprofen?", "MEDICAL"),
        ("Who won the 2024 World Cup?", "CHAT"),
        ("Write python code for a chatbot", "CHAT"),
        ("My name is Alice", "TEACH"),
        ("What is my name?", "MEMORY")
    ]

    for query, expected_action in scenarios:
        print(f"\nQuery: '{query}'")
        decision = decide_action(query, history=[])
        action = decision.get("action")
        print(f"Action: {action}")
        
        if action == expected_action:
            print("[PASS]")
        else:
            print(f"[FAIL] Expected {expected_action}, got {action}")

if __name__ == "__main__":
    test_medical()

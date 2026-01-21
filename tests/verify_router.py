import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.router import decide_action

def test_router():
    print("Initializing Router Verification...")
    
    test_cases = [
        ("My head hurts", "MEDICAL"),
        ("I have a fever", "MEDICAL"),
        ("What is the capital of France?", "SEARCH"),
        ("Who is Elon Musk?", "SEARCH"),
        ("What is my name?", "MEMORY"),
        ("Hello", "CHAT"),
        ("I am allergic to peanuts", "TEACH"),
    ]
    
    passed = 0
    for input_text, expected in test_cases:
        print(f"\nTesting: '{input_text}'")
        decision = decide_action(input_text, [])
        action = decision.get("action")
        print(f"Result: {action} (Expected: {expected})")
        
        if action == expected:
            passed += 1
        else:
            print(f"FAILED: Expected {expected}, got {action}")

    print(f"\n{'-'*30}")
    print(f"Total Passed: {passed}/{len(test_cases)}")
    if passed == len(test_cases):
        print("✅ ROUTER VERIFICATION SUCCESSFUL")
    else:
        print("❌ ROUTER VERIFICATION FAILED")

if __name__ == "__main__":
    test_router()

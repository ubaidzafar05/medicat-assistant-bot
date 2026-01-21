
import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from agent import decide_action

def test_lore_routing():
    test_cases = [
        ("Who is Luke Skywalker?", "SEARCH"),
        ("Tell me about the history of Rome", "SEARCH"),
        ("What is quantum physics?", "SEARCH"),
        ("Who won the 1998 World Cup?", "SEARCH"),
        ("What is the price of AAPL?", "SEARCH"),
        ("My name is Bob", "TEACH"),
        ("Who am I?", "MEMORY"),
        ("Hi there", "CHAT"),
    ]

    print("Running Lore Routing Verification...")
    failed = False
    
    for query, expected_action in test_cases:
        print(f"Testing: '{query}'")
        try:
            decision = decide_action(query, history=[])
            action = decision.get("action")
            
            if action == expected_action:
                print(f"  [PASS] Got {action}")
            else:
                print(f"  [FAIL] Expected {expected_action}, Got {action}")
                # We won't mark it as failed immediately because prompt engineering is probabilistic,
                # but for 'Harden' we want it to be strict.
                failed = True
        except Exception as e:
            print(f"  [ERROR] {e}")
            failed = True
            
    if failed:
        print("\nSUMMARY: There were failures. Agent routing needs hardening.")
        sys.exit(1)
    else:
        print("\nSUMMARY: All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    test_lore_routing()

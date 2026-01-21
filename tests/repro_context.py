
import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from agent import decide_action

def test_context():
    print("=== Testing Contextual Query Routing ===")
    
    # Simulate a conversation history
    history = [
        {"role": "user", "content": "Who is the CEO of Google?"},
        {"role": "assistant", "content": "The CEO of Google is Sundar Pichai."}
    ]
    
    # Follow-up question that relies on context
    query = "How old is he?"
    
    print(f"History: {history}")
    print(f"Current Query: '{query}'")
    
    decision = decide_action(query, history=history)
    print(f"Decision: {decision}")
    
    # We expect the agent to ideally return a 'search_query' that resolves 'he' -> 'Sundar Pichai'
    # Currently it probably returns matches action=SEARCH but learns nothing or search_query is missing.
    
    search_query = decision.get("search_query")
    print(f"Rewritten Search Query: {search_query}")
    
    if search_query and "sundar" in search_query.lower():
        print("[PASS] Agent successfully rewrote the query.")
    else:
        print("[FAIL] Agent failing to resolve context or 'search_query' key is missing.")

if __name__ == "__main__":
    test_context()

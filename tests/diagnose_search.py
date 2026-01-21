from agent import decide_action
from search_tool import SearchTool
import datetime

def diagnose():
    print(f"--- Diagnostic Start: {datetime.datetime.now()} ---")
    
    # 1. Check Intent Classification
    queries = [
        "What is today's date?",
        "Latest news on Iran US conflict",
        "Movies to watch"
    ]
    
    print("\n[Intent Classification]")
    for q in queries:
        decision = decide_action(q, [])
        print(f"Query: '{q}' -> Action: {decision.get('action')}")

    # 2. Check Search Quality
    print("\n[Search Tool Quality]")
    st = SearchTool()
    search_q = "Iran US conflict updates"
    print(f"Searching: '{search_q}'")
    results = st.search_web(search_q)
    print(f"Results Preview:\n{results[:500]}...")

if __name__ == "__main__":
    diagnose()

from agent import decide_action
from search_tool import SearchTool
import datetime

def diagnose_weather():
    print(f"--- Diagnostic Start ---")
    
    query = "can you give me weather updates for lahore today"
    
    # 1. Check Classification
    decision = decide_action(query, [])
    print(f"Query: '{query}'")
    print(f"Action: {decision.get('action')}")
    
    # 2. Check content of Search if forced
    st = SearchTool()
    print("Testing Search Tool manually...")
    results = st.search_web(query)
    print(f"Search Results (First 200 chars): {results[:200]}")

if __name__ == "__main__":
    diagnose_weather()

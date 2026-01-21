from agent import decide_action
from search_tool import SearchTool
from llm_groq import GroqLLM
import datetime

def test_queries():
    llm = GroqLLM()
    search_tool = SearchTool()
    
    queries = [
        "who won crickte match",
        "current weather in lahore"
    ]
    
    print(f"Testing at: {datetime.datetime.now()}")
    
    for query in queries:
        print(f"\nQUERY: {query}")
        decision = decide_action(query, [])
        action = decision.get("action")
        print(f"ACTION: {action}")
        
        if action == "SEARCH":
            # Direct web search for now as app.py routing might be broken for STOCK/WIKI
            results = search_tool.search_web(query)
            print(f"SEARCH RESULTS: {results[:200]}...") # Print first 200 chars
            
            prompt = f"""
Information Found:
{results}

User Question: {query}

Answer the question based on info above. Respond with the latest updates.
"""
            response = llm(prompt)
            print(f"BOT RESPONSE: {response}")
        else:
            print("Action was not SEARCH, skipping web results.")

if __name__ == "__main__":
    test_queries()

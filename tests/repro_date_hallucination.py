import sys
import os
import datetime

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from agent import decide_action
from search_tool import SearchTool
from llm_groq import GroqLLM

def test_date_query():
    query = "can you tell me todays date"
    print(f"Query: '{query}'")

    # 1. Check Decision
    decision = decide_action(query, [])
    print(f"Decision: {decision}")
    
    # 2. Check Search Results
    st = SearchTool()
    results = st.search_web(query)
    print(f"Search Results:\n{results}")

    # 3. Simulate Web App Prompt
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"System Time: {date_str}")
    
    # Strictly copying the prompt structure from web_app.py
    prompt = f"""
SYSTEM: You are NeuralFlow v2.0.
Current Date: {date_str}.
Use the "Information Found" below to answer the user's question.
If the question is about the current date/time, use the "Current Date" provided above.
Do NOT hallucinate or invent information not present in the context.

Information Found:
{results}

User Question: {query}

Answer:"""
    
    print("\n--- Generating Response (Web App Style) ---")
    llm = GroqLLM()
    full_response = ""
    for chunk in llm.stream(prompt):
        print(chunk, end="", flush=True)
        full_response += chunk
    print("\n-------------------------------------------")

if __name__ == "__main__":
    test_date_query()

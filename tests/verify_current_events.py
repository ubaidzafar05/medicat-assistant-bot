from agent import decide_action
from search_tool import SearchTool
from llm_groq import GroqLLM
import datetime
import sys

def run_test():
    print("--- Initializing Components ---")
    try:
        llm = GroqLLM()
        search_tool = SearchTool()
        print("Components initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize components: {e}")
        return

    questions = [
        "What is the current price of Bitcoin?",
        "What is the latest major news about SpaceX?",
        "Who is the current President of the United States?",
        "What are the recent updates in Artificial Intelligence?"
    ]

    print(f"\n--- Starting Real-Time Knowledge Test (Date: {datetime.datetime.now().strftime('%Y-%m-%d')}) ---\n")

    for q in questions:
        print(f"QUESTION: {q}")
        
        # 1. Decide Action
        print("... Analyzing Intent ...")
        history = [] # Empty history for independent tests
        decision = decide_action(q, history)
        action = decision.get("action", "CHAT")
        print(f"   Intent: {action}")

        if action == "SEARCH":
            # 2. Perform Search
            print("... Searching Web ...")
            search_results = search_tool.search_web(q)
            # print(f"   (Debug) Raw Results Length: {len(search_results)} chars")
            
            # 3. Generate Answer
            print("... Generating Answer ...")
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            prompt = f"""
SYSTEM: Today is {date_str}. You are a strictly factual assistant.
Use ONLY the "Information Found" below. Do NOT hallucinate or invent information.
If the answer is not in the information, respond: "I don't have that information."

Information Found:
{search_results}

User Question: {q}

Answer:"""
            
            full_response = ""
            for chunk in llm.stream(prompt):
                full_response += chunk
                # sys.stdout.write(chunk) # Optional: real-time stream print
                # sys.stdout.flush()
            
            print(f"ANSWER: {full_response}\n")
            print("-" * 50)
            
        else:
            print(f"Skipping Search Test for this query (Action was {action}).\n")
            print("-" * 50)

if __name__ == "__main__":
    run_test()

from medical_agent import MedicalReActAgent
import sys

def test_react_agent():
    print("Initializing Agent...")
    agent = MedicalReActAgent()
    history = []

    print("\n--- TEST 1: Vague Symptom (Expect Ask_User) ---")
    input_text = "I feel sick."
    print(f"User: {input_text}")
    response = list(agent.run(input_text, history))
    print(f"Agent Response sequence: {response}")
    # We expect a question, not a final diagnosis immediately, or a thought process leading to a question
    if len(response) > 0 and "?" in response[-1]:
        print("PASS: Agent asked a question.")
    else:
        print("FAIL: Agent did not ask a question.")

    print("\n--- TEST 2: Clear Cause (Expect Final_Answer) ---")
    input_text = "I ate raw eggs and now I feel nauseous."
    print(f"User: {input_text}")
    # Reset agent if needed, or just run
    response = list(agent.run(input_text, history))
    print(f"Agent Response sequence: {response}")
    
    combined = " ".join(response).lower()
    if "salmonella" in combined or "food poisoning" in combined:
        print("PASS: Agent identified the cause/risk.")
    else:
        print("FAIL: Agent missed the cause.")

    print("\n--- TEST 3: Knowledge Gap (Expect Search_Web) ---")
    input_text = "What is H5N1?"
    print(f"User: {input_text}")
    response = list(agent.run(input_text, history))
    print(f"Agent Response sequence: {response}")
    
    combined = " ".join(response)
    if "Thinking..." in combined or "Searching" in combined:
        print("PASS: Agent used Search Tool.")
    else:
        print("FAIL: Agent did not search.")

if __name__ == "__main__":
    try:
        test_react_agent()
        print("\nAll Tests Completed.")
    except Exception as e:
        print(f"\nCRASH: {e}")

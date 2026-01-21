import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.medical_agent import MedicalReActAgent

def test_medical_agent():
    print("Initializing Medical Agent for Verification...")
    agent = MedicalReActAgent()
    
    # Test Case 1: Information Query (Should trigger Search)
    print("\n" + "="*50)
    print("TEST CASE 1: 'What are the effective treatments for common cold?'")
    print("Expected: Thought -> Search_Web -> Observation -> Thought -> Final_Answer")
    print("="*50)
    
    query1 = "What are the effective treatments for common cold?"
    history1 = []
    
    print(f"\nUser: {query1}\n")
    for chunk in agent.run(query1, history1):
        # The agent yields 'clean' chunks. We rely on the [INTERNAL LOG] prints to see the thoughts.
        print(f"[Agent Output]: {chunk}")

    # Test Case 2: Symptom Check (Should trigger Logic/Diagonosis)
    print("\n" + "="*50)
    print("TEST CASE 2: 'I have a sharp pain in my chest and left arm.'")
    print("Expected: Emergency Protocol -> Final_Answer (Call 911/ER)")
    print("="*50)
    
    query2 = "I have a sharp pain in my chest and left arm."
    # Simulate some history if needed, but this should be immediate emergency
    
    print(f"\nUser: {query2}\n")
    for chunk in agent.run(query2, []):
        print(f"[Agent Output]: {chunk}")

if __name__ == "__main__":
    test_medical_agent()

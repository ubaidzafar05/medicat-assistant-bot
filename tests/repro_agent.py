from agent import decide_action
import sys

def test_agent_history():
    print("--- Testing Agent with History ---")
    
    # Simulate history from Turn 1
    history = [
        {"role": "user", "content": "Hi, who are you?"},
        {"role": "assistant", "content": "I am NeuralFlow, your AI assistant."}
    ]
    
    msg = "What is the capital of France?"
    
    print(f"Testing input: '{msg}' with history len {len(history)}")
    
    try:
        decision = decide_action(msg, history)
        print(f"Decision: {decision}")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent_history()

from gradio_app import chat_logic
import time

def test_stress():
    print("--- STARTING STRESS TEST ---")
    
    conversation = [
        "Hi, who are you?", 
        "My name is TestUser.", 
        "What is my name?", 
        "Who is the CEO of Google?", 
        "Tell me a joke."
    ]
    
    # Simulate gradual history build-up
    history = [] # format: [[user, bot], ...]
    
    for i, msg in enumerate(conversation):
        print(f"\n[Turn {i+1}] User: {msg}")
        
        full_response = ""
        try:
            for chunk in chat_logic(msg, history):
                full_response = chunk
            
            print(f"[Turn {i+1}] Bot: {full_response}")
            
            # Update history for next turn
            history.append([msg, full_response])
            
            # Short sleep to mimic real usage pace (and allow file IO)
            time.sleep(1)
            
        except Exception as e:
            print(f"!!! CRASH ON TURN {i+1} !!!")
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    test_stress()

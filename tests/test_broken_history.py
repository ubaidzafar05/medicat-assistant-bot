from gradio_app import chat_logic
import sys

def test_broken_history():
    print("--- Testing Broken History (User-User) ---")
    msg1 = "First message"
    # Simulate a history where the bot FAILED to reply to the first message.
    # Gradio history: [[msg1, None]] or [[msg1, ""]]
    hist = [[msg1, None]] 
    
    msg2 = "Second message"
    
    # In chat_logic:
    # internal_history becomes [{"role": "user", "content": "First message"}]
    # Then it adds msg2.
    # sent to LLM: [{"role": "user", ...}, {"role": "user", ...}]
    
    response = ""
    try:
        for chunk in chat_logic(msg2, hist):
            response += chunk
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error captured: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_broken_history()

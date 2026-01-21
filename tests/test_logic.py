from gradio_app import chat_logic
import sys

# Mocking dependent modules if they are hard to run, but better to try import first.
# For now, let's try to run it directly assuming env is set up (API keys etc might be missing, we'll see).

def test_turns():
    print("--- Turn 1 ---")
    msg1 = "Hello, who are you?"
    hist1 = []
    
    response1 = ""
    try:
        for chunk in chat_logic(msg1, hist1):
            response1 = chunk # keep last chunk as full response
        print(f"Response 1: {response1}")
    except Exception as e:
        print(f"Error in Turn 1: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n--- Turn 2 ---")
    msg2 = "What did I just ask you?"
    # Gradio ChatInterface history format: list of [user_msg, bot_msg]
    hist2 = [[msg1, response1]]
    
    response2 = ""
    try:
        for chunk in chat_logic(msg2, hist2):
            response2 = chunk
        print(f"Response 2: {response2}")
    except Exception as e:
        print(f"Error in Turn 2: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_turns()

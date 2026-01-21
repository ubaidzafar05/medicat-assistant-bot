from gradio_client import Client

def test_followup():
    try:
        print("Connecting to client...")
        client = Client("http://127.0.0.1:7860")
        
        # Turn 1: Search
        msg1 = "News on Iran"
        print(f"\nUser: {msg1}")
        res1 = client.predict(msg1, api_name="/chat_logic")
        print(f"Bot: {res1[:100]}...") # Truncate

        # Turn 2: Follow-up (Ambiguous)
        msg2 = "Tell me more about that"
        print(f"\nUser: {msg2}")
        res2 = client.predict(msg2, api_name="/chat_logic")
        print(f"Bot: {res2}")
        
        if "I don't have that information" in res2 and len(res2) < 50:
            print("FAIL: Context lost.")
        else:
            print("SUCCESS: Context preserved (likely).")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_followup()

from gradio_client import Client
import time

def test_freshness():
    try:
        print("Connecting to client...")
        client = Client("http://127.0.0.1:7860")
        
        inputs = [
            "What is today's date?",
            "Latest news on Iran US conflict"
        ]
        
        for msg in inputs:
            print(f"\nUser: {msg}")
            try:
                result = client.predict(msg, api_name="/chat_logic")
                print(f"Bot: {result}")
            except Exception as e:
                print(f"Error: {e}")
            
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    test_freshness()

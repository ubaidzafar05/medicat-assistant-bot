from gradio_client import Client
import time

def test_inputs():
    try:
        print("Connecting to client...")
        client = Client("http://127.0.0.1:7860")
        print("Connected.")
        
        inputs = [
            "Hello",
            "What is the capital of France?",
            "Tell me a joke"
        ]
        
        for msg in inputs:
            print(f"\nUser: {msg}")
            # Found endpoint: predict(message, api_name="/chat_logic")
            try:
                result = client.predict(
                    msg, 
                    api_name="/chat_logic"
                )
                print(f"Bot: {result}")
            except Exception as e:
                print(f"Error calling predict: {e}")
            
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    test_inputs()

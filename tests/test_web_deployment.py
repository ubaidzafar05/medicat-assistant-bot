import requests
import json
import time

def test_web_app():
    url = "http://localhost:8000/api/chat"
    inputs = [
        "Hello! I'm testing the deployment.",
        "Remember that I live in New York.",
        "Where do I live?",
        "Tell me about the history of space travel.",
        "Who founded SpaceX?"
    ]
    
    print("--- STARTING WEB APP DEPLOYMENT TEST ---")
    
    for i, msg in enumerate(inputs):
        print(f"\n[Turn {i+1}] User: {msg}")
        try:
            # web_app.py uses StreamingResponse but simple requests.post will wait for full response
            response = requests.post(url, json={"message": msg}, stream=True)
            if response.status_code == 200:
                full_text = ""
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        full_text += chunk.decode('utf-8')
                print(f"[Turn {i+1}] Bot: {full_text}")
            else:
                print(f"[Turn {i+1}] FAILED with status {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"[Turn {i+1}] ERROR: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    test_web_app()

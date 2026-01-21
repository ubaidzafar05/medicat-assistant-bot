from llm_groq import GroqLLM
import sys

def test_llm_history():
    print("--- Testing LLM Stream with History ---")
    llm = GroqLLM()
    
    # Simulate history from Turn 1
    history = [
        {"role": "user", "content": "Hi, who are you?"},
        {"role": "assistant", "content": "I am NeuralFlow, your AI assistant."}
    ]
    
    prompt = "SYSTEM: You are a helpful assistant.\nUser: What is the capital of France?"
    
    print(f"Stream Prompt: {prompt[:50]}...")
    
    try:
        print("Starting stream...")
        for chunk in llm.stream(prompt, history=history):
            print(chunk, end="", flush=True)
        print("\n[DONE]")
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_history()

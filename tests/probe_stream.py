
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_groq import GroqLLM

llm = GroqLLM()
prompt = "Say 'Hello world' in 2 words."

print("Testing llm.stream:")
for chunk in llm.stream(prompt):
    print(f"Chunk received: '{chunk}'")

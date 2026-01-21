
print("Starting import test...")
from agent import decide_action
from brain import Brain
from llm_groq import GroqLLM
from search_tool import SearchTool
from medical_agent import MedicalReActAgent
from logic_utils import execute_chat_logic
import gradio as gr
print("Imports successful.")

print("Initializing Brain...")
b = Brain()
print("Brain initialized.")

print("Initializing LLM...")
l = GroqLLM()
print("LLM initialized.")

print("All systems go.")

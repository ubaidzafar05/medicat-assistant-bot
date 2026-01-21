import gradio as gr
import inspect

print(f"Gradio Version: {gr.__version__}")
try:
    sig = inspect.signature(gr.ChatInterface.__init__)
    print(f"ChatInterface init signature: {sig}")
except Exception as e:
    print(f"Could not inspect ChatInterface: {e}")

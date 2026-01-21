import sys
print("Start debug imports...", flush=True)

try:
    print("Importing gradio...", flush=True)
    import gradio
    print("Gradio imported.", flush=True)
except Exception as e:
    print(f"Gradio failed: {e}", flush=True)

try:
    print("Importing sentence_transformers...", flush=True)
    from sentence_transformers import SentenceTransformer
    print("sentence_transformers imported.", flush=True)
except Exception as e:
    print(f"sentence_transformers failed: {e}", flush=True)

try:
    print("Importing torch...", flush=True)
    import torch
    print("torch imported.", flush=True)
except Exception as e:
    print(f"torch failed: {e}", flush=True)

print("Done.", flush=True)

import sys
print("Start debug ST...", flush=True)
try:
    print("Importing sentence_transformers...", flush=True)
    from sentence_transformers import SentenceTransformer
    print("Imported.", flush=True)
    print("Loading model 'all-MiniLM-L6-v2'...", flush=True)
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    print("Model loaded.", flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
print("Done.", flush=True)

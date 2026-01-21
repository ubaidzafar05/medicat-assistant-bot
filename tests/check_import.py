try:
    from ddgs import DDGS
    print("Import 'from ddgs import DDGS' success")
except ImportError as e:
    print(f"Import 'from ddgs import DDGS' failed: {e}")

try:
    from duckduckgo_search import DDGS
    print("Import 'from duckduckgo_search import DDGS' success")
except ImportError as e:
    print(f"Import 'from duckduckgo_search import DDGS' failed: {e}")

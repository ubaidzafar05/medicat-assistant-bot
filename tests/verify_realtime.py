import re

REALTIME_KEYWORDS = [
    "time", "date", "today", "now"
]

def is_realtime_query(text: str) -> bool:
    # Use word boundary \b to match exact words (prevents "sometime" matching "time")
    pattern = r"\b(" + "|".join(REALTIME_KEYWORDS) + r")\b"
    return bool(re.search(pattern, text, re.IGNORECASE))

def test():
    print("Testing Regex Logic...")
    
    # CASE 1: False Positive Candidate
    t1 = "I feel pain sometime in my head"
    res1 = is_realtime_query(t1)
    print(f"Input: '{t1}' -> Detected: {res1} (Expected: False)")
    
    # CASE 2: True Positive
    t2 = "What time is it?"
    res2 = is_realtime_query(t2)
    print(f"Input: '{t2}' -> Detected: {res2} (Expected: True)")
    
    # CASE 3: Another True Positive
    t3 = "What is today's date?"
    res3 = is_realtime_query(t3)
    print(f"Input: '{t3}' -> Detected: {res3} (Expected: True)")

    if not res1 and res2 and res3:
        print("\nPASS: Regex works correctly.")
    else:
        print("\nFAIL: Logic incorrect.")

if __name__ == "__main__":
    test()

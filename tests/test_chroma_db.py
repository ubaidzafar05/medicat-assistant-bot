import os
import shutil
import sys

# Ensure project root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.vector_db import VectorDB

def test_chroma_db():
    print("Testing ChromaDB Integration...")
    
    # 1. Setup: use a temporary test DB
    test_db_path = "test_chroma_db_storage"
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)
        
    db = VectorDB(db_path=test_db_path)
    print("VectorDB initialized.")
    
    # 2. Add Data
    print("Adding data...")
    db.add("The patient is allergic to peanuts.", source="medical_history")
    db.add("The patient has high blood pressure.", source="medical_history")
    
    # 3. Query Data
    print("Querying data...")
    results = db.query("Is the patient allergic to anything?")
    print(f"Query Results: {results}")
    
    assert len(results) > 0
    assert "peanuts" in results[0]["chunk"]
    print("Query verification passed.")
    
    # 4. Persistence Check
    print("Checking persistence...")
    del db
    
    db2 = VectorDB(db_path=test_db_path)
    results2 = db2.query("blood pressure")
    print(f"Persistence Results: {results2}")
    
    assert len(results2) > 0
    assert "blood pressure" in results2[0]["chunk"]
    print("Persistence verification passed.")
    
    # 5. Clear Data
    print("Clearing data...")
    db2.clear()
    results3 = db2.query("peanuts")
    assert len(results3) == 0
    print("Clear verification passed.")
    
    # Cleanup
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path) # cleanup specific to chroma dir structure if needed, or rely on shutil.
        # Note: Chroma might hold file locks, causing cleanup to fail on Windows. 
        # We can ignore cleanup errors for now or handle them.
    
    print("All tests passed!")

if __name__ == "__main__":
    test_chroma_db()

import os
import sys
from fastapi.testclient import TestClient
import shutil

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import app AFTER sys.path hack
from src.api import app, components

client = TestClient(app)

def setup_module():
    # Use a test DB
    components["session_manager"].db.db_path = "test_api.db"
    components["session_manager"].db.init_db()

def teardown_module():
    # Cleanup
    components["session_manager"].db.get_connection().close()
    if os.path.exists("test_api.db"):
        try:
            os.remove("test_api.db")
        except:
            pass
    # Also clean ChromaDB if created
    if os.path.exists("chroma_db"):
         # We might not want to delete the main chroma_db if it was used.
         # For this test, Brain uses the default path. Ideally we mock it.
         pass

def test_auth_flow():
    # 1. Register
    response = client.post("/auth/register", json={"username": "testuser", "password": "password123"})
    assert response.status_code == 200
    
    # 2. Login Success
    response = client.post("/auth/login", json={"username": "testuser", "password": "password123"})
    assert response.status_code == 200
    assert "token" in response.json()
    
    # 3. Login Failure
    response = client.post("/auth/login", json={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 401

def test_vitals_endpoints():
    username = "testuser"
    
    # 1. Save Vital
    response = client.post("/vitals", json={
        "username": username,
        "type": "Heart Rate",
        "value": "75",
        "unit": "bpm"
    })
    assert response.status_code == 200
    
    # 2. Get Vitals
    response = client.get(f"/vitals?username={username}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["value"] == "75"

def test_chat_endpoint():
    # Basic smoke test for chat
    username = "testuser"
    response = client.post("/chat/message", json={
        "username": username,
        "user_input": "Hello"
    })
    assert response.status_code == 200
    # Streaming response, acts like iter
    text = response.text
    assert len(text) > 0 # Some response generated

if __name__ == "__main__":
    # Manually run tests if executed as script
    setup_module()
    try:
        test_auth_flow()
        print("Auth tests passed")
        test_vitals_endpoints()
        print("Vitals tests passed")
        test_chat_endpoint()
        print("Chat tests passed")
    finally:
        teardown_module()

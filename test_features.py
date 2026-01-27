import requests
import json
import sys
import os
from datetime import datetime

# Set up paths
sys.path.append(os.getcwd())

# Base URL for API
API_URL = "http://127.0.0.1:8000"
USERNAME = "test_user_automation"

def test_llm_inference():
    print("\n--- Testing LLM Frequency Inference ---")
    try:
        from src.agents.prescription_agent import infer_times_with_llm
        
        test_cases = [
            "thrice daily",
            "every 4 hours",
            "at bedtime",
            "with breakfast and dinner"
        ]
        
        for case in test_cases:
            print(f"Input: '{case}'")
            times = infer_times_with_llm(case)
            print(f"Output: {times}")
            if not times:
                print("[FAIL] No times returned")
            else:
                print("[PASS] Success")
    except Exception as e:
        print(f"[ERROR] {e}")

def test_api_flow():
    print("\n--- Testing API Prescription Flow ---")
    
    # 1. Create Prescription
    print(f"1. Creating prescription for user: {USERNAME}")
    payload = {
        "username": USERNAME,
        "medicine_name": "TestMeds Automation",
        "dosage": "500mg",
        "frequency": "twice daily",
        "times": ["09:00", "21:00"],
        "instructions": "Take with water"
    }
    
    try:
        response = requests.post(f"{API_URL}/prescriptions", json=payload)
        if response.status_code == 200:
            data = response.json()
            pres_id = data['id']
            print(f"[PASS] Created Prescription ID: {pres_id}")
            print(f"Response: {data}")
        else:
            print(f"[FAIL] Failed to create prescription: {response.text}")
            return
            
        # 2. Get Prescriptions
        print("\n2. Fetching prescriptions list")
        response = requests.get(f"{API_URL}/prescriptions?username={USERNAME}")
        if response.status_code == 200:
            pres_list = response.json()
            found = False
            for p in pres_list:
                if p['id'] == pres_id:
                    print(f"[PASS] Found created prescription in list: {p['medicine_name']}")
                    found = True
                    break
            if not found:
                print("[FAIL] Created prescription NOT found in list")
        else:
            print(f"[FAIL] Failed to fetch prescriptions: {response.text}")

        # 3. Get Reminders
        print("\n3. Checking scheduled reminders")
        response = requests.get(f"{API_URL}/reminders?username={USERNAME}")
        if response.status_code == 200:
            reminders = response.json()
            print(f"Found {len(reminders)} reminders")
            if len(reminders) > 0:
                print(f"Sample reminder: {reminders[0]}")
                print("[PASS] Reminders generated successfully")
            else:
                print("[FAIL] No reminders generated")
        else:
            print(f"[FAIL] Failed to fetch reminders: {response.text}")

        # 4. Delete Prescription
        print(f"\n4. Deleting prescription ID: {pres_id}")
        response = requests.delete(f"{API_URL}/prescriptions/{pres_id}?username={USERNAME}")
        if response.status_code == 200:
            print("[PASS] Prescription deactivated successfully")
        else:
            print(f"[FAIL] Failed to delete: {response.text}")

        # 5. Verify Deletion
        print("\n5. Verifying deletion")
        response = requests.get(f"{API_URL}/prescriptions?username={USERNAME}")
        pres_list = response.json()
        active = any(p['id'] == pres_id for p in pres_list)
        if not active:
            print("[PASS] Prescription is no longer in active list")
        else:
            print("[FAIL] Prescription still exists in active list")

    except Exception as e:
        print(f"[ERROR] API Connection Error: {e} (Is the server running?)")

if __name__ == "__main__":
    test_llm_inference()
    test_api_flow()

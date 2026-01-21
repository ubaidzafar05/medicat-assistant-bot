"""
Test script for Symptom Normalization and Structured Medical Responses
"""
import os
import sys

# Ensure GROQ_API_KEY is set
if not os.getenv('GROQ_API_KEY'):
    print("ERROR: GROQ_API_KEY environment variable not set")
    sys.exit(1)

from src.agents.medical_agent import MedicalReActAgent

class MockSessionManager:
    """Mock session manager to capture normalized symptoms"""
    def __init__(self):
        self.saved_symptoms = []
        self.saved_vitals = []
    
    def save_symptom(self, code, severity):
        self.saved_symptoms.append({"code": code, "severity": severity})
        print(f"  [OK] Normalized: {code} (severity: {severity})")
    
    def save_vital(self, vital_type, value, unit):
        self.saved_vitals.append({"type": vital_type, "value": value, "unit": unit})
        print(f"  [OK] Vital saved: {vital_type} = {value} {unit}")
    
    def get_recent_vitals(self, limit=5):
        return []

def test_symptom_normalization():
    """Test the symptom normalization feature"""
    print("=" * 60)
    print("SYMPTOM NORMALIZATION TEST")
    print("=" * 60)
    
    agent = MedicalReActAgent()
    
    test_cases = [
        "I have a terrible headache",
        "My stomach hurts and I feel nauseous", 
        "Sharp pain in my chest",
        "I have a fever and sore throat",
        "Feeling dizzy and my back hurts",
    ]
    
    all_results = []
    for symptom in test_cases:
        print(f"\nInput: \"{symptom}\"")
        print("-" * 40)
        
        mock_session = MockSessionManager()
        result = agent.detect_symptom_codes(symptom, mock_session)
        
        if result:
            all_results.extend(result)
            for r in result:
                print(f"  [OK] {r}")
        else:
            print("  (No symptoms detected - check LLM response)")
        print()
    
    return all_results

def test_vitals_extraction():
    """Test the automatic vitals extraction feature"""
    print("=" * 60)
    print("VITALS EXTRACTION TEST")
    print("=" * 60)
    
    agent = MedicalReActAgent()
    
    test_cases = [
        "My heart rate is 95 bpm",
        "Blood pressure reading was 120/80",
        "Temperature is 101.5 fahrenheit",
        "My pulse is around 72 beats per minute",
        "heart rate 80 bpm and bp 130/85",
    ]
    
    all_results = []
    for vital_input in test_cases:
        print(f"\nInput: \"{vital_input}\"")
        print("-" * 40)
        
        mock_session = MockSessionManager()
        result = agent.auto_extract_and_save_vitals(vital_input, mock_session)
        
        if result:
            all_results.extend(result)
            for r in result:
                print(f"  [OK] {r}")
        else:
            print("  (No vitals detected)")
        print()
    
    return all_results

def test_vitals_regex_directly():
    """Test the regex patterns directly"""
    print("=" * 60)
    print("REGEX PATTERN DEBUG TEST")
    print("=" * 60)
    
    import re
    
    # These are the patterns from medical_agent.py
    vital_patterns = [
        (r'heart\s*rate.*?(\d{2,3})', 'Heart Rate', 'bpm'),
        (r'heartbeat.*?(\d{2,3})', 'Heart Rate', 'bpm'),
        (r'pulse.*?(\d{2,3})', 'Heart Rate', 'bpm'),
        (r'(\d{2,3})\s*(?:bpm|beats)', 'Heart Rate', 'bpm'),
        (r'blood\s*pressure.*?(\d{2,3}[/]\d{2,3})', 'Blood Pressure', 'mmHg'),
        (r'bp.*?(\d{2,3}[/]\d{2,3})', 'Blood Pressure', 'mmHg'),
        (r'(\d{2,3}[/]\d{2,3})\s*(?:mmhg|mm)', 'Blood Pressure', 'mmHg'),
        (r'temperature.*?(\d{2,3}\.?\d?)', 'Temperature', 'F'),
        (r'temp.*?(\d{2,3}\.?\d?)\s*(?:f|fahrenheit)', 'Temperature', 'F'),
    ]
    
    test_inputs = [
        "my heart rate is 95 bpm",
        "blood pressure reading was 120/80",
        "temperature is 101.5 fahrenheit",
        "pulse is around 72 beats",
        "95 bpm heart rate",
    ]
    
    for input_text in test_inputs:
        print(f"\nInput: \"{input_text}\"")
        print("-" * 40)
        input_lower = input_text.lower()
        
        found = False
        for pattern, vital_type, unit in vital_patterns:
            match = re.search(pattern, input_lower)
            if match:
                print(f"  MATCH: {vital_type} = {match.group(1)} {unit}")
                print(f"  Pattern: {pattern}")
                found = True
        
        if not found:
            print("  NO MATCH")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("NEURALFLOW MEDICAL CHATBOT - FEATURE TESTS")
    print("=" * 60 + "\n")
    
    # Test regex directly first
    test_vitals_regex_directly()
    
    # Test 1: Vitals Extraction (uses regex only, no LLM)
    vitals_results = test_vitals_extraction()
    
    # Test 2: Symptom Normalization (uses LLM)
    symptom_results = test_symptom_normalization()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Vitals extracted: {len(vitals_results)}")
    print(f"Symptoms normalized: {len(symptom_results)}")
    print("=" * 60)

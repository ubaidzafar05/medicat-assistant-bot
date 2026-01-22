"""
Comprehensive Test Suite for Intelligent Chatbot Features
Tests all LLM-driven components that replaced hardcoded logic.
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test results tracking
results = {"passed": 0, "failed": 0, "tests": []}

def log_test(name, passed, details=""):
    status = "[PASS]" if passed else "[FAIL]"
    results["passed" if passed else "failed"] += 1
    results["tests"].append({"name": name, "passed": passed, "details": details})
    print(f"{status}: {name}")
    if details and not passed:
        print(f"   Details: {details}")

def divider(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ==============================================================================
# TEST 1: Configuration Constants
# ==============================================================================
def test_config():
    divider("TEST 1: Configuration Constants")
    
    try:
        from src.config import MEMORY_CONFIDENCE_THRESHOLD, MEDICAL_COMPLETION_MARKERS
        
        # Test threshold is a valid number
        log_test("MEMORY_CONFIDENCE_THRESHOLD is float", 
                 isinstance(MEMORY_CONFIDENCE_THRESHOLD, float),
                 f"Value: {MEMORY_CONFIDENCE_THRESHOLD}")
        
        # Test markers is a list
        log_test("MEDICAL_COMPLETION_MARKERS is list",
                 isinstance(MEDICAL_COMPLETION_MARKERS, list),
                 f"Value: {MEDICAL_COMPLETION_MARKERS}")
        
        # Test markers contains expected items
        expected = ["Final_Answer", "Possible Causes"]
        has_expected = all(m in MEDICAL_COMPLETION_MARKERS for m in expected)
        log_test("MEDICAL_COMPLETION_MARKERS has expected values",
                 has_expected,
                 f"Missing: {[m for m in expected if m not in MEDICAL_COMPLETION_MARKERS]}")
                 
    except ImportError as e:
        log_test("Config imports", False, str(e))

# ==============================================================================
# TEST 2: LLM-Based Vital Extraction
# ==============================================================================
def test_vital_extraction():
    divider("TEST 2: LLM-Based Vital Extraction")
    
    try:
        from src.agents.medical_agent import MedicalReActAgent
        agent = MedicalReActAgent()
        
        # Test 1: Check method exists
        log_test("extract_vitals_llm method exists",
                 hasattr(agent, 'extract_vitals_llm'))
        
        # Test 2: Extract vitals from natural language (digit format)
        test_input = "My heart rate is 85 bpm and temperature is 99.5°F"
        vitals = agent.extract_vitals_llm(test_input)
        
        log_test("Extracts vitals from digit format",
                 len(vitals) > 0,
                 f"Extracted: {vitals}")
        
        # Test 3: Check vital structure
        if vitals:
            has_structure = all(
                "type" in v and "value" in v 
                for v in vitals
            )
            log_test("Vitals have correct structure (type, value)",
                     has_structure,
                     f"First vital: {vitals[0] if vitals else 'None'}")
        
        # Test 4: Extract from natural language (word numbers) - advanced test
        test_input2 = "my pulse is around one hundred and twenty"
        vitals2 = agent.extract_vitals_llm(test_input2)
        
        log_test("Extracts vitals from word numbers",
                 len(vitals2) > 0,
                 f"Extracted: {vitals2}")
        
        # Test 5: No vitals in unrelated text
        test_input3 = "I have a headache and feel tired"
        vitals3 = agent.extract_vitals_llm(test_input3)
        
        log_test("Returns empty for text without vitals",
                 len(vitals3) == 0,
                 f"Extracted (should be empty): {vitals3}")
                 
    except Exception as e:
        log_test("Vital extraction tests", False, str(e))

# ==============================================================================
# TEST 3: Symptom Extraction (LLM-Based)
# ==============================================================================
def test_symptom_extraction():
    divider("TEST 3: Symptom Extraction (LLM-Based)")
    
    try:
        from src.agents.medical_agent import MedicalReActAgent
        from src.core.session_manager import SessionManager
        
        agent = MedicalReActAgent()
        
        # Test 1: Method exists
        log_test("detect_symptom_codes method exists",
                 hasattr(agent, 'detect_symptom_codes'))
        
        # Create a mock session manager for testing
        sm = SessionManager(db_path=":memory:")
        sm.set_user("test_user")
        
        # Test 2: Extract symptoms from text
        test_input = "I have a severe headache for 3 days"
        symptoms = agent.detect_symptom_codes(test_input, sm)
        
        log_test("Extracts symptoms from natural text",
                 len(symptoms) > 0,
                 f"Extracted: {symptoms}")
        
        # Test 3: Extract symptoms with severity
        test_input2 = "Sharp stabbing pain in my chest"
        symptoms2 = agent.detect_symptom_codes(test_input2, sm)
        
        log_test("Extracts symptoms with location/severity",
                 len(symptoms2) > 0,
                 f"Extracted: {symptoms2}")
                 
    except Exception as e:
        log_test("Symptom extraction tests", False, str(e))

# ==============================================================================
# TEST 4: Router Intent Classification
# ==============================================================================
def test_router():
    divider("TEST 4: Router Intent Classification")
    
    try:
        from src.agents.router import decide_action
        
        # Test 1: Medical routing
        result = decide_action("I have a headache")
        log_test("Routes 'I have a headache' to MEDICAL",
                 result.get("action") == "MEDICAL",
                 f"Got: {result.get('action')}")
        
        # Test 2: Search routing
        result = decide_action("What is vitamin C good for?")
        log_test("Routes 'What is vitamin C' to SEARCH or MEDICAL",
                 result.get("action") in ["SEARCH", "MEDICAL"],
                 f"Got: {result.get('action')}")
        
        # Test 3: Teach routing
        result = decide_action("I am allergic to peanuts")
        log_test("Routes 'I am allergic to peanuts' to TEACH",
                 result.get("action") == "TEACH",
                 f"Got: {result.get('action')}")
        
        # Test 4: Memory routing
        result = decide_action("What am I allergic to?")
        log_test("Routes 'What am I allergic to?' to MEMORY",
                 result.get("action") == "MEMORY",
                 f"Got: {result.get('action')}")
        
        # Test 5: Chat routing
        result = decide_action("Hello, how are you?")
        log_test("Routes 'Hello' to CHAT",
                 result.get("action") == "CHAT",
                 f"Got: {result.get('action')}")
                 
    except Exception as e:
        log_test("Router tests", False, str(e))

# ==============================================================================
# TEST 5: Brain Memory System
# ==============================================================================
def test_brain():
    divider("TEST 5: Brain Memory System")
    
    try:
        from src.core.brain import Brain
        from src.config import MEMORY_CONFIDENCE_THRESHOLD
        
        brain = Brain()
        
        # Test 1: Brain initializes
        log_test("Brain initializes successfully", True)
        
        # Test 2: Uses configurable threshold
        from src.core import brain as brain_module
        import inspect
        source = inspect.getsource(brain_module.Brain.ask)
        uses_config = "MEMORY_CONFIDENCE_THRESHOLD" in source
        log_test("Brain.ask uses MEMORY_CONFIDENCE_THRESHOLD",
                 uses_config,
                 "Should import from config, not hardcode 0.28")
        
        # Test 3: Teach and recall
        brain.teach("Test user likes pizza")
        response = brain.ask("What food do I like?")
        
        log_test("Brain can teach and recall facts",
                 response is not None and "pizza" in response.lower(),
                 f"Response: {response[:100] if response else 'None'}...")
        
        # Clean up
        brain.clear_memory()
        
    except Exception as e:
        log_test("Brain tests", False, str(e))

# ==============================================================================
# TEST 6: Session Manager
# ==============================================================================
def test_session_manager():
    divider("TEST 6: Session Manager")
    
    try:
        from src.core.session_manager import SessionManager
        
        sm = SessionManager(db_path=":memory:")
        
        # Test 1: Set and get user
        sm.set_user("test_user_123")
        log_test("SessionManager sets user",
                 sm.user_id == "test_user_123")
        
        # Test 2: Ensure session
        session_id = sm.ensure_session()
        log_test("SessionManager creates session",
                 session_id is not None,
                 f"Session ID: {session_id}")
        
        # Test 3: Add and retrieve messages
        sm.add_message("user", "Hello")
        sm.add_message("assistant", "Hi there!")
        history = sm.get_active_history()
        
        log_test("SessionManager stores messages",
                 len(history) == 2,
                 f"History length: {len(history)}")
        
        # Test 4: Active mode
        sm.set_active_mode("MEDICAL")
        mode = sm.get_active_mode()
        log_test("SessionManager tracks active mode",
                 mode == "MEDICAL",
                 f"Mode: {mode}")
        
        # Test 5: Save and retrieve vitals
        sm.save_vital("Heart Rate", "80", "bpm")
        vitals = sm.get_recent_vitals()
        log_test("SessionManager saves vitals",
                 len(vitals) > 0,
                 f"Vitals: {vitals}")
        
    except Exception as e:
        log_test("Session manager tests", False, str(e))

# ==============================================================================
# TEST 7: Medical Agent ReAct Loop
# ==============================================================================
def test_medical_agent():
    divider("TEST 7: Medical Agent ReAct Loop")
    
    try:
        from src.agents.medical_agent import MedicalReActAgent
        from src.core.session_manager import SessionManager
        
        agent = MedicalReActAgent()
        sm = SessionManager(db_path=":memory:")
        sm.set_user("test_patient")
        
        # Test 1: Agent initializes without vital_patterns (no regex)
        has_vital_patterns = hasattr(agent, 'vital_patterns')
        log_test("Agent does NOT have hardcoded vital_patterns",
                 not has_vital_patterns,
                 "Should use LLM extraction instead")
        
        # Test 2: Agent runs and produces output
        response_chunks = list(agent.run("I have a mild headache", [], sm))
        full_response = "".join(response_chunks)
        
        log_test("Medical agent produces response",
                 len(full_response) > 20,
                 f"Response length: {len(full_response)}")
        
        # Test 3: Response contains structured output indicators
        has_structure = any(marker in full_response for marker in 
                          ["Possible Causes", "Severity", "Next Steps", "Red Flags", "low", "medium", "high"])
        log_test("Response has structured output or diagnosis",
                 has_structure,
                 f"First 200 chars: {full_response[:200]}")
                 
    except Exception as e:
        log_test("Medical agent tests", False, str(e))

# ==============================================================================
# TEST 8: Logic Utils Context Detection
# ==============================================================================
def test_logic_utils():
    divider("TEST 8: Logic Utils Context Detection")
    
    try:
        from src.core import logic_utils
        import inspect
        
        source = inspect.getsource(logic_utils.execute_chat_logic)
        
        # Test 1: No hardcoded keyword list
        has_hardcoded = '"pain", "fever", "symptom", "headache"' in source
        log_test("No hardcoded keyword list in logic_utils",
                 not has_hardcoded,
                 "Should use session state instead of keywords")
        
        # Test 2: Uses session manager get_active_mode
        uses_session_state = "get_active_mode" in source
        log_test("Uses session manager for context detection",
                 uses_session_state,
                 "Should call session_manager.get_active_mode()")
                 
    except Exception as e:
        log_test("Logic utils tests", False, str(e))

# ==============================================================================
# TEST 9: Medical Prompt (No Aggressive Shortcuts)
# ==============================================================================
def test_medical_prompt():
    divider("TEST 9: Medical Prompt (No Aggressive Shortcuts)")
    
    try:
        from src.agents.medical_agent import MedicalReActAgent
        import inspect
        
        agent = MedicalReActAgent()
        source = inspect.getsource(agent.run)
        
        # Test 1: No kidney stone shortcut
        has_kidney_shortcut = "KIDNEY STONES" in source.upper()
        log_test("No hardcoded 'kidney stones' shortcut",
                 not has_kidney_shortcut,
                 "Should use differential diagnosis")
        
        # Test 2: No blood in urine shortcut
        has_blood_shortcut = "BLOOD IN URINE" in source.upper() and "SERIOUS" in source.upper()
        log_test("No hardcoded 'blood in urine' shortcut",
                 not has_blood_shortcut,
                 "Should reason through symptoms")
        
        # Test 3: Uses differential diagnosis
        uses_differential = "DIFFERENTIAL DIAGNOSIS" in source.upper()
        log_test("Uses differential diagnosis reasoning",
                 uses_differential,
                 "Prompt should mention differential diagnosis")
                 
    except Exception as e:
        log_test("Medical prompt tests", False, str(e))

# ==============================================================================
# TEST 10: End-to-End Integration
# ==============================================================================
def test_integration():
    divider("TEST 10: End-to-End Integration")
    
    try:
        from src.core.logic_utils import execute_chat_logic
        from src.core.brain import Brain
        from src.services.llm_groq import GroqLLM
        from src.services.search_tool import SearchTool
        from src.agents.medical_agent import MedicalReActAgent
        from src.core.session_manager import SessionManager
        
        # Setup components
        sm = SessionManager(db_path=":memory:")
        sm.set_user("integration_test_user")
        
        components = {
            "brain": Brain(),
            "llm": GroqLLM(),
            "search_tool": SearchTool(),
            "medical_agent": MedicalReActAgent(),
            "session_manager": sm
        }
        
        # Test 1: MEDICAL action
        response_chunks = list(execute_chat_logic(
            "MEDICAL", "I have a headache", [], 
            {"action": "MEDICAL"}, components
        ))
        full_response = "".join(response_chunks)
        
        log_test("MEDICAL action produces response",
                 len(full_response) > 20,
                 f"Response length: {len(full_response)}")
        
        # Test 2: TEACH action
        response_chunks = list(execute_chat_logic(
            "TEACH", "I am allergic to shellfish", [],
            {"action": "TEACH", "learn": "User is allergic to shellfish"}, 
            components
        ))
        teach_response = "".join(response_chunks)
        
        log_test("TEACH action stores and responds",
                 len(teach_response) > 5,
                 f"Response: {teach_response[:100]}")
        
        # Clean up
        components["brain"].clear_memory()
        
    except Exception as e:
        log_test("Integration tests", False, str(e))

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  COMPREHENSIVE INTELLIGENT CHATBOT TEST SUITE")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    # Run all tests
    test_config()
    test_vital_extraction()
    test_symptom_extraction()
    test_router()
    test_brain()
    test_session_manager()
    test_medical_agent()
    test_logic_utils()
    test_medical_prompt()
    test_integration()
    
    # Summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    print(f"  [PASS] Passed: {results['passed']}")
    print(f"  [FAIL] Failed: {results['failed']}")
    print(f"  [INFO] Total:  {results['passed'] + results['failed']}")
    print("="*60)
    
    # Exit code
    sys.exit(0 if results['failed'] == 0 else 1)

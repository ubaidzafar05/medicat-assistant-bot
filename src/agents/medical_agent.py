import re
import json
import logging
from src.services.llm_groq import GroqLLM
from src.services.search_tool import SearchTool
from src.config import CONTEXT_WINDOW_SIZE
from src.utils import strip_internal_markers
from src.agents.medical_prompt import MEDICAL_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class MedicalReActAgent:
    def __init__(self):
        self.llm = GroqLLM()
        self.search_tool = SearchTool()
        self.max_steps = 5
        
        # Patterns for auto-extracting vitals from user messages
        self.vital_patterns = [
            (r'heart\s*rate.*?(\d{2,3})', 'Heart Rate', 'bpm'),
            (r'heartbeat.*?(\d{2,3})', 'Heart Rate', 'bpm'),
            (r'pulse.*?(\d{2,3})', 'Heart Rate', 'bpm'),
            (r'(\d{2,3})\s*(?:bpm|beats)', 'Heart Rate', 'bpm'),
            (r'blood\s*pressure.*?(\d{2,3}[/]\d{2,3})', 'Blood Pressure', 'mmHg'),
            (r'bp.*?(\d{2,3}[/]\d{2,3})', 'Blood Pressure', 'mmHg'),
            (r'(\d{2,3}[/]\d{2,3})\s*(?:mmhg|mm)', 'Blood Pressure', 'mmHg'),
            (r'temperature.*?(\d{2,3}\.?\d?)', 'Temperature', '°F'),
            (r'temp.*?(\d{2,3}\.?\d?)\s*(?:f|fahrenheit|°f)', 'Temperature', '°F'),
            (r'temp.*?(\d{2}\.?\d?)\s*(?:c|celsius|°c)', 'Temperature', '°C'),
            (r'weight.*?(\d{2,3}\.?\d?)\s*(?:kg|kilogram)', 'Weight', 'kg'),
            (r'weight.*?(\d{2,3}\.?\d?)\s*(?:lb|lbs|pound)', 'Weight', 'lbs'),
            (r'oxygen.*?(\d{2,3})\s*%?', 'Oxygen Saturation', '%'),
            (r'spo2.*?(\d{2,3})', 'Oxygen Saturation', '%'),
        ]
    
    def auto_extract_and_save_vitals(self, user_input, session_manager):
        """
        Automatically extracts and saves any vitals mentioned in user input.
        Returns list of saved vitals for acknowledgment.
        """
        if not session_manager:
            return []
        
        saved_vitals = []
        input_lower = user_input.lower()
        
        for pattern, vital_type, unit in self.vital_patterns:
            match = re.search(pattern, input_lower)
            if match:
                value = match.group(1)
                try:
                    session_manager.save_vital(vital_type, value, unit)
                    saved_vitals.append(f"{vital_type}: {value} {unit}")
                    logger.debug(f"Auto-saved vital: {vital_type} = {value} {unit}")
                except Exception as e:
                    logger.error(f"Error saving vital: {e}")
        
        return saved_vitals

    def detect_symptom_codes(self, user_input, session_manager):
        """
        Uses LLM to convert free text into structured symptom codes.
        Example: "Head hurts for 3 days" -> {"code": "pain.head", "severity": "medium", "duration": "3 days"}
        """
        if not session_manager:
            return []

        # 1. The Ontology Prompt (The "Codebook")
        extraction_prompt = f"""
You are a Medical Data Parser. Extract symptoms from the text below into structured JSON.
TEXT: "{user_input}"

RULES:
1. Return ONLY a valid JSON object. No markdown, no conversational text.
2. Use this Dot-Notation format for codes: [system].[location].[specifier]
   - Systems: pain, gi (stomach/gut), resp (breathing), neuro, cardio, skin, general
   - Examples:
     - "Headache" -> "pain.head.general"
     - "Sharp stomach pain" -> "pain.abd.sharp"
     - "Nausea" -> "gi.nausea"
     - "Fever" -> "general.fever"
3. Severity: Infer "low", "medium", "high" from context (default "unknown").
4. Duration: Extract how long the symptom has been occurring (e.g., "3 days", "2 hours", "1 week"). Use null if not mentioned.

JSON FORMAT:
{{
  "symptoms": [
    {{ "code": "system.location.specifier", "severity": "low/medium/high", "duration": "time period or null" }}
  ]
}}
"""
        try:
            # 2. Call LLM (Fast call)
            response = self.llm(extraction_prompt)
            if not response:
                logger.warning("Empty LLM response for symptom extraction")
                return []

            # 3. Clean JSON (strip markdown code blocks if any)
            clean_json = response.replace("```json", "").replace("```", "").strip()
            # Handle potential intro text if LLM ignores instruction slightly
            if "{" in clean_json:
                clean_json = clean_json[clean_json.find("{"):clean_json.rfind("}")+1]
            
            data = json.loads(clean_json)

            saved_items = []
            if "symptoms" in data:
                for item in data["symptoms"]:
                    code = item.get('code')
                    severity = item.get('severity', 'unknown')
                    duration = item.get('duration')  # NEW: Extract duration
                    if code:
                        # Call the updated session_manager method with duration
                        session_manager.save_symptom(code, severity, duration)
                        duration_str = f", {duration}" if duration else ""
                        saved_items.append(f"{code} ({severity}{duration_str})")

            if saved_items:
                logger.debug(f"Normalized symptoms: {saved_items}")
            return saved_items

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse symptom JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Symptom extraction failed: {e}")
            return []

    def run(self, user_input, history, session_manager=None):
        """
        Executes the ReAct loop: Thought -> Action -> Observation
        """
        # 1. Auto-extract and save any vitals mentioned in the user's message
        saved_vitals = self.auto_extract_and_save_vitals(user_input, session_manager)

        # 2. Auto-extract NORMALIZED SYMPTOMS (New)
        normalized_symptoms = self.detect_symptom_codes(user_input, session_manager)
        
        context_text = ""
        if history:
            context_text = "Conversation History:\n" + "\n".join([f"{msg['role'].replace('user', 'User').replace('assistant', 'Assistant').title()}: {msg['content']}" for msg in history[-CONTEXT_WINDOW_SIZE:]]) + "\n"

        # Check for recent vitals to provide context (if session_manager available)
        vitals_context = ""
        if session_manager:
            recent_vitals = session_manager.get_recent_vitals(limit=3)
            if recent_vitals:
                vitals_context = "\n### RECENT VITALS:\n" + "\n".join([f"- {v['vital_type']}: {v['value']} {v['unit']} ({v['timestamp']})" for v in recent_vitals]) + "\n"
        
        # If we just saved vitals, add that to context for the LLM to acknowledge
        saved_context = ""
        if saved_vitals:
            saved_context = f"\n### VITALS JUST RECORDED:\n" + "\n".join([f"- {v}" for v in saved_vitals]) + "\nAcknowledge that you've recorded these vitals in your response.\n"

        # If we detected symptoms, add them to context
        symptom_context = ""
        if normalized_symptoms:
            symptom_context = f"\n### SYMPTOM DATA DETECTED (Structured):\n" + "\n".join([f"- {s}" for s in normalized_symptoms]) + "\n"

        # NEW: Get symptom history and trends for context
        symptom_history_context = ""
        if session_manager:
            trends = session_manager.get_symptom_trends(days=30)
            if trends:
                recurring = trends.get('recurring_symptoms', [])
                worsening = trends.get('worsening_trends', [])
                total = trends.get('total_symptoms_logged', 0)
                
                if total > 0:
                    symptom_history_context = "\n### PATIENT SYMPTOM HISTORY (Last 30 Days):\n"
                    symptom_history_context += f"- Total symptoms logged: {total}\n"
                    
                    if recurring:
                        symptom_history_context += "- **Recurring symptoms:**\n"
                        for r in recurring[:3]:  # Top 3
                            symptom_history_context += f"  - {r['symptom_code']}: {r['count']} occurrences (max severity: {r['max_severity']})\n"
                    
                    if worsening:
                        symptom_history_context += "- **⚠️ WORSENING TRENDS DETECTED:**\n"
                        for w in worsening:
                            symptom_history_context += f"  - {w['symptom_code']}: {w['first_severity']} → {w['last_severity']} over {w['occurrences']} reports\n"
                        symptom_history_context += "\n**IMPORTANT**: Consider escalating care recommendations due to worsening patterns.\n"

        prompt = f"""
### EMERGENCY PROTOCOL (CRITICAL)
- If Red Flags (chest pain, stroke symptoms, allergic reaction) are detected, use `Final_Answer` IMMEDIATELY to urge the ER.

### CURRENT CONTEXT (READ FIRST):
{context_text}
{vitals_context}
{saved_context}
{symptom_context}

### REASONING PROCESS (AGGRESSIVE):
1. **CHECK HISTORY**: Did the user already mention the Symptom, Location, or Duration? **NEVER ASK AGAIN.**
2. **MATCH & EXIT**: 
   - User says "Back pain shooting to groin"? -> **IT IS KIDNEY STONES.** -> Use `Final_Answer`.
   - User says "Blood in urine"? -> **IT IS SERIOUS.** -> Use `Final_Answer`.
   - User says "Feels like kidneys"? -> **AGREE WITH THEM.** -> Use `Final_Answer`.
3. **STOP LOOPING**: If you are about to ask a question, ask yourself: "Can I give a 'likely' diagnosis instead?" If yes, **DIAGNOSE**.

### TOOLS (STRICT FORMAT):
You must use one of these formats to take action:
1. **Search_Web**: Action: Search_Web: [specific query]
2. **Ask_User**: Action: Ask_User: [clarifying question]
3. **Save_Vital**: Action: Save_Vital: [type] | [value] | [unit] (e.g. Heart Rate | 80 | bpm)
4. **Final_Answer**: Action: Final_Answer: [medical advice or diagnosis]

User: "{user_input}"
"""
        
        trace = prompt + "\nThought:"
        
        for step in range(self.max_steps):
            full_response = self.llm(trace, system_prompt=MEDICAL_SYSTEM_PROMPT)
            
            if not full_response.strip().startswith("Thought:"):
                full_response = "Thought: " + full_response
            
            trace += full_response + "\n"
            
            # action_match = re.search(r"Action:\s*[*_]*(Search_Web|Ask_User|Save_Vital|Final_Answer)[*_]*:?\s*(.*)", full_response, re.IGNORECASE)
            action_match = re.search(
                r"Action:\s*[*_]*(Search_Web|Ask_User|Save_Vital|Final_Answer)[*_]*:?\s*(.*)", 
                full_response, 
                re.IGNORECASE | re.DOTALL
            )
            
            if action_match:
                tool = action_match.group(1)
                tool_input = action_match.group(2).strip()
                
                if tool == "Ask_User":
                    yield strip_internal_markers(tool_input)
                    return
                
                elif tool == "Final_Answer":
                    yield strip_internal_markers(tool_input)
                    return
                
                elif tool == "Search_Web":
                    # Execute Search silently without yielding internal status
                    search_result = self.search_tool.search_web(tool_input)
                    observation = f"Observation: {search_result}\n"
                    trace += observation

                elif tool == "Save_Vital":
                    # Parse the input: type | value | unit
                    parts = [p.strip() for p in tool_input.split("|")]
                    if len(parts) >= 2:
                        v_type = parts[0]
                        v_value = parts[1]
                        v_unit = parts[2] if len(parts) > 2 else ""
                        
                        if session_manager:
                            try:
                                session_manager.save_vital(v_type, v_value, v_unit)
                                observation = f"Observation: Saved {v_type}: {v_value} {v_unit}. You can now analyze this data.\n"
                            except Exception as e:
                                observation = f"Observation: Error saving vital: {e}\n"
                        else:
                            observation = "Observation: Session manager not available. Cannot save vital.\n"
                    else:
                        observation = "Observation: Invalid format for Save_Vital. Use type|value|unit.\n"
                    
                    trace += observation
                    
            else:
                if "Final_Answer:" in full_response:
                    content = full_response.split("Final_Answer:")[-1].strip()
                    yield strip_internal_markers(content)
                    return
                elif "Ask_User:" in full_response:
                    content = full_response.split("Ask_User:")[-1].strip()
                    yield strip_internal_markers(content)
                    return

                yield strip_internal_markers(full_response)
                return
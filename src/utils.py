import re
from src.services.llm_groq import GroqLLM

def get_llm():
    """Returns the configured LLM instance."""
    return GroqLLM()

def strip_internal_markers(text):
    """
    Strip all internal reasoning markers, labels, and formatting from the response.
    Only return the actual user-facing content.
    """
    if not text:
        return ""

    # Markers that indicate the entire line should be removed (internal meta-data)
    drop_patterns = [
        r"^\*?\*?(Thought|Action|Observation):",
        r"^\*?\*?(Session Input|User Input|Patient Context|Immediate Action|Analysis|Step \d+|Procedure|Heading).*",
        r"^\*?\*?(Symptoms|Next Steps|Search_Web|Ask_User|Symptom Update|Plan|Conclusion).*",
        r"^\*?\*?(GAP ANALYSIS|PATTERN RECOGNITION|OBSERVATION CHECKLIST|NEXT ACTION|NEXT QUESTION|TOPIC CHANGE CHECK|EMERGENCY SCAN|ANALYZE|HYPOTHESIZE|ACT).*",
        r"^\*?\*?(Critical missing information|What is critical missing information).*",
        r"^\s*[-\*]\s+(GAP ANALYSIS|PATTERN RECOGNITION|OBSERVATION CHECKLIST|NEXT ACTION|NEXT QUESTION|SYMPTOMS|DURATION|SEVERITY|TRIGGERS|TOPIC CHANGE CHECK|EMERGENCY SCAN|ASSESSMENT|ANALYZE|HYPOTHESIZE|ACT).*",
        r"^\s*[-\*]\s+.*(match a known cluster|new disease mentioned|change in topic|Missing facts).*",
        r"^\s*\(Note:.*\)$", # Drop parenthetical notes
        r"^\s*(Let's think|Let me|I will|I'll|Based on|Ask the user|Ask the patient|Thinking|Analysis|Proceeding|Emergency Scan|Observation Checklist|Gap Analysis|Pattern Recognition|Topic Change Check|Next Question|Next Action|Step \d+|Final Check|Safety Advice|Assessment|Action Plan|Conclusion|Caution is advised|I'd like to ask|Let's start|To better understand|Please explain|How long have you|Analyze|Hypothesize|Act)",
        r"^\*?\*?Next (Question|Action|Step):\*?\*?.*",
        r"^\*?\*?In this situation,.*",
        r"^\*?\*?Tool Call Status:.*",
        r"^\s*- (Not initiated|Yes|No|Not prepared|Unspecified|Unknown).*",
        r"^\s*\d+\.$", # Numbered list item with nothing else
        r"^\s*[\*#]+\s+.*", # Aggressively drop lines starting with * or # (headers)
        r"^\s*\*\*.*\*\*\s*$", # Aggressively drop lines that are JUST bold text
    ]
    
    # Markers that indicate we should just strip the label but KEEP the content
    strip_patterns = [
        r"^\*?\*?(Final Answer|Response|Answer|Bot|Initial Response|Patient|Explanation):\*?\*?\s*",
    ]
    
    lines = text.split('\n')
    clean_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        # 1. Check if we should drop the line entirely
        should_drop = False
        for pattern in drop_patterns:
            if re.match(pattern, stripped, re.IGNORECASE):
                should_drop = True
                break
        if should_drop:
            continue
        
        # 2. Check if we should strip a prefix but keep content
        clean_line = line
        for pattern in strip_patterns:
            match = re.match(pattern, stripped, re.IGNORECASE)
            if match:
                # Remove the matched prefix
                clean_line = stripped[match.end():]
                break
        
        if clean_line.strip():
            clean_lines.append(clean_line)
    
    # Join and clean up
    result = '\n'.join(clean_lines).strip()
    
    # Aggressively strip backticks, triple backticks, and quotes
    result = re.sub(r"```.*```", "", result, flags=re.DOTALL) # Remove code blocks
    result = result.replace("`", "")
    
    # Aggressively strip leading/trailing formatting characters
    result = re.sub(r"^[\s\"'*#:-]+", "", result)
    
    # Strip common final markers if they leaked to the start
    result = re.sub(r"^(Final Answer|Response|Answer|Bot):\s*", "", result, flags=re.IGNORECASE)
    
    # Clean up any remaining asterisks (bolding)
    result = result.replace("*", "")
    
    # Final trim and quote cleanup
    result = result.strip().strip('"')
    
    return result.strip()

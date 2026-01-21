import sys
from src.agents.router import decide_action
from src.core.brain import Brain
from src.utils import strip_internal_markers
from src.services.llm_groq import GroqLLM
from src.config import MAX_HISTORY_LIMIT, CONTEXT_WINDOW_SIZE
from src.services.search_tool import SearchTool
from src.agents.medical_agent import MedicalReActAgent
from src.core.logic_utils import execute_chat_logic

def main():
    print("Initializing NeuralFlow Medical Specialist...")
    
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

    components = {
        "brain": Brain(),
        "llm": GroqLLM(),
        "search_tool": SearchTool(),
        "medical_agent": MedicalReActAgent()
    }
    
    components["brain"].clear_memory()
    
    print("\n[AI] System Online. State Machine Active.")
    print("   - Type 'exit' to stop.\n")

    history = []
    
    # --- STATE TRACKER ---
    # Prevents intent misclassification on short answers
    active_mode = None 

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit"]:
                break

            context_history = history[-CONTEXT_WINDOW_SIZE:]

            # ----------------------------------------------------------------------
            # Step A: Intent Classification with State Lock
            # ----------------------------------------------------------------------
            if active_mode == "MEDICAL":
                # BYPASS ROUTER: Force medical mode for follow-ups
                action_type = "MEDICAL"
                decision = {"action": "MEDICAL"}
            else:
                # NORMAL ROUTING: Ask the router
                decision = decide_action(user_input, context_history)
                action_type = decision.get("action", "CHAT")
                
                # LOCK STATE: Enter medical loop
                if action_type == "MEDICAL":
                    active_mode = "MEDICAL"

            # ----------------------------------------------------------------------
            # Step B: Execute Logic
            # ----------------------------------------------------------------------
            print("Bot: ", end="", flush=True)
            full_response = ""
            
            for chunk in execute_chat_logic(action_type, user_input, context_history, decision, components):
                print(chunk, end="", flush=True)
                full_response += chunk
            
            print() 

            # ----------------------------------------------------------------------
            # Step C: Unlock Condition
            # ----------------------------------------------------------------------
            # Release the lock once a diagnosis is delivered
            if active_mode == "MEDICAL" and "Final_Answer" in full_response:
                active_mode = None
            
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": strip_internal_markers(full_response)})

        except Exception as e:
            print(f"\n[Error] {e}")

if __name__ == "__main__":
    main()
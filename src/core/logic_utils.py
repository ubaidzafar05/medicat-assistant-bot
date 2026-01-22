from src.utils import strip_internal_markers

def execute_chat_logic(action, user_input, history, decision, components):
    """
    Unified logic handler for all chatbot actions.
    Works for both terminal (yielding results) and Gradio (yielding chunks).
    """
    brain = components["brain"]
    llm = components["llm"]
    search_tool = components["search_tool"]
    medical_agent = components["medical_agent"]

    # 1. RESET
    if action == "RESET":
        brain.clear_memory()
        yield "Memory cleared. Starting fresh session."
        return

    # 2. TEACH
    if action == "TEACH":
        fact = decision.get("learn") or user_input
        brain.teach(fact)
        teach_prompt = f"The user just told you this: '{fact}'. Acknowledge it naturally in a brief sentence. Don't say you 'stored' it."
        response = llm(teach_prompt, history=history)
        yield strip_internal_markers(response)
        return

    # 3. MEMORY
    if action == "MEMORY":
        response = brain.ask(user_input, history=history)
        if not response or "don't have" in response.lower():
            yield "I don't have that information in my memory."
            return
        yield strip_internal_markers(response)
        return

    # 4. SEARCH
    if action == "SEARCH":
        router_prompt = f"""
Analyze this user query: "{user_input}"
Determine the best way to search for this information.
1. If it's about a stock, crypto, or currency price, output: STOCK: <ticker_symbol>
2. If it's about a well-known fact, person (non-medical), or history, output: WIKI: <topic>
3. For everything else (news, recent updates), output: WEB: <search_query>

Output ONLY the formatted string.
"""
        routing_decision = llm(router_prompt).strip()
        search_results = ""
        
        # Internal search processing - yields removed for a cleaner UI
        if routing_decision.startswith("STOCK:"):
            ticker = routing_decision.replace("STOCK:", "").strip()
            search_results = search_tool.get_stock_price(ticker)
        elif routing_decision.startswith("WIKI:"):
            topic = routing_decision.replace("WIKI:", "").strip()
            search_results = search_tool.get_wiki_summary(topic)
        else:
            query = routing_decision.replace("WEB:", "").strip() or user_input
            search_results = search_tool.search_web(query)

        # Medical Guard with context check
        guard_prompt = f"""
Recent Context: {history if history else 'None'}
Search Results: {search_results}

Is this information related to the user's health concerns? Reply ONLY "YES" or "NO".
"""
        is_medical = llm(guard_prompt).strip().upper()
        if "NO" in is_medical:
            yield "I found some information, but as a specialized medical expert, I only discuss health-related topics to ensure accuracy and safety. I cannot provide details on that non-medical subject."
            return

        # Synthesis
        prompt = f"""
Information Found:
{search_results}

User Question: {user_input}

Instructions:
1. Answer the question based ONLY on the info above.
2. Focus on health implications if relevant.
3. **CITATION RULE**: Only include the source URL (in parentheses) if the user explicitly asks for a source, or if the information is a specific statistic/study that requires verification. Otherwise, answer smoothly without links.
4. If the info is missing, say "I couldn't find details on that specific health topic."
"""
        response = ""
        for chunk in llm.stream(prompt, history=history):
            yield chunk
        return

    # 5. MEDICAL
    if action == "MEDICAL":
        session_manager = components.get("session_manager")
        for chunk in medical_agent.run(user_input, history, session_manager=session_manager):
            yield chunk
        return

    # 6. CHAT (Enhanced Continuity)
    # Use intelligent state check instead of hardcoded keyword list
    session_manager = components.get("session_manager")
    active_mode = session_manager.get_active_mode() if session_manager else None
    is_mid_diagnosis = (action == "MEDICAL" or active_mode == "MEDICAL")

    system_instruction = f"""
You are a warm, professional Medical Specialist.
Current Context: {'DIAGNOSING USER' if is_mid_diagnosis else 'GENERAL CONVERSATION'}

- If the user says "Yes" or "No", they are answering your medical questions. 
- NEVER say "How can I help you today?" if you were just discussing symptoms.
- Continue the inquiry based on the Conversation History provided.
"""
    prompt = f"User Input: '{user_input}'\nRespond naturally to this input as a doctor would during an exam."
    
    for chunk in llm.stream(prompt, history=history, system_prompt=system_instruction):
        yield chunk
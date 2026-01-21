# ==============================================================================
# BRAIN (Memory Manager)
# This file handles the logic for Long-Term Memory (RAG - Retrieval Augmented Generation).
# It coordinates between the Database (VectorDB) and the AI (LLM).
# ==============================================================================

from src.services.vector_db import VectorDB
from src.services.llm_groq import GroqLLM
from src.config import CONTEXT_WINDOW_SIZE

class Brain:
    def __init__(self):
        # Initialize the Vector Database (where memories live)
        self.vector_db = VectorDB()
        # Initialize the LLM (the voice that articulates the memories)
        self.llm = GroqLLM()

    def teach(self, text: str):
        """
        Adds a new memory to the brain.
        
        Args:
           text (str): The fact/information to remember.
        """
        # We simply pass the text to add() which handles embedding and saving.
        self.vector_db.add(text, source="user_taught")
        return "I've stored that in my memory."

    def clear_memory(self):
        """Clears all long-term memories."""
        self.vector_db.clear()
        return "Memory cleared."

    def ask(self, query: str, history: list = None):
        """
        Retrieves relevant memories and answers the query based on them.
        Uses query expansion to handle implicit links (e.g., Snickers -> Peanuts).
        """
        history = history or []
        
        # 1️⃣ Expand Query for better retrieval
        expansion_prompt = f"""
Identify potential personal constraints (allergies, health, diet, location, workspace) related to this query.
Query: "{query}"
Keywords:"""
        expanded_keywords = self.llm(expansion_prompt).strip()
        search_query = f"{query} {expanded_keywords}"
        print(f"[DEBUG-BRAIN] Expanded Search: {search_query}")

        # 2️⃣ Retrieve top 3 most similar chunks
        results = self.vector_db.query(search_query, top_k=3)

        # Check for confidence threshold
        if not results or results[0]['score'] < 0.28:
            return None

        # 2️⃣ Build context strictly from memory
        context = "\n".join([f"- {r['chunk']}" for r in results])

        # 3️⃣ Include recent conversation history (optional)
        history_text = ""
        if history:
            history_text = "Conversation History:\n" + "\n".join([f"{msg['role'].title()}: {msg['content']}" for msg in history[-CONTEXT_WINDOW_SIZE:]]) + "\n"

        prompt = f"""
SYSTEM: You are a factual assistant. Use the user's personal memories provided below.
Apply common sense reasoning to these memories (e.g., if the user is allergic to peanuts, they shouldn't eat a Snickers).
If the memory context is completely irrelevant, say: "I don't have that information."

Memory Context:
{context}

{history_text}
User Question: {query}

Answer:"""

        # 5️⃣ Call the LLM
        return self.llm(prompt)

# return self.llm.hallucination_safe_call(prompt)

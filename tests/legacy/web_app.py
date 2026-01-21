from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn
import sys
import datetime
import re

from agent import decide_action
from brain import Brain
from llm_groq import GroqLLM
from config import MAX_HISTORY_LIMIT
from search_tool import SearchTool
from medical_agent import MedicalReActAgent

# ------------------------------------------------------------------------------
# Initialization
# ------------------------------------------------------------------------------
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except:
    pass

brain = Brain()
llm = GroqLLM()
search_tool = SearchTool()
medical_agent = MedicalReActAgent()

history = []

class UserMessage(BaseModel):
    message: str

# ------------------------------------------------------------------------------
# Utility: REALTIME detection (HARD RULE)
# ------------------------------------------------------------------------------
REALTIME_KEYWORDS = [
    "time", "date", "today", "now"
]

def is_realtime_query(text: str) -> bool:
    # Use word boundary \b to match exact words (prevents "sometime" matching "time")
    pattern = r"\b(" + "|".join(REALTIME_KEYWORDS) + r")\b"
    return bool(re.search(pattern, text, re.IGNORECASE))

# ------------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat")
async def chat_endpoint(user_msg: UserMessage):
    user_input = user_msg.message.strip()
    if not user_input:
        return {"response": "Please enter a message."}

    async def response_generator():
        global history
        full_response = ""

        # ------------------------------------------------------------------
        # 1️⃣ REALTIME OVERRIDE (NO LLM)
        # ------------------------------------------------------------------
        if is_realtime_query(user_input):
            now = datetime.datetime.now()

            if "time" in user_input.lower():
                msg = f"The current time is {now.strftime('%H:%M:%S')}."
            elif "date" in user_input.lower() or "today" in user_input.lower():
                msg = f"Today's date is {now.strftime('%Y-%m-%d')}."
            else:
                msg = "I need live external data to answer that accurately."

            yield msg
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": msg})
            return

        # ------------------------------------------------------------------
        # 2️⃣ AGENT DECISION
        # ------------------------------------------------------------------
        decision = decide_action(user_input, history)
        action = decision.get("action", "CHAT")

        if decision.get("learn"):
            brain.teach(decision["learn"])
        
        # ------------------------------------------------------------------
        # RESET
        # ------------------------------------------------------------------
        if action == "RESET":
            brain.clear_memory()
            history.clear()
            msg = "Memory cleared. Starting fresh session."
            yield msg
            return

        # ------------------------------------------------------------------
        # SEARCH
        # ------------------------------------------------------------------
        if action == "SEARCH":
            query = decision.get("search_query") or user_input
            yield f"Searching for: {query}...\n\n"
            
            search_results = search_tool.search_web(query)
            
            prompt = f"""
User Query: {user_input}
Search Results:
{search_results}

Answer the user's query using ONLY the search results above.
If the results don't contain the answer, say "I couldn't find that information."
"""
            for chunk in llm.stream(prompt, history=history):
                full_response += chunk
                yield chunk

        # ------------------------------------------------------------------
        # 3️⃣ MEMORY
        # ------------------------------------------------------------------
        elif action == "MEMORY":
            top_memories = brain.vector_db.query(user_input, top_k=3)

            if not top_memories or top_memories[0]["score"] < 0.65:
                msg = "I don't have enough personal information to answer that."
                yield msg
                full_response = msg
            else:
                context = "\n".join(f"- {m['chunk']}" for m in top_memories)
                prompt = f"""
Answer ONLY using the memory below.
If insufficient, say you don't know.

Memory:
{context}

Question: {user_input}
Answer:
"""
                for chunk in llm.stream(prompt, history=history):
                    full_response += chunk
                    yield chunk

        # ------------------------------------------------------------------
        # 4️⃣ MEDICAL (Primary Intent)
        # ------------------------------------------------------------------
        elif action == "MEDICAL":
            # New ReAct Agent Flow
            for chunk in medical_agent.run(user_input, history):
                full_response += chunk
                yield chunk

        # ------------------------------------------------------------------
        # 5️⃣ CHAT (Fail-Safe)
        # ------------------------------------------------------------------
        else:
            system_instruction = """
You are a helpful assistant.
- If the user says "Hi", "Thanks", "Great": Respond with a simple greeting under 10 words (e.g., "Hello! How can I help you?"). Do NOT explain who you are.
- If the user asks non-medical questions (sports, coding): Refuse politely.
"""
            prompt = f"""
{system_instruction}

User Input: "{user_input}"
Response:
"""
            for chunk in llm.stream(prompt, history=history):
                full_response += chunk
                yield chunk

        # ------------------------------------------------------------------
        # 6️⃣ UPDATE HISTORY
        # ------------------------------------------------------------------
        # Only append to history if we haven't already returned (captured inside blocks for some paths)
        # For MEDICAL, MEMORY, CHAT, SEARCH, we need to append.
        if action in ["MEDICAL", "MEMORY", "CHAT", "SEARCH"]:
             history.append({"role": "user", "content": user_input})
             history.append({"role": "assistant", "content": full_response})

        if len(history) > MAX_HISTORY_LIMIT * 2:
            history[:] = history[-MAX_HISTORY_LIMIT * 2:]

    return StreamingResponse(response_generator(), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run("web_app:app", host="127.0.0.1", port=8000, reload=True)

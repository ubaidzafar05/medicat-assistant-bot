# ==============================================================================
# LLM WRAPPER (Groq API)
# This file handles the connection to the Groq Cloud API.
# It wraps the API calls in a class that looks like a standard LangChain LLM.
# ==============================================================================

try:
    from langchain_core.language_models.llms import LLM
except ImportError:
    from langchain.llms.base import LLM

from typing import Optional, List, Any
import requests
from src.config import GROQ_API_KEY, MODEL_NAME, API_URL

class GroqLLM(LLM):
    """
    LangChain-compatible Groq LLM wrapper.
    This allows us to use `llm(prompt)` style calls.
    """

    @property
    def _llm_type(self) -> str:
        return "groq"

    def __call__(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        """Allows class instance to be called like a function."""
        return self._call(prompt, stop, **kwargs)

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> str:
        """
        Send prompt to Groq API and return the response.
        
        Args:
            prompt (str): The text to send to the AI.
            kwargs: Can contain 'history' (list of previous messages).
        """
        
        # ----------------------------------------------------------------------
        # Prepare Messages
        history = kwargs.get("history", [])
        system_prompt = kwargs.get("system_prompt")
        
        # Start with the conversation history (if any)
        messages = history.copy()

        # Insert system prompt at the beginning if provided
        if system_prompt:
            messages.insert(0, {"role": "system", "content": str(system_prompt)})
        
        # Append the current prompt
        messages.append({"role": "user", "content": str(prompt)})
        
        # Sanitize all messages to ensure content is string
        for m in messages:
            if m.get("content") is None:
                m["content"] = ""
            else:
                m["content"] = str(m["content"])
        
        # ----------------------------------------------------------------------
        # 2. Build Request
        # ----------------------------------------------------------------------
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": 0.2 # Controls creativity (0.0 = Fact, 1.0 = Creative)
        }
        
        # ----------------------------------------------------------------------
        # 3. Execute HTTP Call
        # ----------------------------------------------------------------------
        response = requests.post(API_URL, headers=headers, json=payload)

        # ----------------------------------------------------------------------
        # 4. Handle Response
        # ----------------------------------------------------------------------
        if response.status_code != 200:
            return f"❌ Error {response.status_code}: {response.text}"
        try:
            # Extract just the text content from the deep JSON structure
            return response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            return f"❌ Unexpected response format: {response.text}"
    def stream(self, prompt: str, **kwargs) -> Any:
        """
        Streams the response from Groq API token by token.
        Yields: str (content chunks)
        """
        import json
        
        history = kwargs.get("history", [])
        system_prompt = kwargs.get("system_prompt")

        messages = history.copy()

        if system_prompt:
             messages.insert(0, {"role": "system", "content": str(system_prompt)})

        messages.append({"role": "user", "content": prompt})
        
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": 0.2,
            "stream": True # Enable Streaming
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, stream=True)
        
        if response.status_code != 200:
            error_text = response.text
            print(f"[DEBUG-LLM] Stream Error: {response.status_code} - {error_text}")
            yield f"Error: {response.status_code} - {error_text}"
            return

        print("[DEBUG-LLM] Stream started successfully.")
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                # Some APIs send multiple data blocks per line or slightly different formats
                if decoded_line.startswith("data: "):
                    data_str = decoded_line.replace("data: ", "")
                    
                    if data_str.strip() == "[DONE]":
                        print("[DEBUG-LLM] Stream complete [DONE].")
                        break
                        
                    try:
                        data_json = json.loads(data_str)
                        if "choices" in data_json and len(data_json["choices"]) > 0:
                            delta = data_json["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        print(f"[DEBUG-LLM] Failed to parse JSON: {data_str}")
                        continue
                    except Exception as e:
                        print(f"[DEBUG-LLM] Unexpected error parsing stream: {e}")
                        continue


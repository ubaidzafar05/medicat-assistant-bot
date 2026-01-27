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
        Send prompt to Groq API with retries and timeout.
        """
        import time
        from requests.exceptions import RequestException

        # ----------------------------------------------------------------------
        # 1. Prepare Messages
        history = kwargs.get("history", [])
        system_prompt = kwargs.get("system_prompt")
        messages = history.copy()
        if system_prompt:
            messages.insert(0, {"role": "system", "content": str(system_prompt)})
        messages.append({"role": "user", "content": str(prompt)})
        
        for m in messages:
            m["content"] = str(m.get("content", ""))

        # ----------------------------------------------------------------------
        # 2. Build Request
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": 0.2
        }

        # ----------------------------------------------------------------------
        # 3. Execute HTTP Call with Retries
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    try:
                        return response.json()["choices"][0]["message"]["content"]
                    except (KeyError, IndexError):
                        return f"❌ Unexpected response format: {response.text}"
                
                # If rate limited (429) or server error (500+), retry
                if response.status_code in [429, 500, 502, 503, 504]:
                    print(f"[DEBUG-LLM] Attempt {attempt+1} failed with {response.status_code}. Retrying...")
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                
                return f"❌ Error {response.status_code}: {response.text}"

            except RequestException as e:
                print(f"[DEBUG-LLM] Connection attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                else:
                    return f"❌ Connection Error: Unable to reach AI service after {max_retries} attempts."
        
        return "❌ Max retries reached without successful response."
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
        
        response = requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=30)
        
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


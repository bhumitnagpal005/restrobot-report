import httpx
from backend.app import config
from backend.app.llm.base import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = config.OLLAMA_BASE_URL, model: str = config.OLLAMA_MODEL):
        self.base_url = base_url
        self.model = model

    def generate_response(self, prompt: str, system_instruction: str = "") -> str:
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            response = httpx.post(url, json=payload, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
        except Exception as e:
            print(f"Ollama API request failed: {e}")
        
        return "Local Ollama service unavailable. Please check your Ollama configuration."

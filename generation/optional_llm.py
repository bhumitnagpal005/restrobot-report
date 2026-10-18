import os
from dotenv import load_dotenv
from generation.base import BaseLLMProvider

load_dotenv()

class OptionalGeminiLLM(BaseLLMProvider):
    """
    Optional Gemini LLM provider.
    If GEMINI_API_KEY is configured, generates answer.
    If missing, returns graceful notice without crashing retrieval engine.
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("gemini_token")
        self.client = None
        if self.api_key and self.api_key != "your_api_key_here":
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed initializing Gemini client: {e}")

    def generate(self, prompt: str) -> str:
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response and hasattr(response, "text") and response.text:
                    return response.text.strip()
            except Exception as e:
                return f"[LLM Notice: Gemini API call failed ({e}). Showing retrieved context items directly.]"

        return "[LLM Notice: GEMINI_API_KEY not configured. Showing retrieved context items directly.]"

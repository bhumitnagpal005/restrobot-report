import os
from backend.app import config
from backend.app.llm.base import LLMProvider

class GeminiProvider(LLMProvider):
    """
    Gemini API provider for natural language generation.
    Handles client setup using google.genai SDK with graceful fallback if unconfigured.
    """
    def __init__(self, api_key: str = config.GEMINI_API_KEY):
        self.api_key = api_key
        self.client = None
        if self.api_key and self.api_key != "YOUR_GEMINI_API_KEY_HERE":
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed initializing Gemini client: {e}")

    def generate_response(self, prompt: str, system_instruction: str = "") -> str:
        if self.client:
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response and hasattr(response, "text") and response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"Gemini API generation error: {e}. Falling back to context synthesis.")

        # Fallback response generator if Gemini API key is missing or fails
        return self._build_synthetic_response(prompt)

    def _build_synthetic_response(self, prompt: str) -> str:
        if "RELEVANT RETRIEVED RESTAURANT & MENU CONTEXT:" in prompt:
            context = prompt.split("RELEVANT RETRIEVED RESTAURANT & MENU CONTEXT:")[1].split("USER QUERY:")[0].strip()
            if "No relevant menu items" in context:
                return "I couldn't find any menu items satisfying all of those requirements in our restaurant database."
            
            lines = [line.strip() for line in context.split("\n") if line.strip()]
            response_items = []
            for l in lines[:5]:
                response_items.append(f"• {l}")
            
            return (
                "Here are the top matching options found for your request:\n\n"
                + "\n".join(response_items)
                + "\n\n(Generated via RestroBot context synthesis fallback)"
            )
        return "Here are the relevant restaurant options matching your request."

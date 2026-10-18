"""
Google Gemini LLM Provider for RestroBot.
Supports candidate model rotation and robust fallback handling.
"""

import os
import time
from google import genai
from dotenv import load_dotenv
from generation.base import BaseLLMProvider
import config

load_dotenv()


class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        self.candidate_models = config.LLM_CANDIDATE_MODELS
        self._init_client()

    def _init_client(self):
        api_key = os.getenv("gemini_token") or os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()

    def generate(self, prompt: str) -> str:
        """
        Generates grounded answer trying candidate models with retries.
        """
        if not self.client:
            return "I'm sorry, the Gemini API client is not initialized. Please configure GEMINI_API_KEY."

        max_retries = 2
        for model_name in self.candidate_models:
            for attempt in range(max_retries):
                try:
                    res = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if res and res.text:
                        return res.text.strip()
                except Exception as e:
                    print(f"[Warning] Call to {model_name} failed (Attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(1)

        # Fallback response if all LLM API attempts fail
        return "I'm sorry, I am currently experiencing high API server traffic. Please try again in a moment."

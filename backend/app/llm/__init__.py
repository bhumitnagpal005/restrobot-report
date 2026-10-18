from backend.app.llm.base import LLMProvider
from backend.app.llm.gemini import GeminiProvider
from backend.app.llm.ollama import OllamaProvider

def get_llm_provider() -> LLMProvider:
    # Factory function for LLM provider
    return GeminiProvider()

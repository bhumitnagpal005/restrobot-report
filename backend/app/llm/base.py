from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, system_instruction: str = "") -> str:
        """
        Generates a natural language response given a prompt.
        """
        pass

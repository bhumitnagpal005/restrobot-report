from collections import deque


class ConversationMemory:
    def __init__(self, max_turns: int = 5):
        """Initializes a rolling window conversation memory with a max capacity."""
        self._history: deque[tuple[str, str]] = deque(maxlen=max_turns)

    def add(self, query: str, response: str) -> None:
        """Appends a new turn to the conversation history."""
        self._history.append((query.strip(), response.strip()))

    def get_history(self) -> list[tuple[str, str]]:
        """Returns the conversation history as a list of (query, response) tuples."""
        return list(self._history)

    def format_for_prompt(self) -> str:
        """Formats the conversation history for inclusion in LLM prompts."""
        if not self._history:
            return "No previous conversation history."
        return "\n".join(f"Query: {q}\nResponse: {r}" for q, r in self._history)

    def clear(self) -> None:
        """Clears all stored conversation history."""
        self._history.clear()

    def __len__(self) -> int:
        """Returns the current number of stored turns."""
        return len(self._history)
"""
Conversation State Manager for RestroBot.
Tracks multi-turn conversation turns and maintains persistent structured active constraints.
"""

from collections import deque
from query_processing.query_parser import QueryParser
import config


class ConversationState:
    def __init__(self, max_turns: int = config.MAX_CONVERSATION_TURNS):
        self.max_turns = max_turns
        self.history: deque[dict] = deque(maxlen=max_turns)
        self.active_constraints: dict = {
            "food_type": None,
            "diet": None,
            "spice_level": None,
            "min_price": None,
            "max_price": None,
            "restaurant": None,
            "location": None,
        }

    def process_turn(self, query: str) -> dict:
        """
        Parses incoming query, merges new non-null constraints with persistent active constraints,
        and returns updated query analysis.
        """
        parsed = QueryParser.parse_query(query)
        new_constraints = parsed["constraints"]
        
        # Merge new non-None constraints into active_constraints
        for key, val in new_constraints.items():
            if val is not None:
                self.active_constraints[key] = val

        return {
            "query_text": query,
            "intent": parsed["intent"],
            "new_constraints": new_constraints,
            "active_constraints": dict(self.active_constraints),
        }

    def add_turn_result(self, query: str, response: str, approach: str) -> None:
        """
        Appends turn exchange to conversation history.
        """
        self.history.append({
            "query": query,
            "response": response,
            "approach": approach,
            "active_constraints": dict(self.active_constraints),
        })

    def format_history_for_prompt(self) -> str:
        """
        Formats last 5 turns into context string for LLM generation.
        """
        if not self.history:
            return "No previous conversation history."
        
        lines = []
        for turn in self.history:
            lines.append(f"User: {turn['query']}\nAssistant: {turn['response']}")
        return "\n\n".join(lines)

    def clear(self) -> None:
        """
        Resets conversation turns and active constraints.
        """
        self.history.clear()
        self.active_constraints = {
            "food_type": None,
            "diet": None,
            "spice_level": None,
            "min_price": None,
            "max_price": None,
            "restaurant": None,
            "location": None,
        }

import time
from typing import Dict, Any, List, Optional
from backend.app.constraints.schema import ExtractedConstraints

class ConversationTurn:
    def __init__(self, turn_id: int, query: str, answer: str, approach: str, constraints: Optional[ExtractedConstraints] = None):
        self.turn_id = turn_id
        self.query = query
        self.answer = answer
        self.approach = approach
        self.constraints = constraints
        self.timestamp = time.time()

class SessionContext:
    def __init__(self, session_id: str, max_history: int = 5):
        self.session_id = session_id
        self.max_history = max_history
        self.turns: List[ConversationTurn] = []
        self.last_constraints: Optional[ExtractedConstraints] = None

    def add_turn(self, query: str, answer: str, approach: str, constraints: Optional[ExtractedConstraints] = None):
        turn = ConversationTurn(
            turn_id=len(self.turns) + 1,
            query=query,
            answer=answer,
            approach=approach,
            constraints=constraints
        )
        self.turns.append(turn)
        if len(self.turns) > self.max_history:
            self.turns.pop(0)
        if constraints:
            self.last_constraints = constraints

    def get_history_summary(self) -> str:
        if not self.turns:
            return ""
        lines = []
        for t in self.turns[-3:]:  # Controlled context window (last 3 turns)
            lines.append(f"User: {t.query}\nBot ({t.approach}): {t.answer}")
        return "\n".join(lines)


class ConversationManager:
    """
    Session and conversation history manager for multi-turn conversational support.
    """
    def __init__(self):
        self.sessions: Dict[str, SessionContext] = {}

    def get_or_create_session(self, session_id: str) -> SessionContext:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionContext(session_id=session_id)
        return self.sessions[session_id]

    def record_turn(self, session_id: str, query: str, answer: str, approach: str, constraints: Optional[ExtractedConstraints] = None):
        session = self.get_or_create_session(session_id)
        session.add_turn(query, answer, approach, constraints)


_conversation_manager_instance = None

def get_conversation_manager() -> ConversationManager:
    global _conversation_manager_instance
    if _conversation_manager_instance is None:
        _conversation_manager_instance = ConversationManager()
    return _conversation_manager_instance

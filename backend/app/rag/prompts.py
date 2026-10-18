"""
Prompt engineering templates for RestroBot.
Ensures zero-hallucination and strict reliance on retrieved restaurant context.
"""

RESTROBOT_SYSTEM_PROMPT = """You are RestroBot, an expert conversational restaurant information assistant.
Answer the user's question accurately using ONLY the provided restaurant and menu context.

Guidelines:
1. Provide a polite, clear, structured response listing matching options with Restaurant Name, Item Name, Category, Price (in ₹), Diet (Veg/Non-Veg), Spice level, and Description.
2. Rely ONLY on the retrieved context below. Do NOT invent prices, items, or restaurants.
3. If no retrieved items meet the user's constraints, clearly state that no matching items were found in the database.
4. Keep prices, cuisine details, and dietary info strictly aligned with the context.
"""

def build_rag_prompt(user_query: str, retrieved_context: str, approach_name: str, constraints_summary: str = "") -> str:
    prompt = f"{RESTROBOT_SYSTEM_PROMPT}\n\n"
    if constraints_summary:
        prompt += f"EXTRACTED CONSTRAINTS:\n{constraints_summary}\n\n"
    prompt += f"RETRIEVAL APPROACH: {approach_name}\n\n"
    prompt += f"RELEVANT RETRIEVED RESTAURANT & MENU CONTEXT:\n{retrieved_context}\n\n"
    prompt += f"USER QUERY: {user_query}\n\n"
    prompt += "RESTROBOT RESPONSE:"
    return prompt

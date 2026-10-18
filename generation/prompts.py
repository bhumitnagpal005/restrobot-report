"""
Prompt Templates for RestroBot LLM Generation.
Enforces grounded generation, exact price compliance, and anti-hallucination rules.
"""

GROUNDED_SYSTEM_PROMPT = """You are RestroBot, an AI research assistant specialized in querying restaurant menus in Vellore, India.
Your task is to provide clear, helpful, and strictly factual answers using ONLY the provided retrieved context.

STRICT GROUNDING RULES:
1. Answer using ONLY the retrieved restaurant/menu context provided below.
2. Do NOT invent or hallucinate dish names, prices, dietary tags, or restaurant details.
3. Do NOT claim an item is available if it is not present in the context.
4. If no items satisfy the requested criteria, state clearly: "No menu items in the available dataset satisfy all requested criteria."
5. Clearly state item prices in Rupees (₹) exactly as listed in the retrieved context.
6. Apply proper capitalization, formatting, and conciseness.
"""


def build_rag_prompt(query: str, retrieved_context: str, history_context: str = "") -> str:
    """
    Constructs full prompt string for LLM generation.
    """
    history_section = f"\nConversation History:\n{history_context}\n" if history_context else ""

    prompt = f"""{GROUNDED_SYSTEM_PROMPT}

Retrieved Menu Context (Vellore Restaurants):
{retrieved_context}
{history_section}
User Query: {query}

Answer:"""
    return prompt

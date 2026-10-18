"""
Query Parser and Intent Decomposer for RestroBot.
Decomposes natural language queries into semantic intent and explicit constraints.
"""

from query_processing.constraint_extractor import ConstraintExtractor


class QueryParser:
    @staticmethod
    def parse_query(query: str) -> dict:
        """
        Parses a query into a structured object containing raw text, intent, and extracted constraints.
        """
        constraints = ConstraintExtractor.extract_constraints(query)
        
        # Determine intent
        intent = "general_search"
        q_lower = query.lower()
        
        if any(k in q_lower for k in ["cheapest", "price", "budget", "under", "below"]):
            intent = "price_constrained_search"
        elif any(k in q_lower for k in ["veg", "vegetarian", "non-veg", "spicy"]):
            intent = "dietary_spice_search"
        elif constraints.get("restaurant"):
            intent = "restaurant_specific_search"
        elif constraints.get("food_type"):
            intent = "item_category_search"

        return {
            "query_text": query,
            "intent": intent,
            "constraints": constraints,
        }

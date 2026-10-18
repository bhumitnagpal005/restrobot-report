import re
from typing import Dict, Any, Optional
from backend.app.constraints.schema import ExtractedConstraints

RESTAURANTS_KNOWN = [
    "kfc", "domino", "dominos", "pizza hut", "wow momo", "zorko",
    "saleem", "saleem punjabi dhaba", "kailash parbat", "frozen bottle",
    "uncle peter", "lassi house", "limra"
]

CATEGORIES_KNOWN = [
    "pizza", "burger", "biryani", "roll", "rolls", "momo", "momos",
    "pancake", "shake", "shakes", "lassi", "pasta", "wings", "dosa",
    "thali", "rice", "curry", "beverage", "dessert"
]

CUISINES_KNOWN = [
    "italian", "chinese", "north indian", "south indian", "punjabi",
    "american", "fast food", "continental"
]

class ConstraintExtractor:
    """
    Regex and heuristic-based constraint extractor for conversational food queries.
    Distinguishes hard numerical/categorical constraints from soft semantic keywords.
    """
    @staticmethod
    def extract(query: str, session_context: Optional[Dict[str, Any]] = None) -> ExtractedConstraints:
        q_lower = query.lower().strip()
        hard_keys = []
        
        # 1. Price constraint extraction
        max_price = None
        min_price = None
        
        # Pattern: under / below / less than / max / <= 200, ₹200, rs 200, 200 rs
        max_price_match = re.search(r"(?:under|below|less than|max|within|<=|budget of)?\s*(?:₹|rs\.?|inr)?\s*(\d+)\s*(?:rs|rupees|inr)?", q_lower)
        if max_price_match:
            # Verify context trigger for max price
            text_around = q_lower[max(0, max_price_match.start() - 15):min(len(q_lower), max_price_match.end() + 15)]
            if any(kw in text_around for kw in ["under", "below", "less", "max", "within", "<=", "budget", "cheap"]):
                try:
                    max_price = float(max_price_match.group(1))
                    hard_keys.append("max_price")
                except ValueError:
                    pass
            elif not any(kw in text_around for kw in ["above", "more", "min"]):
                # Default numeric token if under/below context
                if re.search(r"(?:under|below|less|max|\b<=\b)", q_lower):
                    try:
                        max_price = float(max_price_match.group(1))
                        hard_keys.append("max_price")
                    except ValueError:
                        pass
        
        min_price_match = re.search(r"(?:above|more than|atleast|min|>=)\s*(?:₹|rs\.?|inr)?\s*(\d+)", q_lower)
        if min_price_match:
            try:
                min_price = float(min_price_match.group(1))
                hard_keys.append("min_price")
            except ValueError:
                pass

        # 2. Dietary preference extraction
        dietary_preference = None
        if "non-veg" in q_lower or "non veg" in q_lower or "non vegetarian" in q_lower or "chicken" in q_lower or "mutton" in q_lower:
            dietary_preference = "non-vegetarian"
            hard_keys.append("dietary_preference")
        elif "vegetarian" in q_lower or "veg" in q_lower or "pure veg" in q_lower or "paneer" in q_lower:
            # Check non-veg wasn't negated or part of non-veg
            if "non" not in q_lower:
                dietary_preference = "vegetarian"
                hard_keys.append("dietary_preference")

        # 3. Spice level extraction
        spice_level = None
        if "extra spicy" in q_lower or "fiery" in q_lower or "very spicy" in q_lower:
            spice_level = "extra spicy"
            hard_keys.append("spice_level")
        elif "spicy" in q_lower or "hot" in q_lower:
            spice_level = "spicy"
            hard_keys.append("spice_level")
        elif "mild" in q_lower or "sweet" in q_lower:
            spice_level = "mild"
            hard_keys.append("spice_level")

        # 4. Restaurant extraction
        restaurant_name = None
        for rest in RESTAURANTS_KNOWN:
            if rest in q_lower:
                restaurant_name = rest.title()
                hard_keys.append("restaurant_name")
                break

        # 5. Food item / Category extraction
        category = None
        food_item = None
        for cat in CATEGORIES_KNOWN:
            if cat in q_lower:
                category = cat.capitalize()
                food_item = cat
                hard_keys.append("category")
                break

        # 6. Cuisine extraction
        cuisine = None
        for cuis in CUISINES_KNOWN:
            if cuis in q_lower:
                cuisine = cuis.title()
                hard_keys.append("cuisine")
                break

        # 7. Location extraction
        location = None
        if "vellore" in q_lower or "katpadi" in q_lower or "gandhi nagar" in q_lower or "delhi" in q_lower:
            if "katpadi" in q_lower:
                location = "Katpadi"
            elif "gandhi nagar" in q_lower:
                location = "Gandhi Nagar"
            elif "delhi" in q_lower:
                location = "Delhi"
            else:
                location = "Vellore"
            hard_keys.append("location")

        # Contextual inheritance for conversational follow-ups (e.g. "Only spicy ones")
        if session_context and isinstance(session_context, dict):
            prev_constraints = session_context.get("last_constraints")
            if prev_constraints and isinstance(prev_constraints, ExtractedConstraints):
                if not dietary_preference and prev_constraints.dietary_preference:
                    dietary_preference = prev_constraints.dietary_preference
                if max_price is None and prev_constraints.max_price is not None:
                    max_price = prev_constraints.max_price
                if not restaurant_name and prev_constraints.restaurant_name:
                    restaurant_name = prev_constraints.restaurant_name
                if not category and prev_constraints.category:
                    category = prev_constraints.category

        return ExtractedConstraints(
            dietary_preference=dietary_preference,
            max_price=max_price,
            min_price=min_price,
            spice_level=spice_level,
            restaurant_name=restaurant_name,
            cuisine=cuisine,
            category=category,
            location=location,
            food_item=food_item,
            hard_constraints=list(set(hard_keys))
        )

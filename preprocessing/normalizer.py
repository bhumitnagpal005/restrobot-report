import re
from typing import Any, Tuple

def normalize_price(val: Any) -> float:
    """
    Normalizes numeric price representation.
    """
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    
    s = str(val).strip().replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)", s)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return 0.0
    return 0.0

def normalize_diet(diet_str: str, item_name: str = "", description: str = "") -> str:
    """
    Standardizes dietary preference to 'vegetarian' or 'non-vegetarian'.
    """
    combined = f"{diet_str} {item_name} {description}".lower()
    
    non_veg_indicators = [
        "non-veg", "non veg", "non-vegetarian", "chicken", "mutton", "egg",
        "fish", "prawn", "seafood", "beef", "pork", "wings", "pepperoni", "bacon", "shawarma"
    ]
    if any(kw in combined for kw in non_veg_indicators):
        return "non-vegetarian"
        
    veg_indicators = ["veg", "vegetarian", "pure veg", "paneer", "tofu", "mushroom", "cheese", "dal", "subz", "chole", "dosa"]
    if any(kw in combined for kw in veg_indicators):
        return "vegetarian"
        
    if "non" in str(diet_str).lower():
        return "non-vegetarian"
    return "vegetarian"

def normalize_spice_level(spice_str: str, text_context: str = "") -> str:
    s = f"{spice_str} {text_context}".lower()
    if "extra spicy" in s or "fiery" in s or "very spicy" in s or "hot & spicy" in s:
        return "extra spicy"
    elif "spicy" in s or "hot" in s or "schezwan" in s or "peri peri" in s:
        return "spicy"
    elif "medium" in s or "mildly" in s:
        return "medium"
    elif "mild" in s or "sweet" in s:
        return "mild"
    return "normal"

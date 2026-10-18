import re
from typing import Dict, Any, Tuple

def normalize_whitespace(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.split()).strip()

def normalize_price(val: Any) -> float:
    """
    Normalizes price formats into float.
    Examples: '₹199' -> 199.0, 'Rs. 199' -> 199.0, 'INR 250.50' -> 250.5
    """
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    
    s = str(val).strip()
    # Match first numeric sequence with optional decimal point
    match = re.search(r"(\d+(?:\.\d+)?)", s.replace(",", ""))
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return 0.0
    return 0.0

def normalize_diet(name: str, description: str, raw_diet: str = "") -> Tuple[bool, bool, str]:
    """
    Returns (is_vegetarian, is_non_vegetarian, normalized_label)
    """
    combined = f"{name} {description} {raw_diet}".lower()
    
    # Check explicit non-veg indicators first
    non_veg_keywords = [
        "non-veg", "non veg", "non-vegetarian", "chicken", "mutton", "egg",
        "fish", "prawn", "seafood", "beef", "pork", "wings", "pepperoni", "bacon"
    ]
    is_non_veg = any(kw in combined for kw in non_veg_keywords)
    
    veg_keywords = ["veg", "vegetarian", "pure veg", "paneer", "tofu", "mushroom", "cheese", "dal", "subz"]
    is_veg = any(kw in combined for kw in veg_keywords) and not is_non_veg
    
    if is_non_veg:
        return False, True, "non-vegetarian"
    elif is_veg:
        return True, False, "vegetarian"
    
    # Default fallback check on raw_diet
    if "non" in str(raw_diet).lower():
        return False, True, "non-vegetarian"
    elif "veg" in str(raw_diet).lower():
        return True, False, "vegetarian"
    
    # Default if unspecified
    return True, False, "vegetarian"

def normalize_spice_level(text: str) -> str:
    """
    Standardizes spice level to: mild, medium, spicy, extra spicy, or normal.
    """
    s = text.lower()
    if "extra spicy" in s or "very spicy" in s or "hot & spicy" in s or "fiery" in s:
        return "extra spicy"
    elif "spicy" in s or "hot" in s or "schezwan" in s or "peri peri" in s:
        return "spicy"
    elif "medium" in s or "mildly" in s:
        return "medium"
    elif "mild" in s or "sweet" in s:
        return "mild"
    return "normal"

def normalize_cuisine(cuisine: str, item_name: str = "") -> str:
    c = cuisine.lower()
    combined = f"{cuisine} {item_name}".lower()
    if "italian" in combined or "pizza" in combined or "pasta" in combined:
        return "Italian"
    elif "chinese" in combined or "momo" in combined or "noodle" in combined or "manchurian" in combined:
        return "Chinese"
    elif "north indian" in combined or "punjabi" in combined or "dhaba" in combined or "biryani" in combined or "tikka" in combined or "naan" in combined:
        return "North Indian"
    elif "south indian" in combined or "dosa" in combined or "idli" in combined:
        return "South Indian"
    elif "american" in combined or "burger" in combined or "fries" in combined or "pancake" in combined:
        return "American / Fast Food"
    elif "beverage" in combined or "drink" in combined or "shake" in combined or "lassi" in combined or "dessert" in combined:
        return "Beverages & Desserts"
    return "Multi-Cuisine" if not cuisine else cuisine.title()

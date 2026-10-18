"""
Constraint Extractor for RestroBot.
Parses natural language queries into structured search constraints using regex, dictionary mappings, and LLM fallback.
"""

import re
import json
import pandas as pd


class ConstraintExtractor:
    # Known restaurants in Vellore dataset
    KNOWN_RESTAURANTS = [
        "KFC", "Domino's Pizza", "Pizza Hut", "Zorko", "Uncle Peter's Pancakes",
        "Wow! Momo", "Limra Garden Restaurant", "Lassi House", "Saleem Punjabi Dhaba",
        "Kailash Parbat", "Frozen Bottle", "Hundreds Heritage", "Pastel Poetry"
    ]

    # Known food categories / types
    FOOD_TYPES = [
        "burger", "pizza", "roll", "paneer", "chicken", "biryani", "momo",
        "pancake", "lassi", "shake", "fries", "beverage", "combo", "meal",
        "noodle", "pasta", "thali", "rice"
    ]

    @classmethod
    def extract_constraints(cls, query: str) -> dict:
        """
        Extracts structured constraint dictionary from query string.
        Schema:
            {
                "food_type": str | None,
                "diet": str | None,         # "vegetarian", "non-vegetarian", or None
                "spice_level": str | None,  # "spicy", "medium", "mild", or None
                "min_price": float | None,
                "max_price": float | None,
                "restaurant": str | None,
                "location": str | None,
            }
        """
        constraints = {
            "food_type": None,
            "diet": None,
            "spice_level": None,
            "min_price": None,
            "max_price": None,
            "restaurant": None,
            "location": None,
        }
        
        if not query:
            return constraints
        
        q_lower = query.lower()

        # ------------------------------------------------------------- #
        # 1. Price Constraints (Regex)                                  #
        # ------------------------------------------------------------- #
        # Max price: "under 200", "below ₹180", "less than rs 150", "under ₹200", "maximum 250"
        max_p_match = re.search(
            r"(?:under|below|less than|max|maximum|within|budget of|upto|up to)\s*(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)",
            q_lower
        )
        if max_p_match:
            try:
                constraints["max_price"] = float(max_p_match.group(1))
            except ValueError:
                pass
        
        # Min price: "above 100", "more than ₹150", "minimum 200"
        min_p_match = re.search(
            r"(?:above|more than|over|min|minimum|atleast|at least)\s*(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)",
            q_lower
        )
        if min_p_match:
            try:
                constraints["min_price"] = float(min_p_match.group(1))
            except ValueError:
                pass

        # Direct rupee pattern fallback if max_price is not set yet
        if constraints["max_price"] is None:
            r_match = re.search(r"(?:under|below|<=)\s*₹?\s*(\d+)", q_lower)
            if r_match:
                constraints["max_price"] = float(r_match.group(1))

        # ------------------------------------------------------------- #
        # 2. Dietary Constraints                                        #
        # ------------------------------------------------------------- #
        if re.search(r"\b(non-veg|nonveg|non veg|chicken|mutton|egg|fish|meat)\b", q_lower):
            constraints["diet"] = "non-vegetarian"
        elif re.search(r"\b(veg|vegetarian|pure veg)\b", q_lower):
            constraints["diet"] = "vegetarian"

        # ------------------------------------------------------------- #
        # 3. Spice Level                                                #
        # ------------------------------------------------------------- #
        if re.search(r"\b(spicy|hot|fiery|peri peri|chilli)\b", q_lower):
            constraints["spice_level"] = "spicy"
        elif re.search(r"\b(mild|sweet|plain)\b", q_lower):
            constraints["spice_level"] = "mild"
        elif re.search(r"\b(medium|normal)\b", q_lower):
            constraints["spice_level"] = "medium"

        # ------------------------------------------------------------- #
        # 4. Restaurant Constraint                                      #
        # ------------------------------------------------------------- #
        for rest in cls.KNOWN_RESTAURANTS:
            # Check keywords
            rest_clean = rest.lower().replace("'s", "").replace("!", "")
            words = [w for w in rest_clean.split() if len(w) > 2]
            for w in words:
                if w in q_lower:
                    constraints["restaurant"] = rest
                    break
            if constraints["restaurant"]:
                break

        # ------------------------------------------------------------- #
        # 5. Location Constraint                                        #
        # ------------------------------------------------------------- #
        if "vit" in q_lower or "katpadi" in q_lower:
            constraints["location"] = "Katpadi, Vellore"
        elif "vellore" in q_lower:
            constraints["location"] = "Vellore, India"

        # ------------------------------------------------------------- #
        # 6. Food Type / Category                                       #
        # ------------------------------------------------------------- #
        for ft in cls.FOOD_TYPES:
            if ft in q_lower:
                constraints["food_type"] = ft
                break

        return constraints

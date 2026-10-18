from typing import Tuple, List, Dict, Any
from backend.app.constraints.schema import ExtractedConstraints

class ConstraintValidator:
    """
    Evaluates candidate restaurant/menu items against extracted query constraints.
    Returns:
        is_valid: bool (True if all hard constraints pass)
        satisfaction_score: float (0.0 to 1.0)
        violations: List[str] (Descriptions of any failed constraints)
    """
    @staticmethod
    def validate(item: Dict[str, Any], constraints: ExtractedConstraints) -> Tuple[bool, float, List[str]]:
        violations = []
        total_checks = 0
        passed_checks = 0

        item_price = float(item.get("price", 0.0))
        is_veg = bool(item.get("is_vegetarian", False))
        is_non_veg = bool(item.get("is_non_vegetarian", False))
        spice_level = str(item.get("spice_level", "")).lower()
        restaurant_name = str(item.get("restaurant_name", "")).lower()
        item_name = str(item.get("item_name", "")).lower()
        category = str(item.get("category", "")).lower()
        cuisine = str(item.get("cuisine", "")).lower()

        # 1. Price Max Constraint (Hard)
        if constraints.max_price is not None:
            total_checks += 1
            if item_price <= constraints.max_price:
                passed_checks += 1
            else:
                violations.append(f"Price ₹{item_price:.0f} exceeds max ₹{constraints.max_price:.0f}")

        # 2. Price Min Constraint (Hard)
        if constraints.min_price is not None:
            total_checks += 1
            if item_price >= constraints.min_price:
                passed_checks += 1
            else:
                violations.append(f"Price ₹{item_price:.0f} is below min ₹{constraints.min_price:.0f}")

        # 3. Dietary Preference Constraint (Strict Hard Constraint)
        if constraints.dietary_preference:
            total_checks += 1
            req_diet = constraints.dietary_preference.lower()
            if req_diet == "vegetarian":
                if is_veg and not is_non_veg:
                    passed_checks += 1
                else:
                    violations.append("Item is non-vegetarian (requested vegetarian)")
            elif req_diet == "non-vegetarian":
                if is_non_veg:
                    passed_checks += 1
                else:
                    violations.append("Item is vegetarian (requested non-vegetarian)")

        # 4. Restaurant Constraint (Hard if specified)
        if constraints.restaurant_name:
            total_checks += 1
            req_rest = constraints.restaurant_name.lower()
            if req_rest in restaurant_name or restaurant_name in req_rest:
                passed_checks += 1
            else:
                violations.append(f"Restaurant '{item.get('restaurant_name')}' does not match requested '{constraints.restaurant_name}'")

        # 5. Spice Level Constraint (Soft / Hard)
        if constraints.spice_level:
            total_checks += 1
            req_spice = constraints.spice_level.lower()
            if req_spice in spice_level or spice_level in req_spice:
                passed_checks += 1
            elif req_spice == "spicy" and spice_level in ["spicy", "extra spicy", "medium"]:
                passed_checks += 1
            else:
                violations.append(f"Spice level '{spice_level}' does not match '{constraints.spice_level}'")

        # 6. Category / Food item Constraint
        if constraints.category or constraints.food_item:
            req_cat = (constraints.category or constraints.food_item).lower()
            total_checks += 1
            if req_cat in category or req_cat in item_name or item_name in req_cat:
                passed_checks += 1
            else:
                violations.append(f"Item '{item.get('item_name')}' does not match category '{req_cat}'")

        if total_checks == 0:
            return True, 1.0, []

        is_valid = (len(violations) == 0)
        satisfaction_score = float(passed_checks) / float(total_checks)
        return is_valid, satisfaction_score, violations

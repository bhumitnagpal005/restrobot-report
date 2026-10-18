from typing import List, Dict, Any

class ContextBuilder:
    @staticmethod
    def build_context(items: List[Dict[str, Any]]) -> str:
        if not items:
            return "No relevant menu items or restaurant details were retrieved."
        
        lines = []
        for idx, item in enumerate(items, 1):
            rest_name = item.get("restaurant_name", "Unknown Restaurant")
            name = item.get("item_name", "Unnamed Item")
            price = item.get("price", 0.0)
            category = item.get("category", "Main")
            is_veg = item.get("is_vegetarian", False)
            diet = "Vegetarian" if is_veg else ("Non-Vegetarian" if item.get("is_non_vegetarian") else "Unspecified")
            spice = item.get("spice_level", "Normal")
            desc = item.get("description", "")
            
            line = f"{idx}. [{rest_name}] {name} - ₹{price:.0f} | Category: {category} | Diet: {diet} | Spice: {spice}"
            if desc:
                line += f" | Description: {desc}"
            lines.append(line)
            
        return "\n".join(lines)

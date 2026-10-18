import json
from pathlib import Path
from typing import List, Dict, Any
from backend.ingestion.normalizers import (
    normalize_whitespace,
    normalize_price,
    normalize_diet,
    normalize_spice_level,
    normalize_cuisine
)

def clean_menu_item(raw_item: Dict[str, Any], restaurant_info: Dict[str, Any], item_idx: int = 0) -> Dict[str, Any]:
    """
    Cleans and normalizes a raw menu item dictionary.
    Preserves both original raw values and normalized values.
    """
    raw_name = str(raw_item.get("name") or raw_item.get("item_name") or "").strip()
    raw_desc = str(raw_item.get("description") or "").strip()
    raw_price = raw_item.get("price") or raw_item.get("cost") or 0.0
    raw_category = str(raw_item.get("category") or "Main Course").strip()
    raw_diet = str(raw_item.get("diet") or raw_item.get("food_type") or "").strip()

    name = normalize_whitespace(raw_name)
    description = normalize_whitespace(raw_desc)
    price = normalize_price(raw_price)
    category = normalize_whitespace(raw_category)
    
    is_veg, is_non_veg, diet_label = normalize_diet(name, description, raw_diet)
    spice_level = normalize_spice_level(f"{name} {description}")
    cuisine = normalize_cuisine(restaurant_info.get("cuisine", ""), name)

    rest_id = str(restaurant_info.get("id") or restaurant_info.get("restaurant_id") or "rest_001")
    raw_id = raw_item.get("id")
    if raw_id:
        item_id = str(raw_id)
    else:
        unique_hash = abs(hash(f"{name}_{category}_{price}_{item_idx}")) & 0xffffffff
        item_id = f"{rest_id}_{item_idx:03d}_{unique_hash}"

    return {
        "id": item_id,
        "restaurant_id": rest_id,
        "item_name": name,
        "category": category,
        "price": price,
        "description": description,
        "is_vegetarian": is_veg,
        "is_non_vegetarian": is_non_veg,
        "spice_level": spice_level,
        "cuisine": cuisine,
        "availability": bool(raw_item.get("available", True)),
        # Document text for RAG indexing
        "document_text": f"Restaurant: {restaurant_info.get('name', 'Unknown')} | Item: {name} | Category: {category} | Price: ₹{price:.0f} | Diet: {diet_label} | Spice: {spice_level} | Cuisine: {cuisine} | Description: {description}",
        "raw_data": {
            "raw_name": raw_name,
            "raw_price": raw_price,
            "raw_category": raw_category,
            "raw_diet": raw_diet,
            "raw_desc": raw_desc
        }
    }

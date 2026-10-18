import pandas as pd
from typing import Dict, Any
from preprocessing.cleaner import clean_text
from preprocessing.normalizer import normalize_price, normalize_diet, normalize_spice_level

def create_document_string(item: Dict[str, Any]) -> str:
    """
    Creates structured document text representation for indexing and retrieval.
    """
    restaurant = item.get("restaurant", "Unknown Restaurant")
    location = item.get("location", "Vellore")
    cuisine = item.get("cuisine", "General")
    category = item.get("category", "Main Course")
    item_name = item.get("item_name", "Menu Item")
    price = normalize_price(item.get("price", 0))
    diet = normalize_diet(str(item.get("diet", "")), item_name, str(item.get("description", "")))
    spice = normalize_spice_level(str(item.get("spice_level", "")), f"{item_name} {item.get('description', '')}")
    description = item.get("description", "")
    ingredients = item.get("ingredients", "")

    doc = (
        f"Restaurant: {restaurant}\n"
        f"Location: {location}\n"
        f"Cuisine: {cuisine}\n"
        f"Category: {category}\n"
        f"Item: {item_name}\n"
        f"Price: ₹{price:.0f}\n"
        f"Diet: {diet.capitalize()}\n"
        f"Spice Level: {spice.capitalize()}\n"
        f"Description: {description}\n"
        f"Ingredients: {ingredients}"
    )
    return doc

def process_dataset(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes raw dataset DataFrame, cleans fields, creates document representations.
    """
    processed_records = []
    for idx, row in raw_df.iterrows():
        item = row.to_dict()
        price = normalize_price(item.get("price"))
        diet = normalize_diet(str(item.get("diet", "")), str(item.get("item_name", "")), str(item.get("description", "")))
        spice = normalize_spice_level(str(item.get("spice_level", "")), f"{item.get('item_name', '')} {item.get('description', '')}")
        
        doc_str = create_document_string({
            "restaurant": item.get("restaurant"),
            "location": item.get("location"),
            "cuisine": item.get("cuisine"),
            "category": item.get("category"),
            "item_name": item.get("item_name"),
            "price": price,
            "diet": diet,
            "spice_level": spice,
            "description": item.get("description"),
            "ingredients": item.get("ingredients")
        })

        record = {
            "item_id": f"item_{idx+1:03d}",
            "restaurant": item.get("restaurant"),
            "location": item.get("location"),
            "cuisine": item.get("cuisine"),
            "category": item.get("category"),
            "item_name": item.get("item_name"),
            "price": price,
            "diet": diet,
            "spice_level": spice,
            "description": item.get("description"),
            "ingredients": item.get("ingredients"),
            "document_text": doc_str,
            "clean_search_text": clean_text(f"{item.get('restaurant')} {item.get('category')} {item.get('item_name')} {diet} {spice} {item.get('description')} {item.get('ingredients')}")
        }
        processed_records.append(record)

    processed_df = pd.DataFrame(processed_records)
    return processed_df

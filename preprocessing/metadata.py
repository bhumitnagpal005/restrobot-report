"""
Metadata Extractor and Document Builder for RestroBot.
Transforms raw menu JSON records into structured DataFrames and clean document representations.
"""

import json
from pathlib import Path
import pandas as pd
from preprocessing.cleaner import clean_text, clean_restaurant_name
from preprocessing.normalizer import normalize_price, normalize_diet, normalize_spice_level, apply_synonyms


def process_raw_json_file(file_path: Path) -> list[dict]:
    """
    Parses a single restaurant raw JSON file into a list of structured menu item dicts.
    """
    items = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[Warning] Failed to load JSON {file_path}: {e}")
        return items

    rest_info = data.get("restaurant", {})
    raw_name = rest_info.get("name", file_path.stem.replace("_menu", "").replace("_", " "))
    restaurant_name = clean_restaurant_name(raw_name)
    
    # Location defaults to Katpadi / Vellore, India
    raw_location = rest_info.get("location", "")
    location = "Katpadi, Vellore" if "katpadi" in raw_location.lower() else "Vellore, India"
    cuisine = rest_info.get("cuisine", "Multi-Cuisine")

    menu_categories = data.get("menu", [])
    for cat_block in menu_categories:
        category = clean_text(cat_block.get("category", "General"))
        for item in cat_block.get("items", []):
            item_name = clean_text(item.get("name", ""))
            if not item_name:
                continue
            
            raw_price = item.get("price", "0")
            price = normalize_price(raw_price)
            
            raw_desc = item.get("description", "")
            description = apply_synonyms(clean_text(raw_desc))
            
            raw_diet = item.get("veg_nonveg", item.get("type", ""))
            diet = normalize_diet(raw_diet if raw_diet else (item_name + " " + description))
            
            raw_spice = item.get("spice_level", "")
            spice_level = normalize_spice_level(raw_spice if raw_spice else description)

            # Build canonical text document representation
            doc_text = (
                f"Restaurant: {restaurant_name}. Location: {location}. Cuisine: {cuisine}. "
                f"Category: {category}. Item: {item_name}. Price: ₹{price:.0f}. "
                f"Diet: {diet}. Spice: {spice_level}. Description: {description}."
            )

            items.append({
                "restaurant_name": restaurant_name,
                "location": location,
                "cuisine": cuisine,
                "menu_category": category,
                "item_name": item_name,
                "price": price,
                "description": description,
                "diet": diet,
                "spice_level": spice_level,
                "document_text": doc_text,
            })

    return items


def load_dataset(raw_dir: Path, output_csv: Path) -> pd.DataFrame:
    """
    Loads all JSON files from raw_dir, builds structured dataset DataFrame, saves to output_csv.
    """
    all_items = []
    json_files = list(raw_dir.glob("*.json"))
    
    for jf in json_files:
        items = process_raw_json_file(jf)
        all_items.extend(items)

    if not all_items:
        print("[Warning] No raw JSON items found. Creating synthetic fallback dataset for Vellore...")
        all_items = get_sample_vellore_dataset()

    df = pd.DataFrame(all_items)
    df.drop_duplicates(subset=["restaurant_name", "item_name"], inplace=True)
    
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"Dataset successfully saved with {len(df)} menu items to {output_csv}")
    return df


def get_sample_vellore_dataset() -> list[dict]:
    """
    Fallback sample dataset for Vellore restaurants.
    """
    sample = [
        {
            "restaurant_name": "KFC",
            "location": "Katpadi, Vellore",
            "cuisine": "Fast Food",
            "menu_category": "Veg Burgers and Meals",
            "item_name": "veg zinger burger",
            "price": 180.0,
            "description": "crispy vegetarian patty with fresh lettuce and mayo in toasted sesame bun",
            "diet": "vegetarian",
            "spice_level": "medium",
            "document_text": "Restaurant: KFC. Location: Katpadi, Vellore. Cuisine: Fast Food. Category: Veg Burgers and Meals. Item: veg zinger burger. Price: ₹180. Diet: vegetarian. Spice: medium. Description: crispy vegetarian patty with fresh lettuce and mayo in toasted sesame bun."
        },
        {
            "restaurant_name": "KFC",
            "location": "Katpadi, Vellore",
            "cuisine": "Fast Food",
            "menu_category": "Veg Burgers and Meals",
            "item_name": "chatpata chana veg burger",
            "price": 140.0,
            "description": "delicious Indian chatpata chana patty with spicy tangy sauce",
            "diet": "vegetarian",
            "spice_level": "spicy",
            "document_text": "Restaurant: KFC. Location: Katpadi, Vellore. Cuisine: Fast Food. Category: Veg Burgers and Meals. Item: chatpata chana veg burger. Price: ₹140. Diet: vegetarian. Spice: spicy. Description: delicious Indian chatpata chana patty with spicy tangy sauce."
        },
        {
            "restaurant_name": "Pizza Hut",
            "location": "Vellore, India",
            "cuisine": "Italian",
            "menu_category": "Pizzas",
            "item_name": "margherita pizza",
            "price": 199.0,
            "description": "classic cheese pizza with 100% mozzarella and tangy tomato sauce",
            "diet": "vegetarian",
            "spice_level": "mild",
            "document_text": "Restaurant: Pizza Hut. Location: Vellore, India. Cuisine: Italian. Category: Pizzas. Item: margherita pizza. Price: ₹199. Diet: vegetarian. Spice: mild. Description: classic cheese pizza with 100% mozzarella and tangy tomato sauce."
        },
        {
            "restaurant_name": "Domino's Pizza",
            "location": "Vellore, India",
            "cuisine": "Italian",
            "menu_category": "Pizzas",
            "item_name": "peppy paneer pizza",
            "price": 250.0,
            "description": "flavorful paneer tikka with crisp capsicum and spicy red paprika",
            "diet": "vegetarian",
            "spice_level": "spicy",
            "document_text": "Restaurant: Domino's Pizza. Location: Vellore, India. Cuisine: Italian. Category: Pizzas. Item: peppy paneer pizza. Price: ₹250. Diet: vegetarian. Spice: spicy. Description: flavorful paneer tikka with crisp capsicum and spicy red paprika."
        },
        {
            "restaurant_name": "Limra Garden Restaurant",
            "location": "Katpadi, Vellore",
            "cuisine": "North Indian",
            "menu_category": "Rolls",
            "item_name": "paneer tikka roll",
            "price": 150.0,
            "description": "spicy grilled paneer wrapped in layered laccha paratha with mint chutney",
            "diet": "vegetarian",
            "spice_level": "spicy",
            "document_text": "Restaurant: Limra Garden Restaurant. Location: Katpadi, Vellore. Cuisine: North Indian. Category: Rolls. Item: paneer tikka roll. Price: ₹150. Diet: vegetarian. Spice: spicy. Description: spicy grilled paneer wrapped in layered laccha paratha with mint chutney."
        },
        {
            "restaurant_name": "Saleem Punjabi Dhaba",
            "location": "Vellore, India",
            "cuisine": "Punjabi",
            "menu_category": "Rolls",
            "item_name": "chicken kathi roll",
            "price": 170.0,
            "description": "succulent spicy chicken tikka pieces wrapped in hot paratha",
            "diet": "non-vegetarian",
            "spice_level": "spicy",
            "document_text": "Restaurant: Saleem Punjabi Dhaba. Location: Vellore, India. Cuisine: Punjabi. Category: Rolls. Item: chicken kathi roll. Price: ₹170. Diet: non-vegetarian. Spice: spicy. Description: succulent spicy chicken tikka pieces wrapped in hot paratha."
        }
    ]
    return sample

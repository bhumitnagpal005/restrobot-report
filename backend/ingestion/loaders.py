import json
import os
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from backend.app import config
from backend.ingestion.cleaners import clean_menu_item
from backend.ingestion.normalizers import normalize_cuisine
from backend.app.models.models import Restaurant, MenuItem

# Fallback / Sample restaurant data to guarantee standalone execution
SAMPLE_RESTAURANTS = [
    {
        "id": "kfc_001",
        "name": "KFC",
        "location": "Vellore Fort / Main Road",
        "address": "No. 12, Katpadi Main Road, Vellore",
        "cuisine": "American / Fast Food",
        "rating": 4.2,
        "phone": "+91-9876543210",
        "opening_hours": "10:00 AM - 11:00 PM"
    },
    {
        "id": "dominos_001",
        "name": "Domino's Pizza",
        "location": "Gandhi Nagar, Vellore",
        "address": "Shop 4, Silk Mill Stop, Gandhi Nagar, Vellore",
        "cuisine": "Italian / Fast Food",
        "rating": 4.4,
        "phone": "+91-9876543211",
        "opening_hours": "11:00 AM - 12:00 AM"
    },
    {
        "id": "zorko_001",
        "name": "Zorko Brand of Foodies",
        "location": "Katpadi, Vellore",
        "address": "Near VIT Main Gate, Katpadi, Vellore",
        "cuisine": "Fast Food & Shakes",
        "rating": 4.3,
        "phone": "+91-9876543212",
        "opening_hours": "11:00 AM - 11:00 PM"
    },
    {
        "id": "saleem_dhaba_001",
        "name": "Saleem Punjabi Dhaba",
        "location": "Green Circle, Vellore",
        "address": "Opp. New Bus Stand, Green Circle, Vellore",
        "cuisine": "North Indian / Punjabi",
        "rating": 4.5,
        "phone": "+91-9876543213",
        "opening_hours": "12:00 PM - 11:30 PM"
    },
    {
        "id": "kailash_parbat_001",
        "name": "Kailash Parbat Pure Veg",
        "location": "Gandhi Nagar, Vellore",
        "address": "1st Main Rd, Gandhi Nagar, Vellore",
        "cuisine": "North Indian / Pure Veg",
        "rating": 4.6,
        "phone": "+91-9876543214",
        "opening_hours": "08:00 AM - 10:30 PM"
    }
]

SAMPLE_MENU_ITEMS = [
    {
        "id": "kfc_item_01",
        "restaurant_id": "kfc_001",
        "item_name": "Veg Zinger Burger",
        "category": "Burgers",
        "price": 179.0,
        "description": "Crispy vegetable patty with fresh lettuce and creamy mayo in a toasted sesame bun.",
        "is_vegetarian": True,
        "is_non_vegetarian": False,
        "spice_level": "medium",
        "cuisine": "American / Fast Food",
        "availability": True,
        "raw_data": {"raw_name": "Veg Zinger Burger", "raw_price": 179}
    },
    {
        "id": "kfc_item_02",
        "restaurant_id": "kfc_001",
        "item_name": "Hot & Spicy Chicken Wings (4 pcs)",
        "category": "Chicken",
        "price": 249.0,
        "description": "Juicy chicken wings coated in hot and spicy breading and fried to perfection.",
        "is_vegetarian": False,
        "is_non_vegetarian": True,
        "spice_level": "spicy",
        "cuisine": "American / Fast Food",
        "availability": True,
        "raw_data": {"raw_name": "Hot & Spicy Chicken Wings", "raw_price": 249}
    },
    {
        "id": "dom_item_01",
        "restaurant_id": "dominos_001",
        "item_name": "Peppy Paneer Pizza (Medium)",
        "category": "Pizza",
        "price": 295.0,
        "description": "Flavorful paneer cubes, crisp capsicum, and spicy red pepper on a cheesy crust.",
        "is_vegetarian": True,
        "is_non_vegetarian": False,
        "spice_level": "spicy",
        "cuisine": "Italian",
        "availability": True,
        "raw_data": {"raw_name": "Peppy Paneer Pizza", "raw_price": 295}
    },
    {
        "id": "dom_item_02",
        "restaurant_id": "dominos_001",
        "item_name": "Veggie Paradise Pizza (Personal)",
        "category": "Pizza",
        "price": 199.0,
        "description": "Goldern corn, black olives, capsicum, and red paprika.",
        "is_vegetarian": True,
        "is_non_vegetarian": False,
        "spice_level": "mild",
        "cuisine": "Italian",
        "availability": True,
        "raw_data": {"raw_name": "Veggie Paradise Pizza", "raw_price": 199}
    },
    {
        "id": "sal_item_01",
        "restaurant_id": "saleem_dhaba_001",
        "item_name": "Special Chicken Biryani",
        "category": "Biryani",
        "price": 220.0,
        "description": "Aromatic basmati rice cooked with tender spicy chicken pieces and authentic Punjabi herbs.",
        "is_vegetarian": False,
        "is_non_vegetarian": True,
        "spice_level": "spicy",
        "cuisine": "North Indian",
        "availability": True,
        "raw_data": {"raw_name": "Special Chicken Biryani", "raw_price": 220}
    },
    {
        "id": "sal_item_02",
        "restaurant_id": "saleem_dhaba_001",
        "item_name": "Paneer Butter Masala & Naan Combo",
        "category": "Main Course",
        "price": 180.0,
        "description": "Rich creamy cottage cheese gravy served with 2 butter naans.",
        "is_vegetarian": True,
        "is_non_vegetarian": False,
        "spice_level": "normal",
        "cuisine": "North Indian",
        "availability": True,
        "raw_data": {"raw_name": "Paneer Butter Masala", "raw_price": 180}
    },
    {
        "id": "zorko_item_01",
        "restaurant_id": "zorko_001",
        "item_name": "Spicy Veg Roll",
        "category": "Rolls",
        "price": 120.0,
        "description": "Delicious stuffed wrap loaded with spicy paneer, crunchy veggies and zesty sauces.",
        "is_vegetarian": True,
        "is_non_vegetarian": False,
        "spice_level": "spicy",
        "cuisine": "Fast Food",
        "availability": True,
        "raw_data": {"raw_name": "Spicy Veg Roll", "raw_price": 120}
    },
    {
        "id": "zorko_item_02",
        "restaurant_id": "zorko_001",
        "item_name": "Spicy Chicken Roll",
        "category": "Rolls",
        "price": 140.0,
        "description": "Juicy grilled chicken roll with hot sauce, onions, and spicy mayo.",
        "is_vegetarian": False,
        "is_non_vegetarian": True,
        "spice_level": "spicy",
        "cuisine": "Fast Food",
        "availability": True,
        "raw_data": {"raw_name": "Spicy Chicken Roll", "raw_price": 140}
    }
]


class DataLoaderAdapter:
    """
    Adapter architecture supporting ingestion from JSON files, CSV files, or sample database seeds.
    """
    def __init__(self, raw_data_dir: Path = config.RAW_DATA_DIR):
        self.raw_data_dir = raw_data_dir

    def load_all_dataset(self) -> pd.DataFrame:
        restaurants, items = self.load_from_json_files()
        return pd.DataFrame(items)

    def load_from_json_files(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        restaurants = []
        menu_items = []
        
        if not self.raw_data_dir.exists():
            return SAMPLE_RESTAURANTS, SAMPLE_MENU_ITEMS
            
        json_files = list(self.raw_data_dir.glob("*.json"))
        if not json_files:
            return SAMPLE_RESTAURANTS, SAMPLE_MENU_ITEMS

        for idx, file_path in enumerate(json_files):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                rest_name = file_path.stem.replace("_menu", "").replace("_", " ").title()
                rest_id = f"rest_{idx+1:03d}"
                rest_info = {
                    "id": rest_id,
                    "name": rest_name,
                    "location": "Vellore",
                    "address": f"{rest_name}, Main Branch, Vellore",
                    "cuisine": normalize_cuisine("", rest_name),
                    "rating": 4.3,
                    "phone": "+91-9876543210",
                    "opening_hours": "10:00 AM - 11:00 PM"
                }
                restaurants.append(rest_info)

                # Parse menu items inside JSON
                items_list = data if isinstance(data, list) else data.get("items", data.get("menu", []))
                for item_idx, item in enumerate(items_list):
                    cleaned_item = clean_menu_item(item, rest_info, item_idx=item_idx)
                    menu_items.append(cleaned_item)
            except Exception as e:
                print(f"Error loading menu file {file_path.name}: {e}")

        # Ensure sample items are appended if list is sparse
        if len(menu_items) < 5:
            return SAMPLE_RESTAURANTS, SAMPLE_MENU_ITEMS
            
        return restaurants, menu_items

    def seed_database(self, db: Session) -> pd.DataFrame:
        """
        Seeds SQLite database and builds DataFrame for retrieval indexing.
        """
        restaurants_data, items_data = self.load_from_json_files()
        
        # Insert restaurants if missing
        for r_dict in restaurants_data:
            existing = db.query(Restaurant).filter(Restaurant.id == r_dict["id"]).first()
            if not existing:
                db_rest = Restaurant(
                    id=r_dict["id"],
                    name=r_dict["name"],
                    location=r_dict["location"],
                    address=r_dict.get("address"),
                    cuisine=r_dict.get("cuisine"),
                    rating=r_dict.get("rating", 4.0),
                    phone=r_dict.get("phone"),
                    opening_hours=r_dict.get("opening_hours")
                )
                db.add(db_rest)
        db.commit()

        # Insert menu items if missing
        records = []
        for i_dict in items_data:
            existing = db.query(MenuItem).filter(MenuItem.id == i_dict["id"]).first()
            if not existing:
                db_item = MenuItem(
                    id=i_dict["id"],
                    restaurant_id=i_dict["restaurant_id"],
                    item_name=i_dict["item_name"],
                    category=i_dict["category"],
                    price=i_dict["price"],
                    description=i_dict["description"],
                    is_vegetarian=i_dict["is_vegetarian"],
                    is_non_vegetarian=i_dict["is_non_vegetarian"],
                    spice_level=i_dict["spice_level"],
                    cuisine=i_dict["cuisine"],
                    availability=i_dict["availability"],
                    raw_data=i_dict.get("raw_data")
                )
                db.add(db_item)
            
            # Fetch restaurant name for document text
            rest_obj = db.query(Restaurant).filter(Restaurant.id == i_dict["restaurant_id"]).first()
            rest_name = rest_obj.name if rest_obj else "Restaurant"
            diet_label = "vegetarian" if i_dict["is_vegetarian"] else ("non-vegetarian" if i_dict["is_non_vegetarian"] else "general")
            
            doc_text = f"Restaurant: {rest_name} | Item: {i_dict['item_name']} | Category: {i_dict['category']} | Price: ₹{i_dict['price']:.0f} | Diet: {diet_label} | Spice: {i_dict['spice_level']} | Cuisine: {i_dict['cuisine']} | Description: {i_dict['description']}"
            
            records.append({
                "item_id": i_dict["id"],
                "restaurant_id": i_dict["restaurant_id"],
                "restaurant_name": rest_name,
                "item_name": i_dict["item_name"],
                "category": i_dict["category"],
                "price": i_dict["price"],
                "description": i_dict["description"],
                "is_vegetarian": i_dict["is_vegetarian"],
                "is_non_vegetarian": i_dict["is_non_vegetarian"],
                "spice_level": i_dict["spice_level"],
                "cuisine": i_dict["cuisine"],
                "availability": i_dict["availability"],
                "document_text": doc_text
            })
        db.commit()

        df = pd.DataFrame(records)
        df.to_csv(config.PROCESSED_DATA_DIR / "processed_menu.csv", index=False)
        return df

import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
from preprocessing.cleaner import clean_text
from preprocessing.normalizer import normalize_price, normalize_diet, normalize_spice_level

def test_clean_text():
    raw = "  Find Spicy Paneer Tikka! Under ₹200  "
    cleaned = clean_text(raw)
    assert "spicy paneer tikka" in cleaned
    assert "200" in cleaned

def test_normalize_price():
    assert normalize_price("180") == 180.0
    assert normalize_price("₹250.50") == 250.5
    assert normalize_price(199) == 199.0

def test_normalize_diet():
    assert normalize_diet("veg") == "vegetarian"
    assert normalize_diet("pure veg") == "vegetarian"
    assert normalize_diet("non veg") == "non-vegetarian"
    assert normalize_diet("", item_name="Chicken Biryani") == "non-vegetarian"

def test_normalize_spice_level():
    assert normalize_spice_level("extra spicy") == "extra spicy"
    assert normalize_spice_level("hot") == "spicy"
    assert normalize_spice_level("mild") == "mild"

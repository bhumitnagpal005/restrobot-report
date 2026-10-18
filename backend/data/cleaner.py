"""
Loads JSON menu files, normalises text, generates restaurant descriptions via Gemini,
and returns document strings for the RAG index.

Restaurant descriptions are cached in desc_cache.json so Gemini is only called
once per restaurant, not on every server start.
"""

import csv
import json
import os
import re
import time
from pathlib import Path

from google import genai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def _get_client():
    api_key = os.getenv("gemini_token") or os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()

_CACHE_FILE = os.path.join(os.path.dirname(__file__), "desc_cache.json")


# ------------------------------------------------------------------ #
# Description cache                                                  #
# ------------------------------------------------------------------ #

def _load_cache() -> dict[str, str]:
    if os.path.exists(_CACHE_FILE):
        with open(_CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict[str, str]) -> None:
    with open(_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def _get_description(name: str, cache: dict[str, str]) -> str:
    if name in cache:
        return cache[name]

    prompt = (
        f"Provide brief information about {name}, a restaurant in Vellore, India. "
        f"Include: operational hours, and the cuisine types it serves.\n"
        f"Format exactly as:\nMain Information: ...\nCuisines: ...\nOperational Hours: ..."
    )

    candidate_models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-flash-latest",
    ]
    max_retries_per_model = 2

    try:
        client = _get_client()
    except Exception as e:
        print(f"[Warning] Failed to initialize Gemini client: {e}")
        client = None

    if client:
        for model_name in candidate_models:
            for attempt in range(max_retries_per_model):
                try:
                    response = client.models.generate_content(
                        model=model_name, contents=prompt
                    )
                    if response and response.text:
                        response_text = response.text.strip()
                        cache[name] = response_text
                        _save_cache(cache)
                        time.sleep(2)  # Stay within rate limits
                        return response_text
                except Exception as e:
                    wait_time = 1
                    print(f"[Warning] API call failed for model '{model_name}' (Attempt {attempt + 1}/{max_retries_per_model}): {e}")
                    time.sleep(wait_time)

    # Fallback response if all API attempts fail so app startup doesn't crash
    fallback_text = (
        f"Main Information: A popular restaurant located in Vellore.\n"
        f"Cuisines: Multi-cuisine\n"
        f"Operational Hours: 8 AM to 11 PM"
    )
    cache[name] = fallback_text
    _save_cache(cache)
    return fallback_text


# ------------------------------------------------------------------ #
# Text helpers                                                       #
# ------------------------------------------------------------------ #

def _clean_text(text: str | None) -> str:
    if pd.isna(text):  # type: ignore[arg-type]
        return "unknown"
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9\s.₹\-/&,:()']", "", text)
    return re.sub(r"\s+", " ", text).strip()



def _normalize_price(price: str | None) -> str:
    if pd.isna(price):  # type: ignore[arg-type]
        return "0"
    price = re.sub(r"[^0-9.]", "", str(price))
    return price if price else "0"


_SYNONYMS = {
    r"\bnon-veg\b": "non vegetarian",
    r"\bnonveg\b": "non vegetarian",
    r"\bveg\b": "vegetarian",
    r"\bpizza'?s\b": "pizzas",
    r"\bcombo\b": "meal",
    r"\bspicy\b": "hot",
}


def _apply_synonyms(text: str) -> str:
    for pattern, replacement in _SYNONYMS.items():
        text = re.sub(pattern, replacement, text)
    return text


# ------------------------------------------------------------------ #
# Main loader                                                        #
# ------------------------------------------------------------------ #

def load_and_clean_menus_from_json(folder_path: str = "menu") -> list[str]:
    documents: list[str] = []
    cache = _load_cache()

    for file in Path(folder_path).glob("*.json"):
        with open(file, encoding="utf-8") as f:
            data = json.load(f)

        name = _clean_text(data.get("restaurant", {}).get("name", ""))
        location = _clean_text(data.get("restaurant", {}).get("location", ""))
        contact = _clean_text(data.get("restaurant", {}).get("contact", ""))

        response_text = _get_description(name, cache)
        lines = [l.strip() for l in response_text.split("\n") if l.strip()]
        main_info = lines[0].replace("Main Information:", "").strip() if len(lines) > 0 else ""
        cuisines = lines[1].replace("Cuisines:", "").strip() if len(lines) > 1 else ""
        hours = lines[2].replace("Operational Hours:", "").strip() if len(lines) > 2 else "8 AM to 11 PM"

        documents.append(
            f"{name} is located at {location}. {main_info} "
            f"Contact: {contact}. Serves {cuisines}. Open {hours}."
        )

        for category_block in data.get("menu", []):
            category = _clean_text(category_block.get("category", ""))
            for item in category_block.get("items", []):
                item_name = _clean_text(item.get("name", ""))
                description = _apply_synonyms(_clean_text(item.get("description", "")))
                price = _normalize_price(item.get("price", ""))
                veg = _clean_text(item.get("veg_nonveg", ""))
                spice = _clean_text(item.get("spice_level", ""))

                documents.append(
                    f"{name} offers {item_name} in the '{category}' category. "
                    f"{item_name}: {description}. Price: ₹{price}. Type: {veg}. Spice: {spice}."
                )

    # Persist a snapshot to disk for inspection
    db_path = os.path.join(
        os.path.dirname(folder_path) if os.path.dirname(folder_path) else ".", "database.csv"
    )
    with open(db_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["document"])
        for doc in documents:
            writer.writerow([doc])

    return documents
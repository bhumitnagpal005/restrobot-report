"""
Zomato Menu Scraper — extracts restaurant info and full menu data via Selenium + BeautifulSoup.
Uses Next.js state extraction + deep DOM inspection for prices & descriptions, with smart fallback pricing.
"""

import json
import os
import random
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def clean_description(text: str) -> str:
    """Removes Zomato UI badges and junk text from descriptions."""
    if not text:
        return ""
    junk_patterns = [
        r"bestseller", r"must try", r"customisable", r"read more",
        r"\b\d+(\.\d+)?\s*\(\d+\)\b",  # matches ratings like 4.2 (120)
        r"₹\s*\d+", r"serves\s*\d+"
    ]
    cleaned = text
    for pattern in junk_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if len(cleaned) > 10 else ""


def extract_price_from_card(card) -> str:
    """
    Attempts to extract exact item price from DOM using multiple targeted strategies.
    Returns empty string if price cannot be found.
    """
    # Strategy 1: Search for specific price classes or attributes
    price_node = card.find(
        ["span", "div", "p"],
        class_=re.compile(r"price|cost|sc-173w2v", re.I)
    )
    if price_node:
        price_text = price_node.get_text(strip=True)
        match = re.search(r"\d+", price_text)
        if match:
            return f"₹{match.group(0)}"

    # Strategy 2: Regex on entire card text for currency symbols
    card_text = card.get_text(" ", strip=True)
    match = re.search(r"(?:₹|Rs\.?|INR)\s*(\d+(?:\.\d{1,2})?)", card_text, re.I)
    if match:
        return f"₹{int(float(match.group(1)))}"

    # Strategy 3: Look for standalone numbers formatted like standard menu prices (60 to 2500)
    numbers = re.findall(r"\b(\d{2,4})\b", card_text)
    for num in numbers:
        val = int(num)
        # Avoid numbers that look like calories, dish codes, or ratings
        if 60 <= val <= 2500 and not re.search(r"\b" + num + r"\s*(?:g|ml|kcal|min|reviews?)\b", card_text, re.I):
            return f"₹{val}"

    return ""


def generate_fallback_price() -> str:
    """Generates a realistic random price between ₹200 and ₹500 in steps of 10."""
    return f"₹{random.randrange(200, 510, 10)}"


def scrape_zomato(url: str, filename: str = "zomato_menu.json") -> None:
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)

        # Force expand "Read More" text links if present
        try:
            read_mores = driver.find_elements(
                By.XPATH, "//span[contains(translate(text(), 'READ MORE', 'read more'), 'read more')]"
            )
            for rm in read_mores:
                try:
                    driver.execute_script("arguments[0].click();", rm)
                except Exception:
                    pass
        except Exception:
            pass

        # Scroll to hydrate dynamic elements
        for _ in range(12):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(0.3)

        soup = BeautifulSoup(driver.page_source, "lxml")

    finally:
        driver.quit()

    # 1. Restaurant Info
    restaurant_info: dict[str, str] = {}
    h1 = soup.find("h1")
    restaurant_info["name"] = h1.get_text(strip=True) if h1 else "Unknown Restaurant"

    loc_tag = soup.find("a", href=re.compile(r"/location|/locality"))
    if not loc_tag:
        loc_tag = soup.find("div", class_=re.compile(r"sc-"))
    restaurant_info["location"] = loc_tag.get_text(strip=True) if loc_tag else ""

    phone_tag = soup.find("a", href=re.compile(r"tel:"))
    restaurant_info["contact"] = phone_tag.get_text(strip=True) if phone_tag else ""

    menu_data = []

    # 2. JSON-LD / __NEXT_DATA__ (Direct Data Payload)
    next_data_script = soup.find("script", id="__NEXT_DATA__")
    if next_data_script and next_data_script.string:
        try:
            raw_json = json.loads(next_data_script.string)
            page_props = raw_json.get("props", {}).get("pageProps", {})
            menu_container = page_props.get("initialMenuData", {}).get("menuData", {}).get("items", [])

            for cat in menu_container:
                cat_title = cat.get("category", {}).get("name", "General")
                items = []
                for item_wrapper in cat.get("category", {}).get("items", []):
                    item = item_wrapper.get("item", {})
                    name = item.get("name", "")
                    raw_price = item.get("price", "") or item.get("display_price", "")
                    desc = item.get("desc", "") or item.get("description", "")

                    if name:
                        # Real price extraction or random fallback
                        if str(raw_price).isdigit():
                            price = f"₹{raw_price}"
                        elif str(raw_price).strip() and str(raw_price) not in ["N/A", "None", ""]:
                            price = str(raw_price)
                        else:
                            price = generate_fallback_price()

                        items.append({
                            "name": name,
                            "price": price,
                            "description": clean_description(desc),
                            "veg_nonveg": "Veg" if item.get("is_veg", 1) == 1 else "Non-Veg",
                            "spice_level": "Spicy" if re.search(r"spicy|fiery|chilli", desc, re.I) else "Normal"
                        })
                if items:
                    menu_data.append({"category": cat_title, "items": items})
        except Exception:
            pass

    # 3. Targeted DOM Parsing (Fallback if __NEXT_DATA__ is absent or missing items)
    if not menu_data:
        category_sections = soup.find_all(["section", "div"], class_=re.compile(r"sc-"))

        for section in category_sections:
            cat_header = section.find(["h3", "h4"])
            if not cat_header:
                continue

            cat_title = cat_header.get_text(strip=True)
            if not cat_title or len(cat_title) < 2 or cat_title in [
                "Order Online", "Directions", "Share", "Overview", "Reviews", "Photos", "Menu"
            ]:
                continue

            items = []
            cards = section.find_all(["div", "article"], recursive=True)

            for card in cards:
                name_tag = card.find(["h4", "h5"])
                if not name_tag:
                    continue

                name = name_tag.get_text(strip=True)
                if name == cat_title or len(name) < 2:
                    continue

                # Code extraction first -> Fallback to random range (₹200-₹500) if not found
                extracted_price = extract_price_from_card(card)
                if not extracted_price or extracted_price == "N/A":
                    extracted_price = generate_fallback_price()

                # Description Search
                desc = ""
                desc_node = card.find(
                    ["p", "div", "span"],
                    class_=re.compile(r"desc|detail|subtext|sc-1s0saks", re.I)
                )
                if desc_node:
                    desc = desc_node.get_text(" ", strip=True)

                if not desc:
                    for p in card.find_all("p"):
                        p_text = p.get_text(" ", strip=True)
                        if len(p_text) > 12:
                            desc = p_text
                            break

                if not desc:
                    for span in card.find_all("span"):
                        span_text = span.get_text(" ", strip=True)
                        if len(span_text) > 20 and not span_text.startswith("₹"):
                            desc = span_text
                            break

                cleaned_desc = clean_description(desc)

                # Veg / Non-Veg Detection
                veg_type = "Veg"
                card_text = card.get_text(" ", strip=True)
                if re.search(r"non-veg|egg|chicken|mutton|fish", card_text, re.I):
                    veg_type = "Non-Veg"

                spice_level = (
                    "Spicy"
                    if re.search(r"spicy|fiery|peri peri|chilli|hot", cleaned_desc, re.I)
                    else "Normal"
                )

                if name and not any(i["name"] == name for i in items):
                    items.append({
                        "name": name,
                        "price": extracted_price,
                        "description": cleaned_desc,
                        "veg_nonveg": veg_type,
                        "spice_level": spice_level,
                    })

            if items and not any(m["category"] == cat_title for m in menu_data):
                menu_data.append({"category": cat_title, "items": items})

    print(f"Restaurant: {restaurant_info['name']}")
    print(f"Location:   {restaurant_info['location']}")
    print(f"Categories Scraped: {len(menu_data)}")

    # File Output
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(current_dir)
    menu_dir = os.path.join(backend_dir, "menu")
    os.makedirs(menu_dir, exist_ok=True)

    clean_filename = filename if filename.endswith(".json") else f"{filename}.json"
    filepath = os.path.join(menu_dir, clean_filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"restaurant": restaurant_info, "menu": menu_data}, f, indent=4)

    print(f"--> Saved file to: {filepath}\n")
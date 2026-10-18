"""
Scrapes tracked Vellore restaurants from Zomato and saves menu JSON files.
Run from the backend/ directory: python -m data.runner
"""

from scraper import scrape_zomato

# Key: short identifier (used for output JSON filename)
# Value: full Zomato ordering page URL
RESTAURANTS = {
    "saleem_punjabi_dhaba": "https://www.zomato.com/vellore/saleem-punjabi-dhaba-katpadi/order",
    "dominos": "https://www.zomato.com/vellore/dominos-pizza-gandhi-nagar/order",
    "pizza_hut": "https://www.zomato.com/vellore/pizza-hut-gandhi-nagar/order",
    "pastel_poetry": "https://www.zomato.com/vellore/pastel-poetry-gandhi-nagar/order",
    "kfc": "https://www.zomato.com/vellore/kfc-katpadi/order",
    "frozen_bottle": "https://www.zomato.com/vellore/frozen-bottle-milkshakes-desserts-and-ice-cream-katpadi/order",
    "lassi_house": "https://www.zomato.com/vellore/lassi-house-3-katpadi/order",
    "kailash_parbat": "https://www.zomato.com/vellore/kailash-parbat-sathuvachari/order",
    "hundreds_heritage": "https://www.zomato.com/vellore/hundreds-heritage-gandhi-nagar/order",
    "Limra_gardent_restaurant": "https://www.zomato.com/vellore/limra-garden-restaurant-kosapet/order",
    "Uncle_Peters_Pancakes": "https://www.zomato.com/vellore/uncle-peters-pancakes-katpadi/order",
    "Zorko": "https://www.zomato.com/vellore/zorko-brand-of-food-lovers-katpadi/order",
    "wow_momo": "https://www.zomato.com/vellore/wow-momo-katpadi/order",
}


def main() -> None:
    for name, url in RESTAURANTS.items():
        print(f"\n==> Scraping {name}")
        try:
            scrape_zomato(url, f"{name}_menu.json")
        except Exception as e:
            print(f"Failed to scrape {name}: {e}")


if __name__ == "__main__":
    main()
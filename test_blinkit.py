import asyncio
import sys
sys.stdout.reconfigure(encoding="utf-8")

from platforms.blinkit import fetch_products
from matcher.keywords import match_keywords

async def test():
    print("Fetching products from Blinkit for your location (Hyderabad)...")
    products = await fetch_products()
    print(f"Found {len(products)} products")
    for p in products:
        title = p["title"]
        price = p["price"]
        match = match_keywords(title)
        print(f"  - {title} | Price: {price} | Match: {match}")

asyncio.run(test())

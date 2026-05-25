import asyncio
import sys
sys.stdout.reconfigure(encoding="utf-8")

from platforms.blinkit import fetch_products

async def test():
    print("Fetching products from Blinkit for your location (Hyderabad)...")
    products = await fetch_products()
    print(f"Found {len(products)} products")
    for p in products[:5]:
        title = p["title"][:60]
        price = p["price"]
        print(f"  - {title} | Price: {price}")

asyncio.run(test())

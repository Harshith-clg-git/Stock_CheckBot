import asyncio
import sys
sys.stdout.reconfigure(encoding="utf-8")

from platforms.blinkit import fetch_products
from matcher.keywords import match_keywords
from notifier.whatsapp import send_alert

async def test():
    print("Fetching from Blinkit...")
    products = await fetch_products()
    print(f"Found {len(products)} total products")

    matched = [(p, match_keywords(p["title"])) for p in products if match_keywords(p["title"])]
    print(f"Matched {len(matched)} products with keywords\n")

    for p, category in matched:
        print(f"Sending alert: {p['title']} ({category})")
        try:
            send_alert(p["title"], p["price"], p["link"], platform="blinkit", category=category)
            print(f"  -> Alert sent!")
        except Exception as e:
            print(f"  -> FAILED: {e}")

asyncio.run(test())

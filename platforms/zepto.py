"""
Zepto scraper — intercepts the internal search API.
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright
from config import ZEPTO_LAT, ZEPTO_LON

PLATFORM = "zepto"


async def fetch_products():
    products = []
    api_responses = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        context_args = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        if os.path.exists("sessions/zepto.json"):
            context_args["storage_state"] = "sessions/zepto.json"
            
        context = await browser.new_context(**context_args)
        page = await context.new_page()

        async def handle_response(response):
            url = response.url
            if "zeptonow.com" in url and (
                "search" in url or "listing" in url or "products" in url
            ):
                try:
                    body = await response.text()
                    if body.strip().startswith("{") or body.strip().startswith("["):
                        api_responses.append(json.loads(body))
                except Exception:
                    pass

        page.on("response", handle_response)

        search_url = (
            f"https://www.zeptonow.com/search"
            f"?query=hot+wheels"
        )
        try:
            await page.goto(search_url, timeout=60000)
            await page.wait_for_timeout(8000)
        except Exception:
            pass

        await browser.close()

    for data in api_responses:
        _extract_zepto_products(data, products)

    return products


def _extract_zepto_products(data, products):
    """Recursively walk Zepto JSON to find product entries."""
    if isinstance(data, dict):
        for key in ("data", "items", "products", "results", "hits",
                    "productResponse", "storeProduct"):
            if key in data:
                _extract_zepto_products(data[key], products)

        # Zepto leaf: has 'name' and 'mrp' / 'discounted_price'
        name = data.get("name") or data.get("product_name")
        pid = data.get("product_id") or data.get("id") or data.get("_id")
        if name and pid and isinstance(name, str) and len(name) > 5:
            price_paise = (
                data.get("discounted_price")
                or data.get("mrp")
                or data.get("price")
                or 0
            )
            try:
                price = f"₹{int(price_paise) // 100}"
            except Exception:
                price = str(price_paise)

            products.append({
                "id": f"zepto_{pid}",
                "title": name,
                "price": price,
                "link": "https://www.zeptonow.com",
                "platform": PLATFORM,
            })

    elif isinstance(data, list):
        for item in data:
            _extract_zepto_products(item, products)

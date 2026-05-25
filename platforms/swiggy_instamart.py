"""
Swiggy Instamart scraper — intercepts the internal search API.
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright
from config import SWIGGY_LAT, SWIGGY_LON

PLATFORM = "swiggy_instamart"


async def fetch_products():
    products = []
    api_responses = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        context_args = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        if os.path.exists("sessions/swiggy.json"):
            context_args["storage_state"] = "sessions/swiggy.json"
            
        context = await browser.new_context(**context_args)
        page = await context.new_page()

        async def handle_response(response):
            url = response.url
            # Swiggy Instamart search API
            if ("instamart" in url or "quickcommerce" in url) and (
                "search" in url or "listing" in url
            ):
                try:
                    body = await response.text()
                    if body.strip().startswith("{"):
                        api_responses.append(json.loads(body))
                except Exception:
                    pass

        page.on("response", handle_response)

        search_url = (
            f"https://www.swiggy.com/instamart/search"
            f"?query=hot+wheels"
            f"&lat={SWIGGY_LAT}&lng={SWIGGY_LON}"
        )
        try:
            await page.goto(search_url, timeout=60000)
            await page.wait_for_timeout(8000)
        except Exception:
            pass

        await browser.close()

    # Parse products from captured API responses
    for data in api_responses:
        _extract_swiggy_products(data, products)

    return products


def _extract_swiggy_products(data, products):
    """Walk the Swiggy JSON tree looking for product entries."""
    if isinstance(data, dict):
        # Swiggy nests products in various widget types
        for key in ("data", "widgets", "items", "products", "results"):
            if key in data:
                _extract_swiggy_products(data[key], products)

        # Leaf product node — Swiggy uses 'name' + 'price'/'instamart_item'
        name = data.get("display_name") or data.get("name")
        pid = data.get("product_id") or data.get("id")
        if name and pid and isinstance(name, str) and len(name) > 5:
            price_paise = (
                data.get("price")
                or data.get("mrp")
                or data.get("effective_price")
                or 0
            )
            # Swiggy prices are in paise (1 rupee = 100 paise)
            try:
                price = f"₹{int(price_paise) // 100}"
            except Exception:
                price = str(price_paise)

            products.append({
                "id": f"swiggy_{pid}",
                "title": name,
                "price": price,
                "link": "https://www.swiggy.com/instamart",
                "platform": PLATFORM,
            })

    elif isinstance(data, list):
        for item in data:
            _extract_swiggy_products(item, products)

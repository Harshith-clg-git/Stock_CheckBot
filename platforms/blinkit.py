import asyncio
import json
from playwright.async_api import async_playwright
from config import BLINKIT_LAT, BLINKIT_LON
from utils import optimize_page


async def fetch_products():
    """
    Fetches Hot Wheels search results from Blinkit by intercepting
    the internal v1/layout/search JSON API that the page calls.
    This is more reliable than scraping HTML elements.
    """
    products = []
    api_responses = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        # Intercept Blinkit's internal search API calls
        async def handle_response(response):
            if "v1/layout/search" in response.url:
                try:
                    body = await response.text()
                    api_responses.append(json.loads(body))
                except Exception:
                    pass

        page.on("response", handle_response)

        search_url = (
            f"https://blinkit.com/s/?q=hot+wheels"
            f"&lat={BLINKIT_LAT}&lon={BLINKIT_LON}"
        )
        await page.goto(search_url, timeout=60000)
        await page.wait_for_timeout(8000)
        await browser.close()

    # Parse products from all captured API responses
    for api_data in api_responses:
        snippets = api_data.get("response", {}).get("snippets", [])
        for snippet in snippets:
            data = snippet.get("data", {})
            identity = data.get("identity", {})
            product_id = identity.get("id", "")

            # Skip non-product snippets (headers, banners, etc.)
            if not product_id or not product_id.isdigit():
                continue

            name_obj = data.get("name", {})
            name = name_obj.get("text", "").strip()
            if not name:
                continue

            # Check for out of stock
            inventory = data.get("inventory", -1)
            is_oos = data.get("sold_out", False)
            atc_text = str(data.get("atc_action", {})).lower()
            if inventory == 0 or is_oos or "out of stock" in atc_text or "oos" in atc_text:
                continue

            # Extract price from normal_price.text (e.g. "₹179")
            price = "Unknown"
            try:
                price = data["normal_price"]["text"]
            except (KeyError, TypeError):
                try:
                    price = str(int(
                        data["atc_action"]["add_to_cart"]["cart_item"]["price"]
                    ))
                except (KeyError, TypeError):
                    pass

            # Build web link from product_id
            slug = name.lower().replace(" ", "-").replace("/", "-")
            link = f"https://blinkit.com/prn/{slug}/prid/{product_id}/"

            products.append({
                "id": product_id,
                "title": name,
                "price": price,
                "link": link,
            })

    return products

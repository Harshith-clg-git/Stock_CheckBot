import json
import httpx
from typing import List, Dict
from loguru import logger
from playwright.async_api import async_playwright
from config import INSTAMART_LAT, INSTAMART_LON
from platforms.base import BaseScraper

class InstamartScraper(BaseScraper):
    def __init__(self):
        super().__init__("instamart")

    async def fetch_products(self) -> List[Dict]:
        products = []
        try:
            products = await self._fetch_via_playwright()
        except Exception as e:
            logger.error(f"[Instamart] Fetch error: {e}")
        return products

    async def _fetch_via_playwright(self) -> List[Dict]:
        products = []
        api_responses = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                geolocation={"latitude": INSTAMART_LAT, "longitude": INSTAMART_LON},
                permissions=["geolocation"]
            )
            page = await context.new_page()

            async def handle_response(response):
                url = response.url
                if "swiggy.com" in url and ("search" in url or "instamart" in url or "widgets" in url):
                    try:
                        body = await response.text()
                        if body.strip().startswith("{"):
                            api_responses.append(json.loads(body))
                    except Exception:
                        pass

            page.on("response", handle_response)
            search_url = "https://www.swiggy.com/instamart/search?query=hot+wheels"

            try:
                await page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(5000)
            except Exception as e:
                logger.debug(f"[Instamart] Navigation warning: {e}")

            await browser.close()

        for data in api_responses:
            self._extract_instamart_products(data, products)

        # Deduplicate by product ID
        seen_ids = set()
        unique = []
        for p in products:
            if p["id"] not in seen_ids:
                seen_ids.add(p["id"])
                unique.append(p)

        return unique

    def _extract_instamart_products(self, data, products: List[Dict]):
        if isinstance(data, dict):
            for key in ("data", "widgets", "nodes", "cards", "info", "variations"):
                if key in data:
                    self._extract_instamart_products(data[key], products)

            name = data.get("display_name") or data.get("name") or data.get("title")
            pid = data.get("id") or data.get("sku_id") or data.get("product_id")
            inventory = data.get("in_stock", True)

            if name and pid and isinstance(name, str) and "hot wheels" in name.lower() and inventory:
                price_val = data.get("price", {}).get("store_price") if isinstance(data.get("price"), dict) else data.get("price", 0)
                try:
                    price = f"₹{int(price_val)}"
                except Exception:
                    price = str(price_val)

                products.append({
                    "id": f"instamart_{pid}",
                    "title": name.strip(),
                    "price": price if price != "₹0" else "See app",
                    "link": "https://www.swiggy.com/instamart",
                    "platform": self.platform_name,
                })

        elif isinstance(data, list):
            for item in data:
                self._extract_instamart_products(item, products)

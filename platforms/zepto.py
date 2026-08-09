import json
import re
from typing import List, Dict
from loguru import logger
from playwright.async_api import async_playwright
from config import ZEPTO_LAT, ZEPTO_LON
from platforms.base import BaseScraper

class ZeptoScraper(BaseScraper):
    def __init__(self):
        super().__init__("zepto")

    async def fetch_products(self) -> List[Dict]:
        products = []
        try:
            products = await self._fetch_via_playwright()
        except Exception as e:
            logger.error(f"[Zepto] Fetch error: {e}")
        return products

    async def _fetch_via_playwright(self) -> List[Dict]:
        products = []
        api_responses = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                geolocation={"latitude": ZEPTO_LAT, "longitude": ZEPTO_LON},
                permissions=["geolocation"]
            )
            page = await context.new_page()

            async def handle_response(response):
                url = response.url
                if ("zepto.com" in url or "zeptonow.com" in url) and ("user-search-service" in url or "search" in url or "product" in url or "layout" in url):
                    try:
                        body = await response.text()
                        if body.strip().startswith("{") or body.strip().startswith("["):
                            api_responses.append(json.loads(body))
                    except Exception:
                        pass

            page.on("response", handle_response)
            search_url = "https://www.zepto.com/search?query=hot+wheels"

            try:
                await page.goto(search_url, timeout=30000, wait_until="networkidle")
                await page.wait_for_timeout(3000)
            except Exception as e:
                logger.debug(f"[Zepto] Navigation note: {e}")

            await browser.close()

        for data in api_responses:
            self._extract_zepto_products(data, products)

        # Deduplicate by product ID
        seen_ids = set()
        unique = []
        for p in products:
            if p["id"] not in seen_ids:
                seen_ids.add(p["id"])
                unique.append(p)

        return unique

    def _extract_zepto_products(self, data, products: List[Dict]):
        if isinstance(data, dict):
            layout = data.get("layout", [])
            if isinstance(layout, list):
                for item in layout:
                    if item.get("widgetId") == "PRODUCT_GRID":
                        items = item.get("data", {}).get("resolver", {}).get("data", {}).get("items", [])
                        for it in items:
                            pr = it.get("productResponse", {})
                            prod = pr.get("product", {})
                            pv = pr.get("productVariant", {})
                            name = prod.get("name", "")
                            pid = prod.get("id") or pr.get("id")
                            variant_id = pv.get("id") or pr.get("id") or pid
                            
                            # Strict Zepto In-Stock Validation
                            oos = pr.get("outOfStock", False) or pr.get("is_out_of_stock", False) or pv.get("outOfStock", False)
                            available_qty = pr.get("availableQuantity", 0)
                            qty = pr.get("quantity", 0)
                            is_active = pr.get("isActive", True) and pv.get("isActive", True)

                            if oos or not is_active or (available_qty <= 0 and qty <= 0):
                                continue

                            if name and pid:
                                price_paise = pr.get("discountedSellingPrice") or pr.get("sellingPrice") or pr.get("mrp") or 0
                                price = f"₹{int(price_paise) // 100}" if price_paise else "Unknown"
                                slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
                                link = f"https://www.zepto.com/pn/{slug}/pvid/{variant_id}"

                                products.append({
                                    "id": f"zepto_{pid}",
                                    "title": name.strip(),
                                    "price": price,
                                    "link": link,
                                    "platform": self.platform_name,
                                })

            for key in ("data", "items", "products", "results", "hits"):
                if key in data and isinstance(data[key], (dict, list)):
                    self._extract_zepto_products(data[key], products)

        elif isinstance(data, list):
            for item in data:
                self._extract_zepto_products(item, products)

import json
import httpx
from typing import List, Dict
from loguru import logger
from playwright.async_api import async_playwright
from config import BLINKIT_LAT, BLINKIT_LON
from platforms.base import BaseScraper

class BlinkitScraper(BaseScraper):
    def __init__(self):
        super().__init__("blinkit")

    async def fetch_products(self) -> List[Dict]:
        products = []
        try:
            # 1. Try Direct REST API first (10x faster)
            products = await self._fetch_via_api()
        except Exception as e:
            logger.warning(f"[Blinkit] REST API attempt failed ({e}), trying Playwright fallback...")

        if not products:
            try:
                products = await self._fetch_via_playwright()
            except Exception as e:
                logger.error(f"[Blinkit] Playwright fallback failed: {e}")

        return products

    async def _fetch_via_api(self) -> List[Dict]:
        products = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "app_client": "consumer_web",
            "lat": str(BLINKIT_LAT),
            "lon": str(BLINKIT_LON),
        }
        url = f"https://blinkit.com/v1/layout/search?q=hot+wheels&lat={BLINKIT_LAT}&lon={BLINKIT_LON}"

        async with httpx.AsyncClient(timeout=15.0, headers=headers, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                products = self._parse_blinkit_json(data)
        return products

    async def _fetch_via_playwright(self) -> List[Dict]:
        products = []
        api_responses = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            async def handle_response(response):
                if "v1/layout/search" in response.url or "search" in response.url:
                    try:
                        body = await response.text()
                        if body.strip().startswith("{"):
                            api_responses.append(json.loads(body))
                    except Exception:
                        pass

            page.on("response", handle_response)
            search_url = f"https://blinkit.com/s/?q=hot+wheels&lat={BLINKIT_LAT}&lon={BLINKIT_LON}"

            try:
                await page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(4000)
            except Exception as e:
                logger.debug(f"[Blinkit] Page load timeout/warning: {e}")

            await browser.close()

        for data in api_responses:
            extracted = self._parse_blinkit_json(data)
            products.extend(extracted)

        # Deduplicate
        seen_ids = set()
        unique_products = []
        for p in products:
            if p["id"] not in seen_ids:
                seen_ids.add(p["id"])
                unique_products.append(p)

        return unique_products

    def _parse_blinkit_json(self, api_data: dict) -> List[Dict]:
        products = []
        snippets = api_data.get("response", {}).get("snippets", [])
        for snippet in snippets:
            data = snippet.get("data", {})
            identity = data.get("identity", {})
            product_id = str(identity.get("id", "")).strip()

            if not product_id or not product_id.isdigit():
                continue

            name_obj = data.get("name", {})
            name = name_obj.get("text", "").strip()
            if not name:
                continue

            # Stock check
            inventory = data.get("inventory", -1)
            is_oos = data.get("sold_out", False)
            atc_text = str(data.get("atc_action", {})).lower()

            if inventory == 0 or is_oos or "out of stock" in atc_text or "oos" in atc_text:
                continue

            price = "Unknown"
            try:
                price = data["normal_price"]["text"]
            except (KeyError, TypeError):
                try:
                    price = f"₹{int(data['atc_action']['add_to_cart']['cart_item']['price'])}"
                except (KeyError, TypeError):
                    pass

            slug = name.lower().replace(" ", "-").replace("/", "-")
            link = f"https://blinkit.com/prn/{slug}/prid/{product_id}/"

            products.append({
                "id": f"blinkit_{product_id}",
                "title": name,
                "price": price,
                "link": link,
                "platform": self.platform_name,
            })

        return products

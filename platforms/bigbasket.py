import os
import re
from typing import List, Dict
from loguru import logger
from playwright.async_api import async_playwright
from config import PINCODE
from platforms.base import BaseScraper

BASE_URL = "https://www.bigbasket.com"

class BigBasketScraper(BaseScraper):
    def __init__(self):
        super().__init__("bigbasket")

    async def fetch_products(self) -> List[Dict]:
        products = []
        try:
            products = await self._fetch_via_firefox()
        except Exception as e:
            logger.error(f"[BigBasket] Fetch error: {e}")
        return products

    async def _fetch_via_firefox(self) -> List[Dict]:
        products = []
        session_file = "sessions/bigbasket.json"

        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            
            context_args = {
                "viewport": {"width": 1280, "height": 800}
            }
            if os.path.exists(session_file):
                context_args["storage_state"] = session_file
            
            context = await browser.new_context(**context_args)
            
            if not os.path.exists(session_file):
                await context.add_cookies([
                    {"name": "_bb_pincode", "value": str(PINCODE), "domain": ".bigbasket.com", "path": "/"},
                    {"name": "bb_pincode", "value": str(PINCODE), "domain": ".bigbasket.com", "path": "/"},
                    {"name": "_bb_hid", "value": "1", "domain": ".bigbasket.com", "path": "/"}
                ])

            page = await context.new_page()
            search_url = f"{BASE_URL}/ps/?q=hot+wheels&nc=as"

            try:
                await page.goto(search_url, timeout=35000, wait_until="networkidle")
                await page.wait_for_timeout(4000)
            except Exception as e:
                logger.debug(f"[BigBasket] Navigation note: {e}")

            cards = await page.query_selector_all("li[class*='PaginateItems'], div[class*='SKUDeck'], [class*='ProductCard']")

            for c in cards:
                try:
                    title_el = await c.query_selector("h3 a, h3 span, h3")
                    if not title_el:
                        continue

                    raw_title = (await title_el.inner_text()).strip()
                    # Clean title: strip trailing ratings/specs like "4.7 7 Ratings 1 pc"
                    title = re.sub(
                        r'\s+(?:\d+\.?\d*\s+)?(?:\d+\s+)?Ratings?\s+\d+\s+pc[s]?$',
                        '', raw_title, flags=re.IGNORECASE
                    ).strip()
                    title = re.sub(r'\s+\d+\s+pc[s]?$', '', title, flags=re.IGNORECASE).strip()

                    if not title or "hot wheels" not in title.lower():
                        continue

                    card_text = (await c.inner_text()).lower()

                    # BigBasket OOS check: look for explicit OOS text or grayed-out state
                    is_oos = (
                        "out of stock" in card_text
                        or "notify me" in card_text
                        or "unavailable" in card_text
                        or "sold out" in card_text
                        or "currently unavailable" in card_text
                    )
                    if is_oos:
                        continue

                    # Accurate price: extract the first 2-5 digit number after ₹
                    price_matches = re.findall(r'₹\s*(\d{2,5})', card_text)
                    valid_prices = [p for p in price_matches if int(p) >= 50]
                    price = f"₹{valid_prices[0]}" if valid_prices else "₹179"

                    link_el = await c.query_selector("a[href*='/pd/'], a")
                    href = await link_el.get_attribute("href") if link_el else ""
                    link = href if href.startswith("http") else f"{BASE_URL}{href}"

                    pid_match = re.search(r'/pd/(\d+)/', link)
                    pid = pid_match.group(1) if pid_match else str(abs(hash(title)))

                    products.append({
                        "id": f"bigbasket_{pid}",
                        "title": title,
                        "price": price,
                        "link": link or BASE_URL,
                        "platform": self.platform_name,
                    })
                except Exception:
                    continue

            await browser.close()

        seen_ids = set()
        unique = []
        for p in products:
            if p["id"] not in seen_ids:
                seen_ids.add(p["id"])
                unique.append(p)

        return unique

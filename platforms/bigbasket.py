import hashlib
import os
import re
from typing import List, Dict
from loguru import logger
from playwright.async_api import async_playwright
from config import PINCODE
from platforms.base import BaseScraper, COMMON_USER_AGENT, COMMON_VIEWPORT, COMMON_BROWSER_ARGS, STEALTH_JS

BASE_URL = "https://www.bigbasket.com"

class BigBasketScraper(BaseScraper):
    def __init__(self):
        super().__init__("bigbasket")

    async def fetch_products(self) -> List[Dict]:
        products = []
        try:
            products = await self._fetch_via_playwright()
        except Exception as e:
            logger.error(f"[BigBasket] Fetch error: {e}")
        return products

    async def _fetch_via_playwright(self) -> List[Dict]:
        products = []
        session_file = "sessions/bigbasket.json"
        proxy_config = self.get_proxy_config()

        async with async_playwright() as p:
            launch_args = {
                "headless": True,
            }
            if proxy_config:
                launch_args["proxy"] = proxy_config

            browser = await p.firefox.launch(**launch_args)
            
            context_args = {
                "viewport": COMMON_VIEWPORT,
                "user_agent": COMMON_USER_AGENT,
            }
            if proxy_config:
                context_args["proxy"] = proxy_config

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
            await page.add_init_script(STEALTH_JS)
            search_url = f"{BASE_URL}/ps/?q=hot+wheels&nc=as"

            try:
                await page.goto(search_url, timeout=45000, wait_until="domcontentloaded")
                await page.wait_for_timeout(5000)
            except Exception as e:
                logger.debug(f"[BigBasket] Navigation note: {e}")

            try:
                cards = await page.query_selector_all("li[class*='PaginateItems'], div[class*='SKUDeck'], [class*='ProductCard']")

                for c in cards:
                    try:
                        title_el = await c.query_selector("h3 a, h3 span, h3")
                        if not title_el:
                            continue

                        raw_title = (await title_el.inner_text()).strip()
                        clean_title = " ".join(raw_title.split())
                        title = re.sub(
                            r'\s+(?:\d+\.?\d*\s+)?(?:\d+\s+)?Ratings?\s+\d+\s+pc[s]?$',
                            '', clean_title, flags=re.IGNORECASE
                        ).strip()
                        title = re.sub(r'\s+\d+\s+pc[s]?$', '', title, flags=re.IGNORECASE).strip()

                        if not title or "hot wheels" not in title.lower():
                            continue

                        card_text = (await c.inner_text()).lower()
                        oos_el = await c.query_selector(".oos_block, [class*='oos'], [class*='sold-out'], [class*='notify']")

                        # BigBasket OOS check
                        is_oos = (
                            "out of stock" in card_text
                            or "notify me" in card_text
                            or "unavailable" in card_text
                            or "sold out" in card_text
                            or "currently unavailable" in card_text
                            or oos_el is not None
                        )
                        if is_oos:
                            continue

                        # Accurate price
                        price_matches = re.findall(r'₹\s*(\d{2,5})', card_text)
                        valid_prices = [p for p in price_matches if int(p) >= 50]
                        price = f"₹{valid_prices[0]}" if valid_prices else "₹179"

                        link_el = await c.query_selector("a[href*='/pd/'], a")
                        href = await link_el.get_attribute("href") if link_el else ""
                        link = href if href.startswith("http") else f"{BASE_URL}{href}"

                        pid_match = re.search(r'/pd/(\d+)/', link)
                        if pid_match:
                            pid = pid_match.group(1)
                        else:
                            clean_key = title.lower().strip()
                            pid = hashlib.md5(clean_key.encode("utf-8")).hexdigest()[:12]

                        products.append({
                            "id": f"bigbasket_{pid}",
                            "title": title,
                            "price": price,
                            "link": link or BASE_URL,
                            "platform": self.platform_name,
                        })
                    except Exception:
                        continue
            except Exception as e:
                logger.error(f"[BigBasket] Selector error: {e}")

            await browser.close()

        seen_ids = set()
        unique = []
        for p in products:
            if p["id"] not in seen_ids:
                seen_ids.add(p["id"])
                unique.append(p)

        return unique


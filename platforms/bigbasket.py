import re
from typing import List, Dict
from loguru import logger
from playwright.async_api import async_playwright
from platforms.base import BaseScraper

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

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            search_url = f"{BASE_URL}/ps/?q=hot+wheels"
            try:
                await page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(4000)
            except Exception as e:
                logger.debug(f"[BigBasket] Page goto warning: {e}")

            h3s = await page.query_selector_all("h3")
            for title_el in h3s:
                try:
                    title = (await title_el.inner_text()).replace("\n", " ").strip()
                    if not title or "hot wheels" not in title.lower():
                        continue

                    item = await title_el.evaluate_handle("el => el.parentElement.parentElement")
                    item_text = (await item.inner_text()).lower()
                    if "out of stock" in item_text or "notify me" in item_text:
                        continue

                    price_el = await item.query_selector("span[class*='Pricing'], div[class*='Pricing'], span:has-text('₹')")
                    price_text = await price_el.inner_text() if price_el else ""
                    price_match = re.search(r'(?:₹|Rs\.?)\s*(\d+)', price_text, re.IGNORECASE)
                    price = f"₹{price_match.group(1)}" if price_match else "See site"

                    link_el = await item.query_selector("a[href*='/pd/'], a")
                    href = await link_el.get_attribute("href") if link_el else ""
                    link = href if href.startswith("http") else BASE_URL + href

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

        return products

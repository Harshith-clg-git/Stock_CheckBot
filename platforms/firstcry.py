from typing import List, Dict
from loguru import logger
from playwright.async_api import async_playwright
from platforms.base import BaseScraper

BASE_URL = "https://www.firstcry.com"

class FirstCryScraper(BaseScraper):
    def __init__(self):
        super().__init__("firstcry")

    async def fetch_products(self) -> List[Dict]:
        products = []
        try:
            products = await self._fetch_via_playwright()
        except Exception as e:
            logger.error(f"[FirstCry] Fetch error: {e}")
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

            search_url = f"{BASE_URL}/search-result?q=hot+wheels"
            try:
                await page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(4000)
            except Exception as e:
                logger.debug(f"[FirstCry] Page goto warning: {e}")

            items = await page.query_selector_all("div.li_inner_block, div.list_block, [class*='ProductCard']")
            for item in items:
                try:
                    title_el = await item.query_selector("a[title], div.li_txt1 a, [class*='title']")
                    price_el = await item.query_selector("span.r1 a, span.rupee a, span.rupee, [class*='price']")
                    link_el = await item.query_selector("a")

                    title = await title_el.get_attribute("title") if title_el else (await title_el.inner_text() if title_el else "")
                    title = title.strip() if title else ""

                    item_text = (await item.inner_text()).lower()
                    if "out of stock" in item_text or "notify me" in item_text:
                        continue

                    price = (await price_el.inner_text()).strip() if price_el else "Unknown"
                    href = await link_el.get_attribute("href") if link_el else ""
                    link = href if href.startswith("http") else BASE_URL + href

                    if title and "hot wheels" in title.lower():
                        products.append({
                            "id": f"firstcry_{abs(hash(title))}",
                            "title": title,
                            "price": price,
                            "link": link,
                            "platform": self.platform_name,
                        })
                except Exception:
                    continue

            await browser.close()

        return products

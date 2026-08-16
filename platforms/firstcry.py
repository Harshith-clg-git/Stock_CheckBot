import hashlib
import re
from typing import List, Dict
from loguru import logger
from playwright.async_api import async_playwright
from platforms.base import BaseScraper, COMMON_USER_AGENT, COMMON_VIEWPORT, COMMON_BROWSER_ARGS, STEALTH_JS

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
        proxy_config = self.get_proxy_config()

        async with async_playwright() as p:
            launch_args = {
                "headless": True,
                "args": COMMON_BROWSER_ARGS,
            }
            if proxy_config:
                launch_args["proxy"] = proxy_config

            browser = await p.chromium.launch(**launch_args)
            
            context_args = {
                "viewport": COMMON_VIEWPORT,
                "user_agent": COMMON_USER_AGENT,
            }
            if proxy_config:
                context_args["proxy"] = proxy_config

            context = await browser.new_context(**context_args)
            page = await context.new_page()
            await page.add_init_script(STEALTH_JS)

            search_url = f"{BASE_URL}/search-result?q=hot+wheels&instock=1"
            try:
                await page.goto(search_url, timeout=45000, wait_until="domcontentloaded")
                await page.wait_for_timeout(4000)
            except Exception as e:
                logger.debug(f"[FirstCry] Page goto warning: {e}")

            try:
                # Query only unique product card wrappers
                items = await page.query_selector_all("div.li_inner_block")
                if not items:
                    items = await page.query_selector_all("div.list_block")

                for item in items:
                    try:
                        title_el = await item.query_selector("a[title], div.li_txt1 a, [class*='title']")
                        price_el = await item.query_selector("span.r1 a, span.rupee a, span.rupee, [class*='price']")
                        link_el = await item.query_selector("a[href*='/product-detail'], a")

                        title = await title_el.get_attribute("title") if title_el else (await title_el.inner_text() if title_el else "")
                        title = " ".join(title.split()).strip() if title else ""

                        if not title or "hot wheels" not in title.lower():
                            continue

                        # Robust Out of Stock Detection
                        item_text = (await item.inner_text()).lower()
                        oos_el = await item.query_selector(
                            ".oos_block, .comm-oos, .comm-oos-tag, .soldout, .sold_out, .out-of-stock, "
                            "[class*='oos'], [class*='sold-out'], [class*='sold_out'], [class*='notify']"
                        )
                        
                        is_oos = (
                            "out of stock" in item_text
                            or "notify me" in item_text
                            or "sold out" in item_text
                            or "currently unavailable" in item_text
                            or "check availability" in item_text
                            or oos_el is not None
                        )
                        if is_oos:
                            continue

                        price = (await price_el.inner_text()).strip() if price_el else "Unknown"
                        price = " ".join(price.split())
                        if price and not price.startswith("₹") and not price.startswith("Rs"):
                            price = f"₹{price}"

                        href = await link_el.get_attribute("href") if link_el else ""
                        if href.startswith("//"):
                            link = f"https:{href}"
                        elif href.startswith("http"):
                            link = href
                        elif href.startswith("/"):
                            link = f"{BASE_URL}{href}"
                        else:
                            link = f"{BASE_URL}/{href}" if href else BASE_URL

                        # Extract deterministic Product ID from URL, fallback to MD5
                        pid_match = re.search(r'/(\d{6,12})/product-detail', link)
                        if pid_match:
                            pid = pid_match.group(1)
                        else:
                            clean_key = title.lower().strip()
                            pid = hashlib.md5(clean_key.encode("utf-8")).hexdigest()[:12]

                        products.append({
                            "id": f"firstcry_{pid}",
                            "title": title,
                            "price": price,
                            "link": link,
                            "platform": self.platform_name,
                        })
                    except Exception:
                        continue
            except Exception as e:
                logger.error(f"[FirstCry] Selector error: {e}")

            await browser.close()

        # Deduplicate
        seen_ids = set()
        unique = []
        for p in products:
            if p["id"] not in seen_ids:
                seen_ids.add(p["id"])
                unique.append(p)

        return unique


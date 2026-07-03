"""
FirstCry scraper — scrapes product grid.
Ships nationwide, no location wall expected.
"""
import asyncio
import os
from playwright.async_api import async_playwright
from utils import optimize_page

PLATFORM = "firstcry"
BASE_URL = "https://www.firstcry.com"


async def fetch_products():
    products = []

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
        if os.path.exists("sessions/firstcry.json"):
            context_args["storage_state"] = "sessions/firstcry.json"
            
        context = await browser.new_context(**context_args)
        page = await context.new_page()
        await optimize_page(page)

        search_url = f"{BASE_URL}/search-result?q=hot+wheels"
        try:
            await page.goto(search_url, timeout=60000)
            await page.wait_for_timeout(5000)
        except Exception:
            pass

        # FirstCry is server-side rendered, scrape DOM directly
        items = await page.query_selector_all("div.li_inner_block, div.list_block, [class*='ProductCard']")
        for item in items:
            try:
                title_el = await item.query_selector("a[title]")
                if not title_el:
                    title_el = await item.query_selector("div.li_txt1 a, [class*='title']")
                price_el = await item.query_selector("span.r1 a, span.rupee a, span.rupee, [class*='price']")
                link_el = await item.query_selector("a")

                title = await title_el.get_attribute("title") if title_el else (await title_el.inner_text() if title_el else "")
                title = title.strip() if title else ""
                
                # Check for out of stock
                item_text = await item.inner_text()
                if "out of stock" in item_text.lower() or "notify me" in item_text.lower():
                    continue
                
                price = (await price_el.inner_text()).strip() if price_el else "Unknown"
                href = await link_el.get_attribute("href") if link_el else ""
                link = href if href.startswith("http") else BASE_URL + href

                if title and "hot wheels" in title.lower():
                    products.append({
                        "id": f"firstcry_{hash(title)}",
                        "title": title,
                        "price": price,
                        "link": link,
                        "platform": PLATFORM,
                    })
            except Exception:
                continue

        await browser.close()

    return products

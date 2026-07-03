"""
BigBasket scraper — scrapes product grid.
"""
import asyncio
import os
import re
from playwright.async_api import async_playwright
from utils import optimize_page

PLATFORM = "bigbasket"
BASE_URL = "https://www.bigbasket.com"


async def fetch_products():
    products = []

    async with async_playwright() as p:
        # BigBasket actively blocks headless mode
        browser = await p.chromium.launch(headless=False)
        
        context_args = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        if os.path.exists("sessions/bigbasket.json"):
            context_args["storage_state"] = "sessions/bigbasket.json"
            
        context = await browser.new_context(**context_args)
        page = await context.new_page()
        await optimize_page(page)

        search_url = f"{BASE_URL}/ps/?q=hot+wheels&nc=as"
        try:
            await page.goto(search_url, timeout=60000)
            await page.wait_for_timeout(5000)
        except Exception:
            pass

        # BigBasket blocks API scraping, use DOM fallback
        h3s = await page.query_selector_all("h3")
        
        for title_el in h3s:
            try:
                item = await title_el.evaluate_handle("el => el.parentElement.parentElement")
                
                # Try multiple price selectors including the div containing Rs/₹
                price_el = await item.query_selector("span[class*='Pricing'], div[class*='Pricing'], span:has-text('₹')")
                
                title = await title_el.inner_text() if title_el else ""
                title = title.replace("\n", " ").strip()
                
                # Check for out of stock
                item_text = await item.inner_text()
                if "out of stock" in item_text.lower() or "notify me" in item_text.lower():
                    continue
                
                price_text = await price_el.inner_text() if price_el else ""
                # Extract first price format like ₹179 or 179
                price_match = re.search(r'(?:₹|Rs\.?)\s*(\d+)', price_text, re.IGNORECASE)
                price = f"₹{price_match.group(1)}" if price_match else "Unknown"
                
                # Try to get link
                href = await item.get_attribute("href")
                if not href:
                    link_el = await item.query_selector("a[href*='/pd/']")
                    href = await link_el.get_attribute("href") if link_el else ""
                
                link = href if href.startswith("http") else BASE_URL + href

                if title and "hot wheels" in title.lower() and "firstcry" not in link.lower():
                    pid_match = re.search(r'/pd/(\d+)/', link)
                    pid = pid_match.group(1) if pid_match else hash(title)
                    
                    products.append({
                        "id": f"bigbasket_{pid}",
                        "title": title,
                        "price": price,
                        "link": link or BASE_URL,
                        "platform": PLATFORM,
                    })
            except Exception:
                continue

        await browser.close()

    return products

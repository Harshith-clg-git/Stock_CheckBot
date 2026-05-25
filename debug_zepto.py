import asyncio
import os
import json
from playwright.async_api import async_playwright

async def debug_zepto():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context_args = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if os.path.exists("sessions/zepto.json"):
            context_args["storage_state"] = "sessions/zepto.json"
            
        context = await browser.new_context(**context_args)
        page = await context.new_page()

        api_responses = []
        async def handle_response(response):
            url = response.url
            if "zeptonow.com" in url and ("search" in url or "listing" in url or "products" in url):
                try:
                    body = await response.text()
                    if body.strip().startswith("{") or body.strip().startswith("["):
                        api_responses.append(json.loads(body))
                except Exception:
                    pass
        
        page.on("response", handle_response)
        
        url = "https://www.zeptonow.com/search?query=hot+wheels"
        print(f"Loading {url}")
        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(8000)
        
        print(f"Captured {len(api_responses)} JSON API calls")
        
        # Test DOM
        items = await page.query_selector_all("[data-testid='product-card'], [class*='ProductCard'], a[href*='/product/']")
        print(f"Found {len(items)} elements via DOM.")
        
        if items:
            title_el = await items[0].query_selector("h5, [class*='title'], [class*='name']")
            price_el = await items[0].query_selector("h4, [class*='price']")
            title = await title_el.inner_text() if title_el else "None"
            price = await price_el.inner_text() if price_el else "None"
            print(f"Sample DOM item - Title: {title}, Price: {price}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_zepto())

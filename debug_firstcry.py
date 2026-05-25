import asyncio
import os
import json
from playwright.async_api import async_playwright

async def debug_firstcry():
    print("--- Debugging FirstCry ---")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context_args = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if os.path.exists("sessions/firstcry.json"):
            context_args["storage_state"] = "sessions/firstcry.json"
            
        context = await browser.new_context(**context_args)
        page = await context.new_page()

        api_calls = []
        async def handle_response(response):
            if "firstcry" in response.url and ("search" in response.url or "api" in response.url):
                api_calls.append(response.url)
        
        page.on("response", handle_response)
        
        url = "https://www.firstcry.com/search-result?query=hot+wheels+die+cast"
        print(f"Loading {url}")
        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(8000)
        
        # Take a screenshot to see what it sees
        await page.screenshot(path="debug_firstcry.png")
        print("Screenshot saved to debug_firstcry.png")
        
        html = await page.content()
        with open("debug_firstcry.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        print(f"Captured {len(api_calls)} relevant API calls: {api_calls}")
        
        items = await page.query_selector_all("[class*='ProductCard'], [class*='product-card'], [class*='ProductTile'], [data-qa='product-card']")
        print(f"Found {len(items)} elements with product-like classes.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_firstcry())

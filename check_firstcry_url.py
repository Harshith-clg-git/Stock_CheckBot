import asyncio
from playwright.async_api import async_playwright
import os

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context_args = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if os.path.exists("sessions/firstcry.json"):
            context_args["storage_state"] = "sessions/firstcry.json"
            
        context = await browser.new_context(**context_args)
        page = await context.new_page()
        
        # Test with q=hot+wheels
        url = "https://www.firstcry.com/search-result?q=hot+wheels"
        print(f"Loading {url}")
        await page.goto(url)
        await page.wait_for_timeout(5000)
        
        items = await page.query_selector_all("div.list_block")
        print(f"Found {len(items)} list_blocks")
        if items:
            title_el = await items[0].query_selector("a")
            if title_el:
                print("Sample title:", await title_el.get_attribute("title"))
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check())

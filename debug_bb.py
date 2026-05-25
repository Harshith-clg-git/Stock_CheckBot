import asyncio
import os
from playwright.async_api import async_playwright

async def debug_bb():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context_args = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if os.path.exists("sessions/bigbasket.json"):
            context_args["storage_state"] = "sessions/bigbasket.json"
            
        context = await browser.new_context(**context_args)
        page = await context.new_page()

        url = "https://www.bigbasket.com/ps/?q=hot+wheels&nc=as"
        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(5000)
        
        html = await page.content()
        with open("bb_product.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        print("Saved HTML to bb_product.html")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_bb())

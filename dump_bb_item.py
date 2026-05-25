import asyncio
from playwright.async_api import async_playwright
import os

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        ctx = await browser.new_context(storage_state='sessions/bigbasket.json') if os.path.exists('sessions/bigbasket.json') else await browser.new_context()
        page = await ctx.new_page()
        
        await page.goto("https://www.bigbasket.com/ps/?q=hot+wheels&nc=as")
        await page.wait_for_timeout(8000)
        
        items = await page.query_selector_all("a[href*='/pd/'], div[class*='SKUDeck']")
        print(f"Found {len(items)} product blocks")
        
        if items:
            html = await items[0].inner_html()
            with open("bb_item.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Dumped HTML for first item to bb_item.html")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check())

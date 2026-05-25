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
        
        for item in items[:3]:
            # Try to get the title
            title_el = await item.query_selector("h3")
            if not title_el:
                title_el = await item.query_selector("[class*='BrandName']")
                
            # Try to get the price
            price_el = await item.query_selector("span[class*='Pricing'], div[class*='Pricing']")
            
            title = await title_el.inner_text() if title_el else "None"
            price = await price_el.inner_text() if price_el else "None"
            
            print(f"Title: {title.strip()}")
            print(f"Price: {price.strip()}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check())

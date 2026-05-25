import asyncio
from playwright.async_api import async_playwright
import os

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(storage_state='sessions/firstcry.json') if os.path.exists('sessions/firstcry.json') else await browser.new_context()
        page = await ctx.new_page()
        
        await page.goto("https://www.firstcry.com/search-result?q=hot+wheels")
        await page.wait_for_timeout(5000)
        
        # Test 1: By API
        print("Waiting to see if we can just scrape DOM")
        items = await page.query_selector_all("div.li_inner_block, div.list_block, [class*='ProductCard']")
        print(f"Found {len(items)} product blocks")
        
        for item in items[:3]:
            title_el = await item.query_selector("a[title]")
            if not title_el:
                title_el = await item.query_selector("div.li_txt1 a, [class*='title']")
            title = await title_el.get_attribute("title") if title_el else (await title_el.inner_text() if title_el else "None")
            
            price_el = await item.query_selector("span.r1 a, span.rupee a, span.rupee, [class*='price']")
            price = await price_el.inner_text() if price_el else "None"
            
            print(f"Title: {title.strip() if title else title}")
            print(f"Price: {price.strip() if price else price}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check())

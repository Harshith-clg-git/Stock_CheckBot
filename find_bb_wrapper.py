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
        
        # Let's find all h3 elements which usually contain the titles
        h3s = await page.query_selector_all("h3")
        print(f"Found {len(h3s)} h3 elements")
        
        # Find the wrapper which contains the h3 and price
        # The common ancestor of the h3 and the price element is likely a li or div
        for h3 in h3s[:3]:
            title = await h3.inner_text()
            print(f"h3 text: {title.strip()}")
            
            # Get the parent 2 levels up
            parent = await h3.evaluate_handle("el => el.parentElement.parentElement")
            tag = await parent.evaluate("el => el.tagName")
            cls = await parent.evaluate("el => el.className")
            print(f"Parent tagName: {tag}, className: {cls}")
            
            price_el = await parent.query_selector("span:has-text('₹')")
            if price_el:
                price = await price_el.inner_text()
                print(f"Price: {price}")
            else:
                print("Price not found in this parent")
            print("-" * 20)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check())

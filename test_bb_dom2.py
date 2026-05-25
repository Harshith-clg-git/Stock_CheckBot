import asyncio
import re
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
            title_el = await item.query_selector("h3, [class*='BrandName']")
            price_el = await item.query_selector("span[class*='Pricing'], div[class*='Pricing'], span:has-text('₹')")
            
            title = await title_el.inner_text() if title_el else ""
            title = title.replace("\n", " ").strip()
            
            item_text = await item.inner_text()
            if "out of stock" in item_text.lower() or "notify me" in item_text.lower():
                print(f"Skipping {title} (out of stock)")
                continue
            
            price_text = await price_el.inner_text() if price_el else ""
            print(f"Raw price_text: {price_text}")
            price_match = re.search(r'(?:₹|Rs\.?)\s*(\d+)', price_text, re.IGNORECASE)
            price = f"₹{price_match.group(1)}" if price_match else "Unknown"
            
            href = await item.get_attribute("href")
            if not href:
                link_el = await item.query_selector("a[href*='/pd/']")
                href = await link_el.get_attribute("href") if link_el else ""
            
            print(f"Title: {title}")
            print(f"Price: {price}")
            print(f"Href: {href}")
            print("-" * 20)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check())

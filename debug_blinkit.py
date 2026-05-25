"""
Debug script — runs Playwright visibly so you can see what the bot sees.
Saves a screenshot and dumps product titles found on the page.
"""
import asyncio
from playwright.async_api import async_playwright

SEARCH_URL = "https://blinkit.com/s/?q=hot+wheels"

async def debug():
    async with async_playwright() as p:
        # Run NON-headless so you can see the browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("Opening Blinkit...")
        await page.goto(SEARCH_URL, timeout=60000)

        # Wait longer for JS to load
        await page.wait_for_timeout(8000)

        # Save screenshot to see what the page looks like
        await page.screenshot(path="debug_screenshot.png", full_page=True)
        print("Screenshot saved as debug_screenshot.png")

        # Try multiple selector strategies and print what we find
        print("\n--- Trying selectors ---")

        selectors_to_try = [
            "[data-testid='product']",
            ".product-container",
            ".plp-product",
            "[class*='Product']",
            "[class*='product']",
            "a[href*='/prn/']",
            "div[class*='plp']",
        ]

        for sel in selectors_to_try:
            items = await page.query_selector_all(sel)
            print(f"  {sel:40s} => {len(items)} elements found")

        # Print page title to confirm what loaded
        title = await page.title()
        print(f"\nPage title: {title}")

        # Check if location popup is visible
        location_modal = await page.query_selector("[class*='LocationPopup'], [class*='location-modal'], [class*='AddressModal']")
        if location_modal:
            print("\n⚠️  LOCATION POPUP DETECTED — bot needs to set location first!")
        else:
            print("\n✅ No location popup detected")

        # Dump all visible text from the page (first 3000 chars)
        body_text = await page.inner_text("body")
        print("\n--- Page text preview (first 2000 chars) ---")
        print(body_text[:2000])

        input("\nPress ENTER to close the browser...")
        await browser.close()

asyncio.run(debug())

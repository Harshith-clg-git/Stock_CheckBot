import asyncio
import json
import sys
sys.stdout.reconfigure(encoding="utf-8")
from playwright.async_api import async_playwright
from config import BLINKIT_LAT, BLINKIT_LON

async def check_location():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        api_responses = []

        async def handle_response(response):
            if "v1/layout/search" in response.url:
                try:
                    body = await response.text()
                    data = json.loads(body)
                    api_responses.append(data)
                    print(f"API URL: {response.url}")
                except Exception as e:
                    print(f"Error parsing response: {e}")

        page.on("response", handle_response)

        search_url = f"https://blinkit.com/s/?q=hot+wheels&lat={BLINKIT_LAT}&lon={BLINKIT_LON}"
        print(f"Opening URL: {search_url}")
        
        await page.goto(search_url, timeout=60000)
        await page.wait_for_timeout(5000)
        
        location_modal = await page.query_selector("[class*='LocationPopup'], [class*='location-modal'], [class*='AddressModal'], [class*='SelectLocation']")
        if location_modal:
            print("⚠️ LOCATION POPUP IS VISIBLE!")
        else:
            print("✅ No location popup visible.")
            
        location_header = await page.query_selector("header [class*='location'], [class*='Address']")
        if location_header:
            text = await location_header.inner_text()
            print(f"Header Location Text: {text.strip()}")
            
        for idx, resp in enumerate(api_responses):
            print(f"API Response {idx} size: {len(str(resp))}")
            # print snippets count
            snippets = resp.get("response", {}).get("snippets", [])
            print(f"Snippets count: {len(snippets)}")

        await browser.close()

asyncio.run(check_location())

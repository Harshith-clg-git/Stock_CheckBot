import asyncio
import json
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding="utf-8")

async def debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        captured = []

        async def handle_response(response):
            if "v1/layout/search" in response.url:
                try:
                    body = await response.text()
                    captured.append(json.loads(body))
                except Exception:
                    pass

        page.on("response", handle_response)
        await page.goto("https://blinkit.com/s/?q=hot+wheels&lat=17.4297&lon=78.4406", timeout=60000)
        await page.wait_for_timeout(8000)
        await browser.close()

    # Find first real product and print ALL its top-level keys + full JSON
    for api_data in captured[:1]:
        snippets = api_data.get("response", {}).get("snippets", [])
        for snippet in snippets:
            data = snippet.get("data", {})
            pid = data.get("identity", {}).get("id", "")
            if pid and pid.isdigit():
                print(f"Product ID: {pid}")
                print(f"Top-level keys: {list(data.keys())}")
                print()
                # Search recursively for any key containing 'price' or 'mrp'
                def find_price_fields(obj, path=""):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            full_path = f"{path}.{k}" if path else k
                            if any(x in k.lower() for x in ("price", "mrp", "cost", "amount")):
                                print(f"  PRICE FIELD: {full_path} = {v}")
                            find_price_fields(v, full_path)
                    elif isinstance(obj, list):
                        for i, v in enumerate(obj):
                            find_price_fields(v, f"{path}[{i}]")

                find_price_fields(data)
                break

asyncio.run(debug())

import asyncio
import os
import sys
from playwright.async_api import async_playwright

PLATFORMS = {
    "1": ("bigbasket", "https://www.bigbasket.com/"),
    "2": ("zepto", "https://www.zepto.com/"),
    "3": ("blinkit", "https://www.blinkit.com/"),
    "4": ("firstcry", "https://www.firstcry.com/"),
}

async def setup_session(platform_name: str, url: str):
    os.makedirs("sessions", exist_ok=True)
    state_file = f"sessions/{platform_name}.json"

    print(f"\n=======================================================")
    print(f"🚀 Setting up session for: {platform_name.upper()}")
    print(f"Opening browser to {url} ...")
    print(f"=======================================================")
    
    async with async_playwright() as p:
        # Launch visible browser for user to interact
        browser = await p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        
        context_args = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        
        # Load existing session if present
        if os.path.exists(state_file):
            context_args["storage_state"] = state_file
            
        context = await browser.new_context(**context_args)
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Note on navigation: {e}")
        
        print("\n" + "="*60)
        print(f"👉 INSTRUCTIONS:")
        print(f"1. In the open browser window, click Location / Address selector.")
        print(f"2. Set your exact Hyderabad address / pincode (e.g. 500073).")
        print(f"3. Search for 'Hot Wheels' to confirm products load for your area.")
        print(f"4. Once done, return to this terminal and press ENTER.")
        print("="*60 + "\n")
        
        # Wait for user confirmation in terminal
        await asyncio.get_event_loop().run_in_executor(None, input, "Press ENTER here when location is set and products are visible...")
        
        # Save session state (cookies, localStorage, session tokens)
        await context.storage_state(path=state_file)
        print(f"\n✅ Session successfully saved to {state_file}")
        
        await browser.close()

async def main():
    print("\nSelect platform to set up location session:")
    for k, (name, _) in PLATFORMS.items():
        print(f"  [{k}] {name.title()}")
    print("  [5] All Platforms sequentially")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice in PLATFORMS:
        name, url = PLATFORMS[choice]
        await setup_session(name, url)
    elif choice == "5":
        for k in ["1", "2", "3", "4"]:
            name, url = PLATFORMS[k]
            await setup_session(name, url)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    asyncio.run(main())

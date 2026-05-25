import asyncio
import os
from playwright.async_api import async_playwright

async def setup_session(platform_name, url):
    # Ensure sessions directory exists
    os.makedirs("sessions", exist_ok=True)
    state_file = f"sessions/{platform_name}.json"

    print(f"\n--- Setting up {platform_name} ---")
    print(f"Opening {url}...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Headless=False so you can see it
        
        context_args = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # We always start fresh here so we don't get stuck in a bad saved state
        context = await browser.new_context(**context_args)
        page = await context.new_page()
        
        await page.goto(url)
        
        print("\n" + "="*50)
        print(f"1. Please log in or set your location to Hyderabad in the browser window.")
        print(f"2. Make sure you can see products when you search for Hot Wheels.")
        print(f"3. Once you are done and everything looks good, press ENTER in this console.")
        print("="*50 + "\n")
        
        # Wait for user input in console
        input("Press ENTER here when you are done...")
        
        # Save the session state
        await context.storage_state(path=state_file)
        print(f"✅ Session saved to {state_file}")
        
        await browser.close()

if __name__ == "__main__":
    import sys
    
    platforms = {
        "1": ("swiggy", "https://www.swiggy.com/instamart"),
        "2": ("zepto", "https://www.zeptonow.com/"),
        "3": ("firstcry", "https://www.firstcry.com/"),
        "4": ("bigbasket", "https://www.bigbasket.com/")
    }
    
    print("Which platform do you want to set up?")
    for key, (name, url) in platforms.items():
        print(f"{key}. {name}")
        
    choice = input("\nEnter number (1-4): ")
    
    if choice in platforms:
        name, url = platforms[choice]
        asyncio.run(setup_session(name, url))
    else:
        print("Invalid choice.")

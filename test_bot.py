import asyncio
import sys
from loguru import logger
from database.db import init_db, process_product
from matcher.engine import match_category, is_priority

async def test_matcher():
    logger.info("--- Testing Keyword Matcher & Filter Rules ---")
    
    # 1. Test Valid Diecast Cars (Should MATCH)
    valid_cars = [
        ("Hot Wheels Super Treasure Hunt Nissan Skyline GT-R R34", "TREASURE_HUNT", True),
        ("Hot Wheels 1971 Porsche 911 GT3 RS White", "EXOTIC", True),
        ("Hot Wheels Toyota Supra Fast and Furious Premium", "PREMIUM", True),
        ("Hot Wheels Honda Civic Type R Red", "JDM", True),
        ("Hot Wheels 128/250 Datsun 620 Die Cast Free Wheel Toy Car - Orange", "JDM", False),
        ("Hot Wheels 53/25069 Chevelle Die Cat Free Wheel Toy Car- Green", "MUSCLE", False),
        ("Hot Wheels 67 Ford Mustang Shelby GT500", "MUSCLE", False),
        ("Hot Wheels BMW M3 E46 Blue", "EURO", False),
        ("Hot Wheels Volkswagen Golf MK7 Die Cast Free Wheel Toy Car", "EURO", False),
    ]

    for title, expected_cat, expected_priority in valid_cars:
        cat = match_category(title)
        prio = is_priority(title)
        logger.info(f"CAR: '{title}' -> Category: {cat} | Priority: {prio}")
        assert cat is not None, f"Expected match but got None for: {title}"
        assert prio == expected_priority, f"Priority mismatch for: {title}"

    # 2. Test Excluded Items (Should return None - NOT matched)
    excluded_items = [
        "Hot Wheels Color Shifters Track and 1 Car - Multicolour",
        "Hot Wheels Rapid Launch & Loop Playset with 1:64 Scale Die-Cast Toy Car",
        "Hot Wheels Stunt Tracks Rapid Launch Cyclone Track Set",
        "Hot Wheels Track Set with 2 Loops and 1 Hot Wheels Car",
        "Hot Wheels Monster Trucks Glow In Dark Multipack",
        "Hot Wheels Glow In Dark Free Wheel Die Cast Monster Truck Tri To Crush Me",
        "Hot Wheels Color Shifters Shark Hammer 2.0 Requin-Marteau 2.0 Toy Car",
        "Hot Wheels X-Blade Bike - RED & Black",
        "Hot Wheels 129/250 Standard Kart Die Cat Free Wheel Toy Car",
        "Hot Wheels Ultimate Dual Dragon Transporter",
        "Hot Wheels Batman Die-Cast Car Set 1:64 Scale Toy Cars Pack of 5",
        "Hot Wheels LGNDS Die Cast Free Wheel Toy Car Pack of 6",
        "Toyshine Thaar Pullback Die Cast Car (Black)",
        "Frendo Premium Metal 1:64 Die Cast Car",
        "Chigy Wooh Defender Pullback Die Cast Car",
        "Hot Wheels School Backpack with Pencil Case",
    ]

    for item in excluded_items:
        cat = match_category(item)
        logger.info(f"EXCLUDED: '{item}' -> Match: {cat}")
        assert cat is None, f"Item was NOT excluded as expected: {item} (matched as {cat})"

    logger.success("All keyword matching and exclusion tests passed successfully!\n")


async def main():
    await test_matcher()

if __name__ == "__main__":
    asyncio.run(main())

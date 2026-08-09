import asyncio
import sys
from loguru import logger
from database.db import init_db, process_product
from matcher.engine import match_category, is_priority
from notifier.telegram_bot import send_telegram_alert

async def test_matcher():
    logger.info("--- Testing Keyword Matcher ---")
    test_titles = [
        ("Hot Wheels Super Treasure Hunt Nissan Skyline GT-R R34", "TREASURE_HUNT", True),
        ("Hot Wheels 1971 Porsche 911 GT3 RS White", "EXOTIC", True),
        ("Hot Wheels Toyota Supra Fast and Furious Premium", "PREMIUM", True),
        ("Hot Wheels Honda Civic Type R Red", "JDM", True),
        ("Hot Wheels 67 Ford Mustang Shelby GT500", "MUSCLE", False),
        ("Hot Wheels BMW M3 E46 Blue", "EURO", False),
        ("Hot Wheels Track Set Builder", "MAINLINE", False),
    ]

    for title, expected_cat, expected_priority in test_titles:
        cat = match_category(title)
        prio = is_priority(title)
        logger.info(f"Title: '{title}' -> Category: {cat} | Priority: {prio}")
        assert cat is not None, f"Failed to match category for '{title}'"
        assert prio == expected_priority, f"Priority mismatch for '{title}'"

    logger.success("Keyword matcher test passed!\n")


async def test_database():
    logger.info("--- Testing Database Operations ---")
    import os
    if os.path.exists("test_database.db"):
        try:
            os.remove("test_database.db")
        except Exception:
            pass

    init_db("test_database.db")

    sample = {
        "id": "test_123",
        "title": "Hot Wheels Nissan Skyline GT-R R34",
        "price": "₹179",
        "platform": "blinkit",
        "link": "https://blinkit.com/test",
        "category": "JDM"
    }

    alert, alert_type = process_product(sample, db_path="test_database.db")
    logger.info(f"First insert: alert={alert}, type='{alert_type}'")
    assert alert is True and alert_type == "NEW", "First insert should trigger NEW alert"

    alert_again, alert_type_again = process_product(sample, db_path="test_database.db")
    logger.info(f"Second insert (duplicate): alert={alert_again}, type='{alert_type_again}'")
    assert alert_again is False, "Duplicate insert should not trigger alert"

    logger.success("Database state test passed!\n")


async def main():
    await test_matcher()
    await test_database()
    logger.success("🎉 All dry-run tests passed successfully!")

if __name__ == "__main__":
    asyncio.run(main())

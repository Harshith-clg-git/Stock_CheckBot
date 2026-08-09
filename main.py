import argparse
import asyncio
import sys
from loguru import logger

from database.db import init_db, process_product, mark_missing_products_oos
from matcher.engine import match_category
from notifier.telegram_bot import send_telegram_alert

from platforms.blinkit import BlinkitScraper
from platforms.zepto import ZeptoScraper
from platforms.firstcry import FirstCryScraper
from platforms.bigbasket import BigBasketScraper

# Reconfigure stdout to UTF-8 for Windows compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Configure logger format
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)

SCRAPERS = [
    BlinkitScraper(),
    ZeptoScraper(),
    FirstCryScraper(),
    BigBasketScraper(),
]


async def run_scan_cycle():
    """Runs a single scan cycle across all configured platforms."""
    logger.info("🚗 Starting Hot Wheels Multi-Platform Stock Check...")
    
    total_found = 0
    total_alerts = 0

    for scraper in SCRAPERS:
        platform_name = scraper.platform_name
        logger.info(f"[{platform_name.upper()}] Scanning...")

        try:
            products = await scraper.fetch_products()
        except Exception as e:
            logger.error(f"[{platform_name.upper()}] Error fetching products: {e}")
            continue

        logger.info(f"[{platform_name.upper()}] Found {len(products)} active products")
        total_found += len(products)
        scraped_ids = set()

        for product in products:
            product["platform"] = platform_name
            scraped_ids.add(product["id"])

            category = match_category(product["title"])
            if not category:
                continue

            product["category"] = category
            should_alert, alert_type = process_product(product)

            if should_alert:
                logger.success(
                    f"[{platform_name.upper()}] MATCH ({category}): {product['title']} — {product.get('price', 'N/A')}"
                )
                total_alerts += 1

                await send_telegram_alert(
                    title=product["title"],
                    price=product.get("price", "Unknown"),
                    link=product.get("link", ""),
                    platform=platform_name,
                    category=category,
                    alert_type=alert_type
                )

        mark_missing_products_oos(scraped_ids, platform_name)

    logger.info(f"🏁 Scan complete. Total active: {total_found} | New Alerts Sent: {total_alerts}")


async def main():
    parser = argparse.ArgumentParser(description="Hot Wheels Stock Checker Bot")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single scan cycle and exit (recommended for GitHub Actions)."
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Scan interval in seconds for continuous daemon mode (default: 300s)."
    )
    args = parser.parse_args()

    init_db()

    if args.once:
        logger.info("Running in Single-Scan Mode (--once)")
        await run_scan_cycle()
    else:
        logger.info(f"Running in Continuous Daemon Mode (Interval: {args.interval}s)")
        while True:
            await run_scan_cycle()
            logger.info(f"Sleeping for {args.interval}s until next scan cycle...")
            await asyncio.sleep(args.interval)


if __name__ == "__main__":
    asyncio.run(main())

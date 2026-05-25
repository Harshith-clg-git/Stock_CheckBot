import asyncio
import sqlite3
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from loguru import logger

from platforms.blinkit          import fetch_products as blinkit_fetch
from platforms.swiggy_instamart import fetch_products as swiggy_fetch
from platforms.zepto            import fetch_products as zepto_fetch
from platforms.firstcry         import fetch_products as firstcry_fetch
from platforms.bigbasket        import fetch_products as bigbasket_fetch

from matcher.keywords import match_keywords
from notifier.whatsapp import send_alert
from config import SCAN_INTERVAL


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_connection():
    return sqlite3.connect("database.db")


def _ensure_schema():
    """Make sure the DB table exists with the platform column."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Drop table on every startup so the bot forgets previous runs.
    # This ensures it sends alerts for ALL currently available products 
    # on the first scan, but only new/restocked products while it keeps running.
    cur.execute("DROP TABLE IF EXISTS products")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            title      TEXT,
            platform   TEXT,
            alerted    INTEGER,
            active     INTEGER
        )
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Per-platform scan
# ---------------------------------------------------------------------------

async def scan_platform(platform_name: str, fetch_fn):
    """Fetch products from one platform and handle alerting."""
    logger.info(f"[{platform_name}] Scanning...")

    try:
        products = await fetch_fn()
    except Exception as e:
        logger.error(f"[{platform_name}] Fetch failed: {e}")
        return set()

    logger.info(f"[{platform_name}] Found {len(products)} products")

    current_ids = set()
    conn = get_connection()
    cur = conn.cursor()

    for product in products:
        product_id = product["id"]
        title      = product["title"]
        price      = product["price"]
        link       = product["link"]
        platform   = product.get("platform", platform_name)

        current_ids.add(product_id)

        category = match_keywords(title)
        if not category:
            continue

        logger.info(f"[{platform_name}] MATCH ({category}): {title} — {price}")

        cur.execute(
            "SELECT alerted, active FROM products WHERE product_id=?",
            (product_id,)
        )
        row = cur.fetchone()

        if row is None:
            # New product — alert immediately
            try:
                send_alert(title, price, link, platform=platform, category=category)
                logger.success(f"[{platform_name}] Alert sent: {title}")
            except Exception as e:
                logger.error(f"[{platform_name}] Alert failed: {e}")

            cur.execute(
                "INSERT INTO products VALUES (?, ?, ?, ?, ?)",
                (product_id, title, platform, 1, 1)
            )

        else:
            alerted, active = row
            if active == 0:
                # Product reappeared after going out of stock
                try:
                    send_alert(title, price, link, platform=platform, category=category)
                    logger.success(f"[{platform_name}] Restock alert: {title}")
                except Exception as e:
                    logger.error(f"[{platform_name}] Alert failed: {e}")

                cur.execute(
                    "UPDATE products SET active=1 WHERE product_id=?",
                    (product_id,)
                )

    # Mark products no longer seen as inactive
    cur.execute(
        "SELECT product_id FROM products WHERE platform=?", (platform_name,)
    )
    for (pid,) in cur.fetchall():
        if pid not in current_ids:
            cur.execute(
                "UPDATE products SET active=0 WHERE product_id=?", (pid,)
            )

    conn.commit()
    conn.close()
    return current_ids


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

PLATFORMS = [
    ("blinkit",          blinkit_fetch),
    ("swiggy_instamart", swiggy_fetch),
    ("zepto",            zepto_fetch),
    ("firstcry",         firstcry_fetch),
    ("bigbasket",        bigbasket_fetch),
]


async def scan_all():
    """Run all platform scans sequentially to save memory on free tier."""
    logger.info("=" * 50)
    logger.info("Starting scan across all platforms sequentially...")
    
    for name, fn in PLATFORMS:
        try:
            await scan_platform(name, fn)
        except Exception as e:
            logger.error(f"[{name}] Unhandled error: {e}")
            
    logger.info("Scan complete.")


def _start_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    class DummyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Hotwheels bot is running!")
        def log_message(self, format, *args):
            pass # Disable noisy logs
            
    def run_server():
        server = HTTPServer(("0.0.0.0", port), DummyHandler)
        logger.info(f"Started dummy health check server on port {port}")
        server.serve_forever()

    threading.Thread(target=run_server, daemon=True).start()

async def main():
    _start_dummy_server()
    _ensure_schema()
    logger.info("🚗 Hot Wheels Multi-Platform Bot started")
    logger.info(f"Platforms: {[p[0] for p in PLATFORMS]}")

    while True:
        try:
            await scan_all()
        except Exception as e:
            logger.error(f"Scan cycle error: {e}")

        logger.info(f"Sleeping {SCAN_INTERVAL}s until next scan...")
        await asyncio.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())

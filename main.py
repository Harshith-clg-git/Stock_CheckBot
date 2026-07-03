import asyncio
import sqlite3
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from loguru import logger

from platforms.blinkit          import fetch_products as blinkit_fetch
from platforms.zepto            import fetch_products as zepto_fetch
from platforms.firstcry         import fetch_products as firstcry_fetch
from platforms.bigbasket        import fetch_products as bigbasket_fetch

from matcher.keywords import match_keywords
from notifier.whatsapp import send_alert
from config import (
    SCAN_INTERVAL,
    ZEPTO_SCAN_INTERVAL,
    FIRSTCRY_SCAN_INTERVAL,
    BIGBASKET_SCAN_INTERVAL
)
import time

# Global flag to track if this is the very first scan after startup
INITIAL_RUN = True


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_connection():
    return sqlite3.connect("database.db")


def _ensure_schema():
    """Make sure the DB table exists with the platform column."""
    conn = get_connection()
    cur = conn.cursor()
    
    # We no longer drop the table. We will use INITIAL_RUN to prevent startup spam.
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
    ("blinkit",          blinkit_fetch,   SCAN_INTERVAL),
    ("zepto",            zepto_fetch,     ZEPTO_SCAN_INTERVAL),
    ("firstcry",         firstcry_fetch,  FIRSTCRY_SCAN_INTERVAL),
    ("bigbasket",        bigbasket_fetch, BIGBASKET_SCAN_INTERVAL),
]

last_scan_times = {p[0]: 0 for p in PLATFORMS}

async def scan_due_platforms():
    """Run platform scans sequentially if they are due, to save memory on free tier."""
    global INITIAL_RUN
    now = time.time()
    
    scanned_any = False
    for name, fn, interval in PLATFORMS:
        if now - last_scan_times[name] >= interval:
            scanned_any = True
            try:
                await scan_platform(name, fn)
            except Exception as e:
                logger.error(f"[{name}] Unhandled error: {e}")
            last_scan_times[name] = time.time()
            
    if scanned_any and INITIAL_RUN:
        logger.info("Initial baseline scan complete. Future scans will send alerts.")
        INITIAL_RUN = False


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
            await scan_due_platforms()
        except Exception as e:
            logger.error(f"Scan cycle error: {e}")

        logger.info("Sleeping 30s until next check...")
        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())

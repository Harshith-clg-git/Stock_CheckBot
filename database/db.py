import sqlite3
import time
from typing import Dict, Tuple, Optional
from loguru import logger

DEFAULT_DB = "database.db"

def get_connection(db_path: str = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB):
    """Initializes the database schema if it doesn't already exist."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    
    # Check if existing products table has required columns
    cur.execute("PRAGMA table_info(products)")
    columns = [row["name"] for row in cur.fetchall()]

    if columns and "in_stock" not in columns:
        logger.warning("Migrating old database table schema...")
        cur.execute("DROP TABLE products")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id    TEXT PRIMARY KEY,
            title         TEXT NOT NULL,
            price         TEXT,
            platform      TEXT NOT NULL,
            link          TEXT,
            category      TEXT,
            in_stock      INTEGER DEFAULT 1,
            first_seen_at REAL,
            last_seen_at  REAL,
            last_alert_at REAL
        )
    """)
    conn.commit()
    conn.close()


def process_product(product: Dict, db_path: str = DEFAULT_DB) -> Tuple[bool, str]:
    """
    Evaluates a scraped product against database state.
    Returns (should_alert, alert_type) where alert_type is 'NEW' or 'RESTOCK'.
    """
    pid      = str(product["id"])
    title    = product["title"]
    price    = product.get("price", "Unknown")
    platform = product.get("platform", "unknown")
    link     = product.get("link", "")
    category = product.get("category", "MAINLINE")
    now      = time.time()

    conn = get_connection(db_path)
    cur  = conn.cursor()

    cur.execute(
        "SELECT product_id, in_stock, price FROM products WHERE product_id = ?",
        (pid,)
    )
    row = cur.fetchone()

    should_alert = False
    alert_type   = ""

    if row is None:
        # Brand new product in stock
        should_alert = True
        alert_type   = "NEW"
        cur.execute(
            """
            INSERT INTO products 
            (product_id, title, price, platform, link, category, in_stock, first_seen_at, last_seen_at, last_alert_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
            """,
            (pid, title, price, platform, link, category, now, now, now)
        )
    else:
        was_in_stock = row["in_stock"]
        if was_in_stock == 0:
            # Reappeared after being out of stock
            should_alert = True
            alert_type   = "RESTOCK"
            cur.execute(
                """
                UPDATE products 
                SET title = ?, price = ?, link = ?, category = ?, in_stock = 1, last_seen_at = ?, last_alert_at = ?
                WHERE product_id = ?
                """,
                (title, price, link, category, now, now, pid)
            )
        else:
            # Still in stock, update metadata silently
            cur.execute(
                """
                UPDATE products 
                SET title = ?, price = ?, link = ?, category = ?, last_seen_at = ?
                WHERE product_id = ?
                """,
                (title, price, link, category, now, pid)
            )

    conn.commit()
    conn.close()
    return should_alert, alert_type


def mark_missing_products_oos(scraped_ids: set, platform: str, db_path: str = DEFAULT_DB):
    """Marks database entries for a platform as out of stock if not found in current scan."""
    if not scraped_ids:
        return

    conn = get_connection(db_path)
    cur  = conn.cursor()

    cur.execute(
        "SELECT product_id FROM products WHERE platform = ? AND in_stock = 1",
        (platform,)
    )
    active_rows = cur.fetchall()

    for row in active_rows:
        pid = row["product_id"]
        if pid not in scraped_ids:
            cur.execute(
                "UPDATE products SET in_stock = 0 WHERE product_id = ?",
                (pid,)
            )

    conn.commit()
    conn.close()

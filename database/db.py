import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    title      TEXT,
    platform   TEXT,
    alerted    INTEGER,
    active     INTEGER
)
''')

# Migrate existing rows — add platform column if it doesn't exist yet
try:
    cur.execute("ALTER TABLE products ADD COLUMN platform TEXT DEFAULT 'blinkit'")
except Exception:
    pass  # column already exists

conn.commit()
conn.close()

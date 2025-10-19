import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "bot.db"
PRODUCTS_FILE = Path(__file__).parent / "products.json"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            lang TEXT DEFAULT 'uz',
            balance INTEGER DEFAULT 0
        )
    """)

    # payments
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            screenshot TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # orders
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_type TEXT,
            item_code TEXT,
            details TEXT,
            price INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # products
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            name TEXT,
            type TEXT,
            price INTEGER
        )
    """)

    # settings (admin card, min/max topup)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()

    # init default settings if not present
    cur.execute("SELECT value FROM settings WHERE key='admin_card'")
    if not cur.fetchone():
        cur.execute("INSERT INTO settings(key,value) VALUES(?,?)", ("admin_card", "9860 1234 5678 9012"))
    cur.execute("SELECT value FROM settings WHERE key='topup_min'")
    if not cur.fetchone():
        cur.execute("INSERT INTO settings(key,value) VALUES(?,?)", ("topup_min", "10000"))
    cur.execute("SELECT value FROM settings WHERE key='topup_max'")
    if not cur.fetchone():
        cur.execute("INSERT INTO settings(key,value) VALUES(?,?)", ("topup_max", "1000000"))

    conn.commit()

    # load products from products.json into products table (if not present)
    if PRODUCTS_FILE.exists():
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            products = json.load(f)
        for p in products:
            cur.execute("SELECT 1 FROM products WHERE code=?", (p["code"],))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO products(code,name,type,price) VALUES(?,?,?,?)",
                    (p["code"], p["name"], p["type"], p["price"])
                )
    conn.commit()
    conn.close()


# ========== Users ==========
def get_or_create_user(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users(user_id) VALUES(?)", (user_id,))
        conn.commit()
    conn.close()

def set_user_lang(user_id: int, lang: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
    conn.commit()
    conn.close()

def get_user_balance(user_id: int) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row["balance"] if row else 0

def update_balance(user_id: int, new_balance: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance=? WHERE user_id=?", (new_balance, user_id))
    conn.commit()
    conn.close()

def add_balance(user_id: int, amount: int):
    bal = get_user_balance(user_id)
    update_balance(user_id, bal + amount)


# ========== Payments ==========
def create_payment(user_id: int, amount: int) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO payments(user_id,amount) VALUES(?,?)", (user_id, amount))
    pid = cur.lastrowid
    conn.commit()
    conn.close()
    return pid

def set_payment_screenshot(pid: int, file_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE payments SET screenshot=? WHERE id=?", (file_id, pid))
    conn.commit()
    conn.close()

def set_payment_status(pid: int, status: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE payments SET status=? WHERE id=?", (status, pid))
    conn.commit()
    conn.close()

def get_pending_payments():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM payments WHERE status='pending' ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def approve_topup(pid: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id, amount FROM payments WHERE id=?", (pid,))
    row = cur.fetchone()
    if row:
        uid = row["user_id"]
        amt = row["amount"]
        add_balance(uid, amt)
        set_payment_status(pid, "approved")
    conn.close()


# ========== Orders ==========
def create_order(user_id: int, item_type: str, item_code: str, details: str, price: int) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders(user_id,item_type,item_code,details,price) VALUES(?,?,?,?,?)",
        (user_id, item_type, item_code, details, price)
    )
    oid = cur.lastrowid
    conn.commit()
    conn.close()
    return oid

def get_pending_orders():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE status='pending' ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def set_order_status(order_id: int, status: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()

def approve_order(order_id: int):
    set_order_status(order_id, "approved")


# ========== Products ==========
def get_products(product_type: str = None):
    conn = get_conn()
    cur = conn.cursor()
    if product_type:
        cur.execute("SELECT * FROM products WHERE type=? ORDER BY id", (product_type,))
    else:
        cur.execute("SELECT * FROM products ORDER BY id")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_product_by_code(code: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE code=?", (code,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def add_product(code: str, name: str, type_: str, price: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO products(code,name,type,price) VALUES(?,?,?,?)", (code, name, type_, price))
    conn.commit()
    conn.close()

def update_product(code: str, name: str, type_: str, price: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE products SET name=?, type=?, price=? WHERE code=?", (name, type_, price, code))
    conn.commit()
    conn.close()

def delete_product(code: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE code=?", (code,))
    conn.commit()
    conn.close()


# ========== Settings ==========
def get_setting(key: str, default=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = cur.fetchone()
    conn.close()
    return row["value"] if row else default

def set_setting(key: str, value: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, value))
    conn.commit()
    conn.close()

def get_payment_settings():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM settings")
    rows = {r["key"]: r["value"] for r in cur.fetchall()}
    conn.close()
    return {
        "card": rows.get("admin_card", "N/A"),
        "min_sum": int(rows.get("topup_min", "10000")),
        "max_sum": int(rows.get("topup_max", "1000000")),
    }


def update_payment_settings(card=None, min_sum=None, max_sum=None):
    conn = get_conn()
    cur = conn.cursor()
    if card:
        cur.execute("UPDATE settings SET value=? WHERE key='admin_card'", (card,))
    if min_sum:
        cur.execute("UPDATE settings SET value=? WHERE key='topup_min'", (min_sum,))
    if max_sum:
        cur.execute("UPDATE settings SET value=? WHERE key='topup_max'", (max_sum,))
    conn.commit()
    conn.close()

import sqlite3
import os
from pathlib import Path

# --- Paths ---
BASE = Path(__file__).parent
DB_PATH = BASE / "storage.db"


# --- Connection ---
def get_conn():
    os.makedirs(BASE, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


conn = get_conn()


# --- Initialize Database ---
def init_db():
    c = conn.cursor()
    # Users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id INTEGER UNIQUE,
            nick TEXT,
            lang TEXT DEFAULT "uz",
            balance INTEGER DEFAULT 0
        )
    ''')
    # Payments (Top-ups)
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_tg INTEGER,
            amount INTEGER,
            screenshot_file_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Orders (Purchases)
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_tg INTEGER,
            item_type TEXT,
            item_code TEXT,
            details TEXT,
            price INTEGER,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()


init_db()

# =====================================================
# 🧍 USER HELPERS
# =====================================================

def get_or_create_user(tg_id):
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE tg_id=?', (tg_id,))
    r = c.fetchone()
    if r:
        return dict(r)
    c.execute('INSERT INTO users(tg_id) VALUES(?)', (tg_id,))
    conn.commit()
    c.execute('SELECT * FROM users WHERE tg_id=?', (tg_id,))
    return dict(c.fetchone())


def set_user_nick(tg_id, nick):
    c = conn.cursor()
    c.execute('UPDATE users SET nick=? WHERE tg_id=?', (nick, tg_id))
    conn.commit()


def set_user_lang(tg_id, lang):
    c = conn.cursor()
    c.execute('UPDATE users SET lang=? WHERE tg_id=?', (lang, tg_id))
    conn.commit()


def get_balance(tg_id):
    c = conn.cursor()
    c.execute('SELECT balance FROM users WHERE tg_id=?', (tg_id,))
    r = c.fetchone()
    return r['balance'] if r else 0


def add_balance(tg_id, amt):
    c = conn.cursor()
    c.execute('UPDATE users SET balance = balance + ? WHERE tg_id=?', (amt, tg_id))
    conn.commit()


def deduct_balance(tg_id, amt):
    bal = get_balance(tg_id)
    if bal < amt:
        return False
    c = conn.cursor()
    c.execute('UPDATE users SET balance = balance - ? WHERE tg_id=?', (amt, tg_id))
    conn.commit()
    return True


# =====================================================
# 💰 PAYMENTS (TOP-UPS)
# =====================================================

def create_payment(tg_id, amt):
    c = conn.cursor()
    c.execute('INSERT INTO payments(user_tg, amount) VALUES(?, ?)', (tg_id, amt))
    conn.commit()
    return c.lastrowid


def set_payment_screenshot(pid, file_id):
    c = conn.cursor()
    c.execute('UPDATE payments SET screenshot_file_id=? WHERE id=?', (file_id, pid))
    conn.commit()


def set_payment_status(pid, status):
    c = conn.cursor()
    c.execute('UPDATE payments SET status=? WHERE id=?', (status, pid))
    conn.commit()


def get_pending_payments():
    c = conn.cursor()
    c.execute('SELECT * FROM payments WHERE status="pending" ORDER BY id DESC')
    return [dict(r) for r in c.fetchall()]


def get_all_payments():
    c = conn.cursor()
    c.execute('SELECT * FROM payments ORDER BY id DESC')
    return [dict(r) for r in c.fetchall()]


# =====================================================
# 🛒 ORDERS
# =====================================================

def create_order(tg_id, item_type, item_code, details, price):
    c = conn.cursor()
    c.execute('INSERT INTO orders(user_tg, item_type, item_code, details, price) VALUES(?,?,?,?,?)',
              (tg_id, item_type, item_code, details, price))
    conn.commit()
    return c.lastrowid


def set_order_status(order_id, status):
    c = conn.cursor()
    c.execute('UPDATE orders SET status=? WHERE id=?', (status, order_id))
    conn.commit()


def get_user_orders(tg_id):
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE user_tg=? ORDER BY id DESC', (tg_id,))
    return [dict(r) for r in c.fetchall()]


def get_pending_orders():
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE status="pending" ORDER BY id DESC')
    return [dict(r) for r in c.fetchall()]


# =====================================================
# 🧩 ADMIN COMPATIBILITY HELPERS
# =====================================================

# Aliases for older handler imports
def get_pending_topups():
    """Alias for get_pending_payments()"""
    return get_pending_payments()


def get_all_pending_orders():
    """Alias for get_pending_orders()"""
    return get_pending_orders()


def get_all_pending_topups():
    """Alias for get_pending_topups()"""
    return get_pending_topups()


def approve_topup(pid):
    """Approve top-up and set status to approved"""
    set_payment_status(pid, "approved")


def approve_order(order_id):
    """Approve order and set status to approved"""
    set_order_status(order_id, "approved")


def update_balance(tg_id, amount):
    """Add balance to user"""
    add_balance(tg_id, amount)


def get_user_balance(tg_id):
    """Get user current balance"""
    return get_balance(tg_id)

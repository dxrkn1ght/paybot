import sqlite3

DB_NAME = "bot.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================================
# 🧩 INIT DATABASE
# =====================================================
def init_db():
    conn = get_db()
    c = conn.cursor()

    # USERS jadvali
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_tg INTEGER PRIMARY KEY,
            lang TEXT DEFAULT 'uz',
            balance INTEGER DEFAULT 0
        )
    """)

    # PAYMENTS jadvali
    c.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_tg INTEGER,
            amount INTEGER,
            screenshot TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY(user_tg) REFERENCES users(user_tg)
        )
    """)

    # ORDERS jadvali
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_tg INTEGER,
            item_type TEXT,
            item_code TEXT,
            details TEXT,
            price INTEGER,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY(user_tg) REFERENCES users(user_tg)
        )
    """)

    conn.commit()
    conn.close()


# =====================================================
# 👤 USERS
# =====================================================
def get_or_create_user(user_tg):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_tg=?", (user_tg,))
    user = c.fetchone()
    if not user:
        c.execute("INSERT INTO users (user_tg) VALUES (?)", (user_tg,))
        conn.commit()
        c.execute("SELECT * FROM users WHERE user_tg=?", (user_tg,))
        user = c.fetchone()
    conn.close()
    return dict(user)


def set_user_lang(user_tg, lang):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET lang=? WHERE user_tg=?', (lang, user_tg))
    conn.commit()
    conn.close()


def get_balance(user_tg):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_tg=?", (user_tg,))
    row = c.fetchone()
    conn.close()
    return row["balance"] if row else 0


def add_balance(user_tg, amount):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_tg=?", (amount, user_tg))
    conn.commit()
    conn.close()


# =====================================================
# 💳 PAYMENTS
# =====================================================
def create_payment(user_tg, amount):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO payments(user_tg, amount) VALUES(?, ?)", (user_tg, amount))
    conn.commit()
    pid = c.lastrowid
    conn.close()
    return pid


def set_payment_screenshot(pid, file_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE payments SET screenshot=? WHERE id=?", (file_id, pid))
    conn.commit()
    conn.close()


def set_payment_status(pid, status):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE payments SET status=? WHERE id=?", (status, pid))
    conn.commit()
    conn.close()


def get_pending_payments():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM payments WHERE status='pending' ORDER BY id DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# =====================================================
# 🛒 ORDERS
# =====================================================
def create_order(user_tg, item_type, item_code, details, price):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO orders(user_tg, item_type, item_code, details, price) VALUES(?,?,?,?,?)',
              (user_tg, item_type, item_code, details, price))
    conn.commit()
    oid = c.lastrowid
    conn.close()
    return oid


def set_order_status(order_id, status):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE orders SET status=? WHERE id=?', (status, order_id))
    conn.commit()
    conn.close()


def get_user_orders(user_tg):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE user_tg=? ORDER BY id DESC', (user_tg,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_pending_orders():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE status="pending" ORDER BY id DESC')
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# =====================================================
# 🧩 ADMIN HELPERS
# =====================================================
def get_pending_topups():
    return get_pending_payments()


def approve_topup(pid):
    set_payment_status(pid, "approved")


def approve_order(order_id):
    set_order_status(order_id, "approved")


def update_balance(user_tg, amount):
    add_balance(user_tg, amount)


def get_user_balance(user_tg):
    return get_balance(user_tg)
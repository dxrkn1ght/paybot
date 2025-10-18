import sqlite3

def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        type TEXT
    )''')
    conn.commit()
    conn.close()

def add_product(name, price, type_):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, type) VALUES (?, ?, ?)", (name, price, type_))
    conn.commit()
    conn.close()

def get_products_by_type(type_):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM products WHERE type=?", (type_,))
    data = cursor.fetchall()
    conn.close()
    return data

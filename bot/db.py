import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__),'storage.db')

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_conn()

def init_db():
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        tg_id INTEGER UNIQUE, 
        nick TEXT, 
        lang TEXT DEFAULT "uz", 
        balance INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_tg INTEGER, 
        amount INTEGER, 
        screenshot_file_id TEXT, 
        status TEXT DEFAULT 'pending', 
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_tg INTEGER, 
        item_type TEXT, 
        details TEXT, 
        price INTEGER, 
        status TEXT DEFAULT 'pending', 
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()

init_db()

def get_or_create_user(tg_id):
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE tg_id=?',(tg_id,))
    r=c.fetchone()
    if r: return dict(r)
    c.execute('INSERT INTO users(tg_id) VALUES(?)',(tg_id,))
    conn.commit()
    c.execute('SELECT * FROM users WHERE tg_id=?',(tg_id,))
    return dict(c.fetchone())

def set_user_nick(tg_id,nick):
    c=conn.cursor()
    c.execute('UPDATE users SET nick=? WHERE tg_id=?',(nick,tg_id))
    conn.commit()

def set_user_lang(tg_id,lang):
    c=conn.cursor()
    c.execute('UPDATE users SET lang=? WHERE tg_id=?',(lang,tg_id))
    conn.commit()

def get_balance(tg_id):
    c=conn.cursor()
    c.execute('SELECT balance FROM users WHERE tg_id=?',(tg_id,))
    r=c.fetchone()
    return r['balance'] if r else 0

def add_balance(tg_id,amt):
    c=conn.cursor()
    c.execute('UPDATE users SET balance = balance + ? WHERE tg_id=?',(amt,tg_id))
    conn.commit()

def deduct_balance(tg_id,amt):
    c=conn.cursor()
    bal=get_balance(tg_id)
    if bal<amt: return False
    c.execute('UPDATE users SET balance = balance - ? WHERE tg_id=?',(amt,tg_id))
    conn.commit()
    return True

def create_payment(tg_id,amt):
    c=conn.cursor()
    c.execute('INSERT INTO payments(user_tg,amount) VALUES(?,?)',(tg_id,amt))
    conn.commit()
    return c.lastrowid

def set_payment_screenshot(pid,fid):
    c=conn.cursor()
    c.execute('UPDATE payments SET screenshot_file_id=? WHERE id=?',(fid,pid))
    conn.commit()

def create_order(tg_id,item,details,price):
    c=conn.cursor()
    c.execute('INSERT INTO orders(user_tg,item_type,details,price) VALUES(?,?,?,?)',(tg_id,item,details,price))
    conn.commit()
    return c.lastrowid

def get_user_orders(tg_id):
    c=conn.cursor()
    c.execute('SELECT * FROM orders WHERE user_tg=? ORDER BY id DESC',(tg_id,))
    return [dict(r) for r in c.fetchall()]

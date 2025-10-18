import json
from pathlib import Path
from db import create_order, get_or_create_user, add_balance, set_payment_screenshot, create_payment, set_payment_status, get_pending_payments, get_pending_orders, set_order_status

BASE = Path(__file__).parent

def load_products():
    p = BASE / "products.json"
    return json.loads(p.read_text(encoding="utf-8"))

def get_products():
    return load_products()

# create order wrapper
def create_order_backend(payload):
    # payload: {user_id, user_nick, product_code, amount}
    user_id = payload.get("user_id")
    item_code = payload.get("product_code")
    # find type and price from products.json
    for p in get_products():
        if p['code'] == item_code:
            item_type = p['type']
            price = p['price']
            break
    else:
        return False, None
    order_id = create_order(user_id, item_type, item_code, payload.get("user_nick",""), price)
    return True, {"id": order_id}

# payments
def create_payment_backend(tg_id, amount):
    return create_payment(tg_id, amount)

def confirm_payment_backend(payment_id):
    # mark payment as approved and add money
    # caller should call add_balance separately after verification
    set_payment_status(payment_id, "approved")
    return True

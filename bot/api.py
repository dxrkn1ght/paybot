import requests
from config import API_BASE

def get_products():
    try:
        r = requests.get(API_BASE + "products/")
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return []

def create_order(data):
    r = requests.post(API_BASE + "payments/orders/", json=data)
    return r.status_code == 201, r.json() if r.content else None

def create_payment(data, files=None):
    r = requests.post(API_BASE + "payments/create-payment/", data=data, files=files)
    return r.status_code == 201, r.json() if r.content else None

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('8317966549:AAEIb0v6tnLMjkb5wc7Iw-XscOJg8mj9wEM', '')
OWNER_CHAT_ID = int(os.getenv('993523630', 0))
API_BASE = os.getenv('API_BASE', 'http://127.0.0.1:8000/api/')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', '@mr1kevin')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip().isdigit()]
COIN_PRICE = int(os.getenv('COIN_PRICE', '1000'))


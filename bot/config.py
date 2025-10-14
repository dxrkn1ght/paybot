import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN','')
API_BASE = os.getenv('API_BASE','http://127.0.0.1:8000/api/')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME','@mr1kevin')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS','').split(',') if x.strip().isdigit()]
COIN_PRICE = int(os.getenv('COIN_PRICE','1000'))

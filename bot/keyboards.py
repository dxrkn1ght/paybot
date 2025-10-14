from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
def lang_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('🇺🇿 O\'zbek', callback_data='lang_uz')],[InlineKeyboardButton('🇷🇺 Русский', callback_data='lang_ru')]])
def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('🛍 Mahsulotlar', callback_data='menu_products')],[InlineKeyboardButton('💳 To\'lov', callback_data='menu_topup')],[InlineKeyboardButton('📦 Buyurtmalar', callback_data='menu_orders')],[InlineKeyboardButton('💰 Balans', callback_data='menu_balance')],[InlineKeyboardButton('🆘 Yordam', callback_data='menu_help')]])
def products_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('🪙 Coin', callback_data='prod_coin')],[InlineKeyboardButton('🏷 Rank', callback_data='prod_rank')],[InlineKeyboardButton('🔙 Orqaga', callback_data='back_main')]])
def rank_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('VIP — 15 000', callback_data='rank_vip')],[InlineKeyboardButton('GOD — 17 000', callback_data='rank_god')],[InlineKeyboardButton('ULTIMATE — 20 000', callback_data='rank_ultimate')],[InlineKeyboardButton('🔙 Orqaga', callback_data='back_products')]])
def coin_confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('✅ Tasdiqlash', callback_data='confirm_coin')],[InlineKeyboardButton('❌ Bekor', callback_data='cancel')]])
def admin_kb(payment_id):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('✅ Tasdiqlash', callback_data=f'admin_approve:{payment_id}'), InlineKeyboardButton('❌ Rad etish', callback_data=f'admin_reject:{payment_id}')]])

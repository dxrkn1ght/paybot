from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from states import BuyStates
from keyboards import products_type_kb, products_inline
from api import get_products, create_order_backend
from db import get_balance, create_order, add_balance
from config import OWNER_CHAT_ID

router = Router()

@router.message(F.text == "🎒 Mahsulotlar")
async def show_products(message: Message):
    await message.answer("Qaysi turdagi mahsulotni ko‘rmoqchisiz?", reply_markup=products_type_kb())

@router.callback_query(F.data == "type_coin")
async def type_coin(call: CallbackQuery):
    await call.answer()
    prods = [p for p in get_products() if p['type'] == 'coin']
    if not prods:
        await call.message.answer("❌ Coinlar topilmadi.")
        return
    await call.message.answer("💰 Quyidagi coin turlaridan birini tanlang:", reply_markup=products_inline(prods))

@router.callback_query(F.data == "type_rank")
async def type_rank(call: CallbackQuery):
    await call.answer()
    prods = [p for p in get_products() if p['type'] == 'rank']
    if not prods:
        await call.message.answer("❌ Ranklar topilmadi.")
        return
    await call.message.answer("🏆 Quyidagi rank turlaridan birini tanlang:", reply_markup=products_inline(prods))

@router.callback_query(F.data.startswith("buy_"))
async def buy_product(call: CallbackQuery, state: FSMContext):
    await call.answer()
    code = call.data.split("buy_", 1)[1]
    prods = get_products()
    prod = next((p for p in prods if p['code'] == code), None)
    if not prod:
        await call.message.answer("❌ Mahsulot topilmadi.")
        return

    user_balance = get_balance(call.from_user.id)
    if user_balance < prod['price']:
        await call.message.answer("❌ Hisobingizda yetarli mablag‘ yo‘q. Iltimos, hisobni to‘ldiring.")
        return

    # Balansni kamaytirish va buyurtma yaratish
    add_balance(call.from_user.id, -prod['price'])
    create_order(call.from_user.id, prod['type'], prod['code'], f"{prod['name']} uchun buyurtma", prod['price'])

    await call.message.answer(
        f"✅ Buyurtma yaratildi!\n"
        f"🧾 Mahsulot: {prod['name']}\n"
        f"💰 Narxi: {prod['price']:,} so‘m\n\n"
        f"🕐 Admin buyurtmangizni tasdiqlaydi."
    )

    try:
        await router.bot.send_message(
            OWNER_CHAT_ID,
            f"📦 Yangi buyurtma!\n👤 User ID: {call.from_user.id}\n🛍 Mahsulot: {prod['name']}\n💰 {prod['price']:,} so‘m"
        )
    except Exception as e:
        print(f"⚠️ Admin ogohlantirish xatosi: {e}")

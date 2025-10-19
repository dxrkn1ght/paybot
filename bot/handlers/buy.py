from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from db import get_products, get_product_by_code, get_user_balance, update_balance, create_order
from keyboards import products_type_kb, products_inline
from config import OWNER_CHAT_ID

router = Router()

@router.message(F.text == "🎒 Mahsulotlar")
async def cmd_products(message: types.Message):
    # user lang not strictly necessary here; default inline labels include emoji
    await message.answer("Qaysi turdagi mahsulotni ko‘rmoqchisiz?", reply_markup=products_type_kb())

@router.callback_query(F.data == "type_coin")
async def show_coins(call: types.CallbackQuery):
    await call.answer()
    prods = get_products("coin")
    if not prods:
        await call.message.answer("❌ Coinlar topilmadi.")
        return
    await call.message.answer("💰 Quyidagi coin turlaridan birini tanlang:", reply_markup=products_inline(prods))

@router.callback_query(F.data == "type_rank")
async def show_ranks(call: types.CallbackQuery):
    await call.answer()
    prods = get_products("rank")
    if not prods:
        await call.message.answer("❌ Ranklar topilmadi.")
        return
    await call.message.answer("🏆 Quyidagi rank turlaridan birini tanlang:", reply_markup=products_inline(prods))

@router.callback_query(F.data.startswith("buy_"))
async def buy_product(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    code = call.data.split("buy_",1)[1]
    prod = get_product_by_code(code)
    if not prod:
        await call.message.answer("❌ Mahsulot topilmadi.")
        return

    bal = get_user_balance(call.from_user.id)
    if bal < prod["price"]:
        await call.message.answer("❌ Hisobingizda yetarli mablag‘ yo‘q. Iltimos, hisobni to‘ldiring.")
        return

    # here we could ask for extra details (nick) — for simplicity ask and store via FSM
    await state.update_data(selected_product=prod)
    await state.set_state("waiting_nick")
    await call.message.answer("Iltimos, Minecraft nickingizni kiriting:")

@router.message(F.state == "waiting_nick")
async def accept_nick(message: types.Message, state: FSMContext):
    data = await state.get_data()
    prod = data.get("selected_product")
    if not prod:
        await message.answer("Xatolik — mahsulot topilmadi.")
        await state.clear()
        return

    nick = message.text.strip()
    bal = get_user_balance(message.from_user.id)
    if bal < prod["price"]:
        await message.answer("❌ Sizning balansingiz yetarli emas.")
        await state.clear()
        return

    # subtract balance and create order
    update_balance(message.from_user.id, bal - prod["price"])
    order_id = create_order(message.from_user.id, prod["type"], prod["code"], f"Nick: {nick}", prod["price"])

    await message.answer(
        f"✅ Buyurtma yaratildi!\n🧾 Mahsulot: {prod['name']}\n💰 Narxi: {prod['price']:,} so‘m\n\n🕐 Admin buyurtmangizni tasdiqlaydi."
    )

    # notify owner/admin
    try:
        await router.bot.send_message(
            OWNER_CHAT_ID,
            f"📦 Yangi buyurtma!\n👤 User ID: {message.from_user.id}\nNick: {nick}\n🛍 Mahsulot: {prod['name']}\n💰 {prod['price']:,} so‘m\nOrder ID: {order_id}"
        )
    except Exception:
        pass

    await state.clear()

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from db import get_user_balance, create_order, get_product
from keyboards import products_type_kb, products_inline, confirm_admin_kb
from config import ADMINS

router = Router()


class OrderStates(StatesGroup):
    choosing_type = State()  # Coin yoki Rank tanlash
    choosing_product = State()  # Mahsulotni tanlash
    waiting_nick = State()  # Minecraft nickini so‘rash


# --- Coin yoki Rank turini tanlash ---
@router.callback_query(lambda c: c.data in ["type_coin", "type_rank"])
async def choose_type(call: types.CallbackQuery, state: FSMContext):
    type_ = "coin" if call.data == "type_coin" else "rank"
    await state.update_data(type=type_)

    # Mahsulotlar ro'yxatini olish (DB yoki JSON fayl orqali)
    products = get_product(type_)  # get_product(type_) → list of dict
    await state.update_data(products=products)

    kb = products_inline(products)
    await call.message.edit_text("Mahsulotni tanlang:", reply_markup=kb)
    await state.set_state(OrderStates.choosing_product)


# --- Mahsulotni tanlash ---
@router.callback_query(lambda c: c.data.startswith("buy_"))
async def choose_product(call: types.CallbackQuery, state: FSMContext):
    product_code = call.data[4:]
    data = await state.get_data()
    products = data.get("products", [])
    product = next((p for p in products if p["code"] == product_code), None)

    if not product:
        await call.answer("Mahsulot topilmadi!")
        return

    user_balance = get_user_balance(call.from_user.id)
    if user_balance < product["price"]:
        await call.message.answer(f"💸 Sizning balansingiz yetarli emas! Sizda {user_balance:,} so‘m bor.")
        await state.clear()
        return

    await state.update_data(selected_product=product)
    await call.message.answer("Iltimos, Minecraft nickingizni kiriting:")
    await state.set_state(OrderStates.waiting_nick)


# --- Nickni olish va admin notify ---
@router.message(OrderStates.waiting_nick)
async def get_nick(message: types.Message, state: FSMContext):
    nick = message.text
    data = await state.get_data()
    product = data.get("selected_product")

    # Buyurtmani yaratish
    order_id = create_order(user_id=message.from_user.id, product=product, nick=nick)
    await state.update_data(order_id=order_id)

    # Adminlarga xabar yuborish
    for admin_id in ADMINS:
        await message.bot.send_message(
            chat_id=admin_id,
            text=f"🔔 New order\nUser: {message.from_user.id}\nNick: {nick}\n"
                 f"Product: {product['name']} — {product['price']:,} so'm\nOrder ID: {order_id}",
            reply_markup=confirm_admin_kb(order_id, type_="order")
        )

    await message.answer("✅ Buyurtmangiz adminga yuborildi. Tasdiqlashni kuting.")
    await state.clear()

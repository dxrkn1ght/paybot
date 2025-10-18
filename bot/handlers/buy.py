from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from states import BuyStates
from keyboards import products_type_kb, products_inline, main_menu
from api import get_products, create_order_backend
from db import get_or_create_user
from config import OWNER_CHAT_ID

router = Router()


# --- Mahsulotlar bo‘limi ---
@router.message(F.text == "🎒 Mahsulotlar")
async def show_products(message: Message):
    await message.answer(
        "Qaysi turdagi mahsulotni ko‘rmoqchisiz?",
        reply_markup=products_type_kb()
    )


# --- Coinlar ---
@router.callback_query(F.data == "type_coin")
async def type_coin(call: CallbackQuery):
    await call.answer()
    prods = [p for p in get_products() if p['type'] == 'coin']
    if not prods:
        await call.message.answer("❌ Coinlar topilmadi.")
        return
    await call.message.answer("💰 Quyidagi coin turlaridan birini tanlang:", reply_markup=products_inline(prods))


# --- Ranklar ---
@router.callback_query(F.data == "type_rank")
async def type_rank(call: CallbackQuery):
    await call.answer()
    prods = [p for p in get_products() if p['type'] == 'rank']
    if not prods:
        await call.message.answer("❌ Ranklar topilmadi.")
        return
    await call.message.answer("🏆 Quyidagi rank turlaridan birini tanlang:", reply_markup=products_inline(prods))


# --- Buyurtma jarayoni ---
@router.callback_query(F.data.startswith("buy_"))
async def buy_product(call: CallbackQuery, state: FSMContext):
    await call.answer()
    code = call.data.split("buy_", 1)[1]
    prods = get_products()
    prod = next((p for p in prods if p['code'] == code), None)

    if not prod:
        await call.message.answer("❌ Mahsulot topilmadi.")
        return

    await state.update_data(selected_product=prod)
    await call.message.answer(
        f"✅ Siz *{prod['name']}* — *{prod['price']:,} so‘m* ni tanladingiz.\n\n"
        "Iltimos, serverdagi *nick* ingizni yuboring:",
        parse_mode="Markdown"
    )
    await state.set_state(BuyStates.waiting_nick)


# --- Nick qabul qilish va buyurtma yaratish ---
@router.message(BuyStates.waiting_nick)
async def ask_nick(message: Message, state: FSMContext):
    nick = message.text.strip()
    data = await state.get_data()
    prod = data.get("selected_product")

    if not prod:
        await message.answer("❌ Xatolik: mahsulot tanlanmagan.")
        await state.clear()
        return

    order_payload = {
        "user_id": message.from_user.id,
        "user_nick": nick,
        "product_code": prod['code'],
        "amount": prod['price']
    }

    ok, res = create_order_backend(order_payload)

    if ok:
        await message.answer(
            "✅ Buyurtma yaratildi!\n\n"
            "💳 Endi to‘lovni amalga oshiring va to‘lov skrinshotini yuboring.\n"
            "🕐 Admin sizning to‘lovni tekshiradi."
        )

        try:
            order_id = res.get("id") if res else "n/a"
            await router.bot.send_message(
                OWNER_CHAT_ID,
                f"📦 *Yangi buyurtma!*\n"
                f"👤 User ID: `{message.from_user.id}`\n"
                f"🛍 Mahsulot: *{prod['name']}* ({prod['price']:,} so‘m)\n"
                f"🎮 Nick: `{nick}`\n"
                f"🆔 Order ID: {order_id}",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"⚠️ Adminni ogohlantirishda xatolik: {e}")
    else:
        await message.answer("❌ Buyurtma yaratishda xatolik yuz berdi.")

    await state.clear()


# --- Hisobni to‘ldirish ---
@router.message(F.text == "💳 Hisobni to'ldirish")
async def topup_balance(message: Message):
    text = (
        "💳 Hisobni to‘ldirish uchun quyidagi kartalardan biriga to‘lov yuboring:\n\n"
        "💠 *UZCARD:* 8600 1234 5678 9012\n"
        "💠 *HUMO:* 9860 0001 2345 6789\n\n"
        "To‘lovni amalga oshirgach, *skrinshotni* yuboring.\n"
        "Admin uni tekshirib, balansingizni to‘ldiradi."
    )
    await message.answer(text, parse_mode="Markdown")

from aiogram import Router, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from states import BuyStates
from keyboards import product_types_kb, products_inline
from api import get_products, create_order
from config import OWNER_CHAT_ID

router = Router()

# --- Mahsulotlar bo‘limi ---
@router.message(F.text == "🎒 Mahsulotlar")
async def show_products(message: Message):
    await message.answer(
        "Qaysi turdagi mahsulotni ko‘rmoqchisiz?",
        reply_markup=product_types_kb
    )


# --- Coinlar ---
@router.callback_query(F.data == "type_coin")
async def type_coin(call: CallbackQuery):
    await call.message.answer("💰 Coin:")
    prods = [p for p in get_products() if p['type'] == 'coin']
    await call.message.answer(
        "Tanlang:",
        reply_markup=products_inline(prods)
    )


# --- Ranklar ---
@router.callback_query(F.data == "type_rank")
async def type_rank(call: CallbackQuery):
    await call.message.answer("🏆 Rank:")
    prods = [p for p in get_products() if p['type'] == 'rank']
    await call.message.answer(
        "Tanlang:",
        reply_markup=products_inline(prods)
    )


# --- Buyurtma boshlangan payt ---
@router.callback_query(F.data.startswith("buy_"))
async def buy_product(call: CallbackQuery, state: FSMContext):
    code = call.data.split("buy_", 1)[1]
    prods = get_products()
    prod = next((p for p in prods if p['code'] == code), None)

    if not prod:
        await call.message.answer("❌ Mahsulot topilmadi.")
        return

    await state.update_data(selected_product=prod)
    await call.message.answer(
        f"✅ Siz {prod['name']} ({prod['price']} so‘m) ni tanladingiz.\n"
        "Iltimos, serverdagi nickingizni kiriting:"
    )
    await state.set_state(BuyStates.waiting_nick)


# --- Nick kiritilgandan so‘ng ---
@router.message(BuyStates.waiting_nick)
async def ask_nick(message: Message, state: FSMContext):
    nick = message.text.strip()
    data = await state.get_data()
    prod = data.get("selected_product")

    if not prod:
        await message.answer("❌ Xatolik: mahsulot tanlanmagan.")
        await state.clear()
        return

    # Backendda buyurtma yaratish
    order_payload = {
        "user_id": message.from_user.id,
        "user_nick": nick,
        "product_code": prod['code'],
        "amount": prod['price']
    }

    ok, res = create_order(order_payload)

    if ok:
        await message.answer(
            "✅ Buyurtma yaratildi.\n"
            "To‘lovni amalga oshiring va tasdiqlovchi skrinshotni yuboring.\n"
            "Admin sizning to‘lovni tekshiradi."
        )

        # Adminni xabardor qilish
        try:
            await router.bot.send_message(
                OWNER_CHAT_ID,
                f"📦 Yangi buyurtma:\n"
                f"👤 User ID: {message.from_user.id}\n"
                f"🛍 Mahsulot: {prod['name']} ({prod['price']} so‘m)\n"
                f"🎮 Nick: {nick}\n"
                f"🆔 OrderID (backend): {res.get('id') if res else 'n/a'}"
            )
        except Exception as e:
            print(f"⚠️ Adminni ogohlantirishda xatolik: {e}")
    else:
        await message.answer("❌ Buyurtma yaratishda xatolik yuz berdi.")

    await state.clear()

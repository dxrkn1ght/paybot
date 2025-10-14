from aiogram import Router, types, F
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from states import BuyStates
from keyboards import product_types_kb, products_inline
from api import get_products, create_order
from config import OWNER_CHAT_ID

router = Router()

@router.message(Text("🎒 Mahsulotlar"))
async def products_menu(message: types.Message):
    await message.answer("Qaysi turdagi mahsulotni ko'rmoqchisiz?", reply_markup=product_types_kb)

@router.callback_query(F.data == "type_coin")
async def type_coin(call: types.CallbackQuery):
    await call.message.answer("Coinlar ro'yxati:")
    prods = [p for p in get_products() if p['type']=='coin']
    await call.message.answer("Tanlang:", reply_markup=products_inline(prods))

@router.callback_query(F.data == "type_rank")
async def type_rank(call: types.CallbackQuery):
    await call.message.answer("Ranklar ro'yxati:")
    prods = [p for p in get_products() if p['type']=='rank']
    await call.message.answer("Tanlang:", reply_markup=products_inline(prods))

@router.callback_query(F.data.startswith("buy_"))
async def buy_product(call: types.CallbackQuery, state: FSMContext):
    code = call.data.split("buy_",1)[1]
    prods = get_products()
    prod = next((p for p in prods if p['code']==code), None)
    if not prod:
        await call.message.answer("Mahsulot topilmadi.")
        return
    await state.update_data(selected_product=prod)
    await call.message.answer(f"✅ Siz {prod['name']} ({prod['price']} so'm) ni tanladingiz.\nIltimos serverdagi nickingizni kiriting:")
    await state.set_state(BuyStates.waiting_nick)

@router.message(BuyStates.waiting_nick)
async def ask_nick(message: types.Message, state: FSMContext):
    nick = message.text.strip()
    data = await state.get_data()
    prod = data.get("selected_product")
    # create order record on backend
    order_payload = {"user_id": message.from_user.id, "user_nick": nick, "product_code": prod['code'], "amount": prod['price']}
    ok, res = create_order(order_payload)
    if ok:
        await message.answer("Buyurtma yaratilidi. To'lovni amalga oshiring va to'lovni tasdiqlovchi skrinshot yuboring.\nAdmin sizning to'lovni tekshiradi.")
        # notify admin in Telegram (by OWNER_CHAT_ID)
        try:
            await router.bot.send_message(OWNER_CHAT_ID, f"Yangi buyurtma: user {message.from_user.id}\nProduct: {prod['name']} {prod['price']} so'm\nNick: {nick}\nOrderID backend: {res.get('id') if res else 'n/a'}")
        except Exception:
            pass
    else:
        await message.answer("Xatolik! Buyurtma yaratishda muammo bo'ldi.")
    await state.clear()

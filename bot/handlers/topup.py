from aiogram import Router, types, F
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from states import TopUpStates
from api import create_payment
from config import OWNER_CHAT_ID

router = Router()

@router.message(Text("💳 Hisobni to'ldirish"))
async def topup_start(message: types.Message, state: FSMContext):
    await message.answer("To'ldirmoqchi bo'lgan summani kiriting (min 10000, max 1000000):")
    await state.set_state(TopUpStates.entering_amount)

@router.message(TopUpStates.entering_amount)
async def topup_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.replace(" ", ""))
    except:
        await message.answer("Iltimos faqat raqam kiriting.")
        return
    if amount < 10000 or amount > 1000000:
        await message.answer("Summa chegaradan tashqarida. 10000 - 1000000 so'm oralig'ida kiriting.")
        return
    await state.update_data(amount=amount)
    await message.answer("Iltimos to'lov uchun karta yoki hisob ma'lumotlarini kiriting (yoki qoldiring default), so'ngra to'lov skrinshotini yuboring.")
    await state.set_state(TopUpStates.waiting_screenshot)

@router.message(TopUpStates.waiting_screenshot, F.photo)
async def topup_screenshot(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("amount")
    # get file
    photo = message.photo[-1]
    file = await photo.download(destination=bytes)  # get bytes
    files = {"screenshot": ("screenshot.jpg", file)}
    # create a temporary order to attach payment? here use create_payment API requiring order id; but our backend expects order foreign key.
    # For simplicity we will create a payment with order id = 0 (admin will match)
    payload = {"order": 0, "sender_account": f"tg:{message.from_user.id}", "amount": amount}
    ok, res = create_payment(payload, files=files)
    if ok:
        await message.answer("Skrinshot qabul qilindi. Admin tasdiqlashini kuting.")
        try:
            await router.bot.send_message(OWNER_CHAT_ID, f"Yangi to'lov skrinshoti: user {message.from_user.id}, amount {amount} so'm")
        except Exception:
            pass
    else:
        await message.answer("Xatolik! To'lovni yuborishda muammo.")
    await state.clear()

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from states import TopUpStates
from api import create_payment  # sizning API funksiyangiz bo'lsa ishlaydi
from config import OWNER_CHAT_ID
import io

router = Router()

@router.message(lambda m: m.text == "💳 Hisobni to'ldirish")
async def topup_start(message: types.Message, state: FSMContext):
    await message.answer("To'ldirmoqchi bo'lgan summani kiriting (min 10000, max 1000000):")
    await state.set_state(TopUpStates.entering_amount)

@router.message(TopUpStates.entering_amount)
async def topup_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.replace(" ", ""))
    except ValueError:
        await message.answer("Iltimos faqat raqam kiriting.")
        return

    if amount < 10000 or amount > 1000000:
        await message.answer("Summa chegaradan tashqarida.")
        return

    await state.update_data(amount=amount)
    await message.answer("To'lov skrinshotini yuboring.")
    await state.set_state(TopUpStates.waiting_screenshot)

@router.message(TopUpStates.waiting_screenshot, F.photo)
async def topup_screenshot(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("amount")
    photo = message.photo[-1]

    file = io.BytesIO()
    await photo.download(destination=file)
    file.seek(0)

    files = {"screenshot": ("screenshot.jpg", file)}

    payload = {
        "order": 0,
        "sender_account": f"tg:{message.from_user.id}",
        "amount": amount
    }

    ok, res = create_payment(payload, files=files)  # sizning API funksiyangiz

    if ok:
        await message.answer("Skrinshot qabul qilindi. Admin tasdiqlashini kuting.")
        # **To'g'ri usul**: message.bot.send_message
        try:
            if OWNER_CHAT_ID and OWNER_CHAT_ID != 0:
                await message.bot.send_message(
                    OWNER_CHAT_ID,
                    f"Yangi to'lov skrinshoti:\nUser ID: {message.from_user.id}\nAmount: {amount} so'm"
                )
        except Exception as e:
            # adminga yuborolmasa - logga yozing
            await message.answer("⚠️ Adminga xabar yuborishda muammo yuz berdi.")
            import logging
            logging.exception("Adminga yuborishda xato:")

    else:
        await message.answer("Xatolik! To'lovni yuborishda muammo.")

    await state.clear()

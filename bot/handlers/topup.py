from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType
from states import TopUpStates
from keyboards import main_menu
from db import get_or_create_user, create_payment, set_payment_screenshot, add_balance
from config import ADMIN_CARD, OWNER_CHAT_ID

router = Router()

@router.message(F.text == "💳 Hisobni to'ldirish")
async def start_topup(message: Message):
    await message.answer("Hisobni to'ldirmoqchi bo'lgan summani kiriting (min 10000, max 1000000):")
    await TopUpStates.waiting_amount.set()

@router.message(TopUpStates.entering_amount)
async def received_amount(message: Message, state: FSMContext):
    try:
        amt = int(message.text.strip())
    except Exception:
        await message.answer("Faqat son kiriting (misol: 10000).")
        return
    if amt < 10000 or amt > 1000000:
        await message.answer("Summani tekshiring: min 10000, max 1000000.")
        return
    # create payment record
    pid = create_payment(message.from_user.id, amt)
    await state.update_data(payment_id=pid, amount=amt)
    # show payment card info
    await message.answer(f"To'lovni quyidagi karta orqali qiling:\n{ADMIN_CARD}\n\nTo'lov qilgandan so'ng, tasdiqlash uchun skrinshot yuboring (rasm yoki fayl).")
    await TopUpStates.waiting_screenshot.set()

@router.message(TopUpStates.waiting_screenshot, F.content_type.in_([ContentType.PHOTO, ContentType.DOCUMENT]))
async def receive_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    pid = data.get("payment_id")
    if not pid:
        await message.answer("To'lov topilmadi, boshqatdan urinib ko'ring.")
        await state.clear()
        return
    # get file_id (photo or document)
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer("Iltimos rasm yoki fayl yuboring.")
        return
    set_payment_screenshot(pid, file_id)
    await message.answer("Skrinshot qabul qilindi. Admin sizning to'lovingizni tekshiradi va tasdiqlaydi.")
    # notify admin
    try:
        await router.bot.send_message(OWNER_CHAT_ID, f"📥 New payment #{pid}\nUser: {message.from_user.id}\nAmount: {data.get('amount')} so'm")
        await router.bot.send_photo(OWNER_CHAT_ID, file_id, caption=f"Payment #{pid} by {message.from_user.id}")
    except Exception:
        pass
    await state.clear()

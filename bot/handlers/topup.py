from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType
from states import TopUpStates
from db import create_payment, set_payment_screenshot
from config import ADMIN_CARD, OWNER_CHAT_ID

router = Router()

@router.message(F.text == "💳 Hisobni to'ldirish")
async def start_topup(message: Message, state: FSMContext):
    await message.answer("💰 Hisobni to‘ldirmoqchi bo‘lgan summani kiriting (min 10000, max 1000000):")
    await state.set_state(TopUpStates.entering_amount)

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

    pid = create_payment(message.from_user.id, amt)
    await state.update_data(payment_id=pid, amount=amt)
    await message.answer(
        f"To‘lovni quyidagi karta orqali qiling:\n\n💳 {ADMIN_CARD}\n\n"
        "To‘lov qilgach, tasdiqlash uchun *skrinshot* yuboring (rasm yoki fayl).",
        parse_mode="Markdown"
    )
    await state.set_state(TopUpStates.waiting_screenshot)

@router.message(TopUpStates.waiting_screenshot, F.content_type.in_([ContentType.PHOTO, ContentType.DOCUMENT]))
async def receive_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    pid = data.get("payment_id")
    amt = data.get("amount")

    if not pid:
        await message.answer("Xatolik: to‘lov topilmadi, qaytadan urinib ko‘ring.")
        await state.clear()
        return

    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    set_payment_screenshot(pid, file_id)
    await message.answer("✅ Skrinshot qabul qilindi. Admin sizning to‘lovingizni tekshiradi.")
    try:
        await router.bot.send_message(
            OWNER_CHAT_ID,
            f"📥 Yangi to‘lov #{pid}\n👤 User: {message.from_user.id}\n💰 Miqdor: {amt:,} so‘m"
        )
        await router.bot.send_photo(OWNER_CHAT_ID, file_id, caption=f"To‘lov #{pid}")
    except Exception as e:
        print(f"⚠️ Admin notify error: {e}")

    await state.clear()

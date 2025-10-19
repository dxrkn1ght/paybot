from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db import get_or_create_user, set_user_lang, create_payment, set_payment_screenshot, get_setting
from keyboards import choose_language_kb, main_menu, confirm_admin_kb
from config import ADMINS

router = Router()

class TopUpStates(StatesGroup):
    waiting_amount = State()
    waiting_screenshot = State()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    get_or_create_user(message.from_user.id)
    await message.answer("Xush kelibsiz! Tilni tanlang:", reply_markup=choose_language_kb())

@router.message(F.text.in_(["🇺🇿 O‘zbekcha", "🇷🇺 Русский"]))
async def choose_language(message: types.Message, state: FSMContext):
    lang = "uz" if message.text == "🇺🇿 O‘zbekcha" else "ru"
    set_user_lang(message.from_user.id, lang)
    await state.update_data(lang=lang)
    await message.answer("Asosiy menyu:", reply_markup=main_menu(lang))

# Show balance
@router.message(F.text == "💰 Mening balansim")
async def show_balance(message: types.Message):
    from db import get_user_balance
    bal = get_user_balance(message.from_user.id)
    await message.answer(f"💰 Sizning balansingiz: {bal:,} so'm")

# Topup start
@router.message(F.text == "💳 Hisobni to'ldirish")
async def topup_start(message: types.Message, state: FSMContext):
    lang = get_setting("lang_default") or "uz"
    min_sum = int(get_setting("topup_min", "10000"))
    max_sum = int(get_setting("topup_max", "1000000"))
    await state.update_data(lang=lang, min_sum=min_sum, max_sum=max_sum)
    await state.set_state(TopUpStates.waiting_amount)
    await message.answer(f"Iltimos, summani so‘mda kiriting (min {min_sum:,}, max {max_sum:,}):")

@router.message(TopUpStates.waiting_amount)
async def topup_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        amount = int(message.text.strip())
    except Exception:
        await message.answer("Noto‘g‘ri format — iltimos faqat raqam kiriting.")
        return

    min_sum = data.get("min_sum")
    max_sum = data.get("max_sum")
    if amount < min_sum or amount > max_sum:
        await message.answer(f"Summani tekshiring: min {min_sum:,}, max {max_sum:,}.")
        return

    pid = create_payment(message.from_user.id, amount)
    await state.update_data(pid=pid, amount=amount)
    await state.set_state(TopUpStates.waiting_screenshot)

    admin_card = get_setting("admin_card", "9860 1234 5678 9012")
    await message.answer(
        f"To‘lovni quyidagi karta orqali qiling:\n\n💳 <code>{admin_card}</code>\n\nTo‘lov qilgach, skrinshot yuboring."
    )

@router.message(TopUpStates.waiting_screenshot, F.content_type.in_(["photo","document"]))
async def topup_screenshot(message: types.Message, state: FSMContext):
    data = await state.get_data()
    pid = data.get("pid")
    amount = data.get("amount")

    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer("Iltimos, kvitansiyaning suratini yoki faylini yuboring.")
        return

    set_payment_screenshot(pid, file_id)

    # notify admins
    for admin_id in ADMINS:
        try:
            await message.bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=f"🔔 New top-up\nUser: {message.from_user.id}\nAmount: {amount:,} so'm\nPayment ID: {pid}",
                reply_markup=confirm_admin_kb(pid, type_="topup")
            )
        except Exception:
            pass

    await message.answer("So‘rovingiz adminga yuborildi. Tasdiqlashni kuting.")
    await state.clear()

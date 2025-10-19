from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import ADMINS, OWNER_CHAT_ID

router = Router()

# FSM state'lar
class TopUpState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_receipt = State()


# Asosiy menyu
def main_menu(lang="uz"):
    if lang == "ru":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="💳 Пополнить баланс")],
                [KeyboardButton(text="🔙 Назад")]
            ],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="💳 Hisobni to‘ldirish")],
                [KeyboardButton(text="🔙 Ortga")]
            ],
            resize_keyboard=True
        )


# /topup yoki knopka bosilganda
@router.message(F.text.in_(["💳 Hisobni to‘ldirish", "💳 Пополнить баланс"]))
async def start_topup(message: types.Message, state: FSMContext):
    lang = "ru" if "Пополнить" in message.text else "uz"
    min_sum = 5000
    max_sum = 1_000_000

    if lang == "ru":
        text = (
            "💳 <b>Пополнение баланса</b>\n\n"
            "Реквизиты для оплаты:\n"
            "<code>9860 1234 5678 9012</code>\n\n"
            f"✅ Минимальная сумма: <b>{min_sum:,} сум</b>\n"
            f"🚫 Максимальная сумма: <b>{max_sum:,} сум</b>\n\n"
            "Введите сумму для пополнения:"
        )
    else:
        text = (
            "💳 <b>Hisobni to‘ldirish</b>\n\n"
            "To‘lov uchun admin karta raqami:\n"
            "<code>9860 1234 5678 9012</code>\n\n"
            f"✅ Minimal summa: <b>{min_sum:,} so‘m</b>\n"
            f"🚫 Maksimal summa: <b>{max_sum:,} so‘m</b>\n\n"
            "Iltimos, to‘ldirmoqchi bo‘lgan summani kiriting:"
        )

    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(TopUpState.waiting_for_amount)
    await state.update_data(lang=lang, min_sum=min_sum, max_sum=max_sum)


# Summani qabul qilish
@router.message(TopUpState.waiting_for_amount, F.text)
async def process_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    min_sum = data.get("min_sum")
    max_sum = data.get("max_sum")

    try:
        amount = int(message.text)
    except ValueError:
        msg = "❌ Faqat raqam kiriting (masalan: 15000)." if lang == "uz" else "❌ Введите только число (например: 15000)."
        await message.answer(msg)
        return

    if amount < min_sum:
        msg = f"⚠️ Minimal to‘lov miqdori {min_sum:,} so‘m." if lang == "uz" else f"⚠️ Минимальная сумма {min_sum:,} сум."
        await message.answer(msg)
        return
    elif amount > max_sum:
        msg = f"⚠️ Maksimal to‘lov miqdori {max_sum:,} so‘m." if lang == "uz" else f"⚠️ Максимальная сумма {max_sum:,} сум."
        await message.answer(msg)
        return

    await state.update_data(amount=amount)
    msg = (
        "📎 Endi to‘lov kvitansiyasini (rasm yoki skrinshot) yuboring.\nTo‘lov admin kartasiga amalga oshirilgan bo‘lishi kerak."
        if lang == "uz"
        else "📎 Теперь отправьте квитанцию (скриншот или фото).\nОплата должна быть выполнена на карту администратора."
    )
    await message.answer(msg)
    await state.set_state(TopUpState.waiting_for_receipt)


# Kvitansiya yuborilganda
@router.message(TopUpState.waiting_for_receipt, F.photo)
async def process_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("amount")
    lang = data.get("lang", "uz")

    caption = (
        f"📥 <b>Yangi to‘lov so‘rovi!</b>\n\n"
        f"👤 Foydalanuvchi: @{message.from_user.username or 'Nomaʼlum'}\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n"
        f"💰 Summa: <b>{amount:,} so‘m</b>\n"
        f"⏳ Tasdiqlash kerak."
    )

    for admin_id in ADMINS + [OWNER_CHAT_ID]:
        try:
            await message.bot.send_photo(admin_id, message.photo[-1].file_id, caption=caption)
        except Exception:
            pass

    msg = (
        "✅ So‘rovingiz yuborildi. Admin tasdiqlaganidan so‘ng balansingiz to‘ldiriladi."
        if lang == "uz"
        else "✅ Запрос отправлен. Баланс будет пополнен после подтверждения администратором."
    )
    await message.answer(msg, reply_markup=main_menu(lang))
    await state.clear()


# Agar foydalanuvchi rasm o‘rniga matn yuborsa
@router.message(TopUpState.waiting_for_receipt)
async def wrong_receipt_type(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    msg = (
        "❌ Iltimos, to‘lov kvitansiyasining <b>rasmini</b> yuboring."
        if lang == "uz"
        else "❌ Отправьте, пожалуйста, <b>фото квитанции</b>."
    )
    await message.answer(msg)

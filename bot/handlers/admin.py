from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from db import (
    get_pending_payments, get_pending_orders,
    approve_topup as db_approve_topup, approve_order,
    set_payment_status, set_order_status,
    get_user_balance, update_balance,
    get_setting, set_setting,
)
from keyboards import admin_menu, confirm_admin_kb
from config import OWNER_CHAT_ID

router = Router()


# =====================
# STATES
# =====================
class EditBalance(StatesGroup):
    waiting_user_id = State()
    waiting_new_balance = State()


class EditSettings(StatesGroup):
    waiting_key = State()
    waiting_value = State()


# =====================
# ADMIN START
# =====================
@router.message(Command("admin"))
async def admin_start(message: types.Message):
    if message.from_user.id != OWNER_CHAT_ID:
        await message.answer("🚫 Siz admin emassiz!")
        return
    await message.answer("👑 Admin panelga xush kelibsiz!", reply_markup=admin_menu())


# =====================
# PENDING TOP-UPS
# =====================
@router.callback_query(F.data == "pending_topups")
async def pending_topups(call: types.CallbackQuery):
    tops = get_pending_payments()
    if not tops:
        await call.message.answer("✅ Hozircha tasdiqlanmagan to‘lovlar yo‘q.")
        return

    for t in tops:
        text = (
            f"💳 Top-up ID: {t['id']}\n"
            f"👤 User ID: {t['user_id']}\n"
            f"💰 Miqdor: {t['amount']} so'm\n"
            f"📸 Screenshot: {t['screenshot']}"
        )
        await call.message.answer(
            text,
            reply_markup=confirm_admin_kb(t['id'], type="topup")
        )


# =====================
# PENDING ORDERS
# =====================
@router.callback_query(F.data == "pending_orders")
async def pending_orders(call: types.CallbackQuery):
    orders = get_pending_orders()
    if not orders:
        await call.message.answer("✅ Hozircha kutayotgan buyurtmalar yo‘q.")
        return

    for o in orders:
        text = (
            f"🆔 Buyurtma ID: {o['id']}\n"
            f"👤 User ID: {o['user_id']}\n"
            f"🎮 Mahsulot: {o['item_code']}\n"
            f"💰 Narx: {o['price']} so'm"
        )
        await call.message.answer(
            text,
            reply_markup=confirm_admin_kb(o['id'], type="order")
        )


# =====================
# ADMIN ACTIONS (approve/decline)
# =====================
@router.callback_query(lambda c: c.data and c.data.startswith("admin:"))
async def admin_actions(callback: types.CallbackQuery):
    if callback.from_user.id != OWNER_CHAT_ID:
        await callback.answer("Siz bu amalni bajara olmaysiz.", show_alert=True)
        return

    parts = callback.data.split(":")
    # expected format: admin:approve|decline:type:id
    if len(parts) < 4:
        await callback.message.answer("Xatolik: noto'g'ri callback.")
        return

    action = parts[1]
    type_ = parts[2]
    pid = int(parts[3])

    # ========== TOP-UP ==========
    if type_ == "topup":
        if action == "approve":
            topup = db_approve_topup(pid)  # db funksiyani chaqiramiz
            if not topup:
                await callback.answer("Top-up topilmadi!", show_alert=True)
                return

            user_id = topup["user_id"]
            amount = topup["amount"]

            # ✅ Userga xabar yuboramiz
            try:
                await callback.bot.send_message(
                    user_id,
                    f"✅ Sizning {amount} so'm miqdoridagi to‘lovingiz "
                    f"admin tomonidan tasdiqlandi!\n💰 Balansingizni tekshiring."
                )
            except Exception as e:
                print(f"⚠️ Foydalanuvchiga xabar yuborilmadi: {e}")

            await callback.message.answer(f"💰 Top-up ID {pid} tasdiqlandi!")

        else:
            set_payment_status(pid, "declined")
            await callback.message.answer(f"💰 Top-up ID {pid} rad etildi!")

    # ========== ORDER ==========
    elif type_ == "order":
        if action == "approve":
            approve_order(pid)
            await callback.message.answer(f"🆔 Buyurtma ID {pid} tasdiqlandi!")
        else:
            set_order_status(pid, "declined")
            await callback.message.answer(f"🆔 Buyurtma ID {pid} rad etildi!")

    await callback.answer("✅ Amal bajarildi.", show_alert=False)


# =====================
# BALANCE EDIT
# =====================
@router.callback_query(F.data == "edit_balance")
async def ask_user_id(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Foydalanuvchi ID sini yuboring:")
    await state.set_state(EditBalance.waiting_user_id)


@router.message(StateFilter(EditBalance.waiting_user_id), F.text.regexp(r"^\d+$"))
async def ask_amount(message: types.Message, state: FSMContext):
    user_id = int(message.text)
    await state.update_data(user_id=user_id)
    balance = get_user_balance(user_id)
    await message.answer(f"Joriy balans: {balance} so‘m\nYangi balansni kiriting:")
    await state.set_state(EditBalance.waiting_new_balance)


@router.message(StateFilter(EditBalance.waiting_new_balance), F.text.regexp(r"^\d+$"))
async def set_balance(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]
    new_balance = int(message.text)
    update_balance(user_id, new_balance)
    await message.answer("✅ Balans yangilandi!")
    await state.clear()


# =====================
# SETTINGS EDIT
# =====================
@router.callback_query(F.data == "edit_settings")
async def start_edit_settings(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Qaysi kalitni o‘zgartirmoqchisiz?\n(admin_card, topup_min, topup_max)"
    )
    await state.set_state(EditSettings.waiting_key)


@router.message(StateFilter(EditSettings.waiting_key))
async def settings_key(message: types.Message, state: FSMContext):
    key = message.text.strip()
    await state.update_data(key=key)
    await message.answer("Yangi qiymatni kiriting:")
    await state.set_state(EditSettings.waiting_value)


@router.message(StateFilter(EditSettings.waiting_value))
async def settings_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    key = data.get("key")
    value = message.text.strip()

    if key:
        set_setting(key, value)
        await message.answer(f"✅ {key} yangilandi: {value}")
    else:
        await message.answer("❌ Xatolik: kalit topilmadi.")

    await state.clear()

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup

from keyboards import admin_menu, confirm_admin_kb
from config import OWNER_CHAT_ID
from db import (
    get_all_pending_orders, get_all_pending_topups,
    approve_order, approve_topup, update_balance,
    get_user_balance
)

# Router
router = Router()


# --- Balansni o‘zgartirish uchun States ---
class EditBalance(StatesGroup):
    waiting_user_id = State()
    waiting_new_balance = State()


# --- /admin komandasi ---
@router.message(Command("admin"))
async def admin_start(message: types.Message):
    if message.from_user.id != OWNER_CHAT_ID:
        await message.answer("🚫 Siz admin emassiz!")
        return
    await message.answer("👑 Admin panelga xush kelibsiz!", reply_markup=admin_menu())


# --- Pending buyurtmalar ---
@router.callback_query(F.data == "pending_orders")
async def pending_orders(call: types.CallbackQuery):
    orders = get_all_pending_orders()
    if not orders:
        await call.message.answer("✅ Hozircha kutayotgan buyurtmalar yo‘q.")
        return

    for o in orders:
        text = (
            f"🆔 Buyurtma ID: {o['id']}\n"
            f"👤 User ID: {o['user_tg']}\n"
            f"🎮 Mahsulot: {o['item_code']}\n"
            f"💰 Narx: {o['price']} so‘m"
        )
        await call.message.answer(text, reply_markup=confirm_admin_kb())


# --- Pending to‘lovlar ---
@router.callback_query(F.data == "pending_topups")
async def pending_topups(call: types.CallbackQuery):
    tops = get_all_pending_topups()
    if not tops:
        await call.message.answer("✅ Hozircha tasdiqlanmagan to‘lovlar yo‘q.")
        return

    for t in tops:
        text = (
            f"💳 Top-up ID: {t['id']}\n"
            f"👤 User ID: {t['user_tg']}\n"
            f"💰 Miqdor: {t['amount']} so‘m\n"
            f"📸 Screenshot: {t['screenshot_file_id']}"
        )
        await call.message.answer(text, reply_markup=confirm_admin_kb())


# --- Admin tasdiqlash ---
@router.callback_query(F.data == "admin_approve")
async def approve_action(call: types.CallbackQuery):
    msg = call.message.text
    if "Buyurtma ID" in msg:
        order_id = msg.split("Buyurtma ID: ")[1].split("\n")[0]
        approve_order(order_id)
        await call.message.answer("✅ Buyurtma tasdiqlandi!")
    elif "Top-up ID" in msg:
        topup_id = msg.split("Top-up ID: ")[1].split("\n")[0]
        approve_topup(topup_id)
        await call.message.answer("💰 To‘lov tasdiqlandi va balans yangilandi!")
    else:
        await call.message.answer("⚠️ Xatolik: ID topilmadi.")
    await call.answer()


# --- Admin rad etish ---
@router.callback_query(F.data == "admin_reject")
async def reject_action(call: types.CallbackQuery):
    await call.message.answer("❌ Rad etildi.")
    await call.answer()


# --- Balans tahrirlash ---
@router.callback_query(F.data == "edit_balance")
async def ask_user_id(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Foydalanuvchi ID sini yuboring:")
    await state.set_state(EditBalance.waiting_user_id)


# --- Foydalanuvchi ID qabul qilish ---
@router.message(StateFilter(EditBalance.waiting_user_id), F.text.regexp(r"^\d+$"))
async def ask_amount(message: types.Message, state: FSMContext):
    await state.update_data(user_id=int(message.text))
    balance = get_user_balance(int(message.text))
    await message.answer(f"Joriy balans: {balance} so‘m\nYangi balansni kiriting:")
    await state.set_state(EditBalance.waiting_new_balance)


# --- Yangi balans kiritish ---
@router.message(StateFilter(EditBalance.waiting_new_balance), F.text.regexp(r"^\d+$"))
async def set_balance(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]
    new_balance = int(message.text)
    update_balance(user_id, new_balance)
    await message.answer("✅ Balans yangilandi!")
    await state.clear()

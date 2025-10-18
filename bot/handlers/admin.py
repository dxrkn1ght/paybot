from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from keyboards import admin_menu, confirm_admin_kb
from config import OWNER_CHAT_ID
from db import get_all_pending_orders, get_all_pending_topups, approve_order, approve_topup, update_balance, get_user_balance

router = Router()

# /admin komandasi bilan kirish
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
            f"👤 User ID: {o['user_id']}\n"
            f"🎮 Nick: {o['user_nick']}\n"
            f"🛒 Mahsulot: {o['product_name']}\n"
            f"💰 Narx: {o['amount']} so‘m"
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
            f"👤 User ID: {t['user_id']}\n"
            f"💰 Miqdor: {t['amount']} so‘m\n"
            f"📸 Screenshot: {t['screenshot_url']}"
        )
        await call.message.answer(text, reply_markup=confirm_admin_kb())


# --- Admin tasdiqlash/reject ---
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


@router.callback_query(F.data == "admin_reject")
async def reject_action(call: types.CallbackQuery):
    await call.message.answer("❌ Rad etildi.")
    await call.answer()


# --- Balans o‘zgartirish ---
@router.callback_query(F.data == "edit_balance")
async def ask_user_id(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Foydalanuvchi ID sini yuboring:")
    await state.set_state("waiting_user_id")


@router.message(F.text.regexp(r"^\d+$"), state="waiting_user_id")
async def ask_amount(message: types.Message, state: FSMContext):
    await state.update_data(user_id=int(message.text))
    balance = get_user_balance(int(message.text))
    await message.answer(f"Joriy balans: {balance} so‘m\nYangi balansni kiriting:")
    await state.set_state("waiting_new_balance")


@router.message(F.text.regexp(r"^\d+$"), state="waiting_new_balance")
async def set_balance(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]
    new_balance = int(message.text)
    update_balance(user_id, new_balance)
    await message.answer("✅ Balans yangilandi!")
    await state.clear()

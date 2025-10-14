import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Text, Command
from aiogram.fsm.context import FSMContext
import config, db, messages, keyboards, states
log = logging.getLogger(__name__)
dp = Dispatcher()
@dp.message(CommandStart())
async def cmd_start(m: Message, state: FSMContext):
    db.get_or_create_user(m.from_user.id)
    await state.clear()
    await m.answer(messages.MESSAGES['uz']['start'], reply_markup=keyboards.lang_kb())
@dp.callback_query(Text(startswith='lang_'))
async def lang_choose(c: CallbackQuery, state: FSMContext):
    lang = c.data.split('_',1)[1]
    db.set_user_lang(c.from_user.id, lang)
    await c.message.edit_text(messages.MESSAGES[lang]['lang_set'].format(lang=lang))
    await c.message.answer(messages.MESSAGES[lang]['ask_nick'])
    await state.set_state(states.SetupStates.asking_nick)
    await c.answer()
@dp.message(states.SetupStates.asking_nick)
async def ask_nick(m: Message, state: FSMContext):
    nick = m.text.strip()
    db.set_user_nick(m.from_user.id, nick)
    data = db.get_or_create_user(m.from_user.id)
    lang = data.get('lang','uz')
    await m.answer(messages.MESSAGES[lang]['main_menu'], reply_markup=keyboards.main_menu_kb())
    await state.clear()
@dp.callback_query(Text('menu_products'))
async def show_products(c: CallbackQuery):
    user = db.get_or_create_user(c.from_user.id)
    lang = user.get('lang','uz')
    # try to read products from backend API
    try:
        import requests
        resp = requests.get(config.API_BASE + 'products/')
        items = resp.json()
        text = 'Products:\n'
        for it in items:
            text += f"{it['id']}. {it['name']} ({it['product_type']}) - {it['price']}\n"
    except Exception:
        text = messages.MESSAGES[lang]['choose_products'] + '\n(Backend unavailable)'
    await c.message.edit_text(text, reply_markup=keyboards.products_kb())
    await c.answer()
@dp.callback_query(Text('prod_coin'))
async def prod_coin(c: CallbackQuery, state: FSMContext):
    user = db.get_or_create_user(c.from_user.id)
    lang = user.get('lang','uz')
    await c.message.answer(messages.MESSAGES[lang]['coin_prompt'])
    await state.set_state(states.BuyStates.choosing_coin_amount)
    await c.answer()
@dp.message(states.BuyStates.choosing_coin_amount)
async def coin_amount_enter(m: Message, state: FSMContext):
    user = db.get_or_create_user(m.from_user.id)
    lang = user.get('lang','uz')
    try:
        amount = int(m.text.strip())
    except:
        await m.answer(messages.MESSAGES[lang]['coin_invalid'])
        return
    if amount < 10 or amount > 10000:
        await m.answer(messages.MESSAGES[lang]['coin_invalid'])
        return
    price = amount * config.COIN_PRICE
    await state.update_data(purchase={'type':'coin','amount':amount,'price':price})
    await m.answer(messages.MESSAGES[lang]['confirm_purchase'].format(item=f"{amount} coin", price=price), reply_markup=keyboards.coin_confirm_kb())
    await state.set_state(states.BuyStates.confirming_purchase)
@dp.callback_query(Text('confirm_coin'))
async def confirm_coin(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    purchase = data.get('purchase')
    user = db.get_or_create_user(c.from_user.id)
    lang = user.get('lang','uz')
    price = purchase['price']
    bal = db.get_balance(c.from_user.id)
    if bal < price:
        await c.message.answer(messages.MESSAGES[lang]['not_enough_balance'].format(balance=bal))
        try:
            await c.bot.send_message(config.ADMIN_USERNAME, f"User @{c.from_user.username} wants to buy {purchase['amount']} coins but has balance {bal}.")
        except:
            pass
        await c.answer()
        return
    ok = db.deduct_balance(c.from_user.id, price)
    if not ok:
        await c.message.answer(messages.MESSAGES[lang]['not_enough_balance'].format(balance=bal))
        await c.answer()
        return
    order_id = db.create_order(c.from_user.id, 'coin', f"amount:{purchase['amount']}", price)
    try:
        await c.bot.send_message(config.ADMIN_USERNAME, f"✅ New order #{order_id} from @{c.from_user.username}\nType: coin\nAmount: {purchase['amount']}\nPrice: {price}\nNick: {user.get('nick')}")
    except:
        pass
    await c.message.answer(messages.MESSAGES[lang]['purchase_success'])
    await state.clear()
    await c.answer()
@dp.callback_query(Text('prod_rank'))
async def prod_rank(c: CallbackQuery, state: FSMContext):
    user = db.get_or_create_user(c.from_user.id)
    lang = user.get('lang','uz')
    await c.message.answer(messages.MESSAGES[lang]['rank_menu'], reply_markup=keyboards.rank_kb())
    await c.answer()
@dp.callback_query(Text(startswith='rank_'))
async def rank_choose(c: CallbackQuery, state: FSMContext):
    which = c.data.split('_',1)[1]
    user = db.get_or_create_user(c.from_user.id)
    lang = user.get('lang','uz')
    price = {'vip':15000,'god':17000,'ultimate':20000}.get(which,0)
    await state.update_data(purchase={'type':'rank','rank':which,'price':price})
    await c.message.answer(messages.MESSAGES[lang]['confirm_purchase'].format(item=which.upper(), price=price), reply_markup=keyboards.coin_confirm_kb())
    await state.set_state(states.BuyStates.confirming_purchase)
    await c.answer()
@dp.callback_query(Text('cancel'))
async def cancel(c: CallbackQuery, state: FSMContext):
    user = db.get_or_create_user(c.from_user.id)
    lang = user.get('lang','uz')
    await state.clear()
    await c.message.answer('Bekor qilindi.', reply_markup=keyboards.main_menu_kb())
    await c.answer()
@dp.callback_query(Text('menu_topup'))
async def menu_topup(c: CallbackQuery, state: FSMContext):
    user = db.get_or_create_user(c.from_user.id)
    lang = user.get('lang','uz')
    await c.message.answer(messages.MESSAGES[lang]['topup_prompt'])
    await state.set_state(states.TopUpStates.entering_amount)
    await c.answer()
@dp.message(states.TopUpStates.entering_amount)
async def topup_amount(m: Message, state: FSMContext):
    user = db.get_or_create_user(m.from_user.id)
    lang = user.get('lang','uz')
    try:
        amount = int(m.text.strip())
    except:
        await m.answer(messages.MESSAGES[lang]['coin_invalid'])
        return
    if amount < 10000 or amount > 1000000:
        await m.answer(messages.MESSAGES[lang]['coin_invalid'])
        return
    payment_id = db.create_payment(m.from_user.id, amount)
    await m.answer(f"To'lov uchun karta ma'lumotlari (namuna):\nCard: 8600 12** **** 3456\n\nTo'lovdan so'ng skrinshot yuboring.\nPayment id: {payment_id}")
    await m.answer(messages.MESSAGES[lang]['topup_after_amount'])
    await state.update_data(payment_id=payment_id)
    await state.set_state(states.TopUpStates.waiting_screenshot)
@dp.message(states.TopUpStates.waiting_screenshot, F.photo | F.document)
async def topup_screenshot(m: Message, state: FSMContext):
    user = db.get_or_create_user(m.from_user.id)
    lang = user.get('lang','uz')
    data = await state.get_data()
    payment_id = data.get('payment_id')
    if m.photo:
        file_id = m.photo[-1].file_id
    else:
        file_id = m.document.file_id
    db.set_payment_screenshot(payment_id, file_id)
    try:
        await m.bot.send_message(config.ADMIN_USERNAME, f"🔔 New topup #{payment_id} by @{m.from_user.username}\nAmount: {m.caption if m.caption else ''}")
        if m.photo:
            await m.bot.send_photo(config.ADMIN_USERNAME, file_id, caption=f"Payment #{payment_id} screenshot")
        else:
            await m.bot.send_document(config.ADMIN_USERNAME, file_id, caption=f"Payment #{payment_id} screenshot")
    except Exception:
        log.exception('admin notify failed')
    await m.answer(messages.MESSAGES[lang]['topup_received'])
    await state.clear()
@dp.callback_query(Text('menu_orders'))
async def menu_orders(c: CallbackQuery):
    orders = db.get_user_orders(c.from_user.id)
    if not orders:
        await c.message.answer('Buyurtmalar topilmadi.', reply_markup=keyboards.main_menu_kb())
        await c.answer()
        return
    text = 'Sizning buyurtmalaringiz:\n'
    for o in orders:
        text += f"#{o['id']} {o['item_type']} — {o['status']} (price: {o['price']})\n"
    await c.message.answer(text, reply_markup=keyboards.main_menu_kb())
    await c.answer()
@dp.callback_query(Text('menu_balance'))
async def menu_balance(c: CallbackQuery):
    bal = db.get_balance(c.from_user.id)
    user = db.get_or_create_user(c.from_user.id)
    lang = user.get('lang','uz')
    await c.message.answer(messages.MESSAGES[lang]['balance'].format(balance=bal), reply_markup=keyboards.main_menu_kb())
    await c.answer()
@dp.callback_query(Text('menu_help'))
async def menu_help(c: CallbackQuery):
    user = db.get_or_create_user(c.from_user.id)
    lang = user.get('lang','uz')
    await c.message.answer(messages.MESSAGES[lang]['help'])
    await c.answer()
@dp.message(Command('admin_payments'))
async def admin_payments(m: Message):
    if not (m.from_user.username == config.ADMIN_USERNAME.lstrip('@') or m.from_user.id in config.ADMIN_IDS):
        await m.reply('Siz admin emassiz.')
        return
    pend = []
    try:
        import sqlite3
        cur = db.conn.cursor(); cur.execute('SELECT * FROM payments WHERE status="pending" ORDER BY id DESC'); pend = [dict(r) for r in cur.fetchall()]
    except:
        pass
    if not pend:
        await m.reply('Pending payments not found.')
        return
    for p in pend:
        text = f"#{p['id']} user:{p['user_tg']} amount:{p['amount']} status:{p['status']}"
        await m.bot.send_message(m.from_user.id, text, reply_markup=keyboards.admin_kb(p['id']))
@dp.callback_query(Text(startswith='admin_approve:'))
async def admin_approve(c: CallbackQuery):
    pid = int(c.data.split(':',1)[1])
    try:
        cur = db.conn.cursor(); cur.execute('SELECT * FROM payments WHERE id=?',(pid,)); row = cur.fetchone()
        if row:
            cur.execute('UPDATE payments SET status=? WHERE id=?',('approved',pid)); cur.execute('UPDATE users SET balance = balance + ? WHERE tg_id=?',(row['amount'], row['user_tg'])); db.conn.commit()
            await c.message.answer(f'Payment #{pid} approved and balance updated.')
            await c.bot.send_message(row['user_tg'], f"✅ To'lovingiz tasdiqlandi. {row['amount']} so'm balansingizga qo'shildi.")
    except Exception:
        pass
    await c.answer()
@dp.callback_query(Text(startswith='admin_reject:'))
async def admin_reject(c: CallbackQuery):
    pid = int(c.data.split(':',1)[1])
    cur = db.conn.cursor(); cur.execute('UPDATE payments SET status=? WHERE id=?',('rejected', pid)); db.conn.commit()
    await c.message.answer(f'Payment #{pid} rejected.')
    await c.answer()

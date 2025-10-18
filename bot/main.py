import telebot
from telebot import types

TOKEN = "8317966549:AAEIb0v6tnLMjkb5wc7Iw-XscOJg8mj9wEM"  # <-- bu yerga bot tokenini yoz
OWNER_ID = 993523630  # <-- bu yerga o‘zingning Telegram ID yoz

bot = telebot.TeleBot(TOKEN)

# Har bir foydalanuvchi uchun tanlangan tilni saqlash
user_language = {}


# /start komandasi
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.InlineKeyboardMarkup()
    uz_btn = types.InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang_uz")
    ru_btn = types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    markup.add(uz_btn, ru_btn)
    bot.send_message(
        message.chat.id,
        "Tilni tanlang / Выберите язык:",
        reply_markup=markup
    )


# Til tanlangandan keyin ishlovchi callback
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def choose_language(call):
    lang = call.data.split('_')[1]
    user_language[call.from_user.id] = lang

    if lang == "uz":
        text = "✅ Til tanlandi: O‘zbek.\n\nAsosiy menyu:"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🪙 Coinlar", "🏆 Ranklar", "👤 Profil")
    else:
        text = "✅ Язык выбран: Русский.\n\nГлавное меню:"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🪙 Монеты", "🏆 Ранги", "👤 Профиль")

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text=text,
        reply_markup=None
    )
    bot.send_message(call.message.chat.id, text, reply_markup=markup)


# /admin komandasi
@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id == OWNER_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📢 Xabar yuborish", "📊 Statistika", "⬅️ Orqaga")
        bot.send_message(message.chat.id, "Admin paneliga xush kelibsiz 👑", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz.")


# Asosiy menyudagi tugmalar
@bot.message_handler(func=lambda message: True)
def main_menu(message):
    lang = user_language.get(message.from_user.id, "uz")

    if message.text in ["🪙 Coinlar", "🪙 Монеты"]:
        text = "Bu yerda turli xil coinlar haqida ma'lumotlar bo‘ladi 💰"
    elif message.text in ["🏆 Ranklar", "🏆 Ранги"]:
        text = "Bu yerda ranklar va ularning shartlari ko‘rsatiladi 🏅"
    elif message.text in ["👤 Profil", "👤 Профиль"]:
        text = "Sizning profil ma’lumotlaringiz 👤"
    elif message.text in ["📢 Xabar yuborish"]:
        if message.from_user.id == OWNER_ID:
            text = "Yuboriladigan xabar matnini kiriting:"
        else:
            text = "❌ Siz admin emassiz."
    elif message.text in ["⬅️ Orqaga"]:
        text = "Asosiy menyuga qaytdingiz 🔙"
    else:
        text = "❓ Noma’lum buyruq."

    bot.send_message(message.chat.id, text)


# Botni ishga tushurish
print("🤖 Bot ishlayapti...")
bot.polling(none_stop=True)

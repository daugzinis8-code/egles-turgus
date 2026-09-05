import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN nerastas!")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎄 Sveikas! EGLĖS TURGUS! Siųsk eglutės foto!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    caption = message.caption or "Be kainos"
    bot.reply_to(message, f"✅ GAVAU foto! Kaina: {caption}\nSkelbimas patalpintas!")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.reply_to(message, f"Gavau: {message.text} - siųsk foto!")

print("Botas paleistas!")
bot.infinity_polling()
import os
import telebot

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎄 Sveikas! EGLES TURGUS! Siusk eglutes foto!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    caption = message.caption or "Be kainos"
    bot.reply_to(message, f"✅ GAVAU foto! Kaina: {caption}")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    bot.reply_to(message, f"Gavau: {message.text} - siusk foto!")

print("Botas paleistas!")
bot.infinity_polling()
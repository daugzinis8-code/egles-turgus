import os
import telebot
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Sveiki! Egles turgus veikia 24/7! 🌲")

@bot.message_handler(func=lambda m: True)
def reply(message):
    bot.send_message(message.chat.id, "Gavau: " + message.text)

bot.infinity_polling()

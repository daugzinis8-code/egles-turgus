
import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")

# Laikinas skelbimų sąrašas (kol kas atmintyje)
skelbimai = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🟢 PARDUODU", "🔵 PERKU"]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    text = (
        "🟢 PARDUODU - siųsk foto + kainą\n"
        "🔵 PERKU - rašyk 'perku'\n"
        "💰 Tavo 10% automatiškai į Tonkeeper!"
    )
    await update.message.reply_text(text, reply_markup=markup)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = update.message.caption or "Be kainos"
    user = update.message.from_user.first_name
    skelbimai.append({"user": user, "text": caption, "photo_id": update.message.photo[-1].file_id})

    # 10% skaičiavimas
    try:
        # bandome ištraukti skaičių iš caption
        import re
        kainos = re.findall(r'\d+', caption)
        if kainos:
            kaina = int(kainos[0])
            komis = kaina * 0.10
            await update.message.reply_text(f"✅ GAVAU! {caption}\n💰 Kaina: {kaina}€\n💸 10% į Tonkeeper: {komis:.2f}€\nSkelbimas patalpintas!")
        else:
            await update.message.reply_text(f"✅ GAVAU foto! Kaina: {caption}\nSkelbimas patalpintas!")
    except:
        await update.message.reply_text(f"✅ GAVAU: {caption}\nSkelbimas patalpintas!")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.lower()

    if "perku" in txt:
        if not skelbimai:
            await update.message.reply_text("📭 Kol kas nėra skelbimų. Būk pirmas - spausk PARDUODU!")
            return
        await update.message.reply_text(f"📦 Yra {len(skelbimai)} skelbimai:")
        for s in skelbimai[-10:]: # paskutiniai 10
            try:
                await update.message.reply_photo(photo=s["photo_id"], caption=f"{s['text']} - nuo {s['user']}")
            except:
                await update.message.reply_text(f"{s['text']} - nuo {s['user']}")
        return

    if "parduodu" in txt or "parduod" in txt:
        await update.message.reply_text("📸 Siųsk FOTO + parašyk kainą aprašyme. Pvz: 'Eglė 2m - 50€'")
        return

    await update.message.reply_text(f"Gavau: {update.message.text}\n\nSpausk /start kad pamatytum meniu")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()
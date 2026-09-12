import telebot, json, os, time
from telebot import types

TOKEN = "8667731379:AAHGElYC3kut4M5zcXhPJy_OY35nrwJHeSA"

bot = telebot.TeleBot(TOKEN)
DB_FILE = "turgus_db.json"
user_data = {}

def load_db():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # fixas kad nebūtų {} ir KeyError: slice
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return list(data.values())
            return []
    except:
        return []

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_main_markup():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("🔵 PARDUODU", "🟢 PERKU")
    m.add("🔍 IEŠKAU")
    m.add("📋 MANO SKELBIMAI", "💰 BALANSAS (10%)")
    return m

def format_item(item):
    user = f"@{item.get('username')}" if item.get('username') else item.get('user','')
    return f"🔵 {item.get('pavadinimas','-')}\n💰 {item.get('kaina','-')}\n📍 {item.get('vieta','-')}\n👤 {user}"

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "Eglės turgus Klaipėda veikia! 🔥\nPasirink:", reply_markup=get_main_markup())
    user_data.pop(msg.chat.id, None)

# --- PARDUODU ---
@bot.message_handler(func=lambda m: m.text == "🔵 PARDUODU")
def parduodu_1(msg):
    user_data[msg.chat.id] = {"action":"sell", "step":1}
    bot.send_message(msg.chat.id, "1/3 Ką parduodi? (pvz: Dviratis)")

@bot.message_handler(func=lambda m: m.text == "🔍 IEŠKAU")
def ieskau_start(msg):
    user_data[msg.chat.id] = {"action":"search", "step":1}
    bot.send_message(msg.chat.id, "🔍 Ką ieškai? Parašyk raktažodį (pvz: eglė, iphone, dviratis):")

@bot.message_handler(func=lambda m: m.text == "🟢 PERKU")
def perku(msg):
    db = load_db()
    if not db:
        bot.send_message(msg.chat.id, "Turgus tuščias.", reply_markup=get_main_markup())
        return
    # rodom paskutinius 10, nuo naujausio
    for item in reversed(db[-10:]):
        txt = format_item(item)
        if item.get("photo"):
            try:
                bot.send_photo(msg.chat.id, item["photo"], caption=txt)
                continue
            except: pass
        bot.send_message(msg.chat.id, txt)

@bot.message_handler(func=lambda m: m.text == "📋 MANO SKELBIMAI")
def mano(msg):
    db = load_db()
    mine = [x for x in db if x.get("chat_id")==msg.chat.id]
    if not mine:
        bot.send_message(msg.chat.id, "Neturi skelbimų")
        return
    for item in mine:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🗑️ Ištrinti", callback_data=f"del_{item['id']}"))
        txt = format_item(item)
        bot.send_message(msg.chat.id, txt, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💰 BALANSAS (10%)")
def balansas(msg):
    db = load_db()
    mine = [x for x in db if x.get("chat_id")==msg.chat.id]
    # pavyzdys: 10% nuo pardavimų
    total = 0
    for x in mine:
        try:
            k = str(x.get('kaina','0')).replace('€','').strip()
            total += float(k)
        except: pass
    bot.send_message(msg.chat.id, f"Tavo skelbimai: {len(mine)}\n10% sistema: {total*0.1:.2f}€")

# --- BENDRAS STEPS HANDLER ---
@bot.message_handler(content_types=['text','photo'])
def steps(msg):
    if msg.chat.id not in user_data:
        return
    data = user_data[msg.chat.id]

    # IEŠKAU logika
    if data["action"]=="search":
        db = load_db()
        q = (msg.text or "").lower()
        found = [x for x in db if q in x.get('pavadinimas','').lower()]
        if not found:
            bot.send_message(msg.chat.id, f"Nieko neradau pagal '{q}'", reply_markup=get_main_markup())
        else:
            for item in found[-10:]:
                bot.send_message(msg.chat.id, format_item(item))
        user_data.pop(msg.chat.id, None)
        return

    # PARDUODU logika
    if data["action"]=="sell":
        if data["step"]==1:
            # čia buvo tavo None klaida - pataisyta
            pavad = msg.text or msg.caption or "Be pavadinimo"
            data["pavadinimas"] = pavad
            data["step"]=2
            bot.send_message(msg.chat.id, "2/3 Kaina? (pvz: 10€)")

        elif data["step"]==2:
            data["kaina"] = msg.text or "0€"
            data["step"]=3
            bot.send_message(msg.chat.id, "3/3 Vieta? (pvz: Vilnius) + gali prisegti foto")

        elif data["step"]==3:
            vieta = msg.text if msg.content_type=='text' else (msg.caption or "Vilnius")
            # jei atsiuntė foto su caption kaip vieta
            if msg.content_type=='photo':
                vieta = msg.caption or "Vilnius"

            db = load_db()
            new_id = int(time.time()*1000)
            item = {
                "id": new_id,
                "pavadinimas": data["pavadinimas"],
                "kaina": data["kaina"],
                "vieta": vieta,
                "user": msg.from_user.first_name,
                "username": msg.from_user.username,
                "chat_id": msg.chat.id,
                "photo": msg.photo[-1].file_id if msg.content_type=='photo' else None
            }
            db.append(item)
            save_db(db)
            bot.send_message(msg.chat.id, "✅ Įdėta! Per PERKU matysi.", reply_markup=get_main_markup())
            user_data.pop(msg.chat.id, None)

@bot.callback_query_handler(func=lambda c: c.data.startswith("del_"))
def delete_item(c):
    try:
        nid = int(c.data.split("_")[1])
        db = load_db()
        db = [x for x in db if x.get('id')!=nid or x.get('chat_id')!=c.message.chat.id]
        save_db(db)
        bot.answer_callback_query(c.id, "Ištrinta")
        bot.delete_message(c.message.chat.id, c.message.message_id)
    except Exception as e:
        print(e)

print("BOTAS PALEISTAS")
while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Restart: {e}")
        time.sleep(3)
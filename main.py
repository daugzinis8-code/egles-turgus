import os, json, time, telebot
from telebot import types

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)
DB = "turgus_db.json"
user_data = {}

def load_db():
    if not os.path.exists(DB): return []
    try:
        with open(DB, "r", encoding="utf-8") as f:
            d=json.load(f); return d if isinstance(d,list) else []
    except: return []

def save_db(d):
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(d,f,ensure_ascii=False,indent=2)

def main_kb():
    kb=types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🔵 PARDUODU","🟢 PERKU"); kb.add("🔍 IEŠKAU")
    kb.add("📋 MANO SKELBIMAI","💰 BALANSAS")
    return kb

def fmt(x):
    return f"{x.get('pavadinimas','-')}\n{x.get('kaina','-')}\n{x.get('vieta','-')}\n@{x.get('username') or ''}"

@bot.message_handler(commands=['start'])
def start(m):
    user_data.pop(m.chat.id,None)
    bot.send_message(m.chat.id,"Eglės turgus Klaipėda 24/7!",reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text=="🔵 PARDUODU")
def p1(m):
    user_data[m.chat.id]={"a":"sell","s":1}
    bot.send_message(m.chat.id,"1/3 Ką parduodi?")

@bot.message_handler(func=lambda m: m.text=="🔍 IEŠKAU")
def s1(m):
    user_data[m.chat.id]={"a":"search"}
    bot.send_message(m.chat.id,"Ką ieškai?")

@bot.message_handler(func=lambda m: m.text=="🟢 PERKU")
def perku(m):
    db=load_db()
    if not db: bot.send_message(m.chat.id,"Turgus tuščias",reply_markup=main_kb()); return
    for x in reversed(db[-15:]): bot.send_message(m.chat.id, fmt(x))

@bot.message_handler(func=lambda m: m.text=="📋 MANO SKELBIMAI")
def mano(m):
    db=load_db(); mine=[x for x in db if x.get('chat_id')==m.chat.id]
    if not mine: bot.send_message(m.chat.id,"Neturi"); return
    for x in mine:
        kb=types.InlineKeyboardMarkup(); kb.add(types.InlineKeyboardButton("🗑️ Ištrinti",callback_data=f"del_{x['id']}"))
        bot.send_message(m.chat.id, fmt(x), reply_markup=kb)

@bot.message_handler(func=lambda m: m.text=="💰 BALANSAS")
def bal(m):
    db=load_db(); bot.send_message(m.chat.id,f"Skelbimu: {len([x for x in db if x.get('chat_id')==m.chat.id])}")

@bot.message_handler(content_types=['text'])
def steps(m):
    if m.chat.id not in user_data: return
    d=user_data[m.chat.id]
    if d['a']=='search':
        q=m.text.lower()[:4]; db=load_db(); found=[x for x in db if q in x.get('pavadinimas','').lower()]
        if not found: bot.send_message(m.chat.id,f"Nieko '{m.text}'",reply_markup=main_kb())
        else:
            for x in found: bot.send_message(m.chat.id, fmt(x))
        user_data.pop(m.chat.id,None); return
    if d['a']=='sell':
        if d['s']==1: d['pav']=m.text; d['s']=2; bot.send_message(m.chat.id,"2/3 Kaina?"); return
        if d['s']==2: d['kaina']=m.text; d['s']=3; bot.send_message(m.chat.id,"3/3 Vieta?"); return
        if d['s']==3:
            db=load_db(); db.append({"id":int(time.time()*1000),"pavadinimas":d['pav'],"kaina":d['kaina'],"vieta":m.text,"username":m.from_user.username,"chat_id":m.chat.id})
            save_db(db); bot.send_message(m.chat.id,"✅ Ideta!",reply_markup=main_kb()); user_data.pop(m.chat.id,None)

@bot.callback_query_handler(func=lambda c: c.data.startswith("del_"))
def dell(c):
    nid=int(c.data.split("_")[1]); db=load_db(); db=[x for x in db if x.get('id')!=nid]; save_db(db); bot.answer_callback_query(c.id,"Istrinta")

while True:
    try: bot.infinity_polling()
    except: time.sleep(3)
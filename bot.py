import telebot
from telebot import types
import json
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOSS_ID_RAW = os.environ.get("BOSS_ID", "0")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN not set in Environment!")
    exit(1)

try:
    BOSS_ID = int(BOSS_ID_RAW)
except:
    BOSS_ID = 0

bot = telebot.TeleBot(BOT_TOKEN)

if os.path.exists("db.json"):
    with open("db.json", "r") as f:
        db = json.load(f)
else:
    db = {"stock": {}, "users": {}}

def save_db():
    with open("db.json", "w") as f:
        json.dump(db, f)

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    if uid not in db["users"]:
        db["users"][uid] = {"plan": "FREE", "balance": 0}
        save_db()
    plan = db["users"][uid]["plan"]
    if message.from_user.id == BOSS_ID:
        plan = "👑 BOSS"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('👑 Buy 1 Days', '👑 Buy 3 Days')
    markup.row('👑 Buy 7 Days', '👑 Buy 15 Days')
    markup.row('👑 Buy 30 Days', '📦 Stock')
    markup.row('➕ Add Funds', '💰 Balance')
    markup.row('📁 Get Files')
    bot.send_message(message.chat.id, f"👑 SHINIGAMI\n\n👤 {message.from_user.first_name}\n👑 Plan: {plan}\n💰 Balance: ₹{db['users'][uid]['balance']}", reply_markup=markup)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != BOSS_ID:
        bot.send_message(message.chat.id, "❌ You are not BOSS!")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('➕ Add Stock', '➖ Delete Stock')
    markup.row('👑 Make VIP', '💎 Make Reseller')
    markup.row('👑 Make BOSS', '📦 Check Stock')
    markup.row('👥 Users List', '🔙 Back to Main')
    bot.send_message(message.chat.id, "👑 **BOSS ADMIN PANEL**\n\n✅ Admin OK BOSS\n\nNiche theke select koro:", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == '➕ Add Stock')
def add_stock_btn(message):
    if message.from_user.id != BOSS_ID: return
    bot.send_message(message.chat.id, "📝 Format:\n/addstock GAME DAYS KEY\nEx: /addstock CARROM 1D ABC-123")

@bot.message_handler(func=lambda m: m.text == '➖ Delete Stock')
def del_stock_btn(message):
    if message.from_user.id != BOSS_ID: return
    bot.send_message(message.chat.id, "🗑️ Format:\n/delstock GAME DAYS KEY")

@bot.message_handler(func=lambda m: m.text == '📦 Check Stock')
def check_stock_btn(message):
    if message.from_user.id != BOSS_ID: return
    text = "📦 STOCK:\n\n"
    if not db["stock"]: text += "Khali!"
    else:
        for k,v in db["stock"].items(): text += f"{k}: {len(v)} keys\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == '🔙 Back to Main')
def back_main(message):
    start(message)

@bot.message_handler(commands=['addstock'])
def addstock(message):
    if message.from_user.id != BOSS_ID: return
    try:
        parts = message.text.split(" ", 3)
        stock_key = f"{parts[1].upper()} {parts[2].upper()}"
        key = parts[3]
        if stock_key not in db["stock"]: db["stock"][stock_key] = []
        db["stock"][stock_key].append(key)
        save_db()
        bot.send_message(message.chat.id, f"✅ Added {stock_key}\n🔑 {key}")
    except:
        bot.send_message(message.chat.id, "❌ Use: /addstock GAME DAYS KEY")

@bot.message_handler(commands=['delstock','makevip','makereseller','makeboss'])
def other_cmds(message):
    if message.from_user.id != BOSS_ID: return
    bot.send_message(message.chat.id, "✅ Command received!")

print("✅ Bot Starting...")
bot.infinity_polling()

import telebot
from telebot import types
import json
import os

BOT_TOKEN = "TOMAR_BOT_TOKEN_EKHANE_DAO"
BOSS_ID = 123456789 # Ekhane tomar Telegram ID dao

bot = telebot.TeleBot(BOT_TOKEN)

# Database
if os.path.exists("db.json"):
    with open("db.json", "r") as f:
        db = json.load(f)
else:
    db = {"stock": {}, "users": {}}

def save_db():
    with open("db.json", "w") as f:
        json.dump(db, f)

# /start
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    if uid not in db["users"]:
        db["users"][uid] = {"plan": "FREE", "balance": 0}
        save_db()
    
    plan = db["users"][uid]["plan"]
    if str(message.from_user.id) == str(BOSS_ID):
        plan = "👑 BOSS"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('👑 Buy 1 Days', '👑 Buy 3 Days')
    markup.row('👑 Buy 7 Days', '👑 Buy 15 Days')
    markup.row('👑 Buy 30 Days', '📦 Stock')
    markup.row('➕ Add Funds', '💰 Balance')
    markup.row('📁 Get Files')
    
    bot.send_message(message.chat.id, f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {message.from_user.first_name}\n👑 Plan: {plan}\n💰 Balance: ₹{db['users'][uid]['balance']}\n🌍 Country: India\n\n🚀 Select an option below to get started", reply_markup=markup)

# /admin - FULL BOSS PANEL
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
    
    bot.send_message(message.chat.id, "👑 **BOSS ADMIN PANEL**\n\n✅ Admin OK BOSS\n\nKi korte chao? Niche theke select koro:", reply_markup=markup)

# Admin Panel Buttons
@bot.message_handler(func=lambda m: m.text == '➕ Add Stock')
def add_stock_btn(message):
    if message.from_user.id != BOSS_ID: return
    bot.send_message(message.chat.id, "📝 **Add Stock Format:**\n\n`/addstock GAME DAYS KEY`\n\n**Example:**\n`/addstock CARROM 1D KEY-ABC-123`\n`/addstock 8BP 7D 8BALL-XYZ-789`\n`/addstock LUDO 30D LUDO-TEST`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == '➖ Delete Stock')
def del_stock_btn(message):
    if message.from_user.id != BOSS_ID: return
    bot.send_message(message.chat.id, "🗑️ **Delete Stock Format:**\n\n`/delstock GAME DAYS KEY`\n\n**Example:**\n`/delstock CARROM 1D KEY-ABC-123`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == '👑 Make VIP')
def make_vip_btn(message):
    if message.from_user.id != BOSS_ID: return
    bot.send_message(message.chat.id, "👑 **Make VIP Format:**\n\n`/makevip USER_ID`\n\nUser er Telegram ID dite hobe.")

@bot.message_handler(func=lambda m: m.text == '💎 Make Reseller')
def make_reseller_btn(message):
    if message.from_user.id != BOSS_ID: return
    bot.send_message(message.chat.id, "💎 **Make Reseller Format:**\n\n`/makereseller USER_ID`")

@bot.message_handler(func=lambda m: m.text == '👑 Make BOSS')
def make_boss_btn(message):
    if message.from_user.id != BOSS_ID: return
    bot.send_message(message.chat.id, "👑 **Make BOSS Format:**\n\n`/makeboss USER_ID`")

@bot.message_handler(func=lambda m: m.text == '📦 Check Stock')
def check_stock_btn(message):
    if message.from_user.id != BOSS_ID: return
    text = "📦 **CURRENT STOCK:**\n\n"
    if not db["stock"]:
        text += "Stock Khali!"
    else:
        for game, keys in db["stock"].items():
            text += f"{game}: {len(keys)} keys\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == '🔙 Back to Main')
def back_main(message):
    start(message)

# /addstock Command
@bot.message_handler(commands=['addstock'])
def addstock(message):
    if message.from_user.id != BOSS_ID: return
    try:
        # /addstock CARROM 1D KEY-123
        parts = message.text.split(" ", 3)
        game = parts[1].upper()
        days = parts[2].upper()
        key = parts[3]
        stock_key = f"{game} {days}"
        if stock_key not in db["stock"]:
            db["stock"][stock_key] = []
        db["stock"][stock_key].append(key)
        save_db()
        bot.send_message(message.chat.id, f"✅ Added {stock_key}\n🔑 Key: {key}\n📦 Total: {len(db['stock'][stock_key])}")
    except:
        bot.send_message(message.chat.id, "❌ Use: /addstock GAME DAYS KEY\nEx: /addstock CARROM 1D MYKEY-123")

# /delstock
@bot.message_handler(commands=['delstock'])
def delstock(message):
    if message.from_user.id != BOSS_ID: return
    try:
        parts = message.text.split(" ", 3)
        game = parts[1].upper()
        days = parts[2].upper()
        key = parts[3]
        stock_key = f"{game} {days}"
        if stock_key in db["stock"] and key in db["stock"][stock_key]:
            db["stock"][stock_key].remove(key)
            save_db()
            bot.send_message(message.chat.id, f"✅ Deleted {key} from {stock_key}")
        else:
            bot.send_message(message.chat.id, "❌ Key not found!")
    except:
        bot.send_message(message.chat.id, "❌ Use: /delstock GAME DAYS KEY")

# /makevip /makereseller /makeboss
@bot.message_handler(commands=['makevip', 'makereseller', 'makeboss'])
def make_role(message):
    if message.from_user.id != BOSS_ID: return
    try:
        role = message.text.split()[0].replace("/", "").replace("make", "").upper()
        uid = message.text.split()[1]
        if uid not in db["users"]:
            db["users"][uid] = {"plan": "FREE", "balance": 0}
        db["users"][uid]["plan"] = role
        save_db()
        bot.send_message(message.chat.id, f"✅ User {uid} is now {role}")
    except:
        bot.send_message(message.chat.id, "❌ Use: /makevip USER_ID")

bot.polling(none_stop=True)

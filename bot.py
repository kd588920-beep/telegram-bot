import json, threading, os
from flask import Flask
from telebot import TeleBot, types

BOT_TOKEN = "9281252293:AAGf7HJwpTabKpth8klBlxMwe37QTwrMKNQ"
ADMIN_ID = 7189081595
BOT_NAME = "Koushik Gaming"
UPI_ID = "Jio Payments - 2754"

bot = TeleBot(BOT_TOKEN)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Live!"

STOCK_FILE = "stock.json"
PRICE = {"1D": 70, "3D": 150, "7D": 300, "15D": 550, "30D": 999}

try:
    with open(STOCK_FILE, 'r') as f: stock = json.load(f)
except: stock = {"1D": [], "3D": [], "7D": [], "15D": [], "30D": []}

def save_stock():
    with open(STOCK_FILE, 'w') as f: json.dump(stock, f)

def get_stock_text():
    return f"""📦 𝗧𝗢𝗧𝗔𝗟 𝗦𝗧𝗢𝗖𝗞 📦
━━━━━━━━━━━━━━━━━━
🔥 1 Days  : {len(stock['1D'])} Keys
🔥 3 Days  : {len(stock['3D'])} Keys
🔥 7 Days  : {len(stock['7D'])} Keys
🔥 15 Days : {len(stock['15D'])} Keys
🔥 30 Days : {len(stock['30D'])} Keys
━━━━━━━━━━━━━━━━━━
✨ Bot: Koushik Gaming"""

user_state = {}

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("🔥 Buy 1 Days"), types.KeyboardButton("🔥 Buy 3 Days"))
    markup.add(types.KeyboardButton("🔥 Buy 7 Days"), types.KeyboardButton("🔥 Buy 15 Days"))
    markup.add(types.KeyboardButton("🔥 Buy 30 Days"), types.KeyboardButton("📦 Stock"))
    markup.add(types.KeyboardButton("➕ Add Funds"), types.KeyboardButton("💰 Balance"))
    markup.add(types.KeyboardButton("📁 Get Files"))
    return markup

def admin_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("✅ 1D Add", callback_data="add_1D"),
               types.InlineKeyboardButton("✅ 3D Add", callback_data="add_3D"))
    markup.add(types.InlineKeyboardButton("✅ 7D Add", callback_data="add_7D"),
               types.InlineKeyboardButton("✅ 15D Add", callback_data="add_15D"),
               types.InlineKeyboardButton("✅ 30D Add", callback_data="add_30D"))
    return markup

@bot.message_handler(commands=['start', 'cancel'])
def start(message):
    if message.from_user.id in user_state: user_state.pop(message.from_user.id)
    name = message.from_user.first_name
    text = f"👑 Welcome to {BOT_NAME} Bot!\n\n👤 Name: {name}\n🏅 Plan: Bronze\n💰 Balance: ₹0.00\n🇮🇳 Country: India\n\n🚀 Select an option below to get started:"
    bot.send_message(message.chat.id, text, reply_markup=main_keyboard())

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    bot.send_message(message.chat.id, f"{get_stock_text()}\n\n👇 Konta add korbe?\n/cancel", reply_markup=admin_keyboard())

@bot.callback_query_handler(func=lambda c: c.data.startswith("add_"))
def ask_keys(call):
    plan = call.data.split("_")[1]
    user_state[call.from_user.id] = plan
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"🔑 {plan} er key paste koro\nCancel: /cancel")

@bot.message_handler(func=lambda m: m.from_user.id in user_state)
def save_keys(message):
    if message.text.startswith('/'): return
    plan = user_state.pop(message.from_user.id)
    keys = [k.strip() for k in message.text.split("\n") if k.strip()]
    stock[plan].extend(keys)
    save_stock()
    bot.send_message(message.chat.id, f"✅ {len(keys)} ta key {plan} te add holo!\n\n{get_stock_text()}", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: "Buy" in m.text and "Days" in m.text)
def buy_handler(message):
    if "1 Days" in message.text: plan="1D"
    elif "3 Days" in message.text: plan="3D"
    elif "7 Days" in message.text: plan="7D"
    elif "15 Days" in message.text: plan="15D"
    elif "30 Days" in message.text: plan="30D"
    else: return
    if len(stock[plan]) == 0:
        bot.send_message(message.chat.id, f"❌ {plan} Stock Out!", reply_markup=main_keyboard())
        return
    price = PRICE[plan]
    text = f"🎯 {plan.replace('D','')} Days Plan - CARROM\n💰 Price: ₹{price}\n🏦 UPI: {UPI_ID}\n\n📲 QR scan kore pay koro"
    bot.send_message(message.chat.id, text, reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "📦 Stock")
def stock_handler(message):
    bot.send_message(message.chat.id, get_stock_text(), reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: "Balance" in m.text)
def balance_handler(message):
    bot.send_message(message.chat.id, f"👤 Name: {message.from_user.first_name}\n💰 Balance: ₹0.00", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: "Add Funds" in m.text or "Get Files" in m.text)
def other_handler(message):
    bot.send_message(message.chat.id, f"📞 Admin @koushik ke contact koro!", reply_markup=main_keyboard())

def run_bot(): bot.infinity_polling()
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

import json, threading, os
from flask import Flask
from telebot import TeleBot, types

BOT_TOKEN = "9281252293:AAGf7HJwpTabKpth8klBlxMwe37QTwrMKNQ"
ADMIN_ID = 7189081595

bot = TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Live!"

STOCK_FILE = "stock.json"
try:
    with open(STOCK_FILE, 'r') as f:
        stock = json.load(f)
except:
    stock = {"1D": [], "3D": [], "7D": [], "15D": [], "30D": []}

def save_stock():
    with open(STOCK_FILE, 'w') as f:
        json.dump(stock, f)

def get_stock_text():
    return f"📦 Total Stock:\n1D: {len(stock['1D'])} | 3D: {len(stock['3D'])} | 7D: {len(stock['7D'])} | 15D: {len(stock['15D'])} | 30D: {len(stock['30D'])}"

user_state = {}

@bot.message_handler(commands=['cancel'])
def cancel_handle(message):
    if message.from_user.id in user_state:
        user_state.pop(message.from_user.id)
        bot.send_message(message.chat.id, "❌ Cancelled! State clear hoye geche.\nEbar /admin likho.")
    else:
        bot.send_message(message.chat.id, "Kichu cancel korar nei.")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ 1D Add", callback_data="add_1D"),
        types.InlineKeyboardButton("✅ 3D Add", callback_data="add_3D"),
        types.InlineKeyboardButton("✅ 7D Add", callback_data="add_7D"),
        types.InlineKeyboardButton("✅ 15D Add", callback_data="add_15D"),
        types.InlineKeyboardButton("✅ 30D Add", callback_data="add_30D"),
    )
    bot.send_message(message.chat.id, f"{get_stock_text()}\n\n👇 Konta add korbe?\nCancel korte /cancel likho", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("add_"))
def ask_keys(call):
    plan = call.data.split("_")[1]
    user_state[call.from_user.id] = plan
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"🔑 {plan} er key paste koro\nCancel korte /cancel likho.")

@bot.message_handler(func=lambda m: m.from_user.id in user_state)
def save_keys(message):
    if message.text.startswith('/'): return
    plan = user_state.pop(message.from_user.id)
    keys = [k.strip() for k in message.text.split("\n") if k.strip()]
    stock[plan].extend(keys)
    save_stock()
    bot.send_message(message.chat.id, f"✅ {len(keys)} ta key {plan} te add holo!\n\n{get_stock_text()}", parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in user_state:
        user_state.pop(message.from_user.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛒 Buy 1D", callback_data="buy_1D"),
               types.InlineKeyboardButton("🛒 Buy 3D", callback_data="buy_3D"))
    markup.add(types.InlineKeyboardButton("🛒 Buy 7D", callback_data="buy_7D"),
               types.InlineKeyboardButton("🛒 Buy 15D", callback_data="buy_15D"),
               types.InlineKeyboardButton("🛒 Buy 30D", callback_data="buy_30D"))
    bot.send_message(message.chat.id, f"Welcome! 👋\n\n{get_stock_text()}", reply_markup=markup, parse_mode="Markdown")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

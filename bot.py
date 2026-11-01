import os, threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7260634404
PRICE = {"1D": 70, "3D": 150, "7D": 300, "15D": 550, "30D": 1000}
stock = {"1D": [], "3D": [], "7D": [], "15D": [], "30D": []}
user_balance = {}

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Running!"

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("💳 Buy 1 Days"), types.KeyboardButton("💳 Buy 3 Days"))
    markup.add(types.KeyboardButton("💳 Buy 7 Days"), types.KeyboardButton("💳 Buy 15 Days"))
    markup.add(types.KeyboardButton("💳 Buy 30 Days"), types.KeyboardButton("📦 Stock"))
    markup.add(types.KeyboardButton("💰 Balance"), types.KeyboardButton("➕ Add Funds"))
    markup.add(types.KeyboardButton("📁 Get Files"))
    return markup

def get_stock_text():
    text = "📦 TOTAL STOCK 📦\n\n"
    for p in ["1D","3D","7D","15D","30D"]:
        text += f"🔥 {p.replace('D','')} Days : {len(stock[p])} Keys\n"
    return text

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id not in user_balance: user_balance[message.chat.id]=0
    bot.send_message(message.chat.id, f"👋 Welcome {message.from_user.first_name}!\n\n{get_stock_text()}", reply_markup=main_keyboard())

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID: return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ 1D Add","✅ 3D Add","✅ 7D Add","✅ 15D Add","✅ 30D Add","📊 All Stock")
    bot.send_message(message.chat.id, "👑 Admin Panel", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text and "✅" in m.text and "Add" in m.text)
def admin_add(message):
    if message.chat.id != ADMIN_ID: return
    plan = message.text.split()[1].replace("Add","").replace("✅","").strip()
    if "1D" in message.text: plan="1D"
    elif "3D" in message.text: plan="3D"
    elif "7D" in message.text: plan="7D"
    elif "15D" in message.text: plan="15D"
    elif "30D" in message.text: plan="30D"
    bot.send_message(message.chat.id, f"Send keys for {plan} (one per line)")
    bot.register_next_step_handler(message, lambda m: save_keys(m, plan))

def save_keys(message, plan):
    keys = [k.strip() for k in message.text.split("\n") if k.strip()]
    stock[plan].extend(keys)
    bot.send_message(message.chat.id, f"✅ {len(keys)} ta key {plan} te add holo!", reply_markup=main_keyboard())

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
    text = f"🎯 {plan.replace('D','')} Days Plan - CARROM\n💰 Price: {price} Taka\n\nUPI Payment koro tarpor screenshot dao!\n\n📦 Stock: {len(stock[plan])} Keys Available"
    bot.send_message(message.chat.id, text, reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "📦 Stock")
def stock_handler(message):
    bot.send_message(message.chat.id, get_stock_text(), reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: "Balance" in m.text)
def balance_handler(message):
    bot.send_message(message.chat.id, f"👤 Name: {message.from_user.first_name}\n💰 Balance: {user_balance.get(message.chat.id,0)} Taka", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: "Add Funds" in m.text or "Get Files" in m.text)
def other_handler(message):
    bot.send_message(message.chat.id, f"📞 Admin Contact:\n👑 Channel: @gamingkoushikyt\n🔗 Link: t.me/gamingkoushikyt", reply_markup=main_keyboard())

def run_bot(): bot.infinity_polling()
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

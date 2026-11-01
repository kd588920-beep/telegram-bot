import os, threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN=os.environ.get("BOT_TOKEN")
ADMIN_ID=7260634404
PRICE={"1D":70,"3D":150,"7D":300,"15D":550,"30D":1000}
stock={"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
user_balance={}

bot=telebot.TeleBot(BOT_TOKEN)
app=Flask(__name__)

@app.route('/')
def home(): return "Bot Running!"

def main_keyboard():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add("💳 Buy 1 Days","💳 Buy 3 Days")
    m.add("💳 Buy 7 Days","💳 Buy 15 Days")
    m.add("💳 Buy 30 Days","📦 Stock")
    m.add("💰 Balance","➕ Add Funds")
    m.add("📁 Get Files")
    return m

def get_stock_text():
    t="📦 TOTAL STOCK 📦\n\n"
    for p in ["1D","3D","7D","15D","30D"]:
        t+=f"🔥 {p}: {len(stock[p])} Keys\n"
    return t

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id,f"Hi {msg.from_user.first_name}\n\n{get_stock_text()}",reply_markup=main_keyboard())

@bot.message_handler(commands=['admin'])
def admin_panel(msg):
    if msg.chat.id!=ADMIN_ID: return
    m=types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("✅ 1D Add","✅ 3D Add","✅ 7D Add","✅ 15D Add","✅ 30D Add")
    bot.send_message(msg.chat.id,"Admin Panel",reply_markup=m)

@bot.message_handler(func=lambda m:"✅" in m.text and "Add" in m.text)
def admin_add(msg):
    if msg.chat.id!=ADMIN_ID: return
    p="1D"
    if "3D" in msg.text: p="3D"
    elif "7D" in msg.text: p="7D"
    elif "15D" in msg.text: p="15D"
    elif "30D" in msg.text: p="30D"
    bot.send_message(msg.chat.id,f"Send keys for {p}")
    bot.register_next_step_handler(msg,lambda m: save_keys(m,p))

def save_keys(msg,plan):
    keys=[k.strip() for k in msg.text.split("\n") if k.strip()]
    stock[plan].extend(keys)
    bot.send_message(msg.chat.id,f"✅ {len(keys)} keys added to {plan}",reply_markup=main_keyboard())

@bot.message_handler(func=lambda m:"Buy" in m.text)
def buy(msg):
    p="1D"
    if "3 Days" in msg.text: p="3D"
    elif "7 Days" in msg.text: p="7D"
    elif "15 Days" in msg.text: p="15D"
    elif "30 Days" in msg.text: p="30D"
    if len(stock[p])==0:
        bot.send_message(msg.chat.id,f"❌ {p} Out of Stock",reply_markup=main_keyboard())
        return
    bot.send_message(msg.chat.id,f"🎯 {p} Plan - CARROM\n💰 Price: {PRICE[p]} Taka\nStock: {len(stock[p])}",reply_markup=main_keyboard())

@bot.message_handler(func=lambda m:m.text=="📦 Stock")
def stk(msg):
    bot.send_message(msg.chat.id,get_stock_text(),reply_markup=main_keyboard())

@bot.message_handler(func=lambda m:"Balance" in m.text)
def bal(msg):
    bot.send_message(msg.chat.id,f"Balance: {user_balance.get(msg.chat.id,0)}",reply_markup=main_keyboard())

@bot.message_handler(func=lambda m:"Add Funds" in m.text or "Get Files" in m.text)
def other(msg):
    bot.send_message(msg.chat.id,"📞 Admin Contact:\n👑 @gamingkoushikyt\n🔗 t.me/gamingkoushikyt",reply_markup=main_keyboard())

def run_bot(): bot.infinity_polling()
if __name__=="__main__":
    threading.Thread(target=run_bot).start()
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)

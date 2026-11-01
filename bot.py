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
    t+=f"🔥 1 Days : {len(stock['1D'])} Keys\n"
    t+=f"🔥 3 Days : {len(stock['3D'])} Keys\n"
    t+=f"🔥 7 Days : {len(stock['7D'])} Keys\n"
    t+=f"🔥 15 Days : {len(stock['15D'])} Keys\n"
    t+=f"🔥 30 Days : {len(stock['30D'])} Keys\n"
    return t

@bot.message_handler(commands=['start'])
def start(msg):
    if msg.chat.id not in user_balance: user_balance[msg.chat.id]=0
    bot.send_message(msg.chat.id,f"Hi {msg.from_user.first_name}!\n\n{get_stock_text()}",reply_markup=main_keyboard())

@bot.message_handler(commands=['admin'])
def admin_panel(msg):
    if msg.chat.id!=ADMIN_ID: return
    m=types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("✅ 1D Add","✅ 3D Add","✅ 7D Add","✅ 15D Add","✅ 30D Add","📊 All Stock")
    bot.send_message(msg.chat.id,"👑 Admin Panel\nKey Add koro:",reply_markup=m)

@bot.message_handler(func=lambda m:m.text and "✅" in m.text and "Add" in m.text)
def admin_add(msg):
    if msg.chat.id!=ADMIN_ID: return
    p="1D"
    if "3D" in msg.text: p="3D"
    elif "7D" in msg.text: p="7D"
    elif "15D" in msg.text: p="15D"
    elif "30D" in msg.text: p="30D"
    bot.send_message(msg.chat.id,f"Send keys for {p} (one per line):")
    bot.register_next_step_handler(msg,lambda m: save_keys(m,p))

def save_keys(msg,plan):
    keys=[k.strip() for k in msg.text.split("\n") if k.strip()]
    stock[plan].extend(keys)
    bot.send_message(msg.chat.id,f"✅ {len(keys)} ta key {plan} te add holo!\n\n{get_stock_text()}",reply_markup=main_keyboard())

@bot.message_handler(func=lambda m:m.text and "Buy" in m.text and "Days" in m.text)
def buy(msg):
    p="1D"
    if "3 Days" in msg.text: p="3D"
    elif "7 Days" in msg.text: p="7D"
    elif "15 Days" in msg.text: p="15D"
    elif "30 Days" in msg.text: p="30D"
    if len(stock[p])==0:
        bot.send_message(msg.chat.id,f"❌ {p} Stock Out! Admin ke bolo!",reply_markup=main_keyboard())
        return
    bot.send_message(msg.chat.id,f"🎯 {p.replace('D','')} Days Plan - CARROM\n💰 Price: {PRICE[p]} Taka\n\n📦 Stock: {len(stock[p])} Keys Available\n\nUPI Payment koro!",reply_markup=main_keyboard())

@bot.message_handler(func=lambda m:m.text=="📦 Stock")
def stk(msg):
    bot.send_message(msg.chat.id,get_stock_text(),reply_markup=main_keyboard())

@bot.message_handler(func=lambda m:m.text and "Balance" in m.text)
def bal(msg):
    bot.send_message(msg.chat.id,f"👤 {msg.from_user.first_name}\n💰 Balance: {user_balance.get(msg.chat.id,0)} Taka",reply_markup=main_keyboard())

@bot.message_handler(func=lambda m:m.text and ("Add Funds" in m.text or "Get Files" in m.text))
def other(msg):
    bot.send_message(msg.chat.id,f"📞 Admin Contact:\n👑 Channel: @gamingkoushikyt\n🔗 Link: t.me/gamingkoushikyt\n\n💬 Message koro!",reply_markup=main_keyboard())

def run_bot(): bot.infinity_polling()
if __name__=="__main__":
    threading.Thread(target=run_bot).start()
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)

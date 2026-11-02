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
def home(): return "SHINIGAMI Bot Running!"

def main_kb():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add("💳 Buy 1 Days","💳 Buy 3 Days")
    m.add("💳 Buy 7 Days","💳 Buy 15 Days")
    m.add("💳 Buy 30 Days","📦 Stock")
    m.add("💰 Balance","➕ Add Funds")
    m.add("📁 Get Files")
    return m

@bot.message_handler(commands=['start'])
def start(msg):
    uid=msg.from_user.id
    if uid not in user_balance: user_balance[uid]=0
    bot.send_message(msg.chat.id, f"☠️ SHINIGAMI STORE ☠️\n\nPlans:\n1D ₹{PRICE['1D']} | 3D ₹{PRICE['3D']}\n7D ₹{PRICE['7D']} | 15D ₹{PRICE['15D']}\n30D ₹{PRICE['30D']}\n\nBalance: ₹{user_balance[uid]}\nID: {uid}\n\nChoose 👇", reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text and "Buy" in m.text)
def buy(msg):
    mapping={"Buy 1 Days":"1D","Buy 3 Days":"3D","Buy 7 Days":"7D","Buy 15 Days":"15D","Buy 30 Days":"30D"}
    plan=None
    for k,v in mapping.items():
        if k in msg.text: plan=v
    if not plan: return
    bal=user_balance.get(msg.from_user.id,0)
    if bal<PRICE[plan]:
        bot.send_message(msg.chat.id, f"❌ Low Balance! Need ₹{PRICE[plan]}, You have ₹{bal}")
        return
    if not stock[plan]:
        bot.send_message(msg.chat.id, f"⚠️ Stock empty for {plan}")
        return
    user_balance[msg.from_user.id]=bal-PRICE[plan]
    file_data=stock[plan].pop(0)
    bot.send_message(msg.chat.id, f"✅ Purchase!\nPlan: {plan}\nFile: {file_data}\nRemaining: ₹{user_balance[msg.from_user.id]}")

@bot.message_handler(commands=['addstock'])
def addstock(msg):
    if msg.from_user.id!=ADMIN_ID: return
    try:
        p=msg.text.split(" ",2); stock[p[1].upper()].append(p[2])
        bot.send_message(msg.chat.id, f"✅ Added. Total {len(stock[p[1].upper()])}")
    except Exception as e: bot.send_message(msg.chat.id, f"Use: /addstock 1D file\nError {e}")

@bot.message_handler(commands=['addbalance'])
def addbal(msg):
    if msg.from_user.id!=ADMIN_ID: return
    try:
        p=msg.text.split(); uid=int(p[1]); amt=int(p[2])
        user_balance[uid]=user_balance.get(uid,0)+amt
        bot.send_message(msg.chat.id, f"✅ Added ₹{amt} to {uid}")
        bot.send_message(uid, f"💰 Admin added ₹{amt}! New Bal ₹{user_balance[uid]}")
    except Exception as e: bot.send_message(msg.chat.id, f"Use: /addbalance ID AMOUNT\n{e}")

def run_flask(): app.run(host="0.0.0.0",port=10000)
threading.Thread(target=run_flask,daemon=True).start()
bot.infinity_polling()

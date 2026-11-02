import os
import threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN=os.environ.get("BOT_TOKEN")
ADMIN_ID=7189081595

PRICE={"1D":70,"3D":150,"7D":300,"15D":550,"30D":1000}

# 2 GAME STOCK
stock_carrom={"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
stock_8ball={"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}

user_balance={}
user_country={}

bot=telebot.TeleBot(BOT_TOKEN)
app=Flask(__name__)

@app.route('/')
def home():
    return "SHINIGAMI Running"

def country_kb():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton("India", callback_data="country_India"),
        types.InlineKeyboardButton("Bangladesh", callback_data="country_Bangladesh")
    )
    return m

def main_kb():
    m=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    m.add(types.KeyboardButton("🩸 Buy 1 Days"), types.KeyboardButton("🩸 Buy 3 Days"))
    m.add(types.KeyboardButton("🩸 Buy 7 Days"), types.KeyboardButton("🩸 Buy 15 Days"))
    m.add(types.KeyboardButton("🩸 Buy 30 Days"), types.KeyboardButton("📦 Stock"))
    m.add(types.KeyboardButton("➕ Add Funds"), types.KeyboardButton("💰 Balance"))
    m.add(types.KeyboardButton("📁 Get Files"))
    return m

@bot.message_handler(commands=['start'])
def s(m):
    uid=m.from_user.id
    if uid not in user_balance:
        user_balance[uid]=0.0
    if uid not in user_country:
        bot.send_message(m.chat.id, "Welcome to SHINIGAMI Bot!\nSelect country:", reply_markup=country_kb())
    else:
        txt=f"Welcome to SHINIGAMI Bot!\n\n👑 Plan: Bronze\n💰 Balance: ₹{user_balance[uid]}\n🌍 Country: {user_country.get(uid,'India')}\n\n🚀 Select an option below to get started:"
        bot.send_message(m.chat.id, txt, reply_markup=main_kb())

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid=c.from_user.id
    if c.data.startswith("country_"):
        user_country[uid]=c.data.split("_")[1]
        bot.send_message(c.message.chat.id, f"Plan: Bronze\nBalance: ₹{user_balance.get(uid,0)}\nCountry: {user_country[uid]}", reply_markup=main_kb())
    bot.answer_callback_query(c.id)

@bot.message_handler(func=lambda m: m.text=="📦 Stock")
def st(m):
    msg="📦 Live Stock Status\n"
    msg+="━━━━━━━━━━━━━━━━━━━━\n\n"
    msg+="🎯 CARROM\n"
    for k in ["1D","3D","7D","15D","30D"]:
        cnt=len(stock_carrom[k])
        if cnt>0:
            msg+=f"✅ {k.replace('D','')} Days: {cnt} keys\n"
        else:
            msg+=f"❌ {k.replace('D','')} Days: 0 keys\n"
    msg+="\n🎱 8 BALL POOL\n"
    for k in ["1D","3D","7D","15D","30D"]:
        cnt=len(stock_8ball[k])
        if cnt>0:
            msg+=f"✅ {k.replace('D','')} Days: {cnt} keys\n"
        else:
            msg+=f"❌ {k.replace('D','')} Days: 0 keys\n"
    bot.send_message(m.chat.id, msg)

@bot.message_handler(func=lambda m: m.text=="💰 Balance")
def bl(m):
    bot.send_message(m.chat.id, f"💰 Balance: ₹{user_balance.get(m.from_user.id,0)}")

@bot.message_handler(commands=['addstock'])
def ast(m):
    if m.from_user.id!=ADMIN_ID:
        return
    try:
        # Use: /addstock CARROM 1D KEY or /addstock 8BALL 1D KEY
        parts=m.text.split(" ",3)
        game=parts[1].upper()
        day=parts[2].upper()
        key=parts[3]
        if "CARROM" in game:
            stock_carrom[day].append(key)
            bot.reply_to(m, f"Added CARROM {day}")
        else:
            stock_8ball[day].append(key)
            bot.reply_to(m, f"Added 8BALL {day}")
    except:
        bot.reply_to(m, "Use:\n/addstock CARROM 1D KEY\n/addstock 8BALL 1D KEY")

@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.from_user.id==ADMIN_ID:
        bot.send_message(m.chat.id, f"ADMIN\nCARROM: {sum(len(v) for v in stock_carrom.values())} keys\n8BALL: {sum(len(v) for v in stock_8ball.values())} keys")

def run():
    app.run(host="0.0.0.0",port=10000)

threading.Thread(target=run,daemon=True).start()
bot.infinity_polling()

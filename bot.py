import os
import threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN=os.environ.get("BOT_TOKEN")
ADMIN_ID=7189081595

# PRICE - choto line
PRICE={}
PRICE["1D"]=70
PRICE["3D"]=150
PRICE["7D"]=300
PRICE["15D"]=550
PRICE["30D"]=1000

# STOCK CARROM - choto line
stock_carrom={}
stock_carrom["1D"]=[]
stock_carrom["3D"]=[]
stock_carrom["7D"]=[]
stock_carrom["15D"]=[]
stock_carrom["30D"]=[]

# STOCK 8BALL - choto line
stock_8ball={}
stock_8ball["1D"]=[]
stock_8ball["3D"]=[]
stock_8ball["7D"]=[]
stock_8ball["15D"]=[]
stock_8ball["30D"]=[]

user_balance={}
user_country={}

bot=telebot.TeleBot(BOT_TOKEN)
app=Flask(__name__)

@app.route('/')
def home():
    return "OK"

def country_kb():
    m=types.InlineKeyboardMarkup()
    m.add(
        types.InlineKeyboardButton(
            "India",
            callback_data="c_India"
        ),
        types.InlineKeyboardButton(
            "Bangladesh",
            callback_data="c_Bangladesh"
        )
    )
    return m

def main_kb():
    m=types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )
    m.add(
        types.KeyboardButton("Buy 1 Days"),
        types.KeyboardButton("Buy 3 Days")
    )
    m.add(
        types.KeyboardButton("Buy 7 Days"),
        types.KeyboardButton("Buy 15 Days")
    )
    m.add(
        types.KeyboardButton("Buy 30 Days"),
        types.KeyboardButton("Stock")
    )
    m.add(
        types.KeyboardButton("Add Funds"),
        types.KeyboardButton("Balance")
    )
    return m

@bot.message_handler(commands=['start'])
def start(m):
    uid=m.from_user.id
    if uid not in user_balance:
        user_balance[uid]=0.0
    if uid not in user_country:
        bot.send_message(
            m.chat.id,
            "Select country",
            reply_markup=country_kb()
        )
    else:
        bot.send_message(
            m.chat.id,
            "Welcome",
            reply_markup=main_kb()
        )

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    if c.data.startswith("c_"):
        user_country[c.from_user.id]=c.data[2:]
        bot.send_message(
            c.message.chat.id,
            "Welcome",
            reply_markup=main_kb()
        )
    bot.answer_callback_query(c.id)

@bot.message_handler(func=lambda m: m.text=="Stock")
def stock_cmd(m):
    txt="Live Stock Status\n"
    txt+="----------------\n\n"
    txt+="CARROM\n"
    for d in ["1D","3D","7D","15D","30D"]:
        n=len(stock_carrom[d])
        if n>0:
            txt+=f"✅ {d} : {n} keys\n"
        else:
            txt+=f"❌ {d} : 0 keys\n"
    txt+="\n8 BALL POOL\n"
    for d in ["1D","3D","7D","15D","30D"]:
        n=len(stock_8ball[d])
        if n>0:
            txt+=f"✅ {d} : {n} keys\n"
        else:
            txt+=f"❌ {d} : 0 keys\n"
    bot.send_message(m.chat.id, txt)

@bot.message_handler(commands=['addstock'])
def add(m):
    if m.from_user.id!=ADMIN_ID:
        return
    try:
        p=m.text.split(" ",3)
        game=p[1].upper()
        day=p[2].upper()
        key=p[3]
        if "CARROM" in game:
            stock_carrom[day].append(key)
            bot.reply_to(m, "CARROM Added")
        else:
            stock_8ball[day].append(key)
            bot.reply_to(m, "8BALL Added")
    except:
        bot.reply_to(m, "Use: /addstock CARROM 1D KEY")

@bot.message_handler(commands=['admin'])
def admin(m):
    if m.from_user.id==ADMIN_ID:
        bot.send_message(m.chat.id, "Admin OK")

def run():
    app.run(host="0.0.0.0",port=10000)

threading.Thread(target=run,daemon=True).start()
bot.infinity_polling()

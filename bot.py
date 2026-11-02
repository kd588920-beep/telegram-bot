import os
import json
import threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN=os.environ.get("BOT_TOKEN")
ADMIN_ID=7189081595

def save_data():
    with open("data.json","w") as f:
        json.dump({
            "bal":user_balance,
            "country":user_country,
            "plan":user_plan,
            "carrom":stock_carrom,
            "ball":stock_8ball
        }, f)

def load_data():
    global user_balance
    global user_country
    global user_plan
    global stock_carrom
    global stock_8ball
    try:
        with open("data.json","r") as f:
            d=json.load(f)
            user_balance=d.get("bal",{})
            user_country=d.get("country",{})
            user_plan=d.get("plan",{})
            stock_carrom=d.get("carrom",stock_carrom)
            stock_8ball=d.get("ball",stock_8ball)
    except:
        pass

PRICE={}
PRICE["1D"]=70
PRICE["3D"]=150
PRICE["7D"]=300
PRICE["15D"]=550
PRICE["30D"]=1000

stock_carrom={}
stock_carrom["1D"]=[]
stock_carrom["3D"]=[]
stock_carrom["7D"]=[]
stock_carrom["15D"]=[]
stock_carrom["30D"]=[]

stock_8ball={}
stock_8ball["1D"]=[]
stock_8ball["3D"]=[]
stock_8ball["7D"]=[]
stock_8ball["15D"]=[]
stock_8ball["30D"]=[]

user_balance={}
user_country={}
user_plan={}

load_data()

bot=telebot.TeleBot(BOT_TOKEN)
app=Flask(__name__)

@app.route('/')
def home():
    return "SHINIGAMI OK"

def country_kb():
    m=types.InlineKeyboardMarkup(row_width=1)
    m.add(
        types.InlineKeyboardButton("🇮🇳 India", callback_data="country_India")
    )
    m.add(
        types.InlineKeyboardButton("🇧🇩 Bangladesh", callback_data="country_Bangladesh")
    )
    return m

def main_kb():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add(types.KeyboardButton("👑 Buy 1 Days"),types.KeyboardButton("👑 Buy 3 Days"))
    m.add(types.KeyboardButton("👑 Buy 7 Days"),types.KeyboardButton("👑 Buy 15 Days"))
    m.add(types.KeyboardButton("👑 Buy 30 Days"),types.KeyboardButton("📦 Stock"))
    m.add(types.KeyboardButton("➕ Add Funds"),types.KeyboardButton("💰 Balance"))
    m.add(types.KeyboardButton("📁 Get Files"))
    return m

def welcome_text(uid):
    uid_str=str(uid)
    bal=user_balance.get(uid_str,0)
    country=user_country.get(uid_str,"India")
    if country=="India":
        flag="🇮🇳"
    else:
        flag="🇧🇩"
    if str(uid)==str(ADMIN_ID):
        plan="👑 BOSS"
    else:
        plan=user_plan.get(uid_str,"Free User")
    return (
        f"👑 Welcome to SHINIGAMI Bot!\n\n"
        f"👤 Name: Koushik\n"
        f"👑 Plan: {plan}\n"
        f"💰 Balance: ₹{bal}\n"
        f"{flag} Country: {country}\n\n"
        f"🚀 Select an option below to get started"
    )

@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid=str(m.from_user.id)
    if uid not in user_balance:
        user_balance[uid]=0.0
        save_data()
    if uid not in user_country:
        bot.send_message(m.chat.id,"🌍 Select country",reply_markup=country_kb())
    else:
        bot.send_message(m.chat.id,welcome_text(m.from_user.id),reply_markup=main_kb())

@bot.callback_query_handler(func=lambda c: True)
def cb_handler(c):
    uid=str(c.from_user.id)
    if "India" in c.data:
        user_country[uid]="India"
        save_data()
        bot.send_message(c.message.chat.id,welcome_text(c.from_user.id),reply_markup=main_kb())
    elif "Bangladesh" in c.data:
        user_country[uid]="Bangladesh"
        save_data()
        bot.send_message(c.message.chat.id,welcome_text(c.from_user.id),reply_markup=main_kb())
    bot.answer_callback_query(c.id)

@bot.message_handler(func=lambda m: m.text=="📦 Stock")
def stock_handler(m):
    txt="📦 Live Stock Status\n━━━━━━━━━━━━\n\n🎯 CARROM\n"
    for d in ["1D","3D","7D","15D","30D"]:
        n=len(stock_carrom.get(d,[]))
        if n>0:
            txt+=f"✅ {d} : {n} keys\n"
        else:
            txt+=f"❌ {d} : 0 keys\n"
    txt+="\n🎱 8 BALL POOL\n"
    for d in ["1D","3D","7D","15D","30D"]:
        n=len(stock_8ball.get(d,[]))
        if n>0:
            txt+=f"✅ {d} : {n} keys\n"
        else:
            txt+=f"❌ {d} : 0 keys\n"
    bot.send_message(m.chat.id, txt)

@bot.message_handler(func=lambda m: m.text=="💰 Balance")
def bal_handler(m):
    uid=str(m.from_user.id)
    b=user_balance.get(uid,0)
    bot.send_message(m.chat.id, f"💰 Balance: ₹{b}")

@bot.message_handler(commands=['addstock'])
def addstock_cmd(m):
    if m.from_user.id!=ADMIN_ID:
        return
    try:
        parts=m.text.split(" ",3)
        game=parts[1].upper()
        day=parts[2].upper()
        key=parts[3]
        if "CARROM" in game:
            stock_carrom[day].append(key)
        else:
            stock_8ball[day].append(key)
        save_data()
        bot.reply_to(m, f"Added {game} {day}")
    except:
        bot.reply_to(m, "Use: /addstock CARROM 1D KEY")

@bot.message_handler(commands=['makevip'])
def makevip_cmd(m):
    if m.from_user.id!=ADMIN_ID:
        return
    try:
        uid=m.text.split(" ")[1]
        user_plan[str(uid)]="Vip 👑 VIP/Reseller"
        save_data()
        bot.reply_to(m, f"✅ {uid} ke VIP banano holo!")
    except:
        bot.reply_to(m, "Use: /makevip USER_ID")

@bot.message_handler(commands=['makereseller'])
def makereseller_cmd(m):
    if m.from_user.id!=ADMIN_ID:
        return
    try:
        uid=m.text.split(" ")[1]
        user_plan[str(uid)]="Reseller"
        save_data()
        bot.reply_to(m, f"✅ {uid} ke Reseller banano holo!")
    except:
        bot.reply_to(m, "Use: /makereseller USER_ID")

@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.from_user.id==ADMIN_ID:
        bot.send_message(m.chat.id, "Admin OK BOSS")

def run_flask():
    app.run(host="0.0.0.0",port=10000)

threading.Thread(target=run_flask,daemon=True).start()
bot.infinity_polling()

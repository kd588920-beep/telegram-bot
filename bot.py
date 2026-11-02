import os, threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN=os.environ.get("BOT_TOKEN")
ADMIN_ID=7260634404
PRICE={"1D":70,"3D":150,"7D":300,"15D":550,"30D":1000}
stock={"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
user_balance={}
user_country={}

bot=telebot.TeleBot(BOT_TOKEN)
app=Flask(__name__)
@app.route('/')
def home(): return "SHINIGAMI Running"

def country_kb():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton("🇮🇳 India", callback_data="country_India"),
        types.InlineKeyboardButton("🇧🇩 Bangladesh", callback_data="country_Bangladesh")
    )
    return m

def main_kb():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("🔴 Buy 1 Days", callback_data="buy_1D"), types.InlineKeyboardButton("🔴 Buy 3 Days", callback_data="buy_3D"))
    m.add(types.InlineKeyboardButton("🔴 Buy 7 Days", callback_data="buy_7D"), types.InlineKeyboardButton("🔴 Buy 15 Days", callback_data="buy_15D"))
    m.add(types.InlineKeyboardButton("🔴 Buy 30 Days", callback_data="buy_30D"), types.InlineKeyboardButton("📦 Stock", callback_data="stock"))
    m.add(types.InlineKeyboardButton("➕ Add Funds", callback_data="addfunds"), types.InlineKeyboardButton("💰 Balance", callback_data="bal"))
    m.add(types.InlineKeyboardButton("📁 Get Files", callback_data="getfiles"))
    return m

def welcome(m):
    name=m.from_user.first_name
    bal=user_balance.get(m.from_user.id,0.00)
    country=user_country.get(m.from_user.id,"India")
    flag="🇮🇳" if country=="India" else "🇧🇩"
    return f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {name}\n🥉 Plan: Bronze\n💰 Balance: ₹{bal:.2f}\n{flag} Country: {country}\n\n🚀 Select an option below to get started:"

@bot.message_handler(commands=['start'])
def s(m):
    uid=m.from_user.id
    if uid not in user_country:
        # New user - ask country
        if uid not in user_balance:
            user_balance[uid]=0.00
        bot.send_message(m.chat.id, f"👋 Hi {m.from_user.first_name}!\n\n🌍 Please select your country first:", reply_markup=country_kb())
    else:
        # Old user - direct welcome
        bot.send_message(m.chat.id, welcome(m), reply_markup=main_kb())

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid=c.from_user.id
    d=c.data
    
    # Country Select
    if d.startswith("country_"):
        country=d.split("_")[1]
        user_country[uid]=country
        bot.edit_message_text(f"✅ Country set to {country}!", c.message.chat.id, c.message.message_id)
        # Now show main menu
        bot.send_message(c.message.chat.id, welcome(c.from_user), reply_markup=main_kb())
        bot.answer_callback_query(c.id, f"Selected {country}")
        return

    if d.startswith("buy_"):
        p=d.split("_")[1]; price=PRICE[p]; bal=user_balance.get(uid,0)
        if bal<price:
            bot.answer_callback_query(c.id, f"❌ Low Balance Need ₹{price}", show_alert=True)
            return
        if not stock[p]:
            bot.answer_callback_query(c.id, "⚠️ Stock Empty", show_alert=True)
            return
        user_balance[uid]=bal-price
        f=stock[p].pop(0)
        bot.send_message(c.message.chat.id, f"✅ Bought {p}!\nFile: {f}\nBal: ₹{user_balance[uid]:.2f}")
    elif d=="stock":
        t="📦 TOTAL STOCK 📦\n\n"
        for k,v in stock.items(): t+=f"🔥 {k} Days : {len(v)} Keys\n"
        bot.send_message(c.message.chat.id, t)
    elif d=="bal":
        bot.send_message(c.message.chat.id, f"💰 Balance: ₹{user_balance.get(uid,0):.2f}")
    elif d=="addfunds":
        bot.send_message(c.message.chat.id, f"💳 Add Funds\nYour ID: {uid}\nContact Admin")
    elif d=="getfiles":
        bot.send_message(c.message.chat.id, "📁 No files yet. Buy first.")
    bot.answer_callback_query(c.id)

@bot.message_handler(commands=['addstock'])
def ast(m):
    if m.from_user.id!=ADMIN_ID: return
    try:
        a=m.text.split(" ",2); stock[a[1].upper()].append(a[2])
        bot.reply_to(m, f"✅ Added. Total {len(stock[a[1].upper()])}")
    except: bot.reply_to(m, "Use: /addstock 1D filelink")

@bot.message_handler(commands=['addbalance'])
def ab(m):
    if m.from_user.id!=ADMIN_ID: return
    try:
        a=m.text.split(); uid=int(a[1]); amt=float(a[2])
        user_balance[uid]=user_balance.get(uid,0)+amt
        bot.reply_to(m, f"✅ Added ₹{amt} to {uid}")
        bot.send_message(uid, f"💰 Admin added ₹{amt}! New Bal ₹{user_balance[uid]:.2f}")
    except: bot.reply_to(m, "Use: /addbalance ID AMOUNT")

def run(): app.run(host="0.0.0.0",port=10000)
threading.Thread(target=run,daemon=True).start()
bot.infinity_polling()

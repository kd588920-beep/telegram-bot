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
    m.add(types.InlineKeyboardButton("🇮🇳 India", callback_data="country_India"), types.InlineKeyboardButton("🇧🇩 Bangladesh", callback_data="country_Bangladesh"))
    return m

def main_kb():
    m=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    m.add(types.KeyboardButton("🩸 Buy 1 Days"), types.KeyboardButton("🩸 Buy 3 Days"))
    m.add(types.KeyboardButton("🩸 Buy 7 Days"), types.KeyboardButton("🩸 Buy 15 Days"))
    m.add(types.KeyboardButton("🩸 Buy 30 Days"), types.KeyboardButton("📦 Stock"))
    m.add(types.KeyboardButton("➕ Add Funds"), types.KeyboardButton("💰 Balance"))
    m.add(types.KeyboardButton("📁 Get Files"))
    return m

def welcome(m):
    bal=user_balance.get(m.from_user.id,0.00)
    country=user_country.get(m.from_user.id,"India")
    flag="🇮🇳" if country=="India" else "🇧🇩"
    plan="Vip 👑 VIP/Reseller" if m.from_user.id==ADMIN_ID else "Bronze"
    return f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Name: {m.from_user.first_name}\n👑 Plan: {plan}\n💰 Balance: ₹{bal:.2f}\n{flag} Country: {country}\n\n🚀 Select an option below to get started:"

@bot.message_handler(commands=['start'])
def s(m):
    uid=m.from_user.id
    if uid not in user_country:
        if uid not in user_balance: user_balance[uid]=0.00
        bot.send_message(m.chat.id, f"🌍 Please select your country:", reply_markup=country_kb())
    else:
        bot.send_message(m.chat.id, welcome(m), reply_markup=main_kb())

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid=c.from_user.id
    if c.data.startswith("country_"):
        user_country[uid]=c.data.split("_")[1]
        bot.edit_message_text(f"✅ Country set to {user_country[uid]}!", c.message.chat.id, c.message.message_id)
        bot.send_message(c.message.chat.id, welcome(c.from_user), reply_markup=main_kb())
        bot.answer_callback_query(c.id)
        return
    bot.answer_callback_query(c.id)

@bot.message_handler(func=lambda m: m.text and "Buy" in m.text)
def buy(m):
    uid=m.from_user.id
    p="1D" if "1 Days" in m.text else "3D" if "3 Days" in m.text else "7D" if "7 Days" in m.text else "15D" if "15 Days" in m.text else "30D"
    price=PRICE[p]; bal=user_balance.get(uid,0)
    if bal<price:
        bot.reply_to(m, f"❌ Low Balance Need ₹{price}")
        return
    if not stock[p]:
        bot.reply_to(m, "⚠️ Stock Empty")
        return
    user_balance[uid]=bal-price
    f=stock[p].pop(0)
    bot.reply_to(m, f"✅ Bought {p}!\nFile: {f}\nBal: ₹{user_balance[uid]:.2f}")

# ***** EITA HOLO TOMAR CHAOA STOCK DESIGN *****
@bot.message_handler(func=lambda m: m.text=="📦 Stock")
def st(m):
    c1=len(stock["1D"]); c3=len(stock["3D"]); c7=len(stock["7D"]); c15=len(stock["15D"]); c30=len(stock["30D"])
    
    def line(count):
        if count>0:
            return f"✅"
        else:
            return f"❌"
    
    text = f"📦 Live Stock Status\n"
    text += f"━━━━━━━━━━━━━━━━━━━━\n\n"
    text += f"🎯 CARROM\n"
    text += f"{line(c1)} 1 Days: {c1} keys\n"
    text += f"{line(c3)} 3 Days: {c3} keys\n"
    text += f"{line(c7)} 7 Days: {c7} keys\n"
    text += f"{line(c15)} 15 Days: {c15} keys\n"
    text += f"{line(c30)} 30 Days: {c30} keys\n\n"
    text += f"🎱 8 BALL POOL\n"
    text += f"❌ 1 Days: 0 keys\n"
    text += f"❌ 3 Days: 0 keys\n"
    text += f"❌ 7 Days: 0 keys\n"
    text += f"❌ 15 Days: 0 keys\n"
    text += f"❌ 30 Days: 0 keys\n"
    
    bot.send_message(m.chat.id, text)

@bot.message_handler(func=lambda m: m.text=="💰 Balance")
def bl(m): bot.send_message(m.chat.id, f"💰 Balance: ₹{user_balance.get(m.from_user.id,0):.2f}")

@bot.message_handler(func=lambda m: m.text=="➕ Add Funds")
def af(m): bot.send_message(m.chat.id, f"💳 Add Funds ID: {m.from_user.id}")

@bot.message_handler(func=lambda m: m.text=="📁 Get Files")
def gf(m): bot.send_message(m.chat.id, "📁 No files yet")

@bot.message_handler(commands=['addstock'])
def ast(m):
    if m.from_user.id!=ADMIN_ID: return
    try:
        a=m.text.split(" ",2); stock[a[1].upper()].append(a[2])
        bot.reply_to(m, f"✅ Added. CARROM {a[1]} now {len(stock[a[1].upper()])} keys")
    except: bot.reply_to(m, "Use /addstock 1D link")

@bot.message_handler(commands=['addbalance'])
def ab(m):
    if m.from_user.id!=ADMIN_ID: return
    try:
        a=m.text.split(); uid=int(a[1]); amt=float(a[2])
        user_balance[uid]=user_balance.get(uid,0)+amt
        bot.reply_to(m, f"Added ₹{amt} to {uid}")
        bot.send_message(uid, f"💰 Added ₹{amt}! Bal ₹{user_balance[uid]:.2f}")
    except: bot.reply_to(m, "Use /addbalance ID AMOUNT")

def run(): app.run(host="0.0.0.0",port=10000)
threading.Thread(target=run,daemon=True).start()
bot.infinity_polling()

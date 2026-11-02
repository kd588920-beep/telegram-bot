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
    global user_balance, user_country, user_plan, stock_carrom, stock_8ball
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

PRICE={"1D":70,"3D":150,"7D":300,"15D":550,"30D":1000}

stock_carrom={"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
stock_8ball={"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
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
    m.add(types.InlineKeyboardButton("🇮🇳 India", callback_data="country_India"))
    m.add(types.InlineKeyboardButton("🇧🇩 Bangladesh", callback_data="country_Bangladesh"))
    return m

def main_kb():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add(types.KeyboardButton("👑 Buy 1 Days"),types.KeyboardButton("👑 Buy 3 Days"))
    m.add(types.KeyboardButton("👑 Buy 7 Days"),types.KeyboardButton("👑 Buy 15 Days"))
    m.add(types.KeyboardButton("👑 Buy 30 Days"),types.KeyboardButton("📦 Stock"))
    m.add(types.KeyboardButton("➕ Add Funds"),types.KeyboardButton("💰 Balance"))
    m.add(types.KeyboardButton("📁 Get Files"))
    return m

def admin_kb():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add(types.KeyboardButton("➕ Add Stock"),types.KeyboardButton("➖ Delete Stock"))
    m.add(types.KeyboardButton("👑 Make VIP"),types.KeyboardButton("💎 Make Reseller"))
    m.add(types.KeyboardButton("❌ Cancel VIP"),types.KeyboardButton("❌ Cancel Reseller"))
    m.add(types.KeyboardButton("📦 Check Stock"),types.KeyboardButton("👥 Users List"))
    m.add(types.KeyboardButton("🔙 Back to Main"))
    return m

def welcome_text(uid):
    uid_str=str(uid)
    bal=user_balance.get(uid_str,0)
    country=user_country.get(uid_str,"India")
    flag="🇮🇳" if country=="India" else "🇧🇩"
    plan="👑 BOSS" if str(uid)==str(ADMIN_ID) else user_plan.get(uid_str,"Free User")
    return f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Plan: {plan}\n💰 Balance: ₹{bal}\n{flag} Country: {country}\n\n🚀 Select an option"

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
    if "India" in c.data: user_country[uid]="India"
    elif "Bangladesh" in c.data: user_country[uid]="Bangladesh"
    save_data()
    bot.send_message(c.message.chat.id,welcome_text(c.from_user.id),reply_markup=main_kb())
    bot.answer_callback_query(c.id)

# --- USER BUTTONS ---
@bot.message_handler(func=lambda m: m.text=="📦 Stock")
def stock_handler(m):
    txt="📦 Live Stock\n━━━━━━━━━━━━\n\n🎯 CARROM\n"
    for d in ["1D","3D","7D","15D","30D"]:
        txt+=f"{'✅' if len(stock_carrom.get(d,[]))>0 else '❌'} {d} : {len(stock_carrom.get(d,[]))} keys\n"
    txt+="\n🎱 8 BALL\n"
    for d in ["1D","3D","7D","15D","30D"]:
        txt+=f"{'✅' if len(stock_8ball.get(d,[]))>0 else '❌'} {d} : {len(stock_8ball.get(d,[]))} keys\n"
    bot.send_message(m.chat.id, txt)

@bot.message_handler(func=lambda m: m.text=="💰 Balance")
def bal_handler(m):
    bot.send_message(m.chat.id, f"💰 Balance: ₹{user_balance.get(str(m.from_user.id),0)}")

# --- ADMIN PANEL ---
@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.from_user.id==ADMIN_ID:
        bot.send_message(m.chat.id, "👑 **BOSS ADMIN PANEL**\n\n✅ Admin OK BOSS\n\nNiche theke select koro:", reply_markup=admin_kb(), parse_mode="Markdown")
    else:
        bot.send_message(m.chat.id, f"❌ Not BOSS! ID: {m.from_user.id}")

@bot.message_handler(func=lambda m: m.text=="➕ Add Stock")
def add_stock_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    bot.send_message(m.chat.id, "📝 **Add Stock Format:**\n\n`/addstock CARROM 1D KEY-123`\n`/addstock 8BALL 7D 8BALL-KEY`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text=="➖ Delete Stock")
def del_stock_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    bot.send_message(m.chat.id, "🗑️ **Delete Format:**\n\n`/delstock CARROM 1D KEY-123`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text=="👑 Make VIP")
def make_vip_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    bot.send_message(m.chat.id, "👑 **Make VIP:**\n\n`/makevip USER_ID`")

@bot.message_handler(func=lambda m: m.text=="💎 Make Reseller")
def make_reseller_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    bot.send_message(m.chat.id, "💎 **Make Reseller:**\n\n`/makereseller USER_ID`")

@bot.message_handler(func=lambda m: m.text=="❌ Cancel VIP")
def cancel_vip_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    bot.send_message(m.chat.id, "❌ **Cancel VIP:**\n\n`/cancelvip USER_ID`")

@bot.message_handler(func=lambda m: m.text=="❌ Cancel Reseller")
def cancel_reseller_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    bot.send_message(m.chat.id, "❌ **Cancel Reseller:**\n\n`/cancelreseller USER_ID`")

@bot.message_handler(func=lambda m: m.text=="📦 Check Stock")
def check_stock_admin(m):
    if m.from_user.id!=ADMIN_ID: return
    stock_handler(m)

@bot.message_handler(func=lambda m: m.text=="👥 Users List")
def users_list(m):
    if m.from_user.id!=ADMIN_ID: return
    txt=f"👥 Total Users: {len(user_balance)}\n\n"
    for uid, plan in list(user_plan.items())[:20]:
        txt+=f"{uid} : {plan}\n"
    bot.send_message(m.chat.id, txt)

@bot.message_handler(func=lambda m: m.text=="🔙 Back to Main")
def back_main(m):
    bot.send_message(m.chat.id, welcome_text(m.from_user.id), reply_markup=main_kb())

# --- ADMIN COMMANDS ---
@bot.message_handler(commands=['addstock'])
def addstock_cmd(m):
    if m.from_user.id!=ADMIN_ID: return
    try:
        parts=m.text.split(" ",3)
        game=parts[1].upper(); day=parts[2].upper(); key=parts[3]
        if "CARROM" in game: stock_carrom[day].append(key)
        else: stock_8ball[day].append(key)
        save_data()
        bot.reply_to(m, f"✅ Added {game} {day}\n🔑 {key}\n📦 Total: {len(stock_carrom[day]) if 'CARROM' in game else len(stock_8ball[day])}")
    except:
        bot.reply_to(m, "Use: /addstock CARROM 1D KEY")

@bot.message_handler(commands=['delstock'])
def delstock_cmd(m):
    if m.from_user.id!=ADMIN_ID: return
    try:
        parts=m.text.split(" ",3)
        game=parts[1].upper(); day=parts[2].upper(); key=parts[3]
        if "CARROM" in game and key in stock_carrom[day]: stock_carrom[day].remove(key)
        elif key in stock_8ball[day]: stock_8ball[day].remove(key)
        save_data()
        bot.reply_to(m, f"✅ Deleted {key}")
    except:
        bot.reply_to(m, "Use: /delstock CARROM 1D KEY")

@bot.message_handler(commands=['makevip'])
def makevip_cmd(m):
    if m.from_user.id!=ADMIN_ID: return
    try:
        uid=m.text.split(" ")[1]
        user_plan[str(uid)]="VIP 👑 VIP"
        save_data()
        bot.reply_to(m, f"✅ {uid} ke VIP banano holo!")
    except:
        bot.reply_to(m, "Use: /makevip USER_ID")

@bot.message_handler(commands=['makereseller'])
def makereseller_cmd(m):
    if m.from_user.id!=ADMIN_ID: return
    try:
        uid=m.text.split(" ")[1]
        user_plan[str(uid)]="Reseller 💎"
        save_data()
        bot.reply_to(m, f"✅ {uid} ke Reseller banano holo!")
    except:
        bot.reply_to(m, "Use: /makereseller USER_ID")

@bot.message_handler(commands=['cancelvip','cancelreseller'])
def cancel_cmd(m):
    if m.from_user.id!=ADMIN_ID: return
    try:
        uid=m.text.split(" ")[1]
        user_plan[str(uid)]="Free User"
        save_data()
        bot.reply_to(m, f"✅ {uid} er VIP/Reseller cancel kora holo! Free kore dilam!")
    except:
        bot.reply_to(m, "Use: /cancelvip USER_ID")

def run_flask():
    app.run(host="0.0.0.0",port=10000)

threading.Thread(target=run_flask,daemon=True).start()
print("✅ SHINIGAMI Bot Starting...")
bot.infinity_polling()

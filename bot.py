import os, json, threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN=os.environ.get("BOT_TOKEN")
ADMIN_ID=7189081595

stock_carrom={"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
stock_8ball={"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
user_balance={}; user_country={}; user_plan={}; pending_add={}

def save_data():
    with open("data.json","w") as f:
        json.dump({"bal":user_balance,"country":user_country,"plan":user_plan,"carrom":stock_carrom,"ball":stock_8ball},f)

def load_data():
    global user_balance,user_country,user_plan,stock_carrom,stock_8ball
    try:
        with open("data.json","r") as f:
            d=json.load(f); user_balance=d.get("bal",{}); user_country=d.get("country",{})
            user_plan=d.get("plan",{}); stock_carrom=d.get("carrom",stock_carrom); stock_8ball=d.get("ball",stock_8ball)
    except: pass

load_data()
bot=telebot.TeleBot(BOT_TOKEN)
app=Flask(__name__)
@app.route('/')
def home(): return "SHINIGAMI FINAL OK"

def get_stock_text():
    txt="🎯 CARROM\n"
    for d in ["1D","3D","7D","15D","30D"]:
        c=len(stock_carrom.get(d,[])); txt+=f"{'✅' if c>0 else '❌'} {d} : {c} keys\n"
    txt+="\n🎱 8 BALL\n"
    for d in ["1D","3D","7D","15D","30D"]:
        c=len(stock_8ball.get(d,[])); txt+=f"{'✅' if c>0 else '❌'} {d} : {c} keys\n"
    return txt

def country_kb():
    m=types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🇮🇳 India",callback_data="country_India"),types.InlineKeyboardButton("🇧🇩 Bangladesh",callback_data="country_Bangladesh")); return m

def main_kb():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add(types.KeyboardButton("👑 Buy 1 Days"),types.KeyboardButton("👑 Buy 3 Days"))
    m.add(types.KeyboardButton("👑 Buy 7 Days"),types.KeyboardButton("👑 Buy 15 Days"))
    m.add(types.KeyboardButton("👑 Buy 30 Days"),types.KeyboardButton("📦 Stock"))
    m.add(types.KeyboardButton("➕ Add Funds"),types.KeyboardButton("💰 Balance")); return m

def admin_kb():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add(types.KeyboardButton("➕ Add Stock"),types.KeyboardButton("➖ Delete Stock"))
    m.add(types.KeyboardButton("👑 Make VIP"),types.KeyboardButton("💎 Make Reseller"))
    m.add(types.KeyboardButton("❌ Cancel VIP"),types.KeyboardButton("❌ Cancel Reseller"))
    m.add(types.KeyboardButton("📦 Check Stock"),types.KeyboardButton("👥 Users List"))
    m.add(types.KeyboardButton("🔙 Back to Main")); return m

def add_stock_inline_kb():
    m=types.InlineKeyboardMarkup(row_width=3)
    m.add(types.InlineKeyboardButton("CARROM 1D",callback_data="addsel_CARROM_1D"),types.InlineKeyboardButton("CARROM 3D",callback_data="addsel_CARROM_3D"),types.InlineKeyboardButton("CARROM 7D",callback_data="addsel_CARROM_7D"))
    m.add(types.InlineKeyboardButton("CARROM 15D",callback_data="addsel_CARROM_15D"),types.InlineKeyboardButton("CARROM 30D",callback_data="addsel_CARROM_30D"))
    m.add(types.InlineKeyboardButton("8BALL 1D",callback_data="addsel_8BALL_1D"),types.InlineKeyboardButton("8BALL 3D",callback_data="addsel_8BALL_3D"),types.InlineKeyboardButton("8BALL 7D",callback_data="addsel_8BALL_7D"))
    m.add(types.InlineKeyboardButton("8BALL 15D",callback_data="addsel_8BALL_15D"),types.InlineKeyboardButton("8BALL 30D",callback_data="addsel_8BALL_30D")); return m

def welcome_text(uid):
    bal=user_balance.get(str(uid),0); return f"👑 Welcome to SHINIGAMI Bot!\n💰 Balance: ₹{bal}\n🚀 Select option"

@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid=str(m.from_user.id)
    if uid not in user_balance: user_balance[uid]=0.0; save_data()
    if uid not in user_country: bot.send_message(m.chat.id,"🌍 Select country",reply_markup=country_kb())
    else: bot.send_message(m.chat.id,welcome_text(m.from_user.id),reply_markup=main_kb())

@bot.callback_query_handler(func=lambda c: True)
def cb_handler(c):
    uid=str(c.from_user.id); data=c.data
    if data.startswith("country_"):
        user_country[uid]="India" if "India" in data else "Bangladesh"; save_data()
        bot.send_message(c.message.chat.id,welcome_text(c.from_user.id),reply_markup=main_kb()); bot.answer_callback_query(c.id); return
    if data.startswith("addsel_"):
        if c.from_user.id!=ADMIN_ID: return
        _,game,day=data.split("_"); pending_add[uid]=(game,day)
        bot.send_message(c.message.chat.id,f"✅ **{game} {day} Select Kiya BOSS!**\n\n🔑 **Abb key add kro BOSS!**",parse_mode="Markdown"); bot.answer_callback_query(c.id)

@bot.message_handler(func=lambda m: m.text and "Check Stock" in m.text)
def check_stock(m):
    bot.send_message(m.chat.id,get_stock_text())

@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.from_user.id==ADMIN_ID: bot.send_message(m.chat.id,"👑 BOSS ADMIN PANEL",reply_markup=admin_kb())

@bot.message_handler(func=lambda m: m.text=="➕ Add Stock")
def add_stock_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    bot.send_message(m.chat.id,"👇 **Kaunsa Add Karoge BOSS?**",reply_markup=add_stock_inline_kb(),parse_mode="Markdown")

@bot.message_handler(func=lambda m: str(m.from_user.id) in pending_add)
def pending_handler(m):
    if m.from_user.id!=ADMIN_ID: return
    uid=str(m.from_user.id)
    if uid not in pending_add: return
    if "Add Stock" in m.text or "Check Stock" in m.text or "Delete Stock" in m.text: return
    game,day=pending_add[uid]; keys=m.text.strip().split("\n"); added=0
    for k in keys:
        k=k.strip()
        if not k: continue
        if "CARROM" in game: stock_carrom[day].append(k)
        else: stock_8ball[day].append(k)
        added+=1
    save_data(); del pending_add[uid]
    total=len(stock_carrom[day]) if "CARROM" in game else len(stock_8ball[day])
    bot.send_message(m.chat.id,f"✅ **SUCCESS BOSS! {game} {day} Added**\n🔑 Added: {added} keys\n📊 Total {day}: {total} keys",parse_mode="Markdown")
    bot.send_message(m.chat.id,"👇 **Aab Kaunsa Add Karoge BOSS?**",reply_markup=add_stock_inline_kb(),parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def all_msg(m):
    if m.text=="🔙 Back to Main": bot.send_message(m.chat.id,welcome_text(m.from_user.id),reply_markup=main_kb())

def run_flask(): app.run(host="0.0.0.0",port=10000)
threading.Thread(target=run_flask,daemon=True).start()
bot.infinity_polling()

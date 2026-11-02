import os, json, threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7189081595

stock_carrom = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
stock_8ball = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
user_balance = {}; user_country = {}; user_plan = {}; pending_add = {}

def save_data():
    with open("data.json","w") as f:
        json.dump({"bal":user_balance,"country":user_country,"plan":user_plan,"carrom":stock_carrom,"ball":stock_8ball},f)

def load_data():
    global user_balance,user_country,user_plan,stock_carrom,stock_8ball
    try:
        with open("data.json","r") as f:
            d=json.load(f)
            user_balance=d.get("bal",{}); user_country=d.get("country",{}); user_plan=d.get("plan",{})
            stock_carrom=d.get("carrom",stock_carrom); stock_8ball=d.get("ball",stock_8ball)
    except: pass

load_data()
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
@app.route('/')
def home(): return "SHINIGAMI STOCK FINAL OK"

def get_stock_text():
    txt="🎯 CARROM\n"
    for d in ["1D","3D","7D","15D","30D"]:
        c=len(stock_carrom.get(d,[])); txt+=f"{'❌' if c==0 else '✅'} {d} : {c} keys\n"
    txt+="\n🎱 8 BALL\n"
    for d in ["1D","3D","7D","15D","30D"]:
        c=len(stock_8ball.get(d,[])); txt+=f"{'❌' if c==0 else '✅'} {d} : {c} keys\n"
    return txt

def country_kb():
    m=types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🇮🇳 India",callback_data="country_India"))
    m.add(types.InlineKeyboardButton("🇧🇩 Bangladesh",callback_data="country_Bangladesh"))
    return m

def main_kb():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add(types.KeyboardButton("👑 Buy 1 Days"),types.KeyboardButton("👑 Buy 3 Days"))
    m.add(types.KeyboardButton("👑 Buy 7 Days"),types.KeyboardButton("👑 Buy 15 Days"))
    m.add(types.KeyboardButton("👑 Buy 30 Days"),types.KeyboardButton("📦 Stock"))
    m.add(types.KeyboardButton("➕ Add Funds"),types.KeyboardButton("💰 Balance"))
    return m

def admin_kb():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add(types.KeyboardButton("➕ Add Stock"),types.KeyboardButton("➖ Delete Stock"))
    m.add(types.KeyboardButton("👑 Make VIP"),types.KeyboardButton("💎 Make Reseller"))
    m.add(types.KeyboardButton("❌ Cancel VIP"),types.KeyboardButton("❌ Cancel Reseller"))
    m.add(types.KeyboardButton("📦 Check Stock"),types.KeyboardButton("👥 Users List"))
    m.add(types.KeyboardButton("🔙 Back to Main"))
    return m

def add_stock_inline_kb():
    m=types.InlineKeyboardMarkup(row_width=3)
    m.add(types.InlineKeyboardButton("CARROM 1D",callback_data="addsel_CARROM_1D"),types.InlineKeyboardButton("CARROM 3D",callback_data="addsel_CARROM_3D"),types.InlineKeyboardButton("CARROM 7D",callback_data="addsel_CARROM_7D"))
    m.add(types.InlineKeyboardButton("CARROM 15D",callback_data="addsel_CARROM_15D"),types.InlineKeyboardButton("CARROM 30D",callback_data="addsel_CARROM_30D"))
    m.add(types.InlineKeyboardButton("8BALL 1D",callback_data="addsel_8BALL_1D"),types.InlineKeyboardButton("8BALL 3D",callback_data="addsel_8BALL_3D"),types.InlineKeyboardButton("8BALL 7D",callback_data="addsel_8BALL_7D"))
    m.add(types.InlineKeyboardButton("8BALL 15D",callback_data="addsel_8BALL_15D"),types.InlineKeyboardButton("8BALL 30D",callback_data="addsel_8BALL_30D"))
    return m

def welcome_text(uid):
    uid=str(uid); bal=user_balance.get(uid,0); country=user_country.get(uid,"India")
    plan_text="👑 BOSS" if str(uid)==str(ADMIN_ID) else ("👑 VIP" if user_plan.get(uid)=="VIP" else "💎 RESELLER" if user_plan.get(uid)=="RESELLER" else "👤 FREE")
    return f"👑 Welcome to SHINIGAMI Bot!\n\n👤 Plan: {plan_text}\n💰 Balance: ₹{bal}\n🇮🇳 Country: {country}\n\n🚀 Select an option"

# ✅ /start e pending clear korbe jate Stock atke na thake
@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid=str(m.from_user.id)
    if uid in pending_add: del pending_add[uid]
    if uid not in user_balance: user_balance[uid]=0.0; save_data()
    if uid not in user_country:
        bot.send_message(m.chat.id,"🌍 Select country",reply_markup=country_kb())
    else:
        if str(m.from_user.id)==str(ADMIN_ID): user_plan[uid]="BOSS"; save_data()
        bot.send_message(m.chat.id,welcome_text(m.from_user.id),reply_markup=main_kb())

@bot.callback_query_handler(func=lambda c: True)
def cb_handler(c):
    uid=str(c.from_user.id); data=c.data
    if data.startswith("country_"):
        user_country[uid]="India" if "India" in data else "Bangladesh"
        if str(c.from_user.id)==str(ADMIN_ID): user_plan[uid]="BOSS"
        save_data()
        bot.send_message(c.message.chat.id,welcome_text(c.from_user.id),reply_markup=main_kb())
        bot.answer_callback_query(c.id); return
    if data.startswith("addsel_"):
        if c.from_user.id!=ADMIN_ID: return
        _,game,day=data.split("_"); pending_add[uid]=(game,day)
        bot.send_message(c.message.chat.id,f"✅ **{game} {day} Select Kiya BOSS!**\n\n🔑 **Abb key add kro BOSS!**",parse_mode="Markdown")
        bot.answer_callback_query(c.id)

# ✅ STOCK FIX - MAIN + ADMIN 2TOI JONNO
@bot.message_handler(func=lambda m: m.text and "Stock" in m.text)
def stock_handler(m):
    uid=str(m.from_user.id)
    if uid in pending_add: del pending_add[uid]
    bot.send_message(m.chat.id,get_stock_text())

@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.from_user.id==ADMIN_ID:
        user_plan[str(m.from_user.id)]="BOSS"; save_data()
        bot.send_message(m.chat.id,"👑 BOSS ADMIN PANEL\n\n✅ Admin OK BOSS\n\nNiche theke select koro:",reply_markup=admin_kb())

@bot.message_handler(func=lambda m: m.text=="➕ Add Stock")
def add_stock_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    bot.send_message(m.chat.id,"👇 **Kaunsa Add Karoge BOSS?**",reply_markup=add_stock_inline_kb(),parse_mode="Markdown")

@bot.message_handler(func=lambda m: str(m.from_user.id) in pending_add)
def pending_handler(m):
    if m.from_user.id!=ADMIN_ID: return
    uid=str(m.from_user.id)
    if uid not in pending_add: return
    txt=m.text or ""
    # Jodi menu button hoy tahole key hisebe dhorbe na
    if any(x in txt for x in ["Add Stock","Check Stock","Delete Stock","Make VIP","Reseller","Cancel","Back to Main","Users List","Buy","Balance","Add Funds","/start","/admin"]):
        if "Stock" in txt:
            bot.send_message(m.chat.id,get_stock_text())
        return
    game,day=pending_add[uid]; keys=txt.strip().split("\n"); added=0
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

@bot.message_handler(func=lambda m: m.text and "Balance" in m.text)
def bal_cmd(m):
    uid=str(m.from_user.id); bal=user_balance.get(uid,0)
    bot.send_message(m.chat.id,f"💰 Balance: ₹{bal}")

@bot.message_handler(func=lambda m: m.text and "Back to Main" in m.text)
def back_main(m):
    uid=str(m.from_user.id)
    if uid in pending_add: del pending_add[uid]
    bot.send_message(m.chat.id,welcome_text(m.from_user.id),reply_markup=main_kb())

def run_flask(): app.run(host="0.0.0.0",port=10000)
threading.Thread(target=run_flask,daemon=True).start()
bot.infinity_polling()

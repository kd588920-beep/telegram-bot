import os, json, threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7189081595
stock_carrom = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
stock_8ball = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
user_balance = {}; user_country = {}; user_plan = {}
pending_add = {}; pending_admin = {}; pending_buy = {}
vip_mode_users = set()
price = {"1D":60,"3D":130,"7D":180,"15D":350,"30D":570}
vip_price = {"1D":40,"3D":80,"7D":110,"15D":210,"30D":320}

def save_data():
    try:
        with open("data.json","w") as f:
            json.dump({"bal":user_balance,"country":user_country,"plan":user_plan,"carrom":stock_carrom,"ball":stock_8ball},f)
    except: pass
def load_data():
    global user_balance,user_country,user_plan,stock_carrom,stock_8ball
    try:
        with open("data.json","r") as f:
            d=json.load(f); user_balance=d.get("bal",{}); user_country=d.get("country",{}); user_plan=d.get("plan",{}); stock_carrom=d.get("carrom",stock_carrom); stock_8ball=d.get("ball",stock_8ball)
    except: pass
load_data()
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
@app.route('/')
def home(): return "KOUSHIK BOT LIVE - BOSS MODE"
def get_price(uid, day):
    s=str(uid)
    if s==str(ADMIN_ID) and s in vip_mode_users: return vip_price[day], "Vip"
    if s==str(ADMIN_ID): return price[day], "BOSS"
    if user_plan.get(s,"FREE") in ["VIP","RESELLER"]: return vip_price[day], "Vip"
    return price[day], "FREE"
def price_list_text(uid):
    s=str(uid) if uid else "0"
    if s==str(ADMIN_ID) and s in vip_mode_users: p=vip_price; medal="VIP MODE"
    elif s==str(ADMIN_ID): p=price; medal="BOSS MODE"
    elif user_plan.get(s,"FREE") in ["VIP","RESELLER"]: p=vip_price; medal="VIP"
    else: p=price; medal="FREE"
    return f"🎯 CARROM\nMedal: {medal}\nPrice:\n1D - ₹{p['1D']}\n3D - ₹{p['3D']}\n7D - ₹{p['7D']}\n15D - ₹{p['15D']}\n30D - ₹{p['30D']}"
    def get_stock_text():
    txt="📦 Stock\nCARROM\n"
    for d in ["1D","3D","7D","15D","30D"]: txt+=f"{d}: {len(stock_carrom.get(d,[]))}\n"
    txt+="\n8 BALL\n"
    for d in ["1D","3D","7D","15D","30D"]: txt+=f"{d}: {len(stock_8ball.get(d,[]))}\n"
    return txt
def main_kb():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2); m.add(types.KeyboardButton("👑 Buy 1 Days"),types.KeyboardButton("👑 Buy 3 Days")); m.add(types.KeyboardButton("👑 Buy 7 Days"),types.KeyboardButton("👑 Buy 15 Days")); m.add(types.KeyboardButton("👑 Buy 30 Days"),types.KeyboardButton("📦 Stock")); m.add(types.KeyboardButton("💰 Balance")); return m
def admin_kb():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2); m.add(types.KeyboardButton("➕ Add Stock"),types.KeyboardButton("📦 Check Stock")); m.add(types.KeyboardButton("🔙 Back to Main")); return m
def add_stock_inline_kb():
    m=types.InlineKeyboardMarkup(row_width=3); m.add(types.InlineKeyboardButton("CARROM 1D",callback_data="addsel_CARROM_1D"),types.InlineKeyboardButton("CARROM 3D",callback_data="addsel_CARROM_3D")); m.add(types.InlineKeyboardButton("CARROM 7D",callback_data="addsel_CARROM_7D")); m.add(types.InlineKeyboardButton("CARROM 15D",callback_data="addsel_CARROM_15D"),types.InlineKeyboardButton("CARROM 30D",callback_data="addsel_CARROM_30D")); return m
def buy_game_kb(day):
    m=types.InlineKeyboardMarkup(); m.add(types.InlineKeyboardButton(f"CARROM {day}",callback_data=f"buy_CARROM_{day}")); return m
def confirm_kb():
    m=types.InlineKeyboardMarkup(row_width=2); m.add(types.InlineKeyboardButton("✅ Confirm",callback_data="confirm_yes"),types.InlineKeyboardButton("❌ Cancel",callback_data="confirm_no")); return m
@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid=str(m.from_user.id)
    if uid not in user_balance: user_balance[uid]=0.0; save_data()
    bot.send_message(m.chat.id,f"Welcome! {price_list_text(m.from_user.id)}",reply_markup=main_kb())
@bot.message_handler(commands=['price'])
def price_cmd(m): bot.send_message(m.chat.id, price_list_text(m.from_user.id))
@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.from_user.id==ADMIN_ID: bot.send_message(m.chat.id,"ADMIN",reply_markup=admin_kb())
@bot.callback_query_handler(func=lambda c: True)
def cb_handler(c):
    uid=str(c.from_user.id); data=c.data
    if data.startswith("addsel_"):
        if c.from_user.id!=ADMIN_ID: return
        _,game,day=data.split("_"); pending_add[uid]=(game,day); bot.send_message(c.message.chat.id,f"{game} {day} Selected! Send keys!"); return
    if data.startswith("buy_"):
        _,game,day=data.split("_"); stock_list=stock_carrom.get(day,[]) if "CARROM" in game else stock_8ball.get(day,[]); p, ptype = get_price(c.from_user.id, day)
        if len(stock_list)==0: bot.send_message(c.message.chat.id,f"{game} {day} Out of Stock!"); return
        pending_buy[uid]=(game,day); bot.send_message(c.message.chat.id,f"Confirm {game} ₹{p} ({ptype})",reply_markup=confirm_kb()); return
    if data=="confirm_yes":
        if uid not in pending_buy: return
        game,day=pending_buy[uid]; p,_=get_price(c.from_user.id, day); bal=user_balance.get(uid,0); stock_list=stock_carrom.get(day,[]) if "CARROM" in game else stock_8ball.get(day,[])
        if bal < p or len(stock_list)==0: bot.send_message(c.message.chat.id,"Failed! Low bal"); del pending_buy[uid]; return
        key=stock_list.pop(0); user_balance[uid]=bal-p
        if "CARROM" in game: stock_carrom[day]=stock_list
        else: stock_8ball[day]=stock_list
        save_data(); del pending_buy[uid]; bot.send_message(c.message.chat.id,f"Success! Key: {key}"); return
@bot.message_handler(func=lambda m: m.text and m.text.lower().strip()=="vip")
def vip_on(m):
    if m.from_user.id!=ADMIN_ID: return
    vip_mode_users.add(str(m.from_user.id)); bot.send_message(m.chat.id,f"VIP ON\n{price_list_text(m.from_user.id)}")
@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["normal","boss"])
def normal_on(m):
    if m.from_user.id!=ADMIN_ID: return
    vip_mode_users.discard(str(m.from_user.id)); bot.send_message(m.chat.id,f"BOSS MODE ₹60\n{price_list_text(m.from_user.id)}")
@bot.message_handler(func=lambda m: m.text and "Add Stock" in m.text)
def add_stock_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    bot.send_message(m.chat.id,"Select",reply_markup=add_stock_inline_kb())
@bot.message_handler(func=lambda m: m.text and "Stock" in m.text)
def stock_h(m): bot.send_message(m.chat.id,get_stock_text())
@bot.message_handler(func=lambda m: True)
def all_msg(m):
    uid=str(m.from_user.id)
    if uid in pending_add:
        game,day=pending_add[uid]; keys=[k.strip() for k in m.text.split("\n") if k.strip()!=""]
        if "CARROM" in game: stock_carrom[day].extend(keys)
        else: stock_8ball[day].extend(keys)
        save_data(); del pending_add[uid]; bot.send_message(m.chat.id,f"Added {len(keys)} keys"); return
def run_flask(): app.run(host="0.0.0.0",port=10000)
threading.Thread(target=run_flask,daemon=True).start()
bot.infinity_polling()

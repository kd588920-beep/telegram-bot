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
price = {"1D":60,"3D":130,"7D":180,"15D":350,"30D":570}
vip_price = {"1D":40,"3D":80,"7D":110,"15D":210,"30D":320}
vip_mode_users = set()

def save_data():
    try:
        with open("data.json","w",encoding="utf-8") as f:
            json.dump({"bal":user_balance,"country":user_country,"plan":user_plan,"carrom":stock_carrom,"ball":stock_8ball,"price":price},f,ensure_ascii=False)
    except: pass

def load_data():
    global user_balance,user_country,user_plan,stock_carrom,stock_8ball,price
    try:
        with open("data.json","r",encoding="utf-8") as f:
            d=json.load(f)
            user_balance=d.get("bal",{}); user_country=d.get("country",{})
            user_plan=d.get("plan",{}); stock_carrom=d.get("carrom",stock_carrom)
            stock_8ball=d.get("ball",stock_8ball); price=d.get("price",price)
    except: pass

load_data()
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
@app.route('/')
def home(): return "KOUSHIK LOGO FINAL LIVE"

def get_price(uid, day):
    s=str(uid)
    if s==str(ADMIN_ID):
        if s in vip_mode_users: return vip_price.get(day,price.get(day)), "Vip pricing"
        else: return price.get(day), "Normal pricing (BOSS)"
    if user_plan.get(s,"FREE") in ["VIP","RESELLER"]: return vip_price.get(day,price.get(day)), "Vip pricing"
    return price.get(day), "Normal pricing"

def price_list_text(uid=None):
    s=str(uid) if uid else "0"
    if s==str(ADMIN_ID):
        if s in vip_mode_users: p=vip_price; medal="VIP/Reseller 👑 - /normal e 60"
        else: p=price; medal="FREE (BOSS) 👑 - /vip e 40"
    elif user_plan.get(s,"FREE") in ["VIP","RESELLER"]: p=vip_price; medal="VIP/Reseller 👑"
    else: p=price; medal="FREE"
    return f"🎯 CARROM\n\n👑 Medal: {medal}\n\n📋 Price List\n• 1 Days - Rs.{p['1D']}\n• 3 Days - Rs.{p['3D']}\n• 7 Days - Rs.{p['7D']}\n• 15 Days - Rs.{p['15D']}\n• 30 Days - Rs.{p['30D']}"

def get_stock_text():
    def fmt(d):
        out=""
        for k in ["1D","3D","7D","15D","30D"]:
            c=len(d.get(k,[]))
            name=k.replace("1D","1 Days").replace("3D","3 Days").replace("7D","7 Days").replace("15D","15 Days").replace("30D","30 Days")
            out+=f"{'✅' if c>0 else '❌'} {name}: {c} keys\n"
        return out
    return f"📦 Live Stock Status\n━━━━━━━━━━━━\n\n🎯 CARROM\n{fmt(stock_carrom)}\n🎱 8 BALL POOL\n{fmt(stock_8ball)}"

def country_kb():
    m=types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🇮🇳 India",callback_data="country_India"))
    m.add(types.InlineKeyboardButton("🇧🇩 Bangladesh",callback_data="country_Bangladesh"))
    return m

def main_kb():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add(types.KeyboardButton("🚀 Buy 1 Days"),types.KeyboardButton("🚀 Buy 3 Days"))
    m.add(types.KeyboardButton("🚀 Buy 7 Days"),types.KeyboardButton("🚀 Buy 15 Days"))
    m.add(types.KeyboardButton("🚀 Buy 30 Days"),types.KeyboardButton("📦 Stock"))
    m.add(types.KeyboardButton("➕ Add Funds"),types.KeyboardButton("💰 Balance"))
    m.add(types.KeyboardButton("📁 Get Files"))
    return m

def admin_kb():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add(types.KeyboardButton("➕ Add Stock"),types.KeyboardButton("➖ Delete Stock"))
    m.add(types.KeyboardButton("👑 Make VIP"),types.KeyboardButton("💎 Make Reseller"))
    m.add(types.KeyboardButton("❌ Cancel VIP"),types.KeyboardButton("❌ Cancel Reseller"))
    m.add(types.KeyboardButton("💰 Add Balance"),types.KeyboardButton("💵 Set Price"))
    m.add(types.KeyboardButton("📢 Broadcast"),types.KeyboardButton("📊 Stats"))
    m.add(types.KeyboardButton("📦 Check Stock"),types.KeyboardButton("🔙 Back to Main"))
    return m

def add_stock_inline_kb():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("🎯 CARROM STOCK POLL",callback_data="addsel_GAME_CARROM"))
    m.add(types.InlineKeyboardButton("🎱 8BALL STOCK POLL",callback_data="addsel_GAME_8BALL"))
    return m

def add_stock_carrom_kb():
    m=types.InlineKeyboardMarkup(row_width=3)
    m.add(types.InlineKeyboardButton("🎯 CARROM 1D",callback_data="addsel_CARROM_1D"),types.InlineKeyboardButton("🎯 CARROM 3D",callback_data="addsel_CARROM_3D"),types.InlineKeyboardButton("🎯 CARROM 7D",callback_data="addsel_CARROM_7D"))
    m.add(types.InlineKeyboardButton("🎯 CARROM 15D",callback_data="addsel_CARROM_15D"),types.InlineKeyboardButton("🎯 CARROM 30D",callback_data="addsel_CARROM_30D"))
    m.add(types.InlineKeyboardButton("🔙 Back",callback_data="addsel_BACK"))
    return m

def add_stock_8ball_kb():
    m=types.InlineKeyboardMarkup(row_width=3)
    m.add(types.InlineKeyboardButton("🎱 8BALL 1D",callback_data="addsel_8BALL_1D"),types.InlineKeyboardButton("🎱 8BALL 3D",callback_data="addsel_8BALL_3D"),types.InlineKeyboardButton("🎱 8BALL 7D",callback_data="addsel_8BALL_7D"))
    m.add(types.InlineKeyboardButton("🎱 8BALL 15D",callback_data="addsel_8BALL_15D"),types.InlineKeyboardButton("🎱 8BALL 30D",callback_data="addsel_8BALL_30D"))
    m.add(types.InlineKeyboardButton("🔙 Back",callback_data="addsel_BACK"))
    return m

def buy_game_kb(day):
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton(f"🎯 CARROM {day}",callback_data=f"buy_CARROM_{day}"),types.InlineKeyboardButton(f"🎱 8 BALL {day}",callback_data=f"buy_8BALL_{day}"))
    return m

def confirm_kb():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("✅ Confirm",callback_data="confirm_yes"),types.InlineKeyboardButton("❌ Cancel",callback_data="confirm_no"))
    return m

def welcome_text(uid, first_name=None):
    s=str(uid)
    if not first_name: first_name="User"
    bal=user_balance.get(s,0)
    country=user_country.get(s,"India")
    plan="BOSS" if s==str(ADMIN_ID) else user_plan.get(s,"Bronze")
    a="Welcome to SHINIGAMI Bot!"
    b1=f"Name: {first_name}"
    b2=f"Plan: {plan}"
    b3=f"Balance: Rs.{bal:.2f}"
    b4=f"Country: {country}"
    b5="Select an option below to get started:"
    return chr(10).join(["",a,"",b1,b2,b3,b4,"",b5,""])
@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid=str(m.from_user.id)
    for d in [pending_add,pending_admin,pending_buy]:
        if uid in d: del d[uid]
    if uid not in user_balance: user_balance[uid]=0.0; save_data()
    if uid not in user_country: bot.send_message(m.chat.id,"🌍 Select country",reply_markup=country_kb())
    else:
        if str(m.from_user.id)==str(ADMIN_ID): user_plan[uid]="BOSS"; save_data()
        bot.send_message(m.chat.id,welcome_text(m.from_user.id, m.from_user.first_name),reply_markup=main_kb())

@bot.message_handler(commands=['vip'])
def vip_cmd(m):
    if m.from_user.id!=ADMIN_ID: return
    vip_mode_users.add(str(m.from_user.id))
    bot.send_message(m.chat.id,f"✅ VIP MODE ON 👑\n\n{price_list_text(m.from_user.id)}",reply_markup=main_kb())

@bot.message_handler(commands=['normal','boss'])
def normal_cmd(m):
    if m.from_user.id!=ADMIN_ID: return
    vip_mode_users.discard(str(m.from_user.id))
    bot.send_message(m.chat.id,f"✅ NORMAL MODE ON 👤\n\n{price_list_text(m.from_user.id)}",reply_markup=main_kb())

@bot.message_handler(commands=['price'])
def price_cmd(m): bot.send_message(m.chat.id,price_list_text(m.from_user.id),reply_markup=main_kb())

@bot.message_handler(commands=['support','help'])
def support_cmd(m):
            bot.send_message(m.chat.id, "🎧 Need Help?\n\nContact our admin for support:\n👤 @koushik_098\n\n⏰ We will reply as soon as possible!", reply_markup=main_kb())

@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.from_user.id==ADMIN_ID:
        user_plan[str(m.from_user.id)]="BOSS"; save_data()
        bot.send_message(m.chat.id,"👑 BOSS FULL ADMIN PANEL",reply_markup=admin_kb())

@bot.callback_query_handler(func=lambda c: True)
def cb_handler(c):
    uid=str(c.from_user.id); data=c.data
    if data.startswith("country_"):
        user_country[uid]="Bangladesh" if "Bangladesh" in data else "India"
        if str(c.from_user.id)==str(ADMIN_ID): user_plan[uid]="BOSS"
        save_data()
        try: bot.delete_message(c.message.chat.id,c.message.message_id)
        except:
            try: bot.edit_message_reply_markup(c.message.chat.id,c.message.message_id,reply_markup=None)
            except: pass
        try: bot.answer_callback_query(c.id,f"✅ {user_country[uid]}")
        except: pass
        bot.send_message(c.message.chat.id,welcome_text(c.from_user.id),reply_markup=main_kb()); return
    if data.startswith("addsel_"):
        if c.from_user.id!=ADMIN_ID: return
        _,game,day=data.split("_"); pending_add[uid]=(game,day)
        bot.send_message(c.message.chat.id,f"✅ {game} {day} Selected"); return
    if data.startswith("buy_"):
        _,game,day=data.split("_")
        stock_list=stock_carrom.get(day,[]) if "CARROM" in game else stock_8ball.get(day,[])
        p,_=get_price(c.from_user.id,day)
        if len(stock_list)==0: bot.send_message(c.message.chat.id,f"{game} {day} Out of Stock",reply_markup=main_kb()); return
        pending_buy[uid]=(game,day); bot.send_message(c.message.chat.id,f"🛒 {game} {day} - Rs.{p}",reply_markup=confirm_kb()); return
    if data=="confirm_yes":
        if uid not in pending_buy: return
        game,day=pending_buy[uid]; p,_=get_price(c.from_user.id,day); bal=user_balance.get(uid,0)
        stock_list=stock_carrom.get(day,[]) if "CARROM" in game else stock_8ball.get(day,[])
        if len(stock_list)==0 or bal<p: bot.send_message(c.message.chat.id,"Failed! Check Balance/Stock",reply_markup=main_kb()); del pending_buy[uid]; return
        key=stock_list.pop(0); user_balance[uid]=bal-p
        if "CARROM" in game: stock_carrom[day]=stock_list
        else: stock_8ball[day]=stock_list
        save_data(); del pending_buy[uid]
        bot.send_message(c.message.chat.id,f"✅ Success!\n🔑 Key: {key}\n💰 Bal: Rs.{user_balance[uid]}",reply_markup=main_kb()); return
    if data=="confirm_no":
        if uid in pending_buy: del pending_buy[uid]
        bot.send_message(c.message.chat.id,"❌ Cancelled",reply_markup=main_kb()); return

@bot.message_handler(func=lambda m: m.text and "Add Stock" in m.text)
def add_stock_btn(m):
    if m.from_user.id==ADMIN_ID: bot.send_message(m.chat.id,"👇 Select",reply_markup=add_stock_inline_kb())
@bot.message_handler(func=lambda m: m.text and "Delete Stock" in m.text)
def del_stock_btn(m):
    if m.from_user.id==ADMIN_ID: pending_admin[str(m.from_user.id)]="del_stock"; bot.send_message(m.chat.id,"Format: CARROM 1D")
@bot.message_handler(func=lambda m: m.text and "Add Balance" in m.text)
def add_bal_btn(m):
    if m.from_user.id==ADMIN_ID: pending_admin[str(m.from_user.id)]="add_bal"; bot.send_message(m.chat.id,"Format: USERID AMOUNT")
@bot.message_handler(func=lambda m: m.text and "Set Price" in m.text)
def set_price_btn(m):
    if m.from_user.id==ADMIN_ID: pending_admin[str(m.from_user.id)]="set_price"; bot.send_message(m.chat.id,f"Current {price}")
@bot.message_handler(func=lambda m: m.text and "Broadcast" in m.text)
def broadcast_btn(m):
    if m.from_user.id==ADMIN_ID: pending_admin[str(m.from_user.id)]="broadcast"; bot.send_message(m.chat.id,"Broadcast msg")
@bot.message_handler(func=lambda m: m.text and "Make VIP" in m.text and "Cancel" not in m.text)
def make_vip_btn(m):
    if m.from_user.id==ADMIN_ID: pending_admin[str(m.from_user.id)]="make_vip"; bot.send_message(m.chat.id,"VIP UserID")
@bot.message_handler(func=lambda m: m.text and "Make Reseller" in m.text)
def make_res_btn(m):
    if m.from_user.id==ADMIN_ID: pending_admin[str(m.from_user.id)]="make_reseller"; bot.send_message(m.chat.id,"Reseller UserID")
@bot.message_handler(func=lambda m: m.text and "Cancel VIP" in m.text)
def cancel_vip_btn(m):
    if m.from_user.id==ADMIN_ID: pending_admin[str(m.from_user.id)]="cancel_vip"; bot.send_message(m.chat.id,"Cancel VIP UserID")
@bot.message_handler(func=lambda m: m.text and "Cancel Reseller" in m.text)
def cancel_res_btn(m):
    if m.from_user.id==ADMIN_ID: pending_admin[str(m.from_user.id)]="cancel_reseller"; bot.send_message(m.chat.id,"Cancel Reseller UserID")
@bot.message_handler(func=lambda m: m.text and "Stock" in m.text)
def stock_handler(m): bot.send_message(m.chat.id,get_stock_text(),reply_markup=main_kb())
@bot.message_handler(func=lambda m: m.text and "Stats" in m.text)
def stats_handler(m):
    if m.from_user.id==ADMIN_ID: bot.send_message(m.chat.id,f"Users {len(user_balance)}",reply_markup=admin_kb())
@bot.message_handler(func=lambda m: m.text and "Buy 1 Days" in m.text)
def buy1(m): bot.send_message(m.chat.id,"🎁 1 Days - Select Game",reply_markup=buy_game_kb("1D"))
@bot.message_handler(func=lambda m: m.text and "Buy 3 Days" in m.text)
def buy3(m): bot.send_message(m.chat.id,"🎁 3 Days - Select Game",reply_markup=buy_game_kb("3D"))
@bot.message_handler(func=lambda m: m.text and "Buy 7 Days" in m.text)
def buy7(m): bot.send_message(m.chat.id,"🎁 7 Days - Select Game",reply_markup=buy_game_kb("7D"))
@bot.message_handler(func=lambda m: m.text and "Buy 15 Days" in m.text)
def buy15(m): bot.send_message(m.chat.id,"🎁 15 Days - Select Game",reply_markup=buy_game_kb("15D"))
@bot.message_handler(func=lambda m: m.text and "Buy 30 Days" in m.text)
def buy30(m): bot.send_message(m.chat.id,"🎁 30 Days - Select Game",reply_markup=buy_game_kb("30D"))
@bot.message_handler(func=lambda m: m.text and "Add Funds" in m.text)
def add_funds_cmd(m):
    uid=str(m.from_user.id); bal=user_balance.get(uid,0)
    kb=types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("📞 Contact Admin", url="https://wa.me/916296272384"))
    kb.add(types.InlineKeyboardButton("📢 Join Channel", url="https://t.me/gamingkoushikyt"))
    bot.send_message(m.chat.id,f"💳 Add Funds\nID: {uid}\nBal: Rs.{bal}\nPay screenshot pathao",reply_markup=kb)
@bot.message_handler(func=lambda m: str(m.from_user.id) in pending_admin)
def pending_admin_handler(m):
    uid=str(m.from_user.id); task=pending_admin.get(uid); txt=m.text or ""
    if any(x in txt for x in ["Add Stock","Delete Stock","Make VIP","Reseller","Cancel","Back to Main","Buy","Balance","Add Funds","/start","/admin","Stock","Add Balance","Broadcast","Set Price","Stats"]): return
    try:
        if task=="add_bal":
            parts=txt.split(); target=parts[0]; amt=float(parts[1]); user_balance[target]=user_balance.get(target,0)+amt; save_data(); bot.send_message(m.chat.id,f"Added Rs.{amt} to {target}")
        elif task=="set_price":
            parts=txt.split(); day=parts[0].upper(); p=int(parts[1]); price[day]=p; save_data(); bot.send_message(m.chat.id,f"Price {day} = Rs.{p}")
        elif task=="broadcast":
            c=0
            for u in user_balance.keys():
                try: bot.send_message(int(u),txt); c+=1
                except: pass
            bot.send_message(m.chat.id,f"Broadcast {c}")
        elif task=="make_vip": user_plan[txt.strip()]="VIP"; save_data(); bot.send_message(m.chat.id,f"{txt} VIP")
        elif task=="make_reseller": user_plan[txt.strip()]="RESELLER"; save_data(); bot.send_message(m.chat.id,f"{txt} RESELLER")
        elif task=="cancel_vip" or task=="cancel_reseller": user_plan[txt.strip()]="FREE"; save_data(); bot.send_message(m.chat.id,f"{txt} FREE")
        elif task=="del_stock":
            t=txt.upper()
            for d in ["1D","3D","7D","15D","30D"]:
                if d in t:
                    if "CARROM" in t: stock_carrom[d]=[]; save_data(); bot.send_message(m.chat.id,f"CARROM {d} Cleared")
                    if "BALL" in t or "8" in t: stock_8ball[d]=[]; save_data(); bot.send_message(m.chat.id,f"8BALL {d} Cleared")
        del pending_admin[uid]
    except Exception as e: bot.send_message(m.chat.id,f"Error {e}")
@bot.message_handler(func=lambda m: str(m.from_user.id) in pending_add)
def pending_handler(m):
    if m.from_user.id!=ADMIN_ID: return
    uid=str(m.from_user.id)
    if uid not in pending_add: return
    txt=m.text or ""
    if any(x in txt for x in ["Add Stock","Delete Stock","Make VIP","Reseller","Cancel","Back to Main","Buy","Balance","Add Funds","/start","/admin","Stock","Add Balance","Broadcast","Set Price","Stats"]): return
    game,day=pending_add[uid]; keys=[k.strip() for k in txt.split("\n") if k.strip()]; added=0
    for k in keys:
        if "CARROM" in game: stock_carrom[day].append(k)
        else: stock_8ball[day].append(k)
        added+=1
    save_data(); del pending_add[uid]; bot.send_message(m.chat.id,f"{game} {day} Added {added}")
@bot.message_handler(func=lambda m: m.text and "Balance" in m.text)
def bal_cmd(m):
    uid=str(m.from_user.id); bal=user_balance.get(uid,0)
    mode="VIP Rs.40" if str(uid) in vip_mode_users else "Normal Rs.60"
    bot.send_message(m.chat.id,f"💰 Wallet\nBalance: Rs.{bal}\nMode: {mode}",reply_markup=main_kb())
@bot.message_handler(func=lambda m: m.text and "Back to Main" in m.text)
def back_main(m):
    uid=str(m.from_user.id)
    for d in [pending_add,pending_admin,pending_buy]:
        if uid in d: del d[uid]
    bot.send_message(m.chat.id,welcome_text(m.from_user.id),reply_markup=main_kb())

def run_flask(): app.run(host="0.0.0.0",port=10000)
threading.Thread(target=run_flask,daemon=True).start()
bot.infinity_polling()

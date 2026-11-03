import os, json, threading, random, string
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7189081595
UPI_ID = "gamingkoushik@upi"  # TOMAR UPI ID
UPI_NAME = "Koushik Gaming"

stock_carrom = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
stock_8ball = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
user_balance = {}; user_country = {}; user_plan = {}
pending_add = {}; pending_admin = {}; pending_buy = {}; pending_funds = {}
price = {"1D":60,"3D":130,"7D":180,"15D":350,"30D":570}
vip_price = {"1D":40,"3D":80,"7D":110,"15D":210,"30D":320}
vip_mode_users = set()

def save_data():
    with open("data.json","w") as f:
        json.dump({"bal":user_balance,"country":user_country,"plan":user_plan,"carrom":stock_carrom,"ball":stock_8ball,"price":price},f)
def load_data():
    global user_balance,user_country,user_plan,stock_carrom,stock_8ball,price
    try:
        with open("data.json","r") as f:
            d=json.load(f); user_balance=d.get("bal",{}); user_country=d.get("country",{}); user_plan=d.get("plan",{}); stock_carrom=d.get("carrom",stock_carrom); stock_8ball=d.get("ball",stock_8ball); price=d.get("price",price)
    except: pass
load_data()

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
@app.route('/')
def home(): return "KOUSHIK FINAL SHINIGAMI FIXED"

def gen_order_id(): return ''.join(random.choices(string.ascii_uppercase+string.digits, k=20))

def get_price(uid, day):
    s=str(uid)
    if s==str(ADMIN_ID):
        if s in vip_mode_users: return vip_price.get(day, price.get(day)), "Vip pricing"
        else: return price.get(day), "BOSS pricing - ₹60"
    if user_plan.get(s,"FREE") in ["VIP","RESELLER"]: return vip_price.get(day, price.get(day)), "Vip pricing"
    return price.get(day), "Normal pricing"

def get_plan_show(uid_str, is_admin=False):
    raw=user_plan.get(uid_str,"FREE")
    if is_admin:
        if uid_str in vip_mode_users: return "BOSS VIP - ₹40"
        return "BOSS - ₹60"
    if raw=="VIP": return "Silver"
    if raw=="RESELLER": return "Gold"
    return "Bronze"

def welcome_text(m):
    uid=str(m.from_user.id); name=m.from_user.first_name or "User"
    bal=user_balance.get(uid,0); country=user_country.get(uid,"India")
    plan_show=get_plan_show(uid, str(m.from_user.id)==str(ADMIN_ID))
    return f"""🎉 Welcome to SHINIGAMI Bot!

👤 Name: {name}
🏅 Plan: {plan_show}
💰 Balance: ₹{bal:.2f}
🇮🇳 Country: {country}

📢 Channel: @gamingkoushikyt

🚀 Select an option below to get started:"""

def wallet_text(uid):
    bal=user_balance.get(uid,0); plan_show=get_plan_show(uid, uid==str(ADMIN_ID))
    return f"""💰 Your Wallet

💰 Current Balance: ₹{bal:.2f}
🏅 Current Plan: {plan_show}

🚀 Top up via ➕ Add Funds to purchase premium keys!"""

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
    m.add(types.KeyboardButton("💰 Add Balance"),types.KeyboardButton("💵 Set Price"))
    m.add(types.KeyboardButton("📢 Broadcast"),types.KeyboardButton("📊 Stats"))
    m.add(types.KeyboardButton("📦 Check Stock"),types.KeyboardButton("🔙 Back to Main"))
    return m
def add_stock_inline_kb():
    m=types.InlineKeyboardMarkup(row_width=3)
    m.add(types.InlineKeyboardButton("CARROM 1D",callback_data="addsel_CARROM_1D"),types.InlineKeyboardButton("CARROM 3D",callback_data="addsel_CARROM_3D"),types.InlineKeyboardButton("CARROM 7D",callback_data="addsel_CARROM_7D"))
    m.add(types.InlineKeyboardButton("CARROM 15D",callback_data="addsel_CARROM_15D"),types.InlineKeyboardButton("CARROM 30D",callback_data="addsel_CARROM_30D"))
    m.add(types.InlineKeyboardButton("8BALL 1D",callback_data="addsel_8BALL_1D"),types.InlineKeyboardButton("8BALL 3D",callback_data="addsel_8BALL_3D"),types.InlineKeyboardButton("8BALL 7D",callback_data="addsel_8BALL_7D"))
    m.add(types.InlineKeyboardButton("8BALL 15D",callback_data="addsel_8BALL_15D"),types.InlineKeyboardButton("8BALL 30D",callback_data="addsel_8BALL_30D"))
    return m
def buy_game_kb(day):
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton(f"🎯 CARROM {day}",callback_data=f"buy_CARROM_{day}"),types.InlineKeyboardButton(f"🎱 8 BALL {day}",callback_data=f"buy_8BALL_{day}"))
    m.add(types.InlineKeyboardButton("❌ Cancel",callback_data="buy_cancel")) # FIX
    return m
def cancel_funds_kb():
    m=types.InlineKeyboardMarkup(); m.add(types.InlineKeyboardButton("❌ Cancel Add Funds",callback_data="cancel_funds")); return m
def confirm_kb():
    m=types.InlineKeyboardMarkup(row_width=2); m.add(types.InlineKeyboardButton("✅ Confirm",callback_data="confirm_yes"),types.InlineKeyboardButton("❌ Cancel",callback_data="confirm_no")); return m
def get_stock_text():
    txt="📦 Live Stock\n\n🎯 CARROM\n"
    for d in ["1D","3D","7D","15D","30D"]: txt+=f"{'✅' if len(stock_carrom.get(d,[]))>0 else '❌'} {d}: {len(stock_carrom.get(d,[]))}\n"
    txt+="\n🎱 8 BALL\n"
    for d in ["1D","3D","7D","15D","30D"]: txt+=f"{'✅' if len(stock_8ball.get(d,[]))>0 else '❌'} {d}: {len(stock_8ball.get(d,[]))}\n"
    return txt

@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid=str(m.from_user.id)
    for d in [pending_add, pending_admin, pending_buy, pending_funds]:
        if uid in d: del d[uid]
    if uid not in user_balance: user_balance[uid]=0.0; save_data()
    if uid not in user_country: bot.send_message(m.chat.id,"🌍 Select your Country",reply_markup=country_kb())
    else: bot.send_message(m.chat.id,welcome_text(m),reply_markup=main_kb())

@bot.callback_query_handler(func=lambda c: True)
def cb_handler(c):
    uid=str(c.from_user.id); data=c.data
    if data.startswith("country_"):
        user_country[uid]="India" if "India" in data else "Bangladesh"
        if str(c.from_user.id)==str(ADMIN_ID): user_plan[uid]="BOSS"
        save_data()
        try: bot.answer_callback_query(c.id, "Country Selected ✅")
        except: pass
        bot.send_message(c.message.chat.id,welcome_text(c.from_user),reply_markup=main_kb()); return
    if data in ["buy_cancel","cancel_funds","confirm_no"]:
        if uid in pending_buy: del pending_buy[uid]
        if uid in pending_funds: del pending_funds[uid]
        try: bot.answer_callback_query(c.id)
        except: pass
        bot.send_message(c.message.chat.id,welcome_text(c.from_user),reply_markup=main_kb()); return
    if data.startswith("addsel_"):
        if c.from_user.id!=ADMIN_ID: return
        _,game,day=data.split("_"); pending_add[uid]=(game,day)
        bot.send_message(c.message.chat.id,f"✅ {game} {day} Selected! Send keys"); bot.answer_callback_query(c.id); return
    if data.startswith("buy_"):
        _,game,day=data.split("_")
        stock_list=stock_carrom.get(day,[]) if "CARROM" in game else stock_8ball.get(day,[])
        p, ptype = get_price(c.from_user.id, day)
        if len(stock_list)==0:
            bot.send_message(c.message.chat.id,f"❌ {game} {day} Out of Stock!",reply_markup=main_kb())
            if uid in pending_buy: del pending_buy[uid]
            bot.answer_callback_query(c.id, "Out of Stock"); return
        pending_buy[uid]=(game,day)
        bot.send_message(c.message.chat.id,f"🛒 Confirm\nGame: {game}\nDuration: {day}\nPrice: ₹{p} ({ptype})",reply_markup=confirm_kb()); bot.answer_callback_query(c.id); return
    if data=="confirm_yes":
        if uid not in pending_buy: return
        game,day=pending_buy[uid]; p,_=get_price(c.from_user.id, day); bal=user_balance.get(uid,0)
        stock_list=stock_carrom.get(day,[]) if "CARROM" in game else stock_8ball.get(day,[])
        if bal < p: bot.send_message(c.message.chat.id,f"❌ Need ₹{p} Have ₹{bal}",reply_markup=main_kb()); del pending_buy[uid]; return
        if len(stock_list)==0: bot.send_message(c.message.chat.id,"❌ Out of Stock",reply_markup=main_kb()); del pending_buy[uid]; return
        key=stock_list.pop(0); user_balance[uid]=bal-p
        if "CARROM" in game: stock_carrom[day]=stock_list
        else: stock_8ball[day]=stock_list
        save_data(); del pending_buy[uid]
        bot.send_message(c.message.chat.id,f"✅ Success!\nGame: {game}\nKey: {key}\nBalance: ₹{user_balance[uid]}",reply_markup=main_kb()); return

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip()=="vip")
def vip_on(m):
    if m.from_user.id!=ADMIN_ID: return
    vip_mode_users.add(str(m.from_user.id)); bot.send_message(m.chat.id,"✅ VIP MODE ON - ₹40")
@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["normal","boss"])
def normal_on(m):
    if m.from_user.id!=ADMIN_ID: return
    vip_mode_users.discard(str(m.from_user.id)); bot.send_message(m.chat.id,"✅ BOSS MODE ON - ₹60")

@bot.message_handler(func=lambda m: m.text and "Add Stock" in m.text)
def add_stock_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    bot.send_message(m.chat.id,"Select",reply_markup=add_stock_inline_kb())
@bot.message_handler(func=lambda m: m.text and "Delete Stock" in m.text)
def del_stock_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    pending_admin[str(m.from_user.id)]="del_stock"; bot.send_message(m.chat.id,"Format: CARROM 1D")
@bot.message_handler(func=lambda m: m.text and "Add Balance" in m.text)
def add_bal_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    pending_admin[str(m.from_user.id)]="add_bal"; bot.send_message(m.chat.id,"Format: USERID AMOUNT")
@bot.message_handler(func=lambda m: m.text and "Set Price" in m.text)
def set_price_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    pending_admin[str(m.from_user.id)]="set_price"; bot.send_message(m.chat.id,f"Current: {price}\nFormat: 1D 60")
@bot.message_handler(func=lambda m: m.text and "Broadcast" in m.text)
def broadcast_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    pending_admin[str(m.from_user.id)]="broadcast"; bot.send_message(m.chat.id,"Broadcast msg:")
@bot.message_handler(func=lambda m: m.text and "Make VIP" in m.text and "Cancel" not in m.text)
def make_vip_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    pending_admin[str(m.from_user.id)]="make_vip"; bot.send_message(m.chat.id,"VIP UserID:")
@bot.message_handler(func=lambda m: m.text and "Make Reseller" in m.text)
def make_res_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    pending_admin[str(m.from_user.id)]="make_reseller"; bot.send_message(m.chat.id,"Reseller UserID:")
@bot.message_handler(func=lambda m: m.text and "Cancel VIP" in m.text)
def cancel_vip_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    pending_admin[str(m.from_user.id)]="cancel_vip"; bot.send_message(m.chat.id,"Cancel VIP UserID:")
@bot.message_handler(func=lambda m: m.text and "Cancel Reseller" in m.text)
def cancel_res_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    pending_admin[str(m.from_user.id)]="cancel_reseller"; bot.send_message(m.chat.id,"Cancel Reseller UserID:")
@bot.message_handler(func=lambda m: m.text and ("Check Stock" in m.text or m.text=="📦 Stock"))
def stock_handler(m): bot.send_message(m.chat.id,get_stock_text(),reply_markup=main_kb())
@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.from_user.id==ADMIN_ID: bot.send_message(m.chat.id,"👑 BOSS PANEL",reply_markup=admin_kb())

@bot.message_handler(func=lambda m: m.text and "Buy 1 Days" in m.text)
def buy1(m): 
    if str(m.from_user.id) in pending_buy: del pending_buy[str(m.from_user.id)]
    bot.send_message(m.chat.id,"✅ 1 Days Plan Selected\n\nSelect a Game:",reply_markup=buy_game_kb("1D"))
@bot.message_handler(func=lambda m: m.text and "Buy 3 Days" in m.text)
def buy3(m): bot.send_message(m.chat.id,"✅ 3 Days Plan Selected\n\nSelect a Game:",reply_markup=buy_game_kb("3D"))
@bot.message_handler(func=lambda m: m.text and "Buy 7 Days" in m.text)
def buy7(m): bot.send_message(m.chat.id,"✅ 7 Days Plan Selected\n\nSelect a Game:",reply_markup=buy_game_kb("7D"))
@bot.message_handler(func=lambda m: m.text and "Buy 15 Days" in m.text)
def buy15(m): bot.send_message(m.chat.id,"✅ 15 Days Plan Selected\n\nSelect a Game:",reply_markup=buy_game_kb("15D"))
@bot.message_handler(func=lambda m: m.text and "Buy 30 Days" in m.text)
def buy30(m): bot.send_message(m.chat.id,"✅ 30 Days Plan Selected\n\nSelect a Game:",reply_markup=buy_game_kb("30D"))

@bot.message_handler(func=lambda m: m.text and "Balance" in m.text and "Add Balance" not in m.text)
def bal_cmd(m): bot.send_message(m.chat.id,wallet_text(str(m.from_user.id)),reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text and "Add Funds" in m.text)
def add_funds_cmd(m):
    uid=str(m.from_user.id)
    if uid in pending_buy: del pending_buy[uid]
    pending_funds[uid]="await_amount"
    bot.send_message(m.chat.id,"💰 Enter amount (e.g. 100):")

@bot.message_handler(func=lambda m: str(m.from_user.id) in pending_funds and pending_funds[str(m.from_user.id)]=="await_amount")
def funds_amount_handler(m):
    uid=str(m.from_user.id)
    try:
        amt=int(m.text.strip())
        if amt<10: bot.send_message(m.chat.id,"❌ Min ₹10"); return
        order_id=gen_order_id()
        upi_link=f"upi://pay?pa={UPI_ID}&pn={UPI_NAME}&am={amt}&cu=INR&tn=Order_{order_id}"
        qr_url=f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={upi_link}"
        caption=f"""💳 SCAN TO PAY
💠 Pay via UPI
1️⃣ Scan QR
2️⃣ Complete payment
3️⃣ Auto detect

Order ID: {order_id}
Timer: 300s
Amount: ₹{amt}

⚠️ Jitna pay karna hai utna hi karein
Auto-checking every 2 seconds...
Ready to receive payment"""
        bot.send_photo(m.chat.id, qr_url, caption=caption, reply_markup=cancel_funds_kb())
        del pending_funds[uid]
    except: bot.send_message(m.chat.id,"❌ Valid amount dao")

@bot.message_handler(func=lambda m: m.text and ("support" in m.text.lower() or m.text.lower().strip()=="cancel" or "Back to Main" in m.text))
def back_main(m):
    uid=str(m.from_user.id)
    for d in [pending_add, pending_admin, pending_buy, pending_funds]:
        if uid in d: del d[uid]
    bot.send_message(m.chat.id,welcome_text(m),reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text and ("🇮🇳" in m.text or m.text.strip().lower()=="india"))
def india_text(m):
    uid=str(m.from_user.id); user_country[uid]="India"; save_data()
    bot.send_message(m.chat.id,welcome_text(m),reply_markup=main_kb())
@bot.message_handler(func=lambda m: m.text and ("🇧🇩" in m.text or m.text.strip().lower()=="bangladesh"))
def bd_text(m):
    uid=str(m.from_user.id); user_country[uid]="Bangladesh"; save_data()
    bot.send_message(m.chat.id,welcome_text(m),reply_markup=main_kb())

@bot.message_handler(func=lambda m: str(m.from_user.id) in pending_admin)
def pending_admin_handler(m):
    uid=str(m.from_user.id); task=pending_admin.get(uid); txt=m.text or ""
    if any(x in txt for x in ["Add Stock","Delete Stock","Make VIP","Reseller","Cancel","Back to Main","Users List","Buy","Balance","Add Funds","/start","/admin","Check Stock","Stock","Add Balance","Broadcast","Set Price","Stats"]): return
    try:
        if task=="add_bal":
            parts=txt.split(); target=parts[0]; amt=float(parts[1]); user_balance[target]=user_balance.get(target,0)+amt; save_data(); bot.send_message(m.chat.id,f"✅ Added ₹{amt} to {target}")
        elif task=="set_price":
            parts=txt.split(); day=parts[0].upper(); p=int(parts[1]); price[day]=p; save_data(); bot.send_message(m.chat.id,f"✅ {day}=₹{p}")
        elif task=="broadcast":
            c=0
            for u in user_balance.keys():
                try: bot.send_message(int(u),f"📢 {txt}"); c+=1
                except: pass
            bot.send_message(m.chat.id,f"✅ Broadcast {c}")
        elif task=="make_vip": user_plan[txt.strip()]="VIP"; save_data(); bot.send_message(m.chat.id,f"✅ {txt.strip()} VIP")
        elif task=="make_reseller": user_plan[txt.strip()]="RESELLER"; save_data(); bot.send_message(m.chat.id,f"✅ {txt.strip()} RES")
        elif task in ["cancel_vip","cancel_reseller"]: user_plan[txt.strip()]="FREE"; save_data(); bot.send_message(m.chat.id,f"✅ {txt.strip()} FREE")
        elif task=="del_stock":
            t=txt.upper()
            if "CARROM" in t:
                for d in ["1D","3D","7D","15D","30D"]:
                    if d in t: stock_carrom[d]=[]; save_data()
            if "BALL" in t or "8" in t:
                for d in ["1D","3D","7D","15D","30D"]:
                    if d in t: stock_8ball[d]=[]; save_data()
            bot.send_message(m.chat.id,"✅ Cleared")
        del pending_admin[uid]
    except Exception as e: bot.send_message(m.chat.id,f"❌ {e}")

@bot.message_handler(func=lambda m: str(m.from_user.id) in pending_add)
def pending_handler(m):
    if m.from_user.id!=ADMIN_ID: return
    uid=str(m.from_user.id); txt=m.text or ""
    if any(x in txt for x in ["Add Stock","Delete Stock","Make VIP","Reseller","Cancel","Back to Main","Users List","Buy","Balance","Add Funds","/start","/admin","Check Stock","Stock","Add Balance","Broadcast","Set Price","Stats"]): return
    game,day=pending_add[uid]; keys=txt.strip().split("\n"); added=0
    for k in keys:
        k=k.strip()
        if not k: continue
        if "CARROM" in game: stock_carrom[day].append(k)
        else: stock_8ball[day].append(k)
        added+=1
    save_data(); del pending_add[uid]
    total=len(stock_carrom[day]) if "CARROM" in game else len(stock_8ball[day])
    bot.send_message(m.chat.id,f"✅ {game} {day} Added: {added}, Total: {total}",reply_markup=add_stock_inline_kb())

@bot.message_handler(func=lambda m: True)
def fallback(m):
    uid=str(m.from_user.id)
    if uid not in user_country: bot.send_message(m.chat.id,"🌍 Select your Country",reply_markup=country_kb())
    else: bot.send_message(m.chat.id,welcome_text(m),reply_markup=main_kb())

def run_flask(): app.run(host="0.0.0.0",port=10000)
threading.Thread(target=run_flask,daemon=True).start()
bot.infinity_polling(skip_pending=True, timeout=20)

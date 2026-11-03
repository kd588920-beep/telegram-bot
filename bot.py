import os, json, threading, random, string
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7189081595

# ===== Tomar UPI ID ekhane bosao =====
UPI_ID = "gamingkoushik@upi"  # <-- tomar UPI ID
UPI_NAME = "Koushik Gaming"

stock_carrom = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
stock_8ball = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
user_balance = {}; user_country = {}; user_plan = {}
pending_add = {}; price = {"1D":60,"3D":130,"7D":180,"15D":350,"30D":570}
vip_price = {"1D":40,"3D":80,"7D":110,"15D":210,"30D":320}
pending_admin = {}; pending_buy = {}; pending_funds = {}
vip_mode_users = set()

def save_data():
    with open("data.json","w") as f:
        json.dump({"bal":user_balance,"country":user_country,"plan":user_plan,"carrom":stock_carrom,"ball":stock_8ball,"price":price},f)

def load_data():
    global user_balance,user_country,user_plan,stock_carrom,stock_8ball,price
    try:
        with open("data.json","r") as f:
            d=json.load(f)
            user_balance=d.get("bal",{}); user_country=d.get("country",{}); user_plan=d.get("plan",{})
            stock_carrom=d.get("carrom",stock_carrom); stock_8ball=d.get("ball",stock_8ball); price=d.get("price",price)
    except: pass

load_data()
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
@app.route('/')
def home(): return "KOUSHIK SHINIGAMI STYLE LIVE"

def gen_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))

def get_plan_show(uid_str, is_admin=False):
    plan_raw = user_plan.get(uid_str, "FREE")
    if is_admin: return "BOSS 👑"
    if plan_raw == "VIP": return "Silver"
    if plan_raw == "RESELLER": return "Gold"
    return "Bronze"

def get_price(uid, day):
    s=str(uid)
    if s==str(ADMIN_ID):
        if s in vip_mode_users: return vip_price.get(day), "Vip pricing"
        else: return price.get(day), "BOSS pricing"
    if user_plan.get(s,"FREE") in ["VIP","RESELLER"]: return vip_price.get(day), "Vip pricing"
    return price.get(day), "Normal pricing"

# ===== 1. SHINIGAMI STYLE WELCOME =====
def welcome_text(m):
    uid=str(m.from_user.id)
    name=m.from_user.first_name or "User"
    bal=user_balance.get(uid,0)
    country=user_country.get(uid,"India")
    plan_show = get_plan_show(uid, str(m.from_user.id)==str(ADMIN_ID))
    return f"""🎉 Welcome to SHINIGAMI Bot!

👤 Name: {name}
🏅 Plan: {plan_show}
💰 Balance: ₹{bal:.2f}
🇮🇳 Country: {country}

📢 Channel: @gamingkoushikyt

🚀 Select an option below to get started:"""

# ===== 3. SHINIGAMI STYLE WALLET =====
def wallet_text(uid):
    bal=user_balance.get(uid,0)
    plan_show = get_plan_show(uid, uid==str(ADMIN_ID))
    return f"""💰 Your Wallet

💰 Current Balance: ₹{bal:.2f}
🏅 Current Plan: {plan_show}

🚀 Top up via ➕ Add Funds to purchase premium keys!"""

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

# ===== 2. BUY + CANCEL BUTTON =====
def buy_game_kb(day):
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton(f"🎯 CARROM {day}",callback_data=f"buy_CARROM_{day}"),types.InlineKeyboardButton(f"🎱 8 BALL {day}",callback_data=f"buy_8BALL_{day}"))
    m.add(types.InlineKeyboardButton("❌ Cancel",callback_data="buy_cancel"))
    return m

def cancel_add_funds_kb():
    m=types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("❌ Cancel Add Funds",callback_data="cancel_funds"))
    return m

def confirm_kb():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("✅ Confirm",callback_data="confirm_yes"),types.InlineKeyboardButton("❌ Cancel",callback_data="confirm_no"))
    return m

def country_kb():
    m=types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("🇮🇳 India",callback_data="country_India"))
    m.add(types.InlineKeyboardButton("🇧🇩 Bangladesh",callback_data="country_Bangladesh"))
    return m

@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid=str(m.from_user.id)
    for d in [pending_add, pending_admin, pending_buy, pending_funds]:
        if uid in d: del d[uid]
    if uid not in user_balance: user_balance[uid]=0.0; save_data()
    if uid not in user_country:
        bot.send_message(m.chat.id,"🌍 Select your Country",reply_markup=country_kb())
    else:
        bot.send_message(m.chat.id,welcome_text(m),reply_markup=main_kb())

@bot.callback_query_handler(func=lambda c: True)
def cb_handler(c):
    uid=str(c.from_user.id); data=c.data
    if data.startswith("country_"):
        user_country[uid]="India" if "India" in data else "Bangladesh"; save_data()
        bot.send_message(c.message.chat.id,welcome_text(c.from_user),reply_markup=main_kb()); bot.answer_callback_query(c.id); return
    
    if data=="buy_cancel" or data=="cancel_funds" or data=="confirm_no":
        if uid in pending_buy: del pending_buy[uid]
        if uid in pending_funds: del pending_funds[uid]
        bot.send_message(c.message.chat.id,welcome_text(c.from_user),reply_markup=main_kb()); bot.answer_callback_query(c.id); return

    if data.startswith("addsel_"):
        if c.from_user.id!=ADMIN_ID: return
        _,game,day=data.split("_"); pending_add[uid]=(game,day)
        bot.send_message(c.message.chat.id,f"✅ {game} {day} Selected! Send keys"); bot.answer_callback_query(c.id); return
    
    if data.startswith("buy_"):
        _,game,day=data.split("_")
        stock_list=stock_carrom.get(day,[]) if "CARROM" in game else stock_8ball.get(day,[])
        p, ptype = get_price(c.from_user.id, day)
        if len(stock_list)==0: bot.send_message(c.message.chat.id,f"❌ {game} {day} Out of Stock!"); bot.answer_callback_query(c.id); return
        pending_buy[uid]=(game,day)
        bot.send_message(c.message.chat.id,f"🛒 Confirm\nGame: {game}\nDuration: {day}\nPrice: ₹{p} ({ptype})",reply_markup=confirm_kb()); bot.answer_callback_query(c.id); return
    
    if data=="confirm_yes":
        if uid not in pending_buy: return
        game,day=pending_buy[uid]; p,_=get_price(c.from_user.id, day); bal=user_balance.get(uid,0)
        stock_list=stock_carrom.get(day,[]) if "CARROM" in game else stock_8ball.get(day,[])
        if bal < p: bot.send_message(c.message.chat.id,f"❌ Low Balance Need ₹{p} You have ₹{bal}"); del pending_buy[uid]; bot.answer_callback_query(c.id); return
        if len(stock_list)==0: bot.send_message(c.message.chat.id,"❌ Out of Stock"); del pending_buy[uid]; bot.answer_callback_query(c.id); return
        key=stock_list.pop(0); user_balance[uid]=bal-p
        if "CARROM" in game: stock_carrom[day]=stock_list
        else: stock_8ball[day]=stock_list
        save_data(); del pending_buy[uid]
        bot.send_message(c.message.chat.id,f"✅ Success!\nGame: {game}\nKey: {key}\nBalance: ₹{user_balance[uid]}"); bot.answer_callback_query(c.id); return

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip()=="vip")
def vip_on(m):
    if m.from_user.id!=ADMIN_ID: return
    vip_mode_users.add(str(m.from_user.id)); bot.send_message(m.chat.id,f"✅ VIP MODE ON - ₹40")

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["normal","boss"])
def normal_on(m):
    if m.from_user.id!=ADMIN_ID: return
    vip_mode_users.discard(str(m.from_user.id)); bot.send_message(m.chat.id,f"✅ BOSS MODE ON - ₹60")

# Cancel likhle Welcome e back
@bot.message_handler(func=lambda m: m.text and m.text.lower().strip()=="cancel")
def cancel_text(m):
    uid=str(m.from_user.id)
    for d in [pending_add, pending_admin, pending_buy, pending_funds]:
        if uid in d: del d[uid]
    bot.send_message(m.chat.id,welcome_text(m),reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text and "Add Stock" in m.text)
def add_stock_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    bot.send_message(m.chat.id,"Select",reply_markup=add_stock_inline_kb())

# Buy handlers with SHINIGAMI text
@bot.message_handler(func=lambda m: m.text and "Buy 1 Days" in m.text)
def buy1(m): bot.send_message(m.chat.id,"✅ 1 Days Plan Selected\n\nSelect a Game:",reply_markup=buy_game_kb("1D"))
@bot.message_handler(func=lambda m: m.text and "Buy 3 Days" in m.text)
def buy3(m): bot.send_message(m.chat.id,"✅ 3 Days Plan Selected\n\nSelect a Game:",reply_markup=buy_game_kb("3D"))
@bot.message_handler(func=lambda m: m.text and "Buy 7 Days" in m.text)
def buy7(m): bot.send_message(m.chat.id,"✅ 7 Days Plan Selected\n\nSelect a Game:",reply_markup=buy_game_kb("7D"))
@bot.message_handler(func=lambda m: m.text and "Buy 15 Days" in m.text)
def buy15(m): bot.send_message(m.chat.id,"✅ 15 Days Plan Selected\n\nSelect a Game:",reply_markup=buy_game_kb("15D"))
@bot.message_handler(func=lambda m: m.text and "Buy 30 Days" in m.text)
def buy30(m): bot.send_message(m.chat.id,"✅ 30 Days Plan Selected\n\nSelect a Game:",reply_markup=buy_game_kb("30D"))

@bot.message_handler(func=lambda m: m.text and "Balance" in m.text and "Add Balance" not in m.text)
def bal_cmd(m):
    uid=str(m.from_user.id)
    bot.send_message(m.chat.id,wallet_text(uid))

# ===== 4. SHINIGAMI STYLE ADD FUNDS WITH QR =====
@bot.message_handler(func=lambda m: m.text and "Add Funds" in m.text)
def add_funds_cmd(m):
    uid=str(m.from_user.id)
    pending_funds[uid]="await_amount"
    bot.send_message(m.chat.id,"💰 Enter amount to add (e.g. 100):")

@bot.message_handler(func=lambda m: str(m.from_user.id) in pending_funds and pending_funds[str(m.from_user.id)]=="await_amount")
def funds_amount_handler(m):
    uid=str(m.from_user.id)
    try:
        amt=int(m.text.strip())
        if amt<10: bot.send_message(m.chat.id,"❌ Minimum ₹10"); return
        order_id=gen_order_id()
        # UPI QR Link
        upi_link=f"upi://pay?pa={UPI_ID}&pn={UPI_NAME}&am={amt}&cu=INR&tn=Order_{order_id}"
        qr_url=f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={upi_link}"
        
        caption=f"""💳 SCAN TO PAY

💠 Pay via UPI
1️⃣ • Scan the QR code
2️⃣ 💰 Complete your payment
3️⃣ 🔄 Payment automatically detect & add ho jayega

❌ Order ID: {order_id}
⏰ Timer: 300s

⚠️ Jitna payment karna hai, utna hi pay karein. Payment automatically verify hokar balance mein add ho jayega.

⏰ Timer: 5:00
🔄 Auto-checking every 2 seconds...
✅ Ready to receive payment
💰 Amount: ₹{amt}

ID: {uid}
Current Balance: ₹{user_balance.get(uid,0)}"""

        bot.send_photo(m.chat.id, qr_url, caption=caption, reply_markup=cancel_add_funds_kb())
        del pending_funds[uid]
        # Save order for manual verification
        pending_funds[uid+f"_order"]=(order_id,amt)
    except Exception as e:
        bot.send_message(m.chat.id,f"❌ Valid amount dao, Error: {e}")

@bot.message_handler(func=lambda m: m.text and "Back to Main" in m.text)
def back_main(m):
    uid=str(m.from_user.id)
    for d in [pending_add, pending_admin, pending_buy, pending_funds]:
        if uid in d: del d[uid]
    bot.send_message(m.chat.id,welcome_text(m),reply_markup=main_kb())

def run_flask(): app.run(host="0.0.0.0",port=10000)
threading.Thread(target=run_flask,daemon=True).start()
bot.infinity_polling()

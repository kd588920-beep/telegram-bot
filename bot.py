import os, json, threading, random, string
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7189081595
UPI_ID = "gamingkoushik@upi"
UPI_NAME = "Koushik Gaming"

stock_carrom = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
stock_8ball = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
user_balance = {}
user_country = {}
user_plan = {}
pending_add = {}
pending_admin = {}
pending_buy = {}
pending_funds = {}
price = {"1D":60,"3D":130,"7D":180,"15D":350,"30D":570}
vip_price = {"1D":40,"3D":80,"7D":110,"15D":210,"30D":320}
vip_mode_users = set()

def save_data():
    try:
        with open("data.json","w") as f:
            json.dump({
                "bal":user_balance,
                "country":user_country,
                "plan":user_plan,
                "carrom":stock_carrom,
                "ball":stock_8ball,
                "price":price
            },f)
    except: pass

def load_data():
    global user_balance, user_country
    global user_plan, stock_carrom
    global stock_8ball, price
    try:
        with open("data.json","r") as f:
            d=json.load(f)
            user_balance=d.get("bal",{})
            user_country=d.get("country",{})
            user_plan=d.get("plan",{})
            stock_carrom=d.get("carrom",stock_carrom)
            stock_8ball=d.get("ball",stock_8ball)
            price=d.get("price",price)
    except: pass

load_data()
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "KOUSHIK FINAL CLEAN LIVE"

def gen_order_id():
    return ''.join(random.choices(
        string.ascii_uppercase+string.digits,k=20))

def get_price(uid, day):
    s=str(uid)
    if s==str(ADMIN_ID):
        if s in vip_mode_users:
            return vip_price.get(day,price.get(day)),"VIP Rs40"
        return price.get(day),"BOSS Rs60"
    if user_plan.get(s,"FREE") in ["VIP","RESELLER"]:
        return vip_price.get(day,price.get(day)),"VIP"
    return price.get(day),"FREE Rs60"

def get_plan_show(uid_str):
    if uid_str==str(ADMIN_ID):
        if uid_str in vip_mode_users:
            return "BOSS VIP - Rs40"
        return "BOSS - Rs60"
    p=user_plan.get(uid_str,"FREE")
    if p=="VIP": return "Silver"
    if p=="RESELLER": return "Gold"
    return "Bronze"

def welcome_text(m):
    uid=str(m.from_user.id)
    name=m.from_user.first_name or "User"
    bal=user_balance.get(uid,0)
    country=user_country.get(uid,"India")
    plan_show=get_plan_show(uid)
    return (
        f"Welcome to SHINIGAMI Bot!\n\n"
        f"Name: {name}\n"
        f"Plan: {plan_show}\n"
        f"Balance: Rs.{bal:.2f}\n"
        f"Country: {country}\n\n"
        f"Channel: @gamingkoushikyt"
    )

def wallet_text(uid):
    bal=user_balance.get(uid,0)
    plan_show=get_plan_show(uid)
    return (
        f"Your Wallet\n\n"
        f"Current Balance: Rs.{bal:.2f}\n"
        f"Current Plan: {plan_show}\n\n"
        f"Top up via Add Funds!"
    )

def price_list_text(uid=None):
    s=str(uid) if uid else "0"
    if s==str(ADMIN_ID):
        if s in vip_mode_users:
            p_dict=vip_price
            medal="VIP MODE - Rs40"
        else:
            p_dict=price
            medal="BOSS MODE - Rs60"
    elif user_plan.get(s,"FREE") in ["VIP","RESELLER"]:
        p_dict=vip_price
        medal="VIP/Reseller"
    else:
        p_dict=price
        medal="FREE - Rs60"
    return (
        f"CARROM\n\n"
        f"Your Medal: {medal}\n\n"
        f"Price List\n"
        f"1 Days - Rs.{p_dict['1D']}\n"
        f"3 Days - Rs.{p_dict['3D']}\n"
        f"7 Days - Rs.{p_dict['7D']}\n"
        f"15 Days - Rs.{p_dict['15D']}\n"
        f"30 Days - Rs.{p_dict['30D']}"
    )

def get_stock_text():
    txt="Live Stock Status\n\nCARROM\n"
    for d in ["1D","3D","7D","15D","30D"]:
        c=len(stock_carrom.get(d,[]))
        txt+=f"{'YES' if c>0 else 'NO'} {d}: {c}\n"
    txt+="\n8 BALL POOL\n"
    for d in ["1D","3D","7D","15D","30D"]:
        c=len(stock_8ball.get(d,[]))
        txt+=f"{'YES' if c>0 else 'NO'} {d}: {c}\n"
    return txt

def country_kb():
    m=types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton(
        "India",callback_data="country_India"))
    m.add(types.InlineKeyboardButton(
        "Bangladesh",callback_data="country_Bangladesh"))
    return m

def main_kb():
    m=types.ReplyKeyboardMarkup(
        resize_keyboard=True,row_width=2)
    m.add(types.KeyboardButton("Buy 1 Days"),
          types.KeyboardButton("Buy 3 Days"))
    m.add(types.KeyboardButton("Buy 7 Days"),
          types.KeyboardButton("Buy 15 Days"))
    m.add(types.KeyboardButton("Buy 30 Days"),
          types.KeyboardButton("Stock"))
    m.add(types.KeyboardButton("Add Funds"),
          types.KeyboardButton("Balance"))
    return m

def buy_game_kb(day):
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton(
            f"CARROM {day}",callback_data=f"buy_CARROM_{day}"),
        types.InlineKeyboardButton(
            f"8 BALL {day}",callback_data=f"buy_8BALL_{day}")
    )
    m.add(types.InlineKeyboardButton(
        "Cancel",callback_data="buy_cancel"))
    return m

def cancel_funds_kb():
    m=types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton(
        "Cancel Add Funds",callback_data="cancel_funds"))
    return m

def confirm_kb():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(
        types.InlineKeyboardButton(
            "Confirm",callback_data="confirm_yes"),
        types.InlineKeyboardButton(
            "Cancel",callback_data="confirm_no")
    )
    return m

@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid=str(m.from_user.id)
    for d in [pending_add,pending_admin,
              pending_buy,pending_funds]:
        if uid in d: del d[uid]
    if uid not in user_balance:
        user_balance[uid]=0.0
        save_data()
    if uid not in user_country:
        bot.send_message(m.chat.id,
            "Select your Country:",reply_markup=country_kb())
    else:
        bot.send_message(m.chat.id,
            welcome_text(m),reply_markup=main_kb())

@bot.message_handler(commands=['price'])
def price_cmd(m):
    bot.send_message(m.chat.id,
        price_list_text(m.from_user.id),reply_markup=main_kb())

@bot.callback_query_handler(
    func=lambda c: c.data.startswith("country_"))
def country_cb(c):
    uid=str(c.from_user.id)
    user_country[uid]="India" if "India" in c.data else "Bangladesh"
    save_data()
    try: bot.answer_callback_query(c.id,"Selected")
    except: pass
    bot.send_message(c.message.chat.id,
        welcome_text(c.from_user),reply_markup=main_kb())

@bot.callback_query_handler(
    func=lambda c: c.data in ["buy_cancel","cancel_funds","confirm_no"])
def cancel_cb(c):
    uid=str(c.from_user.id)
    if uid in pending_buy: del pending_buy[uid]
    if uid in pending_funds: del pending_funds[uid]
    try: bot.answer_callback_query(c.id)
    except: pass
    bot.send_message(c.message.chat.id,
        welcome_text(c.from_user),reply_markup=main_kb())

@bot.callback_query_handler(
    func=lambda c: c.data.startswith("buy_"))
def buy_cb(c):
    uid=str(c.from_user.id)
    _,game,day=c.data.split("_")
    if "CARROM" in game:
        stock_list=stock_carrom.get(day,[])
    else:
        stock_list=stock_8ball.get(day,[])
    p,ptype=get_price(c.from_user.id,day)
    if len(stock_list)==0:
        bot.send_message(c.message.chat.id,
            f"{game} {day} Out of Stock!",reply_markup=main_kb())
        return
    pending_buy[uid]=(game,day)
    bot.send_message(c.message.chat.id,
        f"Confirm\nGame: {game}\nPrice: Rs.{p} ({ptype})",
        reply_markup=confirm_kb())

@bot.callback_query_handler(
    func=lambda c: c.data=="confirm_yes")
def confirm_yes_cb(c):
    uid=str(c.from_user.id)
    if uid not in pending_buy: return
    game,day=pending_buy[uid]
    p,_=get_price(c.from_user.id,day)
    bal=user_balance.get(uid,0)
    if "CARROM" in game:
        stock_list=stock_carrom.get(day,[])
    else:
        stock_list=stock_8ball.get(day,[])
    if len(stock_list)==0 or bal<p:
        bot.send_message(c.message.chat.id,
            "Failed! Check balance or stock",reply_markup=main_kb())
        del pending_buy[uid]
        return
    key=stock_list.pop(0)
    user_balance[uid]=bal-p
    if "CARROM" in game:
        stock_carrom[day]=stock_list
    else:
        stock_8ball[day]=stock_list
    save_data()
    del pending_buy[uid]
    bot.send_message(c.message.chat.id,
        f"Success! Key:{key} Bal:Rs.{user_balance[uid]}",
        reply_markup=main_kb())

@bot.message_handler(
    func=lambda m: m.text and m.text.lower().strip()=="vip")
def vip_on(m):
    if m.from_user.id!=ADMIN_ID: return
    vip_mode_users.add(str(m.from_user.id))
    bot.send_message(m.chat.id,
        f"VIP MODE ON - Rs40\n{price_list_text(m.from_user.id)}",
        reply_markup=main_kb())

@bot.message_handler(
    func=lambda m: m.text and m.text.lower().strip() in ["normal","boss"])
def normal_on(m):
    if m.from_user.id!=ADMIN_ID: return
    vip_mode_users.discard(str(m.from_user.id))
    bot.send_message(m.chat.id,
        f"BOSS MODE ON - Rs60\n{price_list_text(m.from_user.id)}",
        reply_markup=main_kb())

@bot.message_handler(func=lambda m: "Buy 1 Days" in (m.text or ""))
def buy1(m): bot.send_message(m.chat.id,"1 Days Selected",reply_markup=buy_game_kb("1D"))
@bot.message_handler(func=lambda m: "Buy 3 Days" in (m.text or ""))
def buy3(m): bot.send_message(m.chat.id,"3 Days Selected",reply_markup=buy_game_kb("3D"))
@bot.message_handler(func=lambda m: "Buy 7 Days" in (m.text or ""))
def buy7(m): bot.send_message(m.chat.id,"7 Days Selected",reply_markup=buy_game_kb("7D"))
@bot.message_handler(func=lambda m: "Buy 15 Days" in (m.text or ""))
def buy15(m): bot.send_message(m.chat.id,"15 Days Selected",reply_markup=buy_game_kb("15D"))
@bot.message_handler(func=lambda m: "Buy 30 Days" in (m.text or ""))
def buy30(m): bot.send_message(m.chat.id,"30 Days Selected",reply_markup=buy_game_kb("30D"))

@bot.message_handler(func=lambda m: "Balance" in (m.text or ""))
def bal_cmd(m):
    bot.send_message(m.chat.id,
        wallet_text(str(m.from_user.id)),reply_markup=main_kb())

@bot.message_handler(func=lambda m: "Add Funds" in (m.text or ""))
def add_funds_cmd(m):
    uid=str(m.from_user.id)
    pending_funds[uid]="await_amount"
    bot.send_message(m.chat.id,"Enter amount (e.g. 100):")

@bot.message_handler(
    func=lambda m: str(m.from_user.id) in pending_funds and pending_funds[str(m.from_user.id)]=="await_amount")
def funds_amount(m):
    uid=str(m.from_user.id)
    try:
        amt=int(m.text.strip())
        order_id=gen_order_id()
        upi_link=f"upi://pay?pa={UPI_ID}&pn={UPI_NAME}&am={amt}&cu=INR&tn={order_id}"
        qr_url=f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={upi_link}"
        caption=f"SCAN TO PAY\nOrder ID: {order_id}\nTimer: 300s\nAmount: Rs.{amt}"
        bot.send_photo(m.chat.id,qr_url,caption=caption,reply_markup=cancel_funds_kb())
        del pending_funds[uid]
    except:
        bot.send_message(m.chat.id,"Valid amount dao")

@bot.message_handler(func=lambda m: "Back to Main" in (m.text or "") or "cancel" in (m.text or "").lower())
def back_main(m):
    uid=str(m.from_user.id)
    for d in [pending_add,pending_admin,pending_buy,pending_funds]:
        if uid in d: del d[uid]
    bot.send_message(m.chat.id,welcome_text(m),reply_markup=main_kb())

@bot.message_handler(func=lambda m: True)
def fallback(m):
    uid=str(m.from_user.id)
    if uid not in user_country:
        bot.send_message(m.chat.id,"Select your Country:",reply_markup=country_kb())
    else:
        bot.send_message(m.chat.id,welcome_text(m),reply_markup=main_kb())

def run_flask():
    app.run(host="0.0.0.0",port=10000)

threading.Thread(target=run_flask,daemon=True).start()
bot.infinity_polling(skip_pending=True,timeout=20)

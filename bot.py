import os, json, threading, time
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7189081595

stock_carrom = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
stock_8ball = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
user_balance = {}
user_country = {}
user_plan = {}
pending_add = {}
pending_admin = {}
pending_buy = {}
price = {"1D":60,"3D":130,"7D":180,"15D":350,"30D":570}
vip_price = {"1D":40,"3D":80,"7D":110,"15D":210,"30D":320}

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
            user_balance=d.get("bal",{})
            user_country=d.get("country",{})
            user_plan=d.get("plan",{})
            stock_carrom=d.get("carrom",stock_carrom)
            stock_8ball=d.get("ball",stock_8ball)
            price=d.get("price",price)
    except: pass

load_data()
app = Flask(__name__)

@app.route('/')
def home():
    return "KOUSHIK BOT LIVE - PRICE FIXED"

def get_price(uid, day):
    s=str(uid)
    if s==str(ADMIN_ID) or user_plan.get(s,"FREE") in ["VIP","RESELLER"]:
        return vip_price.get(day,price.get(day)),"VIP"
    return price.get(day),"FREE"

def price_list_text(uid):
    s=str(uid)
    if s==str(ADMIN_ID) or user_plan.get(s,"FREE") in ["VIP","RESELLER"]:
        p_dict=vip_price
        medal="VIP/Reseller - Rs40"
    else:
        p_dict=price
        medal="FREE - Rs60"
    return f"""CARROM / 8 BALL POOL

Your Medal: {medal}

Price List
1 Days - Rs.{p_dict['1D']}
3 Days - Rs.{p_dict['3D']}
7 Days - Rs.{p_dict['7D']}
15 Days - Rs.{p_dict['15D']}
30 Days - Rs.{p_dict['30D']}

Select Buy button to purchase"""

def get_stock_text():
    txt="Live Stock\n\nCARROM\n"
    for d in ["1D","3D","7D","15D","30D"]:
        txt+=f"{d}: {len(stock_carrom.get(d,[]))} keys\n"
    txt+="\n8 BALL\n"
    for d in ["1D","3D","7D","15D","30D"]:
        txt+=f"{d}: {len(stock_8ball.get(d,[]))} keys\n"
    return txt

def country_kb():
    m=types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("India",callback_data="country_India"))
    m.add(types.InlineKeyboardButton("Bangladesh",callback_data="country_Bangladesh"))
    return m

def main_kb():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add(types.KeyboardButton("Buy 1 Days"),types.KeyboardButton("Buy 3 Days"))
    m.add(types.KeyboardButton("Buy 7 Days"),types.KeyboardButton("Buy 15 Days"))
    m.add(types.KeyboardButton("Buy 30 Days"),types.KeyboardButton("Stock"))
    m.add(types.KeyboardButton("Add Funds"),types.KeyboardButton("Balance"))
    return m

def admin_kb():
    m=types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add(types.KeyboardButton("Add Stock"),types.KeyboardButton("Delete Stock"))
    m.add(types.KeyboardButton("Make VIP"),types.KeyboardButton("Make Reseller"))
    m.add(types.KeyboardButton("Cancel VIP"),types.KeyboardButton("Cancel Reseller"))
    m.add(types.KeyboardButton("Add Balance"),types.KeyboardButton("Set Price"))
    m.add(types.KeyboardButton("Broadcast"),types.KeyboardButton("Stats"))
    m.add(types.KeyboardButton("Check Stock"),types.KeyboardButton("Back to Main"))
    return m

def buy_game_kb(day):
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton(f"CARROM {day}",callback_data=f"buy_CARROM_{day}"),types.InlineKeyboardButton(f"8 BALL {day}",callback_data=f"buy_8BALL_{day}"))
    m.add(types.InlineKeyboardButton("Cancel",callback_data="cancel"))
    return m

def confirm_kb():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("Confirm",callback_data="yes"),types.InlineKeyboardButton("Cancel",callback_data="no"))
    return m

def add_stock_inline_kb():
    m=types.InlineKeyboardMarkup(row_width=3)
    m.add(types.InlineKeyboardButton("CARROM 1D",callback_data="addsel_CARROM_1D"),types.InlineKeyboardButton("CARROM 3D",callback_data="addsel_CARROM_3D"),types.InlineKeyboardButton("CARROM 7D",callback_data="addsel_CARROM_7D"))
    m.add(types.InlineKeyboardButton("CARROM 15D",callback_data="addsel_CARROM_15D"),types.InlineKeyboardButton("CARROM 30D",callback_data="addsel_CARROM_30D"))
    m.add(types.InlineKeyboardButton("8BALL 1D",callback_data="addsel_8BALL_1D"),types.InlineKeyboardButton("8BALL 3D",callback_data="addsel_8BALL_3D"),types.InlineKeyboardButton("8BALL 7D",callback_data="addsel_8BALL_7D"))
    m.add(types.InlineKeyboardButton("8BALL 15D",callback_data="addsel_8BALL_15D"),types.InlineKeyboardButton("8BALL 30D",callback_data="addsel_8BALL_30D"))
    return m

def welcome_text(uid):
    uid=str(uid)
    bal=user_balance.get(uid,0)
    country=user_country.get(uid,"India")
    plan="BOSS" if uid==str(ADMIN_ID) else user_plan.get(uid,"FREE")
    return f"Welcome Koushik Gaming!\nPlan:{plan}\nBalance:Rs.{bal}\nCountry:{country}\nChannel:@gamingkoushikyt"

# ---- BOT SETUP ----
if not BOT_TOKEN:
    print("BOT_TOKEN missing")

bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None

if bot:
    @bot.message_handler(commands=['start'])
    def start_cmd(m):
        uid=str(m.from_user.id)
        if uid not in user_balance:
            user_balance[uid]=0.0; save_data()
        if uid not in user_country:
            bot.send_message(m.chat.id,"Select country",reply_markup=country_kb())
        else:
            bot.send_message(m.chat.id,welcome_text(m.from_user.id),reply_markup=main_kb())

    @bot.message_handler(commands=['price','prices'])
    def price_cmd(m):
        # FIXED: ebar welcome noy, price list asbe
        bot.send_message(m.chat.id, price_list_text(m.from_user.id), reply_markup=main_kb())

    @bot.message_handler(commands=['support','help'])
    def support_cmd(m):
        bot.send_message(m.chat.id,"Contact @koushik_098", reply_markup=main_kb())

    @bot.callback_query_handler(func=lambda c: True)
    def cb_handler(c):
        uid=str(c.from_user.id); data=c.data
        if data.startswith("country_"):
            user_country[uid]="India" if "India" in data else "Bangladesh"
            save_data()
            bot.send_message(c.message.chat.id,welcome_text(c.from_user.id),reply_markup=main_kb())
            return
        if data.startswith("addsel_"):
            if c.from_user.id!=ADMIN_ID: return
            _,game,day=data.split("_"); pending_add[uid]=(game,day)
            bot.send_message(c.message.chat.id,f"{game} {day} Selected, send keys")
            return
        if data.startswith("buy_"):
            _,game,day=data.split("_")
            stock_list=stock_carrom.get(day,[]) if "CARROM" in game else stock_8ball.get(day,[])
            p,_=get_price(c.from_user.id,day)
            if len(stock_list)==0:
                bot.send_message(c.message.chat.id,"Out of Stock",reply_markup=main_kb())
                return
            pending_buy[uid]=(game,day)
            bot.send_message(c.message.chat.id,f"Confirm {game} {day} Rs.{p}",reply_markup=confirm_kb())
            return
        if data=="yes":
            if uid not in pending_buy: return
            game,day=pending_buy[uid]
            p,_=get_price(c.from_user.id,day)
            bal=user_balance.get(uid,0)
            stock_list=stock_carrom.get(day,[]) if "CARROM" in game else stock_8ball.get(day,[])
            if len(stock_list)==0 or bal<p:
                bot.send_message(c.message.chat.id,"Failed check balance/stock",reply_markup=main_kb())
                del pending_buy[uid]; return
            key=stock_list.pop(0)
            user_balance[uid]=bal-p
            if "CARROM" in game: stock_carrom[day]=stock_list
            else: stock_8ball[day]=stock_list
            save_data(); del pending_buy[uid]
            bot.send_message(c.message.chat.id,f"Success Key:{key} Bal:{user_balance[uid]}",reply_markup=main_kb())
            return
        if data in ["no","cancel"]:
            if uid in pending_buy: del pending_buy[uid]
            bot.send_message(c.message.chat.id,"Cancelled",reply_markup=main_kb())
            return

    @bot.message_handler(func=lambda m: m.text and "Add Stock" in m.text)
    def add_stock_btn(m):
        if m.from_user.id==ADMIN_ID:
            bot.send_message(m.chat.id,"Select",reply_markup=add_stock_inline_kb())

    @bot.message_handler(func=lambda m: m.text and "Buy 1 Days" in m.text)
    def buy1(m): bot.send_message(m.chat.id,"1 Days Plan Selected\nSelect a Game:",reply_markup=buy_game_kb("1D"))
    @bot.message_handler(func=lambda m: m.text and "Buy 3 Days" in m.text)
    def buy3(m): bot.send_message(m.chat.id,"3 Days Plan Selected\nSelect a Game:",reply_markup=buy_game_kb("3D"))
    @bot.message_handler(func=lambda m: m.text and "Buy 7 Days" in m.text)
    def buy7(m): bot.send_message(m.chat.id,"7 Days Plan Selected\nSelect a Game:",reply_markup=buy_game_kb("7D"))
    @bot.message_handler(func=lambda m: m.text and "Buy 15 Days" in m.text)
    def buy15(m): bot.send_message(m.chat.id,"15 Days Plan Selected\nSelect a Game:",reply_markup=buy_game_kb("15D"))
    @bot.message_handler(func=lambda m: m.text and "Buy 30 Days" in m.text)
    def buy30(m): bot.send_message(m.chat.id,"30 Days Plan Selected\nSelect a Game:",reply_markup=buy_game_kb("30D"))

    @bot.message_handler(func=lambda m: m.text and "Stock" in m.text and "Add Stock" not in m.text and "Check Stock" not in m.text)
    def stock_btn(m):
        bot.send_message(m.chat.id,get_stock_text(),reply_markup=main_kb())

    @bot.message_handler(func=lambda m: m.text and "Balance" in m.text and "Add Balance" not in m.text)
    def bal_btn(m):
        bal=user_balance.get(str(m.from_user.id),0)
        bot.send_message(m.chat.id,f"Balance Rs.{bal}",reply_markup=main_kb())

    @bot.message_handler(func=lambda m: m.text and "Back to Main" in m.text)
    def back_main(m):
        bot.send_message(m.chat.id,welcome_text(m.from_user.id),reply_markup=main_kb())

    @bot.message_handler(func=lambda m: str(m.from_user.id) in pending_add)
    def pending_add_handler(m):
        if m.from_user.id!=ADMIN_ID: return
        uid=str(m.from_user.id)
        if uid not in pending_add: return
        game,day=pending_add[uid]
        keys=[k.strip() for k in m.text.strip().split("\n") if k.strip()]
        for k in keys:
            if "CARROM" in game: stock_carrom[day].append(k)
            else: stock_8ball[day].append(k)
        save_data(); del pending_add[uid]
        bot.send_message(m.chat.id,f"Added {len(keys)} keys to {game} {day}",reply_markup=admin_kb())

    # IMPORTANT: fallback sobar ses e
    @bot.message_handler(func=lambda m: True)
    def fallback(m):
        txt=(m.text or "").lower()
        if "/price" in txt or "/support" in txt or "/start" in txt:
            return
        uid=str(m.from_user.id)
        if uid not in user_country:
            bot.send_message(m.chat.id,"Select country",reply_markup=country_kb())
        else:
            bot.send_message(m.chat.id,welcome_text(m.from_user.id),reply_markup=main_kb())

    def run_bot():
        while True:
            try:
                bot.infinity_polling()
            except Exception as e:
                print(f"Polling error {e}")
                time.sleep(5)

    threading.Thread(target=run_bot,daemon=True).start()

# Flask always runs
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=10000)

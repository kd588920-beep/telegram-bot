import os, json, threading, time
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8419174100:AAH7p88W9B48yIdc3y2b3m_92Z1amwJmQO0")
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
vip_mode_users = set()

def save_data():
    try:
        with open("data.json","w",encoding="utf-8") as f:
            json.dump({"bal":user_balance,"country":user_country,"plan":user_plan,"carrom":stock_carrom,"ball":stock_8ball,"price":price},f,ensure_ascii=False)
    except:
        pass

def load_data():
    global user_balance,user_country,user_plan,stock_carrom,stock_8ball,price
    try:
        with open("data.json","r",encoding="utf-8") as f:
            d=json.load(f)
            user_balance=d.get("bal",{})
            user_country=d.get("country",{})
            user_plan=d.get("plan",{})
            stock_carrom.update(d.get("carrom",stock_carrom))
            stock_8ball.update(d.get("ball",stock_8ball))
            price.update(d.get("price",price))
    except:
        pass

load_data()
bot = telebot.TeleBot(BOT_TOKEN)
try:
    bot.remove_webhook()
    time.sleep(1)
except:
    pass

app = Flask(__name__)
@app.route('/')
def home():
    return "KOUSHIK 354 LIVE WITH QR"

def get_price(uid, day):
    s=str(uid)
    if s==str(ADMIN_ID):
        if s in vip_mode_users:
            return vip_price.get(day,price.get(day)), "Vip pricing"
        return price.get(day), "Normal pricing (BOSS)"
    if user_plan.get(s,"FREE") in ["VIP","RESELLER"]:
        return vip_price.get(day,price.get(day)), "Vip pricing"
    return price.get(day), "Normal pricing"

def get_stock_text():
    def fmt(d):
        out=""
        for k in ["1D","3D","7D","15D","30D"]:
            c=len(d.get(k,[]))
            out+=f"{'✅' if c>0 else '❌'} {k}: {c} keys\n"
        return out
    return f"📦 Stock\n\n🎯 CARROM\n{fmt(stock_carrom)}\n🎱 8 BALL\n{fmt(stock_8ball)}"

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
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("🎯 CARROM 1D",callback_data="addsel_CARROM_1D"),types.InlineKeyboardButton("🎯 CARROM 3D",callback_data="addsel_CARROM_3D"))
    m.add(types.InlineKeyboardButton("🎯 CARROM 7D",callback_data="addsel_CARROM_7D"),types.InlineKeyboardButton("🎯 CARROM 15D",callback_data="addsel_CARROM_15D"))
    m.add(types.InlineKeyboardButton("🎯 CARROM 30D",callback_data="addsel_CARROM_30D"))
    m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="addsel_BACK"))
    return mdef add_stock_8ball_kb():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("🎱 8BALL 1D",callback_data="addsel_8BALL_1D"),types.InlineKeyboardButton("🎱 8BALL 3D",callback_data="addsel_8BALL_3D"))
    m.add(types.InlineKeyboardButton("🎱 8BALL 7D",callback_data="addsel_8BALL_7D"),types.InlineKeyboardButton("🎱 8BALL 15D",callback_data="addsel_8BALL_15D"))
    m.add(types.InlineKeyboardButton("🎱 8BALL 30D",callback_data="addsel_8BALL_30D"))
    m.add(types.InlineKeyboardButton("⬅️ Back",callback_data="addsel_BACK"))
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
    bal=user_balance.get(s,0)
    country=user_country.get(s,"India")
    plan="BOSS" if s==str(ADMIN_ID) else user_plan.get(s,"FREE")
    return f"\nWelcome to SHINIGAMI Bot!\n\nName: {first_name or 'User'}\nPlan: {plan}\nBalance: Rs.{bal:.2f}\nCountry: {country}\n\nSelect option:"

@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid=str(m.from_user.id)
    for d in [pending_add,pending_admin,pending_buy]:
        if uid in d:
            del d[uid]
    if uid not in user_balance:
        user_balance[uid]=0.0
        save_data()
    if uid not in user_country:
        bot.send_message(m.chat.id,"🌍 Select country",reply_markup=country_kb())
    else:
        if str(m.from_user.id)==str(ADMIN_ID):
            user_plan[uid]="BOSS"
            save_data()
        bot.send_message(m.chat.id,welcome_text(m.from_user.id, m.from_user.first_name),reply_markup=main_kb())

@bot.message_handler(commands=['vip'])
def vip_cmd(m):
    if m.from_user.id!=ADMIN_ID:
        return
    vip_mode_users.add(str(m.from_user.id))
    bot.send_message(m.chat.id,f"✅ VIP MODE ON 👑",reply_markup=main_kb())

@bot.message_handler(commands=['normal','boss'])
def normal_cmd(m):
    if m.from_user.id!=ADMIN_ID:
        return
    vip_mode_users.discard(str(m.from_user.id))
    bot.send_message(m.chat.id,f"✅ NORMAL MODE ON 👤",reply_markup=main_kb())

@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.from_user.id==ADMIN_ID:
        user_plan[str(m.from_user.id)]="BOSS"
        save_data()
        bot.send_message(m.chat.id,"👑 BOSS PANEL",reply_markup=admin_kb())

@bot.callback_query_handler(func=lambda c: True)
def cb_handler(c):
    uid=str(c.from_user.id)
    data=c.data
    if data.startswith("country_"):
        user_country[uid]="Bangladesh" if "Bangladesh" in data else "India"
        save_data()
        try:
            bot.delete_message(c.message.chat.id,c.message.message_id)
        except:
            pass
        bot.send_message(c.message.chat.id,welcome_text(c.from_user.id,c.from_user.first_name),reply_markup=main_kb())
        return
    if data.startswith("addsel_"):
        if c.from_user.id!=ADMIN_ID:
            return
        tmp=data.replace("addsel_","",1)
        if tmp=="GAME_CARROM":
            bot.edit_message_text("🎯 CARROM STOCK POLL", c.message.chat.id, c.message.message_id, reply_markup=add_stock_carrom_kb())
            return
        if tmp=="GAME_8BALL":
            bot.edit_message_text("🎱 8BALL STOCK POLL", c.message.chat.id, c.message.message_id, reply_markup=add_stock_8ball_kb())
            return
        if tmp=="BACK":
            bot.edit_message_text("👇 Select Stock Type:", c.message.chat.id, c.message.message_id, reply_markup=add_stock_inline_kb())
            return
        if tmp.startswith("CARROM_"):
            game="CARROM"
            day=tmp.replace("CARROM_","",1)
        elif tmp.startswith("8BALL_"):
            game="8BALL"
            day=tmp.replace("8BALL_","",1)
        else:
            _,game,day=data.split("_")
        pending_add[uid]=(game,day)
        bot.send_message(c.message.chat.id,f"✅ {game} {day} Selected\nNow send IDs")
        return
    if data.startswith("buy_"):
        _,game,day=data.split("_")
        stock_list=stock_carrom.get(day,[]) if "CARROM" in game else stock_8ball.get(day,[])
        p,pt=get_price(c.from_user.id,day)
        if len(stock_list)==0:
            bot.send_message(c.message.chat.id,f"❌ {game} {day} Out of Stock",reply_markup=main_kb())
            return
        pending_buy[uid]=(game,day)
        bot.send_message(c.message.chat.id,f"🛒 Confirm {game} {day} - Rs.{p} ({pt})\nStock {len(stock_list)}",reply_markup=confirm_kb())
        return
    if data=="confirm_yes":
        if uid not in pending_buy:
            return
        game,day=pending_buy[uid]
        p,_=get_price(c.from_user.id,day)
        bal=user_balance.get(uid,0)
        stock_list=stock_carrom.get(day,[]) if "CARROM" in game else stock_8ball.get(day,[])
        if len(stock_list)==0:
            bot.send_message(c.message.chat.id,f"❌ Out of Stock",reply_markup=main_kb())
            del pending_buy[uid]
            return
        if bal < p:
            bot.send_message(c.message.chat.id,f"❌ Low Balance Need Rs.{p} You have Rs.{bal}",reply_markup=main_kb())
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
        bot.send_message(c.message.chat.id,f"✅ Success!\n🔑 {key}\n💰 Bal Rs.{user_balance[uid]}",reply_markup=main_kb())
        return
    if data=="confirm_no":
        if uid in pending_buy:
            del pending_buy[uid]
        bot.send_message(c.message.chat.id,welcome_text(c.from_user.id,c.from_user.first_name),reply_markup=main_kb())
        return

@bot.message_handler(func=lambda m: m.text and "Add Stock" in m.text)
def add_stock_btn(m):
    if m.from_user.id==ADMIN_ID:
        bot.send_message(m.chat.id,"👇 Select",reply_markup=add_stock_inline_kb())

@bot.message_handler(func=lambda m: m.text and "Add Funds" in m.text)
def add_funds_cmd(m):
    uid=str(m.from_user.id)
    bal=user_balance.get(uid,0)
    try:
        with open('qr.jpg','rb') as photo:
            bot.send_photo(m.chat.id, photo, caption=f"💳 Add Funds\nID: {uid}\nBal: Rs.{bal:.2f}\n📱 Scan QR & Pay Jio 2754\n✅ Screenshot @koushik_098", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📞 Contact Admin", url="https://t.me/koushik_098")))
    except:
        bot.send_message(m.chat.id,f"💳 Add Funds\nID: {uid}\nBal: Rs.{bal}")

@bot.message_handler(func=lambda m: m.text and "Stock" in m.text)
def stock_handler(m):
    bot.send_message(m.chat.id,get_stock_text(),reply_markup=main_kb())

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

@bot.message_handler(func=lambda m: m.text and "Balance" in m.text)
def bal_cmd(m):
    uid=str(m.from_user.id)
    bal=user_balance.get(uid,0)
    bot.send_message(m.chat.id,f"💰 Wallet\nBalance: Rs.{bal}",reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text and "Add Balance" in m.text)
def add_bal_btn(m):
    if m.from_user.id==ADMIN_ID:
        pending_admin[str(m.from_user.id)]="add_bal"
        bot.send_message(m.chat.id,"Format: USERID AMOUNT")

@bot.message_handler(func=lambda m: m.text and "Delete Stock" in m.text)
def del_stock_btn(m):
    if m.from_user.id==ADMIN_ID:
        pending_admin[str(m.from_user.id)]="del_stock"
        bot.send_message(m.chat.id,"Format: CARROM 1D")

@bot.message_handler(func=lambda m: str(m.from_user.id) in pending_admin)
def pending_admin_handler(m):
    uid=str(m.from_user.id)
    task=pending_admin.get(uid)
    txt=m.text or ""
    if any(x in txt for x in ["Add Stock","Delete Stock","Make VIP","Reseller","Cancel","Back to Main","Buy","Balance","Add Funds","/start","/admin","Stock","Add Balance","Broadcast","Set Price","Stats"]):
        return
    try:
        if task=="add_bal":
            parts=txt.split()
            target=parts[0]
            amt=float(parts[1])
            user_balance[target]=user_balance.get(target,0)+amt
            save_data()
            bot.send_message(m.chat.id,f"Added Rs.{amt} to {target}")
        elif task=="del_stock":
            t=txt.upper()
            for d in ["1D","3D","7D","15D","30D"]:
                if d in t:
                    if "CARROM" in t:
                        stock_carrom[d]=[]
                        save_data()
                        bot.send_message(m.chat.id,f"CARROM {d} Cleared")
                    if "BALL" in t or "8" in t:
                        stock_8ball[d]=[]
                        save_data()
                        bot.send_message(m.chat.id,f"8BALL {d} Cleared")
        if uid in pending_admin:
            del pending_admin[uid]
    except Exception as e:
        bot.send_message(m.chat.id,f"Error {e}")

@bot.message_handler(func=lambda m: str(m.from_user.id) in pending_add)
def pending_handler(m):
    if m.from_user.id!=ADMIN_ID:
        return
    uid=str(m.from_user.id)
    if uid not in pending_add:
        return
    txt=m.text or ""
    if "Add Stock" in txt or "Delete Stock" in txt or "Balance" in txt:
        return
    game,day=pending_add[uid]
    keys=[k.strip() for k in txt.split("\n") if k.strip()]
    added=0
    for k in keys:
        if "CARROM" in game:
            stock_carrom[day].append(k)
        else:
            stock_8ball[day].append(k)
        added+=1
    save_data()
    del pending_add[uid]
    bot.send_message(m.chat.id,f"{game} {day} Added {added}")

@bot.message_handler(func=lambda m: m.text and "Back to Main" in m.text)
def back_main(m):
    uid=str(m.from_user.id)
    for d in [pending_add,pending_admin,pending_buy]:
        if uid in d:
            del d[uid]
    bot.send_message(m.chat.id,welcome_text(m.from_user.id),reply_markup=main_kb())

def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(5)

threading.Thread(target=run_bot, daemon=True).start()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

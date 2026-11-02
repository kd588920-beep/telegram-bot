import os, json, threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 7189081595

stock_carrom = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
stock_8ball = {"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
user_balance = {}; user_country = {}; user_plan = {}; pending_add = {}
price = {"1D":60,"3D":130,"7D":180,"15D":350,"30D":570}
pending_admin = {} # For Balance/Broadcast/Price/VIP

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
def home(): return "SHINIGAMI FULL ADMIN OK"

def get_stock_text():
    txt="🎯 CARROM\n"
    for d in ["1D","3D","7D","15D","30D"]:
        c=len(stock_carrom.get(d,[])); txt+=f"{'❌' if c==0 else '✅'} {d} : {c} keys\n"
    txt+="\n🎱 8 BALL\n"
    for d in ["1D","3D","7D","15D","30D"]:
        c=len(stock_8ball.get(d,[])); txt+=f"{'❌' if c==0 else '✅'} {d} : {c} keys\n"
    txt+=f"\n💵 Price: {price}"
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
    m.add(types.KeyboardButton("💰 Add Balance"),types.KeyboardButton("💵 Set Price"))
    m.add(types.KeyboardButton("📢 Broadcast"),types.KeyboardButton("📊 Stats"))
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

@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid=str(m.from_user.id)
    if uid in pending_add: del pending_add[uid]
    if uid in pending_admin: del pending_admin[uid]
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
        bot.send_message(c.message.chat.id,f"✅ **{game} {day} Select Kiya BOSS!**\n\n🔑 **Abb key add kro! Ek line e ekta key**",parse_mode="Markdown")
        bot.answer_callback_query(c.id)

@bot.message_handler(func=lambda m: m.text and "Add Stock" in m.text)
def add_stock_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    uid=str(m.from_user.id)
    if uid in pending_add: del pending_add[uid]
    if uid in pending_admin: del pending_admin[uid]
    bot.send_message(m.chat.id,"👇 Konta Add Korbe BOSS?",reply_markup=add_stock_inline_kb())

@bot.message_handler(func=lambda m: m.text and "Delete Stock" in m.text)
def del_stock_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    uid=str(m.from_user.id)
    pending_admin[uid]="del_stock"
    bot.send_message(m.chat.id,"🗑️ **Delete Format:**\n`CARROM 1D` likhle oi stock clear hobe\nExample: `CARROM 1D` ba `8BALL 7D`",parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and "Add Balance" in m.text)
def add_bal_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    uid=str(m.from_user.id); pending_admin[uid]="add_bal"
    bot.send_message(m.chat.id,"💰 **Format:** `USERID AMOUNT`\nExample: `7189081595 500`\nUser ID pabe Users List e",parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and "Set Price" in m.text)
def set_price_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    uid=str(m.from_user.id); pending_admin[uid]="set_price"
    bot.send_message(m.chat.id,f"💵 **Current Price:** {price}\n\n**Format:** `DAYS PRICE`\nExample: `7D 450` ba `30D 1300`",parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and "Broadcast" in m.text)
def broadcast_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    uid=str(m.from_user.id); pending_admin[uid]="broadcast"
    bot.send_message(m.chat.id,"📢 **Broadcast Message Likho BOSS:**\nSob user ke jabe",parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and "Make VIP" in m.text and "Cancel" not in m.text)
def make_vip_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    uid=str(m.from_user.id); pending_admin[uid]="make_vip"
    bot.send_message(m.chat.id,"👑 **VIP Banate UserID dou:**\nExample: `123456789`",parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and "Make Reseller" in m.text)
def make_res_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    uid=str(m.from_user.id); pending_admin[uid]="make_reseller"
    bot.send_message(m.chat.id,"💎 **Reseller Banate UserID dou:**",parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and "Cancel VIP" in m.text)
def cancel_vip_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    uid=str(m.from_user.id); pending_admin[uid]="cancel_vip"
    bot.send_message(m.chat.id,"❌ **Cancel VIP UserID dou:**",parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and "Cancel Reseller" in m.text)
def cancel_res_btn(m):
    if m.from_user.id!=ADMIN_ID: return
    uid=str(m.from_user.id); pending_admin[uid]="cancel_reseller"
    bot.send_message(m.chat.id,"❌ **Cancel Reseller UserID dou:**",parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text and ("Check Stock" in m.text or m.text=="📦 Stock"))
def stock_handler(m):
    uid=str(m.from_user.id)
    if uid in pending_add: del pending_add[uid]
    bot.send_message(m.chat.id,get_stock_text())

@bot.message_handler(func=lambda m: m.text and "Stats" in m.text)
def stats_handler(m):
    if m.from_user.id!=ADMIN_ID: return
    total_users=len(user_balance); total_keys=sum([len(v) for v in stock_carrom.values()])+sum([len(v) for v in stock_8ball.values()])
    total_bal=sum(user_balance.values())
    bot.send_message(m.chat.id,f"📊 **STATS**\n👥 Users: {total_users}\n🔑 Total Keys: {total_keys}\n💰 Total Balance in Bot: ₹{total_bal}\n💵 Price List: {price}")

@bot.message_handler(func=lambda m: m.text and "Users List" in m.text)
def users_handler(m):
    if m.from_user.id!=ADMIN_ID: return
    txt="👥 Users:\n"
    for uid, bal in list(user_balance.items())[:50]:
        plan=user_plan.get(uid,"FREE"); txt+=f"{uid} - {plan} - ₹{bal}\n"
    bot.send_message(m.chat.id,txt)

@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.from_user.id==ADMIN_ID:
        user_plan[str(m.from_user.id)]="BOSS"; save_data()
        bot.send_message(m.chat.id,"👑 BOSS FULL ADMIN PANEL",reply_markup=admin_kb())

# PENDING HANDLERS
@bot.message_handler(func=lambda m: str(m.from_user.id) in pending_admin)
def pending_admin_handler(m):
    uid=str(m.from_user.id); task=pending_admin.get(uid); txt=m.text or ""
    if any(x in txt for x in ["Add Stock","Delete Stock","Make VIP","Reseller","Cancel","Back to Main","Users List","Buy","Balance","Add Funds","/start","/admin","Check Stock","📦 Stock","Add Balance","Broadcast","Set Price","Stats"]):
        return
    try:
        if task=="add_bal":
            parts=txt.split(); target=parts[0]; amt=float(parts[1])
            user_balance[target]=user_balance.get(target,0)+amt; save_data()
            bot.send_message(m.chat.id,f"✅ Added ₹{amt} to {target}\nNew Bal: ₹{user_balance[target]}")
        elif task=="set_price":
            parts=txt.split(); day=parts[0].upper(); p=int(parts[1]); price[day]=p; save_data()
            bot.send_message(m.chat.id,f"✅ Price Updated: {day} = ₹{p}")
        elif task=="broadcast":
            count=0
            for u in user_balance.keys():
                try: bot.send_message(int(u),f"📢 **BOSS MESSAGE:**\n\n{txt}",parse_mode="Markdown"); count+=1
                except: pass
            bot.send_message(m.chat.id,f"✅ Broadcast Done to {count} users")
        elif task=="make_vip":
            user_plan[txt.strip()]="VIP"; save_data(); bot.send_message(m.chat.id,f"✅ {txt.strip()} is now VIP")
        elif task=="make_reseller":
            user_plan[txt.strip()]="RESELLER"; save_data(); bot.send_message(m.chat.id,f"✅ {txt.strip()} is now RESELLER")
        elif task=="cancel_vip" or task=="cancel_reseller":
            user_plan[txt.strip()]="FREE"; save_data(); bot.send_message(m.chat.id,f"✅ {txt.strip()} is now FREE")
        elif task=="del_stock":
            t=txt.upper()
            if "CARROM" in t:
                for d in ["1D","3D","7D","15D","30D"]:
                    if d in t: stock_carrom[d]=[]; save_data(); bot.send_message(m.chat.id,f"✅ CARROM {d} Cleared")
            if "BALL" in t or "8" in t:
                for d in ["1D","3D","7D","15D","30D"]:
                    if d in t: stock_8ball[d]=[]; save_data(); bot.send_message(m.chat.id,f"✅ 8BALL {d} Cleared")
        del pending_admin[uid]
    except Exception as e:
        bot.send_message(m.chat.id,f"❌ Error: {e}\nFormat thik dao BOSS")

@bot.message_handler(func=lambda m: str(m.from_user.id) in pending_add)
def pending_handler(m):
    if m.from_user.id!=ADMIN_ID: return
    uid=str(m.from_user.id)
    if uid not in pending_add: return
    txt=m.text or ""
    if any(x in txt for x in ["Add Stock","Delete Stock","Make VIP","Reseller","Cancel","Back to Main","Users List","Buy","Balance","Add Funds","/start","/admin","Check Stock","📦 Stock","Add Balance","Broadcast","Set Price","Stats"]):
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
    bot.send_message(m.chat.id,f"✅ SUCCESS BOSS! {game} {day} Added\nAdded: {added} keys\nTotal {day}: {total} keys")
    bot.send_message(m.chat.id,"👇 Aab Kaunsa Add Karoge BOSS?",reply_markup=add_stock_inline_kb())

@bot.message_handler(func=lambda m: m.text and "Balance" in m.text)
def bal_cmd(m):
    uid=str(m.from_user.id); bal=user_balance.get(uid,0)
    bot.send_message(m.chat.id,f"💰 Balance: ₹{bal}")

@bot.message_handler(func=lambda m: m.text and "Back to Main" in m.text)
def back_main(m):
    uid=str(m.from_user.id)
    if uid in pending_add: del pending_add[uid]
    if uid in pending_admin: del pending_admin[uid]
    bot.send_message(m.chat.id,welcome_text(m.from_user.id),reply_markup=main_kb())

def run_flask(): app.run(host="0.0.0.0",port=10000)
threading.Thread(target=run_flask,daemon=True).start()
bot.infinity_polling()

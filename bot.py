import os, threading
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN=os.environ.get("BOT_TOKEN")
ADMIN_ID=7189081595
PRICE={"1D":70,"3D":150,"7D":300,"15D":550,"30D":1000}
stock={"1D":[],"3D":[],"7D":[],"15D":[],"30D":[]}
user_balance={}
user_country={}

bot=telebot.TeleBot(BOT_TOKEN)
app=Flask(__name__)
@app.route('/')
def home(): return "SHINIGAMI Running"

def country_kb():
    m=types.InlineKeyboardMarkup(row_width=2)
    m.add(types.InlineKeyboardButton("India", callback_data="country_India"), types.InlineKeyboardButton("Bangladesh", callback_data="country_Bangladesh"))
    return m

def main_kb():
    m=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    m.add(types.KeyboardButton("Buy 1 Days"), types.KeyboardButton("Buy 3 Days"))
    m.add(types.KeyboardButton("Buy 7 Days"), types.KeyboardButton("Buy 15 Days"))
    m.add(types.KeyboardButton("Buy 30 Days"), types.KeyboardButton("Stock"))
    m.add(types.KeyboardButton("Add Funds"), types.KeyboardButton("Balance"))
    return m

def admin_kb():
    m=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    m.add(types.KeyboardButton("Admin Panel"), types.KeyboardButton("Check Stock"))
    m.add(types.KeyboardButton("Add Stock Help"), types.KeyboardButton("Back to Shop"))
    return m

def welcome(m):
    bal=user_balance.get(m.from_user.id,0.00)
    plan="VIP/Reseller" if m.from_user.id==ADMIN_ID else "Bronze"
    return f"Welcome {m.from_user.first_name}\nID: {m.from_user.id}\nPlan: {plan}\nBalance: {bal}"

@bot.message_handler(commands=['start'])
def s(m):
    uid=m.from_user.id
    if uid not in user_balance: user_balance[uid]=0.00
    if uid not in user_country:
        bot.send_message(m.chat.id, "Select country:", reply_markup=country_kb())
    else:
        bot.send_message(m.chat.id, welcome(m), reply_markup=main_kb())

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid=c.from_user.id
    if c.data.startswith("country_"):
        user_country[uid]=c.data.split("_")[1]
        bot.send_message(c.message.chat.id, welcome(c.from_user), reply_markup=main_kb())
    bot.answer_callback_query(c.id)

@bot.message_handler(commands=['admin'])
def admin_cmd(m):
    if m.from_user.id!=ADMIN_ID:
        bot.reply_to(m, f"Not admin! Your ID: {m.from_user.id}")
        return
    bot.send_message(m.chat.id, f"ADMIN PANEL\nUsers: {len(user_balance)}\nID: {ADMIN_ID} VIP", reply_markup=admin_kb())

@bot.message_handler(func=lambda m: m.text=="Admin Panel")
def ap(m):
    if m.from_user.id==ADMIN_ID: admin_cmd(m)

@bot.message_handler(func=lambda m: m.text=="Check Stock")
def cs(m):
    if m.from_user.id!=ADMIN_ID: return
    t="STOCK\n"
    for k,v in stock.items(): t+=f"{k}: {len(v)}\n"
    bot.send_message(m.chat.id, t)

@bot.message_handler(func=lambda m: m.text=="Back to Shop")
def bs(m): bot.send_message(m.chat.id, welcome(m), reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text=="Stock")
def st(m):
    t="Live Stock\n"
    for k,v in stock.items(): t+=f"{k}: {len(v)} keys\n"
    bot.send_message(m.chat.id, t)

@bot.message_handler(func=lambda m: m.text=="Balance")
def bl(m): bot.send_message(m.chat.id, f"Balance: {user_balance.get(m.from_user.id,0)}")

@bot.message_handler(func=lambda m: m.text=="Add Funds")
def af(m): bot.send_message(m.chat.id, f"Add Funds ID: {m.from_user.id}")

@bot.message_handler(commands=['addstock'])
def ast(m):
    if m.from_user.id!=ADMIN_ID: return
    try:
        a=m.text.split(" ",2)
        stock[a[1].upper()].append(a[2])
        bot.reply_to(m, f"Added {a[1]} {len(stock[a[1].upper()])} keys")
    except: bot.reply_to(m, "Use /addstock 1D key")

def run(): app.run(host="0.0.0.0",port=10000)
threading.Thread(target=run,daemon=True).start()
bot.infinity_polling()
